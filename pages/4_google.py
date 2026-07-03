import streamlit as st
import pandas as pd
from src.auth import require_auth
from src.parsers.google import parse_google_csv

require_auth()

st.title("📧 Google Workspace Security")
st.markdown("Upload a Google Workspace Admin Alerts CSV export to parse its historical alerts into the unified database.")

# Important: Streamlit clears the memory buffer when the widget is re-rendered or the file is removed, 
# ensuring no caching of sensitive CSVs between sessions.
uploaded_file = st.file_uploader("Upload Google Workspace CSV Export", type=["csv"])

if uploaded_file is not None:
    # Adding a safety check before parsing
    if st.button("Parse to Database", type="primary"):
        with st.spinner("Processing CSV payload..."):
            success, msg = parse_google_csv(uploaded_file)
            
            if success:
                st.success(msg)
                # To clear the uploader instantly, you can rerun the page
                if st.button("Acknowledge & Clear"):
                    st.rerun()
            else:
                st.error(msg)
                
st.divider()

st.info("Upload standard export reports from the Google Workspace Admin Alert Center to log total critical alerts per day.")
