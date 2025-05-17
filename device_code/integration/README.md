# AWS IoT Core to Dashboard Integration

This directory contains scripts to integrate data from AWS IoT Core with the soil quality monitoring dashboard.

## AWS to CSV Integration

The `aws_to_csv.py` script subscribes to an AWS IoT Core MQTT topic where sensor data is published, processes the data, and saves it to CSV files compatible with the dashboard.

### Prerequisites

1. AWS IoT Core setup with a Thing representing your soil sensor
2. Python 3.6 or higher
3. Required Python packages (install using `pip install -r requirements.txt`)

### Installation

1. Clone this repository
2. Navigate to the integration directory
3. Install the required packages:

```bash
pip install -r requirements.txt
```

### Configuration

Before running the script, you need to:

1. Download your AWS IoT Core certificates:
   - Root CA certificate
   - Device certificate
   - Private key

2. Note your AWS IoT Core endpoint (found in AWS IoT Core > Settings)

### Usage

Run the script with the following command:

```bash
python aws_to_csv.py \
  --endpoint <aws-iot-endpoint> \
  --root-ca <root-ca-path> \
  --cert <cert-path> \
  --key <private-key-path> \
  --topic soil/sensors \
  --output-dir ../../app/data
```

Replace the placeholders with your actual values:
- `<aws-iot-endpoint>`: Your AWS IoT Core endpoint (e.g., `a1b2c3d4e5f6g7.iot.us-east-1.amazonaws.com`)
- `<root-ca-path>`: Path to your root CA certificate file
- `<cert-path>`: Path to your device certificate file
- `<private-key-path>`: Path to your private key file
- The output directory should point to the dashboard's data directory

### Running as a Service

For continuous operation, you can set up the script to run as a service:

#### Linux (systemd)

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
ExecStart=/usr/bin/python3 /path/to/aws_to_csv.py --endpoint <aws-iot-endpoint> --root-ca <root-ca-path> --cert <cert-path> --key <private-key-path> --topic soil/sensors --output-dir /path/to/app/data
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

#### Windows

1. Create a batch file (e.g., `start_integration.bat`):

```batch
@echo off
python aws_to_csv.py --endpoint <aws-iot-endpoint> --root-ca <root-ca-path> --cert <cert-path> --key <private-key-path> --topic soil/sensors --output-dir ..\..\app\data
```

2. Use Task Scheduler to run this batch file at startup

### Data Format

The script expects JSON messages from the soil sensors with the following format:

```json
{
  "device_id": "ESP32_Soil_Sensor_1",
  "timestamp": "2023-05-17T14:30:00Z",
  "moisture": 45.2,
  "temperature": 22.5,
  "ph": 6.8,
  "conductivity": 350.5,
  "nitrogen": 12.3,
  "phosphorus": 5.6,
  "potassium": 8.9,
  "dissolved_oxygen": 7.2,
  "turbidity": 12.5
}
```

Not all fields are required, but at minimum, the message should include:
- `device_id`: Identifier for the sensor
- At least one sensor reading (e.g., `moisture`, `temperature`, `ph`)

### Troubleshooting

1. **Connection Issues**:
   - Verify your AWS IoT Core endpoint is correct
   - Check that your certificates are valid and have the correct permissions
   - Ensure your device has internet connectivity

2. **Data Not Appearing in Dashboard**:
   - Check that the output directory is correct
   - Verify that the CSV files are being created and updated
   - Restart the dashboard application to load new data

3. **Script Crashes**:
   - Check the logs for error messages
   - Verify that you have the correct Python version and all dependencies installed

## Other Integration Methods

### AWS Lambda Integration

For a more serverless approach, you can use AWS Lambda to process the MQTT messages and store them in a database:

1. Create an AWS IoT Rule to trigger a Lambda function when messages are received on your topic
2. The Lambda function processes the data and stores it in a database (e.g., DynamoDB)
3. Configure the dashboard to read from this database

### Direct Database Integration

For real-time applications:

1. Set up an AWS IoT Rule to directly insert data into a database
2. Configure the dashboard to read from this database
3. This approach eliminates the need for the integration script

## Security Considerations

- Store your AWS credentials and certificates securely
- Do not commit sensitive information to version control
- Use IAM roles with the principle of least privilege
- Consider using AWS Secrets Manager for credential management
