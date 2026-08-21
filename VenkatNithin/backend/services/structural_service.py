"""
backend/services/structural_service.py
--------------------------------------
Business logic for structural health monitoring, strain analysis, and collapse warnings.
"""
from datetime import datetime
from sqlalchemy.orm import Session
from backend.models.structural_health import StructuralLog, StructuralConfig
from backend.models.dashboard import SystemNotification


def audit_structural_reading(
    db: Session,
    sensor_name: str,
    vibration_frequency: float,
    amplitude: float,
    tilt_angle: float,
    strain: float
) -> StructuralLog:
    """
    Checks structural parameters against safety guidelines.
    Sets instability flag and dispatches system notifications if safety boundaries are crossed.
    """
    # 1. Fetch config limits
    config = db.query(StructuralConfig).filter(StructuralConfig.sensor_name == sensor_name).first()
    max_vib = config.max_vibration_frequency if config else 50.0
    max_tilt = config.max_tilt_angle if config else 5.0
    max_strain = config.max_strain if config else 300.0

    # 2. Check anomalies
    hazards = []
    if vibration_frequency > max_vib:
        hazards.append(f"Excessive Vibration ({vibration_frequency} Hz)")
    if tilt_angle > max_tilt:
        hazards.append(f"Critical Tilt Angle ({tilt_angle}°)")
    if strain > max_strain:
        hazards.append(f"High Tensile Strain ({strain} microstrain)")

    is_unstable = len(hazards) > 0
    reason_str = " | ".join(hazards) if is_unstable else "Healthy"

    # 3. Create log
    log = StructuralLog(
        sensor_name=sensor_name,
        vibration_frequency=vibration_frequency,
        amplitude=amplitude,
        tilt_angle=tilt_angle,
        strain=strain,
        is_unstable=is_unstable,
        instability_reason=reason_str,
        logged_at=datetime.utcnow()
    )
    db.add(log)

    # 4. Trigger collapse warning alert if unstable
    if is_unstable:
        notification = SystemNotification(
            title="🚨 Structural Instability Warning",
            message=(
                f"Dangerous environmental stress detected at '{sensor_name}'. "
                f"Issues: {reason_str}."
            )
        )
        db.add(notification)

    db.commit()
    db.refresh(log)

    return log
