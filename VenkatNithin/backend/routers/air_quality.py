"""
backend/routers/air_quality.py
------------------------------
FastAPI router for air quality monitoring, gas concentration audits, and sensor simulations.
"""
import random
from typing import List, Dict, Any
from datetime import datetime
from fastapi import APIRouter, Depends, status, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field

from backend.database import get_db
from backend.models.user import User
from backend.models.air_quality import AirQualityLog, AirQualityConfig
from backend.routers.auth import get_current_user
from backend.services.dashboard_service import log_activity
from backend.services.air_quality_service import audit_air_quality_reading

router = APIRouter(prefix="/api/v1/air-quality", tags=["Air Quality & Gas Monitoring"])


class AirQualityLogRequest(BaseModel):
    sensor_name: str = Field(..., pattern=r"^(Excavation Tunnel A|Framing & Welding Zone B|Site Perimeter Zone C)$")
    aqi: float = Field(..., ge=0.0, le=500.0)
    pm25: float = Field(..., ge=0.0)
    pm10: float = Field(..., ge=0.0)
    co_level: float = Field(..., ge=0.0)
    no2_level: float = Field(..., ge=0.0)
    voc_level: float = Field(..., ge=0.0)


class AirQualityConfigRequest(BaseModel):
    sensor_name: str = Field(..., pattern=r"^(Excavation Tunnel A|Framing & Welding Zone B|Site Perimeter Zone C)$")
    pm25_limit: float = Field(..., gt=5.0, lt=200.0)
    co_limit: float = Field(..., gt=5.0, lt=150.0)
    voc_limit: float = Field(..., gt=1.0, lt=80.0)


class SimulateAirRequest(BaseModel):
    stress_intensity: float = Field(..., ge=0.0, le=1.0)


class AirQualityLogResponse(BaseModel):
    id: int
    sensor_name: str
    aqi: float
    pm25: float
    pm10: float
    co_level: float
    no2_level: float
    voc_level: float
    is_hazardous: bool
    hazard_reason: str
    logged_at: datetime

    class Config:
        from_attributes = True


class AirQualityConfigResponse(BaseModel):
    id: int
    sensor_name: str
    pm25_limit: float
    co_limit: float
    voc_limit: float
    updated_at: datetime

    class Config:
        from_attributes = True


def initialize_air_configs(db: Session) -> List[AirQualityConfig]:
    """Helper to seed database with standard air quality sensors limits configurations."""
    configs = [
        AirQualityConfig(sensor_name="Excavation Tunnel A", pm25_limit=50.0, co_limit=35.0, voc_limit=10.0),
        AirQualityConfig(sensor_name="Framing & Welding Zone B", pm25_limit=50.0, co_limit=25.0, voc_limit=12.0),
        AirQualityConfig(sensor_name="Site Perimeter Zone C", pm25_limit=35.0, co_limit=15.0, voc_limit=8.0),
    ]
    for config in configs:
        db.add(config)
    db.commit()
    return db.query(AirQualityConfig).all()


@router.get("/logs", response_model=List[AirQualityLogResponse])
def get_logs(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Retrieve historical air logs."""
    return db.query(AirQualityLog).order_by(AirQualityLog.logged_at.desc()).limit(150).all()


@router.get("/configs", response_model=List[AirQualityConfigResponse])
def get_configs(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Retrieve limits for all sensors. Auto-initializes if empty."""
    configs = db.query(AirQualityConfig).order_by(AirQualityConfig.sensor_name.asc()).all()
    if not configs:
        configs = initialize_air_configs(db)
    return configs


@router.post("/log", response_model=AirQualityLogResponse)
def log_air_reading(
    schema: AirQualityLogRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Manually log air quality readouts. Checks safety limits and dispatches alarms."""
    db_configs = db.query(AirQualityConfig).all()
    if not db_configs:
        initialize_air_configs(db)

    log = audit_air_quality_reading(
        db,
        schema.sensor_name,
        schema.aqi,
        schema.pm25,
        schema.pm10,
        schema.co_level,
        schema.no2_level,
        schema.voc_level
    )

    # Log activity audit
    log_activity(
        db,
        current_user.id,
        current_user.role,
        "AIR_LOG",
        f"Manually logged air reading for '{schema.sensor_name}': AQI {schema.aqi}, PM2.5 {schema.pm25}"
    )

    return log


@router.post("/simulate", response_model=List[AirQualityLogResponse])
def simulate_air(
    schema: SimulateAirRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Simulate operational sound/gas sensor outputs. Spikes values on high stress."""
    db_configs = db.query(AirQualityConfig).all()
    if not db_configs:
        initialize_air_configs(db)

    sensors = [
        "Excavation Tunnel A",
        "Framing & Welding Zone B",
        "Site Perimeter Zone C"
    ]

    generated_logs = []
    for name in sensors:
        # Increase values depending on stress factor
        base_pm25 = 12.0
        base_co = 2.0
        base_voc = 1.0
        base_aqi = 40.0
        
        # High stress spikes values
        pm_val = round(base_pm25 + (90.0 * schema.stress_intensity) + random.uniform(1.0, 10.0), 1)
        co_val = round(base_co + (60.0 * schema.stress_intensity) + random.uniform(0.5, 5.0), 1)
        voc_val = round(base_voc + (20.0 * schema.stress_intensity) + random.uniform(0.2, 2.0), 1)
        aqi_val = round(base_aqi + (180.0 * schema.stress_intensity) + random.uniform(5.0, 20.0), 1)
        pm10_val = round(pm_val * 1.5, 1)
        no2_val = round(co_val * 0.1, 2)

        log = audit_air_quality_reading(
            db,
            name,
            aqi_val,
            pm_val,
            pm10_val,
            co_val,
            no2_val,
            voc_val
        )
        generated_logs.append(log)

    # Log activity audit
    log_activity(
        db,
        current_user.id,
        current_user.role,
        "AIR_SIMULATE",
        f"Simulated air sensor readouts (Stress: {int(schema.stress_intensity*100)}%)"
    )

    return generated_logs


@router.post("/config", response_model=AirQualityConfigResponse)
def update_config(
    schema: AirQualityConfigRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Calibrate safety thresholds for a sensor zone."""
    config = db.query(AirQualityConfig).filter(AirQualityConfig.sensor_name == schema.sensor_name).first()
    if not config:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Sensor zone config not found."
        )

    config.pm25_limit = schema.pm25_limit
    config.co_limit = schema.co_limit
    config.voc_limit = schema.voc_limit
    db.commit()
    db.refresh(config)

    # Log activity audit
    log_activity(
        db,
        current_user.id,
        current_user.role,
        "AIR_CONFIG_UPDATE",
        f"Calibrated air safety limits for '{schema.sensor_name}'. PM2.5: {schema.pm25_limit}, CO: {schema.co_limit}, VOC: {schema.voc_limit}"
    )

    return config


@router.post("/reset", response_model=List[AirQualityConfigResponse])
def reset_air_quality(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Clears sensor readings and reverts limits to baselines."""
    db.query(AirQualityLog).delete()
    db.query(AirQualityConfig).delete()
    db.commit()

    configs = initialize_air_configs(db)

    log_activity(
        db,
        current_user.id,
        current_user.role,
        "AIR_RESET",
        "Cleared air quality log histories and restored baseline safety guidelines."
    )

    return configs
