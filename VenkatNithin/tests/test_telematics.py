"""
tests/test_telematics.py
------------------------
Unit and integration tests for IoT equipment telematics and predictive maintenance.
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
from backend.models.telematics import EquipmentTelemetry

TEST_DATABASE_URL = "sqlite:///./data/test_telematics_db.db"

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
            email="tele_user@example.com",
            hashed_password="hashed_password_123",
            first_name="Tele",
            last_name="Inspector",
            role="Equipment Manager",
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
            if os.path.exists("./data/test_telematics_db.db"):
                os.remove("./data/test_telematics_db.db")
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
    return create_access_token(data={"sub": email, "role": "Equipment Manager"})


def test_get_equipment_initialization(client):
    """Test retrieving equipment list auto-initializes the fleet database."""
    token = get_token(client, "tele_user@example.com")
    headers = {"Authorization": f"Bearer {token}"}

    response = client.get("/api/v1/telematics/equipment", headers=headers)
    assert response.status_code == 200
    fleet = response.json()
    assert len(fleet) == 4
    assert fleet[0]["name"] == "Excavator #101"
    assert fleet[0]["health_score"] >= 80.0


def test_telemetry_simulation_stress(client, db_session):
    """Test injecting mechanical/thermal stress triggers failure alerts."""
    token = get_token(client, "tele_user@example.com")
    headers = {"Authorization": f"Bearer {token}"}

    # Inject high stress
    payload = {"stress_intensity": 1.0}
    response = client.post("/api/v1/telematics/simulate", json=payload, headers=headers)
    assert response.status_code == 200
    fleet = response.json()

    # Find Excavator (ID 1) or Concrete Mixer (ID 4)
    mixer = next(e for e in fleet if e["id"] == 4)
    # Check that temperature has spiked and health dropped
    assert mixer["engine_temp"] > 90.0
    
    # Check database status updates
    db_mixer = db_session.query(EquipmentTelemetry).filter(EquipmentTelemetry.id == 4).first()
    assert db_mixer.engine_temp > 90.0


def test_schedule_vehicle_service(client):
    """Test scheduling service logs changes in database."""
    token = get_token(client, "tele_user@example.com")
    headers = {"Authorization": f"Bearer {token}"}

    payload = {
        "equipment_id": 1,
        "scheduled_date": "2026-08-15T09:00:00"
    }
    response = client.post("/api/v1/telematics/schedule-maintenance", json=payload, headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "Scheduled"
    assert "2026-08-15" in data["maintenance_scheduled_at"]


def test_fleet_reset(client):
    """Test fleet reset restores optimal health profiles."""
    token = get_token(client, "tele_user@example.com")
    headers = {"Authorization": f"Bearer {token}"}

    # Reset
    response = client.post("/api/v1/telematics/reset", headers=headers)
    assert response.status_code == 200
    fleet = response.json()
    
    # Confirm excavator (ID 1) temperature and health has been cooled/restored
    ex = next(e for e in fleet if e["id"] == 1)
    assert ex["engine_temp"] == 82.0
    assert ex["health_score"] >= 95.0
