"""
frontend/pages/waste_management.py
----------------------------------
Standalone page for Construction Site Waste Management & Sustainability (Feature 10).
"""
import pandas as pd
import streamlit as st
import plotly.express as px
from frontend.utils.api_client import APIClient


def show_waste_management_page():
    st.markdown(
        '# <span class="gradient-text">♻️ Site Waste Management & Sustainability</span>',
        unsafe_allow_html=True,
    )
    st.markdown(
        '<p class="subtitle-text">Monitor recycling percentages, log debris disposal activities, track reduction goals, and review sustainable site optimization tips.</p>',
        unsafe_allow_html=True,
    )

    # 1. Sidebar control
    st.sidebar.markdown("### 🎛️ Debris Controls")
    btn_reset = st.sidebar.button("🔄 Reset Sustainability Data", use_container_width=True)

    # Handle Reset request
    try:
        if btn_reset:
            with st.spinner("Clearing logs and reverting reduction goals..."):
                APIClient.reset_waste_data()
                st.success("Sustainability logs reset successfully.")
    except Exception as e:
        st.error(f"Sustainability engine error: {str(e)}")

    # Fetch data
    logs = []
    goals = []
    analytics = {}
    try:
        logs = APIClient.get_waste_logs()
        goals = APIClient.get_waste_goals()
        analytics = APIClient.get_waste_analytics()
    except Exception as e:
        st.error(f"Failed to fetch sustainability records: {str(e)}")

    if goals and analytics:
        # 2. KPI metrics cards
        total_qty = analytics["total_waste"]
        diversion_rate = analytics["diversion_rate"]
        goals_met = analytics["goals_met"]
        total_goals = analytics["total_goals"]

        col_metric1, col_metric2, col_metric3 = st.columns(3)
        with col_metric1:
            st.metric("Total Debris Logged", f"{total_qty} Tons")
        with col_metric2:
            st.metric("Landfill Diversion Rate", f"{diversion_rate}%", delta="High Diversion" if diversion_rate > 60 else "Low Recycling", delta_color="normal" if diversion_rate > 60 else "inverse")
        with col_metric3:
            st.metric("Reduction Goals Met", f"{goals_met} of {total_goals}", delta="On Track" if goals_met == total_goals else f"{total_goals - goals_met} breached", delta_color="normal" if goals_met == total_goals else "inverse")

        # 3. Visualization plots
        st.markdown("### 📊 Sustainability Visualizations")
        col_bar, col_pie = st.columns(2)

        with col_bar:
            st.markdown("##### Debris Quantities: Actual vs. Goal Limit")
            bar_list = []
            for g in analytics["goals"]:
                # Actual
                bar_list.append({
                    "Material": g["waste_type"],
                    "Quantity (Tons)": g["actual_quantity"],
                    "Metric Type": "Actual Debris"
                })
                # Goal limit
                bar_list.append({
                    "Material": g["waste_type"],
                    "Quantity (Tons)": g["goal_quantity"],
                    "Metric Type": "Target Limit"
                })
            
            bar_df = pd.DataFrame(bar_list)
            fig_bar = px.bar(
                bar_df,
                x="Material",
                y="Quantity (Tons)",
                color="Metric Type",
                barmode="group",
                color_discrete_map={
                    "Actual Debris": "#EF4444",  # Danger Red
                    "Target Limit": "#10B981"   # Success Green
                }
            )
            fig_bar.update_layout(height=260, margin=dict(l=10, r=10, t=10, b=10))
            st.plotly_chart(fig_bar, use_container_width=True)

        with col_pie:
            st.markdown("##### Disposal Methods Breakdown")
            if logs:
                pie_data = {}
                for l in logs:
                    pie_data[l["disposal_method"]] = pie_data.get(l["disposal_method"], 0.0) + l["quantity"]
                
                pie_df = pd.DataFrame([
                    {"Method": k, "Quantity (Tons)": v}
                    for k, v in pie_data.items()
                ])
                fig_pie = px.pie(
                    pie_df,
                    values="Quantity (Tons)",
                    names="Method",
                    hole=0.4,
                    color_discrete_sequence=px.colors.qualitative.Pastel
                )
                fig_pie.update_layout(height=260, margin=dict(l=10, r=10, t=10, b=10))
                st.plotly_chart(fig_pie, use_container_width=True)
            else:
                st.info("No debris logged. Disposal breakdown donut will populate once logs are added.")

        # 4. Action forms columns
        st.markdown("---")
        col_log_form, col_goal_form = st.columns(2)

        # 4a. Log Waste disposal form
        with col_log_form:
            st.markdown("### 📝 Log Waste Disposal")
            with st.form("waste_log_form", clear_on_submit=True):
                w_type = st.selectbox("Waste Category:", ["Concrete", "Steel", "Wood", "Packaging", "Hazardous"])
                qty = st.number_input("Debris Quantity (Tons):", min_value=0.1, step=0.5)
                disp_method = st.selectbox("Disposal Method:", ["Recycled", "Reused", "Landfill", "Incinerated"])
                cost = st.number_input("Disposal Cost ($):", min_value=0.0, step=10.0)
                btn_log_submit = st.form_submit_button("Log Disposal Event", type="primary")

            if btn_log_submit:
                try:
                    APIClient.log_waste_disposal(w_type, qty, "Tons", disp_method, cost)
                    st.success(f"Successfully logged {qty} Tons of {w_type} debris disposal.")
                    st.rerun()
                except Exception as e:
                    st.error(str(e))

        # 4b. Configure Goals Form
        with col_goal_form:
            st.markdown("### 🎯 Adjust Reduction Goals")
            with st.form("waste_goal_form", clear_on_submit=True):
                w_type_goal = st.selectbox("Waste Category Target:", ["Concrete", "Steel", "Wood", "Packaging", "Hazardous"])
                target_limit = st.number_input("Target Limit (Tons):", min_value=0.5, step=1.0)
                btn_goal_submit = st.form_submit_button("Update Target Goal", type="primary")

            if btn_goal_submit:
                try:
                    APIClient.update_waste_goal(w_type_goal, target_limit, "Tons")
                    st.success(f"Updated waste target goal for '{w_type_goal}' to {target_limit} Tons.")
                    st.rerun()
                except Exception as e:
                    st.error(str(e))

        # 5. Sustainability suggestions
        st.markdown("---")
        st.markdown("### 💡 AI Sustainability & minimization recommendations")
        
        tips = analytics.get("sustainability_tips", [])
        for tip in tips:
            st.info(tip)
