"""
frontend/pages/energy_monitoring.py
-----------------------------------
Standalone page for Real-Time Energy & Power Consumption Monitoring (Feature 15).
"""
import pandas as pd
import streamlit as st
import plotly.express as px
from frontend.utils.api_client import APIClient


def show_energy_monitoring_page():
    st.markdown(
        '# <span class="gradient-text">⚡ Smart Construction Energy & Power Monitoring</span>',
        unsafe_allow_html=True,
    )
    st.markdown(
        '<p class="subtitle-text">IoT Electrical Grid Auditor. Track live power draw (kW), line voltage, power factor efficiency, and cumulative kWh usage across key site areas.</p>',
        unsafe_allow_html=True,
    )

    # 1. Sidebar Control
    st.sidebar.markdown("### 🎛️ Grid Load Simulator")
    stress_intensity = st.sidebar.slider("Grid Electrical Load Stress", 0.0, 1.0, 0.0, step=0.1)
    
    col_mock, col_reset = st.sidebar.columns(2)
    with col_mock:
        btn_mock = st.button("⚡ Mock Power", use_container_width=True, type="primary")
    with col_reset:
        btn_reset = st.button("🔄 Reset Logs", use_container_width=True)

    # Handle simulation and reset
    try:
        if btn_mock:
            with st.spinner("Calculating active power draws and auditing thresholds..."):
                APIClient.simulate_energy_flow(stress_intensity)
                st.success("Smart meter telemetry updated.")
        elif btn_reset:
            with st.spinner("Clearing electrical logs and safety limits..."):
                APIClient.reset_energy_data()
                st.success("Energy configurations and logs reset.")
    except Exception as e:
        st.error(f"Electrical monitoring system error: {str(e)}")

    # Fetch data
    logs = []
    configs = []
    try:
        logs = APIClient.get_energy_logs()
        configs = APIClient.get_energy_configs()
    except Exception as e:
        st.error(f"Failed to fetch energy monitoring records: {str(e)}")

    if configs:
        # 2. KPI metrics cards
        avg_pf = sum(l["power_factor"] for l in logs) / len(logs) if logs else 0.90
        
        # Calculate total energy consumed (sum of latest cumulative kWh across all unique smart meters)
        latest_cumulatives = {}
        for l in logs:
            if l["sensor_name"] not in latest_cumulatives:
                latest_cumulatives[l["sensor_name"]] = l["cumulative_kwh"]
        total_used = sum(latest_cumulatives.values())

        anomalies_count = sum(1 for l in logs if l["is_anomaly"])

        col_metric1, col_metric2, col_metric3 = st.columns(3)
        with col_metric1:
            st.metric("Grid Avg Power Factor", f"{round(avg_pf, 2)}", delta="Optimal" if avg_pf >= 0.85 else "Low Efficiency", delta_color="normal" if avg_pf >= 0.85 else "inverse")
        with col_metric2:
            st.metric("Total Consumption", f"{round(total_used, 1)} kWh")
        with col_metric3:
            st.metric("Active Power Anomalies", f"{anomalies_count} warnings", delta="Overload Danger" if anomalies_count > 0 else "Balanced Grid", delta_color="inverse" if anomalies_count > 0 else "normal")

        # 3. Plots
        st.markdown("### 📊 Smart Meter Power Draw & Cumulative Usage Timelines")
        col_pow_plot, col_usage_plot = st.columns(2)

        with col_pow_plot:
            st.markdown("##### Active Power Draw (kW) over Time")
            if logs:
                pow_list = []
                for l in reversed(logs):
                    pow_list.append({
                        "Timestamp": pd.to_datetime(l["logged_at"]),
                        "Power Draw (kW)": l["power_usage"],
                        "Meter Location": l["sensor_name"]
                    })
                
                pow_df = pd.DataFrame(pow_list)
                fig_pow = px.line(
                    pow_df,
                    x="Timestamp",
                    y="Power Draw (kW)",
                    color="Meter Location",
                    color_discrete_sequence=px.colors.qualitative.Dark24
                )
                fig_pow.update_layout(height=260, margin=dict(l=10, r=10, t=10, b=10))
                st.plotly_chart(fig_pow, use_container_width=True)
            else:
                st.info("No logs. Power draw charts will populate once mock telemetry is run.")

        with col_usage_plot:
            st.markdown("##### Cumulative Consumption (kWh) over Time")
            if logs:
                usage_list = []
                for l in reversed(logs):
                    usage_list.append({
                        "Timestamp": pd.to_datetime(l["logged_at"]),
                        "Cumulative (kWh)": l["cumulative_kwh"],
                        "Meter Location": l["sensor_name"]
                    })
                
                usage_df = pd.DataFrame(usage_list)
                fig_usage = px.line(
                    usage_df,
                    x="Timestamp",
                    y="Cumulative (kWh)",
                    color="Meter Location",
                    color_discrete_sequence=px.colors.qualitative.Pastel
                )
                fig_usage.update_layout(height=260, margin=dict(l=10, r=10, t=10, b=10))
                st.plotly_chart(fig_usage, use_container_width=True)
            else:
                st.info("No logs. Cumulative consumption trends will populate once mock telemetry is run.")

        # 4. Action forms columns
        st.markdown("---")
        col_log_form, col_config_form = st.columns(2)

        # 4a. Manual log form
        with col_log_form:
            st.markdown("### 📝 Log Manual Telemetry")
            with st.form("manual_energy_form", clear_on_submit=True):
                sensor_c = st.selectbox("Smart Meter:", ["Heavy Tower Cranes", "Concrete Batch Plant", "High-Intensity Site Lighting", "Main Site Offices"])
                pow_val = st.number_input("Power Draw (kW):", min_value=0.0, value=35.0, step=5.0)
                volt_val = st.number_input("Line Voltage (V):", min_value=0.0, value=230.0, step=5.0)
                curr_val = st.number_input("Current Draw (A):", min_value=0.0, value=15.0, step=1.0)
                pf_val = st.slider("Power Factor (0.0 - 1.0):", min_value=0.5, max_value=1.0, value=0.90, step=0.01)
                
                # Suggested cumulative kwh
                last_sensor_log = next((l for l in logs if l["sensor_name"] == sensor_c), None)
                fallback_cumulative = last_sensor_log["cumulative_kwh"] if last_sensor_log else 500.0
                
                cumulative_val = st.number_input("Cumulative Consumption (kWh):", min_value=0.0, value=float(fallback_cumulative), step=50.0)
                btn_log_submit = st.form_submit_button("Submit Energy Reading", type="primary")

            if btn_log_submit:
                try:
                    APIClient.log_energy_reading(sensor_c, pow_val, volt_val, curr_val, pf_val, cumulative_val)
                    st.success(f"Energy reading logged for '{sensor_c}'.")
                    st.rerun()
                except Exception as e:
                    st.error(str(e))

        # 4b. Config safety thresholds rules form
        with col_config_form:
            st.markdown("### ⚙️ Calibrate Safety Thresholds")
            with st.form("energy_config_form", clear_on_submit=True):
                sensor_r = st.selectbox("Sensor Target Meter:", ["Heavy Tower Cranes", "Concrete Batch Plant", "High-Intensity Site Lighting", "Main Site Offices"])
                max_pow_lim = st.slider("Max Power Limit (kW):", 20, 500, 150, step=10)
                min_volt_lim = st.slider("Min Voltage Limit (V):", 180, 240, 210, step=5)
                min_pf_lim = st.slider("Min Power Factor:", 0.60, 0.95, 0.85, step=0.01)
                btn_config_submit = st.form_submit_button("Update Safety Guidelines", type="primary")

            if btn_config_submit:
                try:
                    APIClient.update_energy_config(sensor_r, float(max_pow_lim), float(min_volt_lim), float(min_pf_lim))
                    st.success(f"Water safety boundaries updated for '{sensor_r}'.")
                    st.rerun()
                except Exception as e:
                    st.error(str(e))

        # 5. Config thresholds listing
        st.markdown("---")
        st.markdown("### 📋 Calibrated Energy Safety Guidelines")
        config_data = []
        for c in configs:
            config_data.append({
                "Meter Location": c["sensor_name"],
                "Max Power": f"{c['max_power_limit']} kW",
                "Min Voltage": f"{c['min_voltage_limit']} V",
                "Min Power Factor Limit": f"{c['min_power_factor_limit']}",
                "Last Calibrated": pd.to_datetime(c["updated_at"]).strftime("%Y-%m-%d %H:%M")
            })
        st.table(pd.DataFrame(config_data))

        # 6. Detailed Logs Table
        st.markdown("### 📋 Detailed Environmental Energy Audit Logs")
        if logs:
            log_data = []
            for l in logs[:15]:  # Display recent 15 logs
                state_lbl = "🚨 GRID OVERLOAD ANOMALY" if l["is_anomaly"] else "🟢 Balanced Grid"
                log_data.append({
                    "Timestamp": pd.to_datetime(l["logged_at"]).strftime("%Y-%m-%d %H:%M:%S"),
                    "Smart Meter": l["sensor_name"],
                    "Power Draw": f"{l['power_usage']} kW",
                    "Voltage": f"{l['voltage']} V",
                    "Current": f"{l['current']} A",
                    "Power Factor": f"{l['power_factor']}",
                    "Cumulative": f"{l['cumulative_kwh']} kWh",
                    "Audit Result": state_lbl,
                    "Anomaly Type": l["anomaly_type"]
                })
            st.table(pd.DataFrame(log_data))
st.write("")
st.write("")
