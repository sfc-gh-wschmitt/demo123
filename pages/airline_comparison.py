"""
Airline Comparison Page
Comprehensive comparison of airlines operating at SFO
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
from data_generator import get_airline_data, AIRLINES, get_delay_causes_by_airline, generate_route_performance


@st.cache_data
def load_airline_data():
    """Load and cache airline data"""
    return get_airline_data()


@st.cache_data
def get_delay_causes():
    """Load delay causes data"""
    return get_delay_causes_by_airline()


@st.cache_data
def get_routes():
    """Load route performance data"""
    return generate_route_performance()


def show():
    st.title("✈️ Airline Comparison")
    st.markdown("### Comprehensive Performance Analysis of Top Airlines at SFO")

    # Load data
    airline_data = load_airline_data()
    delay_causes = get_delay_causes()
    routes = get_routes()

    # Calculate airline summary statistics
    airline_summary = airline_data.groupby('airline').agg({
        'ontime_pct': 'mean',
        'avg_delay_min': 'mean',
        'cancellation_pct': 'mean',
        'flights': 'sum'
    }).reset_index()

    # Add static info from AIRLINES dict
    airline_summary['daily_flights'] = airline_summary['airline'].map(
        lambda x: AIRLINES.get(x, {}).get('daily_flights', 0)
    )
    airline_summary['annual_passengers_m'] = airline_summary['airline'].map(
        lambda x: AIRLINES.get(x, {}).get('passengers_m', 0)
    )
    airline_summary['rating'] = airline_summary['airline'].map(
        lambda x: AIRLINES.get(x, {}).get('rating', 0)
    )

    # Calculate rank
    airline_summary = airline_summary.sort_values('daily_flights', ascending=False).reset_index(drop=True)
    airline_summary['rank'] = range(1, len(airline_summary) + 1)

    # Reorder columns
    airline_summary = airline_summary[[
        'rank', 'airline', 'daily_flights', 'annual_passengers_m',
        'ontime_pct', 'avg_delay_min', 'cancellation_pct', 'rating'
    ]]

    st.markdown("---")

    # Top airlines table
    st.markdown("### 🏆 Top 15 Airlines Operating at SFO (2024)")

    # Format the display
    display_df = airline_summary.head(15).copy()
    display_df.columns = [
        'Rank', 'Airline', 'Daily Flights', 'Annual Passengers (M)',
        'On-Time %', 'Avg Delay (min)', 'Cancellation %', 'Customer Rating'
    ]

    # Apply styling
    def style_performance(row):
        styles = [''] * len(row)

        # Color on-time %
        if row['On-Time %'] >= 85:
            styles[4] = 'background-color: #d4edda'
        elif row['On-Time %'] >= 75:
            styles[4] = 'background-color: #fff3cd'
        else:
            styles[4] = 'background-color: #f8d7da'

        # Color rating
        if row['Customer Rating'] >= 4.5:
            styles[7] = 'background-color: #d4edda'
        elif row['Customer Rating'] >= 4.0:
            styles[7] = 'background-color: #fff3cd'

        return styles

    styled_df = display_df.style.apply(style_performance, axis=1).format({
        'Daily Flights': '{:.0f}',
        'Annual Passengers (M)': '{:.1f}M',
        'On-Time %': '{:.1f}%',
        'Avg Delay (min)': '{:.1f}',
        'Cancellation %': '{:.2f}%',
        'Customer Rating': '{:.1f}/5'
    })

    st.dataframe(styled_df, use_container_width=True, hide_index=True, height=600)

    # Export button
    csv = display_df.to_csv(index=False)
    st.download_button(
        label="📥 Download Airline Rankings (CSV)",
        data=csv,
        file_name="sfo_airline_rankings.csv",
        mime="text/csv"
    )

    st.markdown("---")

    # Performance comparison charts
    st.markdown("### 📊 Performance Comparison Visualizations")

    col_viz1, col_viz2 = st.columns(2)

    with col_viz1:
        # On-time % comparison
        fig = go.Figure()

        top10 = airline_summary.head(10).sort_values('ontime_pct', ascending=True)

        colors = ['#2ecc71' if x >= 85 else '#f39c12' if x >= 75 else '#e74c3c' for x in top10['ontime_pct']]

        fig.add_trace(go.Bar(
            y=top10['airline'],
            x=top10['ontime_pct'],
            orientation='h',
            marker_color=colors,
            text=np.round(top10['ontime_pct'], 1),
            texttemplate='%{text}%',
            textposition='outside'
        ))

        fig.update_layout(
            title='On-Time Performance - Top 10 Airlines',
            xaxis_title='On-Time %',
            yaxis_title='',
            height=500,
            showlegend=False,
            xaxis=dict(range=[0, 100])
        )

        st.plotly_chart(fig, use_container_width=True)

    with col_viz2:
        # Average delay comparison
        fig = go.Figure()

        top10_delay = airline_summary.head(10).sort_values('avg_delay_min', ascending=True)

        colors_delay = ['#2ecc71' if x < 10 else '#f39c12' if x < 15 else '#e74c3c' for x in top10_delay['avg_delay_min']]

        fig.add_trace(go.Bar(
            y=top10_delay['airline'],
            x=top10_delay['avg_delay_min'],
            orientation='h',
            marker_color=colors_delay,
            text=np.round(top10_delay['avg_delay_min'], 1),
            texttemplate='%{text} min',
            textposition='outside'
        ))

        fig.update_layout(
            title='Average Delay Time - Top 10 Airlines',
            xaxis_title='Average Delay (minutes)',
            yaxis_title='',
            height=500,
            showlegend=False
        )

        st.plotly_chart(fig, use_container_width=True)

    st.markdown("---")

    # Market share and passenger volume
    st.markdown("### 🌍 Market Share Analysis")

    col_market1, col_market2 = st.columns(2)

    with col_market1:
        # Flights market share
        top8_flights = airline_summary.head(8)
        others_flights = airline_summary[8:]['daily_flights'].sum()

        market_data = pd.DataFrame({
            'Airline': list(top8_flights['airline']) + ['Others'],
            'Daily Flights': list(top8_flights['daily_flights']) + [others_flights]
        })

        fig = px.pie(
            market_data,
            values='Daily Flights',
            names='Airline',
            title='Market Share by Daily Flights',
            hole=0.4,
            color_discrete_sequence=px.colors.qualitative.Set3
        )

        fig.update_traces(textposition='inside', textinfo='percent+label')
        fig.update_layout(height=500, showlegend=False)

        st.plotly_chart(fig, use_container_width=True)

    with col_market2:
        # Passenger volume
        fig = go.Figure(data=[
            go.Bar(
                x=airline_summary.head(10)['airline'],
                y=airline_summary.head(10)['annual_passengers_m'],
                marker_color='steelblue',
                text=airline_summary.head(10)['annual_passengers_m'],
                texttemplate='%{text:.1f}M',
                textposition='outside'
            )
        ])

        fig.update_layout(
            title='Annual Passenger Volume - Top 10 Airlines',
            xaxis_title='',
            yaxis_title='Passengers (Millions)',
            height=500,
            showlegend=False
        )

        fig.update_xaxis(tickangle=-45)

        st.plotly_chart(fig, use_container_width=True)

    st.markdown("---")

    # Hourly performance comparison
    st.markdown("### ⏰ Hourly On-Time Performance by Airline")

    # Airline selector
    selected_airlines = st.multiselect(
        "Select up to 5 airlines to compare:",
        options=list(airline_summary.head(15)['airline']),
        default=list(airline_summary.head(5)['airline']),
        max_selections=5
    )

    if selected_airlines:
        # Get hourly data for selected airlines
        hourly_airline = airline_data[airline_data['airline'].isin(selected_airlines)]
        hourly_avg = hourly_airline.groupby(['airline', hourly_airline['datetime'].dt.hour])['ontime_pct'].mean().reset_index()
        hourly_avg.columns = ['airline', 'hour', 'ontime_pct']

        fig = go.Figure()

        colors_map = px.colors.qualitative.Set1
        for i, airline in enumerate(selected_airlines):
            airline_hourly = hourly_avg[hourly_avg['airline'] == airline]

            fig.add_trace(go.Scatter(
                x=airline_hourly['hour'],
                y=airline_hourly['ontime_pct'],
                mode='lines+markers',
                name=airline,
                line=dict(width=2, color=colors_map[i % len(colors_map)]),
                marker=dict(size=6)
            ))

        fig.update_layout(
            title='On-Time Performance by Hour of Day',
            xaxis_title='Hour of Day',
            yaxis_title='On-Time %',
            height=500,
            hovermode='x unified',
            xaxis=dict(tickmode='linear', tick0=0, dtick=2),
            yaxis=dict(range=[60, 95]),
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=-0.3,
                xanchor="center",
                x=0.5
            )
        )

        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("Please select at least one airline to display the comparison chart.")

    st.markdown("---")

    # Delay causes breakdown
    st.markdown("### 🔍 Delay Causes by Airline")

    col_delay1, col_delay2 = st.columns([1, 2])

    with col_delay1:
        selected_airline_delay = st.selectbox(
            "Select airline for detailed view:",
            options=list(airline_summary.head(10)['airline'])
        )

    with col_delay2:
        st.markdown(f"#### Delay Breakdown: {selected_airline_delay}")

    # Display delay causes
    airline_causes = delay_causes[delay_causes['airline'] == selected_airline_delay]

    col_cause1, col_cause2 = st.columns(2)

    with col_cause1:
        # Pie chart
        fig = px.pie(
            airline_causes,
            values='percentage',
            names='cause',
            title=f'{selected_airline_delay} - Delay Causes',
            color_discrete_sequence=px.colors.qualitative.Pastel
        )

        fig.update_traces(textposition='inside', textinfo='percent+label')
        fig.update_layout(height=400, showlegend=False)

        st.plotly_chart(fig, use_container_width=True)

    with col_cause2:
        # Bar chart
        fig = go.Figure(data=[
            go.Bar(
                x=airline_causes['cause'],
                y=airline_causes['percentage'],
                marker_color='steelblue',
                text=airline_causes['percentage'],
                texttemplate='%{text:.1f}%',
                textposition='outside'
            )
        ])

        fig.update_layout(
            title='Delay Cause Distribution',
            xaxis_title='Cause',
            yaxis_title='Percentage',
            height=400,
            showlegend=False
        )

        fig.update_xaxis(tickangle=-45)

        st.plotly_chart(fig, use_container_width=True)

    # Stacked bar chart comparing all airlines
    st.markdown("#### Delay Causes Comparison - All Airlines")

    # Prepare data for stacked bar chart
    pivot_causes = delay_causes.pivot(index='airline', columns='cause', values='percentage')
    pivot_causes = pivot_causes.loc[airline_summary.head(10)['airline']]

    fig = go.Figure()

    causes_list = ['Weather', 'Mechanical', 'Crew', 'Air Traffic', 'Late Aircraft', 'Other']
    colors_causes = ['#3498db', '#e74c3c', '#f39c12', '#9b59b6', '#1abc9c', '#95a5a6']

    for i, cause in enumerate(causes_list):
        if cause in pivot_causes.columns:
            fig.add_trace(go.Bar(
                name=cause,
                x=pivot_causes.index,
                y=pivot_causes[cause],
                marker_color=colors_causes[i]
            ))

    fig.update_layout(
        title='Delay Causes by Airline (Stacked)',
        xaxis_title='Airline',
        yaxis_title='Percentage',
        barmode='stack',
        height=500,
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=-0.4,
            xanchor="center",
            x=0.5
        )
    )

    fig.update_xaxis(tickangle=-45)

    st.plotly_chart(fig, use_container_width=True)

    st.markdown("---")

    # Route performance
    st.markdown("### 🗺️ Top Routes by Volume")

    st.markdown("#### Top 20 Routes from SFO")

    # Display routes table
    routes_display = routes.head(20).copy()
    routes_display['rank'] = range(1, 21)
    routes_display = routes_display[[
        'rank', 'route', 'type', 'daily_flights', 'annual_passengers',
        'ontime_pct', 'avg_delay_min', 'cancellation_pct'
    ]]

    routes_display.columns = [
        'Rank', 'Route', 'Type', 'Daily Flights', 'Annual Passengers',
        'On-Time %', 'Avg Delay (min)', 'Cancel %'
    ]

    # Style the routes table
    def style_routes(row):
        styles = [''] * len(row)

        # Color on-time %
        if row['On-Time %'] >= 80:
            styles[5] = 'background-color: #d4edda'
        elif row['On-Time %'] >= 75:
            styles[5] = 'background-color: #fff3cd'
        else:
            styles[5] = 'background-color: #f8d7da'

        # Color type
        if row['Type'] == 'International':
            styles[2] = 'background-color: #d1ecf1'

        return styles

    styled_routes = routes_display.style.apply(style_routes, axis=1).format({
        'Daily Flights': '{:.0f}',
        'Annual Passengers': '{:,.0f}',
        'On-Time %': '{:.1f}%',
        'Avg Delay (min)': '{:.1f}',
        'Cancel %': '{:.2f}%'
    })

    st.dataframe(styled_routes, use_container_width=True, hide_index=True, height=600)

    # Download button
    csv_routes = routes_display.to_csv(index=False)
    st.download_button(
        label="📥 Download Route Performance (CSV)",
        data=csv_routes,
        file_name="sfo_route_performance.csv",
        mime="text/csv"
    )

    st.markdown("---")

    # Route type comparison
    col_route1, col_route2 = st.columns(2)

    with col_route1:
        # Domestic vs International flights
        domestic_total = routes[routes['type'] == 'Domestic']['daily_flights'].sum()
        intl_total = routes[routes['type'] == 'International']['daily_flights'].sum()

        fig = go.Figure(data=[
            go.Bar(
                x=['Domestic', 'International'],
                y=[domestic_total, intl_total],
                marker_color=['#3498db', '#e74c3c'],
                text=[domestic_total, intl_total],
                texttemplate='%{text:.0f} flights/day',
                textposition='outside'
            )
        ])

        fig.update_layout(
            title='Daily Flights by Route Type',
            yaxis_title='Daily Flights',
            height=400,
            showlegend=False
        )

        st.plotly_chart(fig, use_container_width=True)

    with col_route2:
        # On-time by route type
        domestic_ontime = routes[routes['type'] == 'Domestic']['ontime_pct'].mean()
        intl_ontime = routes[routes['type'] == 'International']['ontime_pct'].mean()

        fig = go.Figure(data=[
            go.Bar(
                x=['Domestic', 'International'],
                y=[domestic_ontime, intl_ontime],
                marker_color=['#3498db', '#e74c3c'],
                text=[f'{domestic_ontime:.1f}%', f'{intl_ontime:.1f}%'],
                textposition='outside'
            )
        ])

        fig.update_layout(
            title='Average On-Time % by Route Type',
            yaxis_title='On-Time %',
            height=400,
            showlegend=False,
            yaxis=dict(range=[0, 100])
        )

        st.plotly_chart(fig, use_container_width=True)

    st.markdown("---")

    # Performance matrix
    st.markdown("### 🎯 Airline Performance Matrix")
    st.markdown("*Bubble size represents daily flight volume*")

    # Create scatter plot
    fig = px.scatter(
        airline_summary.head(15),
        x='ontime_pct',
        y='rating',
        size='daily_flights',
        color='cancellation_pct',
        hover_name='airline',
        hover_data={
            'ontime_pct': ':.1f',
            'rating': ':.1f',
            'daily_flights': ':,.0f',
            'cancellation_pct': ':.2f'
        },
        labels={
            'ontime_pct': 'On-Time %',
            'rating': 'Customer Rating',
            'cancellation_pct': 'Cancellation %'
        },
        color_continuous_scale='RdYlGn_r',
        size_max=60
    )

    # Add quadrant lines
    avg_ontime = airline_summary.head(15)['ontime_pct'].mean()
    avg_rating = airline_summary.head(15)['rating'].mean()

    fig.add_hline(y=avg_rating, line_dash="dash", line_color="gray", opacity=0.5)
    fig.add_vline(x=avg_ontime, line_dash="dash", line_color="gray", opacity=0.5)

    fig.update_layout(
        title='Airline Performance Matrix: On-Time % vs Customer Rating',
        height=600,
        xaxis=dict(range=[70, 90]),
        yaxis=dict(range=[3.5, 5.0])
    )

    st.plotly_chart(fig, use_container_width=True)

    # Quadrant explanation
    col_quad1, col_quad2, col_quad3, col_quad4 = st.columns(4)

    with col_quad1:
        st.markdown("**🌟 Top Performers**")
        st.markdown("High on-time & rating")

    with col_quad2:
        st.markdown("**⚡ Fast but Unloved**")
        st.markdown("High on-time, low rating")

    with col_quad3:
        st.markdown("**❤️ Loved but Slow**")
        st.markdown("Low on-time, high rating")

    with col_quad4:
        st.markdown("**⚠️ Needs Improvement**")
        st.markdown("Low on-time & rating")

    st.markdown("---")

    # Key insights
    st.markdown("### 💡 Key Insights")

    best_ontime = airline_summary.loc[airline_summary['ontime_pct'].idxmax()]
    worst_ontime = airline_summary.loc[airline_summary['ontime_pct'].idxmin()]
    best_rating = airline_summary.loc[airline_summary['rating'].idxmax()]
    market_leader = airline_summary.iloc[0]

    insights = f"""
    - **Market Leader**: **{market_leader['airline']}** dominates with **{market_leader['daily_flights']:.0f} daily flights** (**{market_leader['annual_passengers_m']:.1f}M annual passengers**)
    - **Best On-Time Performance**: **{best_ontime['airline']}** at **{best_ontime['ontime_pct']:.1f}%**
    - **Highest Customer Rating**: **{best_rating['airline']}** with **{best_rating['rating']:.1f}/5.0**
    - **Most Reliable**: International carriers (**Lufthansa, Singapore, ANA**) average **86%+ on-time**
    - **Budget Carrier Performance**: Budget airlines average **5-8% lower** on-time rates than legacy carriers
    - **Route Analysis**: International routes perform **{intl_ontime - domestic_ontime:.1f}% better** than domestic routes on average
    - **Delay Causes**: **Weather (25-35%)** and **air traffic (20-28%)** are primary delay factors across all carriers
    """

    st.markdown(insights)
