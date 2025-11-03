"""
Test script to verify the application structure and imports
"""

import sys
import importlib

print("Testing SFO Flight Analytics Platform")
print("=" * 60)

# Test main modules
print("\n1. Testing core modules...")
try:
    import data_generator
    print("   ✓ data_generator module imported")

    # Test data generation
    hourly_data = data_generator.get_hourly_data()
    print(f"   ✓ Generated {len(hourly_data)} hours of data")

    airline_data = data_generator.get_airline_data()
    print(f"   ✓ Generated {len(airline_data)} airline records")

except Exception as e:
    print(f"   ✗ Error with data_generator: {e}")
    sys.exit(1)

# Test page modules
print("\n2. Testing page modules...")
pages = [
    'flight_overview',
    'ontime_performance',
    'weather_impact',
    'airline_comparison',
    'delay_predictor',
    'advanced_analytics'
]

for page in pages:
    try:
        module = importlib.import_module(f'pages.{page}')
        if hasattr(module, 'show'):
            print(f"   ✓ pages.{page} imported successfully")
        else:
            print(f"   ⚠ pages.{page} missing show() function")
    except Exception as e:
        print(f"   ✗ Error importing pages.{page}: {e}")
        sys.exit(1)

# Test dependencies
print("\n3. Testing dependencies...")
dependencies = [
    'streamlit',
    'pandas',
    'numpy',
    'plotly',
    'scipy'
]

for dep in dependencies:
    try:
        module = importlib.import_module(dep)
        version = getattr(module, '__version__', 'unknown')
        print(f"   ✓ {dep} ({version})")
    except ImportError:
        print(f"   ✗ {dep} not installed")
        sys.exit(1)

print("\n" + "=" * 60)
print("✅ All tests passed! Application is ready to run.")
print("\nTo start the application, run:")
print("   streamlit run app.py")
print("=" * 60)
