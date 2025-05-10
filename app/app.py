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
    page_title="ระบบติดตามคุณภาพดิน",
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
        st.info("กำลังสร้างข้อมูลเซ็นเซอร์... กรุณารอสักครู่")
        file_paths = data_generator.save_sensor_data(days=30, frequency_minutes=15, num_sensors=5, seed=42)
        st.success("สร้างข้อมูลเซ็นเซอร์สำเร็จแล้ว!")
    
    # Load combined data
    combined_data_path = os.path.join(data_dir, 'combined_sensor_data.csv')
    if os.path.exists(combined_data_path):
        combined_data = pd.read_csv(combined_data_path)
        combined_data['timestamp'] = pd.to_datetime(combined_data['timestamp'])
    else:
        st.error("ไม่พบข้อมูลเซ็นเซอร์รวม กรุณาสร้างข้อมูลก่อน")
        combined_data = None
    
    # Load sensor info
    sensor_info_path = os.path.join(data_dir, 'sensor_info.csv')
    if os.path.exists(sensor_info_path):
        sensor_info = pd.read_csv(sensor_info_path)
    else:
        st.error("ไม่พบข้อมูลเซ็นเซอร์ กรุณาสร้างข้อมูลก่อน")
        sensor_info = None
    
    # Load daily summary
    daily_summary_path = os.path.join(data_dir, 'daily_summary.csv')
    if os.path.exists(daily_summary_path):
        daily_summary = pd.read_csv(daily_summary_path)
        daily_summary['date'] = pd.to_datetime(daily_summary['date'])
    else:
        st.error("ไม่พบข้อมูลสรุปรายวัน กรุณาสร้างข้อมูลก่อน")
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
    st.markdown('<h1 class="main-header">ระบบติดตามคุณภาพดิน</h1>', unsafe_allow_html=True)
    
    # Load data
    data = load_data()
    
    if all(v is not None for v in data.values()):
        # Sidebar for navigation
        st.sidebar.title("เมนู")
        
        # Get the number of sensors
        num_sensors = len(data['individual_sensors'])
        
        # Dashboard selection using custom buttons
        st.sidebar.markdown("### เลือกแดชบอร์ด")
        
        # Define dashboard options
        dashboard_options = ["ภาพรวม", "รายละเอียดเซ็นเซอร์", "การวิเคราะห์แนวโน้ม", "การตรวจจับความผิดปกติ", "การบำรุงรักษา"]
        
        # Use session state to keep track of the selected dashboard
        if 'dashboard' not in st.session_state:
            st.session_state.dashboard = "ภาพรวม"
        
        # Create custom buttons for each dashboard option
        for option in dashboard_options:
            active_class = "active" if st.session_state.dashboard == option else ""
            if st.sidebar.button(
                option, 
                key=f"btn_{option}", 
                use_container_width=True,
                help=f"ดูแดชบอร์ด{option}"
            ):
                st.session_state.dashboard = option
        
        # Get the current dashboard from session state
        dashboard = st.session_state.dashboard
        
        # Display the selected dashboard
        if dashboard == "ภาพรวม":
            show_overview_dashboard(data)
        
        elif dashboard == "รายละเอียดเซ็นเซอร์":
            # Sensor selection
            selected_sensor = st.sidebar.selectbox(
                "เลือกเซ็นเซอร์",
                [f"เซ็นเซอร์ {i}" for i in range(1, num_sensors + 1)]
            )
            sensor_id = int(selected_sensor.split()[1])
            show_sensor_detail_dashboard(data, sensor_id)
        
        elif dashboard == "การวิเคราะห์แนวโน้ม":
            show_trend_analysis_dashboard(data)
        
        elif dashboard == "การตรวจจับความผิดปกติ":
            show_anomaly_detection_dashboard(data)
        
        elif dashboard == "การบำรุงรักษา":
            show_maintenance_dashboard(data)
        
        # Footer
        st.sidebar.markdown("---")
        st.sidebar.info(
            "แดชบอร์ดนี้แสดงข้อมูลคุณภาพดินจากเซ็นเซอร์ ประกอบด้วย ค่า pH, ความชื้น, "
            "อุณหภูมิ, ค่าการนำไฟฟ้า, ไนโตรเจน, ฟอสฟอรัส, โพแทสเซียม และค่าอื่นๆ จากเซ็นเซอร์หลายตัว"
        )
        
        # Data last updated
        if data['combined_data'] is not None and not data['combined_data'].empty:
            last_updated = data['combined_data']['timestamp'].max()
            st.sidebar.text(f"ข้อมูลอัปเดตล่าสุด: {last_updated}")
    
    else:
        st.error("ไม่สามารถโหลดข้อมูลที่จำเป็นได้ กรุณาตรวจสอบกระบวนการสร้างข้อมูล")
        
        # Button to generate data
        if st.button("สร้างข้อมูลตัวอย่าง"):
            st.info("กำลังสร้างข้อมูลเซ็นเซอร์... กรุณารอสักครู่")
            file_paths = data_generator.save_sensor_data(days=30, frequency_minutes=15, num_sensors=5, seed=42)
            st.success("สร้างข้อมูลเซ็นเซอร์สำเร็จแล้ว! กรุณารีเฟรชหน้าเว็บ")

if __name__ == "__main__":
    main()
