"""
Flight Overview Page
Displays SFO airport summary statistics and live departure board
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import sys
import os

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from data_generator import generate_flight_board, AIRLINES


def show():
    st.title("🛫 Flight Overview - San Francisco International Airport")
    st.markdown("### Real-time Airport Operations Dashboard")

    # Current date/time simulation
    current_time = datetime(2024, 6, 15, 14, 30)
    st.info(f"📅 Current Time: {current_time.strftime('%A, %B %d, %Y - %I:%M %p')}")

    # Key metrics row
    st.markdown("### 📊 Today's Operations Summary")
    col1, col2, col3, col4, col5 = st.columns(5)

    with col1:
        st.markdown('<div class="metric-on-time">', unsafe_allow_html=True)
        st.metric("Total Flights", "1,247", "↑ 38 vs yesterday")
        st.markdown('</div>', unsafe_allow_html=True)

    with col2:
        st.markdown('<div class="metric-on-time">', unsafe_allow_html=True)
        st.metric("Passengers", "356,320", "↑ 4.2%")
        st.markdown('</div>', unsafe_allow_html=True)

    with col3:
        st.markdown('<div class="metric-on-time">', unsafe_allow_html=True)
        st.metric("On-Time Rate", "78.3%", "↑ 2.1%")
        st.markdown('</div>', unsafe_allow_html=True)

    with col4:
        st.markdown('<div class="metric-delayed">', unsafe_allow_html=True)
        st.metric("Delayed", "187", "↓ 12")
        st.markdown('</div>', unsafe_allow_html=True)

    with col5:
        st.markdown('<div class="metric-cancelled">', unsafe_allow_html=True)
        st.metric("Cancelled", "8", "↑ 3")
        st.markdown('</div>', unsafe_allow_html=True)

    st.markdown("---")

    # Terminal status and current conditions
    col_left, col_right = st.columns([1, 1])

    with col_left:
        st.markdown("### 🏢 Terminal Status")

        terminals = [
            {"name": "Terminal 1 (Domestic)", "status": "🟢 Operational", "gates": "B1-B27", "current_load": "82%"},
            {"name": "Terminal 2 (Domestic)", "status": "🟢 Operational", "gates": "C1-C14", "current_load": "76%"},
            {"name": "Terminal 3 (United)", "status": "🟡 Busy", "gates": "E1-F22", "current_load": "91%"},
            {"name": "International Terminal", "status": "🟢 Operational", "gates": "A1-A15, G1-G14", "current_load": "79%"},
        ]

        terminal_df = pd.DataFrame(terminals)
        st.dataframe(
            terminal_df,
            use_container_width=True,
            hide_index=True,
            column_config={
                "name": st.column_config.TextColumn("Terminal", width="medium"),
                "status": st.column_config.TextColumn("Status", width="small"),
                "gates": st.column_config.TextColumn("Gates", width="small"),
                "current_load": st.column_config.TextColumn("Current Load", width="small"),
            }
        )

        # Terminal load visualization
        fig = go.Figure(data=[
            go.Bar(
                x=[82, 76, 91, 79],
                y=["Terminal 1", "Terminal 2", "Terminal 3", "Intl Terminal"],
                orientation='h',
                marker=dict(
                    color=[82, 76, 91, 79],
                    colorscale='RdYlGn_r',
                    showscale=False
                ),
                text=[f"{v}%" for v in [82, 76, 91, 79]],
                textposition='inside',
            )
        ])

        fig.update_layout(
            title="Terminal Capacity Utilization",
            xaxis_title="Load %",
            height=250,
            margin=dict(l=0, r=0, t=40, b=0),
            showlegend=False
        )

        st.plotly_chart(fig, use_container_width=True)

    with col_right:
        st.markdown("### 🌤️ Current Airport Conditions")

        conditions = {
            "🛬 Active Runways": "28L/28R (Primary), 01L/01R (Secondary)",
            "👁️ Visibility": "10 miles (Excellent)",
            "💨 Wind Speed": "12 mph from W",
            "🌡️ Temperature": "68°F (20°C)",
            "☁️ Cloud Cover": "Partly Cloudy at 3,500 ft",
            "🌫️ Weather Advisory": "None - Good flying conditions",
        }

        for key, value in conditions.items():
            st.markdown(f"**{key}:** {value}")

        st.markdown("---")

        # Quick weather impact indicator
        col_w1, col_w2, col_w3 = st.columns(3)

        with col_w1:
            st.metric("Wind Impact", "Low", "✅")

        with col_w2:
            st.metric("Visibility", "Excellent", "✅")

        with col_w3:
            st.metric("Fog Risk", "0%", "✅")

    st.markdown("---")

    # Live Departure Board
    st.markdown("### 🛫 Live Departure Board - Next 20 Flights")

    # Add refresh button
    col_refresh1, col_refresh2, col_refresh3 = st.columns([1, 1, 4])
    with col_refresh1:
        if st.button("🔄 Refresh Board"):
            st.rerun()

    with col_refresh2:
        show_all = st.checkbox("Show all terminals", value=True)

    # Generate flight board data
    flight_board = generate_flight_board(current_time)

    # Style the status column
    def color_status(val):
        if val == 'On Time':
            return 'background-color: #d4edda; color: #155724'
        elif val == 'Boarding':
            return 'background-color: #d1ecf1; color: #0c5460'
        elif val == 'Delayed':
            return 'background-color: #fff3cd; color: #856404'
        elif val == 'Departed':
            return 'background-color: #e2e3e5; color: #383d41'
        else:
            return ''

    # Display the board with custom formatting
    st.dataframe(
        flight_board.style.applymap(color_status, subset=['status']),
        use_container_width=True,
        hide_index=True,
        column_config={
            "flight_number": st.column_config.TextColumn("Flight", width="small"),
            "airline": st.column_config.TextColumn("Airline", width="medium"),
            "destination": st.column_config.TextColumn("Destination", width="medium"),
            "scheduled_time": st.column_config.TextColumn("Departure", width="small"),
            "gate": st.column_config.TextColumn("Gate", width="small"),
            "terminal": st.column_config.TextColumn("Terminal", width="small"),
            "status": st.column_config.TextColumn("Status", width="small"),
        },
        height=500
    )

    st.markdown("---")

    # Hourly flight distribution
    st.markdown("### 📈 Today's Flight Distribution by Hour")

    hours = list(range(24))
    # Simulate realistic hourly distribution (more flights in morning and evening)
    flights_by_hour = [
        15, 12, 8, 6, 10, 28, 65, 78, 72, 68,  # 0-9
        64, 62, 58, 55, 60, 64, 68, 75, 82, 78,  # 10-19
        72, 65, 45, 28  # 20-23
    ]

    fig = go.Figure()

    fig.add_trace(go.Bar(
        x=hours,
        y=flights_by_hour,
        name='Flights',
        marker_color='steelblue',
        text=flights_by_hour,
        textposition='outside',
    ))

    # Add average line
    avg_flights = sum(flights_by_hour) / len(flights_by_hour)
    fig.add_hline(y=avg_flights, line_dash="dash", line_color="red",
                  annotation_text=f"Average: {avg_flights:.0f} flights/hour",
                  annotation_position="right")

    fig.update_layout(
        title="Flight Operations by Hour",
        xaxis_title="Hour of Day",
        yaxis_title="Number of Flights",
        height=400,
        showlegend=False,
        xaxis=dict(tickmode='linear', tick0=0, dtick=2)
    )

    st.plotly_chart(fig, use_container_width=True)

    # Airline distribution
    col_chart1, col_chart2 = st.columns(2)

    with col_chart1:
        st.markdown("### 🏢 Today's Flights by Airline (Top 10)")

        airline_flights = pd.DataFrame({
            'Airline': list(AIRLINES.keys())[:10],
            'Flights': [385, 95, 78, 62, 58, 24, 22, 14, 12, 11]
        })

        fig = px.pie(
            airline_flights,
            values='Flights',
            names='Airline',
            hole=0.4,
            color_discrete_sequence=px.colors.qualitative.Set3
        )

        fig.update_traces(textposition='inside', textinfo='percent+label')
        fig.update_layout(height=400, showlegend=False)

        st.plotly_chart(fig, use_container_width=True)

    with col_chart2:
        st.markdown("### 🌍 Domestic vs International")

        flight_types = pd.DataFrame({
            'Type': ['Domestic', 'International'],
            'Flights': [872, 375],
            'Percentage': [69.9, 30.1]
        })

        fig = go.Figure(data=[
            go.Bar(
                x=flight_types['Type'],
                y=flight_types['Flights'],
                text=[f"{f}<br>({p}%)" for f, p in zip(flight_types['Flights'], flight_types['Percentage'])],
                textposition='auto',
                marker_color=['#3498db', '#e74c3c']
            )
        ])

        fig.update_layout(
            title="Flight Distribution by Type",
            height=400,
            showlegend=False,
            yaxis_title="Number of Flights"
        )

        st.plotly_chart(fig, use_container_width=True)

    # Export functionality
    st.markdown("---")
    col_export1, col_export2, col_export3 = st.columns([2, 1, 1])

    with col_export1:
        st.markdown("### 💾 Export Data")

    with col_export2:
        csv = flight_board.to_csv(index=False)
        st.download_button(
            label="📥 Download Departure Board (CSV)",
            data=csv,
            file_name=f"sfo_departures_{current_time.strftime('%Y%m%d_%H%M')}.csv",
            mime="text/csv"
        )
