# Water Quality Sensor Dashboard

A comprehensive dashboard for monitoring and analyzing water quality sensor data. This project includes data generation, visualization, and analysis tools for pH, temperature, conductivity, dissolved oxygen, and turbidity measurements.

## Features

- **Data Generation**: Realistic sensor data generation with configurable parameters
- **Interactive Dashboards**: 5 different dashboards for comprehensive monitoring
  - **Overview Dashboard**: High-level summary of all sensors
  - **Sensor Detail Dashboard**: Detailed analysis of individual sensors
  - **Trend Analysis Dashboard**: Time series analysis and pattern detection
  - **Anomaly Detection Dashboard**: Identification of unusual readings
  - **Maintenance Dashboard**: Calibration schedules and sensor health monitoring

## Installation

1. Clone this repository:
```bash
git clone https://github.com/yourusername/sensor-dashboard.git
cd sensor-dashboard
```

2. Install the required dependencies:
```bash
pip install -r requirements.txt
```

## Usage

1. Run the Streamlit application:
```bash
cd app
streamlit run app.py
```

2. The application will automatically generate sample data if none exists.

3. Navigate through the different dashboards using the sidebar.

## Project Structure

```
sensor-dashboard/
├── app/
│   ├── data/                  # Directory for storing generated CSV files
│   ├── dashboards/            # Dashboard modules
│   │   ├── overview.py        # Overview dashboard
│   │   ├── sensor_detail.py   # Sensor detail dashboard
│   │   ├── trend_analysis.py  # Trend analysis dashboard
│   │   ├── anomaly_detection.py # Anomaly detection dashboard
│   │   ├── maintenance.py     # Maintenance dashboard
│   │   └── __init__.py        # Package initialization
│   ├── app.py                 # Main Streamlit application
│   └── data_generator.py      # Data generation module
├── requirements.txt           # Project dependencies
└── README.md                  # Project documentation
```

## Data Generation

The `data_generator.py` module generates realistic sensor data with the following parameters:

- pH (0-14 scale)
- Temperature (°C)
- Conductivity (μS/cm)
- Dissolved Oxygen (mg/L)
- Turbidity (NTU)

The data includes daily and weekly patterns, random fluctuations, and occasional anomalies to simulate real-world conditions.

## Dashboards

### Overview Dashboard
Provides a high-level summary of all sensors, including a map view, latest readings, and daily trends.

### Sensor Detail Dashboard
Offers detailed analysis of individual sensors, including time series data, hourly patterns, correlations between parameters, and statistical analysis.

### Trend Analysis Dashboard
Enables time series analysis, seasonal pattern detection, correlation analysis, and trend detection using statistical methods.

### Anomaly Detection Dashboard
Implements multiple anomaly detection methods (Z-score, IQR, Rolling Z-score) to identify unusual readings in the sensor data.

### Maintenance Dashboard
Tracks calibration schedules, sensor health, and maintenance history to ensure optimal sensor performance.

## Deployment

This application can be deployed to AWS using various services:

1. **Amazon EC2**: Deploy as a standalone application
2. **AWS Elastic Beanstalk**: Simplified deployment and scaling
3. **AWS App Runner**: Fully managed service for containerized applications

## License

This project is licensed under the MIT License - see the LICENSE file for details.
