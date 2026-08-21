"""
backend/routers/schedule.py
---------------------------
FastAPI router for CPM scheduling, risk parameters, and automatic delay forecasting.
"""
from typing import List, Dict, Any
from datetime import datetime, timedelta
from fastapi import APIRouter, Depends, status, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel

from backend.database import get_db
from backend.models.user import User
from backend.models.schedule import ScheduleTask
from backend.routers.auth import get_current_user
from backend.services.dashboard_service import log_activity
from backend.services.schedule_service import run_cpm_algorithm, predict_schedule_delays

router = APIRouter(prefix="/api/v1/schedule", tags=["Project Scheduling"])


class DelayPredictionRequest(BaseModel):
    weather_risk: float  # 0.0 to 1.0
    labor_risk: float    # 0.0 to 1.0


class ScheduleTaskResponse(BaseModel):
    id: int
    name: str
    duration: int
    start_date: datetime
    end_date: datetime
    dependencies: str
    is_critical: bool
    progress: float
    predicted_delay: int
    risk_factors: str

    class Config:
        from_attributes = True


def initialize_baseline_schedule(db: Session) -> List[ScheduleTask]:
    """Helper to initialize the database with standard 5 baseline construction tasks."""
    today = datetime.utcnow().replace(hour=8, minute=0, second=0, microsecond=0)
    
    baseline_tasks = [
        ScheduleTask(
            id=1,
            name="Excavation & Site Prep",
            duration=5,
            start_date=today,
            end_date=today + timedelta(days=5),
            dependencies="",
            progress=100.0,
            predicted_delay=0,
            risk_factors="None"
        ),
        ScheduleTask(
            id=2,
            name="Concrete Foundation Pouring",
            duration=7,
            start_date=today + timedelta(days=5),
            end_date=today + timedelta(days=12),
            dependencies="1",
            progress=40.0,
            predicted_delay=0,
            risk_factors="None"
        ),
        ScheduleTask(
            id=3,
            name="Structural Framing & Steel",
            duration=10,
            start_date=today + timedelta(days=12),
            end_date=today + timedelta(days=22),
            dependencies="2",
            progress=0.0,
            predicted_delay=0,
            risk_factors="None"
        ),
        ScheduleTask(
            id=4,
            name="Roofing Installation",
            duration=6,
            start_date=today + timedelta(days=22),
            end_date=today + timedelta(days=28),
            dependencies="3",
            progress=0.0,
            predicted_delay=0,
            risk_factors="None"
        ),
        ScheduleTask(
            id=5,
            name="Interior Finishes & Wiring",
            duration=12,
            start_date=today + timedelta(days=28),
            end_date=today + timedelta(days=40),
            dependencies="4",
            progress=0.0,
            predicted_delay=0,
            risk_factors="None"
        )
    ]
    
    # Calculate CPM for baseline
    run_cpm_algorithm(baseline_tasks)
    
    # Write to database
    for task in baseline_tasks:
        db.add(task)
    db.commit()
    
    return db.query(ScheduleTask).all()


@router.get("/tasks", response_model=List[ScheduleTaskResponse])
def get_tasks(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Retrieve all project tasks. Auto-initializes if database is empty."""
    tasks = db.query(ScheduleTask).order_by(ScheduleTask.id.asc()).all()
    if not tasks:
        tasks = initialize_baseline_schedule(db)
    return tasks


@router.post("/predict", response_model=List[ScheduleTaskResponse])
def predict_delays(
    schema: DelayPredictionRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Forecasting tool: Predict delays based on weather/labor risk parameters,
    reschedule successor start dates, and recompute CPM critical paths.
    """
    tasks = db.query(ScheduleTask).order_by(ScheduleTask.id.asc()).all()
    if not tasks:
        tasks = initialize_baseline_schedule(db)

    # 1. Execute delay forecast and reschedule
    predict_schedule_delays(tasks, schema.weather_risk, schema.labor_risk)
    db.commit()

    # 2. Log activity audit
    log_activity(
        db,
        current_user.id,
        current_user.role,
        "SCHEDULE_PREDICT",
        f"Simulated delay prediction (Weather: {int(schema.weather_risk*100)}%, Labor: {int(schema.labor_risk*100)}%)"
    )

    return tasks


@router.post("/reset", response_model=List[ScheduleTaskResponse])
def reset_schedule(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Reverts task schedule timelines to baseline plan specs."""
    # Delete existing tasks to simplify reset
    db.query(ScheduleTask).delete()
    db.commit()
    
    # Reinitialize baseline tasks
    tasks = initialize_baseline_schedule(db)

    # Log activity audit
    log_activity(
        db,
        current_user.id,
        current_user.role,
        "SCHEDULE_RESET",
        "Reverted project schedule to original baseline plan."
    )

    return tasks
