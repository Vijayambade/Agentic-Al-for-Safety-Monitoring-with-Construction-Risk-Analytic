"""
backend/models/document.py
--------------------------
SQLAlchemy model for storing audited documents and vector index references.
"""
from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime
from backend.database import Base


class AnalyzedDocument(Base):
    __tablename__ = "analyzed_documents"

    id = Column(Integer, primary_key=True, index=True)
    filename = Column(String, nullable=False)
    doc_type = Column(String, nullable=False)  # "Contract", "BOQ", "Blueprint", "General"
    summary = Column(String, nullable=False)
    missing_clauses = Column(String, nullable=False)
    risks = Column(String, nullable=False)
    recommendations = Column(String, nullable=False)
    raw_text = Column(String, nullable=False)
    index_path = Column(String, nullable=True)  # Path to FAISS index
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
