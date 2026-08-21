"""
backend/services/dashboard_service.py
-------------------------------------
Service logic for fetching and updating dashboard data, tasks, and role-specific stats.
"""
from datetime import datetime, timedelta
import random
from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session

from backend.models.dashboard import TaskItem, ActivityLog, SystemNotification
from backend.schemas.dashboard import TaskCreate, TaskUpdate


# ---------------------------------------------------------------------------
# Tasks Management
# ---------------------------------------------------------------------------
def get_user_tasks(db: Session, user_id: int, role: str) -> List[TaskItem]:
    """
    Retrieve all tasks for a specific user.

    If none exist, seeds default starting tasks based on the user's role.
    """
    tasks = db.query(TaskItem).filter(TaskItem.user_id == user_id).all()
    if not tasks:
        # Seed default tasks
        default_titles = {
            "Admin": [
                "Review system logs and diagnostics",
                "Verify MongoDB connection status",
                "Audit user access controls",
            ],
            "Project Manager": [
                "Finalise phase 2 Gantt schedule",
                "Approve subcontractor billings",
                "Conduct weekly progress review",
            ],
            "HR": [
                "Interview new Site Supervisor candidates",
                "Process monthly payroll for field workers",
                "Organise safety training seminar",
            ],
            "Contractor": [
                "Submit concrete supply invoice",
                "Inspect foundation rebar installation",
                "Request safety permit extension",
            ],
            "Engineer": [
                "Approve load-bearing beam blueprints",
                "Conduct soil stability test analysis",
                "Review concrete compressive strength logs",
            ],
            "Worker": [
                "Complete morning toolbox talk",
                "Inspect safety harness before scaffolding work",
                "Log concrete mixing checklist",
            ],
            "Client": [
                "Review phase 1 structural report",
                "Approve milestone payment #3",
                "Schedule site walkthrough",
            ],
            "Supplier": [
                "Deliver steel reinforcement order #108",
                "Update brick inventory levels",
                "Submit quote for phase 3 plumbing fittings",
            ],
            "Safety Officer": [
                "Conduct morning site safety walk",
                "Inspect fire extinguisher certifications",
                "Log weekly OSHA compliance scorecard",
            ],
            "Site Supervisor": [
                "Log daily crane operation hours",
                "Conduct worker attendance check-in",
                "Verify concrete pour alignment",
            ],
            "Volunteer": [
                "Organise community center painting crew",
                "Distribute PPE safety glasses",
                "Log volunteer registration logs",
            ],
        }

        roles_tasks = default_titles.get(role, ["Complete onboarding steps"])
        for idx, title in enumerate(roles_tasks):
            new_task = TaskItem(
                user_id=user_id,
                title=title,
                description=f"Initial task for the {role} workspace.",
                is_completed=False,
                due_date=datetime.utcnow() + timedelta(days=idx + 1),
            )
            db.add(new_task)
        db.commit()
        tasks = db.query(TaskItem).filter(TaskItem.user_id == user_id).all()

    return tasks


def create_user_task(db: Session, user_id: int, schema: TaskCreate) -> TaskItem:
    """Create a new task item for a user."""
    new_task = TaskItem(
        user_id=user_id,
        title=schema.title,
        description=schema.description,
        is_completed=False,
        due_date=schema.due_date,
    )
    db.add(new_task)
    db.commit()
    db.refresh(new_task)
    return new_task


def update_user_task(
    db: Session, user_id: int, task_id: int, schema: TaskUpdate
) -> TaskItem:
    """Update an existing task item. Raises exception if not owned by user."""
    task = (
        db.query(TaskItem)
        .filter(TaskItem.id == task_id, TaskItem.user_id == user_id)
        .first()
    )
    if not task:
        from fastapi import HTTPException, status

        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task item not found or unauthorized.",
        )

    if schema.title is not None:
        task.title = schema.title
    if schema.description is not None:
        task.description = schema.description
    if schema.is_completed is not None:
        task.is_completed = schema.is_completed
    if schema.due_date is not None:
        task.due_date = schema.due_date

    db.commit()
    db.refresh(task)
    return task


# ---------------------------------------------------------------------------
# Activity Logging
# ---------------------------------------------------------------------------
def get_user_activities(db: Session, user_id: int) -> List[ActivityLog]:
    """Retrieve the recent activity log for a user."""
    return (
        db.query(ActivityLog)
        .filter(ActivityLog.user_id == user_id)
        .order_by(ActivityLog.timestamp.desc())
        .limit(10)
        .all()
    )


def log_activity(
    db: Session, user_id: int, role: str, action_type: str, description: str
) -> ActivityLog:
    """Log an activity action taken by the user."""
    log = ActivityLog(
        user_id=user_id,
        role=role,
        action_type=action_type,
        description=description,
    )
    db.add(log)
    db.commit()
    db.refresh(log)
    return log


# ---------------------------------------------------------------------------
# System Notifications
# ---------------------------------------------------------------------------
def get_user_notifications(
    db: Session, user_id: int, role: str
) -> List[SystemNotification]:
    """
    Retrieve all notifications relevant to the user: global, role-based, or direct.
    """
    notifications = (
        db.query(SystemNotification)
        .filter(
            (SystemNotification.user_id == user_id)
            | (SystemNotification.role == role)
            | (
                (SystemNotification.user_id == None)
                & (SystemNotification.role == None)
            )
        )
        .order_by(SystemNotification.created_at.desc())
        .limit(15)
        .all()
    )

    if not notifications:
        # Seed default notifications
        defaults = [
            (
                "Welcome to Construction Hub",
                f"You have been onboarded as a platform {role}. Please check your widgets.",
                None,
            ),
            (
                "OSHA Safety Notice",
                "Ensure all site personnel are equipped with active PPE (Hard Hats, Safety Vests).",
                "Safety Officer",
            ),
            (
                "Material Alert",
                "Warehouse stock alert: Brick and structural steel levels are running low.",
                "Supplier",
            ),
            (
                "Budget Milestone",
                "Phase 1 construction costs have been finalized and pushed for client review.",
                "Project Manager",
            ),
        ]

        for title, msg, target_role in defaults:
            # Seed matching or general notifications
            if target_role is None or target_role == role:
                new_notif = SystemNotification(
                    user_id=user_id,
                    role=target_role,
                    title=title,
                    message=msg,
                    is_read=False,
                )
                db.add(new_notif)
        db.commit()
        notifications = (
            db.query(SystemNotification)
            .filter(
                (SystemNotification.user_id == user_id)
                | (SystemNotification.role == role)
                | (
                    (SystemNotification.user_id == None)
                    & (SystemNotification.role == None)
                )
            )
            .order_by(SystemNotification.created_at.desc())
            .all()
        )

    return notifications


# ---------------------------------------------------------------------------
# Role-Specific Analytics & Charts Generation
# ---------------------------------------------------------------------------
def get_role_dashboard_stats(
    db: Session, user_id: int, role: str
) -> Dict[str, Any]:
    """
    Generate statistics, charts datasets, and calendar logs tailored to a role.
    """
    tasks = get_user_tasks(db, user_id, role)
    notifications = get_user_notifications(db, user_id, role)
    activities = get_user_activities(db, user_id)

    # Initialise defaults
    metrics = {}
    charts_data = {}
    calendar_events = []

    # Map current datetime
    today = datetime.now()

    # 1. ADMIN
    if role == "Admin":
        metrics = {
            "active_users": 142,
            "system_health": "99.8%",
            "db_connections": 12,
            "api_requests_24h": 3480,
        }
        charts_data = {
            "chart_type": "bar",
            "categories": [
                "Admin",
                "Engineer",
                "Contractor",
                "Worker",
                "HR",
                "Safety Officer",
            ],
            "values": [3, 15, 8, 80, 5, 4],
            "title": "Platform Registered Users by Role",
        }
        calendar_events = [
            {
                "title": "Database Maintenance",
                "start": (today + timedelta(days=2)).strftime("%Y-%m-%d 02:00"),
                "end": (today + timedelta(days=2)).strftime("%Y-%m-%d 04:00"),
            }
        ]

    # 2. ENGINEER
    elif role == "Engineer":
        metrics = {
            "blueprints_reviewed": 18,
            "pending_approvals": 4,
            "material_tests_passed": 36,
            "calculation_reports": 8,
        }
        charts_data = {
            "chart_type": "line",
            "x_axis": ["Week 1", "Week 2", "Week 3", "Week 4"],
            "y_axis": [92, 95, 94, 98],
            "title": "Concrete Compressive Strength Average (MPa)",
        }
        calendar_events = [
            {
                "title": "Blueprint Approval Review",
                "start": today.strftime("%Y-%m-%d 10:00"),
                "end": today.strftime("%Y-%m-%d 11:30"),
            }
        ]

    # 3. CONTRACTOR
    elif role == "Contractor":
        metrics = {
            "active_subcontracts": 7,
            "billings_submitted": "$124,500",
            "milestones_approved": "8 / 10",
            "unresolved_rfis": 3,
        }
        charts_data = {
            "chart_type": "bar",
            "categories": [
                "Excavation",
                "Foundation",
                "Framing",
                "Roofing",
                "Plumbing",
            ],
            "values": [100, 100, 85, 20, 0],
            "title": "Contractor Subcontract Completion (%)",
        }
        calendar_events = [
            {
                "title": "Concrete Subcontract Bid Review",
                "start": (today + timedelta(days=1)).strftime("%Y-%m-%d 14:00"),
                "end": (today + timedelta(days=1)).strftime("%Y-%m-%d 15:30"),
            }
        ]

    # 4. WORKER
    elif role == "Worker":
        metrics = {
            "shifts_attended": 22,
            "hours_logged": 176,
            "safety_toolbox_talks": 22,
            "salary_earned": "$3,520",
        }
        charts_data = {
            "chart_type": "bar",
            "categories": ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat"],
            "values": [8.0, 8.5, 8.0, 9.0, 8.0, 4.0],
            "title": "Daily Hours Logged (Current Week)",
        }
        calendar_events = [
            {
                "title": "Shift A: Main Building Framing",
                "start": today.strftime("%Y-%m-%d 08:00"),
                "end": today.strftime("%Y-%m-%d 17:00"),
            }
        ]

    # 5. HR
    elif role == "HR":
        metrics = {
            "total_headcount": 118,
            "open_requisitions": 9,
            "payroll_processed": "Yes (June)",
            "training_completed": "94%",
        }
        charts_data = {
            "chart_type": "pie",
            "labels": [
                "Full-Time staff",
                "Subcontractor field",
                "Apprentices",
                "Admin Support",
            ],
            "values": [18, 80, 12, 8],
            "title": "Workforce Demographics distribution",
        }
        calendar_events = [
            {
                "title": "Site Supervisor Interview",
                "start": (today + timedelta(days=1)).strftime("%Y-%m-%d 11:00"),
                "end": (today + timedelta(days=1)).strftime("%Y-%m-%d 12:00"),
            }
        ]

    # 6. CLIENT
    elif role == "Client":
        metrics = {
            "overall_completion": "64.2%",
            "payments_processed": "$450,000",
            "outstanding_invoices": "$75,000",
            "upcoming_milestone": "Roof Structure Complete",
        }
        charts_data = {
            "chart_type": "line",
            "x_axis": ["Jan", "Feb", "Mar", "Apr", "May", "Jun"],
            "y_axis": [10, 22, 35, 48, 58, 64],
            "title": "Project Phase Completion Track (%)",
        }
        calendar_events = [
            {
                "title": "Monthly Progress Walkthrough",
                "start": (today + timedelta(days=3)).strftime("%Y-%m-%d 15:00"),
                "end": (today + timedelta(days=3)).strftime("%Y-%m-%d 16:30"),
            }
        ]

    # 7. SUPPLIER
    elif role == "Supplier":
        metrics = {
            "active_purchase_orders": 8,
            "orders_delivered": 42,
            "materials_value": "$64,200",
            "low_stock_warnings": 2,
        }
        charts_data = {
            "chart_type": "bar",
            "categories": ["Cement", "Steel Rebar", "Bricks", "Gravel", "Timber"],
            "values": [80, 15, 90, 45, 10],
            "title": "Warehouse Materials Inventory Levels (%)",
        }
        calendar_events = [
            {
                "title": "Reinforcement Steel Dispatch",
                "start": today.strftime("%Y-%m-%d 06:00"),
                "end": today.strftime("%Y-%m-%d 08:00"),
            }
        ]

    # 8. SAFETY OFFICER
    elif role == "Safety Officer":
        metrics = {
            "days_since_accident": 142,
            "safety_score": "98.5%",
            "active_inspections": 3,
            "hazard_reports": 2,
        }
        charts_data = {
            "chart_type": "line",
            "x_axis": ["Apr", "May", "Jun", "Jul"],
            "y_axis": [1, 2, 0, 0],
            "title": "Monthly Safety Incidents Reported",
        }
        calendar_events = [
            {
                "title": "OSHA Audit Walkthrough",
                "start": (today + timedelta(days=2)).strftime("%Y-%m-%d 09:00"),
                "end": (today + timedelta(days=2)).strftime("%Y-%m-%d 12:00"),
            }
        ]

    # 9. SITE SUPERVISOR
    elif role == "Site Supervisor":
        metrics = {
            "field_workers_present": 48,
            "active_machinery": 6,
            "weather_risk": "Low (Clear)",
            "rfi_responses_pending": 2,
        }
        charts_data = {
            "chart_type": "bar",
            "categories": ["Excavators", "Cranes", "Dump Trucks", "Mixers"],
            "values": [100, 80, 50, 100],
            "title": "Heavy Machinery Utilization Rate (%)",
        }
        calendar_events = [
            {
                "title": "Concrete Pouring Log Check",
                "start": today.strftime("%Y-%m-%d 13:00"),
                "end": today.strftime("%Y-%m-%d 15:00"),
            }
        ]

    # 10. VOLUNTEER
    elif role == "Volunteer":
        metrics = {
            "active_volunteers": 34,
            "volunteer_hours": 240,
            "community_projects": 2,
            "donations_allocated": "$8,200",
        }
        charts_data = {
            "chart_type": "bar",
            "categories": [
                "Painting",
                "Landscaping",
                "Debris Cleaning",
                "Safety Setup",
            ],
            "values": [12, 8, 20, 10],
            "title": "Volunteer Hours by Project Subtask",
        }
        calendar_events = [
            {
                "title": "Community Park Painting Kickoff",
                "start": (today + timedelta(days=1)).strftime("%Y-%m-%d 09:00"),
                "end": (today + timedelta(days=1)).strftime("%Y-%m-%d 14:00"),
            }
        ]

    # 11. PROJECT MANAGER (DEFAULT / CORE)
    else:  # Project Manager
        metrics = {
            "overall_progress": "42%",
            "budget_spent": "48%",
            "days_remaining": 128,
            "active_issues": 3,
        }
        charts_data = {
            "chart_type": "line",
            "x_axis": ["Week 1", "Week 2", "Week 3", "Week 4", "Week 5"],
            "y_axis": [10, 18, 25, 32, 42],
            "title": "Gantt Project Progress Timeline (%)",
        }
        calendar_events = [
            {
                "title": "Project Stakeholder Status Sync",
                "start": today.strftime("%Y-%m-%d 16:00"),
                "end": today.strftime("%Y-%m-%d 17:00"),
            }
        ]

    # Transform Task models to dictionary responses
    tasks_resp = [
        {
            "id": t.id,
            "user_id": t.user_id,
            "title": t.title,
            "description": t.description,
            "is_completed": t.is_completed,
            "due_date": t.due_date,
            "created_at": t.created_at,
        }
        for t in tasks
    ]

    # Transform notifications
    notif_resp = [
        {
            "id": n.id,
            "user_id": n.user_id,
            "role": n.role,
            "title": n.title,
            "message": n.message,
            "is_read": n.is_read,
            "created_at": n.created_at,
        }
        for n in notifications
    ]

    # Transform activities
    act_resp = [
        {
            "id": a.id,
            "user_id": a.user_id,
            "role": a.role,
            "action_type": a.action_type,
            "description": a.description,
            "timestamp": a.timestamp,
        }
        for a in activities
    ]

    return {
        "tasks": tasks_resp,
        "notifications": notif_resp,
        "activities": act_resp,
        "metrics": metrics,
        "charts_data": charts_data,
        "calendar_events": calendar_events,
    }


# ---------------------------------------------------------------------------
# Simulated AI Assistant Response
# ---------------------------------------------------------------------------
def generate_role_chat_response(role: str, user_message: str) -> str:
    """Generate a highly customized, domain-specific simulated AI chatbot response."""
    msg = user_message.lower()

    responses = {
        "Admin": (
            "As the system Administrator, I can assist you with user auditing, database diagnostic logs, "
            "and security configuration checks. Our relational SQLite schema is currently online and fully operational."
        ),
        "Engineer": (
            "Hello Engineer. I can assist you with load calculations, blueprint checks, Concrete Compressive "
            "Strength logs (currently averaging 98MPa under stress test) and structural review criteria."
        ),
        "Contractor": (
            "Welcome Contractor. I can track subcontracts, review progress bills, RFI completions, "
            "and invoice approvals. Let me know if you need to generate a project expense or draw request report."
        ),
        "Worker": (
            "Hi! Remember to wear your Hard Hat and High-Vis Safety Vest at all times today. "
            "I can review your assigned field shifts, toolbox talk confirmations, and attendance hours logged."
        ),
        "HR": (
            "Hello. I am ready to assist you with worker recruitment pipelines, job postings, monthly field payroll, "
            "and contractor onboarding compliance logs."
        ),
        "Client": (
            "Hello Client. Your project overall progress is currently at 64.2% on schedule. "
            "I can help you review payment receipts, download recent engineering progress reports, or submit site walkthrough feedback."
        ),
        "Supplier": (
            "Welcome Supplier. I can help coordinate deliveries (such as Rebar Order #108), monitor inventory "
            "restocking status, and format incoming quotation RFQs."
        ),
        "Safety Officer": (
            "Hello Safety Officer. Our current site has gone 142 days without any incidents. "
            "I can help you generate OSHA safety check cards, log PPE compliance checks, or file safety reports."
        ),
        "Site Supervisor": (
            "Welcome Site Supervisor. Machinery status (Excavators/Cranes) is healthy and worker presence is logged. "
            "Let me know if you need to update crane booking slots or log concrete pours."
        ),
        "Volunteer": (
            "Hi Volunteer! Thank you for supporting our community building projects. "
            "I can help you review upcoming painting/landscaping schedules, track service hours, or register new volunteers."
        ),
        "Project Manager": (
            "Hello Project Manager. Overall construction completion stands at 42%. "
            "I can assist with Gantt timeline calculations, risk alerts, and cost forecasting details."
        ),
    }

    base = responses.get(
        role, "Hello! I am your Construction Intelligent Assistant."
    )

    # Simple keyword routing to feel smart
    if "chart" in msg or "analytics" in msg or "progress" in msg:
        return f"{base} Looking at your active analytics chart, the completion indicators are tracking normally."
    if "task" in msg or "to do" in msg:
        return f"{base} You can manage, add, or complete tasks directly using the Tasks panel on your dashboard."
    if "help" in msg or "capabilities" in msg:
        return f"{base} Let me know how I can make your site management duties simpler."

    return f"{base} How can I assist you with your project today?"
