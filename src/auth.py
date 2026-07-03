import hashlib
import streamlit as st
import os

AUTH_FILE = "db/.auth"

def initialize_auth_state():
    """Initializes authentication state variables in the Streamlit session."""
    if "authenticated" not in st.session_state:
        st.session_state["authenticated"] = False
    if "master_password" not in st.session_state:
        st.session_state["master_password"] = None

def hash_password(password: str) -> str:
    """Hashes a password using SHA-256 for basic verification."""
    return hashlib.sha256(password.encode()).hexdigest()

def is_first_run() -> bool:
    """Checks if the master password has been set yet."""
    return not os.path.exists(AUTH_FILE)

def save_master_password(password: str):
    """Saves the hashed master password to disk."""
    with open(AUTH_FILE, "w") as f:
        f.write(hash_password(password))

def get_stored_hash() -> str:
    """Retrieves the stored password hash."""
    if is_first_run():
        return None
    with open(AUTH_FILE, "r") as f:
        return f.read().strip()

def verify_password(provided_password: str) -> bool:
    """Verifies a provided password against the stored hash."""
    stored = get_stored_hash()
    if not stored:
        return False
    return stored == hash_password(provided_password)

def require_auth():
    """
    Halts execution if the user is not authenticated.
    Used at the top of protected pages.
    """
    if not st.session_state.get("authenticated", False):
        st.warning("Please log in from the main page to access this dashboard.")
        st.stop()
