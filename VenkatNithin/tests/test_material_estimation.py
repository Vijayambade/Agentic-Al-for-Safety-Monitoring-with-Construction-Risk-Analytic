"""
tests/test_material_estimation.py
-----------------------------------
Unit and integration tests for Material Estimation service, schemas, router, and exports.
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
from backend.schemas.material_estimation import MaterialEstimationRequest
from backend.services.material_estimation_service import (
    calculate_material_estimation,
    generate_estimation_pdf,
    generate_estimation_csv,
)

TEST_DATABASE_URL = "sqlite:///./data/test_material.db"

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
            email="material_tester@example.com",
            hashed_password="hashed_password_123",
            first_name="Material",
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
            if os.path.exists("./data/test_material.db"):
                os.remove("./data/test_material.db")
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


def get_token(email):
    from backend.utils.security import create_access_token
    return create_access_token(data={"sub": email, "role": "Engineer"})


def test_service_calculation_residential_rcc():
    """Test material estimation calculation formula for Residential RCC."""
    req = MaterialEstimationRequest(
        project_type="Residential",
        built_up_area=2000.0,
        area_unit="sq_ft",
        floors=2,
        material_quality="Standard",
        construction_type="RCC",
        location="Test Site",
    )
    result = calculate_material_estimation(req)

    assert "materials" in result
    assert len(result["materials"]) == 10
    assert result["total_estimated_cost"] > 0
    assert "material_distribution" in result
    assert "cost_breakdown" in result

    # Verify key materials exist
    mat_names = [m["material_name"] for m in result["materials"]]
    assert "Cement" in mat_names
    assert "Steel" in mat_names
    assert "Concrete" in mat_names
    assert "Bricks" in mat_names


def test_service_calculation_sq_meters_and_luxury():
    """Test unit conversion from sq.m to sq.ft and Luxury multiplier scaling."""
    req = MaterialEstimationRequest(
        project_type="Commercial",
        built_up_area=500.0,
        area_unit="sq_m",
        floors=4,
        material_quality="Luxury",
        construction_type="Steel Structure",
    )
    result = calculate_material_estimation(req)

    assert result["project_summary"]["area_unit"] == "sq_m"
    assert result["project_summary"]["built_up_area_sqft"] > 5000.0  # 500 sq_m approx 5381 sq_ft
    assert result["total_estimated_cost"] > 0


def test_pdf_generation():
    """Test generating PDF report byte stream."""
    req = MaterialEstimationRequest(
        project_type="Industrial",
        built_up_area=3000.0,
        floors=1,
        material_quality="Premium",
        construction_type="Hybrid",
    )
    data = calculate_material_estimation(req)
    pdf_bytes = generate_estimation_pdf(data)

    assert isinstance(pdf_bytes, bytes)
    assert len(pdf_bytes) > 0
    assert pdf_bytes.startswith(b"%PDF")


def test_csv_generation():
    """Test generating CSV report string."""
    req = MaterialEstimationRequest(
        project_type="Residential",
        built_up_area=1500.0,
        floors=2,
        material_quality="Standard",
        construction_type="RCC",
    )
    data = calculate_material_estimation(req)
    csv_str = generate_estimation_csv(data)

    assert "CONSTRUCTION INTELLIGENT HUB - MATERIAL ESTIMATION REPORT" in csv_str
    assert "Cement" in csv_str
    assert "TOTAL ESTIMATED COST" in csv_str


def test_api_estimate_endpoint(client):
    """Test POST /api/v1/material-estimation/estimate API."""
    token = get_token("material_tester@example.com")
    headers = {"Authorization": f"Bearer {token}"}

    payload = {
        "project_type": "Residential",
        "built_up_area": 1200.0,
        "area_unit": "sq_ft",
        "floors": 2,
        "material_quality": "Standard",
        "construction_type": "RCC",
    }
    response = client.post("/api/v1/material-estimation/estimate", json=payload, headers=headers)
    assert response.status_code == 200
    res_data = response.json()
    assert "materials" in res_data
    assert len(res_data["materials"]) == 10
    assert res_data["total_estimated_cost"] > 0


def test_api_export_pdf_endpoint(client):
    """Test POST /api/v1/material-estimation/export-pdf API."""
    token = get_token("material_tester@example.com")
    headers = {"Authorization": f"Bearer {token}"}

    payload = {
        "project_type": "Commercial",
        "built_up_area": 2500.0,
        "floors": 3,
        "material_quality": "Premium",
        "construction_type": "RCC",
    }
    response = client.post("/api/v1/material-estimation/export-pdf", json=payload, headers=headers)
    assert response.status_code == 200
    assert response.headers["content-type"] == "application/pdf"
    assert response.content.startswith(b"%PDF")


def test_api_export_csv_endpoint(client):
    """Test POST /api/v1/material-estimation/export-csv API."""
    token = get_token("material_tester@example.com")
    headers = {"Authorization": f"Bearer {token}"}

    payload = {
        "project_type": "Industrial",
        "built_up_area": 5000.0,
        "floors": 1,
        "material_quality": "Standard",
        "construction_type": "Steel Structure",
    }
    response = client.post("/api/v1/material-estimation/export-csv", json=payload, headers=headers)
    assert response.status_code == 200
    assert "text/csv" in response.headers["content-type"]
    assert "ITEMIZED MATERIAL ESTIMATION" in response.text


def test_invalid_input_validation(client):
    """Test Pydantic validation rejects negative area or zero floors."""
    token = get_token("material_tester@example.com")
    headers = {"Authorization": f"Bearer {token}"}

    payload = {
        "project_type": "Residential",
        "built_up_area": -100.0,  # invalid
        "floors": 0,  # invalid
        "material_quality": "Standard",
        "construction_type": "RCC",
    }
    response = client.post("/api/v1/material-estimation/estimate", json=payload, headers=headers)
    assert response.status_code == 422
