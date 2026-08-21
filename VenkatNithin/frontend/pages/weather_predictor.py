"""
frontend/pages/weather_predictor.py
-----------------------------------
Standalone page for Construction Site Weather & Environmental Hazards Predictor (Feature 16).
"""
import pandas as pd
import streamlit as st
import plotly.express as px
from frontend.utils.api_client import APIClient


def show_weather_monitoring_page():
    st.markdown(
        '# <span class="gradient-text">⛈️ Weather & Environmental Hazards Predictor</span>',
        unsafe_allow_html=True,
    )
    st.markdown(
        '<p class="subtitle-text">IoT Environmental Warning Center. Forecast safety thresholds for high wind crane operations, extreme heat indexes, and heavy rainfall storm risks.</p>',
        unsafe_allow_html=True,
    )

    # 1. Sidebar Control
    st.sidebar.markdown("### 🎛️ Weather Event Simulator")
    stress_intensity = st.sidebar.slider("Extreme Weather Intensity (Storm/Heat)", 0.0, 1.0, 0.0, step=0.1)
    
    col_mock, col_reset = st.sidebar.columns(2)
    with col_mock:
        btn_mock = st.button("⚡ Mock Weather", use_container_width=True, type="primary")
    with col_reset:
        btn_reset = st.button("🔄 Reset Logs", use_container_width=True)

    # Handle simulation and reset
    try:
        if btn_mock:
            with st.spinner("Simulating atmospheric variations and checking safety thresholds..."):
                APIClient.simulate_weather_flow(stress_intensity)
                st.success("Atmospheric telemetry logged.")
        elif btn_reset:
            with st.spinner("Clearing weather logs and safety thresholds..."):
                APIClient.reset_weather_data()
                st.success("Weather configurations and logs reset.")
    except Exception as e:
        st.error(f"Weather monitoring system error: {str(e)}")

    # Fetch data
    logs = []
    configs = []
    try:
        logs = APIClient.get_weather_logs()
        configs = APIClient.get_weather_configs()
    except Exception as e:
        st.error(f"Failed to fetch weather telemetry records: {str(e)}")

    if configs:
        # 2. KPI metrics cards
        current_temp = logs[0]["temperature"] if logs else 25.0
        max_wind = max((l["wind_speed"] for l in logs), default=12.0)
        hazardous_count = sum(1 for l in logs if l["is_hazardous"])

        col_metric1, col_metric2, col_metric3 = st.columns(3)
        with col_metric1:
            st.metric("Grid Avg Temperature", f"{round(current_temp, 1)} °C")
        with col_metric2:
            st.metric("Peak Wind Speed", f"{round(max_wind, 1)} km/h")
        with col_metric3:
            st.metric("Active Weather Hazards", f"{hazardous_count} alerts", delta="Storm Threat" if hazardous_count > 0 else "Clear Skies", delta_color="inverse" if hazardous_count > 0 else "normal")

        # 3. Plots
        st.markdown("### 📊 Wind Velocity & Atmospheric Timelines")
        col_wind_plot, col_rain_plot = st.columns(2)

        with col_wind_plot:
            st.markdown("##### Wind Velocity (km/h) & Temp (°C) over Time")
            if logs:
                wind_list = []
                for l in reversed(logs):
                    wind_list.append({
                        "Timestamp": pd.to_datetime(l["logged_at"]),
                        "Wind Velocity (km/h)": l["wind_speed"],
                        "Temp (°C)": l["temperature"],
                        "Sensor Location": l["sensor_name"]
                    })
                
                wind_df = pd.DataFrame(wind_list)
                fig_wind = px.line(
                    wind_df,
                    x="Timestamp",
                    y=["Wind Velocity (km/h)", "Temp (°C)"],
                    color="Sensor Location",
                    color_discrete_sequence=px.colors.qualitative.Dark2
                )
                fig_wind.update_layout(height=260, margin=dict(l=10, r=10, t=10, b=10))
                st.plotly_chart(fig_wind, use_container_width=True)
            else:
                st.info("No logs. Wind velocity trends will populate once mock telemetry is run.")

        with col_rain_plot:
            st.markdown("##### Rain Precipitation (mm) by Location")
            if logs:
                rain_list = []
                for l in reversed(logs):
                    rain_list.append({
                        "Timestamp": pd.to_datetime(l["logged_at"]),
                        "Precipitation (mm)": l["precipitation"],
                        "Sensor Location": l["sensor_name"]
                    })
                
                rain_df = pd.DataFrame(rain_list)
                fig_rain = px.bar(
                    rain_df,
                    x="Timestamp",
                    y="Precipitation (mm)",
                    color="Sensor Location",
                    color_discrete_sequence=px.colors.qualitative.Pastel1
                )
                fig_rain.update_layout(height=260, margin=dict(l=10, r=10, t=10, b=10))
                st.plotly_chart(fig_rain, use_container_width=True)
            else:
                st.info("No logs. Rain levels will populate once mock telemetry is run.")

        # 4. Action forms columns
        st.markdown("---")
        col_log_form, col_config_form = st.columns(2)

        # 4a. Manual log form
        with col_log_form:
            st.markdown("### 📝 Log Manual Telemetry")
            with st.form("manual_weather_form", clear_on_submit=True):
                sensor_c = st.selectbox("Sensor Location:", ["Tower Crane Jib Peak", "Ground Weather Station", "Perimeter Boundary Mast"])
                temp_val = st.number_input("Temperature (°C):", min_value=-20.0, max_value=50.0, value=28.0, step=1.0)
                wind_val = st.number_input("Wind Speed (km/h):", min_value=0.0, value=15.0, step=1.0)
                hum_val = st.slider("Humidity (%):", 0, 100, 60)
                rain_val = st.number_input("Precipitation (mm):", min_value=0.0, value=0.0, step=1.0)
                baro_val = st.number_input("Barometric Pressure (hPa):", min_value=900.0, max_value=1100.0, value=1013.0, step=1.0)
                uv_val = st.slider("UV Index:", 0.0, 15.0, 3.0, step=0.5)
                btn_log_submit = st.form_submit_button("Submit Weather Log", type="primary")

            if btn_log_submit:
                try:
                    APIClient.log_weather_reading(sensor_c, temp_val, wind_val, float(hum_val), rain_val, baro_val, uv_val)
                    st.success(f"Weather telemetry logged for '{sensor_c}'.")
                    st.rerun()
                except Exception as e:
                    st.error(str(e))

        # 4b. Config safety thresholds rules form
        with col_config_form:
            st.markdown("### ⚙️ Calibrate Safety Thresholds")
            with st.form("weather_config_form", clear_on_submit=True):
                sensor_r = st.selectbox("Sensor Target:", ["Tower Crane Jib Peak", "Ground Weather Station", "Perimeter Boundary Mast"])
                max_wind_lim = st.slider("Max Wind Speed Limit (km/h):", 10, 100, 40)
                max_temp_lim = st.slider("Max Heat Temp Limit (°C):", 20, 50, 38)
                max_rain_lim = st.slider("Max Precipitation Limit (mm):", 10, 150, 50, step=5)
                btn_config_submit = st.form_submit_button("Update Safety Boundaries", type="primary")

            if btn_config_submit:
                try:
                    APIClient.update_weather_config(sensor_r, float(max_wind_lim), float(max_temp_lim), float(max_rain_lim))
                    st.success(f"Safety boundaries updated for '{sensor_r}'.")
                    st.rerun()
                except Exception as e:
                    st.error(str(e))

        # 5. Config thresholds listing
        st.markdown("---")
        st.markdown("### 📋 Calibrated Weather Safety Guidelines")
        config_data = []
        for c in configs:
            config_data.append({
                "Sensor Location": c["sensor_name"],
                "Max Wind Speed": f"{c['max_wind_speed_limit']} km/h",
                "Max Heat Limit": f"{c['max_temp_limit']} °C",
                "Max Rain Limit": f"{c['max_precipitation_limit']} mm",
                "Last Calibrated": pd.to_datetime(c["updated_at"]).strftime("%Y-%m-%d %H:%M")
            })
        st.table(pd.DataFrame(config_data))

        # 6. Detailed Logs Table
        st.markdown("### 📋 Detailed Environmental Weather Audit Logs")
        if logs:
            log_data = []
            for l in logs[:15]:  # Display recent 15 logs
                state_lbl = "🚨 HAZARDOUS THREAT" if l["is_hazardous"] else "🟢 Stable Conditions"
                log_data.append({
                    "Timestamp": pd.to_datetime(l["logged_at"]).strftime("%Y-%m-%d %H:%M:%S"),
                    "Sensor Location": l["sensor_name"],
                    "Temp": f"{l['temperature']} °C",
                    "Wind Speed": f"{l['wind_speed']} km/h",
                    "Rain": f"{l['precipitation']} mm",
                    "UV Index": f"{l['uv_index']}",
                    "Audit Result": state_lbl,
                    "Threat Hazards": l["hazard_types"]
                })
            st.table(pd.DataFrame(log_data))
st.write("")
st.write("")
