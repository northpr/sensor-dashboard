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
    
    # Generate data for 2 years with 2 readings per day for 20 sensors
    file_paths = save_sensor_data(days=730, frequency_minutes=720, num_sensors=20, seed=42)
    
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
