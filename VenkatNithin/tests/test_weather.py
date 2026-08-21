"""
tests/test_weather.py
---------------------
Unit and integration tests for weather telemetry, safety checks, and calibrations.
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
from backend.models.weather_hazards import WeatherLog, WeatherConfig
from backend.models.dashboard import SystemNotification

TEST_DATABASE_URL = "sqlite:///./data/test_weather_db.db"

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
            email="weather_user@example.com",
            hashed_password="hashed_password_123",
            first_name="Weather",
            last_name="Forecaster",
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
            if os.path.exists("./data/test_weather_db.db"):
                os.remove("./data/test_weather_db.db")
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
    """Test retrieving configurations auto-seeds standard weather sensor stations."""
    token = get_token(client, "weather_user@example.com")
    headers = {"Authorization": f"Bearer {token}"}

    response = client.get("/api/v1/weather/configs", headers=headers)
    assert response.status_code == 200
    configs = response.json()
    assert len(configs) == 3
    jib = next(c for c in configs if "Crane" in c["sensor_name"])
    assert jib["max_wind_speed_limit"] == 40.0


def test_log_weather_reading_and_hazard(client, db_session):
    """Test logging weather readings checks hazards and triggers alarms correctly."""
    token = get_token(client, "weather_user@example.com")
    headers = {"Authorization": f"Bearer {token}"}

    # Log 55.0 km/h wind speed for Tower Crane Jib Peak (limit is 40.0, so it breaches safety thresholds)
    payload = {
        "sensor_name": "Tower Crane Jib Peak",
        "temperature": 28.0,
        "wind_speed": 55.0,
        "humidity": 65.0,
        "precipitation": 0.0,
        "barometric_pressure": 1013.0,
        "uv_index": 3.0
    }
    response = client.post("/api/v1/weather/log", json=payload, headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert data["wind_speed"] == 55.0
    assert data["is_hazardous"] is True
    assert "Tower Crane Operation Wind Risk" in data["hazard_types"]

    # Check that a SystemNotification has been generated
    notification = db_session.query(SystemNotification).order_by(SystemNotification.id.desc()).first()
    assert notification is not None
    assert "Tower Crane Jib Peak" in notification.message


def test_update_weather_safety_configs(client):
    """Test updating limits updates config parameters."""
    token = get_token(client, "weather_user@example.com")
    headers = {"Authorization": f"Bearer {token}"}

    payload = {
        "sensor_name": "Tower Crane Jib Peak",
        "max_wind_speed_limit": 60.0,
        "max_temp_limit": 42.0,
        "max_precipitation_limit": 80.0
    }
    response = client.post("/api/v1/weather/config", json=payload, headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert data["max_wind_speed_limit"] == 60.0
    assert data["max_temp_limit"] == 42.0
    assert data["max_precipitation_limit"] == 80.0


def test_simulate_sensor_weather_feeds(client):
    """Test simulation updates values for all zones."""
    token = get_token(client, "weather_user@example.com")
    headers = {"Authorization": f"Bearer {token}"}

    payload = {"stress_intensity": 0.8}
    response = client.post("/api/v1/weather/simulate", json=payload, headers=headers)
    assert response.status_code == 200
    logs = response.json()
    assert len(logs) == 3


def test_weather_reset(client):
    """Test reset clears histories and reverts limits to baselines."""
    token = get_token(client, "weather_user@example.com")
    headers = {"Authorization": f"Bearer {token}"}

    # Reset
    response = client.post("/api/v1/weather/reset", headers=headers)
    assert response.status_code == 200
    configs = response.json()
    jib = next(c for c in configs if "Crane" in c["sensor_name"])
    assert jib["max_wind_speed_limit"] == 40.0
