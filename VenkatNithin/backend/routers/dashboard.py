"""
backend/routers/dashboard.py
----------------------------
FastAPI router containing all dashboard operations.
"""
from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from backend.database import get_db
from backend.models.user import User
from backend.routers.auth import get_current_user
from backend.schemas.dashboard import (
    ActivityCreate,
    ActivityResponse,
    ChatRequest,
    ChatResponse,
    DashboardStatsResponse,
    TaskCreate,
    TaskResponse,
    TaskUpdate,
)
from backend.services.dashboard_service import (
    create_user_task,
    generate_role_chat_response,
    get_role_dashboard_stats,
    log_activity,
    update_user_task,
)

router = APIRouter(prefix="/api/v1/dashboard", tags=["Dashboard"])


@router.get("/stats", response_model=DashboardStatsResponse)
def get_stats(
    current_user: User = Depends(get_current_user), db: Session = Depends(get_db)
):
    """Retrieve all stats, tasks, charts, and events for the current user's role."""
    return get_role_dashboard_stats(db, current_user.id, current_user.role)


@router.post("/tasks", response_model=TaskResponse, status_code=status.HTTP_201_CREATED)
def create_task(
    schema: TaskCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Create a new personal task on the user's dashboard."""
    task = create_user_task(db, current_user.id, schema)

    # Log this action
    log_activity(
        db,
        current_user.id,
        current_user.role,
        "CREATE_TASK",
        f"Created task: '{task.title}'",
    )

    return task


@router.put("/tasks/{task_id}", response_model=TaskResponse)
def toggle_task(
    task_id: int,
    schema: TaskUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Update task properties (e.g. check/uncheck completion)."""
    task = update_user_task(db, current_user.id, task_id, schema)

    # Log this action
    status_str = "completed" if task.is_completed else "incomplete"
    log_activity(
        db,
        current_user.id,
        current_user.role,
        "UPDATE_TASK",
        f"Marked task '{task.title}' as {status_str}",
    )

    return task


@router.post("/activities", response_model=ActivityResponse)
def create_custom_activity(
    schema: ActivityCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Log a custom dashboard action or form submission."""
    return log_activity(
        db,
        current_user.id,
        current_user.role,
        schema.action_type,
        schema.description,
    )


@router.post("/chat", response_model=ChatResponse)
def dashboard_chat(
    schema: ChatRequest, current_user: User = Depends(get_current_user)
):
    """Chat with the assistant, returning a role-specific response."""
    reply = generate_role_chat_response(current_user.role, schema.message)
    return {"response": reply, "role": current_user.role}
