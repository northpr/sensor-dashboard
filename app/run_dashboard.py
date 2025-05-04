#!/usr/bin/env python3
"""
Script to run the Streamlit dashboard application.
"""

import os
import sys
import subprocess

def main():
    """Run the Streamlit dashboard application"""
    print("Starting Water Quality Sensor Dashboard...")
    
    # Check if data exists, if not generate it
    data_dir = os.path.join(os.path.dirname(__file__), 'data')
    if not os.path.exists(data_dir) or not os.listdir(data_dir):
        print("No data found. Generating sample data...")
        from data_generator import save_sensor_data
        save_sensor_data(days=30, frequency_minutes=15, num_sensors=5, seed=42)
        print("Sample data generated successfully!")
    
    # Run the Streamlit app
    print("\nLaunching Streamlit dashboard...")
    subprocess.run(["streamlit", "run", "app.py"])

if __name__ == "__main__":
    main()
