"""
backend/models/noise.py
-----------------------
SQLAlchemy database models for construction site noise levels and decibel thresholds.
"""
from datetime import datetime
from sqlalchemy import Column, Integer, String, Boolean, DateTime, Float
from backend.database import Base


class NoiseLog(Base):
    __tablename__ = "noise_logs"

    id = Column(Integer, primary_key=True, index=True)
    sensor_name = Column(String, nullable=False)  # "Zone A (Excavation)", "Zone B (Framing)", "Zone C (Boundary)"
    decibel_level = Column(Float, nullable=False)  # in dB
    limit_threshold = Column(Float, nullable=False)  # Limit enforced at log timestamp
    is_breached = Column(Boolean, default=False, nullable=False)
    logged_at = Column(DateTime, default=datetime.utcnow, nullable=False)


class NoiseConfig(Base):
    __tablename__ = "noise_configs"

    id = Column(Integer, primary_key=True, index=True)
    sensor_name = Column(String, unique=True, index=True, nullable=False)
    daytime_limit = Column(Float, default=85.0, nullable=False)  # 06:00 to 22:00
    nighttime_limit = Column(Float, default=55.0, nullable=False)  # 22:00 to 06:00
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
