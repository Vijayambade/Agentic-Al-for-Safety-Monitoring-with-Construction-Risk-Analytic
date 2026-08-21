"""
tests/test_document_analyzer.py
-------------------------------
Unit and integration tests for the document analyzer router and RAG services.
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
from backend.models.document import AnalyzedDocument

TEST_DATABASE_URL = "sqlite:///./data/test_analyzer.db"

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
            email="doc_user@example.com",
            hashed_password="hashed_password_123",
            first_name="Doc",
            last_name="Auditor",
            role="Project Manager",
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
            if os.path.exists("./data/test_analyzer.db"):
                os.remove("./data/test_analyzer.db")
            # Clean up test index files
            index_dir = "./data/faiss_indexes"
            if os.path.exists(index_dir):
                for f in os.listdir(index_dir):
                    if f.startswith("test_") or f.endswith(".chunks") or f.endswith(".index"):
                        # Skip deleting active files if concurrent, but clean test ones
                        pass
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
    return create_access_token(data={"sub": email, "role": "Project Manager"})


def test_upload_and_analyze_contract(client, db_session):
    """Test uploading a construction contract document and receiving audits."""
    token = get_token(client, "doc_user@example.com")
    headers = {"Authorization": f"Bearer {token}"}

    file_content = (
        b"This Construction Agreement is between Builder Corp and Client LLC.\n"
        b"Scope of work includes pouring concrete foundations and erecting steel frames.\n"
        b"Termination is governed by Section 9: either party can terminate with 30 days notice.\n"
        b"Indemnification: Contractor will indemnify Client up to $500,000."
    )
    
    files = {
        "file": ("test_contract.txt", io.BytesIO(file_content), "text/plain")
    }

    response = client.post("/api/v1/document-analyzer/upload", files=files, headers=headers)
    assert response.status_code == 201
    data = response.json()
    assert data["filename"] == "test_contract.txt"
    assert data["doc_type"] == "Contract"
    assert "summary" in data
    assert "missing_clauses" in data
    assert "risks" in data
    assert "recommendations" in data

    # Check FAISS index file creation
    doc_id = data["id"]
    assert os.path.exists(f"./data/faiss_indexes/{doc_id}.chunks")


def test_query_document_rag(client):
    """Test querying the document using semantic vector search context (RAG)."""
    token = get_token(client, "doc_user@example.com")
    headers = {"Authorization": f"Bearer {token}"}

    # 1. Fetch document list to find valid ID
    list_resp = client.get("/api/v1/document-analyzer/list", headers=headers)
    assert list_resp.status_code == 200
    docs = list_resp.json()
    assert len(docs) > 0
    doc_id = docs[0]["id"]

    # 2. Query document content
    query_payload = {
        "document_id": doc_id,
        "question": "What is the indemnification limit?"
    }
    
    response = client.post("/api/v1/document-analyzer/query", json=query_payload, headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert data["document_id"] == doc_id
    assert "answer" in data
    assert len(data["context_retrieved"]) > 0


def test_list_and_details_analyzer(client):
    """Test retrieving lists and audit detail blocks."""
    token = get_token(client, "doc_user@example.com")
    headers = {"Authorization": f"Bearer {token}"}

    # List
    list_resp = client.get("/api/v1/document-analyzer/list", headers=headers)
    assert list_resp.status_code == 200
    doc_id = list_resp.json()[0]["id"]

    # Details
    det_resp = client.get(f"/api/v1/document-analyzer/details/{doc_id}", headers=headers)
    assert det_resp.status_code == 200
    data = det_resp.json()
    assert data["id"] == doc_id
