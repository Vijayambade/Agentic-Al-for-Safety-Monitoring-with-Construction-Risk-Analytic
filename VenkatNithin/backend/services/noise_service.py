"""
backend/services/noise_service.py
---------------------------------
Business logic for auditing decibel levels and raising environmental noise breach alerts.
"""
from datetime import datetime
from sqlalchemy.orm import Session
from backend.models.noise import NoiseLog, NoiseConfig
from backend.models.dashboard import SystemNotification


def audit_decibel_reading(db: Session, sensor_name: str, decibel: float) -> NoiseLog:
    """
    Evaluates raw noise readings against sensor-specific daytime/nighttime thresholds.
    Logs decibel data, checks breach flags, and dispatches system notifications if limits are crossed.
    """
    now = datetime.utcnow()
    current_hour = now.hour
    
    # 1. Daytime (06:00 - 22:00) vs. Nighttime (22:00 - 06:00) limits
    is_daytime = (6 <= current_hour < 22)

    # 2. Query sensor configs
    config = db.query(NoiseConfig).filter(NoiseConfig.sensor_name == sensor_name).first()
    if not config:
        # Fallback default configuration limits
        day_limit = 85.0
        night_limit = 55.0
    else:
        day_limit = config.daytime_limit
        night_limit = config.nighttime_limit

    active_limit = day_limit if is_daytime else night_limit
    is_breached = (decibel > active_limit)

    # 3. Create Noise Log
    log = NoiseLog(
        sensor_name=sensor_name,
        decibel_level=decibel,
        limit_threshold=active_limit,
        is_breached=is_breached,
        logged_at=now
    )
    db.add(log)

    # 4. Trigger system notifications if limit is breached
    if is_breached:
        notification = SystemNotification(
            title="🚨 Decibel Breach Alert",
            message=(
                f"Noise level at '{sensor_name}' has breached the limit. "
                f"Recorded: {decibel} dB (Active Limit: {active_limit} dB)."
            )
        )
        db.add(notification)

    db.commit()
    db.refresh(log)

    return log
