# Soil Sensor Data Generator for AWS IoT Core

This project contains code for generating fake soil sensor data and sending it to AWS IoT Core, then integrating the data with the soil quality monitoring dashboard.

## Project Structure

- `esp32/` - Contains the fake data generator script
- `integration/` - Contains scripts for integrating with the dashboard

## Quick Start

### 1. Generate Fake Data and Send to AWS IoT Core

1. Install the required Python package:
   ```bash
   pip install AWSIoTPythonSDK
   ```

2. Set up AWS IoT Core (see detailed instructions in [esp32/README.md](esp32/README.md))

3. Run the fake data generator:
   ```bash
   cd esp32
   python fake_data_generator.py \
     --endpoint <aws-iot-endpoint> \
     --root-ca <root-ca-path> \
     --cert <cert-path> \
     --key <private-key-path>
   ```

### 2. Integrate with the Dashboard

1. In a separate terminal, install the required packages:
   ```bash
   cd integration
   pip install -r requirements.txt
   ```

2. Run the integration script:
   ```bash
   python aws_to_csv.py \
     --endpoint <aws-iot-endpoint> \
     --root-ca <root-ca-path> \
     --cert <cert-path> \
     --key <private-key-path> \
     --topic soil/sensors \
     --output-dir ../../app/data
   ```

### 3. Run the Dashboard

```bash
cd ../../app
streamlit run run_dashboard.py
```

## Data Flow

1. The fake data generator (`esp32/fake_data_generator.py`) generates soil sensor readings and publishes them to AWS IoT Core.
2. The integration script (`integration/aws_to_csv.py`) subscribes to the same topic and saves the data to CSV files.
3. The dashboard reads the CSV files and displays the data.

## Troubleshooting

- **Connection Issues**: Ensure your AWS IoT endpoint is correct and your certificates have the right permissions.
- **Data Not Appearing**: Check that you're subscribed to the correct topic in the MQTT test client.
- **Integration Issues**: Verify that the integration script is running and pointing to the correct output directory.
