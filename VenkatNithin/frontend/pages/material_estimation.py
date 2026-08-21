"""
frontend/pages/material_estimation.py
---------------------------------------
Streamlit page UI for Material Estimation Module.
Allows users to configure construction project parameters, calculate material quantity takeoffs,
view cost breakdowns and interactive Plotly charts, and export PDF/CSV reports.
"""
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st
from frontend.utils.api_client import APIClient


def show_material_estimation_page():
    st.markdown(
        '# <span class="gradient-text">📐 Construction Material Estimation</span>',
        unsafe_allow_html=True,
    )
    st.markdown(
        '<p class="subtitle-text">Calculate detailed quantity takeoffs, material distribution, and itemized cost breakdowns tailored to your project type and quality standards.</p>',
        unsafe_allow_html=True,
    )

    st.markdown("---")

    # 1. Project Input Parameters Form
    st.markdown("### 🛠️ Project Configuration & Parameters")

    with st.form("material_estimation_form"):
        col1, col2, col3 = st.columns(3)

        with col1:
            project_type = st.selectbox(
                "Project Type",
                ["Residential", "Commercial", "Industrial"],
                help="Select the category of construction project.",
            )
            built_up_area = st.number_input(
                "Built-up Area",
                min_value=1.0,
                value=2500.0,
                step=100.0,
                help="Enter total ground or footprint area.",
            )
            area_unit = st.radio(
                "Area Unit",
                ["Square Feet (sq.ft)", "Square Meters (sq.m)"],
                horizontal=True,
            )

        with col2:
            floors = st.number_input(
                "Number of Floors",
                min_value=1,
                max_value=120,
                value=2,
                step=1,
                help="Number of storeys/floors in the building.",
            )
            material_quality = st.selectbox(
                "Material Quality Grade",
                ["Standard", "Premium", "Luxury"],
                help="Quality tier affects material specifications and unit costs.",
            )
            construction_type = st.selectbox(
                "Structural Construction Type",
                ["RCC", "Steel Structure", "Hybrid"],
                help="Primary structural framing system.",
            )

        with col3:
            location = st.text_input(
                "Project Location (Optional)",
                placeholder="e.g. Austin, TX or Site #42",
                help="Optional location identifier for project reporting.",
            )
            st.markdown("<br>", unsafe_allow_html=True)
            btn_estimate = st.form_submit_button(
                "🧮 Estimate Material Quantities & Costs",
                type="primary",
                use_container_width=True,
            )

    # Convert area unit code
    unit_code = "sq_ft" if "Feet" in area_unit else "sq_m"

    # Validation checks
    if btn_estimate:
        if built_up_area <= 0:
            st.error("⚠️ Built-up area must be a positive number greater than 0.")
            return
        if floors < 1:
            st.error("⚠️ Number of floors must be at least 1.")
            return

        payload = {
            "project_type": project_type,
            "built_up_area": float(built_up_area),
            "area_unit": unit_code,
            "floors": int(floors),
            "material_quality": material_quality,
            "construction_type": construction_type,
            "location": location.strip() if location else None,
        }

        with st.spinner("Calculating quantity takeoff formulas and material costs..."):
            try:
                res = APIClient.calculate_material_estimation(payload)
                st.session_state["latest_estimation_result"] = res
                st.session_state["latest_estimation_payload"] = payload
                st.success("Material estimation completed successfully!")
            except Exception as e:
                st.error(f"Failed to calculate estimation: {str(e)}")

    # 2. Display Results if available in session state
    if "latest_estimation_result" in st.session_state:
        res = st.session_state["latest_estimation_result"]
        payload = st.session_state["latest_estimation_payload"]
        summary = res.get("project_summary", {})
        materials = res.get("materials", [])
        total_cost = res.get("total_estimated_cost", 0.0)

        st.markdown("---")
        st.markdown("### 📊 Estimation Summary & Key Metrics")

        m1, m2, m3, m4 = st.columns(4)
        with m1:
            st.metric("Total Estimated Cost", f"${total_cost:,.2f}")
        with m2:
            st.metric("Total Effective Area", f"{summary.get('total_effective_area_sqft'):,} sq.ft.")
        with m3:
            st.metric("Quality Grade", summary.get("material_quality"))
        with m4:
            st.metric("Structural System", summary.get("construction_type"))

        # Table Display
        st.markdown("### 📋 Itemized Material Takeoff Table")
        
        df_materials = pd.DataFrame(materials)
        if not df_materials.empty:
            df_display = df_materials.copy()
            df_display.columns = ["Material Name", "Estimated Quantity", "Unit", "Estimated Cost ($)"]
            df_display["Estimated Quantity"] = df_display["Estimated Quantity"].apply(lambda x: f"{x:,.2f}")
            df_display["Estimated Cost ($)"] = df_display["Estimated Cost ($)"].apply(lambda x: f"${x:,.2f}")
            
            st.dataframe(
                df_display,
                use_container_width=True,
                hide_index=True,
            )

        # Charts Section
        st.markdown("---")
        st.markdown("### 📈 Visual Analytics & Distribution")
        
        chart_col1, chart_col2 = st.columns(2)

        with chart_col1:
            st.markdown("#### Material Quantity Distribution (%)")
            dist_data = res.get("material_distribution", {})
            if dist_data:
                fig_dist = px.pie(
                    names=list(dist_data.keys()),
                    values=list(dist_data.values()),
                    hole=0.4,
                    color_discrete_sequence=px.colors.qualitative.Pastel,
                )
                fig_dist.update_layout(
                    margin=dict(l=20, r=20, t=30, b=20),
                    paper_bgcolor="rgba(0,0,0,0)",
                    plot_bgcolor="rgba(0,0,0,0)",
                    font=dict(color="#1F2937"),
                )
                st.plotly_chart(fig_dist, use_container_width=True)

        with chart_col2:
            st.markdown("#### Cost Breakdown per Material ($)")
            cost_data = res.get("cost_breakdown", {})
            if cost_data:
                df_cost = pd.DataFrame({
                    "Material": list(cost_data.keys()),
                    "Cost": list(cost_data.values()),
                }).sort_values(by="Cost", ascending=True)

                fig_cost = px.bar(
                    df_cost,
                    x="Cost",
                    y="Material",
                    orientation="h",
                    text_auto=".2s",
                    color="Cost",
                    color_continuous_scale="Oranges",
                )
                fig_cost.update_layout(
                    margin=dict(l=20, r=20, t=30, b=20),
                    paper_bgcolor="rgba(0,0,0,0)",
                    plot_bgcolor="rgba(0,0,0,0)",
                    showlegend=False,
                    xaxis_title="Cost ($)",
                    yaxis_title="",
                )
                st.plotly_chart(fig_cost, use_container_width=True)

        # Exports & Print Options
        st.markdown("---")
        st.markdown("### 📄 Export & Print Report")

        exp_col1, exp_col2, exp_col3 = st.columns(3)

        with exp_col1:
            try:
                pdf_bytes = APIClient.export_material_estimation_pdf(payload)
                st.download_button(
                    label="📥 Download PDF Report",
                    data=pdf_bytes,
                    file_name="Material_Estimation_Report.pdf",
                    mime="application/pdf",
                    use_container_width=True,
                    type="primary",
                )
            except Exception as e:
                st.error(f"PDF download error: {str(e)}")

        with exp_col2:
            try:
                csv_data = APIClient.export_material_estimation_csv(payload)
                st.download_button(
                    label="📊 Export as CSV",
                    data=csv_data,
                    file_name="Material_Estimation_Report.csv",
                    mime="text/csv",
                    use_container_width=True,
                )
            except Exception as e:
                st.error(f"CSV export error: {str(e)}")

        with exp_col3:
            with st.popover("🖨️ Print Preview", use_container_width=True):
                st.markdown("#### Report Print View")
                st.markdown(f"**Project Type**: {summary.get('project_type')}")
                st.markdown(f"**Built-up Area**: {summary.get('built_up_area')} {summary.get('area_unit')}")
                st.markdown(f"**Total Estimated Cost**: **${total_cost:,.2f}**")
                st.markdown("---")
                st.markdown("Press `Ctrl + P` in your browser to print this summary page directly.")
