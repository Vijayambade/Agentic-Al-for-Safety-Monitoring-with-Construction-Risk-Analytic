"""
backend/routers/structural.py
-----------------------------
FastAPI router for structural health telemetry, stress checks, and sensor safety thresholds.
"""
import random
from typing import List, Dict, Any
from datetime import datetime
from fastapi import APIRouter, Depends, status, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field

from backend.database import get_db
from backend.models.user import User
from backend.models.structural_health import StructuralLog, StructuralConfig
from backend.routers.auth import get_current_user
from backend.services.dashboard_service import log_activity
from backend.services.structural_service import audit_structural_reading

router = APIRouter(prefix="/api/v1/structural", tags=["Structural Health Monitoring"])


class StructuralLogRequest(BaseModel):
    sensor_name: str = Field(..., pattern=r"^(Scaffolding Tower Zone A|Concrete Formwork Zone B|Foundation Column Pier C)$")
    vibration_frequency: float = Field(..., ge=0.0)
    amplitude: float = Field(..., ge=0.0)
    tilt_angle: float = Field(..., ge=0.0)
    strain: float = Field(..., ge=0.0)


class StructuralConfigRequest(BaseModel):
    sensor_name: str = Field(..., pattern=r"^(Scaffolding Tower Zone A|Concrete Formwork Zone B|Foundation Column Pier C)$")
    max_vibration_frequency: float = Field(..., gt=5.0, lt=200.0)
    max_tilt_angle: float = Field(..., gt=1.0, lt=45.0)
    max_strain: float = Field(..., gt=10.0, lt=1000.0)


class SimulateStructuralRequest(BaseModel):
    stress_intensity: float = Field(..., ge=0.0, le=1.0)


class StructuralLogResponse(BaseModel):
    id: int
    sensor_name: str
    vibration_frequency: float
    amplitude: float
    tilt_angle: float
    strain: float
    is_unstable: bool
    instability_reason: str
    logged_at: datetime

    class Config:
        from_attributes = True


class StructuralConfigResponse(BaseModel):
    id: int
    sensor_name: str
    max_vibration_frequency: float
    max_tilt_angle: float
    max_strain: float
    updated_at: datetime

    class Config:
        from_attributes = True


def initialize_structural_configs(db: Session) -> List[StructuralConfig]:
    """Helper to seed database with standard structural safety guidelines."""
    configs = [
        StructuralConfig(sensor_name="Scaffolding Tower Zone A", max_vibration_frequency=50.0, max_tilt_angle=5.0, max_strain=300.0),
        StructuralConfig(sensor_name="Concrete Formwork Zone B", max_vibration_frequency=40.0, max_tilt_angle=4.0, max_strain=250.0),
        StructuralConfig(sensor_name="Foundation Column Pier C", max_vibration_frequency=30.0, max_tilt_angle=3.0, max_strain=200.0),
    ]
    for config in configs:
        db.add(config)
    db.commit()
    return db.query(StructuralConfig).all()


@router.get("/logs", response_model=List[StructuralLogResponse])
def get_logs(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Retrieve historical structural logs."""
    return db.query(StructuralLog).order_by(StructuralLog.logged_at.desc()).limit(150).all()


@router.get("/configs", response_model=List[StructuralConfigResponse])
def get_configs(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Retrieve configs for all sensors. Auto-initializes if empty."""
    configs = db.query(StructuralConfig).order_by(StructuralConfig.sensor_name.asc()).all()
    if not configs:
        configs = initialize_structural_configs(db)
    return configs


@router.post("/log", response_model=StructuralLogResponse)
def log_structural_reading(
    schema: StructuralLogRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Log manual structural safety variables. Evaluates limits and triggers warnings on collapse hazards."""
    db_configs = db.query(StructuralConfig).all()
    if not db_configs:
        initialize_structural_configs(db)

    log = audit_structural_reading(
        db,
        schema.sensor_name,
        schema.vibration_frequency,
        schema.amplitude,
        schema.tilt_angle,
        schema.strain
    )

    # Log activity audit
    log_activity(
        db,
        current_user.id,
        current_user.role,
        "STRUCTURAL_LOG",
        f"Logged structural variables for '{schema.sensor_name}': {schema.vibration_frequency} Hz, {schema.tilt_angle}°"
    )

    return log


@router.post("/simulate", response_model=List[StructuralLogResponse])
def simulate_structural(
    schema: SimulateStructuralRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Simulates structural load/strain readings. High stress triggers spiky vibration/tilt instability."""
    db_configs = db.query(StructuralConfig).all()
    if not db_configs:
        initialize_structural_configs(db)

    sensors = [
        "Scaffolding Tower Zone A",
        "Concrete Formwork Zone B",
        "Foundation Column Pier C"
    ]

    generated_logs = []
    for name in sensors:
        # Pushes variables depending on stress factor
        base_vib = 10.0
        base_tilt = 0.5
        base_strain = 40.0
        
        # High stress triggers structural instability warnings
        vib_val = round(base_vib + (65.0 * schema.stress_intensity) + random.uniform(1.0, 5.0), 1)
        amp_val = round(random.uniform(0.1, 2.0) * (1.0 + 5.0 * schema.stress_intensity), 2)
        tilt_val = round(base_tilt + (6.0 * schema.stress_intensity) + random.uniform(0.1, 0.5), 2)
        strain_val = round(base_strain + (400.0 * schema.stress_intensity) + random.uniform(5.0, 15.0), 1)

        log = audit_structural_reading(
            db,
            name,
            vib_val,
            amp_val,
            tilt_val,
            strain_val
        )
        generated_logs.append(log)

    # Log activity audit
    log_activity(
        db,
        current_user.id,
        current_user.role,
        "STRUCTURAL_SIMULATE",
        f"Simulated structural health grid readouts (Stress: {int(schema.stress_intensity*100)}%)"
    )

    return generated_logs


@router.post("/config", response_model=StructuralConfigResponse)
def update_config(
    schema: StructuralConfigRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Calibrate safety guidelines for a structural component sensor."""
    config = db.query(StructuralConfig).filter(StructuralConfig.sensor_name == schema.sensor_name).first()
    if not config:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Structural sensor configuration not found."
        )

    config.max_vibration_frequency = schema.max_vibration_frequency
    config.max_tilt_angle = schema.max_tilt_angle
    config.max_strain = schema.max_strain
    db.commit()
    db.refresh(config)

    # Log activity audit
    log_activity(
        db,
        current_user.id,
        current_user.role,
        "STRUCTURAL_CONFIG_UPDATE",
        f"Calibrated structural safety limits for '{schema.sensor_name}'."
    )

    return config


@router.post("/reset", response_model=List[StructuralConfigResponse])
def reset_structural(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Reverts config limits to baseline guidelines and clears log histories."""
    db.query(StructuralLog).delete()
    db.query(StructuralConfig).delete()
    db.commit()

    configs = initialize_structural_configs(db)

    log_activity(
        db,
        current_user.id,
        current_user.role,
        "STRUCTURAL_RESET",
        "Cleared structural safety logs and restored baseline structural safety guidelines."
    )

    return configs
