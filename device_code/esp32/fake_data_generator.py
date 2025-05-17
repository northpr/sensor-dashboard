#!/usr/bin/env python3
"""
Fake Soil Sensor Data Generator for AWS IoT Core

This script generates fake soil sensor data and publishes it to AWS IoT Core.
It simulates an ESP32 device sending soil quality measurements.

Requirements:
- AWSIoTPythonSDK
- json
- random
- time
- datetime

Usage:
python fake_data_generator.py --endpoint <aws-iot-endpoint> --root-ca <root-ca-path> --cert <cert-path> --key <private-key-path> --client-id ESP32_Soil_Sensor_1 --topic soil/sensors
"""

import argparse
import json
import logging
import time
import random
from datetime import datetime
from AWSIoTPythonSDK.MQTTLib import AWSIoTMQTTClient

# Configure logging
logger = logging.getLogger("AWSIoTLogger")
logger.setLevel(logging.INFO)
streamHandler = logging.StreamHandler()
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
streamHandler.setFormatter(formatter)
logger.addHandler(streamHandler)

# Default values for soil parameters
DEFAULT_PARAMS = {
    "ph": {
        "min": 5.5,
        "max": 7.5,
        "drift": 0.1,
        "unit": ""
    },
    "temperature": {
        "min": 15.0,
        "max": 30.0,
        "drift": 0.5,
        "unit": "°C"
    },
    "moisture": {
        "min": 20.0,
        "max": 80.0,
        "drift": 2.0,
        "unit": "%"
    },
    "conductivity": {
        "min": 100.0,
        "max": 500.0,
        "drift": 10.0,
        "unit": "μS/cm"
    },
    "dissolved_oxygen": {
        "min": 5.0,
        "max": 9.0,
        "drift": 0.3,
        "unit": "mg/L"
    },
    "turbidity": {
        "min": 0.0,
        "max": 20.0,
        "drift": 1.0,
        "unit": "NTU"
    }
}

# Current values for each parameter (will be updated with each reading)
current_values = {}

def parse_args():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser()
    parser.add_argument('--endpoint', required=True, help="Your AWS IoT custom endpoint")
    parser.add_argument('--root-ca', required=True, help="Root CA file path")
    parser.add_argument('--cert', required=True, help="Certificate file path")
    parser.add_argument('--key', required=True, help="Private key file path")
    parser.add_argument('--client-id', default="ESP32_Soil_Sensor_1", help="MQTT client ID")
    parser.add_argument('--topic', default="soil/sensors", help="MQTT topic to publish to")
    parser.add_argument('--interval', type=int, default=60, help="Interval between readings in seconds")
    parser.add_argument('--location', default="Chiang Mai Rice Field", help="Sensor location name")
    parser.add_argument('--verbosity', choices=['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'], 
                        default='INFO', help='Logging level')
    
    return parser.parse_args()

def initialize_values():
    """Initialize the current values for each parameter."""
    global current_values
    
    for param, config in DEFAULT_PARAMS.items():
        # Start with a random value within the range
        current_values[param] = random.uniform(config["min"], config["max"])

def generate_reading():
    """Generate a fake sensor reading."""
    global current_values
    
    reading = {
        "timestamp": datetime.now().isoformat(),
        "device_id": args.client_id,
        "location": args.location
    }
    
    # Update each parameter with some random drift
    for param, config in DEFAULT_PARAMS.items():
        # Add some random drift to the current value
        drift = random.uniform(-config["drift"], config["drift"])
        new_value = current_values[param] + drift
        
        # Ensure the value stays within the defined range
        new_value = max(config["min"], min(config["max"], new_value))
        
        # Update the current value
        current_values[param] = new_value
        
        # Add to the reading
        reading[param] = round(new_value, 2)
    
    return reading

def setup_mqtt_client(args):
    """Set up and configure the MQTT client."""
    # Initialize the MQTT client
    mqtt_client = AWSIoTMQTTClient(args.client_id)
    
    # Configure the endpoint and credentials
    mqtt_client.configureEndpoint(args.endpoint, 8883)
    mqtt_client.configureCredentials(args.root_ca, args.key, args.cert)
    
    # Configure connection parameters
    mqtt_client.configureAutoReconnectBackoffTime(1, 32, 20)
    mqtt_client.configureOfflinePublishQueueing(-1)  # Infinite offline queue
    mqtt_client.configureDrainingFrequency(2)  # Draining: 2 Hz
    mqtt_client.configureConnectDisconnectTimeout(10)  # 10 sec
    mqtt_client.configureMQTTOperationTimeout(5)  # 5 sec
    
    return mqtt_client

def main():
    """Main function."""
    # Set logging level
    logger.setLevel(getattr(logging, args.verbosity))
    
    # Initialize sensor values
    initialize_values()
    
    # Set up MQTT client
    mqtt_client = setup_mqtt_client(args)
    
    # Connect to AWS IoT Core
    logger.info(f"Connecting to AWS IoT Core at {args.endpoint}")
    mqtt_client.connect()
    
    try:
        while True:
            # Generate a fake reading
            reading = generate_reading()
            
            # Convert to JSON
            message = json.dumps(reading)
            
            # Publish to AWS IoT Core
            logger.info(f"Publishing: {message}")
            mqtt_client.publish(args.topic, message, 1)
            
            # Print the current values with units
            print("\nCurrent Soil Sensor Readings:")
            print("-" * 30)
            for param, value in reading.items():
                if param in DEFAULT_PARAMS:
                    unit = DEFAULT_PARAMS[param]["unit"]
                    print(f"{param.capitalize()}: {value} {unit}")
            print("-" * 30)
            
            # Wait for the next interval
            logger.info(f"Waiting {args.interval} seconds until next reading...")
            time.sleep(args.interval)
            
    except KeyboardInterrupt:
        logger.info("Disconnecting from AWS IoT Core")
        mqtt_client.disconnect()

if __name__ == "__main__":
    # Parse arguments
    args = parse_args()
    main()
