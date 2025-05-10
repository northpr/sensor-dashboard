import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta

def show_overview_dashboard(data):
    """
    Display the overview dashboard showing summary of all sensors.
    
    Parameters:
    - data: Dictionary containing all sensor data
    """
    st.header("แดชบอร์ดภาพรวม")
    st.markdown("แดชบอร์ดนี้แสดงภาพรวมของเซ็นเซอร์วัดคุณภาพดินทั้งหมด")
    
    # Get the data
    combined_data = data['combined_data']
    sensor_info = data['sensor_info']
    daily_summary = data['daily_summary']
    
    # Get the latest data for each sensor
    latest_data = combined_data.iloc[-1].copy()
    
    # Create columns for the metrics
    col1, col2, col3, col4, col5 = st.columns(5)
    
    # Display the number of sensors
    num_sensors = len([col for col in combined_data.columns if col.endswith('_ph')])
    col1.metric("จำนวนเซ็นเซอร์", num_sensors)
    
    # Display the total number of readings
    total_readings = len(combined_data)
    col2.metric("จำนวนการอ่านค่าทั้งหมด", f"{total_readings:,}")
    
    # Display the date range
    start_date = combined_data['timestamp'].min().date()
    end_date = combined_data['timestamp'].max().date()
    date_range = f"{start_date} ถึง {end_date}"
    col3.metric("ช่วงวันที่", date_range)
    
    # Display the average reading frequency
    time_diff = combined_data['timestamp'].diff().mean()
    minutes = int(time_diff.total_seconds() / 60)
    col4.metric("ความถี่การอ่านค่าเฉลี่ย", f"{minutes} นาที")
    
    # Display the last update time
    last_update = combined_data['timestamp'].max()
    col5.metric("อัปเดตล่าสุด", last_update.strftime("%Y-%m-%d %H:%M"))
    
    st.markdown("---")
    
    # Create two columns for the map and sensor info
    col1, col2 = st.columns([3, 2])
    
    with col1:
        st.subheader("ตำแหน่งเซ็นเซอร์")
        
        # Create a dataframe for the map
        map_data = sensor_info.copy()
        
        # Extract latitude and longitude from coordinates
        map_data['latitude'] = map_data['coordinates'].apply(
            lambda x: float(x.split('°')[0].strip())
        )
        map_data['longitude'] = map_data['coordinates'].apply(
            lambda x: float(x.split('°')[1].strip().split(' ')[1])
        )
        
        # Add latest pH values
        for i, row in map_data.iterrows():
            sensor_id = row['sensor_id']
            ph_col = f'sensor_{sensor_id}_ph'
            if ph_col in latest_data:
                map_data.loc[i, 'latest_ph'] = latest_data[ph_col]
                
                # Add color based on pH value
                ph = latest_data[ph_col]
                if ph < 6.5:
                    map_data.loc[i, 'status'] = "เป็นกรด"
                    map_data.loc[i, 'color'] = "red"
                elif ph > 8.5:
                    map_data.loc[i, 'status'] = "เป็นด่าง"
                    map_data.loc[i, 'color'] = "purple"
                else:
                    map_data.loc[i, 'status'] = "ปกติ"
                    map_data.loc[i, 'color'] = "green"
        
        # Create a new column for hover text that includes soil type
        map_data['hover_text'] = map_data.apply(
            lambda row: f"ประเภทดิน: {row['water_type']}<br>pH: {row['latest_ph']:.2f}<br>สถานะ: {row['status']}",
            axis=1
        )
        
        # Create the map centered on Thailand using Scattermapbox directly
        fig = go.Figure()
        
        # Add points for each sensor
        for status in ["ปกติ", "เป็นกรด", "เป็นด่าง"]:
            df_status = map_data[map_data['status'] == status]
            if not df_status.empty:
                fig.add_trace(go.Scattermapbox(
                    lat=df_status['latitude'],
                    lon=df_status['longitude'],
                    mode='markers',
                    marker=dict(
                        size=15,
                        color={"ปกติ": "green", "เป็นกรด": "red", "เป็นด่าง": "purple"}[status]
                    ),
                    text=df_status['location_name'],
                    hovertext=df_status['hover_text'],
                    hoverinfo='text',
                    name=status
                ))
        
        # Set map layout
        fig.update_layout(
            mapbox=dict(
                style="open-street-map",
                center={"lat": 15.8700, "lon": 100.9925},  # Center on Thailand
                zoom=5
            ),
            margin={"r": 0, "t": 0, "l": 0, "b": 0},
            height=400,
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=1.02,
                xanchor="right",
                x=1
            )
        )
        
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.subheader("ข้อมูลเซ็นเซอร์")
        
        # Display sensor info in a table with renamed columns
        sensor_table = sensor_info[['sensor_id', 'location_name', 'water_type', 'last_calibration']].copy()
        sensor_table.columns = ['รหัสเซ็นเซอร์', 'ตำแหน่ง', 'ประเภทดิน', 'การปรับเทียบล่าสุด']
        st.dataframe(
            sensor_table,
            use_container_width=True
        )
        
        # Display a pie chart of soil types
        soil_type_counts = sensor_info['water_type'].value_counts().reset_index()
        soil_type_counts.columns = ['ประเภทดิน', 'จำนวน']
        
        fig = px.pie(
            soil_type_counts,
            values='จำนวน',
            names='ประเภทดิน',
            title='เซ็นเซอร์ตามประเภทดิน',
            hole=0.4
        )
        
        st.plotly_chart(fig, use_container_width=True)
    
    st.markdown("---")
    
    # Create a section for the latest readings
    st.subheader("ค่าล่าสุดจากเซ็นเซอร์")
    
    # Create a dataframe for the latest readings
    latest_readings = []
    
    for i in range(1, num_sensors + 1):
        sensor_data = {}
        sensor_data['รหัสเซ็นเซอร์'] = i
        
        # Get the location name
        sensor_info_row = sensor_info[sensor_info['sensor_id'] == i]
        if not sensor_info_row.empty:
            sensor_data['ตำแหน่ง'] = sensor_info_row['location_name'].values[0]
        else:
            sensor_data['ตำแหน่ง'] = f"เซ็นเซอร์ {i}"
        
        # Get the latest readings in the specified order
        # pH first, followed by humidity and temperature, then the rest
        for param in ['ph', 'humidity', 'temp', 'conductivity', 'nitrogen', 'phosphorus', 'potassium', 'dissolved_oxygen', 'turbidity']:
            col = f'sensor_{i}_{param}'
            if col in latest_data:
                # Format the parameter name for display
                if param == 'ph':
                    param_name = 'pH'
                elif param == 'temp':
                    param_name = 'อุณหภูมิ'
                elif param == 'humidity':
                    param_name = 'ความชื้น'
                elif param == 'conductivity':
                    param_name = 'การนำไฟฟ้า'
                elif param == 'nitrogen':
                    param_name = 'N'
                elif param == 'phosphorus':
                    param_name = 'P'
                elif param == 'potassium':
                    param_name = 'K'
                elif param == 'dissolved_oxygen':
                    param_name = 'ออกซิเจนละลาย'
                elif param == 'turbidity':
                    param_name = 'ความขุ่น'
                else:
                    param_name = param.capitalize()
                
                sensor_data[param_name] = latest_data[col]
        
        latest_readings.append(sensor_data)
    
    latest_df = pd.DataFrame(latest_readings)
    
    # Function to color code pH values
    def color_ph(val):
        if val < 6.5:
            return 'background-color: rgba(255, 0, 0, 0.2)'
        elif val > 8.5:
            return 'background-color: rgba(128, 0, 128, 0.2)'
        else:
            return 'background-color: rgba(0, 128, 0, 0.2)'
    
    # Apply styling (using .map instead of .applymap which is deprecated)
    # Check if 'pH' column exists in the DataFrame
    if 'pH' in latest_df.columns:
        styled_df = latest_df.style.map(
            color_ph, subset=['pH']
        )
    else:
        styled_df = latest_df.style
    
    st.dataframe(styled_df, use_container_width=True)
    
    st.markdown("---")
    
    # Create a section for the daily trends
    st.subheader("แนวโน้มรายวัน")
    
    # Create tabs for different parameters (in the specified order)
    tabs = st.tabs(["pH", "ความชื้น", "อุณหภูมิ", "การนำไฟฟ้า", "NPK", "ออกซิเจนละลาย", "ความขุ่น"])
    
    # Get the last 7 days of data
    last_7_days = daily_summary[daily_summary['date'] >= (daily_summary['date'].max() - timedelta(days=7))]
    
    # pH tab
    with tabs[0]:
        fig = go.Figure()
        
        for i in range(1, num_sensors + 1):
            avg_col = f'sensor_{i}_ph_avg'
            min_col = f'sensor_{i}_ph_min'
            max_col = f'sensor_{i}_ph_max'
            
            if avg_col in last_7_days.columns:
                # Get the location name
                sensor_info_row = sensor_info[sensor_info['sensor_id'] == i]
                if not sensor_info_row.empty:
                    name = f"เซ็นเซอร์ {i} ({sensor_info_row['location_name'].values[0]})"
                else:
                    name = f"เซ็นเซอร์ {i}"
                
                # Add a line for the average
                fig.add_trace(go.Scatter(
                    x=last_7_days['date'],
                    y=last_7_days[avg_col],
                    mode='lines+markers',
                    name=name
                ))
                
                # Add a range for min/max
                fig.add_trace(go.Scatter(
                    x=last_7_days['date'].tolist() + last_7_days['date'].tolist()[::-1],
                    y=last_7_days[max_col].tolist() + last_7_days[min_col].tolist()[::-1],
                    fill='toself',
                    fillcolor=f'rgba(0, 100, 80, 0.2)',
                    line=dict(color='rgba(255, 255, 255, 0)'),
                    showlegend=False,
                    name=f"{name} Range"
                ))
        
        # Add reference lines for normal pH range
        fig.add_shape(
            type="line",
            x0=last_7_days['date'].min(),
            y0=6.5,
            x1=last_7_days['date'].max(),
            y1=6.5,
            line=dict(color="red", width=2, dash="dash"),
        )
        
        fig.add_shape(
            type="line",
            x0=last_7_days['date'].min(),
            y0=8.5,
            x1=last_7_days['date'].max(),
            y1=8.5,
            line=dict(color="red", width=2, dash="dash"),
        )
        
        fig.update_layout(
            title="ค่าเฉลี่ย pH รายวัน (7 วันล่าสุด)",
            xaxis_title="วันที่",
            yaxis_title="pH",
            legend_title="เซ็นเซอร์",
            hovermode="x unified"
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
        st.info(
            "เส้นประสีแดงแสดงช่วง pH ปกติ (6.5 - 8.5) "
            "ค่าที่อยู่นอกช่วงนี้อาจต้องได้รับการตรวจสอบ"
        )
    
    # Humidity tab (inserted after pH and before Temperature)
    with tabs[1]:
        fig = go.Figure()
        
        for i in range(1, num_sensors + 1):
            avg_col = f'sensor_{i}_humidity_avg'
            
            if avg_col in last_7_days.columns:
                # Get the location name
                sensor_info_row = sensor_info[sensor_info['sensor_id'] == i]
                if not sensor_info_row.empty:
                    name = f"เซ็นเซอร์ {i} ({sensor_info_row['location_name'].values[0]})"
                else:
                    name = f"เซ็นเซอร์ {i}"
                
                # Add a line for the average
                fig.add_trace(go.Scatter(
                    x=last_7_days['date'],
                    y=last_7_days[avg_col],
                    mode='lines+markers',
                    name=name
                ))
        
        fig.update_layout(
            title="ค่าเฉลี่ยความชื้นรายวัน (7 วันล่าสุด)",
            xaxis_title="วันที่",
            yaxis_title="ความชื้น (%)",
            legend_title="เซ็นเซอร์",
            hovermode="x unified"
        )
        
        st.plotly_chart(fig, use_container_width=True)
    
    # Temperature tab
    with tabs[2]:
        fig = go.Figure()
        
        for i in range(1, num_sensors + 1):
            avg_col = f'sensor_{i}_temp_avg'
            
            if avg_col in last_7_days.columns:
                # Get the location name
                sensor_info_row = sensor_info[sensor_info['sensor_id'] == i]
                if not sensor_info_row.empty:
                    name = f"เซ็นเซอร์ {i} ({sensor_info_row['location_name'].values[0]})"
                else:
                    name = f"เซ็นเซอร์ {i}"
                
                # Add a line for the average
                fig.add_trace(go.Scatter(
                    x=last_7_days['date'],
                    y=last_7_days[avg_col],
                    mode='lines+markers',
                    name=name
                ))
        
        fig.update_layout(
            title="ค่าเฉลี่ยอุณหภูมิรายวัน (7 วันล่าสุด)",
            xaxis_title="วันที่",
            yaxis_title="อุณหภูมิ (°C)",
            legend_title="เซ็นเซอร์",
            hovermode="x unified"
        )
        
        st.plotly_chart(fig, use_container_width=True)
    
    # Conductivity tab
    with tabs[3]:
        fig = go.Figure()
        
        for i in range(1, num_sensors + 1):
            avg_col = f'sensor_{i}_conductivity_avg'
            
            if avg_col in last_7_days.columns:
                # Get the location name
                sensor_info_row = sensor_info[sensor_info['sensor_id'] == i]
                if not sensor_info_row.empty:
                    name = f"เซ็นเซอร์ {i} ({sensor_info_row['location_name'].values[0]})"
                else:
                    name = f"เซ็นเซอร์ {i}"
                
                # Add a line for the average
                fig.add_trace(go.Scatter(
                    x=last_7_days['date'],
                    y=last_7_days[avg_col],
                    mode='lines+markers',
                    name=name
                ))
        
        fig.update_layout(
            title="ค่าเฉลี่ยการนำไฟฟ้ารายวัน (7 วันล่าสุด)",
            xaxis_title="วันที่",
            yaxis_title="การนำไฟฟ้า (μS/cm)",
            legend_title="เซ็นเซอร์",
            hovermode="x unified"
        )
        
        st.plotly_chart(fig, use_container_width=True)
    
    # NPK tab (Nitrogen, Phosphorus, Potassium)
    with tabs[4]:
        # Create subtabs for N, P, K
        npk_tabs = st.tabs(["ไนโตรเจน (N)", "ฟอสฟอรัส (P)", "โพแทสเซียม (K)"])
        
        # Nitrogen subtab
        with npk_tabs[0]:
            fig = go.Figure()
            
            for i in range(1, num_sensors + 1):
                avg_col = f'sensor_{i}_nitrogen_avg'
                
                if avg_col in last_7_days.columns:
                    # Get the location name
                    sensor_info_row = sensor_info[sensor_info['sensor_id'] == i]
                    if not sensor_info_row.empty:
                        name = f"เซ็นเซอร์ {i} ({sensor_info_row['location_name'].values[0]})"
                    else:
                        name = f"เซ็นเซอร์ {i}"
                    
                    # Add a line for the average
                    fig.add_trace(go.Scatter(
                        x=last_7_days['date'],
                        y=last_7_days[avg_col],
                        mode='lines+markers',
                        name=name
                    ))
            
            fig.update_layout(
                title="ค่าเฉลี่ยไนโตรเจนรายวัน (7 วันล่าสุด)",
                xaxis_title="วันที่",
                yaxis_title="ไนโตรเจน (mg/kg)",
                legend_title="เซ็นเซอร์",
                hovermode="x unified"
            )
            
            st.plotly_chart(fig, use_container_width=True)
        
        # Phosphorus subtab
        with npk_tabs[1]:
            fig = go.Figure()
            
            for i in range(1, num_sensors + 1):
                avg_col = f'sensor_{i}_phosphorus_avg'
                
                if avg_col in last_7_days.columns:
                    # Get the location name
                    sensor_info_row = sensor_info[sensor_info['sensor_id'] == i]
                    if not sensor_info_row.empty:
                        name = f"เซ็นเซอร์ {i} ({sensor_info_row['location_name'].values[0]})"
                    else:
                        name = f"เซ็นเซอร์ {i}"
                    
                    # Add a line for the average
                    fig.add_trace(go.Scatter(
                        x=last_7_days['date'],
                        y=last_7_days[avg_col],
                        mode='lines+markers',
                        name=name
                    ))
            
            fig.update_layout(
                title="ค่าเฉลี่ยฟอสฟอรัสรายวัน (7 วันล่าสุด)",
                xaxis_title="วันที่",
                yaxis_title="ฟอสฟอรัส (mg/kg)",
                legend_title="เซ็นเซอร์",
                hovermode="x unified"
            )
            
            st.plotly_chart(fig, use_container_width=True)
        
        # Potassium subtab
        with npk_tabs[2]:
            fig = go.Figure()
            
            for i in range(1, num_sensors + 1):
                avg_col = f'sensor_{i}_potassium_avg'
                
                if avg_col in last_7_days.columns:
                    # Get the location name
                    sensor_info_row = sensor_info[sensor_info['sensor_id'] == i]
                    if not sensor_info_row.empty:
                        name = f"เซ็นเซอร์ {i} ({sensor_info_row['location_name'].values[0]})"
                    else:
                        name = f"เซ็นเซอร์ {i}"
                    
                    # Add a line for the average
                    fig.add_trace(go.Scatter(
                        x=last_7_days['date'],
                        y=last_7_days[avg_col],
                        mode='lines+markers',
                        name=name
                    ))
            
            fig.update_layout(
                title="ค่าเฉลี่ยโพแทสเซียมรายวัน (7 วันล่าสุด)",
                xaxis_title="วันที่",
                yaxis_title="โพแทสเซียม (mg/kg)",
                legend_title="เซ็นเซอร์",
                hovermode="x unified"
            )
            
            st.plotly_chart(fig, use_container_width=True)
    
    # Dissolved Oxygen tab
    with tabs[5]:
        fig = go.Figure()
        
        for i in range(1, num_sensors + 1):
            avg_col = f'sensor_{i}_dissolved_oxygen_avg'
            
            if avg_col in last_7_days.columns:
                # Get the location name
                sensor_info_row = sensor_info[sensor_info['sensor_id'] == i]
                if not sensor_info_row.empty:
                    name = f"เซ็นเซอร์ {i} ({sensor_info_row['location_name'].values[0]})"
                else:
                    name = f"เซ็นเซอร์ {i}"
                
                # Add a line for the average
                fig.add_trace(go.Scatter(
                    x=last_7_days['date'],
                    y=last_7_days[avg_col],
                    mode='lines+markers',
                    name=name
                ))
        
        fig.update_layout(
            title="ค่าเฉลี่ยออกซิเจนละลายรายวัน (7 วันล่าสุด)",
            xaxis_title="วันที่",
            yaxis_title="ออกซิเจนละลาย (mg/L)",
            legend_title="เซ็นเซอร์",
            hovermode="x unified"
        )
        
        st.plotly_chart(fig, use_container_width=True)
    
    # Turbidity tab
    with tabs[6]:
        fig = go.Figure()
        
        for i in range(1, num_sensors + 1):
            avg_col = f'sensor_{i}_turbidity_avg'
            
            if avg_col in last_7_days.columns:
                # Get the location name
                sensor_info_row = sensor_info[sensor_info['sensor_id'] == i]
                if not sensor_info_row.empty:
                    name = f"เซ็นเซอร์ {i} ({sensor_info_row['location_name'].values[0]})"
                else:
                    name = f"เซ็นเซอร์ {i}"
                
                # Add a line for the average
                fig.add_trace(go.Scatter(
                    x=last_7_days['date'],
                    y=last_7_days[avg_col],
                    mode='lines+markers',
                    name=name
                ))
        
        fig.update_layout(
            title="ค่าเฉลี่ยความขุ่นรายวัน (7 วันล่าสุด)",
            xaxis_title="วันที่",
            yaxis_title="ความขุ่น (NTU)",
            legend_title="เซ็นเซอร์",
            hovermode="x unified"
        )
        
        st.plotly_chart(fig, use_container_width=True)
