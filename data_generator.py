"""
SFO Flight Data Generator
Generates synthetic but realistic flight performance data for 2024
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import random

# Set random seed for reproducibility
np.random.seed(42)
random.seed(42)

# Airline data with realistic performance profiles
AIRLINES = {
    'United Airlines': {'base_ontime': 79.2, 'variance': 8, 'daily_flights': 385, 'passengers_m': 18.2, 'rating': 4.1},
    'Alaska Airlines': {'base_ontime': 82.5, 'variance': 6, 'daily_flights': 95, 'passengers_m': 4.1, 'rating': 4.3},
    'Southwest': {'base_ontime': 77.8, 'variance': 9, 'daily_flights': 78, 'passengers_m': 3.5, 'rating': 3.9},
    'Delta': {'base_ontime': 80.1, 'variance': 7, 'daily_flights': 62, 'passengers_m': 2.8, 'rating': 4.2},
    'American': {'base_ontime': 76.3, 'variance': 10, 'daily_flights': 58, 'passengers_m': 2.6, 'rating': 3.8},
    'JetBlue': {'base_ontime': 74.2, 'variance': 11, 'daily_flights': 24, 'passengers_m': 1.1, 'rating': 3.7},
    'Air Canada': {'base_ontime': 81.3, 'variance': 7, 'daily_flights': 22, 'passengers_m': 0.945, 'rating': 4.0},
    'Lufthansa': {'base_ontime': 83.7, 'variance': 5, 'daily_flights': 14, 'passengers_m': 0.678, 'rating': 4.4},
    'British Airways': {'base_ontime': 82.9, 'variance': 6, 'daily_flights': 12, 'passengers_m': 0.592, 'rating': 4.2},
    'Singapore Airlines': {'base_ontime': 88.5, 'variance': 4, 'daily_flights': 11, 'passengers_m': 0.534, 'rating': 4.8},
    'Virgin Atlantic': {'base_ontime': 81.7, 'variance': 7, 'daily_flights': 8, 'passengers_m': 0.412, 'rating': 4.1},
    'Cathay Pacific': {'base_ontime': 85.3, 'variance': 5, 'daily_flights': 7, 'passengers_m': 0.378, 'rating': 4.5},
    'Emirates': {'base_ontime': 84.2, 'variance': 6, 'daily_flights': 6, 'passengers_m': 0.324, 'rating': 4.6},
    'ANA': {'base_ontime': 86.8, 'variance': 4, 'daily_flights': 5, 'passengers_m': 0.287, 'rating': 4.7},
    'Air France': {'base_ontime': 79.5, 'variance': 8, 'daily_flights': 4, 'passengers_m': 0.219, 'rating': 3.9},
}

# Destinations with distance categories
DESTINATIONS = {
    'Domestic': ['Los Angeles', 'New York JFK', 'Chicago ORD', 'Dallas DFW', 'Seattle', 'Boston',
                 'Washington IAD', 'Denver', 'Phoenix', 'Atlanta', 'Las Vegas', 'Houston',
                 'Miami', 'Orlando', 'Portland', 'San Diego', 'Austin', 'Philadelphia'],
    'International': ['Tokyo HND', 'London LHR', 'Paris CDG', 'Hong Kong', 'Shanghai PVG',
                     'Frankfurt', 'Sydney', 'Toronto', 'Vancouver', 'Mexico City',
                     'Singapore', 'Seoul ICN', 'Munich', 'Dubai', 'Zurich']
}

def generate_hourly_performance_data():
    """Generate hourly on-time performance data for full year 2024"""

    start_date = datetime(2024, 1, 1)
    hours_in_year = 365 * 24

    data = []

    for hour_idx in range(hours_in_year):
        current_time = start_date + timedelta(hours=hour_idx)
        hour_of_day = current_time.hour
        month = current_time.month
        day_of_week = current_time.strftime('%A')

        # Base on-time rate by hour (early morning best, evening worst)
        hour_factors = {
            0: 86.5, 1: 87.8, 2: 88.2, 3: 87.9, 4: 87.5, 5: 87.3,
            6: 84.1, 7: 78.2, 8: 72.5, 9: 74.3, 10: 75.8, 11: 76.2,
            12: 74.5, 13: 73.1, 14: 71.8, 15: 69.3, 16: 67.2, 17: 65.3,
            18: 68.7, 19: 70.5, 20: 73.2, 21: 76.8, 22: 81.3, 23: 84.7
        }

        base_ontime = hour_factors[hour_of_day]

        # Monthly variation (December worst, September best)
        month_factors = {
            1: -2.3, 2: -1.1, 3: 0.5, 4: 1.2, 5: 2.1, 6: 1.8,
            7: 0.9, 8: 2.5, 9: 5.7, 10: 3.2, 11: 1.1, 12: -7.5
        }

        # Day of week impact (weekends better)
        dow_factors = {
            'Monday': -1.5, 'Tuesday': 0.5, 'Wednesday': 0.8,
            'Thursday': -0.8, 'Friday': -2.1, 'Saturday': 3.2, 'Sunday': 2.8
        }

        # Weather simulation (more fog in summer, more storms in winter)
        fog_prob = 0.15 if month in [6, 7, 8] else 0.05
        has_fog = np.random.random() < fog_prob

        temp = 52 + 10 * np.sin((month - 1) / 12 * 2 * np.pi) + np.random.normal(0, 5)
        wind_speed = 12 + 5 * (hour_of_day >= 12) + np.random.exponential(4)
        visibility = 10 if not has_fog else np.random.uniform(2, 8)
        precipitation = np.random.random() < 0.12  # 12% chance of rain

        # Calculate on-time rate with all factors
        ontime_pct = (base_ontime +
                      month_factors[month] +
                      dow_factors[day_of_week] +
                      (-8 if has_fog else 0) +
                      (-visibility / 10 * 3) +
                      (-wind_speed / 30 * 5) +
                      (-10 if precipitation else 0) +
                      np.random.normal(0, 3))

        ontime_pct = np.clip(ontime_pct, 35, 95)

        # Calculate delay metrics
        avg_delay = (100 - ontime_pct) * 0.35 + np.random.uniform(5, 15)
        cancellation_rate = (100 - ontime_pct) * 0.03 + np.random.uniform(0, 1)

        data.append({
            'datetime': current_time,
            'date': current_time.date(),
            'hour': hour_of_day,
            'month': month,
            'month_name': current_time.strftime('%B'),
            'day_of_week': day_of_week,
            'ontime_pct': round(ontime_pct, 1),
            'avg_delay_min': round(avg_delay, 1),
            'cancellation_pct': round(cancellation_rate, 2),
            'temperature_f': round(temp, 1),
            'wind_speed_mph': round(wind_speed, 1),
            'visibility_mi': round(visibility, 1),
            'has_fog': has_fog,
            'has_precipitation': precipitation,
            'flights': np.random.poisson(50)  # ~50 flights per hour average
        })

    return pd.DataFrame(data)


def generate_airline_performance_data(hourly_data):
    """Generate airline-specific performance data"""

    airline_data = []

    for airline, props in AIRLINES.items():
        for _, hour_row in hourly_data.iterrows():
            # Adjust base airline performance by hour conditions
            airline_ontime = (props['base_ontime'] +
                            (hour_row['ontime_pct'] - 76.4) * 0.3 +  # Market condition factor
                            np.random.normal(0, props['variance']))

            airline_ontime = np.clip(airline_ontime, 40, 98)

            avg_delay = (100 - airline_ontime) * 0.4 + np.random.uniform(3, 12)
            cancellation = (100 - airline_ontime) * 0.025 + np.random.uniform(0, 0.5)

            # Distribute flights by hour (more in morning and evening)
            hour_distribution = {
                range(0, 5): 0.02, range(5, 8): 0.15, range(8, 12): 0.20,
                range(12, 17): 0.18, range(17, 21): 0.25, range(21, 24): 0.20
            }

            hour_factor = next(v for r, v in hour_distribution.items() if hour_row['hour'] in r)
            flights_this_hour = int(props['daily_flights'] * hour_factor * (1 + np.random.uniform(-0.3, 0.3)))

            airline_data.append({
                'datetime': hour_row['datetime'],
                'airline': airline,
                'ontime_pct': round(airline_ontime, 1),
                'avg_delay_min': round(avg_delay, 1),
                'cancellation_pct': round(cancellation, 2),
                'flights': max(0, flights_this_hour),
                'daily_flights': props['daily_flights'],
                'annual_passengers_m': props['passengers_m'],
                'rating': props['rating']
            })

    return pd.DataFrame(airline_data)


def generate_flight_board(current_time=None):
    """Generate live departure board data"""

    if current_time is None:
        current_time = datetime(2024, 6, 15, 14, 30)  # Default: June 15, 2:30 PM

    flights = []

    # Generate 20 upcoming flights
    for i in range(20):
        scheduled_time = current_time + timedelta(minutes=i*10 + np.random.randint(-5, 15))
        airline = random.choice(list(AIRLINES.keys()))

        # Determine if domestic or international
        is_international = random.random() < 0.3
        destination = random.choice(DESTINATIONS['International' if is_international else 'Domestic'])

        # Generate flight number
        airline_codes = {
            'United Airlines': 'UA', 'Alaska Airlines': 'AS', 'Southwest': 'WN',
            'Delta': 'DL', 'American': 'AA', 'JetBlue': 'B6', 'Air Canada': 'AC',
            'Lufthansa': 'LH', 'British Airways': 'BA', 'Singapore Airlines': 'SQ',
            'Virgin Atlantic': 'VS', 'Cathay Pacific': 'CX', 'Emirates': 'EK',
            'ANA': 'NH', 'Air France': 'AF'
        }

        flight_number = f"{airline_codes[airline]}{random.randint(100, 9999)}"

        # Gate assignment
        if is_international:
            gate = f"G{random.randint(1, 14)}"
        else:
            terminal = random.choice(['1', '2', '3'])
            gate = f"{terminal}{random.choice('ABCDEF')}{random.randint(1, 12)}"

        # Status determination
        time_until = (scheduled_time - current_time).total_seconds() / 60

        if time_until < -15:
            status = 'Departed'
        elif time_until < 0:
            status = random.choice(['Departed', 'Delayed', 'Boarding'])
        elif time_until < 30:
            status = random.choice(['On Time', 'Boarding', 'Delayed', 'On Time', 'On Time'])
        else:
            status = random.choice(['On Time', 'On Time', 'On Time', 'Delayed'])

        flights.append({
            'flight_number': flight_number,
            'airline': airline,
            'destination': destination,
            'scheduled_time': scheduled_time.strftime('%H:%M'),
            'gate': gate,
            'status': status,
            'terminal': 'International' if is_international else f'Terminal {gate[0]}' if not is_international and gate[0].isdigit() else 'Terminal 3'
        })

    return pd.DataFrame(flights).sort_values('scheduled_time')


def generate_route_performance():
    """Generate performance data for top routes"""

    routes = []
    all_destinations = DESTINATIONS['Domestic'] + DESTINATIONS['International']

    # Weight destinations by popularity
    popular_domestic = ['Los Angeles', 'New York JFK', 'Chicago ORD', 'Seattle', 'Las Vegas',
                       'Denver', 'Boston', 'Washington IAD']
    popular_international = ['Tokyo HND', 'London LHR', 'Hong Kong', 'Paris CDG', 'Frankfurt']

    popular = popular_domestic + popular_international

    for dest in popular:
        is_international = dest in DESTINATIONS['International']

        # More flights to popular domestic destinations
        if dest in popular_domestic[:4]:
            daily_flights = np.random.randint(40, 80)
        elif dest in popular_domestic:
            daily_flights = np.random.randint(15, 40)
        else:
            daily_flights = np.random.randint(5, 15)

        # International flights generally more punctual
        base_ontime = np.random.uniform(78, 88) if is_international else np.random.uniform(72, 82)

        routes.append({
            'route': f'SFO → {dest}',
            'destination': dest,
            'type': 'International' if is_international else 'Domestic',
            'daily_flights': daily_flights,
            'annual_passengers': daily_flights * 180 * 365,  # ~180 passengers per flight
            'ontime_pct': round(base_ontime, 1),
            'avg_delay_min': round((100 - base_ontime) * 0.4 + np.random.uniform(5, 12), 1),
            'cancellation_pct': round(np.random.uniform(0.5, 2.5), 2)
        })

    return pd.DataFrame(routes).sort_values('daily_flights', ascending=False)


def get_delay_causes_by_airline():
    """Generate delay cause breakdown by airline"""

    causes = ['Weather', 'Mechanical', 'Crew', 'Air Traffic', 'Late Aircraft', 'Other']
    data = []

    for airline in AIRLINES.keys():
        # Different airlines have different delay patterns
        if airline in ['Singapore Airlines', 'ANA', 'Cathay Pacific', 'Lufthansa']:
            # Better maintained airlines - less mechanical
            weights = [0.30, 0.15, 0.10, 0.25, 0.15, 0.05]
        elif airline in ['United Airlines', 'Delta', 'Alaska Airlines']:
            # Major carriers - more air traffic delays
            weights = [0.25, 0.20, 0.12, 0.28, 0.12, 0.03]
        else:
            # Budget/regional - more mechanical and crew issues
            weights = [0.25, 0.25, 0.15, 0.20, 0.12, 0.03]

        for cause, weight in zip(causes, weights):
            data.append({
                'airline': airline,
                'cause': cause,
                'percentage': round(weight * 100, 1)
            })

    return pd.DataFrame(data)


def calculate_prediction(month, day_of_week, hour, airline, temp, wind_speed, visibility, has_fog, flight_type):
    """Calculate delay prediction based on input parameters"""

    # Base rates from historical patterns
    hour_factors = {
        0: 86.5, 1: 87.8, 2: 88.2, 3: 87.9, 4: 87.5, 5: 87.3,
        6: 84.1, 7: 78.2, 8: 72.5, 9: 74.3, 10: 75.8, 11: 76.2,
        12: 74.5, 13: 73.1, 14: 71.8, 15: 69.3, 16: 67.2, 17: 65.3,
        18: 68.7, 19: 70.5, 20: 73.2, 21: 76.8, 22: 81.3, 23: 84.7
    }

    month_factors = {
        1: -2.3, 2: -1.1, 3: 0.5, 4: 1.2, 5: 2.1, 6: 1.8,
        7: 0.9, 8: 2.5, 9: 5.7, 10: 3.2, 11: 1.1, 12: -7.5
    }

    dow_mapping = {
        'Monday': -1.5, 'Tuesday': 0.5, 'Wednesday': 0.8,
        'Thursday': -0.8, 'Friday': -2.1, 'Saturday': 3.2, 'Sunday': 2.8
    }

    # Calculate base probability
    base_ontime = hour_factors.get(hour, 75)
    month_adj = month_factors.get(month, 0)
    dow_adj = dow_mapping.get(day_of_week, 0)

    # Airline adjustment
    airline_base = AIRLINES.get(airline, {'base_ontime': 76.4})['base_ontime']
    airline_adj = (airline_base - 76.4) * 0.5

    # Weather adjustments
    weather_adj = 0
    weather_adj += (-8 if has_fog else 0)
    weather_adj += max(-5, -(10 - visibility) * 1.5)
    weather_adj += max(-4, -wind_speed / 10)
    weather_adj += -2 if temp < 45 or temp > 85 else 0

    # Flight type adjustment
    type_adj = 2 if flight_type == 'International' else 0

    # Calculate final probability
    ontime_prob = base_ontime + month_adj + dow_adj + airline_adj + weather_adj + type_adj
    ontime_prob = np.clip(ontime_prob, 30, 95)

    # Expected delay if delayed
    expected_delay = (100 - ontime_prob) * 0.5 + np.random.uniform(10, 20)

    # Contributing factors
    total_impact = abs(month_adj) + abs(dow_adj) + abs(airline_adj) + abs(weather_adj) + abs(type_adj)

    if total_impact == 0:
        factors = {
            'Weather': 0.25, 'Time of day': 0.25, 'Airline': 0.20,
            'Day of week': 0.15, 'Other': 0.15
        }
    else:
        factors = {
            'Weather': abs(weather_adj) / total_impact,
            'Time of day': abs(hour_factors.get(hour, 75) - 76.4) / (total_impact * 2),
            'Airline': abs(airline_adj) / total_impact,
            'Day of week': abs(dow_adj) / total_impact,
            'Other': 0.05
        }

        # Normalize
        factor_sum = sum(factors.values())
        factors = {k: v / factor_sum for k, v in factors.items()}

    return {
        'ontime_probability': round(ontime_prob, 1),
        'expected_delay': round(expected_delay, 1),
        'factors': factors
    }


# Cache the generated data
_hourly_cache = None
_airline_cache = None

def get_hourly_data():
    """Get cached hourly data"""
    global _hourly_cache
    if _hourly_cache is None:
        _hourly_cache = generate_hourly_performance_data()
    return _hourly_cache

def get_airline_data():
    """Get cached airline data"""
    global _airline_cache
    if _airline_cache is None:
        _airline_cache = generate_airline_performance_data(get_hourly_data())
    return _airline_cache
