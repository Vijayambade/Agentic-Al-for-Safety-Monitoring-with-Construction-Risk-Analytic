"""
tests/test_energy.py
--------------------
Unit and integration tests for smart construction energy telemetry, safety checks, and calibrations.
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
from backend.models.energy import EnergyLog, EnergyConfig
from backend.models.dashboard import SystemNotification

TEST_DATABASE_URL = "sqlite:///./data/test_energy_db.db"

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
            email="energy_user@example.com",
            hashed_password="hashed_password_123",
            first_name="Energy",
            last_name="Auditor",
            role="Environmental Engineer",
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
            if os.path.exists("./data/test_energy_db.db"):
                os.remove("./data/test_energy_db.db")
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
    return create_access_token(data={"sub": email, "role": "Environmental Engineer"})


def test_get_configs_initialization(client):
    """Test retrieving configurations auto-seeds standard smart meters."""
    token = get_token(client, "energy_user@example.com")
    headers = {"Authorization": f"Bearer {token}"}

    response = client.get("/api/v1/energy/configs", headers=headers)
    assert response.status_code == 200
    configs = response.json()
    assert len(configs) == 4
    crane = next(c for c in configs if "Cranes" in c["sensor_name"])
    assert crane["max_power_limit"] == 200.0


def test_log_energy_reading_and_anomaly(client, db_session):
    """Test logging energy readings checks anomalies and triggers alarms correctly."""
    token = get_token(client, "energy_user@example.com")
    headers = {"Authorization": f"Bearer {token}"}

    # Log 250.0 kW for Heavy Tower Cranes (limit is 200.0, so it breaches overload limit)
    payload = {
        "sensor_name": "Heavy Tower Cranes",
        "power_usage": 250.0,
        "voltage": 230.0,
        "current": 45.0,
        "power_factor": 0.90,
        "cumulative_kwh": 5000.0
    }
    response = client.post("/api/v1/energy/log", json=payload, headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert data["power_usage"] == 250.0
    assert data["is_anomaly"] is True
    assert data["anomaly_type"] == "Power Spike / Overload"

    # Check that a SystemNotification has been generated
    notification = db_session.query(SystemNotification).order_by(SystemNotification.id.desc()).first()
    assert notification is not None
    assert "Heavy Tower Cranes" in notification.message


def test_update_energy_safety_configs(client):
    """Test updating limits updates config parameters."""
    token = get_token(client, "energy_user@example.com")
    headers = {"Authorization": f"Bearer {token}"}

    payload = {
        "sensor_name": "Heavy Tower Cranes",
        "max_power_limit": 300.0,
        "min_voltage_limit": 200.0,
        "min_power_factor_limit": 0.80
    }
    response = client.post("/api/v1/energy/config", json=payload, headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert data["max_power_limit"] == 300.0
    assert data["min_voltage_limit"] == 200.0
    assert data["min_power_factor_limit"] == 0.80


def test_simulate_sensor_energy_feeds(client):
    """Test simulation updates values for all zones."""
    token = get_token(client, "energy_user@example.com")
    headers = {"Authorization": f"Bearer {token}"}

    payload = {"stress_intensity": 0.8}
    response = client.post("/api/v1/energy/simulate", json=payload, headers=headers)
    assert response.status_code == 200
    logs = response.json()
    assert len(logs) == 4


def test_energy_reset(client):
    """Test reset clears histories and reverts limits to baselines."""
    token = get_token(client, "energy_user@example.com")
    headers = {"Authorization": f"Bearer {token}"}

    # Reset
    response = client.post("/api/v1/energy/reset", headers=headers)
    assert response.status_code == 200
    configs = response.json()
    crane = next(c for c in configs if "Cranes" in c["sensor_name"])
    assert crane["max_power_limit"] == 200.0
