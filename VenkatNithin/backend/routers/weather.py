"""
backend/routers/weather.py
--------------------------
FastAPI router for weather telemetry, safety checks, and threshold configs.
"""
import random
from typing import List, Dict, Any
from datetime import datetime
from fastapi import APIRouter, Depends, status, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field

from backend.database import get_db
from backend.models.user import User
from backend.models.weather_hazards import WeatherLog, WeatherConfig
from backend.routers.auth import get_current_user
from backend.services.dashboard_service import log_activity
from backend.services.weather_service import audit_weather_reading

router = APIRouter(prefix="/api/v1/weather", tags=["Weather Hazards Predictor"])


class WeatherLogRequest(BaseModel):
    sensor_name: str = Field(..., pattern=r"^(Tower Crane Jib Peak|Ground Weather Station|Perimeter Boundary Mast)$")
    temperature: float = Field(..., ge=-30.0, le=60.0)
    wind_speed: float = Field(..., ge=0.0, le=250.0)
    humidity: float = Field(..., ge=0.0, le=100.0)
    precipitation: float = Field(..., ge=0.0, le=500.0)
    barometric_pressure: float = Field(..., ge=800.0, le=1200.0)
    uv_index: float = Field(..., ge=0.0, le=15.0)


class WeatherConfigRequest(BaseModel):
    sensor_name: str = Field(..., pattern=r"^(Tower Crane Jib Peak|Ground Weather Station|Perimeter Boundary Mast)$")
    max_wind_speed_limit: float = Field(..., gt=5.0, lt=150.0)
    max_temp_limit: float = Field(..., gt=15.0, lt=55.0)
    max_precipitation_limit: float = Field(..., gt=5.0, lt=200.0)


class SimulateWeatherRequest(BaseModel):
    stress_intensity: float = Field(..., ge=0.0, le=1.0)


class WeatherLogResponse(BaseModel):
    id: int
    sensor_name: str
    temperature: float
    wind_speed: float
    humidity: float
    precipitation: float
    barometric_pressure: float
    uv_index: float
    is_hazardous: bool
    hazard_types: str
    logged_at: datetime

    class Config:
        from_attributes = True


class WeatherConfigResponse(BaseModel):
    id: int
    sensor_name: str
    max_wind_speed_limit: float
    max_temp_limit: float
    max_precipitation_limit: float
    updated_at: datetime

    class Config:
        from_attributes = True


def initialize_weather_configs(db: Session) -> List[WeatherConfig]:
    """Helper to seed database with standard weather guidelines."""
    configs = [
        WeatherConfig(sensor_name="Tower Crane Jib Peak", max_wind_speed_limit=40.0, max_temp_limit=38.0, max_precipitation_limit=50.0),
        WeatherConfig(sensor_name="Ground Weather Station", max_wind_speed_limit=35.0, max_temp_limit=37.0, max_precipitation_limit=45.0),
        WeatherConfig(sensor_name="Perimeter Boundary Mast", max_wind_speed_limit=45.0, max_temp_limit=39.0, max_precipitation_limit=60.0),
    ]
    for config in configs:
        db.add(config)
    db.commit()
    return db.query(WeatherConfig).all()


@router.get("/logs", response_model=List[WeatherLogResponse])
def get_logs(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Retrieve historical weather logs."""
    return db.query(WeatherLog).order_by(WeatherLog.logged_at.desc()).limit(150).all()


@router.get("/configs", response_model=List[WeatherConfigResponse])
def get_configs(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Retrieve configs for all sensors. Auto-initializes if empty."""
    configs = db.query(WeatherConfig).order_by(WeatherConfig.sensor_name.asc()).all()
    if not configs:
        configs = initialize_weather_configs(db)
    return configs


@router.post("/log", response_model=WeatherLogResponse)
def log_weather_reading(
    schema: WeatherLogRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Log manual weather parameters. Evaluates limits and dispatches alarms on extreme threat hazards."""
    db_configs = db.query(WeatherConfig).all()
    if not db_configs:
        initialize_weather_configs(db)

    log = audit_weather_reading(
        db,
        schema.sensor_name,
        schema.temperature,
        schema.wind_speed,
        schema.humidity,
        schema.precipitation,
        schema.barometric_pressure,
        schema.uv_index
    )

    # Log activity audit
    log_activity(
        db,
        current_user.id,
        current_user.role,
        "WEATHER_LOG",
        f"Logged weather variables for '{schema.sensor_name}': {schema.temperature}°C, {schema.wind_speed} km/h"
    )

    return log


@router.post("/simulate", response_model=List[WeatherLogResponse])
def simulate_weather(
    schema: SimulateWeatherRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Simulates weather fluctuations. High stress triggers spiky wind/rain storm hazard scenarios."""
    db_configs = db.query(WeatherConfig).all()
    if not db_configs:
        initialize_weather_configs(db)

    sensors = [
        "Tower Crane Jib Peak",
        "Ground Weather Station",
        "Perimeter Boundary Mast"
    ]

    generated_logs = []
    for name in sensors:
        # Pushes variables depending on stress factor
        base_temp = 25.0
        base_wind = 12.0
        base_hum = 55.0
        base_rain = 0.0
        
        # High stress triggers storm/wind/heat threats
        temp_val = round(base_temp + (15.0 * schema.stress_intensity) + random.uniform(-2.0, 2.0), 1)
        wind_val = round(base_wind + (45.0 * schema.stress_intensity) + random.uniform(1.0, 5.0), 1)
        hum_val = round(min(100.0, base_hum + (30.0 * schema.stress_intensity)), 1)
        rain_val = round(base_rain + (60.0 * schema.stress_intensity) + random.uniform(0.0, 5.0), 1)
        baro_val = round(1013.2 - (35.0 * schema.stress_intensity) + random.uniform(-2.0, 2.0), 1)
        uv_val = round(random.uniform(1.0, 5.0) * (1.0 + 2.0 * schema.stress_intensity), 1)

        log = audit_weather_reading(
            db,
            name,
            temp_val,
            wind_val,
            hum_val,
            rain_val,
            baro_val,
            uv_val
        )
        generated_logs.append(log)

    # Log activity audit
    log_activity(
        db,
        current_user.id,
        current_user.role,
        "WEATHER_SIMULATE",
        f"Simulated weather grid readouts (Stress: {int(schema.stress_intensity*100)}%)"
    )

    return generated_logs


@router.post("/config", response_model=WeatherConfigResponse)
def update_config(
    schema: WeatherConfigRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Calibrate safety guidelines for a weather component sensor."""
    config = db.query(WeatherConfig).filter(WeatherConfig.sensor_name == schema.sensor_name).first()
    if not config:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Weather sensor configuration not found."
        )

    config.max_wind_speed_limit = schema.max_wind_speed_limit
    config.max_temp_limit = schema.max_temp_limit
    config.max_precipitation_limit = schema.max_precipitation_limit
    db.commit()
    db.refresh(config)

    # Log activity audit
    log_activity(
        db,
        current_user.id,
        current_user.role,
        "WEATHER_CONFIG_UPDATE",
        f"Calibrated weather safety limits for '{schema.sensor_name}'."
    )

    return config


@router.post("/reset", response_model=List[WeatherConfigResponse])
def reset_weather(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Reverts config limits to baseline parameters and clears log histories."""
    db.query(WeatherLog).delete()
    db.query(WeatherConfig).delete()
    db.commit()

    configs = initialize_weather_configs(db)

    log_activity(
        db,
        current_user.id,
        current_user.role,
        "WEATHER_RESET",
        "Cleared weather logs and restored baseline safety guidelines."
    )

    return configs
