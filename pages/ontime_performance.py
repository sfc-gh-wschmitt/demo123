"""
On-Time Performance Page
Displays hourly on-time percentages, heatmaps, and trends
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import numpy as np
import sys
import os

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from data_generator import get_hourly_data, AIRLINES


@st.cache_data
def load_data():
    """Load and cache hourly performance data"""
    return get_hourly_data()


def show():
    st.title("⏰ On-Time Performance Analysis")
    st.markdown("### Comprehensive Analysis of 2024 Flight Punctuality")

    # Load data
    hourly_data = load_data()

    # Filters section
    st.markdown("### 🔍 Filters")
    col_f1, col_f2, col_f3, col_f4 = st.columns(4)

    with col_f1:
        selected_dow = st.multiselect(
            "Day of Week",
            options=['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday'],
            default=['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
        )

    with col_f2:
        selected_months = st.multiselect(
            "Months",
            options=list(range(1, 13)),
            default=list(range(1, 13)),
            format_func=lambda x: pd.to_datetime(f'2024-{x}-01').strftime('%B')
        )

    with col_f3:
        hour_range = st.slider(
            "Hour Range",
            0, 23, (0, 23)
        )

    with col_f4:
        flight_type = st.selectbox(
            "Flight Type",
            ['All', 'Peak Hours (7-9 AM, 5-7 PM)', 'Off-Peak']
        )

    # Apply filters
    filtered_data = hourly_data[
        (hourly_data['day_of_week'].isin(selected_dow)) &
        (hourly_data['month'].isin(selected_months)) &
        (hourly_data['hour'] >= hour_range[0]) &
        (hourly_data['hour'] <= hour_range[1])
    ]

    if flight_type == 'Peak Hours (7-9 AM, 5-7 PM)':
        filtered_data = filtered_data[
            ((filtered_data['hour'] >= 7) & (filtered_data['hour'] <= 9)) |
            ((filtered_data['hour'] >= 17) & (filtered_data['hour'] <= 19))
        ]
    elif flight_type == 'Off-Peak':
        filtered_data = filtered_data[
            ~(((filtered_data['hour'] >= 7) & (filtered_data['hour'] <= 9)) |
              ((filtered_data['hour'] >= 17) & (filtered_data['hour'] <= 19)))
        ]

    st.markdown("---")

    # Key metrics
    st.markdown("### 📊 Performance Metrics")

    col1, col2, col3, col4, col5 = st.columns(5)

    annual_avg = hourly_data['ontime_pct'].mean()
    filtered_avg = filtered_data['ontime_pct'].mean()

    # Best and worst months
    monthly_avg = hourly_data.groupby('month')['ontime_pct'].mean()
    best_month = monthly_avg.idxmax()
    worst_month = monthly_avg.idxmin()

    # Best and worst hours
    hourly_avg = hourly_data.groupby('hour')['ontime_pct'].mean()
    best_hour = hourly_avg.idxmax()
    worst_hour = hourly_avg.idxmin()

    with col1:
        st.metric(
            "Annual Average",
            f"{annual_avg:.1f}%",
            f"{filtered_avg - annual_avg:+.1f}% filtered"
        )

    with col2:
        st.metric(
            "Filtered Average",
            f"{filtered_avg:.1f}%",
            f"{len(filtered_data)} hours"
        )

    with col3:
        best_month_name = pd.to_datetime(f'2024-{best_month}-01').strftime('%B')
        st.metric(
            "Best Month",
            best_month_name,
            f"{monthly_avg[best_month]:.1f}%"
        )

    with col4:
        worst_month_name = pd.to_datetime(f'2024-{worst_month}-01').strftime('%B')
        st.metric(
            "Worst Month",
            worst_month_name,
            f"{monthly_avg[worst_month]:.1f}%"
        )

    with col5:
        st.metric(
            "Peak Hour Impact",
            f"-{annual_avg - hourly_avg[17]:.1f}%",
            "vs 5 PM hour"
        )

    st.markdown("---")

    # Hourly performance table
    st.markdown("### 📅 On-Time Performance by Hour")

    hourly_summary = filtered_data.groupby('hour').agg({
        'ontime_pct': 'mean',
        'avg_delay_min': 'mean',
        'flights': 'sum'
    }).reset_index()

    hourly_summary.columns = ['Hour', 'On-Time %', 'Avg Delay (min)', 'Total Flights']
    hourly_summary['Hour'] = hourly_summary['Hour'].apply(lambda x: f"{x:02d}:00")

    # Color code the on-time percentages
    def color_ontime(val):
        if val >= 80:
            return 'background-color: #d4edda'
        elif val >= 70:
            return 'background-color: #fff3cd'
        else:
            return 'background-color: #f8d7da'

    styled_hourly = hourly_summary.style.applymap(
        color_ontime,
        subset=['On-Time %']
    ).format({
        'On-Time %': '{:.1f}%',
        'Avg Delay (min)': '{:.1f}',
        'Total Flights': '{:,.0f}'
    })

    st.dataframe(styled_hourly, use_container_width=True, hide_index=True)

    # Download button
    csv = hourly_summary.to_csv(index=False)
    st.download_button(
        label="📥 Download Hourly Summary (CSV)",
        data=csv,
        file_name="sfo_hourly_ontime_summary.csv",
        mime="text/csv"
    )

    st.markdown("---")

    # Heatmap: Hour x Month
    st.markdown("### 🔥 On-Time Performance Heatmap (Hour × Month)")

    # Prepare heatmap data
    heatmap_data = filtered_data.pivot_table(
        values='ontime_pct',
        index='month',
        columns='hour',
        aggfunc='mean'
    )

    # Create month labels
    month_labels = [pd.to_datetime(f'2024-{m}-01').strftime('%b') for m in heatmap_data.index]

    fig = go.Figure(data=go.Heatmap(
        z=heatmap_data.values,
        x=heatmap_data.columns,
        y=month_labels,
        colorscale='RdYlGn',
        zmin=60,
        zmax=90,
        text=np.round(heatmap_data.values, 1),
        texttemplate='%{text}%',
        textfont={"size": 8},
        colorbar=dict(title="On-Time %")
    ))

    fig.update_layout(
        title="On-Time Performance by Hour and Month",
        xaxis_title="Hour of Day",
        yaxis_title="Month",
        height=500,
        xaxis=dict(tickmode='linear', tick0=0, dtick=1)
    )

    st.plotly_chart(fig, use_container_width=True)

    st.markdown("---")

    # Line chart: Hourly trends
    st.markdown("### 📈 Daily On-Time Performance Trends")

    col_chart1, col_chart2 = st.columns(2)

    with col_chart1:
        # Average by hour
        hourly_trend = hourly_data.groupby('hour')['ontime_pct'].mean().reset_index()

        fig = go.Figure()

        fig.add_trace(go.Scatter(
            x=hourly_trend['hour'],
            y=hourly_trend['ontime_pct'],
            mode='lines+markers',
            name='Average On-Time %',
            line=dict(color='steelblue', width=3),
            marker=dict(size=8)
        ))

        # Add threshold line
        fig.add_hline(
            y=76.4,
            line_dash="dash",
            line_color="red",
            annotation_text="Annual Average (76.4%)",
            annotation_position="right"
        )

        fig.update_layout(
            title="Average On-Time % by Hour of Day",
            xaxis_title="Hour",
            yaxis_title="On-Time %",
            height=400,
            xaxis=dict(tickmode='linear', tick0=0, dtick=2),
            yaxis=dict(range=[60, 95])
        )

        st.plotly_chart(fig, use_container_width=True)

    with col_chart2:
        # Day of week comparison
        dow_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
        dow_avg = hourly_data.groupby('day_of_week')['ontime_pct'].mean().reindex(dow_order).reset_index()

        fig = go.Figure()

        colors = ['#e74c3c' if x in ['Friday', 'Monday'] else '#3498db' if x in ['Saturday', 'Sunday'] else '#95a5a6'
                 for x in dow_avg['day_of_week']]

        fig.add_trace(go.Bar(
            x=dow_avg['day_of_week'],
            y=dow_avg['ontime_pct'],
            marker_color=colors,
            text=np.round(dow_avg['ontime_pct'], 1),
            texttemplate='%{text}%',
            textposition='outside'
        ))

        fig.add_hline(
            y=76.4,
            line_dash="dash",
            line_color="red",
            annotation_text="Annual Avg",
            annotation_position="right"
        )

        fig.update_layout(
            title="Average On-Time % by Day of Week",
            xaxis_title="Day",
            yaxis_title="On-Time %",
            height=400,
            showlegend=False,
            yaxis=dict(range=[60, 95])
        )

        st.plotly_chart(fig, use_container_width=True)

    st.markdown("---")

    # Monthly trends with moving average
    st.markdown("### 📊 Monthly Trends with 90-Day Moving Average")

    # Calculate daily averages first
    daily_avg = hourly_data.groupby('date')['ontime_pct'].mean().reset_index()
    daily_avg['date'] = pd.to_datetime(daily_avg['date'])
    daily_avg = daily_avg.sort_values('date')

    # Calculate 30-day and 90-day moving averages
    daily_avg['ma_30'] = daily_avg['ontime_pct'].rolling(window=30, min_periods=1).mean()
    daily_avg['ma_90'] = daily_avg['ontime_pct'].rolling(window=90, min_periods=1).mean()

    fig = go.Figure()

    # Add daily data (with transparency)
    fig.add_trace(go.Scatter(
        x=daily_avg['date'],
        y=daily_avg['ontime_pct'],
        mode='lines',
        name='Daily Average',
        line=dict(color='lightgray', width=1),
        opacity=0.3
    ))

    # Add 30-day MA
    fig.add_trace(go.Scatter(
        x=daily_avg['date'],
        y=daily_avg['ma_30'],
        mode='lines',
        name='30-Day MA',
        line=dict(color='orange', width=2)
    ))

    # Add 90-day MA
    fig.add_trace(go.Scatter(
        x=daily_avg['date'],
        y=daily_avg['ma_90'],
        mode='lines',
        name='90-Day MA',
        line=dict(color='steelblue', width=3)
    ))

    fig.update_layout(
        title="On-Time Performance Trends Throughout 2024",
        xaxis_title="Date",
        yaxis_title="On-Time %",
        height=500,
        hovermode='x unified',
        yaxis=dict(range=[60, 95])
    )

    st.plotly_chart(fig, use_container_width=True)

    st.markdown("---")

    # Performance distribution
    st.markdown("### 📊 Performance Distribution")

    col_dist1, col_dist2 = st.columns(2)

    with col_dist1:
        # Histogram of on-time percentages
        fig = go.Figure()

        fig.add_trace(go.Histogram(
            x=filtered_data['ontime_pct'],
            nbinsx=30,
            marker_color='steelblue',
            opacity=0.7
        ))

        fig.add_vline(
            x=filtered_avg,
            line_dash="dash",
            line_color="red",
            annotation_text=f"Mean: {filtered_avg:.1f}%",
            annotation_position="top"
        )

        fig.update_layout(
            title="Distribution of Hourly On-Time Percentages",
            xaxis_title="On-Time %",
            yaxis_title="Frequency",
            height=400
        )

        st.plotly_chart(fig, use_container_width=True)

    with col_dist2:
        # Box plot by month
        fig = go.Figure()

        for month in sorted(filtered_data['month'].unique()):
            month_data = filtered_data[filtered_data['month'] == month]
            month_name = pd.to_datetime(f'2024-{month}-01').strftime('%b')

            fig.add_trace(go.Box(
                y=month_data['ontime_pct'],
                name=month_name,
                marker_color='steelblue'
            ))

        fig.update_layout(
            title="On-Time % Distribution by Month",
            xaxis_title="Month",
            yaxis_title="On-Time %",
            height=400,
            showlegend=False,
            yaxis=dict(range=[50, 100])
        )

        st.plotly_chart(fig, use_container_width=True)

    # Performance categories
    st.markdown("### 🎯 Performance Categories")

    col_cat1, col_cat2, col_cat3 = st.columns(3)

    excellent = len(filtered_data[filtered_data['ontime_pct'] >= 85]) / len(filtered_data) * 100
    good = len(filtered_data[(filtered_data['ontime_pct'] >= 75) & (filtered_data['ontime_pct'] < 85)]) / len(filtered_data) * 100
    poor = len(filtered_data[filtered_data['ontime_pct'] < 75]) / len(filtered_data) * 100

    with col_cat1:
        st.markdown('<div class="metric-on-time">', unsafe_allow_html=True)
        st.metric("Excellent Hours (≥85%)", f"{excellent:.1f}%", f"{int(excellent * len(filtered_data) / 100)} hours")
        st.markdown('</div>', unsafe_allow_html=True)

    with col_cat2:
        st.markdown('<div class="metric-delayed">', unsafe_allow_html=True)
        st.metric("Good Hours (75-85%)", f"{good:.1f}%", f"{int(good * len(filtered_data) / 100)} hours")
        st.markdown('</div>', unsafe_allow_html=True)

    with col_cat3:
        st.markdown('<div class="metric-cancelled">', unsafe_allow_html=True)
        st.metric("Poor Hours (<75%)", f"{poor:.1f}%", f"{int(poor * len(filtered_data) / 100)} hours")
        st.markdown('</div>', unsafe_allow_html=True)

    # Insights
    st.markdown("---")
    st.markdown("### 💡 Key Insights")

    insights = f"""
    - **Best Time to Fly**: Early morning flights (4-6 AM) have the highest on-time rate at **{hourly_avg[4:7].mean():.1f}%**
    - **Worst Time to Fly**: Evening rush (5-6 PM) shows lowest performance at **{hourly_avg[17:19].mean():.1f}%**
    - **Best Month**: {best_month_name} achieves **{monthly_avg[best_month]:.1f}%** on-time performance
    - **Worst Month**: {worst_month_name} drops to **{monthly_avg[worst_month]:.1f}%** due to holiday travel
    - **Weekend Advantage**: Saturday and Sunday flights are **~4% more punctual** than weekdays
    - **Peak Hour Penalty**: Morning (7-9 AM) and evening (5-7 PM) rush periods see **8-10% lower** on-time rates
    """

    st.markdown(insights)
