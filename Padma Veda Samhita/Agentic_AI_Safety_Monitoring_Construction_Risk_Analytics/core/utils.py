"""
=========================================================
Utility Functions
=========================================================
"""

from pathlib import Path
import streamlit as st

# -------------------------------------------------------
# APP CONFIGURATION
# -------------------------------------------------------

APP_NAME = "Agentic AI Safety Monitoring Construction Risk Analytics"
PAGE_ICON = "🏗️"


def configure_page():
    """Configure Streamlit page."""

    st.set_page_config(
        page_title=APP_NAME,
        page_icon=PAGE_ICON,
        layout="wide",
        initial_sidebar_state="expanded",
    )


# -------------------------------------------------------
# LOAD CSS
# -------------------------------------------------------

def load_local_css():
    """Load custom CSS."""

    css_file = Path("styles/style.css")

    if css_file.exists():
        with open(css_file, "r", encoding="utf-8") as f:
            st.markdown(
                f"<style>{f.read()}</style>",
                unsafe_allow_html=True,
            )


# -------------------------------------------------------
# DASHBOARD DATA
# -------------------------------------------------------
def get_metrics():

    projects = st.session_state.get("projects", [])

    total_projects = len(projects)

    if total_projects > 0:
        avg_progress = int(
            sum(p["progress"] for p in projects) / total_projects
        )
    else:
        avg_progress = 0

    return [

        {
            "title": "Active Projects",
            "value": total_projects,
            "delta": "",
        },

        {
            "title": "Overall Progress",
            "value": f"{avg_progress}%",
            "delta": "",
        },

            ]


def get_recent_activity():

    activity = st.session_state.get("recent_activity", [])

    if len(activity) == 0:
        return ["No recent activity."]

    return activity
def get_projects():

    projects = st.session_state.get("projects", [])

    data = []

    for project in projects:

        data.append(
            (
                project["name"],
                project["progress"],
            )
        )

    return data


def get_quick_actions():
    return [
        "➕ New Project",
        "📄 Upload Drawing",
        "🤖 AI Assistant",
        "📊 Reports",
    ]