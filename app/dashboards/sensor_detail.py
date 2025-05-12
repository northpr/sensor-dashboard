import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta

def show_sensor_detail_dashboard(data, sensor_id):
    """
    แสดงข้อมูลโดยละเอียดสำหรับเซ็นเซอร์เฉพาะ
    
    พารามิเตอร์:
    - data: พจนานุกรมที่มีข้อมูลเซ็นเซอร์ทั้งหมด
    - sensor_id: ID ของเซ็นเซอร์ที่ต้องการแสดง
    """
    # Get the data
    combined_data = data['combined_data']
    sensor_info = data['sensor_info']
    individual_sensors = data['individual_sensors']
    
    # Get the sensor data
    sensor_key = f'sensor_{sensor_id}'
    if sensor_key in individual_sensors:
        sensor_data = individual_sensors[sensor_key]
    else:
        st.error(f"ไม่พบข้อมูลสำหรับเซ็นเซอร์ {sensor_id}")
        return
    
    # Get the sensor info
    sensor_info_row = sensor_info[sensor_info['sensor_id'] == sensor_id]
    if not sensor_info_row.empty:
        location_name = sensor_info_row['location_name'].values[0]
        water_type = sensor_info_row['water_type'].values[0]
        coordinates = sensor_info_row['coordinates'].values[0]
        installation_date = sensor_info_row['installation_date'].values[0]
        maintenance_interval = sensor_info_row['maintenance_interval_days'].values[0]
        last_calibration = sensor_info_row['last_calibration'].values[0]
    else:
        location_name = f"Sensor {sensor_id}"
        water_type = "Unknown"
        coordinates = "Unknown"
        installation_date = "Unknown"
        maintenance_interval = "Unknown"
        last_calibration = "Unknown"
    
    # แสดงส่วนหัวของเซ็นเซอร์
    st.header(f"เซ็นเซอร์ {sensor_id}: {location_name}")
    st.markdown(f"ข้อมูลโดยละเอียดและค่าที่อ่านได้สำหรับเซ็นเซอร์ {sensor_id} ที่ตั้งอยู่ที่ {location_name}")
    
    # Create columns for the sensor info
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.subheader("ข้อมูลเซ็นเซอร์")
        st.markdown(f"**ตำแหน่ง:** {location_name}")
        st.markdown(f"**ประเภทดิน:** {water_type}")
        st.markdown(f"**พิกัด:** {coordinates}")
        st.markdown(f"**วันที่ติดตั้ง:** {installation_date}")
        st.markdown(f"**ช่วงเวลาบำรุงรักษา:** {maintenance_interval} วัน")
        st.markdown(f"**การปรับเทียบล่าสุด:** {last_calibration}")
        
        # Calculate days since last calibration
        if last_calibration != "Unknown":
            last_cal_date = datetime.strptime(last_calibration, "%Y-%m-%d")
            days_since_cal = (datetime.now() - last_cal_date).days
            
            # แสดงสถานะการปรับเทียบ
            if days_since_cal > maintenance_interval:
                st.warning(f"⚠️ เกินกำหนดการปรับเทียบแล้ว {days_since_cal - maintenance_interval} วัน")
            else:
                st.success(f"✅ การปรับเทียบเป็นปัจจุบัน ({days_since_cal} วันนับจากการปรับเทียบครั้งล่าสุด)")
    
    with col2:
        st.subheader("ค่าปัจจุบัน")
        
        # Get the latest readings
        latest_data = sensor_data.iloc[-1]
        
        # Display the latest readings
        for param in ['ph', 'temp', 'conductivity', 'dissolved_oxygen', 'turbidity']:
            if param in latest_data:
                value = latest_data[param]
                
                # Format the value based on the parameter
                if param == 'ph':
                    formatted_value = f"{value:.2f}"
                    if value < 6.5:
                        st.error(f"**pH:** {formatted_value} (เป็นกรด)")
                    elif value > 8.5:
                        st.error(f"**pH:** {formatted_value} (เป็นด่าง)")
                    else:
                        st.success(f"**pH:** {formatted_value} (ปกติ)")
                
                elif param == 'temp':
                    formatted_value = f"{value:.1f} °C"
                    st.markdown(f"**อุณหภูมิ:** {formatted_value}")
                
                elif param == 'conductivity':
                    formatted_value = f"{value:.1f} μS/cm"
                    st.markdown(f"**การนำไฟฟ้า:** {formatted_value}")
                
                elif param == 'dissolved_oxygen':
                    formatted_value = f"{value:.2f} mg/L"
                    if value < 4.0:
                        st.error(f"**ออกซิเจนละลาย:** {formatted_value} (ต่ำ)")
                    else:
                        st.success(f"**ออกซิเจนละลาย:** {formatted_value} (ปกติ)")
                
                elif param == 'turbidity':
                    formatted_value = f"{value:.2f} NTU"
                    if value > 10.0:
                        st.warning(f"**ความขุ่น:** {formatted_value} (สูง)")
                    else:
                        st.success(f"**ความขุ่น:** {formatted_value} (ปกติ)")
        
        # แสดงเวลาที่อัปเดตล่าสุด
        last_update = latest_data['timestamp']
        st.markdown(f"**อัปเดตล่าสุด:** {last_update}")
    
    with col3:
        st.subheader("สถานะพารามิเตอร์")
        
        # Create a gauge chart for pH
        if 'ph' in latest_data:
            ph_value = latest_data['ph']
            
            fig = go.Figure(go.Indicator(
                mode="gauge+number",
                value=ph_value,
                domain={'x': [0, 1], 'y': [0, 1]},
                title={'text': "pH"},
                gauge={
                    'axis': {'range': [0, 14], 'tickwidth': 1, 'tickcolor': "darkblue"},
                    'bar': {'color': "darkblue"},
                    'bgcolor': "white",
                    'borderwidth': 2,
                    'bordercolor': "gray",
                    'steps': [
                        {'range': [0, 6.5], 'color': 'rgba(255, 0, 0, 0.3)'},
                        {'range': [6.5, 8.5], 'color': 'rgba(0, 255, 0, 0.3)'},
                        {'range': [8.5, 14], 'color': 'rgba(255, 0, 0, 0.3)'}
                    ],
                    'threshold': {
                        'line': {'color': "red", 'width': 4},
                        'thickness': 0.75,
                        'value': ph_value
                    }
                }
            ))
            
            fig.update_layout(
                height=200,
                margin=dict(l=20, r=20, t=30, b=20)
            )
            
            st.plotly_chart(fig, use_container_width=True)
    
    st.markdown("---")
    
    # สร้างแท็บสำหรับการแสดงผลต่างๆ
    tabs = st.tabs(["ข้อมูลอนุกรมเวลา", "รูปแบบรายชั่วโมง", "ความสัมพันธ์", "สถิติ"])
    
    # แท็บข้อมูลอนุกรมเวลา
    with tabs[0]:
        st.subheader("ข้อมูลอนุกรมเวลา")
        
        # Create date range selector
        col1, col2 = st.columns(2)
        
        with col1:
            start_date = st.date_input(
                "Start Date",
                value=sensor_data['timestamp'].min().date(),
                min_value=sensor_data['timestamp'].min().date(),
                max_value=sensor_data['timestamp'].max().date()
            )
        
        with col2:
            end_date = st.date_input(
                "End Date",
                value=sensor_data['timestamp'].max().date(),
                min_value=sensor_data['timestamp'].min().date(),
                max_value=sensor_data['timestamp'].max().date()
            )
        
        # Filter data by date range
        filtered_data = sensor_data[
            (sensor_data['timestamp'].dt.date >= start_date) &
            (sensor_data['timestamp'].dt.date <= end_date)
        ]
        
        # Parameter selection
        parameters = st.multiselect(
            "Select Parameters",
            ['ph', 'temp', 'conductivity', 'dissolved_oxygen', 'turbidity'],
            default=['ph']
        )
        
        if not parameters:
            st.warning("Please select at least one parameter.")
        else:
            # Create the time series plot
            fig = go.Figure()
            
            for param in parameters:
                if param in filtered_data.columns:
                    # Get the display name and unit
                    if param == 'ph':
                        display_name = "pH"
                        unit = ""
                    elif param == 'temp':
                        display_name = "Temperature"
                        unit = "°C"
                    elif param == 'conductivity':
                        display_name = "Conductivity"
                        unit = "μS/cm"
                    elif param == 'dissolved_oxygen':
                        display_name = "Dissolved Oxygen"
                        unit = "mg/L"
                    elif param == 'turbidity':
                        display_name = "Turbidity"
                        unit = "NTU"
                    else:
                        display_name = param.capitalize()
                        unit = ""
                    
                    # Add the trace
                    fig.add_trace(go.Scatter(
                        x=filtered_data['timestamp'],
                        y=filtered_data[param],
                        mode='lines',
                        name=f"{display_name} ({unit})" if unit else display_name
                    ))
            
            # Add reference lines for pH if selected
            if 'ph' in parameters:
                fig.add_shape(
                    type="line",
                    x0=filtered_data['timestamp'].min(),
                    y0=6.5,
                    x1=filtered_data['timestamp'].max(),
                    y1=6.5,
                    line=dict(color="red", width=1, dash="dash"),
                    name="Min Normal pH"
                )
                
                fig.add_shape(
                    type="line",
                    x0=filtered_data['timestamp'].min(),
                    y0=8.5,
                    x1=filtered_data['timestamp'].max(),
                    y1=8.5,
                    line=dict(color="red", width=1, dash="dash"),
                    name="Max Normal pH"
                )
            
            # Update the layout
            fig.update_layout(
                title=f"Time Series Data for Sensor {sensor_id} ({location_name})",
                xaxis_title="Timestamp",
                yaxis_title="Value",
                legend_title="Parameter",
                hovermode="x unified"
            )
            
            st.plotly_chart(fig, use_container_width=True)
            
            # Add a download button for the filtered data
            csv = filtered_data.to_csv(index=False)
            st.download_button(
                label="Download Filtered Data as CSV",
                data=csv,
                file_name=f"sensor_{sensor_id}_data_{start_date}_to_{end_date}.csv",
                mime="text/csv"
            )
    
    # แท็บรูปแบบรายชั่วโมง
    with tabs[1]:
        st.subheader("รูปแบบรายชั่วโมง")
        
        # Group data by hour
        sensor_data['hour'] = sensor_data['timestamp'].dt.hour
        hourly_data = sensor_data.groupby('hour').agg({
            'ph': ['mean', 'std'],
            'temp': ['mean', 'std'],
            'conductivity': ['mean', 'std'],
            'dissolved_oxygen': ['mean', 'std'],
            'turbidity': ['mean', 'std']
        }).reset_index()
        
        # Flatten the column names
        hourly_data.columns = ['_'.join(col).strip() for col in hourly_data.columns.values]
        hourly_data.rename(columns={'hour_': 'hour'}, inplace=True)
        
        # Parameter selection
        param = st.selectbox(
            "Select Parameter",
            ['ph', 'temp', 'conductivity', 'dissolved_oxygen', 'turbidity'],
            index=0
        )
        
        # Get the display name and unit
        if param == 'ph':
            display_name = "pH"
            unit = ""
        elif param == 'temp':
            display_name = "Temperature"
            unit = "°C"
        elif param == 'conductivity':
            display_name = "Conductivity"
            unit = "μS/cm"
        elif param == 'dissolved_oxygen':
            display_name = "Dissolved Oxygen"
            unit = "mg/L"
        elif param == 'turbidity':
            display_name = "Turbidity"
            unit = "NTU"
        
        # Create the hourly pattern plot
        fig = go.Figure()
        
        # Add the mean line
        fig.add_trace(go.Scatter(
            x=hourly_data['hour'],
            y=hourly_data[f'{param}_mean'],
            mode='lines+markers',
            name=f"Mean {display_name}",
            line=dict(color='blue')
        ))
        
        # Add the standard deviation range
        fig.add_trace(go.Scatter(
            x=hourly_data['hour'].tolist() + hourly_data['hour'].tolist()[::-1],
            y=(hourly_data[f'{param}_mean'] + hourly_data[f'{param}_std']).tolist() + 
              (hourly_data[f'{param}_mean'] - hourly_data[f'{param}_std']).tolist()[::-1],
            fill='toself',
            fillcolor='rgba(0, 0, 255, 0.1)',
            line=dict(color='rgba(255, 255, 255, 0)'),
            hoverinfo='skip',
            showlegend=True,
            name=f"±1 Std Dev"
        ))
        
        # Update the layout
        fig.update_layout(
            title=f"Hourly Pattern for {display_name}",
            xaxis_title="Hour of Day",
            yaxis_title=f"{display_name} {f'({unit})' if unit else ''}",
            xaxis=dict(
                tickmode='array',
                tickvals=list(range(24)),
                ticktext=[f"{h:02d}:00" for h in range(24)]
            ),
            hovermode="x unified"
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
        st.markdown(
            f"This chart shows how {display_name.lower()} varies throughout the day. "
            f"The blue line represents the average {display_name.lower()} for each hour, "
            f"and the shaded area represents one standard deviation from the mean."
        )
    
    # Correlations tab
    with tabs[2]:
        st.subheader("Parameter Correlations")
        
        # Calculate correlations
        corr_data = sensor_data[['ph', 'temp', 'conductivity', 'dissolved_oxygen', 'turbidity']].corr()
        
        # Create a heatmap
        fig = px.imshow(
            corr_data,
            x=corr_data.columns,
            y=corr_data.columns,
            color_continuous_scale='RdBu_r',
            zmin=-1,
            zmax=1,
            text_auto='.2f'
        )
        
        fig.update_layout(
            title="Correlation Matrix",
            xaxis_title="Parameter",
            yaxis_title="Parameter"
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
        st.markdown(
            "This heatmap shows the correlation between different parameters. "
            "A value close to 1 indicates a strong positive correlation, "
            "a value close to -1 indicates a strong negative correlation, "
            "and a value close to 0 indicates little to no correlation."
        )
        
        # Create scatter plots for selected parameters
        st.subheader("Parameter Relationships")
        
        col1, col2 = st.columns(2)
        
        with col1:
            x_param = st.selectbox(
                "X-axis Parameter",
                ['ph', 'temp', 'conductivity', 'dissolved_oxygen', 'turbidity'],
                index=0
            )
        
        with col2:
            y_param = st.selectbox(
                "Y-axis Parameter",
                ['ph', 'temp', 'conductivity', 'dissolved_oxygen', 'turbidity'],
                index=1
            )
        
        # Get the display names and units
        params = {
            'ph': {"name": "pH", "unit": ""},
            'temp': {"name": "Temperature", "unit": "°C"},
            'conductivity': {"name": "Conductivity", "unit": "μS/cm"},
            'dissolved_oxygen': {"name": "Dissolved Oxygen", "unit": "mg/L"},
            'turbidity': {"name": "Turbidity", "unit": "NTU"}
        }
        
        x_display = params[x_param]["name"]
        x_unit = params[x_param]["unit"]
        y_display = params[y_param]["name"]
        y_unit = params[y_param]["unit"]
        
        # Create the scatter plot
        fig = px.scatter(
            sensor_data,
            x=x_param,
            y=y_param,
            color='timestamp',
            color_continuous_scale='Viridis',
            opacity=0.7,
            trendline="ols"
        )
        
        fig.update_layout(
            title=f"{y_display} vs {x_display}",
            xaxis_title=f"{x_display} {f'({x_unit})' if x_unit else ''}",
            yaxis_title=f"{y_display} {f'({y_unit})' if y_unit else ''}",
            coloraxis_colorbar_title="Time"
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
        # Calculate and display the correlation coefficient
        corr = sensor_data[[x_param, y_param]].corr().iloc[0, 1]
        
        if abs(corr) > 0.7:
            strength = "strong"
        elif abs(corr) > 0.3:
            strength = "moderate"
        else:
            strength = "weak"
        
        direction = "positive" if corr > 0 else "negative"
        
        st.markdown(
            f"The correlation coefficient between {x_display.lower()} and {y_display.lower()} is "
            f"**{corr:.2f}**, indicating a {strength} {direction} correlation."
        )
    
    # Statistics tab
    with tabs[3]:
        st.subheader("Statistical Analysis")
        
        # Calculate statistics for each parameter
        stats = {}
        
        for param in ['ph', 'temp', 'conductivity', 'dissolved_oxygen', 'turbidity']:
            if param in sensor_data.columns:
                stats[param] = {
                    'mean': sensor_data[param].mean(),
                    'median': sensor_data[param].median(),
                    'std': sensor_data[param].std(),
                    'min': sensor_data[param].min(),
                    'max': sensor_data[param].max(),
                    'range': sensor_data[param].max() - sensor_data[param].min(),
                    'q1': sensor_data[param].quantile(0.25),
                    'q3': sensor_data[param].quantile(0.75),
                    'iqr': sensor_data[param].quantile(0.75) - sensor_data[param].quantile(0.25)
                }
        
        # Create a dataframe for the statistics
        stats_df = pd.DataFrame(stats).T
        stats_df.index.name = 'Parameter'
        stats_df.reset_index(inplace=True)
        
        # Add display names
        stats_df['Display Name'] = stats_df['Parameter'].map({
            'ph': 'pH',
            'temp': 'Temperature (°C)',
            'conductivity': 'Conductivity (μS/cm)',
            'dissolved_oxygen': 'Dissolved Oxygen (mg/L)',
            'turbidity': 'Turbidity (NTU)'
        })
        
        # Reorder columns
        stats_df = stats_df[['Parameter', 'Display Name', 'mean', 'median', 'std', 'min', 'q1', 'q3', 'max', 'range', 'iqr']]
        
        # Rename columns
        stats_df.columns = ['Parameter', 'Display Name', 'Mean', 'Median', 'Std Dev', 'Min', 'Q1', 'Q3', 'Max', 'Range', 'IQR']
        
        # Display the statistics
        st.dataframe(stats_df, use_container_width=True)
        
        # Create box plots for each parameter
        st.subheader("Distribution Analysis")
        
        # Parameter selection
        param = st.selectbox(
            "Select Parameter for Distribution Analysis",
            ['ph', 'temp', 'conductivity', 'dissolved_oxygen', 'turbidity'],
            key="dist_param",
            index=0
        )
        
        # Get the display name and unit
        display_info = {
            'ph': {"name": "pH", "unit": ""},
            'temp': {"name": "Temperature", "unit": "°C"},
            'conductivity': {"name": "Conductivity", "unit": "μS/cm"},
            'dissolved_oxygen': {"name": "Dissolved Oxygen", "unit": "mg/L"},
            'turbidity': {"name": "Turbidity", "unit": "NTU"}
        }
        
        display_name = display_info[param]["name"]
        unit = display_info[param]["unit"]
        
        # Create two columns for the box plot and histogram
        col1, col2 = st.columns(2)
        
        with col1:
            # Create the box plot
            fig = go.Figure()
            
            fig.add_trace(go.Box(
                y=sensor_data[param],
                name=display_name,
                boxmean=True,
                boxpoints='outliers'
            ))
            
            fig.update_layout(
                title=f"Box Plot for {display_name}",
                yaxis_title=f"{display_name} {f'({unit})' if unit else ''}",
                showlegend=False
            )
            
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            # Create the histogram
            fig = go.Figure()
            
            fig.add_trace(go.Histogram(
                x=sensor_data[param],
                nbinsx=30,
                name=display_name
            ))
            
            # Add a KDE curve
            kde_x = np.linspace(sensor_data[param].min(), sensor_data[param].max(), 100)
            kde_y = stats_df.loc[stats_df['Parameter'] == param, 'Mean'].values[0] * np.ones_like(kde_x)
            
            fig.add_trace(go.Scatter(
                x=kde_x,
                y=kde_y,
                mode='lines',
                name='Mean',
                line=dict(color='red', dash='dash')
            ))
            
            fig.update_layout(
                title=f"Histogram for {display_name}",
                xaxis_title=f"{display_name} {f'({unit})' if unit else ''}",
                yaxis_title="Frequency",
                showlegend=True
            )
            
            st.plotly_chart(fig, use_container_width=True)
        
        # Display statistics for the selected parameter
        st.markdown(f"### Statistics for {display_name}")
        
        param_stats = stats_df[stats_df['Parameter'] == param].iloc[0]
        
        col1, col2, col3, col4 = st.columns(4)
        
        col1.metric("Mean", f"{param_stats['Mean']:.2f}")
        col2.metric("Median", f"{param_stats['Median']:.2f}")
        col3.metric("Std Dev", f"{param_stats['Std Dev']:.2f}")
        col4.metric("Range", f"{param_stats['Range']:.2f}")
        
        # Check for outliers
        q1 = param_stats['Q1']
        q3 = param_stats['Q3']
        iqr = param_stats['IQR']
        
        lower_bound = q1 - 1.5 * iqr
        upper_bound = q3 + 1.5 * iqr
        
        outliers = sensor_data[(sensor_data[param] < lower_bound) | (sensor_data[param] > upper_bound)]
        
        if not outliers.empty:
            st.warning(f"Found {len(outliers)} outliers in {display_name} data.")
            
            # Display the outliers
            st.dataframe(
                outliers[['timestamp', param]].rename(columns={param: display_name}),
                use_container_width=True
            )
        else:
            st.success(f"No outliers found in {display_name} data.")
