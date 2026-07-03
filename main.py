import streamlit as st
from src.auth import initialize_auth_state, verify_password, is_first_run, save_master_password

# Set page config globally
st.set_page_config(page_title="Sentinel Security", page_icon="🛡️", layout="wide")

initialize_auth_state()

# --- Login & Setup Logic ---
if not st.session_state["authenticated"]:
    st.title("🛡️ Sentinel Security Posture")
    
    if is_first_run():
        st.markdown("### Initial Validation Setup")
        st.info("Welcome to Sentinel. Please securely set your Master Password. This password will be used to encrypt all local integration API keys.")
        with st.form("setup_form"):
            new_password = st.text_input("Create Master Password", type="password")
            confirm_password = st.text_input("Confirm Master Password", type="password")
            submit = st.form_submit_button("Initialize Database")
            
            if submit:
                if len(new_password) < 8:
                    st.error("Password must be at least 8 characters.")
                elif new_password != confirm_password:
                    st.error("Passwords do not match!")
                else:
                    save_master_password(new_password)
                    st.session_state["authenticated"] = True
                    st.session_state["master_password"] = new_password
                    st.success("Master password securely saved!")
                    st.rerun()
    else:
        st.markdown("### Authentication Required")
        with st.form("login_form"):
            password = st.text_input("Master Password", type="password")
            submit = st.form_submit_button("Login")
            
            if submit:
                if verify_password(password):
                    st.session_state["authenticated"] = True
                    st.session_state["master_password"] = password  # Store volatile memory for deriving Vault decryption key
                    st.success("Authenticated successfully.")
                    st.rerun()
                else:
                    st.error("Invalid password provided.")
    st.stop()  # Do not build the rest of the app if not authenticated

# --- Main Navigation (Requires Streamlit 1.36+) ---

overview_page = st.Page("pages/1_overview.py", title="Executive Overview", icon="🏠", default=True)
knowbe4_page = st.Page("pages/2_knowbe4.py", title="Phishing-Training Dashboard", icon="🎣")
mdr_page = st.Page("pages/3_mdr-portal.py", title="Security-Portal MDR Dashboard", icon="🛡️")
google_page = st.Page("pages/4_google.py", title="Google Workspace Security", icon="📧")
incident_page = st.Page("pages/5_incident_logger.py", title="Incident Logger & Parser", icon="📝")

# Define the persistent sidebar structure (Capitalized)
pg = st.navigation(
    {
        "DASHBOARDS": [overview_page],
        "SOURCE INTEGRATIONS": [knowbe4_page, mdr_page, google_page],
        "TOOLS": [incident_page]
    }
)

# Render the selected page
pg.run()
