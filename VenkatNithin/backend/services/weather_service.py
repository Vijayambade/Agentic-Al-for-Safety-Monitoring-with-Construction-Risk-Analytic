"""
backend/services/weather_service.py
-----------------------------------
Business logic for construction site weather safety checks and hazard alert triggering.
"""
from datetime import datetime
from sqlalchemy.orm import Session
from backend.models.weather_hazards import WeatherLog, WeatherConfig
from backend.models.dashboard import SystemNotification


def audit_weather_reading(
    db: Session,
    sensor_name: str,
    temp: float,
    wind: float,
    hum: float,
    rain: float,
    baro: float,
    uv: float
) -> WeatherLog:
    """
    Checks weather parameters against safety guidelines.
    Sets hazard flags and dispatches system notifications if safety limits are crossed.
    """
    # 1. Fetch config limits
    config = db.query(WeatherConfig).filter(WeatherConfig.sensor_name == sensor_name).first()
    max_wind = config.max_wind_speed_limit if config else 40.0
    max_temp = config.max_temp_limit if config else 38.0
    max_rain = config.max_precipitation_limit if config else 50.0

    # 2. Check anomalies
    hazards = []
    if wind > max_wind:
        hazards.append("Tower Crane Operation Wind Risk")
    if temp > max_temp:
        hazards.append("Worker Heat Stroke Warning")
    if rain > max_rain:
        hazards.append("Site Flooding / Concrete Curing Warning")

    is_hazardous = len(hazards) > 0
    hazard_str = ", ".join(hazards) if is_hazardous else "None"

    # 3. Create log
    log = WeatherLog(
        sensor_name=sensor_name,
        temperature=temp,
        wind_speed=wind,
        humidity=hum,
        precipitation=rain,
        barometric_pressure=baro,
        uv_index=uv,
        is_hazardous=is_hazardous,
        hazard_types=hazard_str,
        logged_at=datetime.utcnow()
    )
    db.add(log)

    # 4. Trigger alert notification if hazardous
    if is_hazardous:
        notification = SystemNotification(
            title="🚨 Weather Hazard Threat Warning",
            message=(
                f"Extreme weather conditions detected at '{sensor_name}'. "
                f"Hazards: {hazard_str}. Temperature: {temp}°C, Wind Speed: {wind} km/h, Precipitation: {rain} mm."
            )
        )
        db.add(notification)

    db.commit()
    db.refresh(log)

    return log
