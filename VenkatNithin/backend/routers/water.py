"""
backend/routers/water.py
------------------------
FastAPI router for water flow telemetry, leakage checks, and pipeline thresholds.
"""
import random
from typing import List, Dict, Any
from datetime import datetime
from fastapi import APIRouter, Depends, status, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field

from backend.database import get_db
from backend.models.user import User
from backend.models.water_monitoring import WaterLog, WaterConfig
from backend.routers.auth import get_current_user
from backend.services.dashboard_service import log_activity
from backend.services.water_service import audit_water_reading

router = APIRouter(prefix="/api/v1/water", tags=["Water Flow & Leakage Monitoring"])


class WaterLogRequest(BaseModel):
    sensor_name: str = Field(..., pattern=r"^(Main Supply Inlet|Concrete Mixing Bay|Worker Quarters)$")
    flow_rate: float = Field(..., ge=0.0)
    pressure: float = Field(..., ge=0.0)
    cumulative_liters: float = Field(..., ge=0.0)


class WaterConfigRequest(BaseModel):
    sensor_name: str = Field(..., pattern=r"^(Main Supply Inlet|Concrete Mixing Bay|Worker Quarters)$")
    max_flow_limit: float = Field(..., gt=5.0, lt=500.0)
    min_pressure_limit: float = Field(..., gt=5.0, lt=400.0)


class SimulateWaterRequest(BaseModel):
    stress_intensity: float = Field(..., ge=0.0, le=1.0)


class WaterLogResponse(BaseModel):
    id: int
    sensor_name: str
    flow_rate: float
    pressure: float
    cumulative_liters: float
    is_anomaly: bool
    anomaly_type: str
    logged_at: datetime

    class Config:
        from_attributes = True


class WaterConfigResponse(BaseModel):
    id: int
    sensor_name: str
    max_flow_limit: float
    min_pressure_limit: float
    updated_at: datetime

    class Config:
        from_attributes = True


def initialize_water_configs(db: Session) -> List[WaterConfig]:
    """Helper to seed database with standard water sensor safety guidelines."""
    configs = [
        WaterConfig(sensor_name="Main Supply Inlet", max_flow_limit=120.0, min_pressure_limit=180.0),
        WaterConfig(sensor_name="Concrete Mixing Bay", max_flow_limit=80.0, min_pressure_limit=140.0),
        WaterConfig(sensor_name="Worker Quarters", max_flow_limit=60.0, min_pressure_limit=120.0),
    ]
    for config in configs:
        db.add(config)
    db.commit()
    return db.query(WaterConfig).all()


@router.get("/logs", response_model=List[WaterLogResponse])
def get_logs(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Retrieve historical water telemetry logs."""
    return db.query(WaterLog).order_by(WaterLog.logged_at.desc()).limit(150).all()


@router.get("/configs", response_model=List[WaterConfigResponse])
def get_configs(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Retrieve configs for all sensors. Auto-initializes if empty."""
    configs = db.query(WaterConfig).order_by(WaterConfig.sensor_name.asc()).all()
    if not configs:
        configs = initialize_water_configs(db)
    return configs


@router.post("/log", response_model=WaterLogResponse)
def log_water_reading(
    schema: WaterLogRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Log a manual water sensor reading. Audits limits and triggers alarms on leaks."""
    db_configs = db.query(WaterConfig).all()
    if not db_configs:
        initialize_water_configs(db)

    log = audit_water_reading(
        db,
        schema.sensor_name,
        schema.flow_rate,
        schema.pressure,
        schema.cumulative_liters
    )

    # Log activity audit
    log_activity(
        db,
        current_user.id,
        current_user.role,
        "WATER_LOG",
        f"Logged water reading for '{schema.sensor_name}': {schema.flow_rate} L/min, {schema.pressure} kPa"
    )

    return log


@router.post("/simulate", response_model=List[WaterLogResponse])
def simulate_water(
    schema: SimulateWaterRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Simulates water logs. High stress triggers leak scenario (low pressure, high flow)."""
    db_configs = db.query(WaterConfig).all()
    if not db_configs:
        initialize_water_configs(db)

    sensors = [
        "Main Supply Inlet",
        "Concrete Mixing Bay",
        "Worker Quarters"
    ]

    generated_logs = []
    for name in sensors:
        # Determine latest cumulative liters to increment
        last_log = db.query(WaterLog).filter(WaterLog.sensor_name == name).order_by(WaterLog.logged_at.desc()).first()
        prev_cumulative = last_log.cumulative_liters if last_log else 1000.0

        if schema.stress_intensity > 0.7:
            # Leak scenario: High flow rate, low pressure
            flow_val = round(random.uniform(130.0, 160.0), 1)
            pressure_val = round(random.uniform(50.0, 90.0), 1)
        else:
            # Normal fluctuation
            flow_val = round(random.uniform(30.0, 50.0), 1)
            pressure_val = round(random.uniform(200.0, 240.0), 1)

        added_liters = round(flow_val * 5.0, 1)  # assumed 5 minutes interval usage
        new_cumulative = prev_cumulative + added_liters

        log = audit_water_reading(
            db,
            name,
            flow_val,
            pressure_val,
            new_cumulative
        )
        generated_logs.append(log)

    # Log activity audit
    log_activity(
        db,
        current_user.id,
        current_user.role,
        "WATER_SIMULATE",
        f"Simulated water sensor grid readouts (Stress: {int(schema.stress_intensity*100)}%)"
    )

    return generated_logs


@router.post("/config", response_model=WaterConfigResponse)
def update_config(
    schema: WaterConfigRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Calibrate safety guidelines for a sensor location."""
    config = db.query(WaterConfig).filter(WaterConfig.sensor_name == schema.sensor_name).first()
    if not config:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Water sensor location configuration not found."
        )

    config.max_flow_limit = schema.max_flow_limit
    config.min_pressure_limit = schema.min_pressure_limit
    db.commit()
    db.refresh(config)

    # Log activity audit
    log_activity(
        db,
        current_user.id,
        current_user.role,
        "WATER_CONFIG_UPDATE",
        f"Calibrated water rules for '{schema.sensor_name}'. Max Flow: {schema.max_flow_limit}, Min Pressure: {schema.min_pressure_limit}"
    )

    return config


@router.post("/reset", response_model=List[WaterConfigResponse])
def reset_water(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Reverts configs to baselines and clears log histories."""
    db.query(WaterLog).delete()
    db.query(WaterConfig).delete()
    db.commit()

    configs = initialize_water_configs(db)

    log_activity(
        db,
        current_user.id,
        current_user.role,
        "WATER_RESET",
        "Cleared water logs and restored baseline safety guidelines."
    )

    return configs
