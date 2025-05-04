import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta

def show_maintenance_dashboard(data):
    """
    Display maintenance dashboard for all sensors.
    
    Parameters:
    - data: Dictionary containing all sensor data
    """
    st.header("Maintenance Dashboard")
    st.markdown("This dashboard provides information about sensor maintenance and calibration schedules.")
    
    # Get the data
    combined_data = data['combined_data']
    sensor_info = data['sensor_info']
    
    # Create tabs for different maintenance views
    tabs = st.tabs([
        "Maintenance Overview", 
        "Calibration Schedule", 
        "Sensor Health",
        "Maintenance History"
    ])
    
    # Maintenance Overview tab
    with tabs[0]:
        st.subheader("Maintenance Overview")
        
        # Create a dataframe with maintenance information
        maintenance_df = sensor_info.copy()
        
        # Calculate days since last calibration
        maintenance_df['last_calibration'] = pd.to_datetime(maintenance_df['last_calibration'])
        maintenance_df['days_since_calibration'] = (datetime.now() - maintenance_df['last_calibration']).dt.days
        
        # Calculate days until next calibration
        maintenance_df['next_calibration_due'] = maintenance_df['last_calibration'] + pd.to_timedelta(maintenance_df['maintenance_interval_days'], unit='D')
        maintenance_df['days_until_next_calibration'] = (maintenance_df['next_calibration_due'] - datetime.now()).dt.days
        
        # Determine calibration status
        maintenance_df['calibration_status'] = maintenance_df.apply(
            lambda x: "Overdue" if x['days_until_next_calibration'] < 0 else 
                     ("Due Soon" if x['days_until_next_calibration'] < 7 else "OK"),
            axis=1
        )
        
        # Create a summary card for each sensor
        st.markdown("### Sensor Maintenance Status")
        
        # Create a grid of cards
        cols = st.columns(3)
        
        for i, (_, row) in enumerate(maintenance_df.iterrows()):
            with cols[i % 3]:
                # Determine card color based on status
                if row['calibration_status'] == "Overdue":
                    card_color = "red"
                    icon = "❌"
                elif row['calibration_status'] == "Due Soon":
                    card_color = "orange"
                    icon = "⚠️"
                else:
                    card_color = "green"
                    icon = "✅"
                
                # Create the card
                st.markdown(
                    f"""
                    <div style="
                        padding: 1rem;
                        border-radius: 0.5rem;
                        margin-bottom: 1rem;
                        border-left: 5px solid {card_color};
                        background-color: rgba({','.join(['255' if c == 'red' else '255' if c == 'orange' else '0' for c in [card_color]])}, 0.1);
                    ">
                        <h4 style="margin-top: 0;">{icon} Sensor {row['sensor_id']}: {row['location_name']}</h4>
                        <p><strong>Last Calibration:</strong> {row['last_calibration'].strftime('%Y-%m-%d')}</p>
                        <p><strong>Days Since Calibration:</strong> {row['days_since_calibration']}</p>
                        <p><strong>Next Calibration Due:</strong> {row['next_calibration_due'].strftime('%Y-%m-%d')}</p>
                        <p><strong>Days Until Due:</strong> {row['days_until_next_calibration'] if row['days_until_next_calibration'] >= 0 else f"Overdue by {abs(row['days_until_next_calibration'])}"}</p>
                        <p><strong>Status:</strong> <span style="color: {card_color};">{row['calibration_status']}</span></p>
                    </div>
                    """,
                    unsafe_allow_html=True
                )
        
        # Create a summary of maintenance status
        st.markdown("### Maintenance Summary")
        
        # Count sensors by status
        status_counts = maintenance_df['calibration_status'].value_counts().reset_index()
        status_counts.columns = ['Status', 'Count']
        
        # Create a pie chart
        fig = px.pie(
            status_counts,
            values='Count',
            names='Status',
            color='Status',
            color_discrete_map={
                'Overdue': 'red',
                'Due Soon': 'orange',
                'OK': 'green'
            },
            title='Sensor Calibration Status'
        )
        
        fig.update_traces(textposition='inside', textinfo='percent+label')
        
        st.plotly_chart(fig, use_container_width=True)
        
        # Create a bar chart of days since last calibration
        maintenance_df = maintenance_df.sort_values('days_since_calibration', ascending=False)
        
        fig = px.bar(
            maintenance_df,
            x='location_name',
            y='days_since_calibration',
            color='calibration_status',
            color_discrete_map={
                'Overdue': 'red',
                'Due Soon': 'orange',
                'OK': 'green'
            },
            title='Days Since Last Calibration by Sensor',
            labels={
                'location_name': 'Sensor Location',
                'days_since_calibration': 'Days Since Last Calibration'
            }
        )
        
        # Add a reference line for the average maintenance interval
        avg_interval = maintenance_df['maintenance_interval_days'].mean()
        
        fig.add_shape(
            type="line",
            x0=-0.5,
            y0=avg_interval,
            x1=len(maintenance_df) - 0.5,
            y1=avg_interval,
            line=dict(color="black", width=2, dash="dash"),
        )
        
        fig.add_annotation(
            x=len(maintenance_df) - 1,
            y=avg_interval,
            text=f"Avg Interval: {avg_interval:.0f} days",
            showarrow=False,
            yshift=10
        )
        
        st.plotly_chart(fig, use_container_width=True)
    
    # Calibration Schedule tab
    with tabs[1]:
        st.subheader("Calibration Schedule")
        
        # Create a dataframe with calibration schedule
        schedule_df = sensor_info.copy()
        
        # Calculate next calibration date
        schedule_df['last_calibration'] = pd.to_datetime(schedule_df['last_calibration'])
        schedule_df['next_calibration'] = schedule_df['last_calibration'] + pd.to_timedelta(schedule_df['maintenance_interval_days'], unit='D')
        
        # Calculate days until next calibration
        schedule_df['days_until_calibration'] = (schedule_df['next_calibration'] - datetime.now()).dt.days
        
        # Sort by next calibration date
        schedule_df = schedule_df.sort_values('next_calibration')
        
        # Create a calendar view
        st.markdown("### Upcoming Calibrations")
        
        # Create a date range for the next 90 days
        today = datetime.now().date()
        date_range = [today + timedelta(days=i) for i in range(90)]
        
        # Create a dataframe with calibration events
        events = []
        
        for _, row in schedule_df.iterrows():
            next_cal_date = row['next_calibration'].date()
            
            if next_cal_date >= today and next_cal_date <= today + timedelta(days=90):
                events.append({
                    'date': next_cal_date,
                    'sensor_id': row['sensor_id'],
                    'location': row['location_name'],
                    'days_until': (next_cal_date - today).days
                })
        
        events_df = pd.DataFrame(events)
        
        if not events_df.empty:
            # Group events by date
            events_by_date = events_df.groupby('date')
            
            # Create a timeline
            fig = go.Figure()
            
            # Add events to the timeline
            for date, group in events_by_date:
                for _, event in group.iterrows():
                    fig.add_trace(go.Scatter(
                        x=[date],
                        y=[f"Sensor {event['sensor_id']}"],
                        mode='markers',
                        marker=dict(
                            symbol='square',
                            size=20,
                            color='red' if event['days_until'] <= 7 else 'orange' if event['days_until'] <= 14 else 'green'
                        ),
                        text=f"Sensor {event['sensor_id']}: {event['location']}",
                        hoverinfo='text'
                    ))
            
            # Update the layout
            fig.update_layout(
                title="Calibration Schedule (Next 90 Days)",
                xaxis_title="Date",
                yaxis_title="Sensor",
                height=400
            )
            
            st.plotly_chart(fig, use_container_width=True)
            
            # Create a table of upcoming calibrations
            st.markdown("### Upcoming Calibration Details")
            
            # Format the dataframe for display
            display_df = events_df.copy()
            display_df['date'] = display_df['date'].apply(lambda x: x.strftime('%Y-%m-%d'))
            display_df.columns = ['Date', 'Sensor ID', 'Location', 'Days Until Due']
            
            st.dataframe(display_df, use_container_width=True)
        else:
            st.info("No calibrations scheduled for the next 90 days.")
        
        # Create a calibration frequency chart
        st.markdown("### Calibration Frequency")
        
        fig = px.histogram(
            schedule_df,
            x='maintenance_interval_days',
            nbins=10,
            title="Distribution of Calibration Intervals",
            labels={
                'maintenance_interval_days': 'Calibration Interval (days)',
                'count': 'Number of Sensors'
            }
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
        # Create a form to schedule a new calibration
        st.markdown("### Schedule New Calibration")
        
        with st.form("calibration_form"):
            # Sensor selection
            sensor_id = st.selectbox(
                "Select Sensor",
                options=schedule_df['sensor_id'].tolist(),
                format_func=lambda x: f"Sensor {x}: {schedule_df[schedule_df['sensor_id'] == x]['location_name'].values[0]}"
            )
            
            # Date selection
            cal_date = st.date_input(
                "Calibration Date",
                value=datetime.now().date()
            )
            
            # Notes
            notes = st.text_area(
                "Notes",
                placeholder="Enter any notes about this calibration..."
            )
            
            # Submit button
            submitted = st.form_submit_button("Schedule Calibration")
            
            if submitted:
                st.success(f"Calibration scheduled for Sensor {sensor_id} on {cal_date}. (Note: This is a demo, no data is actually saved)")
    
    # Sensor Health tab
    with tabs[2]:
        st.subheader("Sensor Health")
        
        # Create a dataframe with sensor health information
        health_df = sensor_info.copy()
        
        # Add installation date
        health_df['installation_date'] = pd.to_datetime(health_df['installation_date'])
        
        # Calculate sensor age in days
        health_df['sensor_age_days'] = (datetime.now() - health_df['installation_date']).dt.days
        
        # Calculate sensor age in months
        health_df['sensor_age_months'] = health_df['sensor_age_days'] / 30
        
        # Calculate estimated remaining life (assuming 2-year lifespan)
        health_df['estimated_lifespan_days'] = 730  # 2 years in days
        health_df['remaining_life_days'] = health_df['estimated_lifespan_days'] - health_df['sensor_age_days']
        health_df['remaining_life_percent'] = (health_df['remaining_life_days'] / health_df['estimated_lifespan_days']) * 100
        
        # Determine health status
        health_df['health_status'] = health_df.apply(
            lambda x: "Critical" if x['remaining_life_percent'] < 10 else 
                     ("Warning" if x['remaining_life_percent'] < 25 else "Good"),
            axis=1
        )
        
        # Create a gauge chart for each sensor
        st.markdown("### Sensor Health Status")
        
        # Create a grid of gauge charts
        cols = st.columns(3)
        
        for i, (_, row) in enumerate(health_df.iterrows()):
            with cols[i % 3]:
                # Create the gauge chart
                fig = go.Figure(go.Indicator(
                    mode="gauge+number+delta",
                    value=row['remaining_life_percent'],
                    domain={'x': [0, 1], 'y': [0, 1]},
                    title={'text': f"Sensor {row['sensor_id']}: {row['location_name']}"},
                    delta={'reference': 100, 'decreasing': {'color': "red"}},
                    gauge={
                        'axis': {'range': [0, 100], 'tickwidth': 1, 'tickcolor': "darkblue"},
                        'bar': {'color': "darkblue"},
                        'bgcolor': "white",
                        'borderwidth': 2,
                        'bordercolor': "gray",
                        'steps': [
                            {'range': [0, 10], 'color': 'red'},
                            {'range': [10, 25], 'color': 'orange'},
                            {'range': [25, 100], 'color': 'green'}
                        ],
                        'threshold': {
                            'line': {'color': "red", 'width': 4},
                            'thickness': 0.75,
                            'value': row['remaining_life_percent']
                        }
                    }
                ))
                
                fig.update_layout(
                    height=250,
                    margin=dict(l=20, r=20, t=50, b=20)
                )
                
                st.plotly_chart(fig, use_container_width=True)
                
                # Add sensor details
                st.markdown(
                    f"""
                    <div style="text-align: center;">
                        <p><strong>Installed:</strong> {row['installation_date'].strftime('%Y-%m-%d')}</p>
                        <p><strong>Age:</strong> {row['sensor_age_days']} days ({row['sensor_age_months']:.1f} months)</p>
                        <p><strong>Remaining Life:</strong> {row['remaining_life_days']} days</p>
                    </div>
                    """,
                    unsafe_allow_html=True
                )
        
        # Create a summary of sensor health
        st.markdown("### Sensor Health Summary")
        
        # Count sensors by health status
        status_counts = health_df['health_status'].value_counts().reset_index()
        status_counts.columns = ['Status', 'Count']
        
        # Create a pie chart
        fig = px.pie(
            status_counts,
            values='Count',
            names='Status',
            color='Status',
            color_discrete_map={
                'Critical': 'red',
                'Warning': 'orange',
                'Good': 'green'
            },
            title='Sensor Health Status'
        )
        
        fig.update_traces(textposition='inside', textinfo='percent+label')
        
        st.plotly_chart(fig, use_container_width=True)
        
        # Create a bar chart of sensor age
        health_df = health_df.sort_values('sensor_age_days', ascending=False)
        
        fig = px.bar(
            health_df,
            x='location_name',
            y='sensor_age_days',
            color='health_status',
            color_discrete_map={
                'Critical': 'red',
                'Warning': 'orange',
                'Good': 'green'
            },
            title='Sensor Age by Location',
            labels={
                'location_name': 'Sensor Location',
                'sensor_age_days': 'Sensor Age (days)'
            }
        )
        
        # Add a reference line for the average sensor age
        avg_age = health_df['sensor_age_days'].mean()
        
        fig.add_shape(
            type="line",
            x0=-0.5,
            y0=avg_age,
            x1=len(health_df) - 0.5,
            y1=avg_age,
            line=dict(color="black", width=2, dash="dash"),
        )
        
        fig.add_annotation(
            x=len(health_df) - 1,
            y=avg_age,
            text=f"Avg Age: {avg_age:.0f} days",
            showarrow=False,
            yshift=10
        )
        
        st.plotly_chart(fig, use_container_width=True)
    
    # Maintenance History tab
    with tabs[3]:
        st.subheader("Maintenance History")
        
        # Since we don't have actual maintenance history data, we'll create some simulated data
        st.markdown("### Simulated Maintenance History")
        
        # Create a dataframe with simulated maintenance history
        history_data = []
        
        # Get the number of sensors
        num_sensors = len(sensor_info)
        
        # Generate random maintenance events for each sensor
        for _, row in sensor_info.iterrows():
            sensor_id = row['sensor_id']
            location = row['location_name']
            installation_date = pd.to_datetime(row['installation_date'])
            last_calibration = pd.to_datetime(row['last_calibration'])
            
            # Generate initial installation event
            history_data.append({
                'sensor_id': sensor_id,
                'location': location,
                'date': installation_date,
                'type': 'Installation',
                'description': f"Initial installation of Sensor {sensor_id} at {location}",
                'technician': f"Tech-{np.random.randint(1, 5)}"
            })
            
            # Generate calibration events
            current_date = installation_date + timedelta(days=np.random.randint(30, 90))
            
            while current_date < last_calibration:
                history_data.append({
                    'sensor_id': sensor_id,
                    'location': location,
                    'date': current_date,
                    'type': 'Calibration',
                    'description': f"Routine calibration of Sensor {sensor_id}",
                    'technician': f"Tech-{np.random.randint(1, 5)}"
                })
                
                # Add occasional repair events
                if np.random.random() < 0.2:  # 20% chance of a repair event
                    repair_date = current_date + timedelta(days=np.random.randint(1, 30))
                    
                    if repair_date < last_calibration:
                        history_data.append({
                            'sensor_id': sensor_id,
                            'location': location,
                            'date': repair_date,
                            'type': 'Repair',
                            'description': f"Repair of Sensor {sensor_id} due to {np.random.choice(['drift', 'connection issue', 'physical damage', 'power failure'])}",
                            'technician': f"Tech-{np.random.randint(1, 5)}"
                        })
                
                # Move to next calibration
                current_date += timedelta(days=np.random.randint(30, 90))
            
            # Add the most recent calibration
            history_data.append({
                'sensor_id': sensor_id,
                'location': location,
                'date': last_calibration,
                'type': 'Calibration',
                'description': f"Routine calibration of Sensor {sensor_id}",
                'technician': f"Tech-{np.random.randint(1, 5)}"
            })
        
        # Create a dataframe from the history data
        history_df = pd.DataFrame(history_data)
        
        # Sort by date (most recent first)
        history_df = history_df.sort_values('date', ascending=False)
        
        # Create a filter for sensor and event type
        col1, col2 = st.columns(2)
        
        with col1:
            selected_sensor = st.selectbox(
                "Filter by Sensor",
                options=["All Sensors"] + [f"Sensor {i}" for i in range(1, num_sensors + 1)]
            )
        
        with col2:
            selected_type = st.selectbox(
                "Filter by Event Type",
                options=["All Types"] + history_df['type'].unique().tolist()
            )
        
        # Apply filters
        filtered_df = history_df.copy()
        
        if selected_sensor != "All Sensors":
            sensor_id = int(selected_sensor.split()[1])
            filtered_df = filtered_df[filtered_df['sensor_id'] == sensor_id]
        
        if selected_type != "All Types":
            filtered_df = filtered_df[filtered_df['type'] == selected_type]
        
        # Format the dataframe for display
        display_df = filtered_df.copy()
        display_df['date'] = display_df['date'].dt.strftime('%Y-%m-%d')
        display_df = display_df[['date', 'sensor_id', 'location', 'type', 'description', 'technician']]
        display_df.columns = ['Date', 'Sensor ID', 'Location', 'Event Type', 'Description', 'Technician']
        
        # Display the maintenance history
        st.dataframe(display_df, use_container_width=True)
        
        # Create a timeline of maintenance events
        st.markdown("### Maintenance Timeline")
        
        # Create a dataframe for the timeline
        timeline_df = history_df.copy()
        
        # Apply filters
        if selected_sensor != "All Sensors":
            sensor_id = int(selected_sensor.split()[1])
            timeline_df = timeline_df[timeline_df['sensor_id'] == sensor_id]
        
        if selected_type != "All Types":
            timeline_df = timeline_df[timeline_df['type'] == selected_type]
        
        # Create the timeline
        fig = px.timeline(
            timeline_df,
            x_start='date',
            x_end='date',
            y='location',
            color='type',
            hover_name='description',
            color_discrete_map={
                'Installation': 'blue',
                'Calibration': 'green',
                'Repair': 'red'
            },
            title="Maintenance Timeline"
        )
        
        # Update the layout
        fig.update_layout(
            xaxis_title="Date",
            yaxis_title="Sensor Location",
            height=400
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
        # Create a summary of maintenance events
        st.markdown("### Maintenance Summary")
        
        # Count events by type
        event_counts = history_df['type'].value_counts().reset_index()
        event_counts.columns = ['Event Type', 'Count']
        
        # Create a pie chart
        fig = px.pie(
            event_counts,
            values='Count',
            names='Event Type',
            color='Event Type',
            color_discrete_map={
                'Installation': 'blue',
                'Calibration': 'green',
                'Repair': 'red'
            },
            title='Maintenance Events by Type'
        )
        
        fig.update_traces(textposition='inside', textinfo='percent+label')
        
        st.plotly_chart(fig, use_container_width=True)
        
        # Create a bar chart of events by sensor
        sensor_events = history_df.groupby(['sensor_id', 'location', 'type']).size().reset_index(name='count')
        
        fig = px.bar(
            sensor_events,
            x='location',
            y='count',
            color='type',
            color_discrete_map={
                'Installation': 'blue',
                'Calibration': 'green',
                'Repair': 'red'
            },
            title='Maintenance Events by Sensor and Type',
            labels={
                'location': 'Sensor Location',
                'count': 'Number of Events',
                'type': 'Event Type'
            }
        )
        
        st.plotly_chart(fig, use_container_width=True)
