"""
backend/models/waste.py
-----------------------
SQLAlchemy database models for tracking waste logs and sustainability targets.
"""
from datetime import datetime
from sqlalchemy import Column, Integer, String, Boolean, DateTime, Float
from backend.database import Base


class WasteLog(Base):
    __tablename__ = "waste_logs"

    id = Column(Integer, primary_key=True, index=True)
    waste_type = Column(String, nullable=False)  # "Concrete", "Steel", "Wood", "Packaging", "Hazardous"
    quantity = Column(Float, nullable=False)
    unit = Column(String, default="Tons", nullable=False)
    disposal_method = Column(String, nullable=False)  # "Recycled", "Reused", "Landfill", "Incinerated"
    cost = Column(Float, default=0.0, nullable=False)
    logged_at = Column(DateTime, default=datetime.utcnow, nullable=False)


class WasteGoal(Base):
    __tablename__ = "waste_goals"

    id = Column(Integer, primary_key=True, index=True)
    waste_type = Column(String, unique=True, index=True, nullable=False)
    goal_quantity = Column(Float, nullable=False)
    unit = Column(String, default="Tons", nullable=False)
    achieved = Column(Boolean, default=True, nullable=False)  # True = waste <= goal_quantity
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
