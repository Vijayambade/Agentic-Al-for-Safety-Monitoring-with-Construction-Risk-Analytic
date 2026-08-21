"""
backend/services/energy_service.py
----------------------------------
Business logic for smart construction energy monitoring and grid auditing.
"""
from datetime import datetime
from sqlalchemy.orm import Session
from backend.models.energy import EnergyLog, EnergyConfig
from backend.models.dashboard import SystemNotification


def audit_energy_reading(
    db: Session,
    sensor_name: str,
    power_usage: float,
    voltage: float,
    current: float,
    power_factor: float,
    cumulative: float
) -> EnergyLog:
    """
    Checks energy sensor variables against grid safety thresholds.
    Sets anomaly flags and dispatches system notifications if safety boundaries are crossed.
    """
    # 1. Fetch config limits
    config = db.query(EnergyConfig).filter(EnergyConfig.sensor_name == sensor_name).first()
    max_pow = config.max_power_limit if config else 150.0
    min_volt = config.min_voltage_limit if config else 210.0
    min_pf = config.min_power_factor_limit if config else 0.85

    # 2. Check anomalies
    anomaly_type = "None"
    is_anomaly = False

    if power_usage > max_pow:
        is_anomaly = True
        anomaly_type = "Power Spike / Overload"
    elif voltage < min_volt:
        is_anomaly = True
        anomaly_type = "Low Voltage"
    elif power_factor < min_pf:
        is_anomaly = True
        anomaly_type = "Inefficient Power Factor"

    # 3. Create log
    log = EnergyLog(
        sensor_name=sensor_name,
        power_usage=power_usage,
        voltage=voltage,
        current=current,
        power_factor=power_factor,
        cumulative_kwh=cumulative,
        is_anomaly=is_anomaly,
        anomaly_type=anomaly_type,
        logged_at=datetime.utcnow()
    )
    db.add(log)

    # 4. Trigger alert notification if anomalous
    if is_anomaly:
        notification = SystemNotification(
            title="🚨 Energy Anomaly Alert",
            message=(
                f"Abnormal power reading detected at '{sensor_name}'. "
                f"Type: {anomaly_type}. Power: {power_usage} kW, Voltage: {voltage} V, Power Factor: {power_factor}."
            )
        )
        db.add(notification)

    db.commit()
    db.refresh(log)

    return log
