"""
backend/models/weather_hazards.py
---------------------------------
SQLAlchemy database models for weather sensors and hazard prediction.
"""
from datetime import datetime
from sqlalchemy import Column, Integer, String, Boolean, DateTime, Float
from backend.database import Base


class WeatherLog(Base):
    __tablename__ = "weather_logs"

    id = Column(Integer, primary_key=True, index=True)
    sensor_name = Column(String, nullable=False)  # "Tower Crane Jib Peak", "Ground Weather Station", "Perimeter Boundary Mast"
    temperature = Column(Float, nullable=False)  # in °C
    wind_speed = Column(Float, nullable=False)  # in km/h
    humidity = Column(Float, nullable=False)  # in %
    precipitation = Column(Float, nullable=False)  # in mm
    barometric_pressure = Column(Float, nullable=False)  # in hPa
    uv_index = Column(Float, nullable=False)
    is_hazardous = Column(Boolean, default=False, nullable=False)
    hazard_types = Column(String, default="None", nullable=False)  # "None", or e.g., "High Winds, Heavy Storm"
    logged_at = Column(DateTime, default=datetime.utcnow, nullable=False)


class WeatherConfig(Base):
    __tablename__ = "weather_configs"

    id = Column(Integer, primary_key=True, index=True)
    sensor_name = Column(String, unique=True, index=True, nullable=False)
    max_wind_speed_limit = Column(Float, default=40.0, nullable=False)  # km/h
    max_temp_limit = Column(Float, default=38.0, nullable=False)  # °C
    max_precipitation_limit = Column(Float, default=50.0, nullable=False)  # mm
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
