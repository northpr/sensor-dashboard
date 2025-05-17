#!/usr/bin/env python3
"""
AWS IoT Core to CSV Integration Script

This script subscribes to an AWS IoT Core MQTT topic where sensor data is published,
processes the data, and saves it to CSV files compatible with the dashboard.

Requirements:
- AWS IoT SDK for Python (AWSIoTPythonSDK)
- pandas
- boto3 (for AWS credentials)

Usage:
python aws_to_csv.py --endpoint <aws-iot-endpoint> --root-ca <root-ca-path> --cert <cert-path> --key <private-key-path> --topic <mqtt-topic> --output-dir <csv-output-directory>
"""

import argparse
import json
import logging
import os
import sys
import time
from datetime import datetime
from threading import Thread

import pandas as pd
from AWSIoTPythonSDK.MQTTLib import AWSIoTMQTTClient

# Configure logging
logger = logging.getLogger("AWSIoTLogger")
logger.setLevel(logging.INFO)
streamHandler = logging.StreamHandler()
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
streamHandler.setFormatter(formatter)
logger.addHandler(streamHandler)

# Global variables
received_messages = []
output_directory = None
combined_data_file = None
daily_summary_file = None
sensor_info_file = None

def parse_args():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser()
    parser.add_argument('--endpoint', required=True, help="Your AWS IoT custom endpoint")
    parser.add_argument('--root-ca', required=True, help="Root CA file path")
    parser.add_argument('--cert', required=True, help="Certificate file path")
    parser.add_argument('--key', required=True, help="Private key file path")
    parser.add_argument('--topic', required=True, default="soil/sensors", help="MQTT topic to subscribe to")
    parser.add_argument('--output-dir', required=True, help="Directory to save CSV files")
    parser.add_argument('--client-id', default="soil_sensor_integration", help="MQTT client ID")
    parser.add_argument('--use-websocket', action='store_true', help="Use MQTT over WebSocket")
    parser.add_argument('--verbosity', choices=[x.name for x in logging.Levels], default='INFO',
                        help='Logging level')
    
    return parser.parse_args()

def mqtt_callback(client, userdata, message):
    """Callback when a message is received from AWS IoT Core."""
    try:
        payload = json.loads(message.payload.decode('utf-8'))
        logger.info(f"Received message: {payload}")
        
        # Add timestamp if not present
        if 'timestamp' not in payload:
            payload['timestamp'] = datetime.now().isoformat()
        
        # Add to received messages
        received_messages.append(payload)
        
        # Process and save to CSV
        process_message(payload)
        
    except Exception as e:
        logger.error(f"Error processing message: {e}")

def process_message(message):
    """Process the received message and save to CSV files."""
    global output_directory, combined_data_file, daily_summary_file, sensor_info_file
    
    try:
        # Extract sensor ID from device_id
        device_id = message.get('device_id', 'unknown')
        sensor_id = int(device_id.split('_')[-1]) if device_id.split('_')[-1].isdigit() else 1
        
        # Create timestamp
        if isinstance(message.get('timestamp'), int):
            # Convert milliseconds to datetime
            timestamp = datetime.fromtimestamp(message['timestamp'] / 1000.0)
        else:
            # Parse ISO format timestamp
            timestamp = datetime.fromisoformat(message['timestamp'].replace('Z', '+00:00'))
        
        # Create sensor data row
        sensor_data = {
            'timestamp': timestamp,
            f'sensor_{sensor_id}_ph': message.get('ph', 0),
            f'sensor_{sensor_id}_temp': message.get('temperature', 0),
            f'sensor_{sensor_id}_humidity': message.get('moisture', 0),
            f'sensor_{sensor_id}_conductivity': message.get('conductivity', 0),
            f'sensor_{sensor_id}_nitrogen': message.get('nitrogen', 0),
            f'sensor_{sensor_id}_phosphorus': message.get('phosphorus', 0),
            f'sensor_{sensor_id}_potassium': message.get('potassium', 0),
            f'sensor_{sensor_id}_dissolved_oxygen': message.get('dissolved_oxygen', 0),
            f'sensor_{sensor_id}_turbidity': message.get('turbidity', 0)
        }
        
        # Append to combined data CSV
        combined_df = pd.DataFrame([sensor_data])
        if os.path.exists(combined_data_file):
            # Append to existing file
            combined_df.to_csv(combined_data_file, mode='a', header=False, index=False)
        else:
            # Create new file with header
            combined_df.to_csv(combined_data_file, index=False)
        
        # Update individual sensor CSV
        sensor_file = os.path.join(output_directory, f'sensor_{sensor_id}_data.csv')
        if os.path.exists(sensor_file):
            # Append to existing file
            combined_df.to_csv(sensor_file, mode='a', header=False, index=False)
        else:
            # Create new file with header
            combined_df.to_csv(sensor_file, index=False)
        
        # Update daily summary (simplified - in a real implementation, you would aggregate data)
        update_daily_summary(sensor_id, sensor_data)
        
        # Update sensor info if not exists
        update_sensor_info(sensor_id, message)
        
        logger.info(f"Data saved for sensor {sensor_id}")
        
    except Exception as e:
        logger.error(f"Error saving data to CSV: {e}")

def update_daily_summary(sensor_id, sensor_data):
    """Update the daily summary CSV file."""
    try:
        # Get today's date
        today = sensor_data['timestamp'].date()
        
        # Create daily summary row
        summary_row = {
            'date': today,
            f'sensor_{sensor_id}_ph_avg': sensor_data[f'sensor_{sensor_id}_ph'],
            f'sensor_{sensor_id}_ph_min': sensor_data[f'sensor_{sensor_id}_ph'],
            f'sensor_{sensor_id}_ph_max': sensor_data[f'sensor_{sensor_id}_ph'],
            f'sensor_{sensor_id}_temp_avg': sensor_data[f'sensor_{sensor_id}_temp'],
            f'sensor_{sensor_id}_humidity_avg': sensor_data[f'sensor_{sensor_id}_humidity'],
            f'sensor_{sensor_id}_conductivity_avg': sensor_data[f'sensor_{sensor_id}_conductivity'],
            f'sensor_{sensor_id}_nitrogen_avg': sensor_data[f'sensor_{sensor_id}_nitrogen'],
            f'sensor_{sensor_id}_phosphorus_avg': sensor_data[f'sensor_{sensor_id}_phosphorus'],
            f'sensor_{sensor_id}_potassium_avg': sensor_data[f'sensor_{sensor_id}_potassium'],
            f'sensor_{sensor_id}_dissolved_oxygen_avg': sensor_data[f'sensor_{sensor_id}_dissolved_oxygen'],
            f'sensor_{sensor_id}_turbidity_avg': sensor_data[f'sensor_{sensor_id}_turbidity']
        }
        
        # Check if daily summary file exists
        if os.path.exists(daily_summary_file):
            # Read existing data
            daily_df = pd.read_csv(daily_summary_file)
            
            # Check if today's data exists for this sensor
            today_str = today.strftime('%Y-%m-%d')
            mask = (daily_df['date'] == today_str)
            
            if mask.any():
                # Update existing row (simplified - in reality, you would calculate proper averages)
                # This is just a placeholder for demonstration
                pass
            else:
                # Append new row
                new_row_df = pd.DataFrame([summary_row])
                daily_df = pd.concat([daily_df, new_row_df], ignore_index=True)
            
            # Save updated dataframe
            daily_df.to_csv(daily_summary_file, index=False)
        else:
            # Create new file with header
            summary_df = pd.DataFrame([summary_row])
            summary_df.to_csv(daily_summary_file, index=False)
        
    except Exception as e:
        logger.error(f"Error updating daily summary: {e}")

def update_sensor_info(sensor_id, message):
    """Update the sensor info CSV file."""
    try:
        # Check if sensor info file exists
        if os.path.exists(sensor_info_file):
            # Read existing data
            info_df = pd.read_csv(sensor_info_file)
            
            # Check if this sensor exists
            if not (info_df['sensor_id'] == sensor_id).any():
                # Add new sensor info
                new_sensor = {
                    'sensor_id': sensor_id,
                    'location_name': message.get('location', f'Location {sensor_id}'),
                    'coordinates': message.get('coordinates', f'13.7°N 100.5°E'),  # Default to Bangkok
                    'water_type': message.get('soil_type', 'Clay Loam'),
                    'installation_date': datetime.now().strftime('%Y-%m-%d'),
                    'last_calibration': datetime.now().strftime('%Y-%m-%d'),
                    'maintenance_interval_days': 90
                }
                
                new_row_df = pd.DataFrame([new_sensor])
                info_df = pd.concat([info_df, new_row_df], ignore_index=True)
                info_df.to_csv(sensor_info_file, index=False)
        else:
            # Create new file with header
            new_sensor = {
                'sensor_id': sensor_id,
                'location_name': message.get('location', f'Location {sensor_id}'),
                'coordinates': message.get('coordinates', f'13.7°N 100.5°E'),  # Default to Bangkok
                'water_type': message.get('soil_type', 'Clay Loam'),
                'installation_date': datetime.now().strftime('%Y-%m-%d'),
                'last_calibration': datetime.now().strftime('%Y-%m-%d'),
                'maintenance_interval_days': 90
            }
            
            info_df = pd.DataFrame([new_sensor])
            info_df.to_csv(sensor_info_file, index=False)
        
    except Exception as e:
        logger.error(f"Error updating sensor info: {e}")

def setup_mqtt_client(args):
    """Set up and configure the MQTT client."""
    if args.use_websocket:
        client = AWSIoTMQTTClient(args.client_id, useWebsocket=True)
        client.configureEndpoint(args.endpoint, 443)
        client.configureCredentials(args.root_ca)
    else:
        client = AWSIoTMQTTClient(args.client_id)
        client.configureEndpoint(args.endpoint, 8883)
        client.configureCredentials(args.root_ca, args.key, args.cert)
    
    # Configure connection parameters
    client.configureAutoReconnectBackoffTime(1, 32, 20)
    client.configureOfflinePublishQueueing(-1)  # Infinite offline queue
    client.configureDrainingFrequency(2)  # Draining: 2 Hz
    client.configureConnectDisconnectTimeout(10)  # 10 sec
    client.configureMQTTOperationTimeout(5)  # 5 sec
    
    return client

def main():
    """Main function."""
    global output_directory, combined_data_file, daily_summary_file, sensor_info_file
    
    # Parse arguments
    args = parse_args()
    
    # Set logging level
    logger.setLevel(getattr(logging, args.verbosity))
    
    # Set up output directory
    output_directory = args.output_dir
    os.makedirs(output_directory, exist_ok=True)
    
    # Set up file paths
    combined_data_file = os.path.join(output_directory, 'combined_sensor_data.csv')
    daily_summary_file = os.path.join(output_directory, 'daily_summary.csv')
    sensor_info_file = os.path.join(output_directory, 'sensor_info.csv')
    
    # Set up MQTT client
    mqtt_client = setup_mqtt_client(args)
    
    # Connect to AWS IoT Core
    logger.info(f"Connecting to AWS IoT Core at {args.endpoint}")
    mqtt_client.connect()
    
    # Subscribe to the topic
    logger.info(f"Subscribing to topic: {args.topic}")
    mqtt_client.subscribe(args.topic, 1, mqtt_callback)
    
    # Keep the script running
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        logger.info("Disconnecting from AWS IoT Core")
        mqtt_client.disconnect()
        sys.exit(0)

if __name__ == '__main__':
    main()
