"""
tests/test_auth.py
------------------
Unit and integration tests for backend authentication endpoints.
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

# Use an isolated test database file
TEST_DATABASE_URL = "sqlite:///./data/test_auth.db"

engine = create_engine(
    TEST_DATABASE_URL, connect_args={"check_same_thread": False}
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(scope="module")
def db_session():
    # Make sure parent directory for data exists
    os.makedirs("./data", exist_ok=True)
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()
        Base.metadata.drop_all(bind=engine)
        # Clean up database file after run
        try:
            if os.path.exists("./data/test_auth.db"):
                os.remove("./data/test_auth.db")
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


def test_register_user(client, db_session):
    """Test successful user registration."""
    payload = {
        "email": "engineer@example.com",
        "password": "securepassword123",
        "first_name": "Bob",
        "last_name": "Builder",
        "role": "Engineer",
    }
    response = client.post("/api/v1/auth/register", json=payload)
    assert response.status_code == 201
    data = response.json()
    assert data["email"] == "engineer@example.com"
    assert data["role"] == "Engineer"
    assert data["is_verified"] is False

    # Check database record
    user = (
        db_session.query(User)
        .filter(User.email == "engineer@example.com")
        .first()
    )
    assert user is not None
    assert user.otp_code is not None


def test_register_duplicate_email(client):
    """Test registration fails with a duplicate email."""
    payload = {
        "email": "engineer@example.com",
        "password": "securepassword456",
        "first_name": "Alice",
        "last_name": "Smith",
        "role": "Admin",
    }
    response = client.post("/api/v1/auth/register", json=payload)
    assert response.status_code == 400
    assert "already registered" in response.json()["detail"]


def test_verify_otp(client, db_session):
    """Test account OTP validation/activation."""
    # Find user OTP code from the db session
    user = (
        db_session.query(User)
        .filter(User.email == "engineer@example.com")
        .first()
    )
    otp = user.otp_code

    # Call verify
    payload = {"email": "engineer@example.com", "otp_code": otp}
    response = client.post("/api/v1/auth/verify-otp", json=payload)
    assert response.status_code == 200
    assert "verified successfully" in response.json()["detail"]

    # Verify db status changed
    db_session.refresh(user)
    assert user.is_verified is True
    assert user.otp_code is None


def test_login_successful(client):
    """Test login with correct credentials."""
    payload = {
        "email": "engineer@example.com",
        "password": "securepassword123",
        "remember_me": False,
    }
    response = client.post("/api/v1/auth/login", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"
    assert data["role"] == "Engineer"


def test_login_unverified(client, db_session):
    """Test login fails if email is unverified."""
    # Create another user that is unverified
    new_user = User(
        email="unverified@example.com",
        hashed_password="hashed_placeholder",
        role="Worker",
        is_verified=False,
    )
    db_session.add(new_user)
    db_session.commit()

    payload = {
        "email": "unverified@example.com",
        "password": "somepassword",
        "remember_me": False,
    }
    response = client.post("/api/v1/auth/login", json=payload)
    # Correct response for wrong password/unverified user auth flows
    assert response.status_code == 401 or response.status_code == 403


def test_get_current_user_profile(client):
    """Test reading profile using authenticated bearer token."""
    # Step 1: Login
    payload = {
        "email": "engineer@example.com",
        "password": "securepassword123",
        "remember_me": False,
    }
    login_resp = client.post("/api/v1/auth/login", json=payload)
    token = login_resp.json()["access_token"]

    # Step 2: Get Profile
    headers = {"Authorization": f"Bearer {token}"}
    response = client.get("/api/v1/auth/me", headers=headers)
    assert response.status_code == 200
    profile = response.json()
    assert profile["email"] == "engineer@example.com"
    assert profile["first_name"] == "Bob"


def test_forgot_and_reset_password(client, db_session):
    """Test password forgot and reset workflow."""
    # Step 1: Trigger Forgot Password
    payload = {"email": "engineer@example.com"}
    forgot_resp = client.post("/api/v1/auth/forgot-password", json=payload)
    assert forgot_resp.status_code == 200

    # Step 2: Fetch reset code from database
    user = (
        db_session.query(User)
        .filter(User.email == "engineer@example.com")
        .first()
    )
    otp = user.otp_code
    assert otp is not None

    # Step 3: Reset password
    reset_payload = {
        "email": "engineer@example.com",
        "otp_code": otp,
        "new_password": "newsecurepassword999",
    }
    reset_resp = client.post("/api/v1/auth/reset-password", json=reset_payload)
    assert reset_resp.status_code == 200

    # Step 4: Login with old password (should fail)
    login_payload = {
        "email": "engineer@example.com",
        "password": "securepassword123",
    }
    fail_login = client.post("/api/v1/auth/login", json=login_payload)
    assert fail_login.status_code == 401

    # Step 5: Login with new password (should succeed)
    login_payload["password"] = "newsecurepassword999"
    success_login = client.post("/api/v1/auth/login", json=login_payload)
    assert success_login.status_code == 200
    assert "access_token" in success_login.json()
