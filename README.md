# SFO Flight Performance and On-Time Analytics Platform

A comprehensive Streamlit application for analyzing flight performance at San Francisco International Airport (SFO) with detailed analytics, predictions, and visualizations.

## Features

### 1. Flight Overview
- Real-time airport operations dashboard
- Terminal status and capacity utilization
- Current weather conditions
- Live departure board with next 20 flights
- Daily flight distribution analysis

### 2. On-Time Performance
- Hourly on-time percentages for full year 2024
- Interactive heatmaps (Hour × Month)
- Monthly trends with 90-day moving average
- Performance distribution analysis
- Day of week comparisons

### 3. Weather Impact Analysis
- Hourly weather patterns and correlations
- Scatter plots: Wind vs Delay, Visibility vs On-Time
- Fog impact analysis with monthly breakdown
- Correlation matrix between weather and performance
- Seasonal performance comparison

### 4. Airline Comparison
- Rankings of top 15 airlines at SFO
- Market share analysis
- Hourly performance comparison (up to 5 airlines)
- Delay causes breakdown by airline
- Route performance for top 20 routes
- Performance matrix visualization

### 5. Delay Predictor
- Interactive prediction tool
- Input parameters: date, time, airline, weather
- Real-time probability calculations
- Contributing factors breakdown
- Historical comparisons
- What-if scenario analysis
- Personalized recommendations

### 6. Advanced Analytics
- Runway utilization analysis
- Gate turnaround time metrics
- Cascade delay visualization
- Year-over-year comparison (2023 vs 2024)
- Airport capacity analysis
- Peak period deep-dive (morning/evening rush)

## Installation

1. Clone the repository or download the files

2. Install dependencies:
```bash
pip install -r requirements.txt
```

## Running the Application

```bash
streamlit run app.py
```

The application will open in your default web browser at `http://localhost:8501`

## Data

The application uses synthetic but realistic data for 2024:
- 8,760 hours of flight operations (365 days × 24 hours)
- 15+ major airlines operating at SFO
- Weather conditions including temperature, wind, visibility, and fog
- Performance metrics: on-time %, delays, cancellations

## Technology Stack

- **Streamlit**: Web application framework
- **Pandas**: Data manipulation and analysis
- **NumPy**: Numerical computations
- **Plotly**: Interactive visualizations
- **SciPy**: Statistical correlations

## Project Structure

```
.
├── app.py                      # Main application entry point
├── data_generator.py           # Synthetic data generation module
├── requirements.txt            # Python dependencies
├── README.md                   # This file
└── pages/                      # Page modules
    ├── __init__.py
    ├── flight_overview.py      # Flight Overview page
    ├── ontime_performance.py   # On-Time Performance page
    ├── weather_impact.py       # Weather Impact page
    ├── airline_comparison.py   # Airline Comparison page
    ├── delay_predictor.py      # Delay Predictor page
    └── advanced_analytics.py   # Advanced Analytics page
```

## Features in Detail

### Export Functionality
- Download filtered datasets as CSV
- Export prediction reports
- Save analytics data for offline analysis

### Caching
- Intelligent data caching for improved performance
- Calculations cached to reduce load times

### Interactive Filters
- Multi-select filters for airlines, dates, times
- Dynamic updates across visualizations
- Persistent user preferences

### Real-time Simulation
- Optional real-time mode (configurable in settings)
- Auto-refresh functionality
- Live departure board updates

## Configuration

Settings available in sidebar:
- Real-time mode toggle
- Alert threshold customization (50-90%)
- Animation preferences

## Performance Metrics

Key metrics tracked:
- On-time percentage
- Average delay time
- Cancellation rate
- Customer ratings
- Passenger volume
- Flight counts

## Author

Created as a comprehensive demonstration of flight analytics and data visualization capabilities.

## License

This is a demonstration project with synthetic data for educational and analytical purposes.
