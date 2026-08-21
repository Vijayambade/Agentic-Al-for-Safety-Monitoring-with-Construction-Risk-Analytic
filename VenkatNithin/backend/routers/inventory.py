"""
backend/routers/inventory.py
----------------------------
FastAPI router for construction materials inventory, usage logging, and reordering pipelines.
"""
from typing import List, Dict, Any
from datetime import datetime, timedelta
from fastapi import APIRouter, Depends, status, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field

from backend.database import get_db
from backend.models.user import User
from backend.models.inventory import MaterialStock, MaterialOrder
from backend.routers.auth import get_current_user
from backend.services.dashboard_service import log_activity
from backend.services.inventory_service import check_low_stock_alerts

router = APIRouter(prefix="/api/v1/inventory", tags=["Material Inventory"])


class ConsumeRequest(BaseModel):
    material_id: int
    quantity: float = Field(..., gt=0.0)
    waste: float = Field(default=0.0, ge=0.0)


class ReorderRequest(BaseModel):
    material_id: int
    order_quantity: float = Field(..., gt=0.0)


class DeliveryStatusUpdateRequest(BaseModel):
    order_id: int
    status: str = Field(..., pattern="^(Shipped|Delivered)$")


class MaterialStockResponse(BaseModel):
    id: int
    material_name: str
    quantity: float
    unit: str
    unit_price: float
    min_threshold: float
    low_stock_alert: bool
    waste_quantity: float
    last_updated: datetime

    class Config:
        from_attributes = True


class MaterialOrderResponse(BaseModel):
    id: int
    material_name: str
    order_quantity: float
    total_cost: float
    status: str
    ordered_at: datetime
    expected_delivery: datetime

    class Config:
        from_attributes = True


def initialize_inventory_stocks(db: Session) -> List[MaterialStock]:
    """Helper to seed database with standard construction material baseline stocks."""
    baseline_stocks = [
        MaterialStock(
            id=1,
            material_name="Cement",
            quantity=500.0,
            unit="Bags",
            unit_price=8.00,
            min_threshold=150.0,
            low_stock_alert=False,
            waste_quantity=0.0
        ),
        MaterialStock(
            id=2,
            material_name="Steel Rebar",
            quantity=20.0,
            unit="Tons",
            unit_price=900.00,
            min_threshold=5.0,
            low_stock_alert=False,
            waste_quantity=0.0
        ),
        MaterialStock(
            id=3,
            material_name="Bricks",
            quantity=10000.0,
            unit="Units",
            unit_price=0.25,
            min_threshold=2000.0,
            low_stock_alert=False,
            waste_quantity=0.0
        ),
        MaterialStock(
            id=4,
            material_name="Sand",
            quantity=80.0,
            unit="Tons",
            unit_price=35.00,
            min_threshold=15.0,
            low_stock_alert=False,
            waste_quantity=0.0
        ),
        MaterialStock(
            id=5,
            material_name="Aggregate",
            quantity=120.0,
            unit="Tons",
            unit_price=28.00,
            min_threshold=20.0,
            low_stock_alert=False,
            waste_quantity=0.0
        )
    ]

    for stock in baseline_stocks:
        check_low_stock_alerts(db, stock)
        db.add(stock)
    db.commit()

    return db.query(MaterialStock).all()


@router.get("/stocks", response_model=List[MaterialStockResponse])
def get_stocks(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Retrieve current stock profiles. Auto-initializes if database is empty."""
    stocks = db.query(MaterialStock).order_by(MaterialStock.id.asc()).all()
    if not stocks:
        stocks = initialize_inventory_stocks(db)
    return stocks


@router.get("/orders", response_model=List[MaterialOrderResponse])
def get_orders(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Retrieve all purchase and shipping reorders."""
    return db.query(MaterialOrder).order_by(MaterialOrder.ordered_at.desc()).all()


@router.post("/consume", response_model=MaterialStockResponse)
def consume_materials(
    schema: ConsumeRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Log material quantities consumed and wasted during site tasks."""
    stock = db.query(MaterialStock).filter(MaterialStock.id == schema.material_id).first()
    if not stock:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Material not found."
        )

    if stock.quantity < schema.quantity:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Insufficient stock. Remaining: {stock.quantity} {stock.unit}."
        )

    # Decrement quantities
    stock.quantity = round(stock.quantity - schema.quantity, 2)
    stock.waste_quantity = round(stock.waste_quantity + schema.waste, 2)
    
    # Audit for threshold breaches
    check_low_stock_alerts(db, stock)
    
    db.commit()
    db.refresh(stock)

    # Log activity audit
    log_activity(
        db,
        current_user.id,
        current_user.role,
        "INVENTORY_CONSUME",
        f"Used {schema.quantity} {stock.unit} and wasted {schema.waste} {stock.unit} of '{stock.material_name}'"
    )

    return stock


@router.post("/reorder", response_model=MaterialOrderResponse)
def create_purchase_order(
    schema: ReorderRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Generate a new purchase reorder for material restocking."""
    stock = db.query(MaterialStock).filter(MaterialStock.id == schema.material_id).first()
    if not stock:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Material not found in inventory."
        )

    cost = round(schema.order_quantity * stock.unit_price, 2)
    eta = datetime.utcnow() + timedelta(days=3)

    order = MaterialOrder(
        material_name=stock.material_name,
        order_quantity=schema.order_quantity,
        total_cost=cost,
        status="Ordered",
        expected_delivery=eta
    )
    db.add(order)
    db.commit()
    db.refresh(order)

    # Log activity audit
    log_activity(
        db,
        current_user.id,
        current_user.role,
        "INVENTORY_REORDER",
        f"Placed PO for {schema.order_quantity} {stock.unit} of '{stock.material_name}' (Cost: ${cost})"
    )

    return order


@router.post("/update-delivery", response_model=MaterialOrderResponse)
def update_delivery(
    schema: DeliveryStatusUpdateRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update order shipping status. If status is set to 'Delivered', restocks inventory quantity."""
    order = db.query(MaterialOrder).filter(MaterialOrder.id == schema.order_id).first()
    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Purchase order not found."
        )

    if order.status == "Delivered":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Order has already been delivered and restocked."
        )

    order.status = schema.status
    
    # Restock active quantity if delivered
    if schema.status == "Delivered":
        stock = db.query(MaterialStock).filter(MaterialStock.material_name == order.material_name).first()
        if stock:
            stock.quantity = round(stock.quantity + order.order_quantity, 2)
            check_low_stock_alerts(db, stock)

    db.commit()
    db.refresh(order)

    # Log activity audit
    log_activity(
        db,
        current_user.id,
        current_user.role,
        "DELIVERY_UPDATE",
        f"PO #{order.id} ('{order.material_name}') shipping status updated to: {schema.status}"
    )

    return order


@router.post("/reset", response_model=List[MaterialStockResponse])
def reset_inventory(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Reverts inventory logs and stock parameters to baseline settings."""
    db.query(MaterialStock).delete()
    db.query(MaterialOrder).delete()
    db.commit()

    stocks = initialize_inventory_stocks(db)

    log_activity(
        db,
        current_user.id,
        current_user.role,
        "INVENTORY_RESET",
        "Reverted material stock counts and cleared PO delivery logs."
    )

    return stocks
