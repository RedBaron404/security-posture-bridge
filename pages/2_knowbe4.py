import streamlit as st
import pandas as pd
from src.auth import require_auth
from src.parsers.phishing-training import parse_knowbe4_csv

require_auth()

st.title("🎣 Phishing-Training Dashboard")
st.markdown("Upload a Phishing or Training export CSV to automatically parse its historical metrics into the unified database.")

# Important: Streamlit clears the memory buffer when the widget is re-rendered or the file is removed, 
# ensuring no caching of sensitive CSVs between sessions.
uploaded_file = st.file_uploader("Upload Phishing-Training CSV Export", type=["csv"])

if uploaded_file is not None:
    # Adding a safety check before parsing
    if st.button("Parse to Database", type="primary"):
        with st.spinner("Processing CSV payload..."):
            success, msg = parse_knowbe4_csv(uploaded_file)
            
            if success:
                st.success(msg)
                # To clear the uploader instantly, you can rerun the page
                if st.button("Acknowledge & Clear"):
                    st.rerun()
            else:
                st.error(msg)
                
st.divider()

# In V3, dashboards could eventually query the `db.py` to show specific vendor drill-downs,
# but for now we focus on uploading and relying on the Overview grade chart.
st.info("Upload standard exports from the Phishing-Training console. Look for 'Phish-prone Percentage' or 'Training Completion' data.")
