"""
backend/models/telematics.py
----------------------------
SQLAlchemy database model for construction equipment telemetry and health indicators.
"""
from datetime import datetime
from sqlalchemy import Column, Integer, String, Boolean, DateTime, Float
from backend.database import Base


class EquipmentTelemetry(Base):
    __tablename__ = "equipment_telemetry"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    status = Column(String, default="Active", nullable=False)  # "Active", "Idle", "Scheduled", "Maintenance"
    gps_latitude = Column(Float, nullable=False)
    gps_longitude = Column(Float, nullable=False)
    fuel_level = Column(Float, default=100.0, nullable=False)  # Percentage 0.0 - 100.0
    engine_temp = Column(Float, default=85.0, nullable=False)  # in Celsius
    operating_hours = Column(Float, default=0.0, nullable=False)
    vibration_level = Column(Float, default=2.5, nullable=False)  # in mm/s
    predicted_failure = Column(Boolean, default=False, nullable=False)
    failure_probability = Column(Float, default=0.0, nullable=False)  # Percentage
    maintenance_scheduled_at = Column(DateTime, nullable=True)
    health_score = Column(Float, default=100.0, nullable=False)  # Percentage
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
