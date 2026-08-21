"""
=========================================================
Analytics Page
=========================================================
"""

import streamlit as st
import pandas as pd


# =========================================================
# ANALYTICS PAGE
# =========================================================

def render_analytics():

    # -----------------------------------------------------
    # Header
    # -----------------------------------------------------

    st.title("Analytics")

    st.caption(
        "Monitor project performance, budgets, safety metrics and AI insights."
    )

    st.divider()

    # -----------------------------------------------------
    # Load Project Data
    # -----------------------------------------------------

    projects = st.session_state.get("projects", [])

    total_projects = len(projects)

    active_projects = len(
        [p for p in projects if p["status"] == "Active"]
    )

    completed_projects = len(
        [p for p in projects if p["status"] == "Completed"]
    )

    delayed_projects = len(
        [p for p in projects if p["status"] == "Delayed"]
    )

    if total_projects > 0:

        avg_progress = int(
            sum(p["progress"] for p in projects) / total_projects
        )

    else:

        avg_progress = 0

    # -----------------------------------------------------
    # KPI CARDS
    # -----------------------------------------------------

    c1, c2, c3 = st.columns(3)

    with c1:

        st.metric(
            "Total Projects",
            total_projects,
        )

    with c2:

        st.metric(
            "Active Projects",
            active_projects,
        )

    with c3:

        st.metric(
            "Avg Progress",
            f"{avg_progress}%",
        )

    st.markdown("---")

    # -----------------------------------------------------
    # Project Status Summary
    # -----------------------------------------------------

    st.subheader("Project Status Summary")

    c1, c2, c3 = st.columns(3)

    with c1:

        st.success(f"Completed Projects : {completed_projects}")

    with c2:

        st.info(f"Active Projects : {active_projects}")

    with c3:

        st.warning(f"Delayed Projects : {delayed_projects}")

    st.markdown("---")
        # -----------------------------------------------------
    # PROJECT ANALYTICS
    # -----------------------------------------------------

    st.subheader(" Project Analytics")

    col1, col2 = st.columns(2)

    # ---------------------------------------------
    # Project Progress Chart
    # ---------------------------------------------

    with col1:

        st.markdown("####  Project Progress")

        if len(projects) > 0:

            progress_df = pd.DataFrame(
                {
                    "Project": [p["name"] for p in projects],
                    "Progress": [p["progress"] for p in projects],
                }
            )

            st.bar_chart(
                progress_df.set_index("Project")
            )

        else:

            st.info("No project data available.")

    # ---------------------------------------------
    # Budget Utilization
    # ---------------------------------------------

    with col2:

        st.markdown("####  Budget Utilization")

        budget_df = pd.DataFrame(
            {
                "Category": [
                    "Used",
                    "Remaining",
                ],
                "Amount": [
                    81,
                    19,
                ],
            }
        )

        st.bar_chart(
            budget_df.set_index("Category")
        )

    st.markdown("---")
        # -----------------------------------------------------
    # MONTHLY PROGRESS & SAFETY
    # -----------------------------------------------------

    # -----------------------------------------------------
# MONTHLY PROGRESS
# -----------------------------------------------------

    st.subheader("Monthly Progress")
    monthly_df = pd.DataFrame(
            {
                "Month": [
                    "Jan",
                    "Feb",
                    "Mar",
                    "Apr",
                    "May",
                    "Jun",
                ],
                "Progress": [
                    55,
                    63,
                    69,
                    74,
                    82,
                    90,
                ],
            }
        )

    st.line_chart(
            monthly_df.set_index("Month")
        )
    st.markdown("---")

        # -----------------------------------------------------
    # PROJECT STATUS DISTRIBUTION
    # -----------------------------------------------------

    st.subheader("Project Status Distribution")

    status_counts = {

        "Planning": 0,
        "Active": 0,
        "Completed": 0,
        "Delayed": 0,

    }

    for project in projects:

        status_counts[project["status"]] += 1

    status_df = pd.DataFrame(

        {
            "Status": list(status_counts.keys()),
            "Projects": list(status_counts.values()),
        }

    )

    st.bar_chart(
        status_df.set_index("Status")
    )

    st.markdown("---")
        # -----------------------------------------------------
    # TOP PERFORMING PROJECT
    # -----------------------------------------------------

    st.subheader("Top Performing Project")

    if len(projects) > 0:

        best_project = max(
            projects,
            key=lambda x: x["progress"]
        )

        st.success(
            f"""
### {best_project['name']}

Progress : **{best_project['progress']}%**

Location : **{best_project['location']}**

Status : **{best_project['status']}**
"""
        )

    else:

        st.info("No projects available.")
        st.markdown("---")

    # -----------------------------------------------------
    # PROJECT PERFORMANCE TABLE
    # -----------------------------------------------------

    st.subheader("Project Performance")

    if len(projects) > 0:

        table = pd.DataFrame({

            "Project": [p["name"] for p in projects],

            "Client": [p["client"] for p in projects],

            "Location": [p["location"] for p in projects],

            "Status": [p["status"] for p in projects],

            "Progress (%)": [p["progress"] for p in projects],

        })

        st.dataframe(
            table,
            use_container_width=True,
            hide_index=True,
        )

    else:

        st.info("No project data available.")
        st.markdown("---")

    