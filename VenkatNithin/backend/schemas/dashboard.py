"""
backend/schemas/dashboard.py
---------------------------
Pydantic validation schemas for tasks, activities, and dashboard payloads.
"""
from datetime import datetime
from typing import List, Dict, Any, Optional
from pydantic import BaseModel


class TaskCreate(BaseModel):
    title: str
    description: Optional[str] = None
    due_date: Optional[datetime] = None


class TaskUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    is_completed: Optional[bool] = None
    due_date: Optional[datetime] = None


class TaskResponse(BaseModel):
    id: int
    user_id: int
    title: str
    description: Optional[str] = None
    is_completed: bool
    due_date: Optional[datetime] = None
    created_at: datetime

    class Config:
        from_attributes = True


class ActivityCreate(BaseModel):
    action_type: str
    description: str


class ActivityResponse(BaseModel):
    id: int
    user_id: int
    role: str
    action_type: str
    description: str
    timestamp: datetime

    class Config:
        from_attributes = True


class NotificationResponse(BaseModel):
    id: int
    user_id: Optional[int] = None
    role: Optional[str] = None
    title: str
    message: str
    is_read: bool
    created_at: datetime

    class Config:
        from_attributes = True


class DashboardStatsResponse(BaseModel):
    tasks: List[TaskResponse]
    notifications: List[NotificationResponse]
    activities: List[ActivityResponse]
    metrics: Dict[str, Any]
    charts_data: Dict[str, Any]
    calendar_events: List[Dict[str, Any]]


class ChatRequest(BaseModel):
    message: str


class ChatResponse(BaseModel):
    response: str
    role: str
