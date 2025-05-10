import streamlit as st
import pandas as pd
import os
import sys
from datetime import datetime, timedelta

# Add the current directory to the path so we can import our modules
sys.path.append(os.path.dirname(__file__))

# Import our dashboard modules
from dashboards.overview import show_overview_dashboard
from dashboards.sensor_detail import show_sensor_detail_dashboard
from dashboards.trend_analysis import show_trend_analysis_dashboard
from dashboards.anomaly_detection import show_anomaly_detection_dashboard
from dashboards.maintenance import show_maintenance_dashboard

# Import data generator
import data_generator

# Set page configuration
st.set_page_config(
    page_title="Water Quality Monitoring Dashboard",
    page_icon="💧",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Function to load data
@st.cache_data(ttl=3600)  # Cache data for 1 hour
def load_data():
    """Load sensor data from CSV files or generate if not available"""
    data_dir = os.path.join(os.path.dirname(__file__), 'data')
    
    # Check if data directory exists
    if not os.path.exists(data_dir):
        st.info("Generating sensor data... This may take a moment.")
        file_paths = data_generator.save_sensor_data(days=30, frequency_minutes=15, num_sensors=5, seed=42)
        st.success("Sensor data generated successfully!")
    
    # Load combined data
    combined_data_path = os.path.join(data_dir, 'combined_sensor_data.csv')
    if os.path.exists(combined_data_path):
        combined_data = pd.read_csv(combined_data_path)
        combined_data['timestamp'] = pd.to_datetime(combined_data['timestamp'])
    else:
        st.error("Combined sensor data not found. Please generate data first.")
        combined_data = None
    
    # Load sensor info
    sensor_info_path = os.path.join(data_dir, 'sensor_info.csv')
    if os.path.exists(sensor_info_path):
        sensor_info = pd.read_csv(sensor_info_path)
    else:
        st.error("Sensor info not found. Please generate data first.")
        sensor_info = None
    
    # Load daily summary
    daily_summary_path = os.path.join(data_dir, 'daily_summary.csv')
    if os.path.exists(daily_summary_path):
        daily_summary = pd.read_csv(daily_summary_path)
        daily_summary['date'] = pd.to_datetime(daily_summary['date'])
    else:
        st.error("Daily summary not found. Please generate data first.")
        daily_summary = None
    
    # Load individual sensor data
    individual_sensors = {}
    for i in range(1, 6):  # Assuming 5 sensors
        sensor_path = os.path.join(data_dir, f'sensor_{i}_data.csv')
        if os.path.exists(sensor_path):
            sensor_data = pd.read_csv(sensor_path)
            sensor_data['timestamp'] = pd.to_datetime(sensor_data['timestamp'])
            individual_sensors[f'sensor_{i}'] = sensor_data
    
    return {
        'combined_data': combined_data,
        'sensor_info': sensor_info,
        'daily_summary': daily_summary,
        'individual_sensors': individual_sensors
    }

def main():
    """Main function to run the Streamlit app"""
    # Add custom CSS
    st.markdown("""
    <style>
    .main-header {
        font-size: 2.5rem;
        color: #2c3e50;
        text-align: center;
        margin-bottom: 1rem;
    }
    .dashboard-container {
        background-color: #f8f9fa;
        padding: 1.5rem;
        border-radius: 0.5rem;
        box-shadow: 0 0.125rem 0.25rem rgba(0,0,0,0.075);
    }
    .stMetric {
        background-color: white;
        padding: 1rem;
        border-radius: 0.5rem;
        box-shadow: 0 0.125rem 0.25rem rgba(0,0,0,0.075);
    }
    .nav-link {
        padding: 0.5rem 1rem;
        margin-bottom: 0.5rem;
        border-radius: 0.25rem;
        text-decoration: none;
        display: block;
        text-align: left;
        font-weight: 500;
        background-color: transparent;
        border: none;
        width: 100%;
        cursor: pointer;
        transition: background-color 0.3s;
    }
    .nav-link:hover {
        background-color: rgba(0, 0, 0, 0.05);
    }
    .nav-link.active {
        background-color: #4e8df5;
        color: white;
    }
    </style>
    """, unsafe_allow_html=True)
    
    # Header
    st.markdown('<h1 class="main-header">Water Quality Monitoring Dashboard</h1>', unsafe_allow_html=True)
    
    # Load data
    data = load_data()
    
    if all(v is not None for v in data.values()):
        # Sidebar for navigation
        st.sidebar.title("Navigation")
        
        # Get the number of sensors
        num_sensors = len(data['individual_sensors'])
        
        # Dashboard selection using custom buttons
        st.sidebar.markdown("### Select Dashboard")
        
        # Define dashboard options
        dashboard_options = ["Overview", "Sensor Details", "Trend Analysis", "Anomaly Detection", "Maintenance"]
        
        # Use session state to keep track of the selected dashboard
        if 'dashboard' not in st.session_state:
            st.session_state.dashboard = "Overview"
        
        # Create custom buttons for each dashboard option
        for option in dashboard_options:
            active_class = "active" if st.session_state.dashboard == option else ""
            if st.sidebar.button(
                option, 
                key=f"btn_{option}", 
                use_container_width=True,
                help=f"View {option} dashboard"
            ):
                st.session_state.dashboard = option
        
        # Get the current dashboard from session state
        dashboard = st.session_state.dashboard
        
        # Display the selected dashboard
        if dashboard == "Overview":
            show_overview_dashboard(data)
        
        elif dashboard == "Sensor Details":
            # Sensor selection
            selected_sensor = st.sidebar.selectbox(
                "Select Sensor",
                [f"Sensor {i}" for i in range(1, num_sensors + 1)]
            )
            sensor_id = int(selected_sensor.split()[1])
            show_sensor_detail_dashboard(data, sensor_id)
        
        elif dashboard == "Trend Analysis":
            show_trend_analysis_dashboard(data)
        
        elif dashboard == "Anomaly Detection":
            show_anomaly_detection_dashboard(data)
        
        elif dashboard == "Maintenance":
            show_maintenance_dashboard(data)
        
        # Footer
        st.sidebar.markdown("---")
        st.sidebar.info(
            "This dashboard visualizes water quality sensor data including pH, temperature, "
            "conductivity, dissolved oxygen, and turbidity measurements from multiple sensors."
        )
        
        # Data last updated
        if data['combined_data'] is not None and not data['combined_data'].empty:
            last_updated = data['combined_data']['timestamp'].max()
            st.sidebar.text(f"Data last updated: {last_updated}")
    
    else:
        st.error("Failed to load all required data. Please check the data generation process.")
        
        # Button to generate data
        if st.button("Generate Sample Data"):
            st.info("Generating sensor data... This may take a moment.")
            file_paths = data_generator.save_sensor_data(days=30, frequency_minutes=15, num_sensors=5, seed=42)
            st.success("Sensor data generated successfully! Please refresh the page.")

if __name__ == "__main__":
    main()
