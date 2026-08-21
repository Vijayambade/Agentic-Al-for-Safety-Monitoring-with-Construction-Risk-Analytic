"""
frontend/pages/schedule_predictor.py
-----------------------------------
Standalone page for Construction Scheduling & Delay Predictor (Feature 7).
"""
import pandas as pd
import streamlit as st
import plotly.express as px
from frontend.utils.api_client import APIClient


def show_schedule_predictor_page():
    st.markdown(
        '# <span class="gradient-text">📅 AI Scheduling & Delay Predictor</span>',
        unsafe_allow_html=True,
    )
    st.markdown(
        '<p class="subtitle-text">Analyzes project dependencies using the Critical Path Method (CPM). Adjust risk variables to predict timeline overruns and automatically reschedule successors.</p>',
        unsafe_allow_html=True,
    )

    # 1. Sidebar Risk Settings
    st.sidebar.markdown("### 🎛️ Simulator Parameters")
    weather_risk = st.sidebar.slider("Weather Risk Factor (Rain/Temp)", 0.0, 1.0, 0.0, step=0.05)
    labor_risk = st.sidebar.slider("Labor Shortage / Resource Risk", 0.0, 1.0, 0.0, step=0.05)

    col_sim_btn, col_reset_btn = st.sidebar.columns(2)
    with col_sim_btn:
        btn_predict = st.button("🔮 Predict Delays", use_container_width=True, type="primary")
    with col_reset_btn:
        btn_reset = st.button("🔄 Reset Baseline", use_container_width=True)

    # Handle action submissions
    tasks = []
    try:
        if btn_predict:
            with st.spinner("Calculating delay offsets and running forward/backward CPM passes..."):
                tasks = APIClient.predict_schedule_delays(weather_risk, labor_risk)
                st.success("Rescheduled timeline compiled successfully!")
        elif btn_reset:
            with st.spinner("Reverting to baseline project definitions..."):
                tasks = APIClient.reset_schedule_tasks()
                st.success("Baseline schedule restored.")
        else:
            tasks = APIClient.get_schedule_tasks()
    except Exception as e:
        st.error(f"Scheduling engine error: {str(e)}")

    if tasks:
        # Sort tasks by ID for tabular neatness
        tasks = sorted(tasks, key=lambda x: x["id"])

        # 2. Main KPI Metrics
        total_delay = sum(t["predicted_delay"] for t in tasks)
        critical_tasks = sum(1 for t in tasks if t["is_critical"])
        
        # Latest finish date is the project finish date
        finish_dates = [pd.to_datetime(t["end_date"]) for t in tasks]
        proj_finish = max(finish_dates).strftime("%b %d, %Y") if finish_dates else "N/A"

        col_metric1, col_metric2, col_metric3 = st.columns(3)
        with col_metric1:
            st.metric("Estimated Project Finish", proj_finish)
        with col_metric2:
            st.metric("Total Cumulative Delay", f"{total_delay} days", delta=f"+{total_delay} days" if total_delay > 0 else "0", delta_color="inverse")
        with col_metric3:
            st.metric("Critical Path Tasks", f"{critical_tasks} tasks", delta="Risk Warning" if critical_tasks > 3 else "Normal", delta_color="off" if critical_tasks <= 3 else "inverse")

        # 3. Gantt Chart visualization
        st.markdown("### 📊 Interactive Project Gantt Timeline")
        
        # Prepare DataFrame for Plotly timeline
        df_list = []
        for t in tasks:
            # Map Critical Path status for color coding
            color_label = "🔴 Critical Path" if t["is_critical"] else "🔵 Normal Schedule"
            
            df_list.append({
                "Task": f"({t['id']}) {t['name']}",
                "Start": pd.to_datetime(t["start_date"]),
                "Finish": pd.to_datetime(t["end_date"]),
                "Critical Status": color_label,
                "Duration": f"{t['duration']}d (+{t['predicted_delay']}d delay)",
                "Progress": f"{int(t['progress'])}%"
            })
            
        df = pd.DataFrame(df_list)
        
        # Build plotly timeline
        fig = px.timeline(
            df,
            x_start="Start",
            x_end="Finish",
            y="Task",
            color="Critical Status",
            color_discrete_map={
                "🔴 Critical Path": "#EF4444",      # Danger Red
                "🔵 Normal Schedule": "#3B82F6"      # Soft Blue
            },
            hover_data=["Duration", "Progress"]
        )
        # Reverse y-axis to draw task 1 on top
        fig.update_yaxes(autorange="reversed")
        fig.update_layout(
            height=300,
            margin=dict(l=20, r=20, t=10, b=10),
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
        )
        
        st.plotly_chart(fig, use_container_width=True)

        # 4. Detailed Calculations Table
        st.markdown("### 📋 Detailed Critical Path calculations (CPM)")
        
        table_data = []
        for t in tasks:
            # Parse Float Slack days from risk factors string
            slack_str = "0 days"
            if "Slack Float:" in t["risk_factors"]:
                try:
                    slack_str = t["risk_factors"].split("Slack Float:")[1].split("days")[0].strip() + " days"
                except Exception:
                    pass
            
            start_fmt = pd.to_datetime(t["start_date"]).strftime("%Y-%m-%d")
            end_fmt = pd.to_datetime(t["end_date"]).strftime("%Y-%m-%d")

            table_data.append({
                "ID": t["id"],
                "Task Description": t["name"],
                "Start Date": start_fmt,
                "End Date": end_fmt,
                "Baseline Days": t["duration"],
                "Delay Days": t["predicted_delay"],
                "Slack (Float)": slack_str,
                "Path Status": "🚨 Critical" if t["is_critical"] else "Slack Normal",
                "Predecessors": t["dependencies"] if t["dependencies"] else "None"
            })
            
        st.table(pd.DataFrame(table_data))
