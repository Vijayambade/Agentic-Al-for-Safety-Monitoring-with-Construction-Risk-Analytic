"""
frontend/pages/water_monitoring.py
----------------------------------
Standalone page for Real-Time Water Flow & Leakage Monitoring (Feature 13).
"""
import pandas as pd
import streamlit as st
import plotly.express as px
from frontend.utils.api_client import APIClient


def show_water_monitoring_page():
    st.markdown(
        '# <span class="gradient-text">💧 IoT Site Water Flow & Leakage Monitoring</span>',
        unsafe_allow_html=True,
    )
    st.markdown(
        '<p class="subtitle-text">IoT Water Resource Manager. Track flow rates, pipeline pressure, and identify leak anomalies or pressure drops across the site.</p>',
        unsafe_allow_html=True,
    )

    # 1. Sidebar Control
    st.sidebar.markdown("### 🎛️ Water Leak Simulator")
    stress_intensity = st.sidebar.slider("Leak Simulation Stress (Pressure Drop)", 0.0, 1.0, 0.0, step=0.1)
    
    col_mock, col_reset = st.sidebar.columns(2)
    with col_mock:
        btn_mock = st.button("⚡ Mock Water", use_container_width=True, type="primary")
    with col_reset:
        btn_reset = st.button("🔄 Reset Logs", use_container_width=True)

    # Handle simulation and reset
    try:
        if btn_mock:
            with st.spinner("Acquiring water grid telemetry and auditing thresholds..."):
                APIClient.simulate_water_flow(stress_intensity)
                st.success("Water sensor grid data updated.")
        elif btn_reset:
            with st.spinner("Clearing water logs and restoring baseline limits..."):
                APIClient.reset_water_data()
                st.success("Water configurations and logs reset.")
    except Exception as e:
        st.error(f"Water monitoring system error: {str(e)}")

    # Fetch data
    logs = []
    configs = []
    try:
        logs = APIClient.get_water_logs()
        configs = APIClient.get_water_configs()
    except Exception as e:
        st.error(f"Failed to fetch water monitoring records: {str(e)}")

    if configs:
        # 2. KPI metrics cards
        avg_flow = sum(l["flow_rate"] for l in logs) / len(logs) if logs else 35.0
        
        # Calculate total water consumed (sum of latest cumulative liters across all unique sensors)
        latest_cumulatives = {}
        for l in logs:
            if l["sensor_name"] not in latest_cumulatives:
                latest_cumulatives[l["sensor_name"]] = l["cumulative_liters"]
        total_used = sum(latest_cumulatives.values())

        anomalies_count = sum(1 for l in logs if l["is_anomaly"])

        col_metric1, col_metric2, col_metric3 = st.columns(3)
        with col_metric1:
            st.metric("Grid Avg Flow Rate", f"{round(avg_flow, 1)} L/min")
        with col_metric2:
            st.metric("Total Water Consumed", f"{round(total_used, 1)} Liters")
        with col_metric3:
            st.metric("Active Anomaly Alarms", f"{anomalies_count} warnings", delta="Leak Hazard" if anomalies_count > 0 else "Normal Grid", delta_color="inverse" if anomalies_count > 0 else "normal")

        # 3. Plots
        st.markdown("### 📊 Pipeline Flow & Cumulative Consumption Timelines")
        col_flow_plot, col_usage_plot = st.columns(2)

        with col_flow_plot:
            st.markdown("##### Water Flow Rate (L/min) over Time")
            if logs:
                flow_list = []
                for l in reversed(logs):
                    flow_list.append({
                        "Timestamp": pd.to_datetime(l["logged_at"]),
                        "Flow Rate (L/min)": l["flow_rate"],
                        "Location": l["sensor_name"]
                    })
                
                flow_df = pd.DataFrame(flow_list)
                fig_flow = px.line(
                    flow_df,
                    x="Timestamp",
                    y="Flow Rate (L/min)",
                    color="Location",
                    color_discrete_sequence=px.colors.qualitative.Prism
                )
                fig_flow.update_layout(height=260, margin=dict(l=10, r=10, t=10, b=10))
                st.plotly_chart(fig_flow, use_container_width=True)
            else:
                st.info("No logs. Flow rate charts will populate once mock feeds are run.")

        with col_usage_plot:
            st.markdown("##### Cumulative Consumption (Liters) over Time")
            if logs:
                usage_list = []
                for l in reversed(logs):
                    usage_list.append({
                        "Timestamp": pd.to_datetime(l["logged_at"]),
                        "Cumulative (Liters)": l["cumulative_liters"],
                        "Location": l["sensor_name"]
                    })
                
                usage_df = pd.DataFrame(usage_list)
                fig_usage = px.line(
                    usage_df,
                    x="Timestamp",
                    y="Cumulative (Liters)",
                    color="Location",
                    color_discrete_sequence=px.colors.qualitative.Vivid
                )
                fig_usage.update_layout(height=260, margin=dict(l=10, r=10, t=10, b=10))
                st.plotly_chart(fig_usage, use_container_width=True)
            else:
                st.info("No logs. Cumulative usage trends will populate once mock feeds are run.")

        # 4. Action forms columns
        st.markdown("---")
        col_log_form, col_config_form = st.columns(2)

        # 4a. Manual log form
        with col_log_form:
            st.markdown("### 📝 Log Manual Reading")
            with st.form("manual_water_form", clear_on_submit=True):
                sensor_c = st.selectbox("Location Station:", ["Main Supply Inlet", "Concrete Mixing Bay", "Worker Quarters"])
                flow_val = st.number_input("Flow Rate (L/min):", min_value=0.0, value=35.0, step=5.0)
                pressure_val = st.number_input("Pressure (kPa):", min_value=0.0, value=220.0, step=10.0)
                
                # Determine fallback cumulative value to suggest
                last_sensor_log = next((l for l in logs if l["sensor_name"] == sensor_c), None)
                fallback_cumulative = last_sensor_log["cumulative_liters"] if last_sensor_log else 1000.0
                
                cumulative_val = st.number_input("Cumulative Consumption (Liters):", min_value=0.0, value=float(fallback_cumulative), step=50.0)
                btn_log_submit = st.form_submit_button("Submit Water Reading", type="primary")

            if btn_log_submit:
                try:
                    APIClient.log_water_reading(sensor_c, flow_val, pressure_val, cumulative_val)
                    st.success(f"Water reading logged for '{sensor_c}'.")
                    st.rerun()
                except Exception as e:
                    st.error(str(e))

        # 4b. Config daytime/nighttime rules form
        with col_config_form:
            st.markdown("### ⚙️ Calibrate Safety Guidelines")
            with st.form("water_config_form", clear_on_submit=True):
                sensor_r = st.selectbox("Sensor Station Target:", ["Main Supply Inlet", "Concrete Mixing Bay", "Worker Quarters"])
                max_flow_lim = st.slider("Max Flow Limit (L/min):", 20, 300, 100, step=5)
                min_pressure_lim = st.slider("Min Pressure Limit (kPa):", 50, 300, 150, step=10)
                btn_config_submit = st.form_submit_button("Update Safety Guidelines", type="primary")

            if btn_config_submit:
                try:
                    APIClient.update_water_config(sensor_r, float(max_flow_lim), float(min_pressure_lim))
                    st.success(f"Water safety parameters updated for '{sensor_r}'.")
                    st.rerun()
                except Exception as e:
                    st.error(str(e))

        # 5. Config thresholds listing
        st.markdown("---")
        st.markdown("### 📋 Calibrated Water Safety Guidelines")
        config_data = []
        for c in configs:
            config_data.append({
                "Location Station": c["sensor_name"],
                "Max Flow Limit": f"{c['max_flow_limit']} L/min",
                "Min Pressure Limit": f"{c['min_pressure_limit']} kPa",
                "Last Calibrated": pd.to_datetime(c["updated_at"]).strftime("%Y-%m-%d %H:%M")
            })
        st.table(pd.DataFrame(config_data))

        # 6. Detailed Logs Table
        st.markdown("### 📋 Detailed Environmental Water Audit Logs")
        if logs:
            log_data = []
            for l in logs[:15]:  # Display recent 15 logs
                state_lbl = "🚨 PIPELINE ANOMALY" if l["is_anomaly"] else "🟢 Safe Grid"
                log_data.append({
                    "Timestamp": pd.to_datetime(l["logged_at"]).strftime("%Y-%m-%d %H:%M:%S"),
                    "Location": l["sensor_name"],
                    "Flow Rate": f"{l['flow_rate']} L/min",
                    "Pressure": f"{l['pressure']} kPa",
                    "Cumulative": f"{l['cumulative_liters']} L",
                    "Audit Result": state_lbl,
                    "Issues Logged": l["anomaly_type"]
                })
            st.table(pd.DataFrame(log_data))
st.write("")
st.write("")
