"""
backend/models/energy.py
------------------------
SQLAlchemy database models for smart construction energy and power consumption monitoring.
"""
from datetime import datetime
from sqlalchemy import Column, Integer, String, Boolean, DateTime, Float
from backend.database import Base


class EnergyLog(Base):
    __tablename__ = "energy_logs"

    id = Column(Integer, primary_key=True, index=True)
    sensor_name = Column(String, nullable=False)  # "Heavy Tower Cranes", "Concrete Batch Plant", "High-Intensity Site Lighting", "Main Site Offices"
    power_usage = Column(Float, nullable=False)  # in kW
    voltage = Column(Float, nullable=False)  # in V
    current = Column(Float, nullable=False)  # in A
    power_factor = Column(Float, nullable=False)  # efficiency factor 0.0 to 1.0
    cumulative_kwh = Column(Float, nullable=False)  # Total consumption in kWh
    is_anomaly = Column(Boolean, default=False, nullable=False)
    anomaly_type = Column(String, default="None", nullable=False)  # "None", "Power Spike / Overload", "Low Voltage", "Inefficient Power Factor"
    logged_at = Column(DateTime, default=datetime.utcnow, nullable=False)


class EnergyConfig(Base):
    __tablename__ = "energy_configs"

    id = Column(Integer, primary_key=True, index=True)
    sensor_name = Column(String, unique=True, index=True, nullable=False)
    max_power_limit = Column(Float, default=150.0, nullable=False)  # kW
    min_voltage_limit = Column(Float, default=210.0, nullable=False)  # V
    min_power_factor_limit = Column(Float, default=0.85, nullable=False)  # efficiency threshold
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
