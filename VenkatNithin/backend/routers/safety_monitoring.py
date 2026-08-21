"""
backend/routers/safety_monitoring.py
------------------------------------
FastAPI router for onsite safety monitoring and automated PPE compliance camera feeds.
"""
from typing import List, Dict, Any
from fastapi import APIRouter, Depends, UploadFile, File, status, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel

from backend.database import get_db
from backend.models.user import User
from backend.models.dashboard import SystemNotification
from backend.routers.auth import get_current_user
from backend.services.detection_service import analyze_ppe_image
from backend.services.dashboard_service import log_activity

router = APIRouter(prefix="/api/v1/safety-monitoring", tags=["Safety Monitoring"])


class PPEDetectionResponse(BaseModel):
    compliance_score: int
    detected_gear: List[str]
    missing_gear: List[str]
    violations: List[str]
    annotated_image: str  # Base64 image data URI string


@router.post("/detect", response_model=PPEDetectionResponse)
async def detect_ppe_violations(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Upload a site webcam snap or photo.
    Detects safety gear violations and raises automatic alarm notifications.
    """
    file_bytes = await file.read()
    filename = file.filename

    try:
        results = analyze_ppe_image(file_bytes, filename)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Image detection processing failed: {str(e)}"
        )

    # If violations are present, trigger system alarms
    missing = results["missing_gear"]
    if missing:
        missing_str = ", ".join(missing)
        score = results["compliance_score"]
        
        notification = SystemNotification(
            title="🚨 Critical PPE Safety Violation",
            message=f"Image '{filename}' failed compliance check with score {score}%. Missing gear: {missing_str}."
        )
        db.add(notification)
        
        # 2. Log activity audit
        log_activity(
            db,
            current_user.id,
            current_user.role,
            "PPE_VIOLATION",
            f"PPE Alarm on '{filename}'. Score: {score}%. Missing: {missing_str}."
        )
        db.commit()

    return results
