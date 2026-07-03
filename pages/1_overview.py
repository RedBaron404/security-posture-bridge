import streamlit as st
import pandas as pd
import plotly.express as px
from src.auth import require_auth
from src.db import get_historical_trends

require_auth()

st.title("🏠 Executive Overview")
st.markdown("Centralized view of the Sentinel Security Posture.")

# Fetch all historical data
all_trends_df = get_historical_trends()

if all_trends_df.empty:
    st.warning("⚠️ No Data Available: Please navigate to the integration pages and upload CSV reports to generate your Posture Grade.")
else:
    # Use the most recent entry for the current grade
    latest_data = all_trends_df.iloc[-1]
    
    live_ppp = latest_data.get("knowbe4_ppp", 0)
    live_esentire = latest_data.get("esentire_active_incidents", 0)
    live_google = latest_data.get("google_alerts_24h", 0)
    
    # Calculation Logic
    human_score = min(live_ppp * 2, 100)
    mdr_score = min(live_esentire * 10, 100)
    admin_score = min(live_google * 2, 100)
    
    # Use the pre-calculated pulse_score if it exists, otherwise calculate it
    weighted_score = latest_data.get("pulse_score", (human_score * 0.35) + (mdr_score * 0.40) + (admin_score * 0.25))
    
    if weighted_score < 15: grade = "A"
    elif weighted_score < 30: grade = "B"
    elif weighted_score < 50: grade = "C"
    elif weighted_score < 75: grade = "D"
    else: grade = "F"

    col1, col2 = st.columns([1, 2])
    
    with col1:
        st.markdown("### Posture Grade")
        st.markdown(f"<h1 style='text-align: center; font-size: 100px; margin-top: 0;'>{grade}</h1>", unsafe_allow_html=True)
        st.caption(f"Calculated Score: {weighted_score:.1f} / 100")
            
    with col2:
        st.markdown(f"### Executive Summary (As of {latest_data['timestamp'].strftime('%Y-%m-%d')})")
        m1, m2, m3 = st.columns(3)
        m1.metric("Avg. Phish Susceptibility", f"{live_ppp}%")
        m2.metric("Active Security-Portal Incidents", live_esentire)
        m3.metric("Workspace Alerts", live_google)

st.divider()

col_trend, col_filter = st.columns([3, 1])
with col_trend:
    st.markdown("### Historical Posture Trend")
with col_filter:
    time_filter = st.selectbox(
        "Time Range",
        ["30 Days", "90 Days", "6 Months", "12 Months", "2 Years", "3 Years", "All Time"],
        index=1
    )

days_map = {
    "30 Days": 30,
    "90 Days": 90,
    "6 Months": 180,
    "12 Months": 365,
    "2 Years": 730,
    "3 Years": 1095,
    "All Time": None
}

trends_df = get_historical_trends(days=days_map[time_filter])

if not trends_df.empty:
    fig = px.line(trends_df, x='timestamp', y='pulse_score', 
                  title='Security Pulse Score Over Time',
                  labels={'pulse_score': 'Weighted Risk Score', 'timestamp': 'Date'},
                  markers=True)
                  
    # Add colored threshold zones mapped to the Letter Grade logic (Lower is Better)
    fig.add_hrect(y0=0, y1=15, line_width=0, fillcolor="green", opacity=0.15, annotation_text="A", annotation_position="top left")
    fig.add_hrect(y0=15, y1=30, line_width=0, fillcolor="yellow", opacity=0.15, annotation_text="B", annotation_position="top left")
    fig.add_hrect(y0=30, y1=50, line_width=0, fillcolor="orange", opacity=0.15, annotation_text="C", annotation_position="top left")
    fig.add_hrect(y0=50, y1=75, line_width=0, fillcolor="red", opacity=0.15, annotation_text="D", annotation_position="top left")
    fig.add_hrect(y0=75, y1=100, line_width=0, fillcolor="black", opacity=0.15, annotation_text="F", annotation_position="top left")
    
    # Fix Y-axis range to always show 0-100 regardless of data points
    fig.update_layout(yaxis_range=[0, 100])
    
    st.plotly_chart(fig, use_container_width=True)
else:
    st.info(f"No historical trends available for the selected range ({time_filter}).")
