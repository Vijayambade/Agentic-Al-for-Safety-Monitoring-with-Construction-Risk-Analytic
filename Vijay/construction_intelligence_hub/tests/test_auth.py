import pytest
from unittest.mock import patch
import os
from utils import auth

@pytest.fixture(autouse=True)
def setup_test_db():
    """
    Fixture to automatically redirect database access to a temporary file-backed test DB
    for every test, ensuring local database isolation and clean teardown.
    """
    test_db_path = os.path.join(os.path.dirname(__file__), "test_users.db")
    if os.path.exists(test_db_path):
        try:
            os.remove(test_db_path)
        except Exception:
            pass
            
    original_db = auth.DB_PATH
    auth.DB_PATH = test_db_path
    auth.init_db(test_db_path)
    
    yield
    
    auth.DB_PATH = original_db
    if os.path.exists(test_db_path):
        try:
            os.remove(test_db_path)
        except Exception:
            pass

@patch("utils.auth.st")
def test_default_credentials(mock_st):
    # Default admin credentials seeded in init_db
    assert auth.check_credentials("admin", "password123") is True
    assert auth.check_credentials("wrong", "password123") is False
    assert auth.check_credentials("admin", "wrong") is False

@patch("utils.auth.st")
def test_login_success(mock_st):
    mock_st.session_state = {}
    
    # Try logging in with correct credentials
    success = auth.login("admin", "password123")
    assert success is True
    assert mock_st.session_state["logged_in"] is True

@patch("utils.auth.st")
def test_login_failure(mock_st):
    mock_st.session_state = {}
    
    # Try logging in with wrong credentials
    success = auth.login("admin", "wrong")
    assert success is False
    assert mock_st.session_state.get("logged_in") is not True

@patch("utils.auth.st")
def test_logout(mock_st):
    mock_st.session_state = {"logged_in": True, "chat_history": [{"role": "system"}]}
    
    auth.logout()
    assert mock_st.session_state["logged_in"] is False
    assert "chat_history" not in mock_st.session_state

@patch("utils.auth.st")
def test_register_user_success(mock_st):
    # Registering Bob
    success, msg = auth.register_user("bob_builder", "securepass123")
    assert success is True
    assert "successfully created" in msg
    
    # Verify Bob can now log in
    assert auth.check_credentials("bob_builder", "securepass123") is True

@patch("utils.auth.st")
def test_register_user_duplicate(mock_st):
    # Register admin (which already exists by default seeding)
    success, msg = auth.register_user("admin", "newpassword123")
    assert success is False
    assert "already taken" in msg

@patch("utils.auth.st")
def test_register_user_validation(mock_st):
    # Empty username
    success, msg = auth.register_user("", "somepassword")
    assert success is False
    assert "cannot be empty" in msg
    
    # Empty password
    success, msg = auth.register_user("someone", "")
    assert success is False
    assert "cannot be empty" in msg
    
    # Short password
    success, msg = auth.register_user("someone", "12345")
    assert success is False
    assert "at least 6 characters" in msg

@patch("utils.auth.st")
def test_custom_credentials_seed(mock_st):
    # Mock environment variables to verify customized initial seeding
    with patch.dict(os.environ, {"CIH_USERNAME": "custom_user", "CIH_PASSWORD": "custom_password"}):
        test_db_path = os.path.join(os.path.dirname(__file__), "test_custom_users.db")
        if os.path.exists(test_db_path):
            try:
                os.remove(test_db_path)
            except Exception:
                pass
        
        auth.init_db(test_db_path)
        assert auth.check_credentials("custom_user", "custom_password", db_path=test_db_path) is True
        
        if os.path.exists(test_db_path):
            try:
                os.remove(test_db_path)
            except Exception:
                pass
