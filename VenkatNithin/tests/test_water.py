"""
tests/test_water.py
-------------------
Unit and integration tests for water flow grid monitoring, leaks, and safety calibrations.
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
from backend.models.water_monitoring import WaterLog, WaterConfig
from backend.models.dashboard import SystemNotification

TEST_DATABASE_URL = "sqlite:///./data/test_water_db.db"

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
            email="water_user@example.com",
            hashed_password="hashed_password_123",
            first_name="Water",
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
            if os.path.exists("./data/test_water_db.db"):
                os.remove("./data/test_water_db.db")
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


def test_get_configs_initialization(client):
    """Test retrieving configurations auto-seeds standard water sensors."""
    token = get_token(client, "water_user@example.com")
    headers = {"Authorization": f"Bearer {token}"}

    response = client.get("/api/v1/water/configs", headers=headers)
    assert response.status_code == 200
    configs = response.json()
    assert len(configs) == 3
    inlet = next(c for c in configs if "Inlet" in c["sensor_name"])
    assert inlet["max_flow_limit"] == 120.0


def test_log_water_reading_and_anomaly(client, db_session):
    """Test logging raw water readings checks anomalies and triggers alarms correctly."""
    token = get_token(client, "water_user@example.com")
    headers = {"Authorization": f"Bearer {token}"}

    # Log 150.0 L/min for Main Supply Inlet (limit is 120, so it breaches flow threshold)
    payload = {
        "sensor_name": "Main Supply Inlet",
        "flow_rate": 150.0,
        "pressure": 220.0,
        "cumulative_liters": 5000.0
    }
    response = client.post("/api/v1/water/log", json=payload, headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert data["flow_rate"] == 150.0
    assert data["is_anomaly"] is True
    assert data["anomaly_type"] == "High Flow"

    # Check that a SystemNotification has been generated
    notification = db_session.query(SystemNotification).order_by(SystemNotification.id.desc()).first()
    assert notification is not None
    assert "Main Supply Inlet" in notification.message


def test_update_water_safety_configs(client):
    """Test updating limits updates rule databases."""
    token = get_token(client, "water_user@example.com")
    headers = {"Authorization": f"Bearer {token}"}

    payload = {
        "sensor_name": "Main Supply Inlet",
        "max_flow_limit": 180.0,
        "min_pressure_limit": 160.0
    }
    response = client.post("/api/v1/water/config", json=payload, headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert data["max_flow_limit"] == 180.0
    assert data["min_pressure_limit"] == 160.0


def test_simulate_sensor_water_feeds(client):
    """Test simulation updates values for all zones."""
    token = get_token(client, "water_user@example.com")
    headers = {"Authorization": f"Bearer {token}"}

    payload = {"stress_intensity": 0.8}
    response = client.post("/api/v1/water/simulate", json=payload, headers=headers)
    assert response.status_code == 200
    logs = response.json()
    assert len(logs) == 3


def test_water_reset(client):
    """Test reset clears histories and reverts limits to baselines."""
    token = get_token(client, "water_user@example.com")
    headers = {"Authorization": f"Bearer {token}"}

    # Reset
    response = client.post("/api/v1/water/reset", headers=headers)
    assert response.status_code == 200
    configs = response.json()
    inlet = next(c for c in configs if "Inlet" in c["sensor_name"])
    assert inlet["max_flow_limit"] == 120.0
