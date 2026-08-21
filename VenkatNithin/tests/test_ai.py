"""
tests/test_ai.py
----------------
Unit and integration tests for the general AI Construction Assistant router and services.
"""
import io
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
from backend.models.ai_history import GeneralChatHistory

TEST_DATABASE_URL = "sqlite:///./data/test_ai.db"

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
        # Create active verified user
        user = User(
            email="ai_user@example.com",
            hashed_password="hashed_password_123",
            first_name="AI",
            last_name="Tester",
            role="Engineer",
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
            if os.path.exists("./data/test_ai.db"):
                os.remove("./data/test_ai.db")
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
    return create_access_token(data={"sub": email, "role": "Engineer"})


def test_general_chat_text(client, db_session):
    """Test standard text-based chat QA."""
    token = get_token(client, "ai_user@example.com")
    headers = {"Authorization": f"Bearer {token}"}
    
    # 1. Ask about concrete grade mix
    payload = {
        "session_id": "test_session_99",
        "prompt": "what is the mixing ratio for concrete?",
        "language": "en"
    }
    response = client.post("/api/v1/ai/general-chat", data=payload, headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert "user_message" in data
    assert "response" in data
    assert "M25" in data["response"] or "ratio" in data["response"]


def test_general_chat_multilingual(client):
    """Test requesting chat translation response."""
    token = get_token(client, "ai_user@example.com")
    headers = {"Authorization": f"Bearer {token}"}
    
    payload = {
        "session_id": "test_session_99",
        "prompt": "what is concrete cover?",
        "language": "es"
    }
    response = client.post("/api/v1/ai/general-chat", data=payload, headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert "Traducción al Español" in data["response"]


def test_general_chat_doc_upload(client):
    """Test document context inclusion."""
    token = get_token(client, "ai_user@example.com")
    headers = {"Authorization": f"Bearer {token}"}
    
    # Create fake TXT file
    file_content = b"Specification details: Structural steel thickness must be at least 15mm."
    files = {
        "document": ("specs.txt", io.BytesIO(file_content), "text/plain")
    }
    data = {
        "session_id": "test_session_99",
        "prompt": "Summarize steel parameters",
        "language": "en"
    }
    
    response = client.post("/api/v1/ai/general-chat", data=data, files=files, headers=headers)
    assert response.status_code == 200
    res_data = response.json()
    assert "Document QA" in res_data["response"] or "15mm" in res_data["response"]


def test_general_chat_history_ops(client, db_session):
    """Test retrieving and clearing chat history logs."""
    token = get_token(client, "ai_user@example.com")
    headers = {"Authorization": f"Bearer {token}"}
    
    # 1. Fetch History
    resp = client.get("/api/v1/ai/general-chat/history/test_session_99", headers=headers)
    assert resp.status_code == 200
    history = resp.json()
    assert len(history) >= 2  # contains user & assistant exchanges
    
    # 2. Clear History
    clear_resp = client.delete("/api/v1/ai/general-chat/history/test_session_99", headers=headers)
    assert clear_resp.status_code == 200
    
    # 3. Verify Empty
    verify_resp = client.get("/api/v1/ai/general-chat/history/test_session_99", headers=headers)
    assert len(verify_resp.json()) == 0
