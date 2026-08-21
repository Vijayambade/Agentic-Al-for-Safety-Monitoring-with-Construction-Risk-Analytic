"""
=========================================================
Database Layer (SQLite)
=========================================================

This module is the single place the app talks to the
database. It provides:

- User accounts (for the Login page)
- Project storage (so projects survive an app restart)
- Report storage (so every generated report is saved and
  can be re-downloaded later from "Report History")

SQLite is used because it needs no separate server -- the
whole database lives in one file: database/construction.db
"""

import sqlite3
import hashlib
import secrets
from pathlib import Path
from datetime import datetime

DB_PATH = Path(__file__).resolve().parent.parent / "database" / "construction.db"


def get_connection():
    """Open a connection to the SQLite database file."""
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    """Create all tables if they do not already exist."""
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            full_name TEXT,
            email TEXT,
            password_hash TEXT NOT NULL,
            salt TEXT NOT NULL,
            created_at TEXT
        )
    """)

    # This matches the "projects" table that already existed
    # in database/construction.db, so any data already in
    # there is kept as-is.
    cur.execute("""
        CREATE TABLE IF NOT EXISTS projects (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            project_name TEXT,
            client TEXT,
            location TEXT,
            engineer TEXT,
            start_date TEXT,
            end_date TEXT,
            status TEXT,
            progress INTEGER,
            budget REAL
        )
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS reports (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT,
            generated_by TEXT,
            summary TEXT,
            pdf BLOB,
            created_at TEXT
        )
    """)

    conn.commit()
    conn.close()


# =========================================================
# PASSWORD HASHING
# =========================================================
# Passwords are never stored in plain text. Each password is
# combined with a random salt and hashed using PBKDF2-SHA256.

def hash_password(password, salt=None):
    if salt is None:
        salt = secrets.token_hex(16)

    pwd_hash = hashlib.pbkdf2_hmac(
        "sha256",
        password.encode("utf-8"),
        salt.encode("utf-8"),
        100_000,
    ).hex()

    return pwd_hash, salt


# =========================================================
# USERS
# =========================================================

def create_user(username, password, full_name="", email=""):
    """Create a new user account. Returns (success, message)."""
    username = username.strip()

    conn = get_connection()
    cur = conn.cursor()

    cur.execute("SELECT id FROM users WHERE username = ?", (username,))
    if cur.fetchone():
        conn.close()
        return False, "That username is already taken."

    pwd_hash, salt = hash_password(password)

    cur.execute(
        """INSERT INTO users
           (username, full_name, email, password_hash, salt, created_at)
           VALUES (?, ?, ?, ?, ?, ?)""",
        (username, full_name, email, pwd_hash, salt, datetime.now().isoformat()),
    )

    conn.commit()
    conn.close()
    return True, "Account created successfully."


def verify_user(username, password):
    """Check username/password. Returns (success, user_dict_or_None)."""
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM users WHERE username = ?", (username.strip(),))
    row = cur.fetchone()
    conn.close()

    if row is None:
        return False, None

    pwd_hash, _ = hash_password(password, row["salt"])

    if pwd_hash == row["password_hash"]:
        return True, dict(row)

    return False, None


# =========================================================
# PROJECTS
# =========================================================

def _row_to_project(row):
    return {
        "id": row["id"],
        "name": row["project_name"],
        "client": row["client"],
        "location": row["location"],
        "engineer": row["engineer"],
        "start_date": row["start_date"],
        "end_date": row["end_date"],
        "status": row["status"],
        "progress": row["progress"] if row["progress"] is not None else 0,
        "budget": row["budget"] if row["budget"] is not None else 0,
    }


def get_all_projects():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM projects ORDER BY id")
    rows = cur.fetchall()
    conn.close()
    return [_row_to_project(r) for r in rows]


def add_project(project):
    """Insert a new project. Returns the new project id."""
    conn = get_connection()
    cur = conn.cursor()

    cur.execute(
        """INSERT INTO projects
           (project_name, client, location, engineer, start_date,
            end_date, status, progress, budget)
           VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
        (
            project.get("name", ""),
            project.get("client", ""),
            project.get("location", ""),
            project.get("engineer", ""),
            str(project.get("start_date", "")),
            str(project.get("end_date", "")),
            project.get("status", "Planning"),
            project.get("progress", 0),
            project.get("budget", 0) or 0,
        ),
    )

    conn.commit()
    new_id = cur.lastrowid
    conn.close()
    return new_id


def update_project(project_id, project):
    """Update an existing project by id."""
    conn = get_connection()
    cur = conn.cursor()

    cur.execute(
        """UPDATE projects SET
           project_name = ?, client = ?, location = ?,
           status = ?, progress = ?
           WHERE id = ?""",
        (
            project.get("name", ""),
            project.get("client", ""),
            project.get("location", ""),
            project.get("status", ""),
            project.get("progress", 0),
            project_id,
        ),
    )

    conn.commit()
    conn.close()


def delete_project(project_id):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("DELETE FROM projects WHERE id = ?", (project_id,))
    conn.commit()
    conn.close()


def get_or_seed_projects():
    """
    Load projects from the database. The very first time the
    app is run (empty database) it seeds the same 3 demo
    projects that used to be hard-coded, so the app still
    looks the same on first launch -- but from then on every
    project lives in the database.
    """
    projects = get_all_projects()

    if len(projects) == 0:
        demo_projects = [
            {"name": "Skyline Tower", "client": "ABC Builders",
             "location": "Bangalore", "status": "Active", "progress": 82},
            {"name": "Metro Extension", "client": "Metro Rail",
             "location": "Mysore", "status": "Planning", "progress": 67},
            {"name": "Green Residency", "client": "Green Homes",
             "location": "Hyderabad", "status": "Completed", "progress": 91},
        ]
        for p in demo_projects:
            add_project(p)
        projects = get_all_projects()

    return projects


# =========================================================
# REPORTS
# =========================================================

def save_report(title, generated_by, summary, pdf_bytes):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        """INSERT INTO reports (title, generated_by, summary, pdf, created_at)
           VALUES (?, ?, ?, ?, ?)""",
        (title, generated_by, summary, pdf_bytes, datetime.now().isoformat()),
    )
    conn.commit()
    new_id = cur.lastrowid
    conn.close()
    return new_id


def get_reports(limit=20):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        """SELECT id, title, generated_by, created_at
           FROM reports ORDER BY id DESC LIMIT ?""",
        (limit,),
    )
    rows = cur.fetchall()
    conn.close()
    return [dict(r) for r in rows]


def get_report_pdf(report_id):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT pdf FROM reports WHERE id = ?", (report_id,))
    row = cur.fetchone()
    conn.close()
    return row["pdf"] if row else None


# Make sure the tables exist as soon as this module is imported
# anywhere in the app (some pages read from the database at
# import time, before main.py gets a chance to call init_db()
# itself), so ordering of imports never matters.
init_db()
