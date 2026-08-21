"""
=========================================================
Authentication
=========================================================

Provides a simple username/password login screen backed by
the SQLite "users" table (see core/database.py). The rest of
the app is only rendered once st.session_state.authenticated
is True.
"""

import streamlit as st

from core.database import init_db, create_user, verify_user


def render_login():
    """Render the login / create-account screen."""

    st.markdown(
        """
        <div style="text-align:center;padding:50px 0 10px 0;">
        <h1>Agentic AI Safety Monitoring Construction Risk Analytics</h1>
        <p style="color:#6B7280;font-size:16px;">
        Sign in to manage your construction projects
        </p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    col1, col2, col3 = st.columns([1, 1.4, 1])

    with col2:

        with st.container(border=True):

            tab_login, tab_signup = st.tabs(["🔑 Login", "🆕 Create Account"])

            # -------------------------------------------------
            # LOGIN
            # -------------------------------------------------
            with tab_login:

                with st.form("login_form"):

                    username = st.text_input("Username", key="login_username")
                    password = st.text_input(
                        "Password", type="password", key="login_password"
                    )

                    submitted = st.form_submit_button(
                        "Login", use_container_width=True, type="primary"
                    )

                if submitted:
                    if not username or not password:
                        st.error("Please enter both username and password.")
                    else:
                        ok, user = verify_user(username, password)

                        if ok:
                            st.session_state.authenticated = True
                            st.session_state.username = user["username"]
                            st.session_state.full_name = (
                                user["full_name"] or user["username"]
                            )
                            st.success("Login successful. Redirecting...")
                            st.rerun()
                        else:
                            st.error("Invalid username or password.")

            # -------------------------------------------------
            # SIGN UP
            # -------------------------------------------------
            with tab_signup:

                with st.form("signup_form"):

                    new_username = st.text_input("Choose a Username")
                    full_name = st.text_input("Full Name")
                    email = st.text_input("Email (optional)")
                    new_password = st.text_input(
                        "Choose a Password", type="password"
                    )
                    confirm_password = st.text_input(
                        "Confirm Password", type="password"
                    )

                    signup = st.form_submit_button(
                        "Create Account", use_container_width=True
                    )

                if signup:
                    if not new_username or not new_password:
                        st.error("Username and password are required.")
                    elif new_password != confirm_password:
                        st.error("Passwords do not match.")
                    elif len(new_password) < 4:
                        st.error("Password should be at least 4 characters.")
                    else:
                        ok, message = create_user(
                            new_username, new_password, full_name, email
                        )

                        if ok:
                            st.success(message + " You can now log in.")
                        else:
                            st.error(message)

        st.caption(
            "Demo tip: create an account on the 'Create Account' tab, "
            "then log in with the same username and password."
        )


def require_login():
    """
    Gate the whole app behind the login screen.
    Call this at the very top of main.py, right after
    configure_page(). Stops execution until the user logs in.
    """

    init_db()

    if "authenticated" not in st.session_state:
        st.session_state.authenticated = False

    if not st.session_state.authenticated:
        render_login()
        st.stop()


def render_logout_button():
    """Small logout control, meant to be placed in the sidebar."""

    name = st.session_state.get("full_name", "User")
    st.caption(f"Logged in as **{name}**")

    if st.button("🚪 Logout", use_container_width=True, key="logout_btn"):
        for key in ("authenticated", "username", "full_name"):
            st.session_state.pop(key, None)
        st.rerun()
