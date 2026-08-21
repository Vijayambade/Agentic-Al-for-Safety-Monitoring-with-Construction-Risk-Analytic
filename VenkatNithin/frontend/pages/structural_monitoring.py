"""
frontend/pages/structural_monitoring.py
---------------------------------------
Standalone page for Real-Time Structural Health & Vibration Monitoring (Feature 14).
"""
import pandas as pd
import streamlit as st
import plotly.express as px
from frontend.utils.api_client import APIClient


def show_structural_monitoring_page():
    st.markdown(
        '# <span class="gradient-text">🏗️ IoT Structural Health & Vibration Monitoring</span>',
        unsafe_allow_html=True,
    )
    st.markdown(
        '<p class="subtitle-text">IoT Structural Safety Center. Track structure stress, strain forces, tilt angles, and vibration frequencies across structural grids.</p>',
        unsafe_allow_html=True,
    )

    # 1. Sidebar Control
    st.sidebar.markdown("### 🎛️ Structure Load Simulator")
    stress_intensity = st.sidebar.slider("Structure Load Stress (Weight/Wind)", 0.0, 1.0, 0.0, step=0.1)
    
    col_mock, col_reset = st.sidebar.columns(2)
    with col_mock:
        btn_mock = st.button("⚡ Mock Load", use_container_width=True, type="primary")
    with col_reset:
        btn_reset = st.button("🔄 Reset Logs", use_container_width=True)

    # Handle simulation and reset
    try:
        if btn_mock:
            with st.spinner("Calculating load strain and auditing structural guidelines..."):
                APIClient.simulate_structural_health(stress_intensity)
                st.success("Structural telemetry logs captured.")
        elif btn_reset:
            with st.spinner("Clearing safety logs and restoring guidelines..."):
                APIClient.reset_structural_data()
                st.success("Structural configurations and logs reset.")
    except Exception as e:
        st.error(f"Structural monitoring system error: {str(e)}")

    # Fetch data
    logs = []
    configs = []
    try:
        logs = APIClient.get_structural_logs()
        configs = APIClient.get_structural_configs()
    except Exception as e:
        st.error(f"Failed to fetch structural monitoring records: {str(e)}")

    if configs:
        # 2. KPI metrics cards
        avg_vib = sum(l["vibration_frequency"] for l in logs) / len(logs) if logs else 10.0
        max_strain = max((l["strain"] for l in logs), default=30.0)
        unstable_count = sum(1 for l in logs if l["is_unstable"])

        col_metric1, col_metric2, col_metric3 = st.columns(3)
        with col_metric1:
            st.metric("Grid Avg Vibration", f"{round(avg_vib, 1)} Hz")
        with col_metric2:
            st.metric("Peak Structural Strain", f"{round(max_strain, 1)} µε")
        with col_metric3:
            st.metric("Collapse Warnings", f"{unstable_count} warnings", delta="Instability Danger" if unstable_count > 0 else "All Stable", delta_color="inverse" if unstable_count > 0 else "normal")

        # 3. Plots
        st.markdown("### 📊 Structural Vibration & Tilt Timelines")
        col_vib_plot, col_tilt_plot = st.columns(2)

        with col_vib_plot:
            st.markdown("##### Vibration Frequency (Hz) over Time")
            if logs:
                vib_list = []
                for l in reversed(logs):
                    vib_list.append({
                        "Timestamp": pd.to_datetime(l["logged_at"]),
                        "Vibration (Hz)": l["vibration_frequency"],
                        "Structure Zone": l["sensor_name"]
                    })
                
                vib_df = pd.DataFrame(vib_list)
                fig_vib = px.line(
                    vib_df,
                    x="Timestamp",
                    y="Vibration (Hz)",
                    color="Structure Zone",
                    color_discrete_sequence=px.colors.qualitative.Dark2
                )
                fig_vib.update_layout(height=260, margin=dict(l=10, r=10, t=10, b=10))
                st.plotly_chart(fig_vib, use_container_width=True)
            else:
                st.info("No logs. Vibration charts will populate once mock telemetry is run.")

        with col_tilt_plot:
            st.markdown("##### Tilt Angle (degrees) over Time")
            if logs:
                tilt_list = []
                for l in reversed(logs):
                    tilt_list.append({
                        "Timestamp": pd.to_datetime(l["logged_at"]),
                        "Tilt Angle (°)": l["tilt_angle"],
                        "Structure Zone": l["sensor_name"]
                    })
                
                tilt_df = pd.DataFrame(tilt_list)
                fig_tilt = px.line(
                    tilt_df,
                    x="Timestamp",
                    y="Tilt Angle (°)",
                    color="Structure Zone",
                    color_discrete_sequence=px.colors.qualitative.Pastel1
                )
                fig_tilt.update_layout(height=260, margin=dict(l=10, r=10, t=10, b=10))
                st.plotly_chart(fig_tilt, use_container_width=True)
            else:
                st.info("No logs. Tilt charts will populate once mock telemetry is run.")

        # 4. Action forms columns
        st.markdown("---")
        col_log_form, col_config_form = st.columns(2)

        # 4a. Manual log form
        with col_log_form:
            st.markdown("### 📝 Log Manual Telemetry")
            with st.form("manual_structural_form", clear_on_submit=True):
                sensor_c = st.selectbox("Structure Zone:", ["Scaffolding Tower Zone A", "Concrete Formwork Zone B", "Foundation Column Pier C"])
                vib_val = st.number_input("Vibration Frequency (Hz):", min_value=0.0, value=12.0, step=1.0)
                amp_val = st.number_input("Amplitude (mm):", min_value=0.0, value=0.5, step=0.05)
                tilt_val = st.number_input("Tilt Angle (degrees):", min_value=0.0, value=0.5, step=0.1)
                strain_val = st.number_input("Strain (microstrain):", min_value=0.0, value=40.0, step=10.0)
                btn_log_submit = st.form_submit_button("Submit Telemetry Log", type="primary")

            if btn_log_submit:
                try:
                    APIClient.log_structural_reading(sensor_c, vib_val, amp_val, tilt_val, strain_val)
                    st.success(f"Structural telemetry logged for '{sensor_c}'.")
                    st.rerun()
                except Exception as e:
                    st.error(str(e))

        # 4b. Config safety thresholds rules form
        with col_config_form:
            st.markdown("### ⚙️ Calibrate Safety Thresholds")
            with st.form("structural_config_form", clear_on_submit=True):
                sensor_r = st.selectbox("Sensor Target Zone:", ["Scaffolding Tower Zone A", "Concrete Formwork Zone B", "Foundation Column Pier C"])
                max_vib_lim = st.slider("Max Vibration Frequency (Hz):", 10, 150, 50)
                max_tilt_lim = st.slider("Max Tilt Angle (degrees):", 1, 45, 5)
                max_strain_lim = st.slider("Max Strain (microstrain):", 50, 1000, 300, step=50)
                btn_config_submit = st.form_submit_button("Update Safety Boundaries", type="primary")

            if btn_config_submit:
                try:
                    APIClient.update_structural_config(sensor_r, float(max_vib_lim), float(max_tilt_lim), float(max_strain_lim))
                    st.success(f"Safety boundaries updated for '{sensor_r}'.")
                    st.rerun()
                except Exception as e:
                    st.error(str(e))

        # 5. Config thresholds listing
        st.markdown("---")
        st.markdown("### 📋 Calibrated Structural Safety Guidelines")
        config_data = []
        for c in configs:
            config_data.append({
                "Structure Location": c["sensor_name"],
                "Max Vibration": f"{c['max_vibration_frequency']} Hz",
                "Max Tilt Angle": f"{c['max_tilt_angle']}°",
                "Max Strain Limit": f"{c['max_strain']} µε",
                "Last Calibrated": pd.to_datetime(c["updated_at"]).strftime("%Y-%m-%d %H:%M")
            })
        st.table(pd.DataFrame(config_data))

        # 6. Detailed Logs Table
        st.markdown("### 📋 Detailed Structural Stress Audit Logs")
        if logs:
            log_data = []
            for l in logs[:15]:  # Display recent 15 logs
                state_lbl = "🚨 COLLAPSE HAZARD ALERT" if l["is_unstable"] else "🟢 Stable Structure"
                log_data.append({
                    "Timestamp": pd.to_datetime(l["logged_at"]).strftime("%Y-%m-%d %H:%M:%S"),
                    "Location": l["sensor_name"],
                    "Vibration": f"{l['vibration_frequency']} Hz",
                    "Tilt Angle": f"{l['tilt_angle']}°",
                    "Strain Force": f"{l['strain']} µε",
                    "Audit Result": state_lbl,
                    "Issues Logged": l["instability_reason"]
                })
            st.table(pd.DataFrame(log_data))
st.write("")
st.write("")
