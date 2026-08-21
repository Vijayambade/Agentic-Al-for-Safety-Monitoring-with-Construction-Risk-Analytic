"""
Simple CSV-backed persistence for labour records and attendance.
Keeps data across app restarts without needing a real database.
"""

import pandas as pd
from pathlib import Path

DATA_DIR = Path(__file__).resolve().parent.parent / "data"
DATA_DIR.mkdir(exist_ok=True)

LABOUR_FILE = DATA_DIR / "labour_master.csv"
ATTENDANCE_FILE = DATA_DIR / "attendance.csv"

LABOUR_COLUMNS = ["LabourID", "Name", "Role", "Contact", "DailyWage", "JoinDate"]
ATTENDANCE_COLUMNS = ["Date", "LabourID", "Name", "Status", "WagePayable"]


def _ensure_file(path: Path, columns: list[str]):
    if not path.exists():
        pd.DataFrame(columns=columns).to_csv(path, index=False)


# ---------- Labour master ----------

def load_labour() -> pd.DataFrame:
    _ensure_file(LABOUR_FILE, LABOUR_COLUMNS)
    return pd.read_csv(LABOUR_FILE)


def save_labour(df: pd.DataFrame):
    df.to_csv(LABOUR_FILE, index=False)


def add_labour(name: str, role: str, contact: str, daily_wage: float, join_date: str) -> int:
    df = load_labour()
    next_id = 1 if df.empty else int(df["LabourID"].max()) + 1
    new_row = {
        "LabourID": next_id, "Name": name, "Role": role,
        "Contact": contact, "DailyWage": daily_wage, "JoinDate": join_date,
    }
    df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)
    save_labour(df)
    return next_id


def delete_labour(labour_id: int):
    df = load_labour()
    df = df[df["LabourID"] != labour_id]
    save_labour(df)


# ---------- Attendance ----------

def load_attendance() -> pd.DataFrame:
    _ensure_file(ATTENDANCE_FILE, ATTENDANCE_COLUMNS)
    return pd.read_csv(ATTENDANCE_FILE)


def save_attendance(df: pd.DataFrame):
    df.to_csv(ATTENDANCE_FILE, index=False)


def mark_attendance(entries: list[dict]):
    """entries: list of {Date, LabourID, Name, Status, WagePayable}.
    Overwrites any existing record for the same Date + LabourID (so re-marking
    a day doesn't create duplicates)."""
    df = load_attendance()
    new_df = pd.DataFrame(entries)
    if not df.empty:
        key = df["Date"].astype(str) + "_" + df["LabourID"].astype(str)
        new_key = new_df["Date"].astype(str) + "_" + new_df["LabourID"].astype(str)
        df = df[~key.isin(new_key)]
    df = pd.concat([df, new_df], ignore_index=True)
    save_attendance(df)
