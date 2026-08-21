"""
backend/models/water_monitoring.py
----------------------------------
SQLAlchemy database models for water flow monitoring and leakage alarms.
"""
from datetime import datetime
from sqlalchemy import Column, Integer, String, Boolean, DateTime, Float
from backend.database import Base


class WaterLog(Base):
    __tablename__ = "water_logs"

    id = Column(Integer, primary_key=True, index=True)
    sensor_name = Column(String, nullable=False)  # "Main Supply Inlet", "Concrete Mixing Bay", "Worker Quarters"
    flow_rate = Column(Float, nullable=False)  # in L/min
    pressure = Column(Float, nullable=False)  # in kPa
    cumulative_liters = Column(Float, nullable=False)  # Total liters used
    is_anomaly = Column(Boolean, default=False, nullable=False)
    anomaly_type = Column(String, default="None", nullable=False)  # "None", "High Flow", "Leak / Pressure Drop"
    logged_at = Column(DateTime, default=datetime.utcnow, nullable=False)


class WaterConfig(Base):
    __tablename__ = "water_configs"

    id = Column(Integer, primary_key=True, index=True)
    sensor_name = Column(String, unique=True, index=True, nullable=False)
    max_flow_limit = Column(Float, default=100.0, nullable=False)  # L/min
    min_pressure_limit = Column(Float, default=150.0, nullable=False)  # kPa
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
