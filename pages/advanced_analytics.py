"""
Advanced Analytics Page
Deep-dive analysis of runway utilization, cascade delays, and capacity
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import numpy as np
import sys
import os
from datetime import datetime, timedelta

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from data_generator import get_hourly_data


@st.cache_data
def load_data():
    """Load and cache hourly data"""
    return get_hourly_data()


@st.cache_data
def generate_runway_data():
    """Generate runway utilization data"""
    hours = list(range(24))
    data = []

    for hour in hours:
        # Runway selection based on wind and time
        # 28L/28R are primary (westerly operations), 01L/01R for easterly
        base_28 = 75  # Base percentage for 28L/28R
        base_01 = 25  # Base percentage for 01L/01R

        # More easterly operations at night
        if 0 <= hour < 6:
            usage_28 = base_28 - 15
            usage_01 = base_01 + 15
        else:
            usage_28 = base_28 + np.random.uniform(-5, 5)
            usage_01 = base_01 + np.random.uniform(-5, 5)

        # Normalize
        total = usage_28 + usage_01
        usage_28 = (usage_28 / total) * 100
        usage_01 = (usage_01 / total) * 100

        data.append({
            'hour': hour,
            '28L/28R': round(usage_28, 1),
            '01L/01R': round(usage_01, 1)
        })

    return pd.DataFrame(data)


@st.cache_data
def generate_gate_turnaround():
    """Generate gate turnaround time data"""
    terminals = ['Terminal 1', 'Terminal 2', 'Terminal 3', 'International']

    data = []
    for terminal in terminals:
        # Different turnaround times by terminal
        if terminal == 'International':
            base_time = 90  # Longer for international
        elif terminal == 'Terminal 3':
            base_time = 55  # United hub - efficient
        else:
            base_time = 65

        # By hour
        for hour in range(24):
            # Slower during peak hours
            if 7 <= hour <= 9 or 17 <= hour <= 19:
                turnaround = base_time + np.random.uniform(10, 20)
            else:
                turnaround = base_time + np.random.uniform(-5, 10)

            data.append({
                'terminal': terminal,
                'hour': hour,
                'avg_turnaround_min': round(turnaround, 1)
            })

    return pd.DataFrame(data)


def show():
    st.title("🔬 Advanced Analytics")
    st.markdown("### Deep-Dive Analysis of Airport Operations")

    # Load data
    hourly_data = load_data()
    runway_data = generate_runway_data()
    gate_data = generate_gate_turnaround()

    st.markdown("---")

    # Runway Utilization
    st.markdown("### 🛬 Runway Utilization Analysis")

    st.markdown("""
    **SFO Runway Configuration:**
    - **28L/28R**: Primary runways for westerly operations (prevailing winds)
    - **01L/01R**: Secondary runways for easterly operations (rare)
    """)

    col_runway1, col_runway2 = st.columns(2)

    with col_runway1:
        # Hourly runway usage
        fig = go.Figure()

        fig.add_trace(go.Scatter(
            x=runway_data['hour'],
            y=runway_data['28L/28R'],
            mode='lines+markers',
            name='28L/28R (Westerly)',
            fill='tonexty',
            line=dict(color='steelblue', width=3),
            marker=dict(size=8)
        ))

        fig.add_trace(go.Scatter(
            x=runway_data['hour'],
            y=runway_data['01L/01R'],
            mode='lines+markers',
            name='01L/01R (Easterly)',
            fill='tozeroy',
            line=dict(color='orange', width=3),
            marker=dict(size=8)
        ))

        fig.update_layout(
            title='Runway Usage by Hour of Day',
            xaxis_title='Hour',
            yaxis_title='Usage %',
            height=400,
            hovermode='x unified',
            xaxis=dict(tickmode='linear', tick0=0, dtick=2),
            yaxis=dict(range=[0, 100])
        )

        st.plotly_chart(fig, use_container_width=True)

    with col_runway2:
        # Overall distribution
        total_28 = runway_data['28L/28R'].mean()
        total_01 = runway_data['01L/01R'].mean()

        fig = go.Figure(data=[
            go.Pie(
                labels=['28L/28R (Westerly)', '01L/01R (Easterly)'],
                values=[total_28, total_01],
                hole=0.4,
                marker=dict(colors=['steelblue', 'orange']),
                textinfo='label+percent',
                textposition='inside'
            )
        ])

        fig.update_layout(
            title='Overall Runway Distribution (2024)',
            height=400
        )

        st.plotly_chart(fig, use_container_width=True)

    # Wind direction impact
    st.markdown("#### Wind Direction Impact on Runway Selection")

    # Simulate wind-runway correlation
    wind_scenarios = pd.DataFrame({
        'Wind Direction': ['West (270°)', 'Northwest (315°)', 'North (0°)', 'East (90°)', 'Variable'],
        '28L/28R Usage %': [92, 85, 65, 15, 50],
        '01L/01R Usage %': [8, 15, 35, 85, 50],
        'Frequency': [45, 30, 12, 8, 5]
    })

    col_wind1, col_wind2 = st.columns([2, 1])

    with col_wind1:
        fig = go.Figure()

        fig.add_trace(go.Bar(
            name='28L/28R',
            x=wind_scenarios['Wind Direction'],
            y=wind_scenarios['28L/28R Usage %'],
            marker_color='steelblue'
        ))

        fig.add_trace(go.Bar(
            name='01L/01R',
            x=wind_scenarios['Wind Direction'],
            y=wind_scenarios['01L/01R Usage %'],
            marker_color='orange'
        ))

        fig.update_layout(
            title='Runway Usage by Wind Direction',
            xaxis_title='Wind Direction',
            yaxis_title='Usage %',
            barmode='stack',
            height=350
        )

        st.plotly_chart(fig, use_container_width=True)

    with col_wind2:
        st.markdown("**Wind Frequency**")
        st.dataframe(
            wind_scenarios[['Wind Direction', 'Frequency']].style.format({
                'Frequency': '{}% of year'
            }),
            use_container_width=True,
            hide_index=True
        )

    st.markdown("---")

    # Gate Turnaround Analysis
    st.markdown("### 🚪 Gate Turnaround Time Analysis")

    st.markdown("""
    **Gate turnaround time**: The time between an aircraft's arrival and its next departure from the same gate.
    Faster turnaround improves efficiency and reduces delays.
    """)

    # Average by terminal
    terminal_avg = gate_data.groupby('terminal')['avg_turnaround_min'].mean().reset_index()
    terminal_avg = terminal_avg.sort_values('avg_turnaround_min')

    col_gate1, col_gate2 = st.columns(2)

    with col_gate1:
        fig = go.Figure(data=[
            go.Bar(
                x=terminal_avg['terminal'],
                y=terminal_avg['avg_turnaround_min'],
                marker_color='steelblue',
                text=terminal_avg['avg_turnaround_min'].round(1),
                texttemplate='%{text} min',
                textposition='outside'
            )
        ])

        fig.update_layout(
            title='Average Gate Turnaround Time by Terminal',
            xaxis_title='Terminal',
            yaxis_title='Average Time (minutes)',
            height=400,
            showlegend=False
        )

        st.plotly_chart(fig, use_container_width=True)

    with col_gate2:
        # Hourly heatmap
        gate_pivot = gate_data.pivot(index='terminal', columns='hour', values='avg_turnaround_min')

        fig = go.Figure(data=go.Heatmap(
            z=gate_pivot.values,
            x=gate_pivot.columns,
            y=gate_pivot.index,
            colorscale='RdYlGn_r',
            colorbar=dict(title="Minutes")
        ))

        fig.update_layout(
            title='Turnaround Time Heatmap (Hour × Terminal)',
            xaxis_title='Hour of Day',
            yaxis_title='Terminal',
            height=400
        )

        st.plotly_chart(fig, use_container_width=True)

    st.markdown("---")

    # Cascade Delay Visualization
    st.markdown("### 🌊 Cascade Delay Effect")

    st.markdown("""
    **Cascade delays**: How morning delays propagate through the day as aircraft are used for multiple flights.
    One delayed departure can impact subsequent flights throughout the day.
    """)

    # Simulate cascade effect
    hours = list(range(6, 23))
    initial_delay = 15  # minutes

    cascade_data = []
    cumulative_delay = initial_delay

    for i, hour in enumerate(hours):
        # Delay accumulates but also dissipates
        if i == 0:
            delay = initial_delay
        else:
            # Each hour: 70% of previous delay + new delays
            delay = cumulative_delay * 0.7 + np.random.uniform(2, 8)

        cumulative_delay = delay
        cascade_data.append({
            'hour': hour,
            'avg_delay_min': round(delay, 1),
            'flights_affected': int(50 * (delay / initial_delay))
        })

    cascade_df = pd.DataFrame(cascade_data)

    col_cascade1, col_cascade2 = st.columns(2)

    with col_cascade1:
        fig = go.Figure()

        fig.add_trace(go.Scatter(
            x=cascade_df['hour'],
            y=cascade_df['avg_delay_min'],
            mode='lines+markers',
            name='Average Delay',
            line=dict(color='red', width=3),
            marker=dict(size=10),
            fill='tozeroy'
        ))

        fig.add_annotation(
            x=6,
            y=initial_delay,
            text=f"Initial delay: {initial_delay} min at 6 AM",
            showarrow=True,
            arrowhead=2,
            ax=-50,
            ay=-40
        )

        fig.update_layout(
            title='Cascade Delay Propagation Throughout the Day',
            xaxis_title='Hour of Day',
            yaxis_title='Average Delay (minutes)',
            height=400,
            hovermode='x unified'
        )

        st.plotly_chart(fig, use_container_width=True)

    with col_cascade2:
        fig = go.Figure(data=[
            go.Bar(
                x=cascade_df['hour'],
                y=cascade_df['flights_affected'],
                marker_color=cascade_df['flights_affected'],
                marker_colorscale='Reds',
                showscale=False,
                text=cascade_df['flights_affected'],
                textposition='outside'
            )
        ])

        fig.update_layout(
            title='Flights Affected by Cascade Delays',
            xaxis_title='Hour of Day',
            yaxis_title='Number of Flights',
            height=400
        )

        st.plotly_chart(fig, use_container_width=True)

    st.info("💡 **Key Insight**: A 15-minute delay at 6 AM can affect 50+ flights and persist for 8-10 hours")

    st.markdown("---")

    # Year-over-Year Comparison
    st.markdown("### 📅 Year-over-Year Performance (2023 vs 2024)")

    # Simulate 2023 data (slightly worse than 2024)
    monthly_2024 = hourly_data.groupby('month')['ontime_pct'].mean()
    monthly_2023 = monthly_2024 - np.random.uniform(2, 5, len(monthly_2024))

    yoy_df = pd.DataFrame({
        'Month': [datetime(2024, m, 1).strftime('%b') for m in range(1, 13)],
        '2023': monthly_2023.values,
        '2024': monthly_2024.values,
        'Change': monthly_2024.values - monthly_2023.values
    })

    col_yoy1, col_yoy2 = st.columns([2, 1])

    with col_yoy1:
        fig = go.Figure()

        fig.add_trace(go.Scatter(
            x=yoy_df['Month'],
            y=yoy_df['2023'],
            mode='lines+markers',
            name='2023',
            line=dict(color='gray', width=2),
            marker=dict(size=8)
        ))

        fig.add_trace(go.Scatter(
            x=yoy_df['Month'],
            y=yoy_df['2024'],
            mode='lines+markers',
            name='2024',
            line=dict(color='steelblue', width=3),
            marker=dict(size=10)
        ))

        fig.update_layout(
            title='Monthly On-Time Performance: 2023 vs 2024',
            xaxis_title='Month',
            yaxis_title='On-Time %',
            height=400,
            hovermode='x unified',
            yaxis=dict(range=[65, 90])
        )

        st.plotly_chart(fig, use_container_width=True)

    with col_yoy2:
        # Summary metrics
        avg_2023 = yoy_df['2023'].mean()
        avg_2024 = yoy_df['2024'].mean()
        improvement = avg_2024 - avg_2023

        st.metric("2023 Average", f"{avg_2023:.1f}%")
        st.metric("2024 Average", f"{avg_2024:.1f}%", f"+{improvement:.1f}%")

        best_improvement = yoy_df.loc[yoy_df['Change'].idxmax()]
        st.metric(
            "Best Improvement",
            best_improvement['Month'],
            f"+{best_improvement['Change']:.1f}%"
        )

        worst_change = yoy_df.loc[yoy_df['Change'].idxmin()]
        st.metric(
            "Worst Performance",
            worst_change['Month'],
            f"{worst_change['Change']:.1f}%"
        )

    # Detailed comparison table
    st.markdown("#### Detailed Monthly Comparison")

    yoy_display = yoy_df.copy()
    yoy_display['2023'] = yoy_display['2023'].round(1).astype(str) + '%'
    yoy_display['2024'] = yoy_display['2024'].round(1).astype(str) + '%'
    yoy_display['Change'] = yoy_display['Change'].round(1).apply(lambda x: f"+{x}%" if x > 0 else f"{x}%")

    st.dataframe(yoy_display, use_container_width=True, hide_index=True)

    st.markdown("---")

    # Airport Capacity Analysis
    st.markdown("### 🏢 Airport Capacity Analysis")

    st.markdown("""
    **Capacity utilization**: Relationship between flight volume and on-time performance.
    As the airport approaches capacity, delays increase exponentially.
    """)

    # Create capacity analysis data
    capacity_data = hourly_data.groupby('hour').agg({
        'flights': 'mean',
        'ontime_pct': 'mean'
    }).reset_index()

    capacity_data['capacity_utilization'] = (capacity_data['flights'] / capacity_data['flights'].max() * 100).round(1)

    col_cap1, col_cap2 = st.columns(2)

    with col_cap1:
        # Scatter: flights per hour vs on-time %
        fig = px.scatter(
            capacity_data,
            x='flights',
            y='ontime_pct',
            size='capacity_utilization',
            color='capacity_utilization',
            color_continuous_scale='RdYlGn_r',
            hover_data={'hour': True, 'capacity_utilization': ':.1f'},
            labels={
                'flights': 'Flights per Hour',
                'ontime_pct': 'On-Time %',
                'capacity_utilization': 'Capacity %'
            }
        )

        # Add trend line
        z = np.polyfit(capacity_data['flights'], capacity_data['ontime_pct'], 2)
        p = np.poly1d(z)
        x_trend = np.linspace(capacity_data['flights'].min(), capacity_data['flights'].max(), 100)

        fig.add_trace(go.Scatter(
            x=x_trend,
            y=p(x_trend),
            mode='lines',
            name='Trend',
            line=dict(color='red', dash='dash', width=3)
        ))

        fig.update_layout(
            title='Flights per Hour vs On-Time Performance',
            height=400
        )

        st.plotly_chart(fig, use_container_width=True)

    with col_cap2:
        # Capacity by hour
        fig = go.Figure()

        fig.add_trace(go.Bar(
            x=capacity_data['hour'],
            y=capacity_data['flights'],
            marker_color=capacity_data['flights'],
            marker_colorscale='Blues',
            showscale=False,
            text=capacity_data['flights'].round(0),
            textposition='outside',
            name='Flights'
        ))

        # Add capacity threshold
        max_efficient = capacity_data['flights'].max() * 0.85
        fig.add_hline(
            y=max_efficient,
            line_dash="dash",
            line_color="red",
            annotation_text="Efficient Capacity Threshold",
            annotation_position="right"
        )

        fig.update_layout(
            title='Average Flights per Hour',
            xaxis_title='Hour of Day',
            yaxis_title='Flights',
            height=400,
            xaxis=dict(tickmode='linear', tick0=0, dtick=2)
        )

        st.plotly_chart(fig, use_container_width=True)

    st.markdown("---")

    # Peak Period Deep Dive
    st.markdown("### 🔍 Peak Period Deep Dive")

    peak_periods = {
        'Morning Rush (7-9 AM)': (7, 9),
        'Evening Rush (5-7 PM)': (17, 19)
    }

    selected_peak = st.selectbox(
        "Select Peak Period",
        options=list(peak_periods.keys())
    )

    start_hour, end_hour = peak_periods[selected_peak]

    # Filter data for selected peak
    peak_data = hourly_data[
        (hourly_data['hour'] >= start_hour) &
        (hourly_data['hour'] <= end_hour)
    ]

    col_peak1, col_peak2, col_peak3, col_peak4 = st.columns(4)

    with col_peak1:
        avg_ontime = peak_data['ontime_pct'].mean()
        overall_avg = hourly_data['ontime_pct'].mean()
        st.metric(
            "Avg On-Time %",
            f"{avg_ontime:.1f}%",
            f"{avg_ontime - overall_avg:.1f}% vs overall"
        )

    with col_peak2:
        avg_delay = peak_data['avg_delay_min'].mean()
        st.metric(
            "Avg Delay",
            f"{avg_delay:.1f} min",
            "when delayed"
        )

    with col_peak3:
        total_flights = peak_data['flights'].sum()
        st.metric(
            "Total Flights",
            f"{total_flights:,}",
            "in period"
        )

    with col_peak4:
        cancel_rate = peak_data['cancellation_pct'].mean()
        st.metric(
            "Cancel Rate",
            f"{cancel_rate:.2f}%",
            "average"
        )

    # Detailed hourly breakdown
    peak_hourly = peak_data.groupby('hour').agg({
        'ontime_pct': 'mean',
        'avg_delay_min': 'mean',
        'flights': 'sum',
        'cancellation_pct': 'mean'
    }).reset_index()

    col_peak_viz1, col_peak_viz2 = st.columns(2)

    with col_peak_viz1:
        fig = go.Figure()

        fig.add_trace(go.Bar(
            x=[f"{h:02d}:00" for h in peak_hourly['hour']],
            y=peak_hourly['ontime_pct'],
            marker_color='steelblue',
            text=peak_hourly['ontime_pct'].round(1),
            texttemplate='%{text}%',
            textposition='outside',
            name='On-Time %'
        ))

        fig.update_layout(
            title=f'{selected_peak} - On-Time Performance',
            xaxis_title='Hour',
            yaxis_title='On-Time %',
            height=350,
            yaxis=dict(range=[0, 100])
        )

        st.plotly_chart(fig, use_container_width=True)

    with col_peak_viz2:
        fig = go.Figure()

        fig.add_trace(go.Bar(
            x=[f"{h:02d}:00" for h in peak_hourly['hour']],
            y=peak_hourly['flights'],
            marker_color='orange',
            text=peak_hourly['flights'].round(0),
            texttemplate='%{text}',
            textposition='outside',
            name='Flights'
        ))

        fig.update_layout(
            title=f'{selected_peak} - Flight Volume',
            xaxis_title='Hour',
            yaxis_title='Total Flights',
            height=350
        )

        st.plotly_chart(fig, use_container_width=True)

    st.markdown("---")

    # Export all analytics
    st.markdown("### 💾 Export Analytics Data")

    col_export1, col_export2, col_export3 = st.columns(3)

    with col_export1:
        csv_runway = runway_data.to_csv(index=False)
        st.download_button(
            label="📥 Runway Data (CSV)",
            data=csv_runway,
            file_name="sfo_runway_utilization.csv",
            mime="text/csv"
        )

    with col_export2:
        csv_gate = gate_data.to_csv(index=False)
        st.download_button(
            label="📥 Gate Turnaround (CSV)",
            data=csv_gate,
            file_name="sfo_gate_turnaround.csv",
            mime="text/csv"
        )

    with col_export3:
        csv_capacity = capacity_data.to_csv(index=False)
        st.download_button(
            label="📥 Capacity Analysis (CSV)",
            data=csv_capacity,
            file_name="sfo_capacity_analysis.csv",
            mime="text/csv"
        )
