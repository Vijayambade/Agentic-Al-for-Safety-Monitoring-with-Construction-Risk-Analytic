"""
backend/models/ai_history.py
----------------------------
SQLAlchemy model for storing general chat conversation history.
"""
from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime
from backend.database import Base


class GeneralChatHistory(Base):
    __tablename__ = "general_chat_history"

    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(String, index=True, nullable=False)
    role = Column(String, nullable=False)  # "user" or "assistant"
    message = Column(String, nullable=False)
    has_audio = Column(String, default="false")  # stored as string to match DB style or boolean
    audio_url = Column(String, nullable=True)
    timestamp = Column(DateTime, default=datetime.utcnow, nullable=False)
