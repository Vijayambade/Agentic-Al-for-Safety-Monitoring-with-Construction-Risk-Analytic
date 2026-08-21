"""
backend/routers/safety.py
-------------------------
FastAPI router for safety operations, incident logs, checklists, and emergency procedures.
"""
from typing import List, Any
from datetime import datetime
from fastapi import APIRouter, Depends, status, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field

from backend.database import get_db
from backend.models.user import User
from backend.models.safety import SafetyIncident
from backend.routers.auth import get_current_user
from backend.services.dashboard_service import log_activity
from backend.services.safety_service import (
    call_safety_llm,
    get_default_checklist,
    get_emergency_sop,
)

router = APIRouter(prefix="/api/v1/safety", tags=["Site Safety Assistant"])


class SafetyChatRequest(BaseModel):
    message: str
    is_emergency: bool = False


class IncidentCreate(BaseModel):
    hazard_description: str = Field(..., min_length=5, max_length=500)
    severity: str = Field(..., pattern="^(Low Warning|Medium Risk|High Critical)$")


class IncidentResponse(BaseModel):
    id: int
    reporter_id: int
    hazard_description: str
    severity: str
    status: str
    created_at: Any

    class Config:
        from_attributes = True


@router.post("/chat")
def safety_chat(
    schema: SafetyChatRequest,
    current_user: User = Depends(get_current_user)
):
    """Query the safety advisor AI chatbot."""
    reply = call_safety_llm(schema.message, schema.is_emergency)
    return {"response": reply}


@router.post("/incidents", status_code=status.HTTP_201_CREATED)
def report_incident(
    schema: IncidentCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """File a new safety hazard or incident report."""
    incident = SafetyIncident(
        reporter_id=current_user.id,
        hazard_description=schema.hazard_description,
        severity=schema.severity,
        status="Open"
    )
    db.add(incident)
    db.commit()
    db.refresh(incident)

    # Log dashboard activity audit
    log_activity(
        db,
        current_user.id,
        current_user.role,
        "HAZARD_REPORT",
        f"Logged hazard: '{incident.hazard_description}' [Severity: {incident.severity}]"
    )

    return {
        "id": incident.id,
        "reporter_id": incident.reporter_id,
        "hazard_description": incident.hazard_description,
        "severity": incident.severity,
        "status": incident.status,
        "created_at": incident.created_at
    }


@router.get("/checklist", response_model=List[str])
def get_checklist(
    activity: str,
    current_user: User = Depends(get_current_user)
):
    """Get active safety checklist items based on activity type."""
    return get_default_checklist(activity)


@router.get("/emergency-sop")
def get_sop(
    incident_type: str,
    current_user: User = Depends(get_current_user)
):
    """Retrieve first-response manual instructions for emergencies."""
    sop_content = get_emergency_sop(incident_type)
    return {"sop": sop_content}
