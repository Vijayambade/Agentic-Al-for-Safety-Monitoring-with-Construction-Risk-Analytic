"""
frontend/pages/noise_monitoring.py
----------------------------------
Standalone page for Real-Time Noise & Decibel Monitoring (Feature 11).
"""
import pandas as pd
import streamlit as st
import plotly.express as px
from datetime import datetime
from frontend.utils.api_client import APIClient


def show_noise_monitoring_page():
    st.markdown(
        '# <span class="gradient-text">🔊 Real-Time Noise & Decibel Monitoring</span>',
        unsafe_allow_html=True,
    )
    st.markdown(
        '<p class="subtitle-text">IoT Noise Decibel Monitor. Track zone environmental sound levels, calibrate day/night rules, and audit decibel breaches to prevent community noise pollution.</p>',
        unsafe_allow_html=True,
    )

    # 1. Sidebar Control
    st.sidebar.markdown("### 🎛️ Noise Simulator")
    stress_intensity = st.sidebar.slider("Ambient Sound Stress (dB Spike)", 0.0, 1.0, 0.0, step=0.1)
    
    col_mock, col_reset = st.sidebar.columns(2)
    with col_mock:
        btn_mock = st.button("⚡ Mock Feeds", use_container_width=True, type="primary")
    with col_reset:
        btn_reset = st.button("🔄 Reset Logs", use_container_width=True)

    # Handle mock and reset submissions
    try:
        if btn_mock:
            with st.spinner("Acquiring raw decibel readings and auditing limits..."):
                APIClient.simulate_noise_decibels(stress_intensity)
                st.success("Sensor readings captured.")
        elif btn_reset:
            with st.spinner("Clearing historical sensor logs and restoring rules..."):
                APIClient.reset_noise_data()
                st.success("Noise configurations and history cleared.")
    except Exception as e:
        st.error(f"Noise monitoring system error: {str(e)}")

    # Fetch data
    logs = []
    configs = []
    try:
        logs = APIClient.get_noise_logs()
        configs = APIClient.get_noise_configs()
    except Exception as e:
        st.error(f"Failed to fetch environmental records: {str(e)}")

    if configs:
        # Determine current Day/Night phase
        current_hour = datetime.utcnow().hour
        is_daytime = (6 <= current_hour < 22)
        phase_str = "Daytime Limit ☀️" if is_daytime else "Nighttime Limit 🌙"

        # 2. Metric Cards
        avg_db = sum(l["decibel_level"] for l in logs) / len(logs) if logs else 55.0
        breaches_count = sum(1 for l in logs if l["is_breached"])
        
        col_metric1, col_metric2, col_metric3 = st.columns(3)
        with col_metric1:
            st.metric("Fleet Average Decibels", f"{round(avg_db, 1)} dB")
        with col_metric2:
            st.metric("Active Decibel Breaches", f"{breaches_count} alerts", delta="Hazard Alarm" if breaches_count > 0 else "Optimal", delta_color="inverse" if breaches_count > 0 else "normal")
        with col_metric3:
            st.metric("Current Audit Phase", phase_str)

        # 3. Trend Line Chart
        st.markdown("### 📈 Decibel Level Trend over Time")
        if logs:
            line_list = []
            for l in reversed(logs):
                # Only plot the last 50 readouts to avoid cluttered lines
                line_list.append({
                    "Timestamp": pd.to_datetime(l["logged_at"]),
                    "Decibel level (dB)": l["decibel_level"],
                    "Sensor Zone": l["sensor_name"],
                    "Limit Limit (dB)": l["limit_threshold"]
                })
            
            line_df = pd.DataFrame(line_list)
            fig_line = px.line(
                line_df,
                x="Timestamp",
                y="Decibel level (dB)",
                color="Sensor Zone",
                hover_data=["Limit Limit (dB)"],
                color_discrete_sequence=px.colors.qualitative.Dark2
            )
            fig_line.update_layout(height=280, margin=dict(l=10, r=10, t=10, b=10))
            st.plotly_chart(fig_line, use_container_width=True)
        else:
            st.info("No decibel logs recorded. Line trends will display once sensor feeds are simulated.")

        # 4. Action forms columns
        st.markdown("---")
        col_log_form, col_config_form = st.columns(2)

        # 4a. Manual log form
        with col_log_form:
            st.markdown("### 📝 Log Manual Reading")
            with st.form("manual_noise_form", clear_on_submit=True):
                zone_c = st.selectbox("Sensor Zone:", ["Zone A (Excavation Area)", "Zone B (Structural Framing)", "Zone C (Site Boundary)"])
                db_val = st.number_input("Recorded Level (dB):", min_value=30.0, max_value=130.0, step=1.0)
                btn_log_submit = st.form_submit_button("Submit Decibel Reading", type="primary")

            if btn_log_submit:
                try:
                    APIClient.log_noise_decibel(zone_c, db_val)
                    st.success(f"Log registered for '{zone_c}': {db_val} dB.")
                    st.rerun()
                except Exception as e:
                    st.error(str(e))

        # 4b. Config daytime/nighttime rules form
        with col_config_form:
            st.markdown("### ⚙️ Calibrate Threshold Rules")
            with st.form("noise_config_form", clear_on_submit=True):
                zone_r = st.selectbox("Sensor Zone Target:", ["Zone A (Excavation Area)", "Zone B (Structural Framing)", "Zone C (Site Boundary)"])
                day_lim = st.slider("Daytime Limit (dB):", 40, 110, 85)
                night_lim = st.slider("Nighttime Limit (dB):", 30, 95, 55)
                btn_config_submit = st.form_submit_button("Update Calibration Rules", type="primary")

            if btn_config_submit:
                try:
                    APIClient.update_noise_config(zone_r, float(day_lim), float(night_lim))
                    st.success(f"Environmental noise rules updated for '{zone_r}'.")
                    st.rerun()
                except Exception as e:
                    st.error(str(e))

        # 5. Config thresholds listing
        st.markdown("---")
        st.markdown("### 📋 Calibrated Threshold Rules Sheet")
        config_data = []
        for c in configs:
            config_data.append({
                "Zone Description": c["sensor_name"],
                "Daytime Limit": f"{c['daytime_limit']} dB",
                "Nighttime Limit": f"{c['nighttime_limit']} dB",
                "Last Calibrated": pd.to_datetime(c["updated_at"]).strftime("%Y-%m-%d %H:%M")
            })
        st.table(pd.DataFrame(config_data))

        # 6. Detailed Logs Table
        st.markdown("### 📋 Detailed Decibel Audit History")
        if logs:
            log_data = []
            for l in logs[:15]:  # Display recent 15 readouts
                state_lbl = "🚨 BREACH WARNING" if l["is_breached"] else "🟢 Safe"
                log_data.append({
                    "Timestamp": pd.to_datetime(l["logged_at"]).strftime("%Y-%m-%d %H:%M:%S"),
                    "Zone": l["sensor_name"],
                    "Decibel Level": f"{l['decibel_level']} dB",
                    "Limit Enforced": f"{l['limit_threshold']} dB",
                    "Status": state_lbl
                })
            st.table(pd.DataFrame(log_data))
