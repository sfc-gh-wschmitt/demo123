"""
Delay Predictor Page
Interactive tool to predict flight delays based on various parameters
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import numpy as np
import sys
import os
from datetime import datetime

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from data_generator import calculate_prediction, AIRLINES


def show():
    st.title("🔮 Flight Delay Predictor")
    st.markdown("### Predict On-Time Probability for Your Flight")

    st.info("📝 Enter your flight parameters below to get a prediction of on-time departure probability")

    st.markdown("---")

    # Input form
    st.markdown("### 📋 Flight Parameters")

    col_input1, col_input2, col_input3 = st.columns(3)

    with col_input1:
        st.markdown("#### 📅 Date & Time")

        month = st.selectbox(
            "Month",
            options=list(range(1, 13)),
            index=5,  # Default to June
            format_func=lambda x: datetime(2024, x, 1).strftime('%B')
        )

        day_of_week = st.selectbox(
            "Day of Week",
            options=['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday'],
            index=2  # Default to Wednesday
        )

        hour = st.slider(
            "Departure Hour (24-hour)",
            min_value=0,
            max_value=23,
            value=14,  # Default to 2 PM
            format="%d:00"
        )

    with col_input2:
        st.markdown("#### ✈️ Flight Details")

        airline = st.selectbox(
            "Airline",
            options=sorted(AIRLINES.keys()),
            index=sorted(AIRLINES.keys()).index('United Airlines')
        )

        flight_type = st.radio(
            "Flight Type",
            options=['Domestic', 'International'],
            index=0
        )

        st.markdown("---")
        st.markdown("**Airline Base Performance**")
        airline_base = AIRLINES[airline]['base_ontime']
        st.metric("Historical On-Time", f"{airline_base:.1f}%")

    with col_input3:
        st.markdown("#### 🌤️ Weather Conditions")

        temperature = st.slider(
            "Temperature (°F)",
            min_value=40,
            max_value=90,
            value=68,
            step=1
        )

        wind_speed = st.slider(
            "Wind Speed (mph)",
            min_value=0,
            max_value=40,
            value=12,
            step=1
        )

        visibility = st.slider(
            "Visibility (miles)",
            min_value=0.0,
            max_value=10.0,
            value=10.0,
            step=0.5
        )

        has_fog = st.checkbox("Fog Present", value=False)

    # Calculate prediction
    if st.button("🔮 Predict Performance", type="primary", use_container_width=True):
        with st.spinner("Calculating prediction..."):
            prediction = calculate_prediction(
                month=month,
                day_of_week=day_of_week,
                hour=hour,
                airline=airline,
                temp=temperature,
                wind_speed=wind_speed,
                visibility=visibility,
                has_fog=has_fog,
                flight_type=flight_type
            )

            st.session_state.prediction = prediction
            st.session_state.input_params = {
                'month': month,
                'day_of_week': day_of_week,
                'hour': hour,
                'airline': airline,
                'flight_type': flight_type,
                'temperature': temperature,
                'wind_speed': wind_speed,
                'visibility': visibility,
                'has_fog': has_fog
            }

    # Display results if prediction exists
    if 'prediction' in st.session_state:
        st.markdown("---")
        st.markdown("### 📊 Prediction Results")

        prediction = st.session_state.prediction
        params = st.session_state.input_params

        # Risk level determination
        ontime_prob = prediction['ontime_probability']
        if ontime_prob >= 80:
            risk_level = "Low"
            risk_color = "green"
            risk_emoji = "✅"
        elif ontime_prob >= 65:
            risk_level = "Medium"
            risk_color = "orange"
            risk_emoji = "⚠️"
        else:
            risk_level = "High"
            risk_color = "red"
            risk_emoji = "❌"

        # Main prediction display
        col_pred1, col_pred2, col_pred3 = st.columns([2, 1, 1])

        with col_pred1:
            st.markdown(f'<div style="background-color: {risk_color}; padding: 30px; border-radius: 10px; text-align: center;">', unsafe_allow_html=True)
            st.markdown(f'<h1 style="color: white; margin: 0;">{ontime_prob:.1f}%</h1>', unsafe_allow_html=True)
            st.markdown(f'<h3 style="color: white; margin: 0;">Chance of On-Time Departure</h3>', unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)

        with col_pred2:
            st.metric(
                "Expected Delay",
                f"{prediction['expected_delay']:.0f} min",
                "if delayed",
                delta_color="inverse"
            )

        with col_pred3:
            st.metric(
                "Risk Level",
                f"{risk_emoji} {risk_level}",
                f"{100-ontime_prob:.1f}% delay risk",
                delta_color="inverse"
            )

        st.markdown("---")

        # Gauge chart for visualization
        st.markdown("### 🎯 On-Time Probability Gauge")

        fig = go.Figure(go.Indicator(
            mode="gauge+number+delta",
            value=ontime_prob,
            domain={'x': [0, 1], 'y': [0, 1]},
            title={'text': "On-Time Probability", 'font': {'size': 24}},
            delta={'reference': airline_base, 'increasing': {'color': "green"}},
            gauge={
                'axis': {'range': [None, 100], 'tickwidth': 1, 'tickcolor': "darkblue"},
                'bar': {'color': "darkblue"},
                'bgcolor': "white",
                'borderwidth': 2,
                'bordercolor': "gray",
                'steps': [
                    {'range': [0, 65], 'color': '#f8d7da'},
                    {'range': [65, 80], 'color': '#fff3cd'},
                    {'range': [80, 100], 'color': '#d4edda'}
                ],
                'threshold': {
                    'line': {'color': "red", 'width': 4},
                    'thickness': 0.75,
                    'value': airline_base
                }
            }
        ))

        fig.update_layout(height=400)
        st.plotly_chart(fig, use_container_width=True)

        st.markdown("---")

        # Contributing factors
        st.markdown("### 📈 Contributing Factors Breakdown")

        factors_df = pd.DataFrame({
            'Factor': list(prediction['factors'].keys()),
            'Impact': [v * 100 for v in prediction['factors'].values()]
        }).sort_values('Impact', ascending=True)

        fig = go.Figure(go.Bar(
            x=factors_df['Impact'],
            y=factors_df['Factor'],
            orientation='h',
            marker=dict(
                color=factors_df['Impact'],
                colorscale='RdYlGn_r',
                showscale=False
            ),
            text=[f"{v:.1f}%" for v in factors_df['Impact']],
            textposition='outside'
        ))

        fig.update_layout(
            title='Impact of Each Factor on Delay Prediction',
            xaxis_title='Impact (%)',
            yaxis_title='',
            height=400,
            xaxis=dict(range=[0, max(factors_df['Impact']) * 1.2])
        )

        st.plotly_chart(fig, use_container_width=True)

        st.markdown("---")

        # Historical comparison
        st.markdown("### 📚 Historical Comparison")

        col_hist1, col_hist2 = st.columns(2)

        with col_hist1:
            # Similar flights performance (simulated)
            similar_ontime = ontime_prob + np.random.uniform(-5, 5)
            similar_flights = np.random.randint(500, 2000)

            st.markdown("#### Similar Flights (Past Year)")
            st.metric(
                "Historical On-Time Rate",
                f"{similar_ontime:.1f}%",
                f"Based on {similar_flights:,} flights"
            )

            st.markdown(f"""
            **Similar Flight Criteria:**
            - Same airline: {params['airline']}
            - Same departure hour: {params['hour']:02d}:00
            - Same month: {datetime(2024, params['month'], 1).strftime('%B')}
            - Same day type: {params['day_of_week']}
            """)

        with col_hist2:
            # Performance distribution
            # Simulate distribution around the prediction
            distribution = np.random.normal(ontime_prob, 5, 1000)
            distribution = np.clip(distribution, 30, 98)

            fig = go.Figure()

            fig.add_trace(go.Histogram(
                x=distribution,
                nbinsx=30,
                marker_color='steelblue',
                opacity=0.7,
                name='Historical Distribution'
            ))

            fig.add_vline(
                x=ontime_prob,
                line_dash="dash",
                line_color="red",
                annotation_text=f"Your Flight: {ontime_prob:.1f}%",
                annotation_position="top"
            )

            fig.update_layout(
                title='Performance Distribution of Similar Flights',
                xaxis_title='On-Time %',
                yaxis_title='Frequency',
                height=350,
                showlegend=False
            )

            st.plotly_chart(fig, use_container_width=True)

        st.markdown("---")

        # Recommendations
        st.markdown("### 💡 Recommendations")

        recommendations = []

        # Time-based recommendations
        if params['hour'] >= 17 and params['hour'] <= 19:
            better_hour = 7
            improvement = 12
            recommendations.append(
                f"🕐 Consider a **{better_hour:02d}:00 AM departure** for approximately **{improvement}% better** on-time rate"
            )
        elif params['hour'] >= 7 and params['hour'] <= 9:
            better_hour = 21
            improvement = 8
            recommendations.append(
                f"🕐 Evening departures (around **{better_hour:02d}:00**) may offer **{improvement}% better** performance"
            )

        # Day of week recommendations
        if params['day_of_week'] in ['Friday', 'Monday']:
            recommendations.append(
                "📅 **Weekend flights** (Saturday/Sunday) typically have **3-4% better** on-time rates"
            )

        # Weather recommendations
        if params['has_fog']:
            recommendations.append(
                "🌫️ **Fog warning**: Consider rebooking if possible. Fog reduces on-time rate by **8-10%**"
            )

        if params['visibility'] < 5:
            recommendations.append(
                "👁️ **Low visibility**: Expect potential delays. Average delay increases by **15-20 minutes**"
            )

        if params['wind_speed'] > 25:
            recommendations.append(
                "💨 **High winds**: Crosswinds may cause delays. Consider monitoring weather updates"
            )

        # Month recommendations
        if params['month'] == 12:
            recommendations.append(
                "🎄 **December travel**: Holiday season shows **7-8% lower** on-time rates. Allow extra time"
            )

        # Airline recommendations
        sorted_airlines = sorted(AIRLINES.items(), key=lambda x: x[1]['base_ontime'], reverse=True)
        if AIRLINES[params['airline']]['base_ontime'] < sorted_airlines[0][1]['base_ontime'] - 5:
            best_airline = sorted_airlines[0][0]
            improvement = sorted_airlines[0][1]['base_ontime'] - AIRLINES[params['airline']]['base_ontime']
            recommendations.append(
                f"✈️ **{best_airline}** has **{improvement:.1f}% better** historical on-time performance on this route"
            )

        # General recommendation
        if ontime_prob < 70:
            recommendations.append(
                "⚠️ **High delay risk**: Strongly consider earlier flight or alternative travel date"
            )
        elif ontime_prob >= 85:
            recommendations.append(
                "✅ **Excellent choice**: This flight has very high on-time probability"
            )

        if recommendations:
            for rec in recommendations:
                st.markdown(f"- {rec}")
        else:
            st.success("✅ Your flight parameters are optimal! No specific recommendations.")

        st.markdown("---")

        # What-if scenarios
        st.markdown("### 🔄 What-If Scenarios")
        st.markdown("See how changing parameters affects your on-time probability")

        scenario_col1, scenario_col2 = st.columns(2)

        with scenario_col1:
            st.markdown("#### Change Departure Time")

            scenario_hours = [5, 8, 12, 14, 17, 21]
            scenario_results = []

            for scenario_hour in scenario_hours:
                scenario_pred = calculate_prediction(
                    month=params['month'],
                    day_of_week=params['day_of_week'],
                    hour=scenario_hour,
                    airline=params['airline'],
                    temp=params['temperature'],
                    wind_speed=params['wind_speed'],
                    visibility=params['visibility'],
                    has_fog=params['has_fog'],
                    flight_type=params['flight_type']
                )
                scenario_results.append({
                    'Hour': f"{scenario_hour:02d}:00",
                    'On-Time %': scenario_pred['ontime_probability'],
                    'Selected': scenario_hour == params['hour']
                })

            scenario_df = pd.DataFrame(scenario_results)

            fig = go.Figure()

            colors = ['red' if row['Selected'] else 'steelblue' for _, row in scenario_df.iterrows()]

            fig.add_trace(go.Bar(
                x=scenario_df['Hour'],
                y=scenario_df['On-Time %'],
                marker_color=colors,
                text=[f"{v:.1f}%" for v in scenario_df['On-Time %']],
                textposition='outside'
            ))

            fig.update_layout(
                title='On-Time % by Departure Hour',
                xaxis_title='Departure Hour',
                yaxis_title='On-Time %',
                height=400,
                showlegend=False,
                yaxis=dict(range=[0, 100])
            )

            st.plotly_chart(fig, use_container_width=True)

        with scenario_col2:
            st.markdown("#### Change Day of Week")

            dow_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
            dow_results = []

            for dow in dow_order:
                dow_pred = calculate_prediction(
                    month=params['month'],
                    day_of_week=dow,
                    hour=params['hour'],
                    airline=params['airline'],
                    temp=params['temperature'],
                    wind_speed=params['wind_speed'],
                    visibility=params['visibility'],
                    has_fog=params['has_fog'],
                    flight_type=params['flight_type']
                )
                dow_results.append({
                    'Day': dow[:3],
                    'On-Time %': dow_pred['ontime_probability'],
                    'Selected': dow == params['day_of_week']
                })

            dow_df = pd.DataFrame(dow_results)

            fig = go.Figure()

            colors = ['red' if row['Selected'] else 'steelblue' for _, row in dow_df.iterrows()]

            fig.add_trace(go.Bar(
                x=dow_df['Day'],
                y=dow_df['On-Time %'],
                marker_color=colors,
                text=[f"{v:.1f}%" for v in dow_df['On-Time %']],
                textposition='outside'
            ))

            fig.update_layout(
                title='On-Time % by Day of Week',
                xaxis_title='Day',
                yaxis_title='On-Time %',
                height=400,
                showlegend=False,
                yaxis=dict(range=[0, 100])
            )

            st.plotly_chart(fig, use_container_width=True)

        st.markdown("---")

        # Export prediction report
        st.markdown("### 💾 Export Prediction Report")

        report_data = {
            'Prediction Date': [datetime.now().strftime('%Y-%m-%d %H:%M')],
            'Flight Month': [datetime(2024, params['month'], 1).strftime('%B')],
            'Day of Week': [params['day_of_week']],
            'Departure Hour': [f"{params['hour']:02d}:00"],
            'Airline': [params['airline']],
            'Flight Type': [params['flight_type']],
            'Temperature (°F)': [params['temperature']],
            'Wind Speed (mph)': [params['wind_speed']],
            'Visibility (mi)': [params['visibility']],
            'Fog Present': [params['has_fog']],
            'On-Time Probability': [f"{ontime_prob:.1f}%"],
            'Expected Delay (min)': [f"{prediction['expected_delay']:.1f}"],
            'Risk Level': [risk_level]
        }

        report_df = pd.DataFrame(report_data)
        csv = report_df.to_csv(index=False)

        st.download_button(
            label="📥 Download Prediction Report (CSV)",
            data=csv,
            file_name=f"sfo_delay_prediction_{datetime.now().strftime('%Y%m%d_%H%M')}.csv",
            mime="text/csv"
        )

    else:
        st.markdown("---")
        st.info("👆 Click the **Predict Performance** button above to see your results!")
