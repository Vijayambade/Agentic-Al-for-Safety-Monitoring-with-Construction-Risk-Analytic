"""
tests/test_waste.py
-------------------
Unit and integration tests for site waste logs, reduction goals, and sustainability metrics.
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
from backend.models.waste import WasteLog, WasteGoal
from backend.models.dashboard import SystemNotification

TEST_DATABASE_URL = "sqlite:///./data/test_waste_db.db"

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
            email="waste_user@example.com",
            hashed_password="hashed_password_123",
            first_name="Waste",
            last_name="Auditor",
            role="Sustainability Manager",
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
            if os.path.exists("./data/test_waste_db.db"):
                os.remove("./data/test_waste_db.db")
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
    return create_access_token(data={"sub": email, "role": "Sustainability Manager"})


def test_get_goals_initialization(client):
    """Test retrieving goals list auto-seeds default reduction targets."""
    token = get_token(client, "waste_user@example.com")
    headers = {"Authorization": f"Bearer {token}"}

    response = client.get("/api/v1/waste/goals", headers=headers)
    assert response.status_code == 200
    goals = response.json()
    assert len(goals) == 4
    concrete_goal = next(g for g in goals if g["waste_type"] == "Concrete")
    assert concrete_goal["goal_quantity"] == 10.0
    assert concrete_goal["achieved"] is True


def test_log_waste_and_goal_breach(client, db_session):
    """Test logging debris disposal triggers notifications and toggles status upon goal breach."""
    token = get_token(client, "waste_user@example.com")
    headers = {"Authorization": f"Bearer {token}"}

    # Log 12.0 Tons of Concrete waste (limit is 10.0)
    payload = {
        "waste_type": "Concrete",
        "quantity": 12.0,
        "unit": "Tons",
        "disposal_method": "Landfill",
        "cost": 450.0
    }
    response = client.post("/api/v1/waste/log", json=payload, headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert data["quantity"] == 12.0

    # Verify goal achieved state shifts to False
    goal = db_session.query(WasteGoal).filter(WasteGoal.waste_type == "Concrete").first()
    assert goal.achieved is False

    # Check notification generation
    notification = db_session.query(SystemNotification).order_by(SystemNotification.id.desc()).first()
    assert notification is not None
    assert "Concrete" in notification.message


def test_adjust_goal_limits(client, db_session):
    """Test setting target goals updates achievement flags."""
    token = get_token(client, "waste_user@example.com")
    headers = {"Authorization": f"Bearer {token}"}

    # Adjust Concrete goal to 15.0 Tons (actual logged Concrete is 12.0)
    payload = {
        "waste_type": "Concrete",
        "goal_quantity": 15.0,
        "unit": "Tons"
    }
    response = client.post("/api/v1/waste/goal", json=payload, headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert data["achieved"] is True


def test_get_sustainability_analytics(client):
    """Test fetching analytics resolves rates and tips correctly."""
    token = get_token(client, "waste_user@example.com")
    headers = {"Authorization": f"Bearer {token}"}

    # Log 6.0 Tons of Steel waste (Recycled)
    payload_steel = {
        "waste_type": "Steel",
        "quantity": 6.0,
        "unit": "Tons",
        "disposal_method": "Recycled",
        "cost": 150.0
    }
    client.post("/api/v1/waste/log", json=payload_steel, headers=headers)

    response = client.get("/api/v1/waste/analytics", headers=headers)
    assert response.status_code == 200
    analytics = response.json()

    # Total waste = 12.0 (Concrete) + 6.0 (Steel) = 18.0
    # Diverted = 6.0 (Recycled)
    # Diversion rate = (6 / 18) * 100 = 33.3%
    assert analytics["total_waste"] == 18.0
    assert analytics["diversion_rate"] == 33.3
    assert len(analytics["sustainability_tips"]) > 0


def test_waste_reset(client):
    """Test waste reset clears logs and restores default goals."""
    token = get_token(client, "waste_user@example.com")
    headers = {"Authorization": f"Bearer {token}"}

    # Reset
    response = client.post("/api/v1/waste/reset", headers=headers)
    assert response.status_code == 200
    goals = response.json()
    assert len(goals) == 4
    concrete_goal = next(g for g in goals if g["waste_type"] == "Concrete")
    assert concrete_goal["goal_quantity"] == 10.0
