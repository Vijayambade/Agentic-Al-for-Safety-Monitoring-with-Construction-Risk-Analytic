"""
===========================================================
Main Entry Point
===========================================================
"""

import streamlit as st


from core.utils import configure_page, load_local_css
from core.auth import require_login
from core.database import get_or_seed_projects
from pages.dashboard import render_dashboard
from pages.projects import render_projects
from pages.ai_assistant import render_ai_assistant
from pages.analytics import render_analytics
from pages.estimators import render_estimators
from pages.knowledge_hub import render_knowledge_hub
from pages.reports import render_reports
from core.ui import render_sidebar


# ----------------------------------------------------------
# Configure Application
# ----------------------------------------------------------

configure_page()
load_local_css()

# ----------------------------------------------------------
# Login Gate
# ----------------------------------------------------------
# Nothing below this line runs until the user is logged in.

require_login()

if "page" not in st.session_state:
    st.session_state.page = "Dashboard"

if "show_add_project" not in st.session_state:
    st.session_state.show_add_project = False

if "upload_mode" not in st.session_state:
    st.session_state.upload_mode = False

# ADD THIS
if "projects" not in st.session_state:

    # Projects now come from the SQLite database
    # (database/construction.db) instead of being hard-coded.
    # The first time the app ever runs, it seeds the same 3
    # demo projects so nothing looks different -- but from
    # then on, everything is read from / written to the DB.
    st.session_state["projects"] = get_or_seed_projects()

    # AI Assistant Chat History
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []
# Recent Activity
if "recent_activity" not in st.session_state:
    st.session_state.recent_activity = []
# ----------------------------------------------------------
# Navigation
# ----------------------------------------------------------

selected = render_sidebar()
st.session_state.page = selected
if selected == "Dashboard":
    render_dashboard()

elif selected == "Projects":
    render_projects()

# We'll add the remaining pages later
elif selected == "AI Assistant":
    render_ai_assistant()
    

elif selected == "Analytics":
    render_analytics()

elif selected == "Estimators":
    render_estimators()

elif selected == "Knowledge Hub":
    render_knowledge_hub()

elif selected == "Reports":
    render_reports()

