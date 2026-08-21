"""
tests/test_air_quality.py
-------------------------
Unit and integration tests for environmental air quality monitoring, gas alarms, and calibrations.
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
from backend.models.air_quality import AirQualityLog, AirQualityConfig
from backend.models.dashboard import SystemNotification

TEST_DATABASE_URL = "sqlite:///./data/test_air_db.db"

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
            email="air_user@example.com",
            hashed_password="hashed_password_123",
            first_name="Air",
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
            if os.path.exists("./data/test_air_db.db"):
                os.remove("./data/test_air_db.db")
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
    token = get_token(client, "air_user@example.com")
    headers = {"Authorization": f"Bearer {token}"}

    response = client.get("/api/v1/air-quality/configs", headers=headers)
    assert response.status_code == 200
    configs = response.json()
    assert len(configs) == 3
    tunnel = next(c for c in configs if "Tunnel" in c["sensor_name"])
    assert tunnel["co_limit"] == 35.0


def test_log_air_quality_and_hazard(client, db_session):
    """Test logging raw air parameters audits thresholds and flags hazards correctly."""
    token = get_token(client, "air_user@example.com")
    headers = {"Authorization": f"Bearer {token}"}

    # Log 80.0 ppm of Carbon Monoxide for Excavation Tunnel (limit is 35, so it breaches safety boundaries)
    payload = {
        "sensor_name": "Excavation Tunnel A",
        "aqi": 120.0,
        "pm25": 15.0,
        "pm10": 22.0,
        "co_level": 80.0,
        "no2_level": 1.2,
        "voc_level": 2.0
    }
    response = client.post("/api/v1/air-quality/log", json=payload, headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert data["co_level"] == 80.0
    assert data["is_hazardous"] is True
    assert "CO gas leak" in data["hazard_reason"]

    # Check that a SystemNotification has been generated
    notification = db_session.query(SystemNotification).order_by(SystemNotification.id.desc()).first()
    assert notification is not None
    assert "Tunnel A" in notification.message


def test_update_air_safety_configs(client):
    """Test updating limits updates rule databases."""
    token = get_token(client, "air_user@example.com")
    headers = {"Authorization": f"Bearer {token}"}

    payload = {
        "sensor_name": "Excavation Tunnel A",
        "pm25_limit": 65.0,
        "co_limit": 90.0,
        "voc_limit": 25.0
    }
    response = client.post("/api/v1/air-quality/config", json=payload, headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert data["pm25_limit"] == 65.0
    assert data["co_limit"] == 90.0
    assert data["voc_limit"] == 25.0


def test_simulate_sensor_air_feeds(client):
    """Test simulation updates values for all zones."""
    token = get_token(client, "air_user@example.com")
    headers = {"Authorization": f"Bearer {token}"}

    payload = {"stress_intensity": 0.7}
    response = client.post("/api/v1/air-quality/simulate", json=payload, headers=headers)
    assert response.status_code == 200
    logs = response.json()
    assert len(logs) == 3


def test_air_reset(client):
    """Test reset clears histories and reverts limits to baselines."""
    token = get_token(client, "air_user@example.com")
    headers = {"Authorization": f"Bearer {token}"}

    # Reset
    response = client.post("/api/v1/air-quality/reset", headers=headers)
    assert response.status_code == 200
    configs = response.json()
    tunnel = next(c for c in configs if "Tunnel" in c["sensor_name"])
    assert tunnel["co_limit"] == 35.0
