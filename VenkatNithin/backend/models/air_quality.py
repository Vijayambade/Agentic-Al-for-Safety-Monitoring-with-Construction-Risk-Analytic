"""
backend/models/air_quality.py
-----------------------------
SQLAlchemy database models for air quality readings and gas safety parameters.
"""
from datetime import datetime
from sqlalchemy import Column, Integer, String, Boolean, DateTime, Float
from backend.database import Base


class AirQualityLog(Base):
    __tablename__ = "air_quality_logs"

    id = Column(Integer, primary_key=True, index=True)
    sensor_name = Column(String, nullable=False)  # "Excavation Tunnel A", "Framing & Welding Zone B", "Site Perimeter Zone C"
    aqi = Column(Float, nullable=False)  # Air Quality Index (0 - 500)
    pm25 = Column(Float, nullable=False)  # PM2.5 in ug/m3
    pm10 = Column(Float, nullable=False)  # PM10 in ug/m3
    co_level = Column(Float, nullable=False)  # Carbon Monoxide in ppm
    no2_level = Column(Float, nullable=False)  # Nitrogen Dioxide in ppm
    voc_level = Column(Float, nullable=False)  # Volatile Organic Compounds in ppm
    is_hazardous = Column(Boolean, default=False, nullable=False)
    hazard_reason = Column(String, default="", nullable=False)
    logged_at = Column(DateTime, default=datetime.utcnow, nullable=False)


class AirQualityConfig(Base):
    __tablename__ = "air_quality_configs"

    id = Column(Integer, primary_key=True, index=True)
    sensor_name = Column(String, unique=True, index=True, nullable=False)
    pm25_limit = Column(Float, default=50.0, nullable=False)  # in ug/m3
    co_limit = Column(Float, default=35.0, nullable=False)  # in ppm
    voc_limit = Column(Float, default=10.0, nullable=False)  # in ppm
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
