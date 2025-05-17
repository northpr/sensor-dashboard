# Fake Soil Sensor Data Generator for AWS IoT Core

This directory contains a Python script that generates fake soil sensor data and publishes it to AWS IoT Core.

## Prerequisites

1. AWS IoT Core setup with a Thing and certificates
2. Python 3.6 or higher
3. AWSIoTPythonSDK package

## Installation

```bash
pip install AWSIoTPythonSDK
```

## Usage

```bash
python fake_data_generator.py \
  --endpoint <aws-iot-endpoint> \
  --root-ca <root-ca-path> \
  --cert <cert-path> \
  --key <private-key-path> \
  --client-id ESP32_Soil_Sensor_1 \
  --topic soil/sensors \
  --interval 60 \
  --location "Chiang Mai Rice Field"
```

### Parameters

- `--endpoint`: Your AWS IoT Core endpoint (required)
- `--root-ca`: Path to your root CA certificate file (required)
- `--cert`: Path to your device certificate file (required)
- `--key`: Path to your private key file (required)
- `--client-id`: MQTT client ID (default: "ESP32_Soil_Sensor_1")
- `--topic`: MQTT topic to publish to (default: "soil/sensors")
- `--interval`: Interval between readings in seconds (default: 60)
- `--location`: Sensor location name (default: "Chiang Mai Rice Field")
- `--verbosity`: Logging level (default: "INFO")

## Data Format

The script generates fake readings for the following soil parameters:

- pH (5.5-7.5)
- Temperature (15-30°C)
- Moisture (20-80%)
- Conductivity (100-500 μS/cm)
- Dissolved Oxygen (5-9 mg/L)
- Turbidity (0-20 NTU)

Each reading is published as a JSON message with the following format:

```json
{
  "timestamp": "2023-05-17T15:30:45.123456",
  "device_id": "ESP32_Soil_Sensor_1",
  "location": "Chiang Mai Rice Field",
  "ph": 6.8,
  "temperature": 25.3,
  "moisture": 45.7,
  "conductivity": 320.5,
  "dissolved_oxygen": 7.2,
  "turbidity": 12.5
}
```

## Customizing Parameters

You can customize the parameter ranges by modifying the `DEFAULT_PARAMS` dictionary in the script:

```python
DEFAULT_PARAMS = {
    "ph": {
        "min": 5.5,
        "max": 7.5,
        "drift": 0.1,
        "unit": ""
    },
    # Add or modify other parameters as needed
}
```

- `min` and `max`: The range of values for the parameter
- `drift`: The maximum amount the value can change between readings
- `unit`: The unit of measurement for display purposes
