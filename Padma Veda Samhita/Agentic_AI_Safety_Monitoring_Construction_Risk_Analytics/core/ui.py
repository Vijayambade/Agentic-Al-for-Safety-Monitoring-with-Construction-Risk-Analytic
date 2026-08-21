import streamlit as st


from core.utils import (
    get_metrics,
    get_recent_activity,
    get_projects,
    get_quick_actions,
)
from core.auth import render_logout_button

# =========================================================
# SIDEBAR
# =========================================================

def render_sidebar():

    with st.sidebar:

        st.markdown("""
        <div style="text-align:center;padding:20px 0;">

        <h2 style="color:white;">
        Agentic AI Safety Monitoring Construction Risk Analytics</h2>

        </div>
        """, unsafe_allow_html=True)

        st.divider()

        menu = [
            ("🏠 Dashboard", "Dashboard"),
            ("📁 Projects", "Projects"),
            ("🤖 AI Assistant", "AI Assistant"),
            ("📊 Analytics", "Analytics"),
            ("🧮 Estimators", "Estimators"),
            ("📚 Knowledge Hub", "Knowledge Hub"),
            ("📄 Reports", "Reports"),
                ]

        for text, page in menu:

            if st.button(
                text,
                use_container_width=True,
                key=f"sidebar_{page}",
            ):

                st.session_state.page = page
                st.rerun()

        st.divider()
        render_logout_button()

    return st.session_state.page
        
    

# =========================================================
# HEADER
# =========================================================

def render_header():

    left, right = st.columns([5, 1])

    with left:

        st.title("Agentic AI Safety Monitoring Construction Risk Analytics")

        st.markdown(
"""
<span style="font-size:18px;color:#6B7280;">
Monitor projects, AI insights, reports, analytics and construction activities
from one intelligent workspace.
</span>
""",
unsafe_allow_html=True
)

    with right:

        st.write("")
        st.write("")
        if st.button("➕ New Project", key="dashboard_new_project"):
            st.session_state.page = "Projects"
            st.session_state.show_add_project = True
            st.rerun()

# =========================================================
# KPI CARDS
# =========================================================

def render_metrics():

    metrics = get_metrics()

    cols = st.columns(2)

    icons = [
        "🏗️",
        "📈",
        
    ]

    for col, metric, icon in zip(cols, metrics, icons):

        with col:

            st.metric(
    f"{icon} {metric['title']}",
    metric["value"],
    metric["delta"],
)



# =========================================================
# RECENT ACTIVITY
# =========================================================
def render_recent_activity():

    st.subheader("Recent Activity")

    activity = get_recent_activity()

    if activity == ["No recent activity."]:
        st.info("No recent activity.")
        return

    for item in activity:

        st.markdown(
f"""
<div style="
background:white;
padding:18px;
border-radius:12px;
margin-bottom:12px;
box-shadow:0 4px 10px rgba(0,0,0,.05);
">

<b>{item}</b>

<br>

<small style="color:gray;">Today</small>

</div>
""",
unsafe_allow_html=True,
)

# =========================================================
# PROJECT OVERVIEW
# =========================================================

def render_project_overview():

    st.subheader("Project Overview")

    for project, progress in get_projects():
        left,right=st.columns([5,1])
        with left:
            st.write(project)
        with right:
            st.write(f"**{progress}%**")
        st.progress(progress/100)
        st.write("")

# =========================================================
# QUICK ACTIONS
# =========================================================

def render_quick_actions():

    st.subheader("⚡ Quick Actions")

    col1, col2, col3, col4 = st.columns(4)

# -----------------------------------------------------
# New Project
# -----------------------------------------------------

    with col1:

        if st.button(
            "➕ New Project",
            key="quick_new_project",
            use_container_width=True,
            type="primary",
        ):

            st.session_state.page = "Projects"
            st.session_state.show_add_project = True
            st.rerun()

# -----------------------------------------------------
# Upload Drawing
# -----------------------------------------------------

    with col2:

        if st.button(
            "📄 Upload Drawing",
            key="quick_upload",
            use_container_width=True,
            type="primary",
        ):

            st.session_state.page = "Projects"
            st.session_state.upload_mode = True
            st.rerun()

# -----------------------------------------------------
# AI Assistant
# -----------------------------------------------------

    with col3:

        if st.button(
            "🤖 AI Assistant",
            key="quick_ai",
            use_container_width=True,
            type="primary",
        ):

            st.session_state.page = "AI Assistant"
            st.rerun()

# -----------------------------------------------------
# Reports
# -----------------------------------------------------

    with col4:

        if st.button(
            "📊 Reports",
            key="quick_reports",
            use_container_width=True,
            type="primary",
        ):

            st.session_state.page = "Reports"
            st.rerun()
# =========================================================
# FOOTER
# =========================================================

def render_footer():

    st.divider()
    
    st.markdown("""
<div style="text-align:center;
padding:10px 0;
color:#6B7280;
line-height:1.6;">

<b>Construction Intelligence Hub</b>

</div>
""", unsafe_allow_html=True)