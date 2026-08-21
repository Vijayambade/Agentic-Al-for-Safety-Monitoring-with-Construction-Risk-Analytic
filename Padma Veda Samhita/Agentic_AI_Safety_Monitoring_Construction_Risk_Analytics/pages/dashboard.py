"""
=========================================================
Dashboard Page
=========================================================
"""

import streamlit as st

from core.ui import (
    render_sidebar,
    render_header,
    render_metrics,
    render_recent_activity,
    render_project_overview,
    render_quick_actions,
    render_footer,
)


def render_dashboard():
    """Render the main dashboard."""

    

    # Header
    render_header()

    st.markdown("---")

    # KPI Cards
    render_metrics()

    st.markdown("###")

    render_recent_activity()

    st.markdown("###")

    # Project Overview
    render_project_overview()

    st.markdown("###")

    # Quick Actions
    render_quick_actions()

    st.markdown("###")

    # Footer
    render_footer()