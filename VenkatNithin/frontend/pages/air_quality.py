"""
frontend/pages/air_quality.py
----------------------------
Standalone page for Real-Time Air Quality & Gas Monitoring (Feature 12).
"""
import pandas as pd
import streamlit as st
import plotly.express as px
from datetime import datetime
from frontend.utils.api_client import APIClient


def show_air_quality_page():
    st.markdown(
        '# <span class="gradient-text">💨 Air Quality & Hazardous Gas Monitoring</span>',
        unsafe_allow_html=True,
    )
    st.markdown(
        '<p class="subtitle-text">IoT Environmental Safety Portal. Monitor particulate matter (PM2.5, PM10) and hazardous gas concentrations (CO, NO2, VOCs) across site zones.</p>',
        unsafe_allow_html=True,
    )

    # 1. Sidebar Control
    st.sidebar.markdown("### 🎛️ Gas Leak Simulator")
    stress_intensity = st.sidebar.slider("Ambient Air Stress (Spike Gas/Dust)", 0.0, 1.0, 0.0, step=0.1)
    
    col_mock, col_reset = st.sidebar.columns(2)
    with col_mock:
        btn_mock = st.button("⚡ Mock Air Feeds", use_container_width=True, type="primary")
    with col_reset:
        btn_reset = st.button("🔄 Reset Air Logs", use_container_width=True)

    # Handle simulation and reset
    try:
        if btn_mock:
            with st.spinner("Acquiring sensor telematics and checking safety thresholds..."):
                APIClient.simulate_air_quality(stress_intensity)
                st.success("Air sensor readouts compiled.")
        elif btn_reset:
            with st.spinner("Clearing historical sensor logs and restoring baseline limits..."):
                APIClient.reset_air_quality_data()
                st.success("Air configs and logs reset.")
    except Exception as e:
        st.error(f"Environmental monitoring system error: {str(e)}")

    # Fetch data
    logs = []
    configs = []
    try:
        logs = APIClient.get_air_quality_logs()
        configs = APIClient.get_air_quality_configs()
    except Exception as e:
        st.error(f"Failed to fetch environmental records: {str(e)}")

    if configs:
        # 2. KPI metrics cards
        avg_aqi = sum(l["aqi"] for l in logs) / len(logs) if logs else 45.0
        max_pm25 = max((l["pm25"] for l in logs), default=12.0)
        hazards_count = sum(1 for l in logs if l["is_hazardous"])

        col_metric1, col_metric2, col_metric3 = st.columns(3)
        with col_metric1:
            st.metric("Fleet Average AQI", f"{round(avg_aqi, 1)}", delta="Unhealthy" if avg_aqi > 150 else "Moderate" if avg_aqi > 100 else "Good", delta_color="normal" if avg_aqi <= 100 else "inverse")
        with col_metric2:
            st.metric("Peak PM2.5 Level", f"{round(max_pm25, 1)} ug/m3")
        with col_metric3:
            st.metric("Active Gas Alerts", f"{hazards_count} warnings", delta="Hazard Alarm" if hazards_count > 0 else "All Clean", delta_color="inverse" if hazards_count > 0 else "normal")

        # 3. Plots
        st.markdown("### 📊 Air Quality & Gas Concentration Timelines")
        col_line, col_bar = st.columns(2)

        with col_line:
            st.markdown("##### PM2.5 Particulate Trends over Time")
            if logs:
                line_list = []
                for l in reversed(logs):
                    line_list.append({
                        "Timestamp": pd.to_datetime(l["logged_at"]),
                        "PM2.5 (ug/m3)": l["pm25"],
                        "Sensor Station": l["sensor_name"],
                        "PM2.5 Limit": l["limit_threshold"] if "limit_threshold" in l else 50.0
                    })
                
                line_df = pd.DataFrame(line_list)
                fig_line = px.line(
                    line_df,
                    x="Timestamp",
                    y="PM2.5 (ug/m3)",
                    color="Sensor Station",
                    color_discrete_sequence=px.colors.qualitative.Safe
                )
                fig_line.update_layout(height=260, margin=dict(l=10, r=10, t=10, b=10))
                st.plotly_chart(fig_line, use_container_width=True)
            else:
                st.info("No logs. PM2.5 trends will display once mock feeds are run.")

        with col_bar:
            st.markdown("##### Gas Concentrations (CO, NO2, VOCs)")
            if logs:
                # Group by sensor to get the latest gas concentration
                latest_logs = {}
                for l in logs:
                    if l["sensor_name"] not in latest_logs:
                        latest_logs[l["sensor_name"]] = l
                
                bar_list = []
                for name, log_obj in latest_logs.items():
                    bar_list.append({"Station": name, "Gas": "CO (ppm)", "Concentration": log_obj["co_level"]})
                    bar_list.append({"Station": name, "Gas": "NO2 (ppm)", "Concentration": log_obj["no2_level"] * 10.0})  # Scaled for visualization
                    bar_list.append({"Station": name, "Gas": "VOC (ppm)", "Concentration": log_obj["voc_level"]})
                
                bar_df = pd.DataFrame(bar_list)
                fig_bar = px.bar(
                    bar_df,
                    x="Station",
                    y="Concentration",
                    color="Gas",
                    barmode="group",
                    color_discrete_sequence=px.colors.qualitative.Bold
                )
                fig_bar.update_layout(height=260, margin=dict(l=10, r=10, t=10, b=10))
                st.plotly_chart(fig_bar, use_container_width=True)
            else:
                st.info("No logs. Gas concentrations will populate once feeds are run.")

        # 4. Action forms columns
        st.markdown("---")
        col_log_form, col_config_form = st.columns(2)

        # 4a. Manual log form
        with col_log_form:
            st.markdown("### 📝 Log Manual Reading")
            with st.form("manual_air_form", clear_on_submit=True):
                sensor_c = st.selectbox("Sensor Station:", ["Excavation Tunnel A", "Framing & Welding Zone B", "Site Perimeter Zone C"])
                col_aqi, col_pm = st.columns(2)
                with col_aqi:
                    aqi_val = st.number_input("AQI Index:", min_value=0.0, max_value=500.0, value=50.0, step=5.0)
                    pm10_val = st.number_input("PM10 (ug/m3):", min_value=0.0, value=30.0, step=5.0)
                with col_pm:
                    pm25_val = st.number_input("PM2.5 (ug/m3):", min_value=0.0, value=15.0, step=5.0)
                    co_val = st.number_input("CO Gas (ppm):", min_value=0.0, value=2.0, step=0.5)
                
                col_no2, col_voc = st.columns(2)
                with col_no2:
                    no2_val = st.number_input("NO2 Gas (ppm):", min_value=0.0, value=0.1, step=0.05)
                with col_voc:
                    voc_val = st.number_input("VOC level (ppm):", min_value=0.0, value=1.0, step=0.5)
                
                btn_log_submit = st.form_submit_button("Submit Air Quality Reading", type="primary")

            if btn_log_submit:
                try:
                    APIClient.log_air_quality(sensor_c, aqi_val, pm25_val, pm10_val, co_val, no2_val, voc_val)
                    st.success(f"Air reading logged for '{sensor_c}'.")
                    st.rerun()
                except Exception as e:
                    st.error(str(e))

        # 4b. Config daytime/nighttime rules form
        with col_config_form:
            st.markdown("### ⚙️ Calibrate Gas Threshold Limits")
            with st.form("air_config_form", clear_on_submit=True):
                sensor_r = st.selectbox("Sensor Station Target:", ["Excavation Tunnel A", "Framing & Welding Zone B", "Site Perimeter Zone C"])
                pm25_lim = st.slider("PM2.5 Safety Limit (ug/m3):", 10.0, 150.0, 50.0, step=5.0)
                co_lim = st.slider("CO Gas Safety Limit (ppm):", 10.0, 100.0, 35.0, step=5.0)
                voc_lim = st.slider("VOC Fumes Limit (ppm):", 5.0, 50.0, 10.0, step=1.0)
                btn_config_submit = st.form_submit_button("Update Safety Guidelines", type="primary")

            if btn_config_submit:
                try:
                    APIClient.update_air_quality_config(sensor_r, float(pm25_lim), float(co_lim), float(voc_lim))
                    st.success(f"Safety limits updated for '{sensor_r}'.")
                    st.rerun()
                except Exception as e:
                    st.error(str(e))

        # 5. Config thresholds listing
        st.markdown("---")
        st.markdown("### 📋 Calibrated Air Safety Guidelines")
        config_data = []
        for c in configs:
            config_data.append({
                "Station Zone": c["sensor_name"],
                "PM2.5 Limit": f"{c['pm25_limit']} ug/m3",
                "CO Gas Limit": f"{c['co_limit']} ppm",
                "VOC Fumes Limit": f"{c['voc_limit']} ppm",
                "Last Calibrated": pd.to_datetime(c["updated_at"]).strftime("%Y-%m-%d %H:%M")
            })
        st.table(pd.DataFrame(config_data))

        # 6. Detailed Logs Table
        st.markdown("### 📋 Detailed Environmental Audit Logs")
        if logs:
            log_data = []
            for l in logs[:15]:  # Display recent 15 logs
                state_lbl = "🚨 HAZARDOUS BREACH" if l["is_hazardous"] else "🟢 Safe"
                log_data.append({
                    "Timestamp": pd.to_datetime(l["logged_at"]).strftime("%Y-%m-%d %H:%M:%S"),
                    "Station": l["sensor_name"],
                    "AQI": int(l["aqi"]),
                    "PM2.5": f"{l['pm25']} ug/m3",
                    "CO Level": f"{l['co_level']} ppm",
                    "VOC Level": f"{l['voc_level']} ppm",
                    "Audit Result": state_lbl,
                    "Issues Logged": l["hazard_reason"]
                })
            st.table(pd.DataFrame(log_data))
st.write("")
st.write("")
