"""
backend/services/water_service.py
---------------------------------
Business logic for water flow monitoring and leakage anomaly detection.
"""
from datetime import datetime
from sqlalchemy.orm import Session
from backend.models.water_monitoring import WaterLog, WaterConfig
from backend.models.dashboard import SystemNotification


def audit_water_reading(
    db: Session,
    sensor_name: str,
    flow_rate: float,
    pressure: float,
    cumulative: float
) -> WaterLog:
    """
    Checks water sensor variables against pipeline guidelines.
    Sets anomaly flags and dispatches system notifications if safety boundaries are crossed.
    """
    # 1. Fetch config limits
    config = db.query(WaterConfig).filter(WaterConfig.sensor_name == sensor_name).first()
    max_flow = config.max_flow_limit if config else 100.0
    min_pressure = config.min_pressure_limit if config else 150.0

    # 2. Check anomalies
    anomaly_type = "None"
    is_anomaly = False

    if flow_rate > max_flow:
        is_anomaly = True
        anomaly_type = "High Flow"
    elif pressure < min_pressure and flow_rate > 10.0:
        is_anomaly = True
        anomaly_type = "Leak / Pressure Drop"

    # 3. Create log
    log = WaterLog(
        sensor_name=sensor_name,
        flow_rate=flow_rate,
        pressure=pressure,
        cumulative_liters=cumulative,
        is_anomaly=is_anomaly,
        anomaly_type=anomaly_type,
        logged_at=datetime.utcnow()
    )
    db.add(log)

    # 4. Trigger alert notification if anomalous
    if is_anomaly:
        notification = SystemNotification(
            title="🚨 Water Leakage Alert",
            message=(
                f"Abnormal water flow detected at '{sensor_name}'. "
                f"Type: {anomaly_type}. Flow Rate: {flow_rate} L/min, Pressure: {pressure} kPa."
            )
        )
        db.add(notification)

    db.commit()
    db.refresh(log)

    return log
