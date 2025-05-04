#!/usr/bin/env python3
"""
Script to generate sample sensor data for the dashboard.
This can be run independently to create or refresh the data.
"""

import os
import sys
from data_generator import save_sensor_data

def main():
    """Generate sample sensor data"""
    print("Generating sensor data...")
    
    # Generate data for 30 days with readings every 15 minutes for 5 sensors
    file_paths = save_sensor_data(days=30, frequency_minutes=15, num_sensors=5, seed=42)
    
    print("\nSensor data generated and saved to:")
    for key, path in file_paths.items():
        if isinstance(path, dict):
            for sub_key, sub_path in path.items():
                print(f"  - {sub_key}: {sub_path}")
        else:
            print(f"  - {key}: {path}")
    
    print("\nData generation complete!")

if __name__ == "__main__":
    main()
