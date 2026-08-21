"""
backend/routers/telematics.py
----------------------------
FastAPI router for IoT equipment telematics and predictive maintenance alerts.
"""
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
from fastapi import APIRouter, Depends, status, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel

from backend.database import get_db
from backend.models.user import User
from backend.models.telematics import EquipmentTelemetry
from backend.routers.auth import get_current_user
from backend.services.dashboard_service import log_activity
from backend.services.telematics_service import (
    calculate_equipment_health,
    simulate_sensor_fluctuations,
)

router = APIRouter(prefix="/api/v1/telematics", tags=["Equipment Telematics"])


class SimulateRequest(BaseModel):
    stress_intensity: float  # 0.0 to 1.0


class MaintenanceScheduleRequest(BaseModel):
    equipment_id: int
    scheduled_date: str  # ISO string or date representation


class EquipmentTelemetryResponse(BaseModel):
    id: int
    name: str
    status: str
    gps_latitude: float
    gps_longitude: float
    fuel_level: float
    engine_temp: float
    operating_hours: float
    vibration_level: float
    predicted_failure: bool
    failure_probability: float
    maintenance_scheduled_at: Optional[datetime] = None
    health_score: float

    class Config:
        from_attributes = True


def initialize_telematics_fleet(db: Session) -> List[EquipmentTelemetry]:
    """Helper to initialize the database with 4 baseline construction vehicles."""
    baseline_fleet = [
        EquipmentTelemetry(
            id=1,
            name="Excavator #101",
            status="Active",
            gps_latitude=17.4485,
            gps_longitude=78.3741,
            fuel_level=82.0,
            engine_temp=82.0,
            operating_hours=245.0,
            vibration_level=2.2,
            predicted_failure=False,
            failure_probability=0.0,
            health_score=100.0
        ),
        EquipmentTelemetry(
            id=2,
            name="Tower Crane #202",
            status="Active",
            gps_latitude=17.4490,
            gps_longitude=78.3748,
            fuel_level=95.0,
            engine_temp=78.0,
            operating_hours=120.0,
            vibration_level=1.8,
            predicted_failure=False,
            failure_probability=0.0,
            health_score=100.0
        ),
        EquipmentTelemetry(
            id=3,
            name="Bulldozer #303",
            status="Idle",
            gps_latitude=17.4480,
            gps_longitude=78.3735,
            fuel_level=45.0,
            engine_temp=65.0,
            operating_hours=410.0,
            vibration_level=0.8,
            predicted_failure=False,
            failure_probability=0.0,
            health_score=100.0
        ),
        EquipmentTelemetry(
            id=4,
            name="Concrete Mixer #404",
            status="Active",
            gps_latitude=17.4498,
            gps_longitude=78.3752,
            fuel_level=68.0,
            engine_temp=88.0,
            operating_hours=315.0,
            vibration_level=4.8,
            predicted_failure=False,
            failure_probability=0.0,
            health_score=100.0
        )
    ]

    for eq in baseline_fleet:
        calculate_equipment_health(eq)
        db.add(eq)
    db.commit()

    return db.query(EquipmentTelemetry).all()


@router.get("/equipment", response_model=List[EquipmentTelemetryResponse])
def get_equipment(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Retrieve telematics parameters for all vehicles. Auto-initializes if empty."""
    fleet = db.query(EquipmentTelemetry).order_by(EquipmentTelemetry.id.asc()).all()
    if not fleet:
        fleet = initialize_telematics_fleet(db)
    return fleet


@router.post("/simulate", response_model=List[EquipmentTelemetryResponse])
def simulate_sensor_changes(
    schema: SimulateRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Simulates sensor fluctuations (dropping fuel, rising temps and vibrations)."""
    fleet = db.query(EquipmentTelemetry).order_by(EquipmentTelemetry.id.asc()).all()
    if not fleet:
        fleet = initialize_telematics_fleet(db)

    simulate_sensor_fluctuations(fleet, schema.stress_intensity)
    db.commit()

    # Log activity audit
    log_activity(
        db,
        current_user.id,
        current_user.role,
        "TELEMETRY_SIMULATE",
        f"Triggered sensor telemetry simulation (Stress: {int(schema.stress_intensity*100)}%)"
    )

    return fleet


@router.post("/schedule-maintenance", response_model=EquipmentTelemetryResponse)
def schedule_maintenance(
    schema: MaintenanceScheduleRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Schedule custom maintenance date for a vehicle."""
    eq = db.query(EquipmentTelemetry).filter(EquipmentTelemetry.id == schema.equipment_id).first()
    if not eq:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Equipment not found."
        )

    # Update date and status
    try:
        parsed_date = datetime.fromisoformat(schema.scheduled_date.replace("Z", "+00:00"))
    except ValueError:
        parsed_date = datetime.utcnow() + timedelta(days=2)

    eq.maintenance_scheduled_at = parsed_date
    eq.status = "Scheduled"
    db.commit()
    db.refresh(eq)

    # Log activity audit
    log_activity(
        db,
        current_user.id,
        current_user.role,
        "EQUIPMENT_SCHEDULE",
        f"Scheduled service maintenance for '{eq.name}' on {parsed_date.strftime('%Y-%m-%d')}"
    )

    return eq


@router.post("/reset", response_model=List[EquipmentTelemetryResponse])
def reset_fleet(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Resets all vehicles to healthy baseline settings."""
    db.query(EquipmentTelemetry).delete()
    db.commit()

    fleet = initialize_telematics_fleet(db)

    log_activity(
        db,
        current_user.id,
        current_user.role,
        "TELEMETRY_RESET",
        "Reverted telematics fleet to normal baseline parameters."
    )

    return fleet
