import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
from scipy import stats

def detect_anomalies_zscore(data, column, threshold=3.0):
    """
    Detect anomalies using Z-score method.
    
    Parameters:
    - data: DataFrame containing the data
    - column: Column name to check for anomalies
    - threshold: Z-score threshold (default: 3.0)
    
    Returns:
    - DataFrame with anomaly flags
    """
    # Calculate Z-scores
    mean = data[column].mean()
    std = data[column].std()
    data['zscore'] = abs((data[column] - mean) / std)
    
    # Flag anomalies
    data['anomaly'] = data['zscore'] > threshold
    
    return data

def detect_anomalies_iqr(data, column, multiplier=1.5):
    """
    Detect anomalies using IQR method.
    
    Parameters:
    - data: DataFrame containing the data
    - column: Column name to check for anomalies
    - multiplier: IQR multiplier (default: 1.5)
    
    Returns:
    - DataFrame with anomaly flags
    """
    # Calculate IQR
    q1 = data[column].quantile(0.25)
    q3 = data[column].quantile(0.75)
    iqr = q3 - q1
    
    # Calculate bounds
    lower_bound = q1 - multiplier * iqr
    upper_bound = q3 + multiplier * iqr
    
    # Flag anomalies
    data['anomaly'] = (data[column] < lower_bound) | (data[column] > upper_bound)
    data['lower_bound'] = lower_bound
    data['upper_bound'] = upper_bound
    
    return data

def detect_anomalies_rolling(data, column, window=24, threshold=3.0):
    """
    Detect anomalies using rolling Z-score method.
    
    Parameters:
    - data: DataFrame containing the data
    - column: Column name to check for anomalies
    - window: Rolling window size (default: 24)
    - threshold: Z-score threshold (default: 3.0)
    
    Returns:
    - DataFrame with anomaly flags
    """
    # Calculate rolling mean and std
    data['rolling_mean'] = data[column].rolling(window=window, center=True).mean()
    data['rolling_std'] = data[column].rolling(window=window, center=True).std()
    
    # Calculate Z-scores
    data['zscore'] = abs((data[column] - data['rolling_mean']) / data['rolling_std'])
    
    # Flag anomalies
    data['anomaly'] = data['zscore'] > threshold
    
    # Fill NaN values in anomaly column
    data['anomaly'] = data['anomaly'].fillna(False)
    
    return data

def show_anomaly_detection_dashboard(data):
    """
    Display anomaly detection dashboard for all sensors.
    
    Parameters:
    - data: Dictionary containing all sensor data
    """
    st.header("Anomaly Detection Dashboard")
    st.markdown("This dashboard helps identify anomalies in water quality parameters.")
    
    # Get the data
    combined_data = data['combined_data']
    sensor_info = data['sensor_info']
    
    # Create tabs for different anomaly detection methods
    tabs = st.tabs([
        "Time Series Anomalies", 
        "Statistical Anomalies", 
        "Correlation Anomalies",
        "Anomaly Summary"
    ])
    
    # Time Series Anomalies tab
    with tabs[0]:
        st.subheader("Time Series Anomalies")
        
        # Parameter and sensor selection
        col1, col2, col3 = st.columns(3)
        
        with col1:
            parameter = st.selectbox(
                "Select Parameter",
                ["pH", "Temperature", "Conductivity", "Dissolved Oxygen", "Turbidity"],
                key="ts_anomaly_parameter"
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
                key="ts_anomaly_sensor"
            )
        
        with col3:
            detection_method = st.selectbox(
                "Detection Method",
                ["Z-Score", "IQR", "Rolling Z-Score"],
                key="ts_anomaly_method"
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
            anomaly_data = combined_data[['timestamp', col_name]].copy()
            
            # Method-specific parameters
            if detection_method == "Z-Score":
                threshold = st.slider(
                    "Z-Score Threshold",
                    min_value=1.0,
                    max_value=5.0,
                    value=3.0,
                    step=0.1,
                    key="zscore_threshold"
                )
                
                # Detect anomalies
                anomaly_data = detect_anomalies_zscore(anomaly_data, col_name, threshold)
                
                # Create the plot
                fig = go.Figure()
                
                # Add the data
                fig.add_trace(go.Scatter(
                    x=anomaly_data['timestamp'],
                    y=anomaly_data[col_name],
                    mode='lines',
                    name=parameter,
                    line=dict(color='blue')
                ))
                
                # Add anomalies
                anomalies = anomaly_data[anomaly_data['anomaly']]
                
                fig.add_trace(go.Scatter(
                    x=anomalies['timestamp'],
                    y=anomalies[col_name],
                    mode='markers',
                    name='Anomalies',
                    marker=dict(color='red', size=8, symbol='circle')
                ))
                
                # Update the layout
                fig.update_layout(
                    title=f"Z-Score Anomaly Detection for {parameter} - {selected_sensor}",
                    xaxis_title="Timestamp",
                    yaxis_title=f"{parameter} {f'({unit})' if unit else ''}",
                    legend_title="Data",
                    hovermode="closest"
                )
                
                st.plotly_chart(fig, use_container_width=True)
                
                # Display explanation
                st.markdown(
                    f"This chart shows anomalies detected using the Z-Score method with a threshold of {threshold}. "
                    f"Points are flagged as anomalies if they are more than {threshold} standard deviations away from the mean."
                )
                
                # Display anomaly statistics
                num_anomalies = anomalies.shape[0]
                anomaly_percent = (num_anomalies / anomaly_data.shape[0]) * 100
                
                st.metric("Number of Anomalies", num_anomalies)
                st.metric("Percentage of Anomalies", f"{anomaly_percent:.2f}%")
                
                # Display anomalies in a table
                if not anomalies.empty:
                    st.subheader("Anomaly Details")
                    
                    # Format the table
                    anomaly_table = anomalies[['timestamp', col_name, 'zscore']].copy()
                    anomaly_table.columns = ['Timestamp', parameter, 'Z-Score']
                    
                    st.dataframe(anomaly_table, use_container_width=True)
                else:
                    st.info("No anomalies detected with the current threshold.")
            
            elif detection_method == "IQR":
                multiplier = st.slider(
                    "IQR Multiplier",
                    min_value=1.0,
                    max_value=3.0,
                    value=1.5,
                    step=0.1,
                    key="iqr_multiplier"
                )
                
                # Detect anomalies
                anomaly_data = detect_anomalies_iqr(anomaly_data, col_name, multiplier)
                
                # Create the plot
                fig = go.Figure()
                
                # Add the data
                fig.add_trace(go.Scatter(
                    x=anomaly_data['timestamp'],
                    y=anomaly_data[col_name],
                    mode='lines',
                    name=parameter,
                    line=dict(color='blue')
                ))
                
                # Add anomalies
                anomalies = anomaly_data[anomaly_data['anomaly']]
                
                fig.add_trace(go.Scatter(
                    x=anomalies['timestamp'],
                    y=anomalies[col_name],
                    mode='markers',
                    name='Anomalies',
                    marker=dict(color='red', size=8, symbol='circle')
                ))
                
                # Add bounds
                fig.add_shape(
                    type="line",
                    x0=anomaly_data['timestamp'].min(),
                    y0=anomaly_data['lower_bound'].iloc[0],
                    x1=anomaly_data['timestamp'].max(),
                    y1=anomaly_data['lower_bound'].iloc[0],
                    line=dict(color="red", width=1, dash="dash"),
                    name="Lower Bound"
                )
                
                fig.add_shape(
                    type="line",
                    x0=anomaly_data['timestamp'].min(),
                    y0=anomaly_data['upper_bound'].iloc[0],
                    x1=anomaly_data['timestamp'].max(),
                    y1=anomaly_data['upper_bound'].iloc[0],
                    line=dict(color="red", width=1, dash="dash"),
                    name="Upper Bound"
                )
                
                # Update the layout
                fig.update_layout(
                    title=f"IQR Anomaly Detection for {parameter} - {selected_sensor}",
                    xaxis_title="Timestamp",
                    yaxis_title=f"{parameter} {f'({unit})' if unit else ''}",
                    legend_title="Data",
                    hovermode="closest"
                )
                
                st.plotly_chart(fig, use_container_width=True)
                
                # Display explanation
                st.markdown(
                    f"This chart shows anomalies detected using the IQR method with a multiplier of {multiplier}. "
                    f"Points are flagged as anomalies if they are below Q1-{multiplier}*IQR or above Q3+{multiplier}*IQR."
                )
                
                # Display anomaly statistics
                num_anomalies = anomalies.shape[0]
                anomaly_percent = (num_anomalies / anomaly_data.shape[0]) * 100
                
                st.metric("Number of Anomalies", num_anomalies)
                st.metric("Percentage of Anomalies", f"{anomaly_percent:.2f}%")
                
                # Display anomalies in a table
                if not anomalies.empty:
                    st.subheader("Anomaly Details")
                    
                    # Format the table
                    anomaly_table = anomalies[['timestamp', col_name]].copy()
                    anomaly_table.columns = ['Timestamp', parameter]
                    
                    st.dataframe(anomaly_table, use_container_width=True)
                else:
                    st.info("No anomalies detected with the current multiplier.")
            
            elif detection_method == "Rolling Z-Score":
                col1, col2 = st.columns(2)
                
                with col1:
                    window = st.slider(
                        "Window Size (hours)",
                        min_value=1,
                        max_value=48,
                        value=24,
                        step=1,
                        key="rolling_window"
                    )
                
                with col2:
                    threshold = st.slider(
                        "Z-Score Threshold",
                        min_value=1.0,
                        max_value=5.0,
                        value=3.0,
                        step=0.1,
                        key="rolling_threshold"
                    )
                
                # Convert window from hours to data points (assuming 15-minute intervals)
                window_points = int(window * 60 / 15)
                
                # Detect anomalies
                anomaly_data = detect_anomalies_rolling(anomaly_data, col_name, window_points, threshold)
                
                # Create the plot
                fig = go.Figure()
                
                # Add the data
                fig.add_trace(go.Scatter(
                    x=anomaly_data['timestamp'],
                    y=anomaly_data[col_name],
                    mode='lines',
                    name=parameter,
                    line=dict(color='blue')
                ))
                
                # Add rolling mean
                fig.add_trace(go.Scatter(
                    x=anomaly_data['timestamp'],
                    y=anomaly_data['rolling_mean'],
                    mode='lines',
                    name='Rolling Mean',
                    line=dict(color='green', dash='dash')
                ))
                
                # Add anomalies
                anomalies = anomaly_data[anomaly_data['anomaly']]
                
                fig.add_trace(go.Scatter(
                    x=anomalies['timestamp'],
                    y=anomalies[col_name],
                    mode='markers',
                    name='Anomalies',
                    marker=dict(color='red', size=8, symbol='circle')
                ))
                
                # Update the layout
                fig.update_layout(
                    title=f"Rolling Z-Score Anomaly Detection for {parameter} - {selected_sensor}",
                    xaxis_title="Timestamp",
                    yaxis_title=f"{parameter} {f'({unit})' if unit else ''}",
                    legend_title="Data",
                    hovermode="closest"
                )
                
                st.plotly_chart(fig, use_container_width=True)
                
                # Display explanation
                st.markdown(
                    f"This chart shows anomalies detected using the Rolling Z-Score method with a window of {window} hours "
                    f"and a threshold of {threshold}. Points are flagged as anomalies if they are more than {threshold} "
                    f"standard deviations away from the rolling mean."
                )
                
                # Display anomaly statistics
                num_anomalies = anomalies.shape[0]
                anomaly_percent = (num_anomalies / anomaly_data.shape[0]) * 100
                
                st.metric("Number of Anomalies", num_anomalies)
                st.metric("Percentage of Anomalies", f"{anomaly_percent:.2f}%")
                
                # Display anomalies in a table
                if not anomalies.empty:
                    st.subheader("Anomaly Details")
                    
                    # Format the table
                    anomaly_table = anomalies[['timestamp', col_name, 'zscore']].copy()
                    anomaly_table.columns = ['Timestamp', parameter, 'Z-Score']
                    
                    st.dataframe(anomaly_table, use_container_width=True)
                else:
                    st.info("No anomalies detected with the current settings.")
    
    # Statistical Anomalies tab
    with tabs[1]:
        st.subheader("Statistical Anomalies")
        
        # Parameter and sensor selection
        col1, col2 = st.columns(2)
        
        with col1:
            parameter = st.selectbox(
                "Select Parameter",
                ["pH", "Temperature", "Conductivity", "Dissolved Oxygen", "Turbidity"],
                key="stat_anomaly_parameter"
            )
        
        with col2:
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
                key="stat_anomaly_sensor"
            )
        
        # Map parameter to column name
        param_code = param_map[parameter]
        unit = unit_map[parameter]
        
        # Extract sensor ID from selected sensor
        sensor_id = int(selected_sensor.split()[1].split('(')[0])
        
        # Get the column name
        col_name = f'sensor_{sensor_id}_{param_code}'
        
        if col_name in combined_data.columns:
            # Create a copy of the data with the selected parameter
            stat_data = combined_data[['timestamp', col_name]].copy()
            
            # Create a box plot
            fig = go.Figure()
            
            fig.add_trace(go.Box(
                y=stat_data[col_name],
                name=parameter,
                boxpoints='outliers',
                jitter=0.3,
                pointpos=-1.8,
                marker=dict(
                    color='blue',
                    outliercolor='red',
                    size=6
                )
            ))
            
            # Update the layout
            fig.update_layout(
                title=f"Box Plot for {parameter} - {selected_sensor}",
                yaxis_title=f"{parameter} {f'({unit})' if unit else ''}",
                showlegend=False
            )
            
            st.plotly_chart(fig, use_container_width=True)
            
            # Display explanation
            st.markdown(
                "This box plot shows the distribution of values and highlights outliers. "
                "The box represents the interquartile range (IQR), the line inside the box is the median, "
                "and the whiskers extend to 1.5 times the IQR. Points outside the whiskers are considered outliers."
            )
            
            # Create a histogram
            fig = px.histogram(
                stat_data,
                x=col_name,
                nbins=30,
                marginal="box",
                title=f"Histogram for {parameter} - {selected_sensor}"
            )
            
            fig.update_layout(
                xaxis_title=f"{parameter} {f'({unit})' if unit else ''}",
                yaxis_title="Frequency"
            )
            
            st.plotly_chart(fig, use_container_width=True)
            
            # Display statistics
            st.subheader("Statistical Summary")
            
            # Calculate statistics
            stat_values = {
                'Mean': stat_data[col_name].mean(),
                'Median': stat_data[col_name].median(),
                'Std Dev': stat_data[col_name].std(),
                'Min': stat_data[col_name].min(),
                'Max': stat_data[col_name].max(),
                'Range': stat_data[col_name].max() - stat_data[col_name].min(),
                'Q1': stat_data[col_name].quantile(0.25),
                'Q3': stat_data[col_name].quantile(0.75),
                'IQR': stat_data[col_name].quantile(0.75) - stat_data[col_name].quantile(0.25)
            }
            
            # Create a dataframe for the statistics
            stats_df = pd.DataFrame(stat_values.items(), columns=['Statistic', 'Value'])
            
            # Display the statistics
            col1, col2, col3 = st.columns(3)
            
            col1.metric("Mean", f"{stat_values['Mean']:.2f}")
            col1.metric("Median", f"{stat_values['Median']:.2f}")
            col1.metric("Std Dev", f"{stat_values['Std Dev']:.2f}")
            
            col2.metric("Min", f"{stat_values['Min']:.2f}")
            col2.metric("Max", f"{stat_values['Max']:.2f}")
            col2.metric("Range", f"{stat_values['Range']:.2f}")
            
            col3.metric("Q1", f"{stat_values['Q1']:.2f}")
            col3.metric("Q3", f"{stat_values['Q3']:.2f}")
            col3.metric("IQR", f"{stat_values['IQR']:.2f}")
            
            # Detect outliers using IQR method
            q1 = stat_values['Q1']
            q3 = stat_values['Q3']
            iqr = stat_values['IQR']
            
            lower_bound = q1 - 1.5 * iqr
            upper_bound = q3 + 1.5 * iqr
            
            outliers = stat_data[(stat_data[col_name] < lower_bound) | (stat_data[col_name] > upper_bound)]
            
            # Display outliers
            st.subheader("Outliers")
            
            num_outliers = outliers.shape[0]
            outlier_percent = (num_outliers / stat_data.shape[0]) * 100
            
            st.metric("Number of Outliers", num_outliers)
            st.metric("Percentage of Outliers", f"{outlier_percent:.2f}%")
            
            if not outliers.empty:
                # Format the table
                outlier_table = outliers[['timestamp', col_name]].copy()
                outlier_table.columns = ['Timestamp', parameter]
                
                st.dataframe(outlier_table, use_container_width=True)
            else:
                st.info("No outliers detected.")
    
    # Correlation Anomalies tab
    with tabs[2]:
        st.subheader("Correlation Anomalies")
        
        # Sensor selection
        selected_sensor = st.selectbox(
            "Select Sensor",
            sensor_options,
            index=0,
            key="corr_anomaly_sensor"
        )
        
        # Extract sensor ID from selected sensor
        sensor_id = int(selected_sensor.split()[1].split('(')[0])
        
        # Create a dataframe with all parameters for the selected sensor
        sensor_data = combined_data[['timestamp']].copy()
        
        for param in ['ph', 'temp', 'conductivity', 'dissolved_oxygen', 'turbidity']:
            col_name = f'sensor_{sensor_id}_{param}'
            if col_name in combined_data.columns:
                sensor_data[param] = combined_data[col_name]
        
        # Parameter selection
        col1, col2 = st.columns(2)
        
        with col1:
            x_param = st.selectbox(
                "X-axis Parameter",
                ['ph', 'temp', 'conductivity', 'dissolved_oxygen', 'turbidity'],
                index=0,
                key="corr_anomaly_x_param"
            )
        
        with col2:
            y_param = st.selectbox(
                "Y-axis Parameter",
                ['ph', 'temp', 'conductivity', 'dissolved_oxygen', 'turbidity'],
                index=1,
                key="corr_anomaly_y_param"
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
        
        # Calculate the correlation
        corr = sensor_data[[x_param, y_param]].corr().iloc[0, 1]
        
        # Detect correlation anomalies
        # We'll use Mahalanobis distance to detect multivariate outliers
        
        # First, we need to standardize the data
        X = sensor_data[[x_param, y_param]].copy()
        X_std = (X - X.mean()) / X.std()
        
        # Calculate the covariance matrix
        cov_matrix = X_std.cov()
        
        # Calculate the inverse of the covariance matrix
        inv_cov_matrix = np.linalg.inv(cov_matrix)
        
        # Calculate the Mahalanobis distance
        X_std['mahalanobis'] = X_std.apply(
            lambda x: np.sqrt(x.values @ inv_cov_matrix @ x.values),
            axis=1
        )
        
        # Set a threshold for anomalies
        # Chi-square with 2 degrees of freedom, 95% confidence
        threshold = np.sqrt(stats.chi2.ppf(0.95, 2))
        
        # Flag anomalies
        X_std['anomaly'] = X_std['mahalanobis'] > threshold
        
        # Add the anomaly flag to the original data
        sensor_data['anomaly'] = X_std['anomaly']
        sensor_data['mahalanobis'] = X_std['mahalanobis']
        
        # Create the scatter plot
        fig = px.scatter(
            sensor_data,
            x=x_param,
            y=y_param,
            color='anomaly',
            color_discrete_map={True: 'red', False: 'blue'},
            opacity=0.7,
            hover_data=['timestamp', 'mahalanobis']
        )
        
        # Add a trendline
        fig.add_trace(
            px.scatter(
                sensor_data,
                x=x_param,
                y=y_param,
                trendline="ols"
            ).data[1]
        )
        
        # Update the layout
        fig.update_layout(
            title=f"Correlation Anomalies: {y_display} vs {x_display} - {selected_sensor}",
            xaxis_title=f"{x_display} {f'({x_unit})' if x_unit else ''}",
            yaxis_title=f"{y_display} {f'({y_unit})' if y_unit else ''}",
            legend_title="Anomaly"
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
        # Display explanation
        st.markdown(
            f"This chart shows correlation anomalies between {x_display.lower()} and {y_display.lower()}. "
            f"Points are flagged as anomalies if they deviate significantly from the expected relationship "
            f"based on the Mahalanobis distance."
        )
        
        # Display correlation
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
        
        # Display anomaly statistics
        anomalies = sensor_data[sensor_data['anomaly']]
        
        num_anomalies = anomalies.shape[0]
        anomaly_percent = (num_anomalies / sensor_data.shape[0]) * 100
        
        st.metric("Number of Correlation Anomalies", num_anomalies)
        st.metric("Percentage of Correlation Anomalies", f"{anomaly_percent:.2f}%")
        
        # Display anomalies in a table
        if not anomalies.empty:
            st.subheader("Anomaly Details")
            
            # Format the table
            anomaly_table = anomalies[['timestamp', x_param, y_param, 'mahalanobis']].copy()
            anomaly_table.columns = ['Timestamp', x_display, y_display, 'Mahalanobis Distance']
            
            st.dataframe(anomaly_table, use_container_width=True)
        else:
            st.info("No correlation anomalies detected.")
    
    # Anomaly Summary tab
    with tabs[3]:
        st.subheader("Anomaly Summary")
        
        # Create a summary of anomalies for all sensors and parameters
        st.markdown("This tab provides a summary of anomalies detected across all sensors and parameters.")
        
        # Method selection
        detection_method = st.selectbox(
            "Detection Method",
            ["Z-Score", "IQR", "Rolling Z-Score"],
            key="summary_method"
        )
        
        # Method-specific parameters
        if detection_method == "Z-Score":
            threshold = st.slider(
                "Z-Score Threshold",
                min_value=1.0,
                max_value=5.0,
                value=3.0,
                step=0.1,
                key="summary_zscore_threshold"
            )
        elif detection_method == "IQR":
            multiplier = st.slider(
                "IQR Multiplier",
                min_value=1.0,
                max_value=3.0,
                value=1.5,
                step=0.1,
                key="summary_iqr_multiplier"
            )
        elif detection_method == "Rolling Z-Score":
            col1, col2 = st.columns(2)
            
            with col1:
                window = st.slider(
                    "Window Size (hours)",
                    min_value=1,
                    max_value=48,
                    value=24,
                    step=1,
                    key="summary_rolling_window"
                )
            
            with col2:
                threshold = st.slider(
                    "Z-Score Threshold",
                    min_value=1.0,
                    max_value=5.0,
                    value=3.0,
                    step=0.1,
                    key="summary_rolling_threshold"
                )
        
        # Create a button to run the analysis
        if st.button("Run Anomaly Detection"):
            # Create a progress bar
            progress_bar = st.progress(0)
            
            # Create a dataframe to store the results
            results = []
            
            # Get the number of sensors and parameters
            num_sensors = len([col for col in combined_data.columns if col.endswith('_ph')])
            parameters = ['ph', 'temp', 'conductivity', 'dissolved_oxygen', 'turbidity']
            
            # Calculate the total number of combinations
            total_combinations = num_sensors * len(parameters)
            current_combination = 0
            
            # Loop through all sensors and parameters
            for sensor_id in range(1, num_sensors + 1):
                # Get the sensor info
                sensor_info_row = sensor_info[sensor_info['sensor_id'] == sensor_id]
                if not sensor_info_row.empty:
                    location_name = sensor_info_row['location_name'].values[0]
                else:
                    location_name = f"Sensor {sensor_id}"
                
                for param in parameters:
                    # Get the column name
                    col_name = f'sensor_{sensor_id}_{param}'
                    
                    if col_name in combined_data.columns:
                        # Create a copy of the data with the selected parameter
                        anomaly_data = combined_data[['timestamp', col_name]].copy()
                        
                        # Detect anomalies based on the selected method
                        if detection_method == "Z-Score":
                            anomaly_data = detect_anomalies_zscore(anomaly_data, col_name, threshold)
                        elif detection_method == "IQR":
                            anomaly_data = detect_anomalies_iqr(anomaly_data, col_name, multiplier)
                        elif detection_method == "Rolling Z-Score":
                            # Convert window from hours to data points (assuming 15-minute intervals)
                            window_points = int(window * 60 / 15)
                            anomaly_data = detect_anomalies_rolling(anomaly_data, col_name, window_points, threshold)
                        
                        # Count the anomalies
                        anomalies = anomaly_data[anomaly_data['anomaly']]
                        num_anomalies = anomalies.shape[0]
                        anomaly_percent = (num_anomalies / anomaly_data.shape[0]) * 100
                        
                        # Add the results to the dataframe
                        results.append({
                            'Sensor ID': sensor_id,
                            'Location': location_name,
                            'Parameter': param,
                            'Parameter Display': params[param]['name'],
                            'Total Points': anomaly_data.shape[0],
                            'Anomalies': num_anomalies,
                            'Anomaly %': anomaly_percent
                        })
                    
                    # Update the progress bar
                    current_combination += 1
                    progress_bar.progress(current_combination / total_combinations)
            
            # Create a dataframe from the results
            results_df = pd.DataFrame(results)
            
            # Sort by anomaly percentage
            results_df = results_df.sort_values('Anomaly %', ascending=False)
            
            # Display the results
            st.subheader("Anomaly Summary")
            
            # Format the dataframe for display
            display_df = results_df.copy()
            display_df['Anomaly %'] = display_df['Anomaly %'].apply(lambda x: f"{x:.2f}%")
            
            st.dataframe(display_df, use_container_width=True)
            
            # Create a bar chart of anomaly percentages
            fig = px.bar(
                results_df,
                x='Parameter Display',
                y='Anomaly %',
                color='Location',
                barmode='group',
                title="Anomaly Percentage by Parameter and Location"
            )
            
            fig.update_layout(
                xaxis_title="Parameter",
                yaxis_title="Anomaly Percentage (%)",
                legend_title="Location"
            )
            
            st.plotly_chart(fig, use_container_width=True)
            
            # Create a heatmap of anomaly counts
            heatmap_data = results_df.pivot_table(
                values='Anomalies',
                index='Location',
                columns='Parameter Display'
            )
            
            fig = px.imshow(
                heatmap_data,
                text_auto=True,
                color_continuous_scale='Viridis',
                title="Anomaly Count by Parameter and Location"
            )
            
            fig.update_layout(
                xaxis_title="Parameter",
                yaxis_title="Location"
            )
            
            st.plotly_chart(fig, use_container_width=True)
            
            # Display the most anomalous parameter-location combinations
            st.subheader("Most Anomalous Parameter-Location Combinations")
            
            top_anomalies = results_df.head(5)
            
            for _, row in top_anomalies.iterrows():
                st.markdown(
                    f"**{row['Parameter Display']} at {row['Location']}**: "
                    f"{row['Anomalies']} anomalies ({row['Anomaly %']:.2f}%)"
                )
        else:
            st.info("Click the button to run anomaly detection across all sensors and parameters.")
