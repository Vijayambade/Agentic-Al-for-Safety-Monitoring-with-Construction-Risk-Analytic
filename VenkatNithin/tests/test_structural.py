"""
tests/test_structural.py
------------------------
Unit and integration tests for structural health telemetry, stress checks, and safety rules.
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
from backend.models.structural_health import StructuralLog, StructuralConfig
from backend.models.dashboard import SystemNotification

TEST_DATABASE_URL = "sqlite:///./data/test_structural_db.db"

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
            email="structural_user@example.com",
            hashed_password="hashed_password_123",
            first_name="Structure",
            last_name="Inspector",
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
            if os.path.exists("./data/test_structural_db.db"):
                os.remove("./data/test_structural_db.db")
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
    """Test retrieving configurations auto-seeds standard structural zones."""
    token = get_token(client, "structural_user@example.com")
    headers = {"Authorization": f"Bearer {token}"}

    response = client.get("/api/v1/structural/configs", headers=headers)
    assert response.status_code == 200
    configs = response.json()
    assert len(configs) == 3
    scaffold = next(c for c in configs if "Scaffolding" in c["sensor_name"])
    assert scaffold["max_vibration_frequency"] == 50.0


def test_log_structural_reading_and_anomaly(client, db_session):
    """Test logging structural readings checks anomalies and triggers alarms correctly."""
    token = get_token(client, "structural_user@example.com")
    headers = {"Authorization": f"Bearer {token}"}

    # Log 12.0 degrees tilt for Scaffolding Tower (limit is 5.0, so it breaches safety thresholds)
    payload = {
        "sensor_name": "Scaffolding Tower Zone A",
        "vibration_frequency": 12.0,
        "amplitude": 0.5,
        "tilt_angle": 12.0,
        "strain": 40.0
    }
    response = client.post("/api/v1/structural/log", json=payload, headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert data["tilt_angle"] == 12.0
    assert data["is_unstable"] is True
    assert "Critical Tilt Angle" in data["instability_reason"]

    # Check that a SystemNotification has been generated
    notification = db_session.query(SystemNotification).order_by(SystemNotification.id.desc()).first()
    assert notification is not None
    assert "Scaffolding Tower Zone A" in notification.message


def test_update_structural_safety_configs(client):
    """Test updating limits updates config parameters."""
    token = get_token(client, "structural_user@example.com")
    headers = {"Authorization": f"Bearer {token}"}

    payload = {
        "sensor_name": "Scaffolding Tower Zone A",
        "max_vibration_frequency": 65.0,
        "max_tilt_angle": 15.0,
        "max_strain": 350.0
    }
    response = client.post("/api/v1/structural/config", json=payload, headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert data["max_vibration_frequency"] == 65.0
    assert data["max_tilt_angle"] == 15.0
    assert data["max_strain"] == 350.0


def test_simulate_sensor_structural_feeds(client):
    """Test simulation updates values for all zones."""
    token = get_token(client, "structural_user@example.com")
    headers = {"Authorization": f"Bearer {token}"}

    payload = {"stress_intensity": 0.8}
    response = client.post("/api/v1/structural/simulate", json=payload, headers=headers)
    assert response.status_code == 200
    logs = response.json()
    assert len(logs) == 3


def test_structural_reset(client):
    """Test reset clears histories and reverts limits to baselines."""
    token = get_token(client, "structural_user@example.com")
    headers = {"Authorization": f"Bearer {token}"}

    # Reset
    response = client.post("/api/v1/structural/reset", headers=headers)
    assert response.status_code == 200
    configs = response.json()
    scaffold = next(c for c in configs if "Scaffolding" in c["sensor_name"])
    assert scaffold["max_vibration_frequency"] == 50.0
