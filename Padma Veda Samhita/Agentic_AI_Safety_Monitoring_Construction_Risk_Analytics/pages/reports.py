"""
=========================================================
Reports
=========================================================
"""

import streamlit as st
from datetime import datetime
from core.ai import ask_ai, get_project_context
from core.pdf_generator import generate_pdf
from core import database as db


def render_reports():

    st.title("Reports")

    st.caption(
        "Generate project reports and AI summaries."
    )

    st.divider()

    projects = st.session_state.get("projects", [])

    total_projects = len(projects)

    active = sum(
        1 for p in projects
        if p["status"] == "Active"
    )

    completed = sum(
        1 for p in projects
        if p["status"] == "Completed"
    )

    planning = sum(
        1 for p in projects
        if p["status"] == "Planning"
    )

    if total_projects > 0:
        avg_progress = int(
            sum(p["progress"] for p in projects)
            / total_projects
        )
    else:
        avg_progress = 0

    # --------------------------------------------------------
    # REPORT DASHBOARD
    # --------------------------------------------------------

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric(
            "Total Projects",
            total_projects,
        )

    with col2:
        st.metric(
            "Active",
            active,
        )

    with col3:
        st.metric(
            "Completed",
            completed,
        )

    with col4:
        st.metric(
            "Avg Progress",
            f"{avg_progress}%",
        )

    st.markdown("---")

    # --------------------------------------------------------
    # PROJECT DETAILS
    # --------------------------------------------------------

    st.subheader("Project Details")

    if total_projects == 0:

        st.info("No projects available.")

    else:

        for project in projects:

            with st.container(border=True):

                st.write(f"**Project:** {project['name']}")
                st.write(f"**Client:** {project['client']}")
                st.write(f"**Location:** {project['location']}")
                st.write(f"**Status:** {project['status']}")

                st.progress(project["progress"] / 100)

                st.caption(
                    f"{project['progress']}% Completed"
                )

    st.markdown("---")

    if "ai_summary" not in st.session_state:
        st.session_state.ai_summary = ""

    # --------------------------------------------------------
    # AI SUMMARY
    # --------------------------------------------------------

    st.subheader("Project Summary")

    if total_projects == 0:

        st.info("No projects available for analysis.")

    else:

        if st.button("🤖 Generate AI Summary", use_container_width=True):

            with st.spinner("Generating AI project summary..."):

                project_details = ""

                for project in projects:
                    project_details += get_project_context(project["name"])
                    project_details += "\n\n"

                prompt = f"""You are an experienced construction project consultant.
                Analyze ONLY the project information below.
                {project_details}
                Do NOT invent or assume facts that are not provided.
                Base your analysis only on:
                - Project Name
                - Client
                - Location
                - Status
                - Progress
                If information is insufficient, clearly mention that additional project information is required.
                Generate:
                - Executive Summary
                - Current Project Health
                - Key Risks
                - Recommendations
                - Overall Conclusion
                Keep the response under 250 words.
"""

                st.session_state.ai_summary = ask_ai(prompt)
        if st.session_state.ai_summary:
                st.success(st.session_state.ai_summary)

    # --------------------------------------------------------
    # DOWNLOAD REPORT
    # --------------------------------------------------------

    # Remove Markdown symbols from AI response
    clean_summary = (
        st.session_state.ai_summary
        .replace("**", "")
        .replace("###", "")
        .replace("##", "")
    )

    report = f"""
============================================================
              PROJECT ANALYSIS REPORT
============================================================

Generated On : {datetime.now().strftime("%d %B %Y  %I:%M %p")}

------------------------------------------------------------
PROJECT STATISTICS
------------------------------------------------------------

Total Projects      : {total_projects}
Active Projects     : {active}
Completed Projects  : {completed}
Planning Projects   : {planning}
Average Progress    : {avg_progress}%

------------------------------------------------------------
PROJECT DETAILS
------------------------------------------------------------
"""

    # Add every project
    for project in projects:

        report += f"""

Project Name : {project['name']}
Client       : {project['client']}
Location     : {project['location']}
Status       : {project['status']}
Progress     : {project['progress']}%

------------------------------------------------------------
"""

    # Add AI Summary
    report += f"""

EXECUTIVE SUMMARY
------------------------------------------------------------

{clean_summary}

------------------------------------------------------------
RECOMMENDATIONS
------------------------------------------------------------

• Continue weekly progress monitoring.

• Prioritize delayed projects.

• Maintain PPE compliance.

• Review project budgets regularly.

• Perform quality inspections at every milestone.

------------------------------------------------------------

Generated by

Construction Intelligence Hub

AI Powered using Ollama (llama3.2)

============================================================
"""

    pdf = generate_pdf(
        "Construction Intelligence Hub",
        report,
    )

    # ----------------------------------------------------------
    # SAVE REPORT TO DATABASE
    # ----------------------------------------------------------
    # Every time a *new* AI summary is generated, store the
    # resulting PDF in the database so it shows up in
    # "Report History" below and can be re-downloaded later.

    if st.session_state.ai_summary and st.session_state.get(
        "last_saved_summary"
    ) != st.session_state.ai_summary:

        db.save_report(
            title=f"Construction Report - {datetime.now().strftime('%d %b %Y %H:%M')}",
            generated_by=st.session_state.get("username", "guest"),
            summary=st.session_state.ai_summary,
            pdf_bytes=pdf,
        )

        st.session_state.last_saved_summary = st.session_state.ai_summary

    if total_projects == 0:
        st.info("No projects available to generate a report."
        )
    elif st.session_state.ai_summary:
        st.download_button("📄 Download PDF Report",pdf,
                           file_name="construction_report.pdf",
                           mime="application/pdf",
                           use_container_width=True,
        )
    else:
        st.info("Generate the AI Summary before downloading the PDF."
        )

    st.markdown("---")

    # --------------------------------------------------------
    # REPORT HISTORY (stored in the database)
    # --------------------------------------------------------

    st.subheader("🗂 Report History")

    history = db.get_reports()

    if not history:
        st.info("No reports generated yet. Generate an AI Summary above to create one.")
    else:
        for r in history:
            with st.container(border=True):
                c1, c2, c3 = st.columns([3, 2, 1])

                with c1:
                    st.write(f"**{r['title']}**")

                with c2:
                    created = r["created_at"].replace("T", " ")[:16]
                    st.caption(f"By {r['generated_by']} • {created}")

                with c3:
                    pdf_bytes = db.get_report_pdf(r["id"])
                    st.download_button(
                        "⬇ PDF",
                        pdf_bytes,
                        file_name=f"construction_report_{r['id']}.pdf",
                        mime="application/pdf",
                        key=f"hist_dl_{r['id']}",
                        use_container_width=True,
                    )

    st.markdown("---")

    st.caption("Construction Intelligence Hub")