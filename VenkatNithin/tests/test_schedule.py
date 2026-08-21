"""
tests/test_schedule.py
----------------------
Unit and integration tests for CPM scheduling algorithms and delay forecasting routers.
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
from backend.models.schedule import ScheduleTask

TEST_DATABASE_URL = "sqlite:///./data/test_schedule_db.db"

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
            email="sched_user@example.com",
            hashed_password="hashed_password_123",
            first_name="Sched",
            last_name="Planner",
            role="Planning Engineer",
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
            if os.path.exists("./data/test_schedule_db.db"):
                os.remove("./data/test_schedule_db.db")
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
    return create_access_token(data={"sub": email, "role": "Planning Engineer"})


def test_get_tasks_initialization(client):
    """Test retrieving tasks list auto-initializes database baseline project tasks."""
    token = get_token(client, "sched_user@example.com")
    headers = {"Authorization": f"Bearer {token}"}

    response = client.get("/api/v1/schedule/tasks", headers=headers)
    assert response.status_code == 200
    tasks = response.json()
    assert len(tasks) == 5
    assert tasks[0]["name"] == "Excavation & Site Prep"
    assert tasks[0]["is_critical"] is True  # In CPM baseline, linear paths are critical


def test_delay_prediction_simulation(client, db_session):
    """Test entering risk parameters computes delays and shifts dates down dependency paths."""
    token = get_token(client, "sched_user@example.com")
    headers = {"Authorization": f"Bearer {token}"}

    payload = {"weather_risk": 0.8, "labor_risk": 0.5}
    response = client.post("/api/v1/schedule/predict", json=payload, headers=headers)
    assert response.status_code == 200
    tasks = response.json()

    # Find Excavation task (ID 1)
    t1 = next(t for t in tasks if t["id"] == 1)
    # Excavation duration is 5, with weather risk 0.8/labor 0.5 delay should be computed
    assert t1["predicted_delay"] > 0
    
    # Confirm successor starts shift down the path (Task 2 ES matches Task 1 EF)
    t2 = next(t for t in tasks if t["id"] == 2)
    assert t2["start_date"] == t1["end_date"]


def test_schedule_reset(client):
    """Test schedule reset restores baseline timelines and clears delays."""
    token = get_token(client, "sched_user@example.com")
    headers = {"Authorization": f"Bearer {token}"}

    # Reset
    response = client.post("/api/v1/schedule/reset", headers=headers)
    assert response.status_code == 200
    tasks = response.json()
    
    # Verify delay is back to 0
    t1 = next(t for t in tasks if t["id"] == 1)
    assert t1["predicted_delay"] == 0
