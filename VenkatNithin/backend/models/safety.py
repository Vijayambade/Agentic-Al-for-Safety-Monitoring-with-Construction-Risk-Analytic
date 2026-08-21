"""
backend/models/safety.py
------------------------
SQLAlchemy model for logging safety hazards and incident reports.
"""
from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from backend.database import Base


class SafetyIncident(Base):
    __tablename__ = "safety_incidents"

    id = Column(Integer, primary_key=True, index=True)
    reporter_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    hazard_description = Column(String, nullable=False)
    severity = Column(String, nullable=False)  # "Low Warning", "Medium Risk", "High Critical"
    status = Column(String, default="Open", nullable=False)  # "Open", "Investigating", "Resolved"
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
