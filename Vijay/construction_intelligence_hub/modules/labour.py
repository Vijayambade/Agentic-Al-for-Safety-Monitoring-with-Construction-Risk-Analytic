import streamlit as st
import pandas as pd
from datetime import date
from utils import data_store as ds
from utils.helpers import format_currency

STATUS_WAGE_FACTOR = {"Present": 1.0, "Half Day": 0.5, "Absent": 0.0, "Paid Leave": 1.0}
ROLES = ["Mason", "Carpenter", "Electrician", "Plumber", "Painter",
         "Helper", "Steel Fixer", "Supervisor", "Other"]


def render():
    st.header("👷 Labour Management & Attendance")
    tab1, tab2, tab3 = st.tabs(["📋 Labour Directory", "✅ Mark Attendance", "📈 Attendance & Wages"])

    with tab1:
        _render_directory()
    with tab2:
        _render_attendance_marking()
    with tab3:
        _render_summary()


def _render_directory():
    st.subheader("Add New Labour")
    with st.form("add_labour_form", clear_on_submit=True):
        c1, c2 = st.columns(2)
        with c1:
            name = st.text_input("Full Name")
            role = st.selectbox("Role", ROLES)
            contact = st.text_input("Contact Number")
        with c2:
            daily_wage = st.number_input("Daily Wage (₹)", min_value=200, value=700, step=50)
            join_date = st.date_input("Join Date", value=date.today())
        submitted = st.form_submit_button("Add Labour", type="primary")

        if submitted:
            if not name.strip():
                st.error("Name is required.")
            else:
                lid = ds.add_labour(name.strip(), role, contact, daily_wage, str(join_date))
                st.success(f"Added {name} (ID: {lid})")
                st.rerun()

    st.subheader("Current Labour Directory")
    df = ds.load_labour()
    if df.empty:
        st.info("No labourers added yet — use the form above.")
        return

    st.dataframe(df, use_container_width=True)

    c1, c2 = st.columns([2, 1])
    with c1:
        remove_id = st.selectbox(
            "Remove a labourer",
            options=df["LabourID"].tolist(),
            format_func=lambda lid: f"{lid} — {df.loc[df.LabourID == lid, 'Name'].values[0]}",
        )
    with c2:
        st.write("")
        st.write("")
        if st.button("🗑️ Remove Selected"):
            ds.delete_labour(remove_id)
            st.success("Removed.")
            st.rerun()


def _render_attendance_marking():
    df = ds.load_labour()
    if df.empty:
        st.info("Add labourers in the Directory tab first.")
        return

    att_date = st.date_input("Attendance Date", value=date.today(), key="att_date")
    st.caption(f"Marking attendance for {len(df)} labourer(s) on {att_date}")

    statuses = {}
    for _, row in df.iterrows():
        statuses[row["LabourID"]] = st.selectbox(
            f"{row['Name']} ({row['Role']}) — ₹{row['DailyWage']:.0f}/day",
            list(STATUS_WAGE_FACTOR.keys()),
            key=f"status_{row['LabourID']}_{att_date}",
        )

    if st.button("Save Attendance", type="primary"):
        entries = []
        for _, row in df.iterrows():
            status = statuses[row["LabourID"]]
            wage = row["DailyWage"] * STATUS_WAGE_FACTOR[status]
            entries.append({
                "Date": str(att_date), "LabourID": row["LabourID"], "Name": row["Name"],
                "Status": status, "WagePayable": wage,
            })
        ds.mark_attendance(entries)
        st.success(f"Attendance saved for {att_date}.")


def _render_summary():
    att = ds.load_attendance()
    if att.empty:
        st.info("No attendance records yet — mark attendance in the previous tab.")
        return

    att["Date"] = pd.to_datetime(att["Date"])
    st.dataframe(att.sort_values("Date", ascending=False), use_container_width=True)

    c1, c2, c3 = st.columns(3)
    c1.metric("Total Attendance Records", len(att))
    c2.metric("Total Wages Payable", format_currency(att["WagePayable"].sum()))
    today_present = att[(att["Date"] == pd.Timestamp(date.today())) & (att["Status"] != "Absent")]
    c3.metric("Present Today", len(today_present))

    st.subheader("Monthly Wage Summary")
    att["Month"] = att["Date"].dt.to_period("M").astype(str)
    monthly = att.groupby("Month")["WagePayable"].sum().reset_index()
    import plotly.express as px
    fig = px.bar(monthly, x="Month", y="WagePayable")
    fig.update_layout(height=320, margin=dict(t=20, b=10))
    st.plotly_chart(fig, use_container_width=True)

    st.subheader("Attendance Breakdown by Labourer")
    per_labour = att.groupby("Name")["Status"].value_counts().unstack(fill_value=0)
    st.dataframe(per_labour, use_container_width=True)
