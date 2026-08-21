"""
backend/routers/energy.py
-------------------------
FastAPI router for smart construction energy telemetry, safety checks, and calibrations.
"""
import random
from typing import List, Dict, Any
from datetime import datetime
from fastapi import APIRouter, Depends, status, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field

from backend.database import get_db
from backend.models.user import User
from backend.models.energy import EnergyLog, EnergyConfig
from backend.routers.auth import get_current_user
from backend.services.dashboard_service import log_activity
from backend.services.energy_service import audit_energy_reading

router = APIRouter(prefix="/api/v1/energy", tags=["Smart Energy Monitoring"])


class EnergyLogRequest(BaseModel):
    sensor_name: str = Field(..., pattern=r"^(Heavy Tower Cranes|Concrete Batch Plant|High-Intensity Site Lighting|Main Site Offices)$")
    power_usage: float = Field(..., ge=0.0)
    voltage: float = Field(..., ge=0.0)
    current: float = Field(..., ge=0.0)
    power_factor: float = Field(..., ge=0.0, le=1.0)
    cumulative_kwh: float = Field(..., ge=0.0)


class EnergyConfigRequest(BaseModel):
    sensor_name: str = Field(..., pattern=r"^(Heavy Tower Cranes|Concrete Batch Plant|High-Intensity Site Lighting|Main Site Offices)$")
    max_power_limit: float = Field(..., gt=5.0, lt=1000.0)
    min_voltage_limit: float = Field(..., gt=50.0, lt=500.0)
    min_power_factor_limit: float = Field(..., ge=0.5, le=1.0)


class SimulateEnergyRequest(BaseModel):
    stress_intensity: float = Field(..., ge=0.0, le=1.0)


class EnergyLogResponse(BaseModel):
    id: int
    sensor_name: str
    power_usage: float
    voltage: float
    current: float
    power_factor: float
    cumulative_kwh: float
    is_anomaly: bool
    anomaly_type: str
    logged_at: datetime

    class Config:
        from_attributes = True


class EnergyConfigResponse(BaseModel):
    id: int
    sensor_name: str
    max_power_limit: float
    min_voltage_limit: float
    min_power_factor_limit: float
    updated_at: datetime

    class Config:
        from_attributes = True


def initialize_energy_configs(db: Session) -> List[EnergyConfig]:
    """Helper to seed database with standard smart meter safety guidelines."""
    configs = [
        EnergyConfig(sensor_name="Heavy Tower Cranes", max_power_limit=200.0, min_voltage_limit=210.0, min_power_factor_limit=0.85),
        EnergyConfig(sensor_name="Concrete Batch Plant", max_power_limit=150.0, min_voltage_limit=210.0, min_power_factor_limit=0.85),
        EnergyConfig(sensor_name="High-Intensity Site Lighting", max_power_limit=50.0, min_voltage_limit=200.0, min_power_factor_limit=0.80),
        EnergyConfig(sensor_name="Main Site Offices", max_power_limit=40.0, min_voltage_limit=215.0, min_power_factor_limit=0.88),
    ]
    for config in configs:
        db.add(config)
    db.commit()
    return db.query(EnergyConfig).all()


@router.get("/logs", response_model=List[EnergyLogResponse])
def get_logs(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Retrieve historical energy logs."""
    return db.query(EnergyLog).order_by(EnergyLog.logged_at.desc()).limit(150).all()


@router.get("/configs", response_model=List[EnergyConfigResponse])
def get_configs(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Retrieve configs for all smart meters. Auto-initializes if empty."""
    configs = db.query(EnergyConfig).order_by(EnergyConfig.sensor_name.asc()).all()
    if not configs:
        configs = initialize_energy_configs(db)
    return configs


@router.post("/log", response_model=EnergyLogResponse)
def log_energy_reading(
    schema: EnergyLogRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Log manual energy smart meter readings. Audits safety parameters and raises overload alarms."""
    db_configs = db.query(EnergyConfig).all()
    if not db_configs:
        initialize_energy_configs(db)

    log = audit_energy_reading(
        db,
        schema.sensor_name,
        schema.power_usage,
        schema.voltage,
        schema.current,
        schema.power_factor,
        schema.cumulative_kwh
    )

    # Log activity audit
    log_activity(
        db,
        current_user.id,
        current_user.role,
        "ENERGY_LOG",
        f"Logged energy metrics for '{schema.sensor_name}': {schema.power_usage} kW, PF: {schema.power_factor}"
    )

    return log


@router.post("/simulate", response_model=List[EnergyLogResponse])
def simulate_energy(
    schema: SimulateEnergyRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Simulates smart meter readings. High stress triggers power overload and efficiency drop scenarios."""
    db_configs = db.query(EnergyConfig).all()
    if not db_configs:
        initialize_energy_configs(db)

    sensors = [
        "Heavy Tower Cranes",
        "Concrete Batch Plant",
        "High-Intensity Site Lighting",
        "Main Site Offices"
    ]

    generated_logs = []
    for name in sensors:
        # Determine latest cumulative kwh to increment
        last_log = db.query(EnergyLog).filter(EnergyLog.sensor_name == name).order_by(EnergyLog.logged_at.desc()).first()
        prev_cumulative = last_log.cumulative_kwh if last_log else 500.0

        if schema.stress_intensity > 0.7:
            # Overload / Low Efficiency state
            pow_val = round(random.uniform(160.0, 240.0) if name in ["Heavy Tower Cranes", "Concrete Batch Plant"] else random.uniform(55.0, 75.0), 1)
            pf_val = round(random.uniform(0.65, 0.82), 2)
            volt_val = round(random.uniform(190.0, 208.0), 1)
        else:
            # Optimal running state
            pow_val = round(random.uniform(60.0, 110.0) if name in ["Heavy Tower Cranes", "Concrete Batch Plant"] else random.uniform(15.0, 35.0), 1)
            pf_val = round(random.uniform(0.88, 0.97), 2)
            volt_val = round(random.uniform(220.0, 240.0), 1)

        curr_val = round((pow_val * 1000.0) / (volt_val * 1.732 * pf_val), 1)  # Assumed 3-phase calculation
        added_kwh = round(pow_val * (5.0 / 60.0), 2)  # assumed 5 minutes interval consumption
        new_cumulative = prev_cumulative + added_kwh

        log = audit_energy_reading(
            db,
            name,
            pow_val,
            volt_val,
            curr_val,
            pf_val,
            new_cumulative
        )
        generated_logs.append(log)

    # Log activity audit
    log_activity(
        db,
        current_user.id,
        current_user.role,
        "ENERGY_SIMULATE",
        f"Simulated energy grid smart meter readouts (Stress: {int(schema.stress_intensity*100)}%)"
    )

    return generated_logs


@router.post("/config", response_model=EnergyConfigResponse)
def update_config(
    schema: EnergyConfigRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Calibrate safety thresholds for a smart meter area."""
    config = db.query(EnergyConfig).filter(EnergyConfig.sensor_name == schema.sensor_name).first()
    if not config:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Energy sensor location configuration not found."
        )

    config.max_power_limit = schema.max_power_limit
    config.min_voltage_limit = schema.min_voltage_limit
    config.min_power_factor_limit = schema.min_power_factor_limit
    db.commit()
    db.refresh(config)

    # Log activity audit
    log_activity(
        db,
        current_user.id,
        current_user.role,
        "ENERGY_CONFIG_UPDATE",
        f"Calibrated energy rules for '{schema.sensor_name}'. Max Power: {schema.max_power_limit} kW"
    )

    return config


@router.post("/reset", response_model=List[EnergyConfigResponse])
def reset_energy(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Reverts config limits to baseline parameters and clears log histories."""
    db.query(EnergyLog).delete()
    db.query(EnergyConfig).delete()
    db.commit()

    configs = initialize_energy_configs(db)

    log_activity(
        db,
        current_user.id,
        current_user.role,
        "ENERGY_RESET",
        "Cleared energy logs and restored baseline safety guidelines."
    )

    return configs
