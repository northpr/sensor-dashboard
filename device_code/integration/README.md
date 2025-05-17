# AWS IoT Core to Dashboard Integration

This directory contains a script that subscribes to AWS IoT Core messages and saves them to CSV files for the dashboard.

## Prerequisites

- AWS IoT Core setup with a Thing and certificates
- Python 3.6 or higher
- Required Python packages (listed in requirements.txt)

## Installation

```bash
pip install -r requirements.txt
```

## Usage

```bash
python aws_to_csv.py \
  --endpoint <aws-iot-endpoint> \
  --root-ca <path-to-root-ca> \
  --cert <path-to-certificate> \
  --key <path-to-private-key> \
  --topic soil/sensors \
  --output-dir ../../app/data
```

### Parameters

- `--endpoint`: Your AWS IoT Core endpoint (required)
- `--root-ca`: Path to your root CA certificate file (required)
- `--cert`: Path to your device certificate file (required)
- `--key`: Path to your private key file (required)
- `--topic`: MQTT topic to subscribe to (default: "soil/sensors")
- `--output-dir`: Directory to save CSV files (default: "../../app/data")

## How It Works

1. The script connects to AWS IoT Core using the provided certificates
2. It subscribes to the specified MQTT topic
3. When messages are received, it processes them and saves the data to CSV files:
   - combined_sensor_data.csv - All sensor data
   - sensor_X_data.csv - Data for each individual sensor
   - daily_summary.csv - Daily summary statistics
   - sensor_info.csv - Information about each sensor

## Running as a Service

For continuous operation, you can set up the script to run as a service:

### Linux (systemd)

1. Create a service file:

```bash
sudo nano /etc/systemd/system/aws-soil-integration.service
```

2. Add the following content:

```
[Unit]
Description=AWS IoT to Soil Dashboard Integration
After=network.target

[Service]
ExecStart=/usr/bin/python3 /path/to/aws_to_csv.py --endpoint <aws-iot-endpoint> --root-ca <path-to-root-ca> --cert <path-to-certificate> --key <path-to-private-key> --topic soil/sensors --output-dir /path/to/app/data
Restart=always
User=<your-username>
Group=<your-group>
Environment=PATH=/usr/bin:/usr/local/bin
WorkingDirectory=/path/to/integration

[Install]
WantedBy=multi-user.target
```

3. Enable and start the service:

```bash
sudo systemctl enable aws-soil-integration.service
sudo systemctl start aws-soil-integration.service
```

## Troubleshooting

- **Connection Issues**: Ensure your AWS IoT endpoint is correct and your certificates have the right permissions
- **Data Not Appearing**: Check that you're subscribed to the correct topic
- **CSV Files Not Created**: Verify that the output directory exists and is writable
