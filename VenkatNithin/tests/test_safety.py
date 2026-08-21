"""
tests/test_safety.py
--------------------
Unit and integration tests for the site safety advisor router and services.
"""
import os
import sys
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.database import Base, get_db
from backend.main import app
from backend.models.user import User
from backend.models.safety import SafetyIncident

TEST_DATABASE_URL = "sqlite:///./data/test_safety_db.db"

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
            email="safety_officer@example.com",
            hashed_password="hashed_password_123",
            first_name="Safe",
            last_name="Officer",
            role="Safety Officer",
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
            if os.path.exists("./data/test_safety_db.db"):
                os.remove("./data/test_safety_db.db")
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
    return create_access_token(data={"sub": email, "role": "Safety Officer"})


def test_safety_chat_general(client):
    """Test standard safety chat guidelines."""
    token = get_token(client, "safety_officer@example.com")
    headers = {"Authorization": f"Bearer {token}"}

    payload = {"message": "tell me about scaffolding safety", "is_emergency": False}
    response = client.post("/api/v1/safety/chat", json=payload, headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert "response" in data
    assert "scaffold" in data["response"].lower()


def test_safety_chat_emergency(client):
    """Test priority rescue guidance in emergency chat."""
    token = get_token(client, "safety_officer@example.com")
    headers = {"Authorization": f"Bearer {token}"}

    payload = {"message": "someone fell and has a deep cut on leg", "is_emergency": True}
    response = client.post("/api/v1/safety/chat", json=payload, headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert "response" in data
    assert "emergency" in data["response"].lower() or "first aid" in data["response"].lower() or "medical" in data["response"].lower()


def test_report_hazard_incidents(client, db_session):
    """Test logging safety hazards persistently and verifying logs."""
    token = get_token(client, "safety_officer@example.com")
    headers = {"Authorization": f"Bearer {token}"}

    payload = {
        "hazard_description": "Scaffolding planks on building C are loose and missing midrails.",
        "severity": "High Critical"
    }
    response = client.post("/api/v1/safety/incidents", json=payload, headers=headers)
    assert response.status_code == 201
    data = response.json()
    assert data["hazard_description"] == payload["hazard_description"]
    assert data["severity"] == "High Critical"
    assert data["status"] == "Open"

    # Verify database persistence
    incident = db_session.query(SafetyIncident).filter(SafetyIncident.id == data["id"]).first()
    assert incident is not None
    assert incident.severity == "High Critical"


def test_safety_checklist_retrievals(client):
    """Test fetching activity checklist specifications."""
    token = get_token(client, "safety_officer@example.com")
    headers = {"Authorization": f"Bearer {token}"}

    response = client.get("/api/v1/safety/checklist?activity=Welding", headers=headers)
    assert response.status_code == 200
    items = response.json()
    assert len(items) > 0
    assert any("extinguisher" in item.lower() for item in items)


def test_emergency_sop_retrievals(client):
    """Test fetching emergency first response protocol files."""
    token = get_token(client, "safety_officer@example.com")
    headers = {"Authorization": f"Bearer {token}"}

    response = client.get("/api/v1/safety/emergency-sop?incident_type=Fire Outbreak", headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert "sop" in data
    assert "evacuate" in data["sop"].lower()
