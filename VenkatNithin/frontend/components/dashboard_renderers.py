"""
frontend/components/dashboard_renderers.py
-----------------------------------------
Interactive layout renderers for all 11 platform roles.
"""
import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime
from frontend.utils.api_client import APIClient


# ---------------------------------------------------------------------------
# Helper Widgets: Shared Components
# ---------------------------------------------------------------------------
def render_metrics_cards(metrics: dict):
    """Render a row of custom CSS-styled KPI metrics cards."""
    cols = st.columns(len(metrics))
    for col, (label, val) in zip(cols, metrics.items()):
        clean_label = label.replace("_", " ").title()
        col.markdown(
            f"""
            <div class="stat-card">
                <div class="stat-title">{clean_label}</div>
                <div class="stat-value">{val}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )


def render_plotly_chart(charts_data: dict):
    """Render a Plotly chart based on structured data received from backend."""
    chart_type = charts_data.get("chart_type", "line")
    title = charts_data.get("title", "Analytics")

    fig = go.Figure()

    if chart_type == "bar":
        fig.add_trace(
            go.Bar(
                x=charts_data.get("categories", []),
                y=charts_data.get("values", []),
                marker_color="#FF8C00",
                name="Value",
            )
        )
    elif chart_type == "pie":
        fig.add_trace(
            go.Pie(
                labels=charts_data.get("labels", []),
                values=charts_data.get("values", []),
                hole=0.4,
            )
        )
    else:  # line
        fig.add_trace(
            go.Scatter(
                x=charts_data.get("x_axis", []),
                y=charts_data.get("y_axis", []),
                mode="lines+markers",
                line=dict(color="#FF8C00", width=3),
                marker=dict(size=8, color="#FFCC00"),
                name="Progress",
            )
        )

    fig.update_layout(
        title=title,
        template="plotly_dark",
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        margin=dict(l=40, r=40, t=40, b=40),
        height=320,
    )

    st.plotly_chart(fig, use_container_width=True)


def render_tasks_manager(tasks: list):
    """Render the interactive task list and new task input form."""
    st.subheader("📋 Tasks Checklist")

    # Add task form
    with st.form("new_task_form", clear_on_submit=True):
        new_title = st.text_input("Add New Task", placeholder="Enter task title...")
        if st.form_submit_button("Add Task", type="primary"):
            if new_title.strip():
                try:
                    APIClient.create_dashboard_task(new_title.strip())
                    st.success(f"Task '{new_title}' added successfully!")
                    st.rerun()
                except Exception as e:
                    st.error(str(e))

    # List active tasks
    if not tasks:
        st.info("No active tasks found.")
        return

    for task in tasks:
        # Checkbox key must be unique
        cb_key = f"task_cb_{task['id']}"
        is_completed = st.checkbox(
            task["title"],
            value=task["is_completed"],
            key=cb_key,
        )
        # If checked state differs from DB, update
        if is_completed != task["is_completed"]:
            try:
                # Backend handles logging activity
                APIClient.update_dashboard_task(task["id"], is_completed)
                st.rerun()
            except Exception as e:
                st.error(str(e))

        # Show due date if exists
        if task.get("due_date"):
            try:
                due = datetime.fromisoformat(task["due_date"].replace("Z", ""))
                st.markdown(
                    f"<small style='color: grey; margin-left: 28px;'>Due: {due.strftime('%Y-%m-%d')}</small>",
                    unsafe_allow_html=True,
                )
            except Exception:
                pass


def render_notifications_list(notifications: list):
    """Render a timeline panel of recent alerts and notices."""
    st.subheader("🔔 Alerts & Notifications")
    if not notifications:
        st.info("No recent alerts.")
        return

    for n in notifications:
        # Determine styling
        style_cls = "custom-alert-success" if "Welcome" in n["title"] else "custom-alert-error"
        st.markdown(
            f"""
            <div class="custom-alert {style_cls}">
                <b>{n['title']}</b><br/>
                <small>{n['message']}</small>
            </div>
            """,
            unsafe_allow_html=True,
        )


def render_activities_timeline(activities: list):
    """Render logs of recent activity."""
    st.subheader("🕒 Activity Feed")
    if not activities:
        st.write("<small style='color: grey;'>No recent activity logs.</small>", unsafe_allow_html=True)
        return

    for act in activities:
        try:
            ts = datetime.fromisoformat(act["timestamp"].replace("Z", ""))
            ts_str = ts.strftime("%H:%M:%S")
        except Exception:
            ts_str = "Recent"

        st.markdown(
            f"**[{ts_str}]** `{act['action_type']}`: {act['description']}"
        )


def render_chatbot_ui(role: str):
    """Render the contextual AI Chatbot companion helper."""
    st.subheader(f"💬 {role} Assistant Chat")

    # Store messages locally in session state
    chat_key = f"chat_history_{role}"
    if chat_key not in st.session_state:
        st.session_state[chat_key] = [
            {"role": "assistant", "content": f"Hello! I am your {role} AI helper. Ask me anything!"}
        ]

    # Input message
    user_input = st.text_input("Ask a question:", key=f"chat_input_{role}", placeholder="Type here...")

    if st.button("Send Message", key=f"chat_send_{role}"):
        if user_input.strip():
            # Append user message
            st.session_state[chat_key].append({"role": "user", "content": user_input.strip()})
            # Call backend API
            try:
                res = APIClient.send_dashboard_chat(user_input.strip())
                st.session_state[chat_key].append({"role": "assistant", "content": res["response"]})
            except Exception as e:
                st.session_state[chat_key].append({"role": "assistant", "content": f"Error: {str(e)}"})
            st.rerun()

    # Display message history
    for msg in reversed(st.session_state[chat_key]):
        role_label = "**Assistant**" if msg["role"] == "assistant" else "**You**"
        color = "#FF8C00" if msg["role"] == "assistant" else "grey"
        st.markdown(
            f"<div style='border-left: 3px solid {color}; padding-left: 10px; margin-bottom: 10px;'>"
            f"{role_label}: {msg['content']}</div>",
            unsafe_allow_html=True,
        )


def render_profile_tab(user_profile: dict):
    """Render standard Profile overview tab."""
    st.subheader("👤 User Profile Profile")
    if not user_profile:
        st.warning("Profile information unavailable.")
        return

    st.markdown(
        f"""
        - **First Name:** {user_profile.get('first_name', 'N/A')}
        - **Last Name:** {user_profile.get('last_name', 'N/A')}
        - **Email Address:** {user_profile.get('email', 'N/A')}
        - **System Role:** {user_profile.get('role', 'N/A')}
        - **Account Status:** Active
        - **Verified User:** {'Yes' if user_profile.get('is_verified') else 'No'}
        """
    )


def render_calendar_view(events: list):
    """Render simple calendar timeline events."""
    st.subheader("📅 Workspace Calendar")
    if not events:
        st.info("No events scheduled for this week.")
        return

    for event in events:
        st.markdown(
            f"""
            <div style='background-color: rgba(255, 140, 0, 0.08); border: 1px solid rgba(255, 140, 0, 0.2); border-radius: 8px; padding: 12px; margin-bottom: 10px;'>
                <b>{event['title']}</b><br/>
                <small>Starts: {event['start']} | Ends: {event['end']}</small>
            </div>
            """,
            unsafe_allow_html=True,
        )


# ---------------------------------------------------------------------------
# Individual Dashboard Layout Renderers
# ---------------------------------------------------------------------------
def render_admin_dashboard(data: dict):
    render_metrics_cards(data["metrics"])

    col_charts, col_tasks = st.columns([2, 1])
    with col_charts:
        render_plotly_chart(data["charts_data"])

        # Quick Actions
        st.subheader("🛠️ Administrative Quick Actions")
        act_col1, act_col2 = st.columns(2)
        with act_col1:
            if st.button("Trigger Database Backup Check"):
                try:
                    APIClient.log_dashboard_activity("SYSTEM_BACKUP", "Initiated user database backup check.")
                    st.success("Backup test log registered.")
                    st.rerun()
                except Exception as e:
                    st.error(str(e))
        with act_col2:
            if st.button("Toggle System Maintenance Mode"):
                try:
                    APIClient.log_dashboard_activity("SYSTEM_MAINTENANCE", "Toggled system maintenance flag.")
                    st.warning("Maintenance activity logged.")
                    st.rerun()
                except Exception as e:
                    st.error(str(e))
    with col_tasks:
        render_tasks_manager(data["tasks"])


def render_engineer_dashboard(data: dict):
    render_metrics_cards(data["metrics"])

    col_charts, col_tasks = st.columns([2, 1])
    with col_charts:
        render_plotly_chart(data["charts_data"])

        # Quick Actions
        st.subheader("📝 Engineer Operations")
        with st.form("concrete_strength_form"):
            strength = st.number_input("Log Concrete Strength (MPa)", min_value=10, max_value=150, value=95)
            if st.form_submit_button("Log Test", type="primary"):
                try:
                    APIClient.log_dashboard_activity("STRENGTH_TEST", f"Logged concrete core test value: {strength} MPa")
                    st.success(f"Core compressive test of {strength} MPa submitted.")
                    st.rerun()
                except Exception as e:
                    st.error(str(e))
    with col_tasks:
        render_tasks_manager(data["tasks"])


def render_pm_dashboard(data: dict):
    render_metrics_cards(data["metrics"])

    col_charts, col_tasks = st.columns([2, 1])
    with col_charts:
        render_plotly_chart(data["charts_data"])

        # Quick Actions
        st.subheader("📈 Project Manager Actions")
        with st.form("pm_rfi_form"):
            rfi_title = st.text_input("Request for Information (RFI) Subject")
            if st.form_submit_button("Submit RFI Request"):
                if rfi_title.strip():
                    try:
                        APIClient.log_dashboard_activity("RFI_SUBMIT", f"Created engineering RFI: '{rfi_title}'")
                        st.success(f"RFI request '{rfi_title}' dispatched.")
                        st.rerun()
                    except Exception as e:
                        st.error(str(e))
                else:
                    st.error("RFI Title is required.")
    with col_tasks:
        render_tasks_manager(data["tasks"])


def render_hr_dashboard(data: dict):
    render_metrics_cards(data["metrics"])

    col_charts, col_tasks = st.columns([2, 1])
    with col_charts:
        render_plotly_chart(data["charts_data"])

        # Quick Actions
        st.subheader("👥 HR Recruiting & Payroll Actions")
        with st.form("hr_job_form"):
            title = st.text_input("Open Job Requisition Title")
            if st.form_submit_button("Post Open Job"):
                if title.strip():
                    try:
                        APIClient.log_dashboard_activity("JOB_POST", f"Created job post requisition: '{title}'")
                        st.success(f"Job posting '{title}' published.")
                        st.rerun()
                    except Exception as e:
                        st.error(str(e))
                else:
                    st.error("Job title is required.")
    with col_tasks:
        render_tasks_manager(data["tasks"])


def render_contractor_dashboard(data: dict):
    render_metrics_cards(data["metrics"])

    col_charts, col_tasks = st.columns([2, 1])
    with col_charts:
        render_plotly_chart(data["charts_data"])

        # Quick Actions
        st.subheader("💵 Billings & Invoice Claims")
        with st.form("contractor_invoice_form"):
            amount = st.number_input("Invoice Claim Amount ($)", min_value=100, max_value=500000, value=25000)
            if st.form_submit_button("Submit Progress Claim"):
                try:
                    APIClient.log_dashboard_activity("BILLING_SUBMIT", f"Submitted invoice claim: ${amount:,.2f}")
                    st.success(f"Progress invoice for ${amount:,.2f} registered.")
                    st.rerun()
                except Exception as e:
                    st.error(str(e))
    with col_tasks:
        render_tasks_manager(data["tasks"])


def render_worker_dashboard(data: dict):
    render_metrics_cards(data["metrics"])

    col_charts, col_tasks = st.columns([2, 1])
    with col_charts:
        render_plotly_chart(data["charts_data"])

        # Quick Actions
        st.subheader("👷 Shift Actions")
        col_clk1, col_clk2 = st.columns(2)
        with col_clk1:
            if st.button("Clock In Shift", use_container_width=True):
                try:
                    APIClient.log_dashboard_activity("CLOCK_IN", "Clocked in for field shift.")
                    st.success("Clock-in recorded.")
                    st.rerun()
                except Exception as e:
                    st.error(str(e))
        with col_clk2:
            if st.button("Clock Out Shift", use_container_width=True):
                try:
                    APIClient.log_dashboard_activity("CLOCK_OUT", "Clocked out of active shift.")
                    st.info("Clock-out recorded.")
                    st.rerun()
                except Exception as e:
                    st.error(str(e))
    with col_tasks:
        render_tasks_manager(data["tasks"])


def render_client_dashboard(data: dict):
    render_metrics_cards(data["metrics"])

    col_charts, col_tasks = st.columns([2, 1])
    with col_charts:
        render_plotly_chart(data["charts_data"])

        # Quick Actions
        st.subheader("💳 Client Payment Submission")
        with st.form("client_payment_form"):
            ref = st.text_input("Wire Reference / Receipt #")
            if st.form_submit_button("Submit Payment Advice", type="primary"):
                if ref.strip():
                    try:
                        APIClient.log_dashboard_activity("PAYMENT_ADVICE", f"Client logged wire transaction: Ref {ref}")
                        st.success("Receipt transaction recorded for approval.")
                        st.rerun()
                    except Exception as e:
                        st.error(str(e))
                else:
                    st.error("Reference is required.")
    with col_tasks:
        render_tasks_manager(data["tasks"])


def render_supplier_dashboard(data: dict):
    render_metrics_cards(data["metrics"])

    col_charts, col_tasks = st.columns([2, 1])
    with col_charts:
        render_plotly_chart(data["charts_data"])

        # Quick Actions
        st.subheader("📦 Inventory Update")
        with st.form("supplier_inv_form"):
            item = st.selectbox("Material Stock Item", ["Cement", "Steel Rebar", "Bricks", "Gravel", "Timber"])
            qty = st.number_input("Add Inventory Quantity", min_value=1, max_value=5000, value=100)
            if st.form_submit_button("Refill Material"):
                try:
                    APIClient.log_dashboard_activity("STOCK_ADD", f"Restocked {qty} units of {item}.")
                    st.success(f"{qty} units of {item} logged in inventory.")
                    st.rerun()
                except Exception as e:
                    st.error(str(e))
    with col_tasks:
        render_tasks_manager(data["tasks"])


def render_safety_dashboard(data: dict):
    render_metrics_cards(data["metrics"])

    col_charts, col_tasks = st.columns([2, 1])
    with col_charts:
        render_plotly_chart(data["charts_data"])

        # Quick Actions
        st.subheader("⚠️ Hazard Incident Log")
        with st.form("safety_hazard_form"):
            hazard = st.text_input("Describe Safety Hazard (e.g. Scaffolding loose)")
            severity = st.selectbox("Severity Classification", ["Low Warning", "Medium Risk", "High Critical"])
            if st.form_submit_button("File Hazard Report", type="primary"):
                if hazard.strip():
                    try:
                        APIClient.log_dashboard_activity("HAZARD_LOG", f"Reported {severity}: '{hazard}'")
                        st.success("Hazard incident registered for corrective check.")
                        st.rerun()
                    except Exception as e:
                        st.error(str(e))
                else:
                    st.error("Hazard description is required.")
    with col_tasks:
        render_tasks_manager(data["tasks"])


def render_supervisor_dashboard(data: dict):
    render_metrics_cards(data["metrics"])

    col_charts, col_tasks = st.columns([2, 1])
    with col_charts:
        render_plotly_chart(data["charts_data"])

        # Quick Actions
        st.subheader("📋 Supervisor Daily Site Checklist")
        with st.form("supervisor_log_form"):
            progress = st.text_input("Daily progress updates summary")
            machinery = st.checkbox("Heavy Cranes & Machinery checked & verified")
            if st.form_submit_button("Commit Daily Log"):
                try:
                    APIClient.log_dashboard_activity("DAILY_LOG", f"Log: '{progress}' | Machinery checked: {machinery}")
                    st.success("Daily progress logs locked in.")
                    st.rerun()
                except Exception as e:
                    st.error(str(e))
    with col_tasks:
        render_tasks_manager(data["tasks"])


def render_volunteer_dashboard(data: dict):
    render_metrics_cards(data["metrics"])

    col_charts, col_tasks = st.columns([2, 1])
    with col_charts:
        render_plotly_chart(data["charts_data"])

        # Quick Actions
        st.subheader("🤝 Community Signups")
        with st.form("volunteer_hour_form"):
            v_name = st.text_input("Volunteer Candidate Name")
            hours = st.number_input("Log Volunteer hours worked", min_value=1.0, max_value=12.0, value=4.0)
            if st.form_submit_button("Record Service Hours"):
                if v_name.strip():
                    try:
                        APIClient.log_dashboard_activity("VOL_HOURS", f"Logged {hours} volunteer hours for '{v_name}'")
                        st.success(f"{hours} service hours saved for {v_name}.")
                        st.rerun()
                    except Exception as e:
                        st.error(str(e))
                else:
                    st.error("Volunteer name is required.")
    with col_tasks:
        render_tasks_manager(data["tasks"])


# ---------------------------------------------------------------------------
# Routing Function: Renders Dashboard based on role
# ---------------------------------------------------------------------------
def render_dashboard(stats_data: dict, user_profile: dict):
    """
    Renders dashboard tabs (Overview, Schedule, Feed, Assistant, Profile)
    containing role-specific widget pages.
    """
    role = stats_data["charts_data"]["title"].split("for ")[-1] if "for " in stats_data["charts_data"].get("title", "") else user_profile.get("role", "Project Manager")

    tab1, tab2, tab3, tab4, tab5 = st.tabs(
        ["📊 Overview Workspace", "📅 Calendar Schedule", "🕒 Recent Feed", "💬 AI Assistant", "👤 Account Profile"]
    )

    with tab1:
        # Dispatch to role-specific layouts
        renderers = {
            "Admin": render_admin_dashboard,
            "Engineer": render_engineer_dashboard,
            "Contractor": render_contractor_dashboard,
            "Worker": render_worker_dashboard,
            "HR": render_hr_dashboard,
            "Client": render_client_dashboard,
            "Supplier": render_supplier_dashboard,
            "Safety Officer": render_safety_dashboard,
            "Site Supervisor": render_supervisor_dashboard,
            "Volunteer": render_volunteer_dashboard,
        }

        render_func = renderers.get(role, render_pm_dashboard)
        render_func(stats_data)

    with tab2:
        # Standard Calendar & Notifications split
        c_left, c_right = st.columns([2, 1])
        with c_left:
            render_calendar_view(stats_data.get("calendar_events", []))
        with c_right:
            render_notifications_list(stats_data.get("notifications", []))

    with tab3:
        # Recent Activity Feed logs & system notifications
        c_left, c_right = st.columns([2, 1])
        with c_left:
            render_activities_timeline(stats_data.get("activities", []))
        with c_right:
            st.subheader("📥 Download Center")
            st.button("Export Dashboard stats (CSV)", use_container_width=True)
            st.button("Generate Monthly report (PDF)", use_container_width=True)

    with tab4:
        # Contextual chat helper
        render_chatbot_ui(role)

    with tab5:
        # Profile view
        render_profile_tab(user_profile)
