# Soil Sensor Data Generator - Step by Step Guide

This guide will walk you through the process of generating fake soil sensor data, sending it to AWS IoT Core, and integrating it with your dashboard.

## Prerequisites

- AWS account with access to AWS IoT Core
- Python 3.6 or higher
- Basic knowledge of command line operations

## Step 1: Set Up AWS IoT Core

1. **Sign in to the AWS Management Console**
   - Go to https://aws.amazon.com/console/
   - Sign in with your AWS account

2. **Navigate to AWS IoT Core**
   - Search for "IoT Core" in the AWS services search bar
   - Click on "IoT Core"

3. **Create a Thing**
   - In the left navigation pane, click on "Manage" > "Things"
   - Click "Create things"
   - Choose "Create a single thing"
   - Name it (e.g., "ESP32_Soil_Sensor_1")
   - Click "Next"

4. **Create a Certificate**
   - Choose "Auto-generate a new certificate"
   - Click "Next"

5. **Download Certificates**
   - Download all three files:
     - Device certificate
     - Public key
     - Private key
   - Also download the root CA certificate (Amazon Root CA 1)
   - Save these files in a secure location (e.g., `~/aws-iot-certs/`)
   - Click "Activate" to activate the certificate
   - Click "Attach a policy"

6. **Create a Policy**
   - Click "Create policy"
   - Name it (e.g., "ESP32_Soil_Sensor_Policy")
   - In the policy document, add:
   ```json
   {
     "Version": "2012-10-17",
     "Statement": [
       {
         "Effect": "Allow",
         "Action": "iot:Connect",
         "Resource": "*"
       },
       {
         "Effect": "Allow",
         "Action": "iot:Publish",
         "Resource": "arn:aws:iot:*:*:topic/soil/sensors"
       },
       {
         "Effect": "Allow",
         "Action": "iot:Subscribe",
         "Resource": "arn:aws:iot:*:*:topicfilter/soil/sensors"
       },
       {
         "Effect": "Allow",
         "Action": "iot:Receive",
         "Resource": "arn:aws:iot:*:*:topic/soil/sensors"
       }
     ]
   }
   ```
   - Click "Create"
   - Attach this policy to your certificate

7. **Note Your AWS IoT Endpoint**
   - In the left navigation pane, click on "Settings"
   - Copy your "Endpoint" (it looks like `xxxxxxx-ats.iot.region.amazonaws.com`)

## Step 2: Generate Fake Data and Send to AWS IoT Core

1. **Install Required Python Package**
   ```bash
   pip install AWSIoTPythonSDK
   ```

2. **Run the Fake Data Generator**
   ```bash
   cd device_code/esp32
   python fake_data_generator.py \
     --endpoint <your-aws-iot-endpoint> \
     --root-ca <path-to-root-ca> \
     --cert <path-to-certificate> \
     --key <path-to-private-key> \
     --client-id ESP32_Soil_Sensor_1 \
     --topic soil/sensors \
     --interval 60
   ```

   Replace the placeholders:
   - `<your-aws-iot-endpoint>`: Your AWS IoT endpoint from Step 1.7
   - `<path-to-root-ca>`: Path to the root CA certificate (e.g., `~/aws-iot-certs/AmazonRootCA1.pem`)
   - `<path-to-certificate>`: Path to your device certificate (e.g., `~/aws-iot-certs/device.pem.crt`)
   - `<path-to-private-key>`: Path to your private key (e.g., `~/aws-iot-certs/private.pem.key`)

3. **Verify Data in AWS IoT Core**
   - In the AWS IoT Core console, go to "Test" > "MQTT test client"
   - In "Subscribe to a topic", enter "soil/sensors"
   - Click "Subscribe"
   - You should see messages appearing at the interval you specified

## Step 3: Integrate with the Dashboard

1. **Install Required Python Packages**
   ```bash
   cd ../integration
   pip install -r requirements.txt
   ```

2. **Run the Integration Script**
   ```bash
   python aws_to_csv.py \
     --endpoint <your-aws-iot-endpoint> \
     --root-ca <path-to-root-ca> \
     --cert <path-to-certificate> \
     --key <path-to-private-key> \
     --topic soil/sensors \
     --output-dir ../../app/data
   ```

   Use the same certificate paths as in Step 2.2.

## Step 4: Run the Dashboard

```bash
cd ../../app
streamlit run run_dashboard.py
```

The dashboard should now display the fake sensor data.

## Troubleshooting

- **Connection Issues**: Ensure your AWS IoT endpoint is correct and your certificates have the right permissions.
- **Data Not Appearing**: Check that you're subscribed to the correct topic in the MQTT test client.
- **Integration Issues**: Verify that the integration script is running and pointing to the correct output directory.

## Next Steps

Once you have this working with fake data, you can:
1. Set up a real ESP32 with soil sensors
2. Modify the integration to use AWS Lambda or direct database integration
3. Customize the dashboard to display your specific soil parameters
