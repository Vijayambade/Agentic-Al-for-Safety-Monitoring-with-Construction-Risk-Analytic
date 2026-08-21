"""
backend/models/schedule.py
--------------------------
SQLAlchemy database model for construction project tasks and CPM attributes.
"""
from datetime import datetime
from sqlalchemy import Column, Integer, String, Boolean, DateTime, Float
from backend.database import Base


class ScheduleTask(Base):
    __tablename__ = "schedule_tasks"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    duration = Column(Integer, nullable=False)  # in days
    start_date = Column(DateTime, nullable=False)
    end_date = Column(DateTime, nullable=False)
    dependencies = Column(String, default="", nullable=False)  # e.g., "1,2" (IDs comma separated)
    is_critical = Column(Boolean, default=False, nullable=False)
    progress = Column(Float, default=0.0, nullable=False)  # Percentage 0.0 - 100.0
    predicted_delay = Column(Integer, default=0, nullable=False)  # in days
    risk_factors = Column(String, default="", nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
