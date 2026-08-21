"""
tests/test_dashboard.py
-----------------------
Unit and integration tests for dashboard endpoints.
"""
import os
import sys
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Ensure the root project directory is on the path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.database import Base, get_db
from backend.main import app
from backend.models.user import User
from backend.models.dashboard import TaskItem

TEST_DATABASE_URL = "sqlite:///./data/test_dashboard.db"

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
        # Create users for multiple roles
        roles = ["Admin", "Safety Officer", "Supplier", "Project Manager"]
        for role in roles:
            email = f"{role.lower().replace(' ', '_')}@example.com"
            user = User(
                email=email,
                hashed_password="hashed_password_123",
                first_name=role,
                last_name="Test",
                role=role,
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
            if os.path.exists("./data/test_dashboard.db"):
                os.remove("./data/test_dashboard.db")
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
    # Retrieve user token directly by calling login (simulate login bypass since password is encrypted and we hardcoded it in setup)
    # Actually, let's login by creating a token directly using security utils or mock login endpoint
    # Wait, we can just call login since the hashed_password matches the verify_password in db setup if we hash it!
    # Let's see: in setup we used "hashed_password_123" plain string, which won't pass bcrypt verify!
    # Let's update the password in setup to be hashed, or we can just call security utility to create token!
    from backend.utils.security import create_access_token

    return create_access_token(data={"sub": email, "role": "some-role"})


def test_get_dashboard_stats_admin(client, db_session):
    """Test retrieving dashboard stats for Admin role."""
    token = get_token(client, "admin@example.com")
    headers = {"Authorization": f"Bearer {token}"}

    response = client.get("/api/v1/dashboard/stats", headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert "metrics" in data
    assert "charts_data" in data
    assert "tasks" in data
    assert "notifications" in data
    assert "activities" in data

    assert data["metrics"]["system_health"] == "99.8%"
    assert data["charts_data"]["chart_type"] == "bar"


def test_get_dashboard_stats_safety_officer(client, db_session):
    """Test retrieving dashboard stats for Safety Officer role."""
    token = get_token(client, "safety_officer@example.com")
    headers = {"Authorization": f"Bearer {token}"}

    response = client.get("/api/v1/dashboard/stats", headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert data["metrics"]["days_since_accident"] == 142
    assert "incidents" in data["charts_data"]["title"].lower()


def test_create_and_toggle_task(client, db_session):
    """Test creating and toggling completeness of a task."""
    token = get_token(client, "admin@example.com")
    headers = {"Authorization": f"Bearer {token}"}

    # 1. Create task
    task_payload = {"title": "Verify firewall policies", "description": "Admin security check"}
    response = client.post("/api/v1/dashboard/tasks", json=task_payload, headers=headers)
    assert response.status_code == 201
    task_data = response.json()
    assert task_data["title"] == "Verify firewall policies"
    assert task_data["is_completed"] is False
    task_id = task_data["id"]

    # 2. Toggle to completed
    update_payload = {"is_completed": True}
    update_resp = client.put(f"/api/v1/dashboard/tasks/{task_id}", json=update_payload, headers=headers)
    assert update_resp.status_code == 200
    updated_data = update_resp.json()
    assert updated_data["is_completed"] is True

    # 3. Verify in database
    user = db_session.query(User).filter(User.email == "admin@example.com").first()
    task = db_session.query(TaskItem).filter(TaskItem.id == task_id, TaskItem.user_id == user.id).first()
    assert task.is_completed is True


def test_log_custom_activity(client, db_session):
    """Test posting a custom activity log."""
    token = get_token(client, "admin@example.com")
    headers = {"Authorization": f"Bearer {token}"}

    payload = {"action_type": "AUDIT_CHECK", "description": "Verified server SSL certificates."}
    response = client.post("/api/v1/dashboard/activities", json=payload, headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert data["action_type"] == "AUDIT_CHECK"
    assert "SSL" in data["description"]


def test_assistant_chat(client, db_session):
    """Test AI assistant responding contextually based on user role."""
    # Test for Safety Officer
    token_safety = get_token(client, "safety_officer@example.com")
    headers_safety = {"Authorization": f"Bearer {token_safety}"}
    chat_payload = {"message": "What is my task list?"}
    response = client.post("/api/v1/dashboard/chat", json=chat_payload, headers=headers_safety)
    assert response.status_code == 200
    data = response.json()
    assert "Safety Officer" in data["response"]
    assert "PPE" in data["response"] or "incident" in data["response"] or "task" in data["response"]
