"""
backend/models/structural_health.py
-----------------------------------
SQLAlchemy database models for structural health telemetry and collapse prevention.
"""
from datetime import datetime
from sqlalchemy import Column, Integer, String, Boolean, DateTime, Float
from backend.database import Base


class StructuralLog(Base):
    __tablename__ = "structural_logs"

    id = Column(Integer, primary_key=True, index=True)
    sensor_name = Column(String, nullable=False)  # "Scaffolding Tower Zone A", "Concrete Formwork Zone B", "Foundation Column Pier C"
    vibration_frequency = Column(Float, nullable=False)  # in Hz
    amplitude = Column(Float, nullable=False)  # in mm
    tilt_angle = Column(Float, nullable=False)  # in degrees
    strain = Column(Float, nullable=False)  # in microstrain
    is_unstable = Column(Boolean, default=False, nullable=False)
    instability_reason = Column(String, default="", nullable=False)
    logged_at = Column(DateTime, default=datetime.utcnow, nullable=False)


class StructuralConfig(Base):
    __tablename__ = "structural_configs"

    id = Column(Integer, primary_key=True, index=True)
    sensor_name = Column(String, unique=True, index=True, nullable=False)
    max_vibration_frequency = Column(Float, default=50.0, nullable=False)  # Hz
    max_tilt_angle = Column(Float, default=5.0, nullable=False)  # degrees
    max_strain = Column(Float, default=300.0, nullable=False)  # microstrain
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
