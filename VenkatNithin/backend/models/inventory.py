"""
backend/models/inventory.py
---------------------------
SQLAlchemy database models for tracking construction material stocks and purchase reorders.
"""
from datetime import datetime
from sqlalchemy import Column, Integer, String, Boolean, DateTime, Float
from backend.database import Base


class MaterialStock(Base):
    __tablename__ = "material_stocks"

    id = Column(Integer, primary_key=True, index=True)
    material_name = Column(String, unique=True, index=True, nullable=False)
    quantity = Column(Float, default=0.0, nullable=False)
    unit = Column(String, nullable=False)  # e.g., "Tons", "Bags", "Units"
    unit_price = Column(Float, nullable=False)  # Price per unit
    min_threshold = Column(Float, nullable=False)  # Minimum quantity limit
    low_stock_alert = Column(Boolean, default=False, nullable=False)
    waste_quantity = Column(Float, default=0.0, nullable=False)  # Total waste recorded
    last_updated = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)


class MaterialOrder(Base):
    __tablename__ = "material_orders"

    id = Column(Integer, primary_key=True, index=True)
    material_name = Column(String, nullable=False)
    order_quantity = Column(Float, nullable=False)
    total_cost = Column(Float, nullable=False)
    status = Column(String, default="Ordered", nullable=False)  # "Ordered", "Shipped", "Delivered"
    ordered_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    expected_delivery = Column(DateTime, nullable=False)
