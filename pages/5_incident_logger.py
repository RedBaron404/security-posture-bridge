import streamlit as st
import pandas as pd
import PyPDF2
from docx import Document as DocxDocument
import re
from datetime import datetime
from src.auth import require_auth
from src.db import add_incident, get_recent_incidents

require_auth()

st.title("📝 Incident Logger & Parser")
st.markdown("Track structured security incidents or parse them directly from threat intelligence/AAR reports.")

# Helper functions for Parsing
def extract_text(uploaded_file):
    text = ""
    if uploaded_file.name.endswith(".pdf"):
        reader = PyPDF2.PdfReader(uploaded_file)
        for page in reader.pages:
            text += page.extract_text() + " "
    elif uploaded_file.name.endswith(".docx"):
        doc = DocxDocument(uploaded_file)
        for para in doc.paragraphs:
            text += para.text + "\n"
    else:
        text = str(uploaded_file.read(), "utf-8", errors='ignore')
    return text

def parse_incident_fields(text):
    """
    Rudimentary Regex extraction for suggesting form fields based on common phrasing.
    """
    suggestions = {
        "date": datetime.today().date(),
        "type": "Malware",
        "root_cause": "",
        "remediation": ""
    }
    
    # Very basic parsing heuristics
    if "phishing" in text.lower():
        suggestions["type"] = "Phishing"
    elif "ransomware" in text.lower():
        suggestions["type"] = "Ransomware"
        
    date_match = re.search(r'\d{4}-\d{2}-\d{2}', text)
    if date_match:
         try:
            suggestions["date"] = datetime.strptime(date_match.group(), "%Y-%m-%d").date()
         except: pass

    # Assume paragraphs following bold keywords might contain context
    cause_match = re.search(r'(?i)(?:root cause|vector):?\s*(.+?)(?=\n|$)', text)
    if cause_match:
         suggestions["root_cause"] = cause_match.group(1).strip()
         
    rem_match = re.search(r'(?i)(?:remediation|action|response):?\s*(.+?)(?=\n|$)', text)
    if rem_match:
         suggestions["remediation"] = rem_match.group(1).strip()
         
    return suggestions

# --- Document Parser Section ---
st.markdown("### Auto-Parse from Document")
st.caption("Upload a PDF or Word document to auto-fill the incident fields below.")
uploaded_file = st.file_uploader("Upload Post-Incident Report", type=["pdf", "docx", "txt"])

# Default Form State
default_date = datetime.today().date()
default_type = "Other"
default_cause = ""
default_remediation = ""

# Auto-parse execution
if uploaded_file is not None:
    try:
        raw_text = extract_text(uploaded_file)
        parsed = parse_incident_fields(raw_text)
        
        default_date = parsed["date"]
        default_type = parsed["type"]
        default_cause = parsed["root_cause"]
        default_remediation = parsed["remediation"]
        
        st.success("Document analyzed successfully. Review the suggested fields below.")
    except Exception as e:
         st.error(f"Error parsing document: {e}")

st.divider()

# --- Manual Form Logging Section ---
st.markdown("### Incident Details")

with st.form("incident_logger_form"):
    inc_date = st.date_input("Date of Incident", value=default_date)
    inc_type = st.selectbox(
        "Incident Type", 
        ["Phishing", "Malware", "Ransomware", "Data Exfiltration", "Insider Threat", "Other"],
        index=["Phishing", "Malware", "Ransomware", "Data Exfiltration", "Insider Threat", "Other"].index(default_type) if default_type in ["Phishing", "Malware", "Ransomware", "Data Exfiltration", "Insider Threat", "Other"] else 5
    )
    inc_root_cause = st.text_area("Root Cause Analysis", value=default_cause)
    inc_remed = st.text_area("Remediation / Response Actions", value=default_remediation)
    
    submitted = st.form_submit_button("Log Incident")
    
    if submitted:
        add_incident(inc_date, inc_type, inc_root_cause, inc_remed)
        st.success("Incident logged successfully to the local database!")

# --- Recent Log History ---
st.markdown("### Recent Incident Log")
recent_df = get_recent_incidents()
if not recent_df.empty:
    st.dataframe(recent_df.drop(columns=['id']), use_container_width=True)
else:
    st.info("No incidents logged yet.")
