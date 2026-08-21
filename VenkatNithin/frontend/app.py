"""
frontend/app.py
---------------
Streamlit entry point for the Construction Intelligent Hub application.
"""
import os
import streamlit as st

# Set page configurations (Must be the first Streamlit command)
st.set_page_config(
    page_title="Construction Intelligent Hub",
    page_icon="🏗️",
    layout="wide",
    initial_sidebar_state="expanded",
)

from dotenv import load_dotenv

# Load environment variables
load_dotenv()

from frontend.utils.api_client import APIClient

# ---------------------------------------------------------------------------
# Load Custom CSS Styles
# ---------------------------------------------------------------------------
def load_custom_css():
    css_path = os.path.join(os.path.dirname(__file__), "assets", "style.css")
    if os.path.exists(css_path):
        try:
            with open(css_path, "r", encoding="utf-8") as f:
                css_content = f.read()
                st.markdown(f"<style>{css_content}</style>", unsafe_allow_html=True)
        except Exception as e:
            st.error(f"Error loading CSS: {str(e)}")


load_custom_css()

# Initialize session state variables
if "authenticated" not in st.session_state:
    st.session_state["authenticated"] = False
if "auth_screen" not in st.session_state:
    st.session_state["auth_screen"] = "login"
if "temp_email" not in st.session_state:
    st.session_state["temp_email"] = ""
if "user_role" not in st.session_state:
    st.session_state["user_role"] = None
if "user_email" not in st.session_state:
    st.session_state["user_email"] = None
if "access_token" not in st.session_state:
    st.session_state["access_token"] = None
if "user_profile" not in st.session_state:
    st.session_state["user_profile"] = None

# Sidebar branding & settings
st.sidebar.markdown(
    '# <span style="color: #FF8C00;">🏗️ Hub Settings</span>',
    unsafe_allow_html=True,
)
theme_mode = st.sidebar.selectbox(
    "Theme Aesthetic", ["Modern Dark Mode", "Refined Light Mode"]
)
theme_class = "light-theme" if "Light" in theme_mode else ""

if "Light" in theme_mode:
    st.markdown(
        """
        <style>
        :root, .stApp {
            --background-color: #f5f7fa !important;
            --secondary-background-color: #e4e8f0 !important;
            --text-color: #1f2937 !important;
        }
        .stApp {
            background: linear-gradient(135deg, #f5f7fa 0%, #e4e8f0 100%) !important;
            color: #1f2937 !important;
        }
        .auth-card {
            background: rgba(255, 255, 255, 0.85) !important;
            border-color: rgba(255, 140, 0, 0.12) !important;
            color: #1f2937 !important;
            box-shadow: 0 8px 32px 0 rgba(31, 38, 135, 0.08) !important;
        }
        .stat-card {
            background: linear-gradient(135deg, #ffffff 0%, #f0f2f6 100%) !important;
            border-color: rgba(255, 140, 0, 0.2) !important;
        }
        .stat-title {
            color: #4b5563 !important;
        }
        .stat-value {
            color: #1f2937 !important;
        }
        .subtitle-text {
            color: #4b5563 !important;
        }
        div[data-baseweb="input"] {
            background-color: #ffffff !important;
            border-color: rgba(255, 140, 0, 0.2) !important;
            color: #1f2937 !important;
        }
        div[data-baseweb="select"] {
            background-color: #ffffff !important;
            color: #1f2937 !important;
        }
        .stMarkdown p, .stMarkdown li, .stMarkdown span {
            color: #1f2937 !important;
        }
        section[data-testid="stSidebar"] {
            background-color: #f0f2f6 !important;
        }
        section[data-testid="stSidebar"] * {
            color: #1f2937 !important;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )

active_page = "📊 Role Dashboard"
if st.session_state.get("authenticated", False):
    st.sidebar.markdown("---")
    st.sidebar.markdown("### 🧭 Navigation")
    active_page = st.sidebar.radio(
        "Select Page View",
        ["📊 Role Dashboard", "🤖 AI Construction Assistant", "📂 Document Analyzer", "📐 Material Estimation", "⚠️ Site Safety Assistant", "📷 PPE Detection & Cam", "📅 Project Scheduling AI", "🚜 Equipment Telematics", "📦 Smart Site Inventory", "♻️ Site Waste Management", "🔊 Noise & Decibel Monitoring", "💨 Air Quality & Gas", "💧 Water Flow & Leakage", "🏗️ Structural Health & Vibration", "⚡ Energy & Power Monitoring", "⛈️ Weather Hazards Predictor"]
    )

# Helper to check active status and profile on start
if st.session_state["authenticated"] and not st.session_state["user_profile"]:
    try:
        APIClient.get_me()
    except Exception:
        # Session expired or backend down
        st.session_state["authenticated"] = False
        st.session_state["access_token"] = None

# Wrap content in a CSS container for theme support
st.markdown(f'<div class="{theme_class} fade-in-ui">', unsafe_allow_html=True)

# ---------------------------------------------------------------------------
# Unauthenticated Navigation
# ---------------------------------------------------------------------------
if not st.session_state["authenticated"]:
    # Application Title
    st.markdown(
        '# <span class="gradient-text">Construction Intelligent Hub</span>',
        unsafe_allow_html=True,
    )
    st.markdown(
        '<p class="subtitle-text">AI-Powered Construction Management & Intelligent Hiring Platform</p>',
        unsafe_allow_html=True,
    )

    # 1. Login Screen
    if st.session_state["auth_screen"] == "login":
        st.markdown('<div class="auth-card">', unsafe_allow_html=True)
        st.subheader("Sign In")

        login_email = st.text_input(
            "Email Address", value=st.session_state["temp_email"]
        )
        login_password = st.text_input("Password", type="password")
        remember_me = st.checkbox("Remember Me on this device", value=False)

        col1, col2 = st.columns([1, 1])
        with col1:
            if st.button("Log In", type="primary", use_container_width=True):
                if not login_email or not login_password:
                    st.error("Please enter both email and password.")
                else:
                    try:
                        APIClient.login(
                            login_email, login_password, remember_me
                        )
                        st.session_state["temp_email"] = ""
                        st.success("Successfully logged in!")
                        st.rerun()
                    except Exception as e:
                        err_msg = str(e)
                        st.error(err_msg)
                        # If email not verified, direct to OTP verification
                        if "not verified" in err_msg.lower():
                            st.session_state["temp_email"] = login_email
                            st.session_state["auth_screen"] = "verify_otp"
                            st.info("Redirecting to OTP verification page...")
                            st.rerun()
        with col2:
            if st.button(
                "Verify Code / OTP", use_container_width=True
            ):
                st.session_state["auth_screen"] = "verify_otp"
                st.rerun()

        st.markdown("---")
        c1, c2 = st.columns([1, 1])
        with c1:
            if st.button("Register New Account", use_container_width=True):
                st.session_state["auth_screen"] = "register"
                st.rerun()
        with c2:
            if st.button("Forgot Password?", use_container_width=True):
                st.session_state["auth_screen"] = "forgot_password"
                st.rerun()
        st.markdown("</div>", unsafe_allow_html=True)

    # 2. Registration Screen
    elif st.session_state["auth_screen"] == "register":
        st.markdown('<div class="auth-card">', unsafe_allow_html=True)
        st.subheader("Create Account")

        reg_email = st.text_input("Email Address")
        reg_first_name = st.text_input("First Name")
        reg_last_name = st.text_input("Last Name")

        roles_list = [
            "Admin",
            "Engineer",
            "Contractor",
            "Worker",
            "HR",
            "Client",
            "Supplier",
            "Project Manager",
            "Safety Officer",
            "Site Supervisor",
            "Volunteer",
        ]
        reg_role = st.selectbox("Your Project Role", roles_list)

        reg_password = st.text_input("Password", type="password")
        reg_confirm = st.text_input("Confirm Password", type="password")

        if st.button("Register", type="primary", use_container_width=True):
            if not reg_email or not reg_password:
                st.error("Email and Password are required.")
            elif reg_password != reg_confirm:
                st.error("Passwords do not match.")
            else:
                try:
                    APIClient.register(
                        email=reg_email,
                        password=reg_password,
                        first_name=reg_first_name,
                        last_name=reg_last_name,
                        role=reg_role,
                    )
                    st.session_state["temp_email"] = reg_email
                    st.session_state["auth_screen"] = "verify_otp"
                    st.success(
                        "Registration submitted! Please verify the 6-digit OTP code sent to your email."
                    )
                    st.rerun()
                except Exception as e:
                    st.error(str(e))

        if st.button("Back to Login", use_container_width=True):
            st.session_state["auth_screen"] = "login"
            st.rerun()
        st.markdown("</div>", unsafe_allow_html=True)

    # 3. OTP Verification Screen
    elif st.session_state["auth_screen"] == "verify_otp":
        st.markdown('<div class="auth-card">', unsafe_allow_html=True)
        st.subheader("Email OTP Verification")

        otp_email = st.text_input(
            "Account Email", value=st.session_state["temp_email"]
        )
        otp_code = st.text_input("6-digit Verification Code (OTP)", max_chars=6)

        # Developer Fallback OTP Display
        if otp_email:
            try:
                dev_res = APIClient.get_developer_otp(otp_email)
                if dev_res and "otp_code" in dev_res and dev_res["otp_code"]:
                    st.info(f"💡 **Simulated active OTP code:** `{dev_res['otp_code']}`")
            except Exception:
                pass

        col1, col2 = st.columns([1, 1])
        with col1:
            if st.button("Verify OTP", type="primary", use_container_width=True):
                if not otp_email or not otp_code:
                    st.error("Email and OTP Code are required.")
                else:
                    try:
                        APIClient.verify_otp(otp_email, otp_code)
                        st.session_state["temp_email"] = otp_email
                        st.session_state["auth_screen"] = "login"
                        st.success(
                            "Account verified successfully! You can now log in."
                        )
                        st.rerun()
                    except Exception as e:
                        st.error(str(e))
        with col2:
            if st.button("Resend Code", use_container_width=True):
                if not otp_email:
                    st.error("Email address is required to resend OTP.")
                else:
                    try:
                        APIClient.resend_otp(otp_email)
                        st.success("A new verification code has been sent.")
                    except Exception as e:
                        st.error(str(e))

        if st.button("Back to Login", use_container_width=True):
            st.session_state["auth_screen"] = "login"
            st.rerun()
        st.markdown("</div>", unsafe_allow_html=True)

    # 4. Forgot Password Screen
    elif st.session_state["auth_screen"] == "forgot_password":
        st.markdown('<div class="auth-card">', unsafe_allow_html=True)
        st.subheader("Forgot Password")
        st.write(
            "Enter your email address and we will send you a 6-digit OTP code to reset your password."
        )

        forgot_email = st.text_input("Email Address")

        if st.button("Send Reset Code", type="primary", use_container_width=True):
            if not forgot_email:
                st.error("Email address is required.")
            else:
                try:
                    APIClient.forgot_password(forgot_email)
                    st.session_state["temp_email"] = forgot_email
                    st.session_state["auth_screen"] = "reset_password"
                    st.success(
                        "If the account exists, a password reset code has been sent."
                    )
                    st.rerun()
                except Exception as e:
                    st.error(str(e))

        if st.button("Back to Login", use_container_width=True):
            st.session_state["auth_screen"] = "login"
            st.rerun()
        st.markdown("</div>", unsafe_allow_html=True)

    # 5. Reset Password Screen
    elif st.session_state["auth_screen"] == "reset_password":
        st.markdown('<div class="auth-card">', unsafe_allow_html=True)
        st.subheader("Reset Password")

        reset_email = st.text_input(
            "Account Email", value=st.session_state["temp_email"]
        )
        reset_otp = st.text_input("Reset OTP Code", max_chars=6)

        # Developer Fallback OTP Display
        if reset_email:
            try:
                dev_res = APIClient.get_developer_otp(reset_email)
                if dev_res and "otp_code" in dev_res and dev_res["otp_code"]:
                    st.info(f"💡 **Simulated active reset OTP code:** `{dev_res['otp_code']}`")
            except Exception:
                pass

        reset_pass = st.text_input("New Password", type="password")
        reset_confirm = st.text_input("Confirm New Password", type="password")

        if st.button("Update Password", type="primary", use_container_width=True):
            if not reset_email or not reset_otp or not reset_pass:
                st.error("All fields are required.")
            elif reset_pass != reset_confirm:
                st.error("Passwords do not match.")
            else:
                try:
                    APIClient.reset_password(
                        reset_email, reset_otp, reset_pass
                    )
                    st.session_state["temp_email"] = reset_email
                    st.session_state["auth_screen"] = "login"
                    st.success(
                        "Password reset complete! Please log in with your new credentials."
                    )
                    st.rerun()
                except Exception as e:
                    st.error(str(e))

        if st.button("Back to Login", use_container_width=True):
            st.session_state["auth_screen"] = "login"
            st.rerun()
        st.markdown("</div>", unsafe_allow_html=True)

# ---------------------------------------------------------------------------
# Authenticated Navigation (Dashboard Placeholder)
# ---------------------------------------------------------------------------
else:
    profile = st.session_state.get("user_profile") or {}
    user_name = (
        f"{profile.get('first_name', '')} {profile.get('last_name', '')}".strip()
    )
    if not user_name:
        user_name = st.session_state["user_email"]

    # Header with User Greeting
    col_title, col_logout = st.columns([4, 1])
    with col_title:
        st.markdown(
            f'# <span class="gradient-text">Construction Intelligent Hub</span>',
            unsafe_allow_html=True,
        )
        st.markdown(
            f'#### Welcome back, {user_name} | Role: **{st.session_state["user_role"]}**',
            unsafe_allow_html=True,
        )
    with col_logout:
        if st.button("Sign Out", type="primary", use_container_width=True):
            APIClient.logout()
            st.success("Successfully logged out.")
            st.rerun()

    st.markdown("---")

    if active_page == "🤖 AI Construction Assistant":
        from frontend.pages import show_construction_assistant_page
        show_construction_assistant_page()
    elif active_page == "📂 Document Analyzer":
        from frontend.pages import show_document_analyzer_page
        show_document_analyzer_page()
    elif active_page == "⚠️ Site Safety Assistant":
        from frontend.pages import show_site_safety_page
        show_site_safety_page()
    elif active_page == "📷 PPE Detection & Cam":
        from frontend.pages import show_safety_monitoring_page
        show_safety_monitoring_page()
    elif active_page == "📅 Project Scheduling AI":
        from frontend.pages import show_schedule_predictor_page
        show_schedule_predictor_page()
    elif active_page == "🚜 Equipment Telematics":
        from frontend.pages import show_telematics_dashboard_page
        show_telematics_dashboard_page()
    elif active_page == "📦 Smart Site Inventory":
        from frontend.pages import show_inventory_manager_page
        show_inventory_manager_page()
    elif active_page == "♻️ Site Waste Management":
        from frontend.pages import show_waste_management_page
        show_waste_management_page()
    elif active_page == "🔊 Noise & Decibel Monitoring":
        from frontend.pages import show_noise_monitoring_page
        show_noise_monitoring_page()
    elif active_page == "💨 Air Quality & Gas":
        from frontend.pages import show_air_quality_page
        show_air_quality_page()
    elif active_page == "💧 Water Flow & Leakage":
        from frontend.pages import show_water_monitoring_page
        show_water_monitoring_page()
    elif active_page == "🏗️ Structural Health & Vibration":
        from frontend.pages import show_structural_monitoring_page
        show_structural_monitoring_page()
    elif active_page == "⚡ Energy & Power Monitoring":
        from frontend.pages import show_energy_monitoring_page
        show_energy_monitoring_page()
    elif active_page == "⛈️ Weather Hazards Predictor":
        from frontend.pages import show_weather_monitoring_page
        show_weather_monitoring_page()
    elif active_page == "📐 Material Estimation":
        from frontend.pages import show_material_estimation_page
        show_material_estimation_page()
    else:
        # Fetch dynamic dashboard stats from backend
        try:
            stats_data = APIClient.get_dashboard_stats()
        except Exception as e:
            st.error(f"Failed to load dashboard metrics: {str(e)}")
            stats_data = None

        if stats_data:
            from frontend.components import render_dashboard
            render_dashboard(stats_data, profile)

st.markdown("</div>", unsafe_allow_html=True)
