"""
backend/routers/waste.py
------------------------
FastAPI router for site waste tracking, goal limits, and sustainability audits.
"""
from typing import List, Dict, Any
from datetime import datetime
from fastapi import APIRouter, Depends, status, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field

from backend.database import get_db
from backend.models.user import User
from backend.models.waste import WasteLog, WasteGoal
from backend.models.dashboard import SystemNotification
from backend.routers.auth import get_current_user
from backend.services.dashboard_service import log_activity
from backend.services.waste_service import calculate_waste_analytics

router = APIRouter(prefix="/api/v1/waste", tags=["Site Waste Management"])


class WasteLogRequest(BaseModel):
    waste_type: str = Field(..., pattern="^(Concrete|Steel|Wood|Packaging|Hazardous)$")
    quantity: float = Field(..., gt=0.0)
    unit: str = Field(default="Tons")
    disposal_method: str = Field(..., pattern="^(Recycled|Reused|Landfill|Incinerated)$")
    cost: float = Field(default=0.0, ge=0.0)


class WasteGoalRequest(BaseModel):
    waste_type: str = Field(..., pattern="^(Concrete|Steel|Wood|Packaging|Hazardous)$")
    goal_quantity: float = Field(..., gt=0.0)
    unit: str = Field(default="Tons")


class WasteLogResponse(BaseModel):
    id: int
    waste_type: str
    quantity: float
    unit: str
    disposal_method: str
    cost: float
    logged_at: datetime

    class Config:
        from_attributes = True


class WasteGoalResponse(BaseModel):
    id: int
    waste_type: str
    goal_quantity: float
    unit: str
    achieved: bool
    updated_at: datetime

    class Config:
        from_attributes = True


def initialize_waste_goals(db: Session) -> List[WasteGoal]:
    """Seed database with standard waste reduction target goals."""
    baseline_goals = [
        WasteGoal(waste_type="Concrete", goal_quantity=10.0, unit="Tons", achieved=True),
        WasteGoal(waste_type="Steel", goal_quantity=3.0, unit="Tons", achieved=True),
        WasteGoal(waste_type="Wood", goal_quantity=5.0, unit="Tons", achieved=True),
        WasteGoal(waste_type="Packaging", goal_quantity=2.0, unit="Tons", achieved=True),
    ]
    for goal in baseline_goals:
        db.add(goal)
    db.commit()
    return db.query(WasteGoal).all()


@router.get("/logs", response_model=List[WasteLogResponse])
def get_logs(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Retrieve all logged waste disposal events."""
    return db.query(WasteLog).order_by(WasteLog.logged_at.desc()).all()


@router.get("/goals", response_model=List[WasteGoalResponse])
def get_goals(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Retrieve all waste reduction goals. Auto-seeds defaults if empty."""
    goals = db.query(WasteGoal).order_by(WasteGoal.waste_type.asc()).all()
    if not goals:
        goals = initialize_waste_goals(db)
    return goals


@router.get("/analytics")
def get_analytics(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Retrieve diversion rates, goals progress, and sustainability suggestions."""
    # Ensure goals exist
    db_goals = db.query(WasteGoal).all()
    if not db_goals:
        initialize_waste_goals(db)
    return calculate_waste_analytics(db)


@router.post("/log", response_model=WasteLogResponse)
def log_waste(
    schema: WasteLogRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Log a site waste disposal event. Triggers warnings if goals are breached."""
    # Ensure goals are seeded
    db_goals = db.query(WasteGoal).all()
    if not db_goals:
        initialize_waste_goals(db)

    # 1. Log waste entry
    log = WasteLog(
        waste_type=schema.waste_type,
        quantity=schema.quantity,
        unit=schema.unit,
        disposal_method=schema.disposal_method,
        cost=schema.cost
    )
    db.add(log)
    db.commit()
    db.refresh(log)

    # 2. Check category totals against goals
    all_logs = db.query(WasteLog).filter(WasteLog.waste_type == schema.waste_type).all()
    total_qty = sum(l.quantity for l in all_logs)

    goal = db.query(WasteGoal).filter(WasteGoal.waste_type == schema.waste_type).first()
    if goal and total_qty > goal.goal_quantity:
        goal.achieved = False
        
        # Trigger SystemNotification
        notification = SystemNotification(
            title="🚨 Waste Goal Breached Alert",
            message=(
                f"Debris waste for category '{schema.waste_type}' has exceeded the limit goal. "
                f"Cumulative total: {round(total_qty, 2)} Tons (Goal Limit: {goal.goal_quantity} Tons)."
            )
        )
        db.add(notification)

    db.commit()

    # 3. Log activity audit
    log_activity(
        db,
        current_user.id,
        current_user.role,
        "WASTE_LOG",
        f"Logged {schema.quantity} {schema.unit} of '{schema.waste_type}' waste. Method: {schema.disposal_method}"
    )

    return log


@router.post("/goal", response_model=WasteGoalResponse)
def update_or_create_goal(
    schema: WasteGoalRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Set or update a waste reduction goal."""
    goal = db.query(WasteGoal).filter(WasteGoal.waste_type == schema.waste_type).first()
    if goal:
        goal.goal_quantity = schema.goal_quantity
        goal.unit = schema.unit
    else:
        goal = WasteGoal(
            waste_type=schema.waste_type,
            goal_quantity=schema.goal_quantity,
            unit=schema.unit
        )
        db.add(goal)

    # Recalculate achievement state
    all_logs = db.query(WasteLog).filter(WasteLog.waste_type == schema.waste_type).all()
    total_qty = sum(l.quantity for l in all_logs)
    goal.achieved = (total_qty <= goal.goal_quantity)

    db.commit()
    db.refresh(goal)

    log_activity(
        db,
        current_user.id,
        current_user.role,
        "WASTE_GOAL_UPDATE",
        f"Updated waste limit goal for '{schema.waste_type}' to {schema.goal_quantity} {schema.unit}"
    )

    return goal


@router.post("/reset", response_model=List[WasteGoalResponse])
def reset_waste(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Deletes all waste logs and reverts goals to baseline."""
    db.query(WasteLog).delete()
    db.query(WasteGoal).delete()
    db.commit()

    goals = initialize_waste_goals(db)

    log_activity(
        db,
        current_user.id,
        current_user.role,
        "WASTE_RESET",
        "Reverted waste log metrics and restored baseline goals."
    )

    return goals
