"""
frontend/pages/site_safety.py
----------------------------
Standalone page for the Site Safety AI Chatbot (Feature 5).
"""
import streamlit as st
from frontend.utils.api_client import APIClient


def show_site_safety_page():
    st.markdown(
        '# <span class="gradient-text">⚠️ Site Safety AI Advisor</span>',
        unsafe_allow_html=True,
    )
    st.markdown(
        '<p class="subtitle-text">Acts as the Site Safety Officer. Provide PPE checks, identify trench excavation shoring, view emergency protocols, and report safety hazards.</p>',
        unsafe_allow_html=True,
    )

    # 1. Panic Button State Control
    if "safety_panic_active" not in st.session_state:
        st.session_state["safety_panic_active"] = False

    # Red Emergency Warning Banner if Panic is Active
    if st.session_state["safety_panic_active"]:
        st.markdown(
            """
            <div style="background-color: #EF4444; border: 2px solid #B91C1C; border-radius: 12px; padding: 20px; color: white; margin-bottom: 25px; animation: pulse 2s infinite;">
                <h3 style="margin: 0; color: white;">🚨 EMERGENCY PANIC MODE ACTIVE</h3>
                <p style="margin: 5px 0 0 0; font-size: 1.1rem;">
                    Immediate safety protocol engaged. Do not panic. Read the instructions below, evacuate the danger zone, and notify onsite safety supervisors immediately.
                </p>
            </div>
            """,
            unsafe_allow_html=True
        )

    # Split layout: Chatbot Workspace on left; Checklists/Hazard Reports on right
    col_chat, col_details = st.columns([1.2, 1])

    with col_details:
        # A. PPE Activity Checklists
        st.markdown("### 📋 Activity Safety Checklist")
        activity = st.selectbox(
            "Select Site Activity:",
            ["Scaffolding", "Excavation", "Welding", "Electrical", "Concrete"]
        )
        
        checklist = []
        try:
            checklist = APIClient.get_safety_checklist(activity)
        except Exception as e:
            st.error(str(e))
            
        for item in checklist:
            st.markdown(f"✔ {item}")

        st.markdown("---")

        # B. File Hazard Report Form
        st.markdown("### ⚠️ Log Safety Hazard")
        with st.form("hazard_report_form", clear_on_submit=True):
            description = st.text_area("Hazard Description", placeholder="e.g. Workers operating at 15ft without safety lines.")
            severity = st.selectbox("Severity Level", ["Low Warning", "Medium Risk", "High Critical"])
            submit_report = st.form_submit_button("Submit Hazard Log", type="primary")

        if submit_report:
            if len(description.strip()) < 5:
                st.error("Please enter a descriptive hazard explanation (minimum 5 characters).")
            else:
                try:
                    APIClient.report_safety_hazard(description.strip(), severity)
                    st.success("Hazard report logged persistently and flagged in supervisor dashboard audits.")
                    st.rerun()
                except Exception as e:
                    st.error(str(e))

        st.markdown("---")

        # C. Emergency SOP Accordions
        st.markdown("### 📞 Emergency SOP Procedures")
        sops = ["Fire Outbreak", "Gas Leak / Spill", "Medical / Injury", "Structural Collapse"]
        for sop in sops:
            with st.expander(f"Protocol: {sop}"):
                try:
                    sop_data = APIClient.get_emergency_sop(sop)
                    st.write(sop_data.get("sop", "No instructions available."))
                except Exception as e:
                    st.error(str(e))

    with col_chat:
        st.markdown("### 🛡️ Safety Officer Workspace")
        
        # Panic Trigger Button
        btn_label = "🚨 DEACTIVATE PANIC CALL" if st.session_state["safety_panic_active"] else "🚨 EMERGENCY HELP PANIC CALL"
        btn_type = "secondary" if st.session_state["safety_panic_active"] else "primary"
        
        if st.button(btn_label, key="panic_button_click", use_container_width=True):
            st.session_state["safety_panic_active"] = not st.session_state["safety_panic_active"]
            # Trigger custom audit log on panic engagement
            status_act = "Engaged" if st.session_state["safety_panic_active"] else "Resolved"
            try:
                APIClient.log_dashboard_activity("PANIC_ALERT", f"Emergency Safety Panic {status_act} by user.")
            except Exception:
                pass
            st.rerun()

        # Chat history local state
        history_key = "safety_assistant_chat_history"
        if history_key not in st.session_state:
            st.session_state[history_key] = [
                {"role": "assistant", "content": "I am the Site Safety Officer. Ask me about PPE checks, OSHA scaffolding heights, or trench excavation standards."}
            ]

        chat_container = st.container(height=350)
        with chat_container:
            for msg in st.session_state[history_key]:
                avatar = "👷 Worker" if msg["role"] == "user" else "🛡️ Safety Lead"
                color = "#FF8C00" if msg["role"] == "assistant" else "grey"
                border = "1px solid rgba(239, 68, 68, 0.4)" if st.session_state["safety_panic_active"] else f"1px solid {color}"
                
                st.markdown(
                    f"""
                    <div style='border-left: 3px solid {color}; padding-left: 10px; margin-bottom: 12px;'>
                        <b>{avatar}</b><br/>
                        {msg['content']}
                    </div>
                    """,
                    unsafe_allow_html=True
                )

        # Message input
        placeholder_text = "e.g. Help! A worker has fallen and is bleeding!" if st.session_state["safety_panic_active"] else "e.g. Scaffolding inspection guidelines..."
        with st.form("safety_chat_form", clear_on_submit=True):
            user_msg = st.text_input("Ask Safety Officer:", placeholder=placeholder_text)
            submit_msg = st.form_submit_button("Send Query", type="primary")

        if submit_msg and user_msg.strip():
            # Add user message
            st.session_state[history_key].append({"role": "user", "content": user_msg.strip()})
            
            with st.spinner("Analyzing site parameters and safety standards..."):
                try:
                    reply = APIClient.send_safety_chat(user_msg.strip(), is_emergency=st.session_state["safety_panic_active"])
                    st.session_state[history_key].append({"role": "assistant", "content": reply["response"]})
                except Exception as e:
                    st.session_state[history_key].append({"role": "assistant", "content": f"Error: {str(e)}"})
            st.rerun()
