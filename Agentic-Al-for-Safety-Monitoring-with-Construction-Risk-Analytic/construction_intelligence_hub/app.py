import streamlit as st
from pathlib import Path

from modules import (
    estimation,
    analytics,
    risk,
    ai_assistant,
    labour,
    compare,
    project_management,
    worker_management,
    material_management,
    equipment,
    reports,
    safety_monitoring,
    site_monitoring,
    settings,
)
from utils.ollama_client import check_ollama_running
from utils import auth


st.set_page_config(
    page_title="Construction Intelligence Hub",
    page_icon="🏗️",
    layout="wide",
)


def load_css():
    css_path = Path(__file__).parent / "assets" / "style.css"
    if css_path.exists():
        st.markdown(f"<style>{css_path.read_text()}</style>", unsafe_allow_html=True)


def main():
    load_css()

    if not auth.is_logged_in():
        render_login_page()
        return
    with st.sidebar:
        st.title("🏗️ Construction Intelligence Hub")
        st.markdown("---")
        page = st.radio(
            "Navigate",
            [
                "🏠 Home",
                "📁 Project Management",
                "👷 Worker Management",
                "🧱 Material Management",
                "🚜 Equipment",
                "📊 Project Analytics",
                "📄 Reports",
                "📷 Safety Monitoring",
                "🗺️ Site Monitoring",
                "🏗️ Cost Estimation",
                "🆚 Compare Options",
                "👷 Labour & Attendance",
                "⚠️ Risk Analysis",
                "🤖 AI Assistant",
                "⚙️ Settings",
            ],
            label_visibility="collapsed",
        )
        st.markdown("---")
        status = "🟢 AI connected" if check_ollama_running() else "🔴 AI not available"
        st.caption(status)
        st.caption("Local AI-powered construction analytics")
        st.markdown("---")
        if st.button("🚪 Logout", key="logout_btn", use_container_width=True):
            auth.logout()
            st.rerun()


    if page == "🏠 Home":
        render_home()
    elif page == "📁 Project Management":
        project_management.render()
    elif page == "👷 Worker Management":
        worker_management.render()
    elif page == "🧱 Material Management":
        material_management.render()
    elif page == "🚜 Equipment":
        equipment.render()
    elif page == "📊 Project Analytics":
        analytics.render()
    elif page == "📄 Reports":
        reports.render()
    elif page == "📷 Safety Monitoring":
        safety_monitoring.render()
    elif page == "🗺️ Site Monitoring":
        site_monitoring.render()
    elif page == "🏗️ Cost Estimation":
        estimation.render()
    elif page == "🆚 Compare Options":
        compare.render()
    elif page == "👷 Labour & Attendance":
        labour.render()
    elif page == "⚠️ Risk Analysis":
        risk.render()
    elif page == "🤖 AI Assistant":
        ai_assistant.render()
    elif page == "⚙️ Settings":
        settings.render()


def render_home():
    st.title("🏗️ Construction Intelligence Hub")
    st.markdown(
        "A single dashboard for **cost estimation**, **project analytics**, "
        "**risk scoring**, and an **AI assistant** powered by a locally-running "
        "AI model — no data leaves your machine."
    )

    c1, c2, c3, c4 = st.columns(4)
    c1.info("**Cost Estimation**\n\nRule-based cost calculator with AI-written summaries.")
    c2.info("**Compare Options**\n\nSide-by-side comparison of structure/quality/location combos.")
    c3.info("**Project Analytics**\n\nUpload project data, see budget & schedule variance.")
    c4.info("**Labour & Attendance**\n\nAdd labourers, mark daily attendance, track wages.")

    c5, c6 = st.columns(2)
    c5.info("**Risk Analysis**\n\nScore risk factors, get an AI mitigation plan.")
    c6.info("**AI Assistant**\n\nChat and analyze RFPs/specs with a local LLM.")

    st.markdown("---")
    st.subheader("Getting started")
    st.markdown(
        "1. Use the sidebar to pick a module.\n"
        "2. For AI features, make sure the local model server is running (`ollama serve`) "
        "and a model is pulled (`ollama pull llama3.1`).\n"
        "3. The sidebar status indicator tells you if AI is reachable."
    )


def render_login_page():
    col1, col2, col3 = st.columns([1, 1.5, 1])
    with col2:
        st.markdown('<div class="login-header">🏗️ Construction<br>Intelligence Hub</div>', unsafe_allow_html=True)
        st.markdown('<div class="login-subtitle">Dashboard Authentication</div>', unsafe_allow_html=True)
        
        tab_signin, tab_signup = st.tabs(["🔑 Sign In", "📝 Sign Up"])
        
        with tab_signin:
            with st.form("signin_form"):
                username_input = st.text_input("Username", placeholder="Enter username", key="signin_user")
                password_input = st.text_input("Password", type="password", placeholder="Enter password", key="signin_pass")
                submit_button = st.form_submit_button("Access Dashboard", use_container_width=True)
                
                if submit_button:
                    if auth.login(username_input, password_input):
                        st.success("🔓 Access Granted! Redirecting...")
                        st.rerun()
                    else:
                        st.error("❌ Invalid Username or Password")
                        
        with tab_signup:
            with st.form("signup_form"):
                st.caption("Create a new user account below:")
                new_user = st.text_input("Choose Username", placeholder="Enter new username", key="signup_user")
                new_pass = st.text_input("Choose Password", type="password", placeholder="Enter password (min 6 chars)", key="signup_pass")
                confirm_pass = st.text_input("Confirm Password", type="password", placeholder="Re-enter password", key="signup_confirm")
                submit_reg = st.form_submit_button("Create Account", use_container_width=True)
                
                if submit_reg:
                    if new_pass != confirm_pass:
                        st.error("❌ Passwords do not match.")
                    else:
                        success, msg = auth.register_user(new_user, new_pass)
                        if success:
                            st.success(msg)
                        else:
                            st.error(f"❌ {msg}")
        
        st.info(
            "ℹ️ **Account Access:**\n"
            "Log in to your dashboard using your user profile. If this is a fresh setup, you can log in with:\n"
            "* **Username:** `admin` \n"
            "* **Password:** `password123`  \n"
            "Or use the **Sign Up** tab to register a custom account."
        )
        
        st.markdown('<div class="login-footer">Construction Intelligence Hub &copy; 2026. All rights reserved.</div>', unsafe_allow_html=True)



if __name__ == "__main__":
    main()

