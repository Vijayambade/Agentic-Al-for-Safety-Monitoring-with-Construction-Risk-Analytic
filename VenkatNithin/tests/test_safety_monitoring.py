"""
tests/test_safety_monitoring.py
--------------------------------
Unit and integration tests for the safety monitoring and computer vision router.
"""
import io
import os
import sys
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from PIL import Image

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.database import Base, get_db
from backend.main import app
from backend.models.user import User
from backend.models.dashboard import SystemNotification, ActivityLog

TEST_DATABASE_URL = "sqlite:///./data/test_monitoring.db"

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
            email="mon_user@example.com",
            hashed_password="hashed_password_123",
            first_name="Mon",
            last_name="Auditor",
            role="Safety Inspector",
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
            if os.path.exists("./data/test_monitoring.db"):
                os.remove("./data/test_monitoring.db")
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
    return create_access_token(data={"sub": email, "role": "Safety Inspector"})


def create_test_image_bytes():
    """Helper to generate a simple solid color JPEG image in memory."""
    img = Image.new("RGB", (300, 300), color="blue")
    img_byte_arr = io.BytesIO()
    img.save(img_byte_arr, format="JPEG")
    return img_byte_arr.getvalue()


def test_safety_detection_compliant(client):
    """Test safety gear detection with a simulated fully compliant image."""
    token = get_token(client, "mon_user@example.com")
    headers = {"Authorization": f"Bearer {token}"}
    
    img_bytes = create_test_image_bytes()
    files = {
        "file": ("safe_worker.jpg", io.BytesIO(img_bytes), "image/jpeg")
    }

    response = client.post("/api/v1/safety-monitoring/detect", files=files, headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert data["compliance_score"] == 100
    assert len(data["detected_gear"]) == 5
    assert len(data["missing_gear"]) == 0
    assert data["annotated_image"].startswith("data:image/jpeg;base64,")


def test_safety_detection_violation(client, db_session):
    """Test safety gear detection with a violation file, triggering system alarm logs."""
    token = get_token(client, "mon_user@example.com")
    headers = {"Authorization": f"Bearer {token}"}
    
    img_bytes = create_test_image_bytes()
    files = {
        "file": ("violation_check.jpg", io.BytesIO(img_bytes), "image/jpeg")
    }

    response = client.post("/api/v1/safety-monitoring/detect", files=files, headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert data["compliance_score"] < 100
    assert len(data["missing_gear"]) > 0
    
    # Verify that a SystemNotification was automatically written to database
    notif = db_session.query(SystemNotification).filter(
        SystemNotification.title.like("%Critical PPE%")
    ).first()
    assert notif is not None
    assert "violation_check.jpg" in notif.message

    # Verify that an ActivityLog of PPE_VIOLATION was logged
    act = db_session.query(ActivityLog).filter(
        ActivityLog.action_type == "PPE_VIOLATION"
    ).first()
    assert act is not None
