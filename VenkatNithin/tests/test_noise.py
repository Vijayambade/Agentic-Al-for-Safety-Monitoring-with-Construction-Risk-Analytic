"""
tests/test_noise.py
-------------------
Unit and integration tests for noise decibel monitoring, threshold configurations, and alarms.
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
from backend.models.noise import NoiseLog, NoiseConfig
from backend.models.dashboard import SystemNotification

TEST_DATABASE_URL = "sqlite:///./data/test_noise_db.db"

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
            email="noise_user@example.com",
            hashed_password="hashed_password_123",
            first_name="Noise",
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
            if os.path.exists("./data/test_noise_db.db"):
                os.remove("./data/test_noise_db.db")
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
    """Test retrieving configurations auto-seeds standard zone sensors."""
    token = get_token(client, "noise_user@example.com")
    headers = {"Authorization": f"Bearer {token}"}

    response = client.get("/api/v1/noise/configs", headers=headers)
    assert response.status_code == 200
    configs = response.json()
    assert len(configs) == 3
    excavation = next(c for c in configs if "Excavation" in c["sensor_name"])
    assert excavation["daytime_limit"] == 85.0


def test_log_decibel_and_breach(client, db_session):
    """Test logging raw decibels checks thresholds and records breaches correctly."""
    token = get_token(client, "noise_user@example.com")
    headers = {"Authorization": f"Bearer {token}"}

    # Log 110.0 dB for Excavation Area (limit is 85/55, so it breaches in both day and night phases)
    payload = {
        "sensor_name": "Zone A (Excavation Area)",
        "decibel_level": 110.0
    }
    response = client.post("/api/v1/noise/log", json=payload, headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert data["decibel_level"] == 110.0
    assert data["is_breached"] is True

    # Check that a SystemNotification has been generated
    notification = db_session.query(SystemNotification).order_by(SystemNotification.id.desc()).first()
    assert notification is not None
    assert "Excavation Area" in notification.message


def test_update_threshold_configs(client, db_session):
    """Test updating day/night limits updates rules database."""
    token = get_token(client, "noise_user@example.com")
    headers = {"Authorization": f"Bearer {token}"}

    payload = {
        "sensor_name": "Zone A (Excavation Area)",
        "daytime_limit": 98.0,
        "nighttime_limit": 68.0
    }
    response = client.post("/api/v1/noise/config", json=payload, headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert data["daytime_limit"] == 98.0
    assert data["nighttime_limit"] == 68.0


def test_simulate_sensor_noise_feeds(client):
    """Test simulation updates noise levels for all zones."""
    token = get_token(client, "noise_user@example.com")
    headers = {"Authorization": f"Bearer {token}"}

    payload = {"stress_intensity": 0.8}
    response = client.post("/api/v1/noise/simulate", json=payload, headers=headers)
    assert response.status_code == 200
    logs = response.json()
    assert len(logs) == 3


def test_noise_reset(client):
    """Test reset clears histories and reverts limits to baselines."""
    token = get_token(client, "noise_user@example.com")
    headers = {"Authorization": f"Bearer {token}"}

    # Reset
    response = client.post("/api/v1/noise/reset", headers=headers)
    assert response.status_code == 200
    configs = response.json()
    excavation = next(c for c in configs if "Excavation" in c["sensor_name"])
    assert excavation["daytime_limit"] == 85.0
