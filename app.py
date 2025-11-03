"""
SFO Flight Performance and On-Time Analytics Platform
Multi-page Streamlit application for comprehensive flight analytics
"""

import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime

# Page configuration
st.set_page_config(
    page_title="SFO Flight Analytics",
    page_icon="✈️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
<style>
    .main {
        padding: 0rem 1rem;
    }
    .stMetric {
        background-color: #f0f2f6;
        padding: 10px;
        border-radius: 5px;
    }
    .metric-on-time {
        background-color: #d4edda;
        padding: 15px;
        border-radius: 5px;
        border-left: 5px solid #28a745;
    }
    .metric-delayed {
        background-color: #fff3cd;
        padding: 15px;
        border-radius: 5px;
        border-left: 5px solid #ffc107;
    }
    .metric-cancelled {
        background-color: #f8d7da;
        padding: 15px;
        border-radius: 5px;
        border-left: 5px solid #dc3545;
    }
    h1 {
        color: #1f4788;
    }
    h2 {
        color: #2e5c8a;
    }
    .sidebar .sidebar-content {
        background-color: #f8f9fa;
    }
    div[data-testid="stDataFrame"] {
        font-size: 12px;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'current_page' not in st.session_state:
    st.session_state.current_page = 'Flight Overview'

if 'filter_preferences' not in st.session_state:
    st.session_state.filter_preferences = {}

if 'bookmarked_views' not in st.session_state:
    st.session_state.bookmarked_views = []

# Sidebar navigation
with st.sidebar:
    st.title("✈️ SFO Analytics")
    st.markdown("---")

    # Page selection
    pages = [
        "Flight Overview",
        "On-Time Performance",
        "Weather Impact Analysis",
        "Airline Comparison",
        "Delay Predictor",
        "Advanced Analytics"
    ]

    st.session_state.current_page = st.radio(
        "Navigation",
        pages,
        index=pages.index(st.session_state.current_page)
    )

    st.markdown("---")

    # Quick stats in sidebar
    st.subheader("📊 Quick Stats")
    col1, col2 = st.columns(2)
    with col1:
        st.metric("Today", "1,247", "↑ 3.2%")
    with col2:
        st.metric("On-Time", "78.3%", "↑ 2.1%")

    st.markdown("---")

    # About section
    with st.expander("ℹ️ About"):
        st.write("""
        **SFO Flight Analytics Platform**

        Comprehensive analytics for San Francisco International Airport
        flight operations and on-time performance.

        Data: 2024 Full Year
        Updated: Real-time simulation
        """)

    # Settings
    with st.expander("⚙️ Settings"):
        st.checkbox("Real-time mode", value=False, key='realtime_mode')
        st.slider("Alert threshold (%)", 50, 90, 70, key='alert_threshold')
        st.checkbox("Show animations", value=True, key='show_animations')

# Main content area
if st.session_state.current_page == "Flight Overview":
    from pages import flight_overview
    flight_overview.show()

elif st.session_state.current_page == "On-Time Performance":
    from pages import ontime_performance
    ontime_performance.show()

elif st.session_state.current_page == "Weather Impact Analysis":
    from pages import weather_impact
    weather_impact.show()

elif st.session_state.current_page == "Airline Comparison":
    from pages import airline_comparison
    airline_comparison.show()

elif st.session_state.current_page == "Delay Predictor":
    from pages import delay_predictor
    delay_predictor.show()

elif st.session_state.current_page == "Advanced Analytics":
    from pages import advanced_analytics
    advanced_analytics.show()
