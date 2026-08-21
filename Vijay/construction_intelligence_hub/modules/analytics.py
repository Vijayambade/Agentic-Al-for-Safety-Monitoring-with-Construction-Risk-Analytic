import streamlit as st
import pandas as pd
import plotly.express as px
from utils.helpers import generate_sample_projects, format_currency


def render():
    st.header("📊 Project Analytics")
    st.caption("Upload your own project CSV, or explore with sample data.")

    uploaded = st.file_uploader(
        "Upload project CSV (columns: Project, Type, Budget, ActualCost, "
        "PlannedDays, ActualDays, Progress%, Status)", type=["csv"]
    )

    if uploaded is not None:
        df = pd.read_csv(uploaded)
    else:
        st.info("No file uploaded — showing sample data so you can preview the dashboard.")
        df = generate_sample_projects()

    st.dataframe(df, use_container_width=True)

    df["CostVariance"] = df["ActualCost"] - df["Budget"]
    df["CostVariance%"] = (df["CostVariance"] / df["Budget"] * 100).round(1)
    df["ScheduleVariance%"] = ((df["ActualDays"] - df["PlannedDays"]) / df["PlannedDays"] * 100).round(1)

    k1, k2, k3, k4 = st.columns(4)
    k1.metric("Total Projects", len(df))
    k2.metric("Total Budget", format_currency(df["Budget"].sum()))
    k3.metric("Avg Cost Variance", f"{df['CostVariance%'].mean():.1f}%")
    k4.metric("Avg Schedule Variance", f"{df['ScheduleVariance%'].mean():.1f}%")

    st.subheader("Budget vs Actual Cost")
    fig1 = px.bar(df, x="Project", y=["Budget", "ActualCost"], barmode="group")
    fig1.update_layout(height=380, margin=dict(t=20, b=10))
    st.plotly_chart(fig1, use_container_width=True)

    c1, c2 = st.columns(2)
    with c1:
        st.subheader("Projects by Type")
        fig2 = px.pie(df, names="Type", hole=0.45)
        fig2.update_layout(height=320, margin=dict(t=20, b=10))
        st.plotly_chart(fig2, use_container_width=True)
    with c2:
        st.subheader("Status Distribution")
        fig3 = px.bar(df["Status"].value_counts().reset_index(),
                       x="Status", y="count", color="Status")
        fig3.update_layout(height=320, margin=dict(t=20, b=10))
        st.plotly_chart(fig3, use_container_width=True)

    st.subheader("Cost Variance % by Project")
    fig4 = px.bar(df.sort_values("CostVariance%"), x="Project", y="CostVariance%",
                   color="CostVariance%", color_continuous_scale="RdYlGn_r")
    fig4.update_layout(height=350, margin=dict(t=20, b=10))
    st.plotly_chart(fig4, use_container_width=True)
