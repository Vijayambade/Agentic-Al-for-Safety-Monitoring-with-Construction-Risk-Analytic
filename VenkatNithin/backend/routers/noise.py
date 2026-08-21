"""
backend/routers/noise.py
------------------------
FastAPI router for noise levels tracking, sensor calibrations, and decibel breach alarms.
"""
import random
from typing import List, Dict, Any
from datetime import datetime
from fastapi import APIRouter, Depends, status, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field

from backend.database import get_db
from backend.models.user import User
from backend.models.noise import NoiseLog, NoiseConfig
from backend.routers.auth import get_current_user
from backend.services.dashboard_service import log_activity
from backend.services.noise_service import audit_decibel_reading

router = APIRouter(prefix="/api/v1/noise", tags=["Noise & Decibel Monitoring"])


class NoiseLogRequest(BaseModel):
    sensor_name: str = Field(..., pattern=r"^(Zone A \(Excavation Area\)|Zone B \(Structural Framing\)|Zone C \(Site Boundary\))$")
    decibel_level: float = Field(..., gt=0.0)


class NoiseConfigUpdateRequest(BaseModel):
    sensor_name: str = Field(..., pattern=r"^(Zone A \(Excavation Area\)|Zone B \(Structural Framing\)|Zone C \(Site Boundary\))$")
    daytime_limit: float = Field(..., gt=40.0, lt=120.0)
    nighttime_limit: float = Field(..., gt=30.0, lt=100.0)


class SimulateNoiseRequest(BaseModel):
    stress_intensity: float = Field(..., ge=0.0, le=1.0)


class NoiseLogResponse(BaseModel):
    id: int
    sensor_name: str
    decibel_level: float
    limit_threshold: float
    is_breached: bool
    logged_at: datetime

    class Config:
        from_attributes = True


class NoiseConfigResponse(BaseModel):
    id: int
    sensor_name: str
    daytime_limit: float
    nighttime_limit: float
    updated_at: datetime

    class Config:
        from_attributes = True


def initialize_noise_configs(db: Session) -> List[NoiseConfig]:
    """Helper to seed database with standard noise sensor configurations."""
    configs = [
        NoiseConfig(sensor_name="Zone A (Excavation Area)", daytime_limit=85.0, nighttime_limit=55.0),
        NoiseConfig(sensor_name="Zone B (Structural Framing)", daytime_limit=85.0, nighttime_limit=55.0),
        NoiseConfig(sensor_name="Zone C (Site Boundary)", daytime_limit=70.0, nighttime_limit=50.0),
    ]
    for config in configs:
        db.add(config)
    db.commit()
    return db.query(NoiseConfig).all()


@router.get("/logs", response_model=List[NoiseLogResponse])
def get_logs(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Retrieve historical decibel logs."""
    return db.query(NoiseLog).order_by(NoiseLog.logged_at.desc()).limit(150).all()


@router.get("/configs", response_model=List[NoiseConfigResponse])
def get_configs(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Retrieve decibel limits for all zones. Auto-initializes if empty."""
    configs = db.query(NoiseConfig).order_by(NoiseConfig.sensor_name.asc()).all()
    if not configs:
        configs = initialize_noise_configs(db)
    return configs


@router.post("/log", response_model=NoiseLogResponse)
def log_decibel(
    schema: NoiseLogRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Manually log a noise sensor readout. Triggers notifications if limits are breached."""
    db_configs = db.query(NoiseConfig).all()
    if not db_configs:
        initialize_noise_configs(db)

    log = audit_decibel_reading(db, schema.sensor_name, schema.decibel_level)

    # Log activity audit
    log_activity(
        db,
        current_user.id,
        current_user.role,
        "NOISE_LOG",
        f"Logged noise level for '{schema.sensor_name}': {schema.decibel_level} dB"
    )

    return log


@router.post("/simulate", response_model=List[NoiseLogResponse])
def simulate_noise(
    schema: SimulateNoiseRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Simulates noise levels across all 3 zones. High stress pushes decibels past safety limits."""
    db_configs = db.query(NoiseConfig).all()
    if not db_configs:
        initialize_noise_configs(db)

    zones = [
        "Zone A (Excavation Area)",
        "Zone B (Structural Framing)",
        "Zone C (Site Boundary)"
    ]

    generated_logs = []
    for zone in zones:
        # Pushes decibels depending on stress intensity
        base_db = 60.0 if zone != "Zone C (Site Boundary)" else 45.0
        peak_var = 45.0 * schema.stress_intensity
        rand_var = random.uniform(5.0, 15.0)
        
        simulated_db = round(base_db + peak_var + rand_var, 1)
        log = audit_decibel_reading(db, zone, simulated_db)
        generated_logs.append(log)

    # Log activity audit
    log_activity(
        db,
        current_user.id,
        current_user.role,
        "NOISE_SIMULATE",
        f"Simulated noise sensor feed (Stress: {int(schema.stress_intensity*100)}%)"
    )

    return generated_logs


@router.post("/config", response_model=NoiseConfigResponse)
def update_config(
    schema: NoiseConfigUpdateRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update daytime or nighttime decibel limits for a zone."""
    config = db.query(NoiseConfig).filter(NoiseConfig.sensor_name == schema.sensor_name).first()
    if not config:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Sensor zone configuration not found."
        )

    config.daytime_limit = schema.daytime_limit
    config.nighttime_limit = schema.nighttime_limit
    db.commit()
    db.refresh(config)

    # Log activity audit
    log_activity(
        db,
        current_user.id,
        current_user.role,
        "NOISE_CONFIG_UPDATE",
        f"Calibrated noise rules for '{schema.sensor_name}'. Daytime: {schema.daytime_limit} dB, Nighttime: {schema.nighttime_limit} dB"
    )

    return config


@router.post("/reset", response_model=List[NoiseConfigResponse])
def reset_noise(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Reverts config limits to baseline settings and clears log histories."""
    db.query(NoiseLog).delete()
    db.query(NoiseConfig).delete()
    db.commit()

    configs = initialize_noise_configs(db)

    log_activity(
        db,
        current_user.id,
        current_user.role,
        "NOISE_RESET",
        "Cleared decibel logs and restored baseline environmental rules."
    )

    return configs
