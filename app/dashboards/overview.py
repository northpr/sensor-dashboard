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
    st.header("Overview Dashboard")
    st.markdown("This dashboard provides a high-level overview of all soil quality sensors.")
    
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
    col1.metric("Total Sensors", num_sensors)
    
    # Display the total number of readings
    total_readings = len(combined_data)
    col2.metric("Total Readings", f"{total_readings:,}")
    
    # Display the date range
    start_date = combined_data['timestamp'].min().date()
    end_date = combined_data['timestamp'].max().date()
    date_range = f"{start_date} to {end_date}"
    col3.metric("Date Range", date_range)
    
    # Display the average reading frequency
    time_diff = combined_data['timestamp'].diff().mean()
    minutes = int(time_diff.total_seconds() / 60)
    col4.metric("Avg Reading Frequency", f"{minutes} min")
    
    # Display the last update time
    last_update = combined_data['timestamp'].max()
    col5.metric("Last Updated", last_update.strftime("%Y-%m-%d %H:%M"))
    
    st.markdown("---")
    
    # Create two columns for the map and sensor info
    col1, col2 = st.columns([3, 2])
    
    with col1:
        st.subheader("Sensor Locations")
        
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
                    map_data.loc[i, 'status'] = "Acidic"
                    map_data.loc[i, 'color'] = "red"
                elif ph > 8.5:
                    map_data.loc[i, 'status'] = "Alkaline"
                    map_data.loc[i, 'color'] = "purple"
                else:
                    map_data.loc[i, 'status'] = "Normal"
                    map_data.loc[i, 'color'] = "green"
        
        # Create a new column for hover text that includes soil type
        map_data['hover_text'] = map_data.apply(
            lambda row: f"Soil Type: {row['water_type']}<br>pH: {row['latest_ph']:.2f}<br>Status: {row['status']}",
            axis=1
        )
        
        # Create the map centered on Thailand using Scattermapbox directly
        fig = go.Figure()
        
        # Add points for each sensor
        for status in ["Normal", "Acidic", "Alkaline"]:
            df_status = map_data[map_data['status'] == status]
            if not df_status.empty:
                fig.add_trace(go.Scattermapbox(
                    lat=df_status['latitude'],
                    lon=df_status['longitude'],
                    mode='markers',
                    marker=dict(
                        size=15,
                        color={"Normal": "green", "Acidic": "red", "Alkaline": "purple"}[status]
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
        st.subheader("Sensor Information")
        
        # Display sensor info in a table with renamed columns
        sensor_table = sensor_info[['sensor_id', 'location_name', 'water_type', 'last_calibration']].copy()
        sensor_table.columns = ['Sensor ID', 'Location', 'Soil Type', 'Last Calibration']
        st.dataframe(
            sensor_table,
            use_container_width=True
        )
        
        # Display a pie chart of soil types
        soil_type_counts = sensor_info['water_type'].value_counts().reset_index()
        soil_type_counts.columns = ['Soil Type', 'Count']
        
        fig = px.pie(
            soil_type_counts,
            values='Count',
            names='Soil Type',
            title='Sensors by Soil Type',
            hole=0.4
        )
        
        st.plotly_chart(fig, use_container_width=True)
    
    st.markdown("---")
    
    # Create a section for the latest readings
    st.subheader("Latest Sensor Readings")
    
    # Create a dataframe for the latest readings
    latest_readings = []
    
    for i in range(1, num_sensors + 1):
        sensor_data = {}
        sensor_data['Sensor ID'] = i
        
        # Get the location name
        sensor_info_row = sensor_info[sensor_info['sensor_id'] == i]
        if not sensor_info_row.empty:
            sensor_data['Location'] = sensor_info_row['location_name'].values[0]
        else:
            sensor_data['Location'] = f"Sensor {i}"
        
        # Get the latest readings in the specified order
        # pH first, followed by humidity and temperature, then the rest
        for param in ['ph', 'humidity', 'temp', 'conductivity', 'nitrogen', 'phosphorus', 'potassium', 'dissolved_oxygen', 'turbidity']:
            col = f'sensor_{i}_{param}'
            if col in latest_data:
                # Format the parameter name for display
                if param == 'ph':
                    param_name = 'pH'
                elif param == 'temp':
                    param_name = 'Temperature'
                elif param == 'nitrogen':
                    param_name = 'N'
                elif param == 'phosphorus':
                    param_name = 'P'
                elif param == 'potassium':
                    param_name = 'K'
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
    st.subheader("Daily Trends")
    
    # Create tabs for different parameters (in the specified order)
    tabs = st.tabs(["pH", "Humidity", "Temperature", "Conductivity", "NPK", "Dissolved Oxygen", "Turbidity"])
    
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
                    name = f"Sensor {i} ({sensor_info_row['location_name'].values[0]})"
                else:
                    name = f"Sensor {i}"
                
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
            title="Daily Average pH (Last 7 Days)",
            xaxis_title="Date",
            yaxis_title="pH",
            legend_title="Sensor",
            hovermode="x unified"
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
        st.info(
            "The dashed red lines indicate the normal pH range (6.5 - 8.5). "
            "Values outside this range may require attention."
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
                    name = f"Sensor {i} ({sensor_info_row['location_name'].values[0]})"
                else:
                    name = f"Sensor {i}"
                
                # Add a line for the average
                fig.add_trace(go.Scatter(
                    x=last_7_days['date'],
                    y=last_7_days[avg_col],
                    mode='lines+markers',
                    name=name
                ))
        
        fig.update_layout(
            title="Daily Average Humidity (Last 7 Days)",
            xaxis_title="Date",
            yaxis_title="Humidity (%)",
            legend_title="Sensor",
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
                    name = f"Sensor {i} ({sensor_info_row['location_name'].values[0]})"
                else:
                    name = f"Sensor {i}"
                
                # Add a line for the average
                fig.add_trace(go.Scatter(
                    x=last_7_days['date'],
                    y=last_7_days[avg_col],
                    mode='lines+markers',
                    name=name
                ))
        
        fig.update_layout(
            title="Daily Average Temperature (Last 7 Days)",
            xaxis_title="Date",
            yaxis_title="Temperature (°C)",
            legend_title="Sensor",
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
                    name = f"Sensor {i} ({sensor_info_row['location_name'].values[0]})"
                else:
                    name = f"Sensor {i}"
                
                # Add a line for the average
                fig.add_trace(go.Scatter(
                    x=last_7_days['date'],
                    y=last_7_days[avg_col],
                    mode='lines+markers',
                    name=name
                ))
        
        fig.update_layout(
            title="Daily Average Conductivity (Last 7 Days)",
            xaxis_title="Date",
            yaxis_title="Conductivity (μS/cm)",
            legend_title="Sensor",
            hovermode="x unified"
        )
        
        st.plotly_chart(fig, use_container_width=True)
    
    # NPK tab (Nitrogen, Phosphorus, Potassium)
    with tabs[4]:
        # Create subtabs for N, P, K
        npk_tabs = st.tabs(["Nitrogen (N)", "Phosphorus (P)", "Potassium (K)"])
        
        # Nitrogen subtab
        with npk_tabs[0]:
            fig = go.Figure()
            
            for i in range(1, num_sensors + 1):
                avg_col = f'sensor_{i}_nitrogen_avg'
                
                if avg_col in last_7_days.columns:
                    # Get the location name
                    sensor_info_row = sensor_info[sensor_info['sensor_id'] == i]
                    if not sensor_info_row.empty:
                        name = f"Sensor {i} ({sensor_info_row['location_name'].values[0]})"
                    else:
                        name = f"Sensor {i}"
                    
                    # Add a line for the average
                    fig.add_trace(go.Scatter(
                        x=last_7_days['date'],
                        y=last_7_days[avg_col],
                        mode='lines+markers',
                        name=name
                    ))
            
            fig.update_layout(
                title="Daily Average Nitrogen (Last 7 Days)",
                xaxis_title="Date",
                yaxis_title="Nitrogen (mg/kg)",
                legend_title="Sensor",
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
                        name = f"Sensor {i} ({sensor_info_row['location_name'].values[0]})"
                    else:
                        name = f"Sensor {i}"
                    
                    # Add a line for the average
                    fig.add_trace(go.Scatter(
                        x=last_7_days['date'],
                        y=last_7_days[avg_col],
                        mode='lines+markers',
                        name=name
                    ))
            
            fig.update_layout(
                title="Daily Average Phosphorus (Last 7 Days)",
                xaxis_title="Date",
                yaxis_title="Phosphorus (mg/kg)",
                legend_title="Sensor",
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
                        name = f"Sensor {i} ({sensor_info_row['location_name'].values[0]})"
                    else:
                        name = f"Sensor {i}"
                    
                    # Add a line for the average
                    fig.add_trace(go.Scatter(
                        x=last_7_days['date'],
                        y=last_7_days[avg_col],
                        mode='lines+markers',
                        name=name
                    ))
            
            fig.update_layout(
                title="Daily Average Potassium (Last 7 Days)",
                xaxis_title="Date",
                yaxis_title="Potassium (mg/kg)",
                legend_title="Sensor",
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
                    name = f"Sensor {i} ({sensor_info_row['location_name'].values[0]})"
                else:
                    name = f"Sensor {i}"
                
                # Add a line for the average
                fig.add_trace(go.Scatter(
                    x=last_7_days['date'],
                    y=last_7_days[avg_col],
                    mode='lines+markers',
                    name=name
                ))
        
        fig.update_layout(
            title="Daily Average Dissolved Oxygen (Last 7 Days)",
            xaxis_title="Date",
            yaxis_title="Dissolved Oxygen (mg/L)",
            legend_title="Sensor",
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
                    name = f"Sensor {i} ({sensor_info_row['location_name'].values[0]})"
                else:
                    name = f"Sensor {i}"
                
                # Add a line for the average
                fig.add_trace(go.Scatter(
                    x=last_7_days['date'],
                    y=last_7_days[avg_col],
                    mode='lines+markers',
                    name=name
                ))
        
        fig.update_layout(
            title="Daily Average Turbidity (Last 7 Days)",
            xaxis_title="Date",
            yaxis_title="Turbidity (NTU)",
            legend_title="Sensor",
            hovermode="x unified"
        )
        
        st.plotly_chart(fig, use_container_width=True)
