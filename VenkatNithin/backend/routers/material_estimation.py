"""
backend/routers/material_estimation.py
----------------------------------------
FastAPI router for Material Estimation module.
Provides endpoints to compute material estimates, export PDF reports, and export CSV files.
"""
from fastapi import APIRouter, Depends, Response, HTTPException, status
from backend.models.user import User
from backend.routers.auth import get_current_user
from backend.schemas.material_estimation import (
    MaterialEstimationRequest,
    MaterialEstimationResponse,
)
from backend.services.material_estimation_service import (
    calculate_material_estimation,
    generate_estimation_pdf,
    generate_estimation_csv,
)

router = APIRouter(prefix="/api/v1/material-estimation", tags=["Material Estimation"])


@router.post("/estimate", response_model=MaterialEstimationResponse)
def estimate_materials(
    payload: MaterialEstimationRequest,
    current_user: User = Depends(get_current_user),
):
    """
    Calculate estimated material quantities, costs, and percentage distribution
    for a given project configuration.
    """
    try:
        result = calculate_material_estimation(payload)
        return result
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Material estimation calculation failed: {str(e)}",
        )


@router.post("/export-pdf")
def export_pdf(
    payload: MaterialEstimationRequest,
    current_user: User = Depends(get_current_user),
):
    """Generate and return downloadable PDF report byte stream."""
    try:
        estimation_data = calculate_material_estimation(payload)
        pdf_bytes = generate_estimation_pdf(estimation_data)
        return Response(
            content=pdf_bytes,
            media_type="application/pdf",
            headers={
                "Content-Disposition": "attachment; filename=Material_Estimation_Report.pdf"
            },
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"PDF generation failed: {str(e)}",
        )


@router.post("/export-csv")
def export_csv(
    payload: MaterialEstimationRequest,
    current_user: User = Depends(get_current_user),
):
    """Generate and return downloadable CSV report file."""
    try:
        estimation_data = calculate_material_estimation(payload)
        csv_content = generate_estimation_csv(estimation_data)
        return Response(
            content=csv_content,
            media_type="text/csv",
            headers={
                "Content-Disposition": "attachment; filename=Material_Estimation_Report.csv"
            },
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"CSV export failed: {str(e)}",
        )
