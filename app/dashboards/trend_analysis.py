import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
from scipy import stats

def show_trend_analysis_dashboard(data):
    """
    Display trend analysis dashboard for all sensors.
    
    Parameters:
    - data: Dictionary containing all sensor data
    """
    st.header("Trend Analysis Dashboard")
    st.markdown("This dashboard provides tools for analyzing trends in water quality parameters over time.")
    
    # Get the data
    combined_data = data['combined_data']
    sensor_info = data['sensor_info']
    daily_summary = data['daily_summary']
    
    # Create tabs for different trend analyses
    tabs = st.tabs([
        "Time Series Analysis", 
        "Seasonal Patterns", 
        "Correlation Analysis",
        "Trend Detection"
    ])
    
    # Time Series Analysis tab
    with tabs[0]:
        st.subheader("Time Series Analysis")
        
        # Create date range selector
        col1, col2 = st.columns(2)
        
        with col1:
            start_date = st.date_input(
                "Start Date",
                value=combined_data['timestamp'].min().date(),
                min_value=combined_data['timestamp'].min().date(),
                max_value=combined_data['timestamp'].max().date(),
                key="ts_start_date"
            )
        
        with col2:
            end_date = st.date_input(
                "End Date",
                value=combined_data['timestamp'].max().date(),
                min_value=combined_data['timestamp'].min().date(),
                max_value=combined_data['timestamp'].max().date(),
                key="ts_end_date"
            )
        
        # Filter data by date range
        filtered_data = combined_data[
            (combined_data['timestamp'].dt.date >= start_date) &
            (combined_data['timestamp'].dt.date <= end_date)
        ]
        
        # Parameter and sensor selection
        col1, col2 = st.columns(2)
        
        with col1:
            parameter = st.selectbox(
                "Select Parameter",
                ["pH", "Temperature", "Conductivity", "Dissolved Oxygen", "Turbidity"],
                key="ts_parameter"
            )
        
        with col2:
            # Get the number of sensors
            num_sensors = len([col for col in combined_data.columns if col.endswith('_ph')])
            
            # Create a list of sensor options with location names
            sensor_options = []
            for i in range(1, num_sensors + 1):
                sensor_info_row = sensor_info[sensor_info['sensor_id'] == i]
                if not sensor_info_row.empty:
                    location_name = sensor_info_row['location_name'].values[0]
                    sensor_options.append(f"Sensor {i} ({location_name})")
                else:
                    sensor_options.append(f"Sensor {i}")
            
            selected_sensors = st.multiselect(
                "Select Sensors",
                sensor_options,
                default=sensor_options[:3],
                key="ts_sensors"
            )
        
        # Map parameter to column name
        param_map = {
            "pH": "ph",
            "Temperature": "temp",
            "Conductivity": "conductivity",
            "Dissolved Oxygen": "dissolved_oxygen",
            "Turbidity": "turbidity"
        }
        
        param_code = param_map[parameter]
        
        # Map parameter to unit
        unit_map = {
            "pH": "",
            "Temperature": "°C",
            "Conductivity": "μS/cm",
            "Dissolved Oxygen": "mg/L",
            "Turbidity": "NTU"
        }
        
        unit = unit_map[parameter]
        
        # Extract sensor IDs from selected sensors
        selected_sensor_ids = [int(s.split()[1].split('(')[0]) for s in selected_sensors]
        
        if not selected_sensor_ids:
            st.warning("Please select at least one sensor.")
        else:
            # Create the time series plot
            fig = go.Figure()
            
            for sensor_id in selected_sensor_ids:
                # Get the sensor info
                sensor_info_row = sensor_info[sensor_info['sensor_id'] == sensor_id]
                if not sensor_info_row.empty:
                    location_name = sensor_info_row['location_name'].values[0]
                else:
                    location_name = f"Sensor {sensor_id}"
                
                # Get the column name
                col_name = f'sensor_{sensor_id}_{param_code}'
                
                if col_name in filtered_data.columns:
                    # Add the trace
                    fig.add_trace(go.Scatter(
                        x=filtered_data['timestamp'],
                        y=filtered_data[col_name],
                        mode='lines',
                        name=f"Sensor {sensor_id} ({location_name})"
                    ))
            
            # Add reference lines for pH if selected
            if parameter == "pH":
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
                title=f"{parameter} Time Series",
                xaxis_title="Timestamp",
                yaxis_title=f"{parameter} {f'({unit})' if unit else ''}",
                legend_title="Sensor",
                hovermode="x unified"
            )
            
            st.plotly_chart(fig, use_container_width=True)
            
            # Add options for moving averages
            st.subheader("Moving Averages")
            
            col1, col2 = st.columns(2)
            
            with col1:
                show_ma = st.checkbox("Show Moving Averages", value=False)
            
            if show_ma:
                with col2:
                    ma_window = st.slider(
                        "Window Size (hours)",
                        min_value=1,
                        max_value=48,
                        value=6,
                        step=1
                    )
                
                # Calculate the number of data points in the window
                # Assuming data is recorded every 15 minutes
                window_size = int(ma_window * 60 / 15)
                
                # Create the moving average plot
                fig = go.Figure()
                
                for sensor_id in selected_sensor_ids:
                    # Get the sensor info
                    sensor_info_row = sensor_info[sensor_info['sensor_id'] == sensor_id]
                    if not sensor_info_row.empty:
                        location_name = sensor_info_row['location_name'].values[0]
                    else:
                        location_name = f"Sensor {sensor_id}"
                    
                    # Get the column name
                    col_name = f'sensor_{sensor_id}_{param_code}'
                    
                    if col_name in filtered_data.columns:
                        # Calculate the moving average
                        ma_values = filtered_data[col_name].rolling(window=window_size, center=True).mean()
                        
                        # Add the trace
                        fig.add_trace(go.Scatter(
                            x=filtered_data['timestamp'],
                            y=ma_values,
                            mode='lines',
                            name=f"Sensor {sensor_id} ({location_name}) - {ma_window}h MA"
                        ))
                
                # Add reference lines for pH if selected
                if parameter == "pH":
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
                    title=f"{parameter} {ma_window}-Hour Moving Average",
                    xaxis_title="Timestamp",
                    yaxis_title=f"{parameter} {f'({unit})' if unit else ''}",
                    legend_title="Sensor",
                    hovermode="x unified"
                )
                
                st.plotly_chart(fig, use_container_width=True)
    
    # Seasonal Patterns tab
    with tabs[1]:
        st.subheader("Seasonal Patterns")
        
        # Parameter and sensor selection
        col1, col2 = st.columns(2)
        
        with col1:
            parameter = st.selectbox(
                "Select Parameter",
                ["pH", "Temperature", "Conductivity", "Dissolved Oxygen", "Turbidity"],
                key="sp_parameter"
            )
        
        with col2:
            # Get the number of sensors
            num_sensors = len([col for col in combined_data.columns if col.endswith('_ph')])
            
            # Create a list of sensor options with location names
            sensor_options = []
            for i in range(1, num_sensors + 1):
                sensor_info_row = sensor_info[sensor_info['sensor_id'] == i]
                if not sensor_info_row.empty:
                    location_name = sensor_info_row['location_name'].values[0]
                    sensor_options.append(f"Sensor {i} ({location_name})")
                else:
                    sensor_options.append(f"Sensor {i}")
            
            selected_sensor = st.selectbox(
                "Select Sensor",
                sensor_options,
                index=0,
                key="sp_sensor"
            )
        
        # Map parameter to column name
        param_map = {
            "pH": "ph",
            "Temperature": "temp",
            "Conductivity": "conductivity",
            "Dissolved Oxygen": "dissolved_oxygen",
            "Turbidity": "turbidity"
        }
        
        param_code = param_map[parameter]
        
        # Map parameter to unit
        unit_map = {
            "pH": "",
            "Temperature": "°C",
            "Conductivity": "μS/cm",
            "Dissolved Oxygen": "mg/L",
            "Turbidity": "NTU"
        }
        
        unit = unit_map[parameter]
        
        # Extract sensor ID from selected sensor
        sensor_id = int(selected_sensor.split()[1].split('(')[0])
        
        # Get the column name
        col_name = f'sensor_{sensor_id}_{param_code}'
        
        if col_name in combined_data.columns:
            # Create a copy of the data with additional time components
            pattern_data = combined_data.copy()
            pattern_data['hour'] = pattern_data['timestamp'].dt.hour
            pattern_data['day_of_week'] = pattern_data['timestamp'].dt.dayofweek
            pattern_data['day_name'] = pattern_data['timestamp'].dt.day_name()
            pattern_data['month'] = pattern_data['timestamp'].dt.month
            pattern_data['month_name'] = pattern_data['timestamp'].dt.month_name()
            
            # Create tabs for different patterns
            pattern_tabs = st.tabs(["Hourly", "Daily", "Monthly"])
            
            # Hourly pattern tab
            with pattern_tabs[0]:
                st.subheader("Hourly Pattern")
                
                # Group by hour
                hourly_data = pattern_data.groupby('hour')[col_name].agg(['mean', 'std', 'count']).reset_index()
                
                # Create the hourly pattern plot
                fig = go.Figure()
                
                # Add the mean line
                fig.add_trace(go.Scatter(
                    x=hourly_data['hour'],
                    y=hourly_data['mean'],
                    mode='lines+markers',
                    name=f"Mean {parameter}",
                    line=dict(color='blue')
                ))
                
                # Add the standard deviation range
                fig.add_trace(go.Scatter(
                    x=hourly_data['hour'].tolist() + hourly_data['hour'].tolist()[::-1],
                    y=(hourly_data['mean'] + hourly_data['std']).tolist() + 
                      (hourly_data['mean'] - hourly_data['std']).tolist()[::-1],
                    fill='toself',
                    fillcolor='rgba(0, 0, 255, 0.1)',
                    line=dict(color='rgba(255, 255, 255, 0)'),
                    hoverinfo='skip',
                    showlegend=True,
                    name=f"±1 Std Dev"
                ))
                
                # Update the layout
                fig.update_layout(
                    title=f"Hourly Pattern for {parameter} - {selected_sensor}",
                    xaxis_title="Hour of Day",
                    yaxis_title=f"{parameter} {f'({unit})' if unit else ''}",
                    xaxis=dict(
                        tickmode='array',
                        tickvals=list(range(24)),
                        ticktext=[f"{h:02d}:00" for h in range(24)]
                    ),
                    hovermode="x unified"
                )
                
                st.plotly_chart(fig, use_container_width=True)
                
                st.markdown(
                    f"This chart shows how {parameter.lower()} varies throughout the day. "
                    f"The blue line represents the average {parameter.lower()} for each hour, "
                    f"and the shaded area represents one standard deviation from the mean."
                )
            
            # Daily pattern tab
            with pattern_tabs[1]:
                st.subheader("Daily Pattern")
                
                # Group by day of week
                daily_data = pattern_data.groupby(['day_of_week', 'day_name'])[col_name].agg(['mean', 'std', 'count']).reset_index()
                
                # Sort by day of week
                daily_data = daily_data.sort_values('day_of_week')
                
                # Create the daily pattern plot
                fig = go.Figure()
                
                # Add the mean line
                fig.add_trace(go.Scatter(
                    x=daily_data['day_name'],
                    y=daily_data['mean'],
                    mode='lines+markers',
                    name=f"Mean {parameter}",
                    line=dict(color='blue')
                ))
                
                # Add the standard deviation range
                fig.add_trace(go.Scatter(
                    x=daily_data['day_name'].tolist() + daily_data['day_name'].tolist()[::-1],
                    y=(daily_data['mean'] + daily_data['std']).tolist() + 
                      (daily_data['mean'] - daily_data['std']).tolist()[::-1],
                    fill='toself',
                    fillcolor='rgba(0, 0, 255, 0.1)',
                    line=dict(color='rgba(255, 255, 255, 0)'),
                    hoverinfo='skip',
                    showlegend=True,
                    name=f"±1 Std Dev"
                ))
                
                # Update the layout
                fig.update_layout(
                    title=f"Daily Pattern for {parameter} - {selected_sensor}",
                    xaxis_title="Day of Week",
                    yaxis_title=f"{parameter} {f'({unit})' if unit else ''}",
                    hovermode="x unified"
                )
                
                st.plotly_chart(fig, use_container_width=True)
                
                st.markdown(
                    f"This chart shows how {parameter.lower()} varies throughout the week. "
                    f"The blue line represents the average {parameter.lower()} for each day, "
                    f"and the shaded area represents one standard deviation from the mean."
                )
            
            # Monthly pattern tab
            with pattern_tabs[2]:
                st.subheader("Monthly Pattern")
                
                # Group by month
                monthly_data = pattern_data.groupby(['month', 'month_name'])[col_name].agg(['mean', 'std', 'count']).reset_index()
                
                # Sort by month
                monthly_data = monthly_data.sort_values('month')
                
                # Create the monthly pattern plot
                fig = go.Figure()
                
                # Add the mean line
                fig.add_trace(go.Scatter(
                    x=monthly_data['month_name'],
                    y=monthly_data['mean'],
                    mode='lines+markers',
                    name=f"Mean {parameter}",
                    line=dict(color='blue')
                ))
                
                # Add the standard deviation range
                fig.add_trace(go.Scatter(
                    x=monthly_data['month_name'].tolist() + monthly_data['month_name'].tolist()[::-1],
                    y=(monthly_data['mean'] + monthly_data['std']).tolist() + 
                      (monthly_data['mean'] - monthly_data['std']).tolist()[::-1],
                    fill='toself',
                    fillcolor='rgba(0, 0, 255, 0.1)',
                    line=dict(color='rgba(255, 255, 255, 0)'),
                    hoverinfo='skip',
                    showlegend=True,
                    name=f"±1 Std Dev"
                ))
                
                # Update the layout
                fig.update_layout(
                    title=f"Monthly Pattern for {parameter} - {selected_sensor}",
                    xaxis_title="Month",
                    yaxis_title=f"{parameter} {f'({unit})' if unit else ''}",
                    hovermode="x unified"
                )
                
                st.plotly_chart(fig, use_container_width=True)
                
                st.markdown(
                    f"This chart shows how {parameter.lower()} varies throughout the year. "
                    f"The blue line represents the average {parameter.lower()} for each month, "
                    f"and the shaded area represents one standard deviation from the mean."
                )
    
    # Correlation Analysis tab
    with tabs[2]:
        st.subheader("Correlation Analysis")
        
        # Sensor selection
        # Get the number of sensors
        num_sensors = len([col for col in combined_data.columns if col.endswith('_ph')])
        
        # Create a list of sensor options with location names
        sensor_options = []
        for i in range(1, num_sensors + 1):
            sensor_info_row = sensor_info[sensor_info['sensor_id'] == i]
            if not sensor_info_row.empty:
                location_name = sensor_info_row['location_name'].values[0]
                sensor_options.append(f"Sensor {i} ({location_name})")
            else:
                sensor_options.append(f"Sensor {i}")
        
        selected_sensor = st.selectbox(
            "Select Sensor",
            sensor_options,
            index=0,
            key="corr_sensor"
        )
        
        # Extract sensor ID from selected sensor
        sensor_id = int(selected_sensor.split()[1].split('(')[0])
        
        # Create a dataframe with all parameters for the selected sensor
        sensor_data = combined_data[['timestamp']].copy()
        
        for param in ['ph', 'temp', 'conductivity', 'dissolved_oxygen', 'turbidity']:
            col_name = f'sensor_{sensor_id}_{param}'
            if col_name in combined_data.columns:
                sensor_data[param] = combined_data[col_name]
        
        # Calculate correlations
        corr_data = sensor_data.drop('timestamp', axis=1).corr()
        
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
            title=f"Correlation Matrix for {selected_sensor}",
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
                index=0,
                key="corr_x_param"
            )
        
        with col2:
            y_param = st.selectbox(
                "Y-axis Parameter",
                ['ph', 'temp', 'conductivity', 'dissolved_oxygen', 'turbidity'],
                index=1,
                key="corr_y_param"
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
            title=f"{y_display} vs {x_display} for {selected_sensor}",
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
        
        # Cross-correlation between sensors
        st.subheader("Cross-Sensor Correlation")
        
        # Parameter selection
        parameter = st.selectbox(
            "Select Parameter",
            ["pH", "Temperature", "Conductivity", "Dissolved Oxygen", "Turbidity"],
            key="cross_corr_parameter"
        )
        
        param_code = param_map[parameter]
        
        # Create a dataframe with the selected parameter for all sensors
        cross_corr_data = pd.DataFrame()
        
        for i in range(1, num_sensors + 1):
            col_name = f'sensor_{i}_{param_code}'
            if col_name in combined_data.columns:
                # Get the sensor info
                sensor_info_row = sensor_info[sensor_info['sensor_id'] == i]
                if not sensor_info_row.empty:
                    location_name = sensor_info_row['location_name'].values[0]
                else:
                    location_name = f"Sensor {i}"
                
                cross_corr_data[f"Sensor {i} ({location_name})"] = combined_data[col_name]
        
        # Calculate correlations
        cross_corr_matrix = cross_corr_data.corr()
        
        # Create a heatmap
        fig = px.imshow(
            cross_corr_matrix,
            x=cross_corr_matrix.columns,
            y=cross_corr_matrix.columns,
            color_continuous_scale='RdBu_r',
            zmin=-1,
            zmax=1,
            text_auto='.2f'
        )
        
        fig.update_layout(
            title=f"Cross-Sensor Correlation Matrix for {parameter}",
            xaxis_title="Sensor",
            yaxis_title="Sensor"
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
        st.markdown(
            f"This heatmap shows the correlation of {parameter.lower()} readings between different sensors. "
            "A high correlation indicates that sensors are measuring similar patterns, "
            "while a low correlation may indicate different water conditions or sensor issues."
        )
    
    # Trend Detection tab
    with tabs[3]:
        st.subheader("Trend Detection")
        
        # Parameter and sensor selection
        col1, col2 = st.columns(2)
        
        with col1:
            parameter = st.selectbox(
                "Select Parameter",
                ["pH", "Temperature", "Conductivity", "Dissolved Oxygen", "Turbidity"],
                key="trend_parameter"
            )
        
        with col2:
            # Get the number of sensors
            num_sensors = len([col for col in combined_data.columns if col.endswith('_ph')])
            
            # Create a list of sensor options with location names
            sensor_options = []
            for i in range(1, num_sensors + 1):
                sensor_info_row = sensor_info[sensor_info['sensor_id'] == i]
                if not sensor_info_row.empty:
                    location_name = sensor_info_row['location_name'].values[0]
                    sensor_options.append(f"Sensor {i} ({location_name})")
                else:
                    sensor_options.append(f"Sensor {i}")
            
            selected_sensor = st.selectbox(
                "Select Sensor",
                sensor_options,
                index=0,
                key="trend_sensor"
            )
        
        # Map parameter to column name
        param_map = {
            "pH": "ph",
            "Temperature": "temp",
            "Conductivity": "conductivity",
            "Dissolved Oxygen": "dissolved_oxygen",
            "Turbidity": "turbidity"
        }
        
        param_code = param_map[parameter]
        
        # Map parameter to unit
        unit_map = {
            "pH": "",
            "Temperature": "°C",
            "Conductivity": "μS/cm",
            "Dissolved Oxygen": "mg/L",
            "Turbidity": "NTU"
        }
        
        unit = unit_map[parameter]
        
        # Extract sensor ID from selected sensor
        sensor_id = int(selected_sensor.split()[1].split('(')[0])
        
        # Get the column name
        col_name = f'sensor_{sensor_id}_{param_code}'
        
        if col_name in combined_data.columns:
            # Create a copy of the data with the selected parameter
            trend_data = combined_data[['timestamp', col_name]].copy()
            
            # Resample to daily data for trend analysis
            trend_data.set_index('timestamp', inplace=True)
            daily_data = trend_data.resample('D').mean().reset_index()
            
            # Perform Mann-Kendall trend test
            # This test checks if there's a monotonic upward or downward trend
            x = np.arange(len(daily_data))
            y = daily_data[col_name].values
            
            # Calculate the Mann-Kendall test
            result = stats.kendalltau(x, y)
            tau, p_value = result
            
            # Determine if there's a significant trend
            alpha = 0.05
            if p_value < alpha:
                if tau > 0:
                    trend_direction = "increasing"
                    trend_color = "red"
                else:
                    trend_direction = "decreasing"
                    trend_color = "blue"
                
                trend_message = (
                    f"**Significant {trend_direction} trend detected** "
                    f"(p-value: {p_value:.4f}, tau: {tau:.4f})"
                )
            else:
                trend_direction = "no significant"
                trend_color = "gray"
                trend_message = (
                    f"**No significant trend detected** "
                    f"(p-value: {p_value:.4f}, tau: {tau:.4f})"
                )
            
            # Display the trend result
            st.markdown(f"### Trend Analysis for {parameter} - {selected_sensor}")
            
            st.markdown(trend_message)
            
            # Create the trend plot
            fig = go.Figure()
            
            # Add the daily data
            fig.add_trace(go.Scatter(
                x=daily_data['timestamp'],
                y=daily_data[col_name],
                mode='markers',
                name=f"Daily {parameter}",
                marker=dict(color='black', size=5)
            ))
            
            # Add a linear regression line
            z = np.polyfit(x, y, 1)
            p = np.poly1d(z)
            
            fig.add_trace(go.Scatter(
                x=daily_data['timestamp'],
                y=p(x),
                mode='lines',
                name=f"Trend Line (slope: {z[0]:.4f})",
                line=dict(color=trend_color, width=2)
            ))
            
            # Update the layout
            fig.update_layout(
                title=f"Trend Analysis for {parameter} - {selected_sensor}",
                xaxis_title="Date",
                yaxis_title=f"{parameter} {f'({unit})' if unit else ''}",
                legend_title="Parameter",
                hovermode="x unified"
            )
            
            st.plotly_chart(fig, use_container_width=True)
            
            # Add explanation
            st.markdown(
                f"This chart shows the daily average {parameter.lower()} values and the overall trend. "
                f"The trend line shows the general direction of change over time."
            )
            
            # Add seasonal decomposition
            st.subheader("Seasonal Decomposition")
            
            st.markdown(
                "Seasonal decomposition breaks down a time series into trend, seasonal, and residual components. "
                "This can help identify underlying patterns in the data."
            )
            
            # Check if we have enough data for seasonal decomposition
            if len(daily_data) >= 14:  # Need at least 2 weeks of data
                try:
                    # Create a button to perform seasonal decomposition
                    if st.button("Perform Seasonal Decomposition"):
                        from statsmodels.tsa.seasonal import seasonal_decompose
                        
                        # Set the index to timestamp for decomposition
                        decomp_data = daily_data.set_index('timestamp')
                        
                        # Perform seasonal decomposition
                        # Period is set to 7 for weekly seasonality
                        result = seasonal_decompose(decomp_data[col_name], model='additive', period=7)
                        
                        # Create a figure with subplots
                        fig = go.Figure()
                        
                        # Add the observed data
                        fig.add_trace(go.Scatter(
                            x=decomp_data.index,
                            y=result.observed,
                            mode='lines',
                            name='Observed'
                        ))
                        
                        # Add the trend component
                        fig.add_trace(go.Scatter(
                            x=decomp_data.index,
                            y=result.trend,
                            mode='lines',
                            name='Trend',
                            line=dict(color='red')
                        ))
                        
                        # Add the seasonal component
                        fig.add_trace(go.Scatter(
                            x=decomp_data.index,
                            y=result.seasonal,
                            mode='lines',
                            name='Seasonal',
                            line=dict(color='green')
                        ))
                        
                        # Add the residual component
                        fig.add_trace(go.Scatter(
                            x=decomp_data.index,
                            y=result.resid,
                            mode='lines',
                            name='Residual',
                            line=dict(color='purple')
                        ))
                        
                        # Update the layout
                        fig.update_layout(
                            title=f"Seasonal Decomposition for {parameter} - {selected_sensor}",
                            xaxis_title="Date",
                            yaxis_title="Component Value",
                            legend_title="Component",
                            hovermode="x unified"
                        )
                        
                        st.plotly_chart(fig, use_container_width=True)
                        
                        st.markdown(
                            "**Components:**\n"
                            "- **Observed**: The original data\n"
                            "- **Trend**: The overall direction of the data\n"
                            "- **Seasonal**: Repeating patterns in the data\n"
                            "- **Residual**: The remaining variation after removing trend and seasonal components"
                        )
                    else:
                        st.info("Click the button to perform seasonal decomposition.")
                except Exception as e:
                    st.error(f"Error performing seasonal decomposition: {str(e)}")
            else:
                st.warning(
                    "Not enough data for seasonal decomposition. "
                    "At least 14 days of data are required."
                )
