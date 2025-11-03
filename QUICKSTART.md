# Quick Start Guide

## Installation & Setup

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Test the Application
```bash
python3 test_app.py
```

### 3. Run the Application
```bash
streamlit run app.py
```

The app will automatically open in your browser at `http://localhost:8501`

## Navigation

The app has 6 main pages accessible via the sidebar:

1. **Flight Overview** - Real-time airport dashboard
2. **On-Time Performance** - Detailed punctuality analysis
3. **Weather Impact Analysis** - Weather correlation studies
4. **Airline Comparison** - Compare airlines and routes
5. **Delay Predictor** - Interactive prediction tool
6. **Advanced Analytics** - Deep-dive operational metrics

## Key Features to Try

### Flight Overview
- View live departure board
- Check terminal capacity utilization
- See current weather conditions

### On-Time Performance
- Explore the Hour × Month heatmap
- Apply filters for specific days/airlines
- Download hourly summary data

### Weather Impact Analysis
- Check fog impact statistics
- View weather correlation matrix
- Compare seasonal performance

### Airline Comparison
- Review airline rankings table
- Compare multiple airlines hourly
- Analyze delay causes by airline

### Delay Predictor
- Enter your flight parameters
- Get on-time probability prediction
- View personalized recommendations
- Explore what-if scenarios

### Advanced Analytics
- Analyze runway utilization patterns
- Check gate turnaround times
- View cascade delay effects
- Compare year-over-year performance

## Tips

- Use filters to narrow down analysis
- Download CSV exports for offline analysis
- Check tooltips on charts for detailed info
- Experiment with the delay predictor's what-if scenarios
- Adjust settings in the sidebar (alert thresholds, etc.)

## Data Information

- **Time Period**: Full year 2024 (8,760 hours)
- **Airlines**: 15 major carriers at SFO
- **Flights**: ~1,200 per day (~440,000 annually)
- **Data Type**: Synthetic but realistic patterns

## Troubleshooting

If you encounter issues:

1. Ensure all dependencies are installed:
   ```bash
   pip install -r requirements.txt
   ```

2. Run the test script:
   ```bash
   python3 test_app.py
   ```

3. Clear Streamlit cache:
   ```bash
   streamlit cache clear
   ```

4. Check Python version (3.8+ required):
   ```bash
   python3 --version
   ```

## Support

For issues or questions, refer to:
- README.md for detailed documentation
- Code comments in each module
- Streamlit documentation: https://docs.streamlit.io

Enjoy exploring SFO flight analytics! ✈️
