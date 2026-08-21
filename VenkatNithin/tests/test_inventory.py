"""
tests/test_inventory.py
-----------------------
Unit and integration tests for material stock monitoring, consumption logs, and purchase orders.
"""
import os
import sys
from datetime import datetime
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.database import Base, get_db
from backend.main import app
from backend.models.user import User
from backend.models.inventory import MaterialStock, MaterialOrder
from backend.models.dashboard import SystemNotification

TEST_DATABASE_URL = "sqlite:///./data/test_inventory_db.db"

engine = create_engine(
    TEST_DATABASE_URL, connect_args={"check_same_thread": False}
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(scope="module")
def db_session():
    os.makedirs("./data", exist_ok=True)
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    try:
        user = User(
            email="inv_user@example.com",
            hashed_password="hashed_password_123",
            first_name="Inv",
            last_name="Steward",
            role="Materials Manager",
            is_active=True,
            is_verified=True,
        )
        db.add(user)
        db.commit()
        yield db
    finally:
        db.close()
        Base.metadata.drop_all(bind=engine)
        try:
            if os.path.exists("./data/test_inventory_db.db"):
                os.remove("./data/test_inventory_db.db")
        except Exception:
            pass


@pytest.fixture(scope="module")
def client(db_session):
    def override_get_db():
        try:
            yield db_session
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()


def get_token(client, email):
    from backend.utils.security import create_access_token
    return create_access_token(data={"sub": email, "role": "Materials Manager"})


def test_get_stocks_initialization(client):
    """Test retrieving inventory stocks list auto-seeds standard materials."""
    token = get_token(client, "inv_user@example.com")
    headers = {"Authorization": f"Bearer {token}"}

    response = client.get("/api/v1/inventory/stocks", headers=headers)
    assert response.status_code == 200
    stocks = response.json()
    assert len(stocks) == 5
    cement = next(s for s in stocks if s["material_name"] == "Cement")
    assert cement["quantity"] == 500.0
    assert cement["low_stock_alert"] is False


def test_material_consumption_and_low_stock_alarm(client, db_session):
    """Test consuming material triggers warning alarm and SystemNotification when breaching thresholds."""
    token = get_token(client, "inv_user@example.com")
    headers = {"Authorization": f"Bearer {token}"}

    # Consume 400 Bags of Cement (stock will drop to 100, which is below min_threshold 150)
    payload = {
        "material_id": 1,
        "quantity": 400.0,
        "waste": 15.0
    }
    response = client.post("/api/v1/inventory/consume", json=payload, headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert data["quantity"] == 100.0
    assert data["waste_quantity"] == 15.0
    assert data["low_stock_alert"] is True

    # Check that a SystemNotification has been generated
    notification = db_session.query(SystemNotification).order_by(SystemNotification.id.desc()).first()
    assert notification is not None
    assert "Cement" in notification.message


def test_create_and_receive_reorder(client, db_session):
    """Test dispatching a purchase order and delivery updating restocks quantities."""
    token = get_token(client, "inv_user@example.com")
    headers = {"Authorization": f"Bearer {token}"}

    # Place reorder for Cement (300 bags)
    payload = {
        "material_id": 1,
        "order_quantity": 300.0
    }
    response = client.post("/api/v1/inventory/reorder", json=payload, headers=headers)
    assert response.status_code == 200
    order = response.json()
    assert order["status"] == "Ordered"
    assert order["total_cost"] == 300.0 * 8.00  # unit_price is 8.00

    order_id = order["id"]

    # Mark as Shipped
    response_shipped = client.post(
        "/api/v1/inventory/update-delivery",
        json={"order_id": order_id, "status": "Shipped"},
        headers=headers
    )
    assert response_shipped.status_code == 200
    assert response_shipped.json()["status"] == "Shipped"

    # Mark as Delivered (triggers restock and clears alarms)
    response_delivered = client.post(
        "/api/v1/inventory/update-delivery",
        json={"order_id": order_id, "status": "Delivered"},
        headers=headers
    )
    assert response_delivered.status_code == 200
    assert response_delivered.json()["status"] == "Delivered"

    # Verify stock quantity has increased (100 + 300 = 400)
    cement_stock = db_session.query(MaterialStock).filter(MaterialStock.id == 1).first()
    assert cement_stock.quantity == 400.0
    assert cement_stock.low_stock_alert is False  # Restocked above threshold (150)


def test_inventory_reset(client):
    """Test inventory reset clears orders and restores stock baselines."""
    token = get_token(client, "inv_user@example.com")
    headers = {"Authorization": f"Bearer {token}"}

    # Reset
    response = client.post("/api/v1/inventory/reset", headers=headers)
    assert response.status_code == 200
    stocks = response.json()
    cement = next(s for s in stocks if s["material_name"] == "Cement")
    assert cement["quantity"] == 500.0
    assert cement["waste_quantity"] == 0.0
