import streamlit as st
import pandas as pd
from src.auth import require_auth
from src.parsers.security-portal import parse_mdr_csv

require_auth()

st.title("🛡️ Security-Portal MDR Dashboard")
st.markdown("Upload an Security-Portal Atlas CSV export to parse its historical incident alerts into the unified database.")

# Important: Streamlit clears the memory buffer when the widget is re-rendered or the file is removed, 
# ensuring no caching of sensitive CSVs between sessions.
uploaded_file = st.file_uploader("Upload Security-Portal Atlas CSV Export", type=["csv"])

if uploaded_file is not None:
    # Adding a safety check before parsing
    if st.button("Parse to Database", type="primary"):
        with st.spinner("Processing CSV payload..."):
            success, msg = parse_mdr_csv(uploaded_file)
            
            if success:
                st.success(msg)
                # To clear the uploader instantly, you can rerun the page
                if st.button("Acknowledge & Clear"):
                    st.rerun()
            else:
                st.error(msg)
                
st.divider()

st.info("Upload standard export reports from the Security-Portal Atlas console. It uses the alert count per day to track active incidents.")
