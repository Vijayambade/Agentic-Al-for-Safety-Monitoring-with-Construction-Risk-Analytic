"""
frontend/pages/telematics_dashboard.py
-------------------------------------
Standalone page for Construction Equipment Telematics & Maintenance (Feature 8).
"""
import pandas as pd
import streamlit as st
from datetime import datetime
from frontend.utils.api_client import APIClient


def show_telematics_dashboard_page():
    st.markdown(
        '# <span class="gradient-text">🚜 Equipment Telematics & Predictive Maintenance</span>',
        unsafe_allow_html=True,
    )
    st.markdown(
        '<p class="subtitle-text">IoT telematics fleet manager. Monitor GPS coordinates, fuel levels, engine temperatures, and vibration sensors to forecast failure points automatically.</p>',
        unsafe_allow_html=True,
    )

    # 1. Sidebar Controls
    st.sidebar.markdown("### 🎛️ Sensor Simulator")
    stress_intensity = st.sidebar.slider("Inject Mechanical/Thermal Stress", 0.0, 1.0, 0.0, step=0.1)
    
    col_sim, col_reset = st.sidebar.columns(2)
    with col_sim:
        btn_sim = st.button("⚡ Inject Stress", use_container_width=True, type="primary")
    with col_reset:
        btn_reset = st.button("🔄 Reset Fleet", use_container_width=True)

    # Handle action requests
    fleet = []
    try:
        if btn_sim:
            with st.spinner("Injecting sensor stress values and updating health scores..."):
                fleet = APIClient.simulate_telematics_sensors(stress_intensity)
                st.success("Sensor telemetry updated successfully.")
        elif btn_reset:
            with st.spinner("Reverting fleet to default parameters..."):
                fleet = APIClient.reset_telematics_equipment()
                st.success("Fleet telemetry reset.")
        else:
            fleet = APIClient.get_telematics_equipment()
    except Exception as e:
        st.error(f"Telematics server error: {str(e)}")

    if fleet:
        # Sort fleet by ID
        fleet = sorted(fleet, key=lambda x: x["id"])

        # 2. KPI metrics cards
        avg_health = sum(eq["health_score"] for eq in fleet) / len(fleet)
        failures_count = sum(1 for eq in fleet if eq["predicted_failure"])
        low_fuel = sum(1 for eq in fleet if eq["fuel_level"] < 50.0)

        col_metric1, col_metric2, col_metric3 = st.columns(3)
        with col_metric1:
            st.metric("Fleet Health Average", f"{round(avg_health, 1)}%", delta=f"{round(avg_health - 100, 1)}%" if avg_health < 100 else "Optimal")
        with col_metric2:
            st.metric("Critical Failure Risks", f"{failures_count} alerts", delta="Emergency" if failures_count > 0 else "All Clean", delta_color="inverse" if failures_count > 0 else "normal")
        with col_metric3:
            st.metric("Low Fuel Alert Status", f"{low_fuel} vehicles", delta="Refuel Needed" if low_fuel > 0 else "Normal", delta_color="inverse" if low_fuel > 0 else "normal")

        # 3. GPS Map Overlay
        st.markdown("### 🗺️ Fleet Location Overlay (GPS)")
        map_data = []
        for eq in fleet:
            map_data.append({
                "latitude": eq["gps_latitude"],
                "longitude": eq["gps_longitude"],
                "name": eq["name"]
            })
        
        map_df = pd.DataFrame(map_data)
        st.map(map_df, size=20, zoom=14)

        # 4. Telemetry details table
        st.markdown("### 📋 Real-Time Telemetry Parameters")
        
        table_data = []
        for eq in fleet:
            risk_label = "🚨 High Risk" if eq["predicted_failure"] else "🟢 Healthy"
            sched_str = datetime.fromisoformat(eq["maintenance_scheduled_at"].replace("Z", "+00:00")).strftime("%Y-%m-%d") if eq["maintenance_scheduled_at"] else "None"
            
            table_data.append({
                "ID": eq["id"],
                "Equipment Name": eq["name"],
                "Status": eq["status"],
                "Fuel Level": f"{eq['fuel_level']}%",
                "Engine Temp": f"{eq['engine_temp']}°C",
                "Vibration": f"{eq['vibration_level']} mm/s",
                "Health Score": f"{eq['health_score']}%",
                "Failure Risk": risk_label,
                "Service Date": sched_str
            })
            
        st.table(pd.DataFrame(table_data))

        st.markdown("---")

        # 5. Interactive Maintenance Scheduling form
        st.markdown("### 📅 Schedule Preventive Maintenance")
        
        eq_options = {eq["name"]: eq["id"] for eq in fleet}
        
        with st.form("maintenance_form", clear_on_submit=True):
            col_eq, col_date = st.columns(2)
            with col_eq:
                selected_eq_name = st.selectbox("Select Equipment:", options=list(eq_options.keys()))
            with col_date:
                sched_date = st.date_input("Scheduled Date:", min_value=datetime.today())
                
            submit_sched = st.form_submit_button("Submit Maintenance Schedule", type="primary")

        if submit_sched:
            eq_id = eq_options[selected_eq_name]
            date_str = sched_date.isoformat()
            try:
                APIClient.schedule_equipment_maintenance(eq_id, date_str)
                st.success(f"Maintenance successfully scheduled for '{selected_eq_name}' on {sched_date}.")
                st.rerun()
            except Exception as e:
                st.error(str(e))
