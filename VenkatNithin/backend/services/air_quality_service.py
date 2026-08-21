"""
backend/services/air_quality_service.py
---------------------------------------
Business logic for air quality monitoring and hazardous gas warnings.
"""
from datetime import datetime
from sqlalchemy.orm import Session
from backend.models.air_quality import AirQualityLog, AirQualityConfig
from backend.models.dashboard import SystemNotification


def audit_air_quality_reading(
    db: Session,
    sensor_name: str,
    aqi: float,
    pm25: float,
    pm10: float,
    co: float,
    no2: float,
    voc: float
) -> AirQualityLog:
    """
    Checks air sensor parameters against threshold limits.
    Sets hazardous flag and logs system notifications if thresholds are crossed.
    """
    # 1. Fetch config limits
    config = db.query(AirQualityConfig).filter(AirQualityConfig.sensor_name == sensor_name).first()
    pm25_lim = config.pm25_limit if config else 50.0
    co_lim = config.co_limit if config else 35.0
    voc_lim = config.voc_limit if config else 10.0

    # 2. Check parameters
    hazards = []
    if pm25 > pm25_lim:
        hazards.append(f"High particulate matter (PM2.5: {pm25} ug/m3)")
    if co > co_lim:
        hazards.append(f"CO gas leak alert (CO: {co} ppm)")
    if voc > voc_lim:
        hazards.append(f"High chemical fumes VOC (VOC: {voc} ppm)")
    if aqi > 150.0:
        hazards.append(f"Unhealthy AQI index (AQI: {aqi})")

    is_hazardous = len(hazards) > 0
    reason_str = " | ".join(hazards) if is_hazardous else "Normal"

    # 3. Create Log entry
    log = AirQualityLog(
        sensor_name=sensor_name,
        aqi=aqi,
        pm25=pm25,
        pm10=pm10,
        co_level=co,
        no2_level=no2,
        voc_level=voc,
        is_hazardous=is_hazardous,
        hazard_reason=reason_str,
        logged_at=datetime.utcnow()
    )
    db.add(log)

    # 4. Create alert notification if hazardous
    if is_hazardous:
        notification = SystemNotification(
            title="🚨 Hazardous Air Alert",
            message=(
                f"Dangerous environmental readings at '{sensor_name}'. "
                f"Issues: {reason_str}."
            )
        )
        db.add(notification)

    db.commit()
    db.refresh(log)

    return log
