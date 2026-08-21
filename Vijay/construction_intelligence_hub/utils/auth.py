import os
import sqlite3
import hashlib
import secrets
import streamlit as st

# Path for the database file
DB_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data", "users.db")

def load_env():
    """
    Manually loads .env file if it exists, to avoid external dependencies like python-dotenv.
    """
    current_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    env_path = os.path.join(current_dir, ".env")
    
    if os.path.exists(env_path):
        try:
            with open(env_path, "r", encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith("#"):
                        if "=" in line:
                            key, val = line.split("=", 1)
                            val_clean = val.strip().strip('"').strip("'")
                            os.environ[key.strip()] = val_clean
        except Exception:
            pass

def hash_password(password: str) -> str:
    """
    Hashes a password using PBKDF2-HMAC-SHA256 with a unique salt.
    """
    salt = secrets.token_hex(16)
    dk = hashlib.pbkdf2_hmac('sha256', password.encode('utf-8'), salt.encode('utf-8'), 100000)
    return f"{salt}${dk.hex()}"

def verify_password(stored_password_hash: str, password_to_check: str) -> bool:
    """
    Verifies a password against its PBKDF2-HMAC-SHA256 hash.
    """
    try:
        salt, hash_hex = stored_password_hash.split('$', 1)
        dk = hashlib.pbkdf2_hmac('sha256', password_to_check.encode('utf-8'), salt.encode('utf-8'), 100000)
        return secrets.compare_digest(dk.hex(), hash_hex)
    except Exception:
        return False

def init_db(db_path=DB_PATH):
    """
    Initializes the SQLite database and creates the users table if it doesn't exist.
    Also pre-populates default admin account.
    """
    if db_path != ":memory:":
        db_dir = os.path.dirname(db_path)
        os.makedirs(db_dir, exist_ok=True)
        
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    conn.commit()
    
    # Support loading config-based credentials if defined in .env
    load_env()
    env_username = os.getenv("CIH_USERNAME")
    env_password = os.getenv("CIH_PASSWORD")
    
    # Check if we should seed default admin
    cursor.execute("SELECT COUNT(*) FROM users")
    count = cursor.fetchone()[0]
    if count == 0:
        username = env_username if env_username else "admin"
        password = env_password if env_password else "password123"
        hashed = hash_password(password)
        cursor.execute("INSERT OR IGNORE INTO users (username, password_hash) VALUES (?, ?)", (username, hashed))
        conn.commit()
    else:
        # If env variables are present and user does not exist in DB, seed it
        if env_username and env_password:
            cursor.execute("SELECT id FROM users WHERE username = ?", (env_username,))
            if not cursor.fetchone():
                hashed = hash_password(env_password)
                cursor.execute("INSERT INTO users (username, password_hash) VALUES (?, ?)", (env_username, hashed))
                conn.commit()
                
    conn.close()

def register_user(username_input: str, password_input: str, db_path=None) -> tuple[bool, str]:
    """
    Registers a new user. Returns (success: bool, status_message: str).
    """
    path = db_path if db_path else DB_PATH
    username = username_input.strip()
    
    if not username:
        return False, "Username cannot be empty."
    if not password_input:
        return False, "Password cannot be empty."
    if len(password_input) < 6:
        return False, "Password must be at least 6 characters long."
        
    conn = sqlite3.connect(path)
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT id FROM users WHERE username = ?", (username,))
        if cursor.fetchone():
            conn.close()
            return False, f"Username '{username}' is already taken."
            
        hashed = hash_password(password_input)
        cursor.execute("INSERT INTO users (username, password_hash) VALUES (?, ?)", (username, hashed))
        conn.commit()
        conn.close()
        return True, "Account successfully created! Please switch to the Sign In tab to log in."
    except Exception as e:
        conn.close()
        return False, f"Database error: {str(e)}"

def check_credentials(username_input: str, password_input: str, db_path=None) -> bool:
    """
    Checks if credentials match any user in the database.
    """
    path = db_path if db_path else DB_PATH
    username = username_input.strip()
    
    conn = sqlite3.connect(path)
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT password_hash FROM users WHERE username = ?", (username,))
        row = cursor.fetchone()
        conn.close()
        if row:
            return verify_password(row[0], password_input)
        return False
    except Exception:
        conn.close()
        return False

def is_logged_in() -> bool:
    """
    Checks if the user session is authenticated.
    """
    return st.session_state.get("logged_in", False)

def login(username_input: str, password_input: str, db_path=None) -> bool:
    """
    Logs the user in if credentials match.
    """
    if check_credentials(username_input, password_input, db_path):
        st.session_state["logged_in"] = True
        return True
    return False

def logout():
    """
    Clears authenticated session and resets session memory.
    """
    st.session_state["logged_in"] = False
    if "chat_history" in st.session_state:
        del st.session_state["chat_history"]

# Auto-initialize database on import unless in a test/dry-run context
try:
    init_db(DB_PATH)
except Exception:
    pass
