import numpy as np
import pandas as pd
import os
from datetime import datetime, timedelta
import random

def generate_ph_data(days=30, frequency_minutes=15, num_sensors=3, seed=42):
    """
    Generate realistic pH sensor data for multiple sensors.
    
    Parameters:
    - days: Number of days of data to generate
    - frequency_minutes: Data recording frequency in minutes
    - num_sensors: Number of pH sensors to simulate
    - seed: Random seed for reproducibility
    
    Returns:
    - DataFrame with timestamp and pH values for each sensor
    """
    np.random.seed(seed)
    
    # Create timestamp range
    end_date = datetime.now()
    start_date = end_date - timedelta(days=days)
    
    # Generate timestamps at specified frequency
    timestamps = []
    current = start_date
    while current <= end_date:
        timestamps.append(current)
        current += timedelta(minutes=frequency_minutes)
    
    data = {'timestamp': timestamps}
    
    # Generate pH data for each sensor with realistic patterns
    for i in range(1, num_sensors + 1):
        # Base pH value (slightly different for each sensor)
        base_ph = 7.0 + np.random.uniform(-0.5, 0.5)
        
        # Generate pH values with daily patterns, random fluctuations, and occasional anomalies
        ph_values = []
        
        for timestamp in timestamps:
            # Daily pattern (pH might vary slightly throughout the day)
            hour_effect = 0.2 * np.sin(2 * np.pi * timestamp.hour / 24)
            
            # Weekly pattern (e.g., different operations on weekends)
            day_of_week_effect = 0.1 * np.sin(2 * np.pi * timestamp.weekday() / 7)
            
            # Random noise
            noise = np.random.normal(0, 0.1)
            
            # Occasional anomalies (1% chance)
            anomaly = 0
            if np.random.random() < 0.01:
                anomaly = np.random.uniform(-1.0, 1.0)
            
            # Gradual drift over time (pH sensors often drift)
            days_passed = (timestamp - start_date).days
            drift = 0.01 * days_passed / 30  # Small drift over a month
            
            # Calculate pH value
            ph = base_ph + hour_effect + day_of_week_effect + noise + anomaly + drift
            
            # Ensure pH stays within realistic bounds (0-14)
            ph = max(0, min(14, ph))
            
            ph_values.append(round(ph, 2))
        
        data[f'sensor_{i}_ph'] = ph_values
    
    return pd.DataFrame(data)

def generate_temperature_data(ph_df, correlation=0.3, seed=42):
    """
    Generate temperature data with some correlation to pH values.
    
    Parameters:
    - ph_df: DataFrame containing pH data
    - correlation: Correlation coefficient between pH and temperature
    - seed: Random seed for reproducibility
    
    Returns:
    - DataFrame with temperature data for each sensor
    """
    np.random.seed(seed)
    
    temp_df = ph_df.copy()
    
    # Get the number of sensors from the pH dataframe
    num_sensors = sum(1 for col in ph_df.columns if col.endswith('_ph'))
    
    for i in range(1, num_sensors + 1):
        ph_col = f'sensor_{i}_ph'
        
        # Base temperature (different for each sensor)
        base_temp = 25.0 + np.random.uniform(-3, 3)
        
        # Generate temperature with daily patterns and correlation to pH
        temp_values = []
        
        for idx, row in ph_df.iterrows():
            timestamp = row['timestamp']
            ph = row[ph_col]
            
            # Daily temperature pattern (higher during day, lower at night)
            hour_effect = 2.0 * np.sin(2 * np.pi * (timestamp.hour - 12) / 24)
            
            # Seasonal effect (if data spans multiple months)
            month_effect = 5.0 * np.sin(2 * np.pi * (timestamp.month - 6) / 12)
            
            # Correlation with pH (higher pH might correlate with higher temperature)
            ph_effect = correlation * (ph - 7.0) * 3
            
            # Random noise
            noise = np.random.normal(0, 0.5)
            
            # Calculate temperature
            temp = base_temp + hour_effect + month_effect + ph_effect + noise
            
            temp_values.append(round(temp, 1))
        
        temp_df[f'sensor_{i}_temp'] = temp_values
    
    return temp_df

def generate_conductivity_data(ph_df, temp_df, seed=42):
    """
    Generate conductivity data with correlation to pH and temperature.
    
    Parameters:
    - ph_df: DataFrame containing pH data
    - temp_df: DataFrame containing temperature data
    - seed: Random seed for reproducibility
    
    Returns:
    - DataFrame with conductivity data for each sensor
    """
    np.random.seed(seed)
    
    cond_df = ph_df.copy()
    
    # Get the number of sensors from the pH dataframe
    num_sensors = sum(1 for col in ph_df.columns if col.endswith('_ph'))
    
    for i in range(1, num_sensors + 1):
        ph_col = f'sensor_{i}_ph'
        temp_col = f'sensor_{i}_temp'
        
        # Base conductivity (different for each sensor, in μS/cm)
        base_cond = 500.0 + np.random.uniform(-100, 100)
        
        # Generate conductivity with correlation to pH and temperature
        cond_values = []
        
        for idx, row in ph_df.iterrows():
            ph = row[ph_col]
            temp = temp_df.loc[idx, temp_col]
            
            # pH effect (conductivity often increases as pH deviates from neutral)
            ph_effect = 50.0 * abs(ph - 7.0)
            
            # Temperature effect (conductivity increases with temperature)
            temp_effect = 10.0 * (temp - 25.0)
            
            # Random noise
            noise = np.random.normal(0, 20.0)
            
            # Calculate conductivity
            cond = base_cond + ph_effect + temp_effect + noise
            
            # Ensure conductivity is positive
            cond = max(10, cond)
            
            cond_values.append(round(cond, 1))
        
        cond_df[f'sensor_{i}_conductivity'] = cond_values
    
    return cond_df

def generate_dissolved_oxygen_data(ph_df, temp_df, seed=42):
    """
    Generate dissolved oxygen (DO) data with correlation to pH and temperature.
    
    Parameters:
    - ph_df: DataFrame containing pH data
    - temp_df: DataFrame containing temperature data
    - seed: Random seed for reproducibility
    
    Returns:
    - DataFrame with DO data for each sensor
    """
    np.random.seed(seed)
    
    do_df = ph_df.copy()
    
    # Get the number of sensors from the pH dataframe
    num_sensors = sum(1 for col in ph_df.columns if col.endswith('_ph'))
    
    for i in range(1, num_sensors + 1):
        ph_col = f'sensor_{i}_ph'
        temp_col = f'sensor_{i}_temp'
        
        # Generate DO with correlation to pH and temperature
        do_values = []
        
        for idx, row in ph_df.iterrows():
            timestamp = row['timestamp']
            ph = row[ph_col]
            temp = temp_df.loc[idx, temp_col]
            
            # Base DO (mg/L) - temperature dependent (DO decreases as temperature increases)
            # Approximate relationship based on water at atmospheric pressure
            base_do = 14.6 * 0.65 ** (0.04 * (temp - 20))
            
            # pH effect (slight effect)
            ph_effect = 0.2 * (ph - 7.0)
            
            # Daily pattern (photosynthesis during daylight hours increases DO)
            hour_effect = 0.5 * np.sin(2 * np.pi * (timestamp.hour - 14) / 24)
            
            # Random noise
            noise = np.random.normal(0, 0.3)
            
            # Calculate DO
            do = base_do + ph_effect + hour_effect + noise
            
            # Ensure DO is positive and within realistic bounds
            do = max(0.1, min(20, do))
            
            do_values.append(round(do, 2))
        
        do_df[f'sensor_{i}_dissolved_oxygen'] = do_values
    
    return do_df

def generate_turbidity_data(ph_df, seed=42):
    """
    Generate turbidity data with some correlation to pH.
    
    Parameters:
    - ph_df: DataFrame containing pH data
    - seed: Random seed for reproducibility
    
    Returns:
    - DataFrame with turbidity data for each sensor
    """
    np.random.seed(seed)
    
    turb_df = ph_df.copy()
    
    # Get the number of sensors from the pH dataframe
    num_sensors = sum(1 for col in ph_df.columns if col.endswith('_ph'))
    
    for i in range(1, num_sensors + 1):
        ph_col = f'sensor_{i}_ph'
        
        # Base turbidity (NTU)
        base_turb = 5.0 + np.random.uniform(-2, 2)
        
        # Generate turbidity with some correlation to pH
        turb_values = []
        
        for idx, row in ph_df.iterrows():
            timestamp = row['timestamp']
            ph = row[ph_col]
            
            # pH effect (higher pH might correlate with lower turbidity in some cases)
            ph_effect = -0.5 * (ph - 7.0)
            
            # Random events (e.g., rain, disturbance) causing spikes in turbidity
            event = 0
            if np.random.random() < 0.05:  # 5% chance of an event
                event = np.random.exponential(10)
            
            # Random noise
            noise = np.random.normal(0, 1.0)
            
            # Calculate turbidity
            turb = base_turb + ph_effect + event + noise
            
            # Ensure turbidity is positive
            turb = max(0.1, turb)
            
            turb_values.append(round(turb, 2))
        
        turb_df[f'sensor_{i}_turbidity'] = turb_values
    
    return turb_df

def generate_humidity_data(ph_df, temp_df, seed=42):
    """
    Generate soil humidity data with correlation to pH and temperature.
    
    Parameters:
    - ph_df: DataFrame containing pH data
    - temp_df: DataFrame containing temperature data
    - seed: Random seed for reproducibility
    
    Returns:
    - DataFrame with humidity data for each sensor
    """
    np.random.seed(seed)
    
    humidity_df = ph_df.copy()
    
    # Get the number of sensors from the pH dataframe
    num_sensors = sum(1 for col in ph_df.columns if col.endswith('_ph'))
    
    for i in range(1, num_sensors + 1):
        ph_col = f'sensor_{i}_ph'
        temp_col = f'sensor_{i}_temp'
        
        # Base humidity (different for each sensor, in %)
        base_humidity = 50.0 + np.random.uniform(-10, 10)
        
        # Generate humidity with correlation to pH and temperature
        humidity_values = []
        
        for idx, row in ph_df.iterrows():
            timestamp = row['timestamp']
            ph = row[ph_col]
            temp = temp_df.loc[idx, temp_col]
            
            # Daily pattern (humidity might be higher at night and early morning)
            hour_effect = -5.0 * np.sin(2 * np.pi * (timestamp.hour - 6) / 24)
            
            # Temperature effect (humidity decreases as temperature increases)
            temp_effect = -0.5 * (temp - 25.0)
            
            # pH effect (slight effect)
            ph_effect = -2.0 * (ph - 7.0)
            
            # Random noise
            noise = np.random.normal(0, 3.0)
            
            # Calculate humidity
            humidity = base_humidity + hour_effect + temp_effect + ph_effect + noise
            
            # Ensure humidity is within realistic bounds (0-100%)
            humidity = max(0, min(100, humidity))
            
            humidity_values.append(round(humidity, 1))
        
        humidity_df[f'sensor_{i}_humidity'] = humidity_values
    
    return humidity_df

def generate_nitrogen_data(ph_df, humidity_df, seed=42):
    """
    Generate soil nitrogen (N) data with correlation to pH and humidity.
    
    Parameters:
    - ph_df: DataFrame containing pH data
    - humidity_df: DataFrame containing humidity data
    - seed: Random seed for reproducibility
    
    Returns:
    - DataFrame with nitrogen data for each sensor
    """
    np.random.seed(seed)
    
    nitrogen_df = ph_df.copy()
    
    # Get the number of sensors from the pH dataframe
    num_sensors = sum(1 for col in ph_df.columns if col.endswith('_ph'))
    
    for i in range(1, num_sensors + 1):
        ph_col = f'sensor_{i}_ph'
        humidity_col = f'sensor_{i}_humidity'
        
        # Base nitrogen level (different for each sensor, in mg/kg)
        base_nitrogen = 40.0 + np.random.uniform(-10, 10)
        
        # Generate nitrogen with correlation to pH and humidity
        nitrogen_values = []
        
        for idx, row in ph_df.iterrows():
            timestamp = row['timestamp']
            ph = row[ph_col]
            humidity = humidity_df.loc[idx, humidity_col]
            
            # pH effect (nitrogen availability is affected by pH)
            # Optimal pH for nitrogen availability is around 6.0-7.0
            ph_effect = -5.0 * abs(ph - 6.5)
            
            # Humidity effect (higher humidity can increase nitrogen availability)
            humidity_effect = 0.2 * (humidity - 50)
            
            # Seasonal effect
            day_of_year = timestamp.timetuple().tm_yday
            seasonal_effect = 10.0 * np.sin(2 * np.pi * (day_of_year - 120) / 365)
            
            # Random noise
            noise = np.random.normal(0, 3.0)
            
            # Calculate nitrogen
            nitrogen = base_nitrogen + ph_effect + humidity_effect + seasonal_effect + noise
            
            # Ensure nitrogen is positive
            nitrogen = max(0, nitrogen)
            
            nitrogen_values.append(round(nitrogen, 1))
        
        nitrogen_df[f'sensor_{i}_nitrogen'] = nitrogen_values
    
    return nitrogen_df

def generate_phosphorus_data(ph_df, humidity_df, seed=42):
    """
    Generate soil phosphorus (P) data with correlation to pH and humidity.
    
    Parameters:
    - ph_df: DataFrame containing pH data
    - humidity_df: DataFrame containing humidity data
    - seed: Random seed for reproducibility
    
    Returns:
    - DataFrame with phosphorus data for each sensor
    """
    np.random.seed(seed)
    
    phosphorus_df = ph_df.copy()
    
    # Get the number of sensors from the pH dataframe
    num_sensors = sum(1 for col in ph_df.columns if col.endswith('_ph'))
    
    for i in range(1, num_sensors + 1):
        ph_col = f'sensor_{i}_ph'
        humidity_col = f'sensor_{i}_humidity'
        
        # Base phosphorus level (different for each sensor, in mg/kg)
        base_phosphorus = 15.0 + np.random.uniform(-5, 5)
        
        # Generate phosphorus with correlation to pH and humidity
        phosphorus_values = []
        
        for idx, row in ph_df.iterrows():
            timestamp = row['timestamp']
            ph = row[ph_col]
            humidity = humidity_df.loc[idx, humidity_col]
            
            # pH effect (phosphorus availability is highly affected by pH)
            # Optimal pH for phosphorus availability is around 6.0-7.0
            # Phosphorus becomes less available at high pH (> 7.5) and low pH (< 5.5)
            if ph < 5.5:
                ph_effect = -5.0 * (5.5 - ph)
            elif ph > 7.5:
                ph_effect = -3.0 * (ph - 7.5)
            else:
                ph_effect = 2.0 * (1 - abs(ph - 6.5) / 1.0)
            
            # Humidity effect (moderate effect)
            humidity_effect = 0.1 * (humidity - 50)
            
            # Seasonal effect
            day_of_year = timestamp.timetuple().tm_yday
            seasonal_effect = 3.0 * np.sin(2 * np.pi * (day_of_year - 90) / 365)
            
            # Random noise
            noise = np.random.normal(0, 1.5)
            
            # Calculate phosphorus
            phosphorus = base_phosphorus + ph_effect + humidity_effect + seasonal_effect + noise
            
            # Ensure phosphorus is positive
            phosphorus = max(0, phosphorus)
            
            phosphorus_values.append(round(phosphorus, 1))
        
        phosphorus_df[f'sensor_{i}_phosphorus'] = phosphorus_values
    
    return phosphorus_df

def generate_potassium_data(ph_df, humidity_df, seed=42):
    """
    Generate soil potassium (K) data with correlation to pH and humidity.
    
    Parameters:
    - ph_df: DataFrame containing pH data
    - humidity_df: DataFrame containing humidity data
    - seed: Random seed for reproducibility
    
    Returns:
    - DataFrame with potassium data for each sensor
    """
    np.random.seed(seed)
    
    potassium_df = ph_df.copy()
    
    # Get the number of sensors from the pH dataframe
    num_sensors = sum(1 for col in ph_df.columns if col.endswith('_ph'))
    
    for i in range(1, num_sensors + 1):
        ph_col = f'sensor_{i}_ph'
        humidity_col = f'sensor_{i}_humidity'
        
        # Base potassium level (different for each sensor, in mg/kg)
        base_potassium = 150.0 + np.random.uniform(-30, 30)
        
        # Generate potassium with correlation to pH and humidity
        potassium_values = []
        
        for idx, row in ph_df.iterrows():
            timestamp = row['timestamp']
            ph = row[ph_col]
            humidity = humidity_df.loc[idx, humidity_col]
            
            # pH effect (potassium availability is moderately affected by pH)
            # Potassium is generally available across a wide pH range
            ph_effect = -10.0 * abs(ph - 6.5) / 6.5
            
            # Humidity effect (higher humidity can increase potassium availability)
            humidity_effect = 0.3 * (humidity - 50)
            
            # Seasonal effect
            day_of_year = timestamp.timetuple().tm_yday
            seasonal_effect = 15.0 * np.sin(2 * np.pi * (day_of_year - 150) / 365)
            
            # Random noise
            noise = np.random.normal(0, 10.0)
            
            # Calculate potassium
            potassium = base_potassium + ph_effect + humidity_effect + seasonal_effect + noise
            
            # Ensure potassium is positive
            potassium = max(0, potassium)
            
            potassium_values.append(round(potassium, 1))
        
        potassium_df[f'sensor_{i}_potassium'] = potassium_values
    
    return potassium_df

def generate_all_sensor_data(days=30, frequency_minutes=15, num_sensors=3, seed=42):
    """
    Generate a complete dataset with all sensor parameters.
    
    Parameters:
    - days: Number of days of data to generate
    - frequency_minutes: Data recording frequency in minutes
    - num_sensors: Number of sensors to simulate
    - seed: Random seed for reproducibility
    
    Returns:
    - DataFrame with all sensor data
    """
    # Generate base pH data
    ph_df = generate_ph_data(days, frequency_minutes, num_sensors, seed)
    
    # Generate temperature data
    temp_df = generate_temperature_data(ph_df, correlation=0.3, seed=seed)
    
    # Generate humidity data
    humidity_df = generate_humidity_data(ph_df, temp_df, seed=seed)
    
    # Generate conductivity data
    cond_df = generate_conductivity_data(ph_df, temp_df, seed=seed)
    
    # Generate nitrogen data
    nitrogen_df = generate_nitrogen_data(ph_df, humidity_df, seed=seed)
    
    # Generate phosphorus data
    phosphorus_df = generate_phosphorus_data(ph_df, humidity_df, seed=seed)
    
    # Generate potassium data
    potassium_df = generate_potassium_data(ph_df, humidity_df, seed=seed)
    
    # Generate dissolved oxygen data
    do_df = generate_dissolved_oxygen_data(ph_df, temp_df, seed=seed)
    
    # Generate turbidity data
    turb_df = generate_turbidity_data(ph_df, seed=seed)
    
    # Combine all data
    all_data = ph_df.copy()
    
    for i in range(1, num_sensors + 1):
        # Add parameters in order of importance as specified by the user
        all_data[f'sensor_{i}_ph'] = ph_df[f'sensor_{i}_ph']  # Most important
        all_data[f'sensor_{i}_humidity'] = humidity_df[f'sensor_{i}_humidity']  # Second
        all_data[f'sensor_{i}_temp'] = temp_df[f'sensor_{i}_temp']  # Third
        all_data[f'sensor_{i}_conductivity'] = cond_df[f'sensor_{i}_conductivity']
        all_data[f'sensor_{i}_nitrogen'] = nitrogen_df[f'sensor_{i}_nitrogen']
        all_data[f'sensor_{i}_phosphorus'] = phosphorus_df[f'sensor_{i}_phosphorus']
        all_data[f'sensor_{i}_potassium'] = potassium_df[f'sensor_{i}_potassium']
        all_data[f'sensor_{i}_dissolved_oxygen'] = do_df[f'sensor_{i}_dissolved_oxygen']
        all_data[f'sensor_{i}_turbidity'] = turb_df[f'sensor_{i}_turbidity']
    
    return all_data

def add_location_info(df, num_sensors=3):
    """
    Add location information for each sensor in Thailand.
    
    Parameters:
    - df: DataFrame with sensor data
    - num_sensors: Number of sensors
    
    Returns:
    - DataFrame with location information
    """
    # Define possible locations for soil sensors in Thailand
    locations = [
        {"name": "Chiang Mai Rice Field", "type": "Clay Soil", "coordinates": "18.7883° N, 98.9853° E"},
        {"name": "Khon Kaen Cassava Farm", "type": "Sandy Loam", "coordinates": "16.4419° N, 102.8360° E"},
        {"name": "Rayong Fruit Orchard", "type": "Loamy Soil", "coordinates": "12.6748° N, 101.2815° E"},
        {"name": "Chiang Rai Tea Plantation", "type": "Silt Loam", "coordinates": "19.9071° N, 99.8306° E"},
        {"name": "Nakhon Ratchasima Corn Field", "type": "Clay Loam", "coordinates": "14.9798° N, 102.0978° E"},
        {"name": "Sukhothai Rice Paddy", "type": "Silty Clay", "coordinates": "17.0076° N, 99.8268° E"},
        {"name": "Kanchanaburi Sugarcane Field", "type": "Sandy Clay", "coordinates": "14.0227° N, 99.5328° E"}
    ]
    
    # Create a new dataframe with sensor metadata
    sensor_info = []
    
    for i in range(1, num_sensors + 1):
        # Randomly select a location (without replacement if possible)
        loc_idx = (i - 1) % len(locations)
        location = locations[loc_idx]
        
        sensor_info.append({
            "sensor_id": i,
            "location_name": location["name"],
            "water_type": location["type"],
            "coordinates": location["coordinates"],
            "installation_date": (datetime.now() - timedelta(days=random.randint(30, 365))).strftime("%Y-%m-%d"),
            "maintenance_interval_days": random.choice([30, 60, 90]),
            "last_calibration": (datetime.now() - timedelta(days=random.randint(1, 30))).strftime("%Y-%m-%d")
        })
    
    return pd.DataFrame(sensor_info)

def save_sensor_data(days=30, frequency_minutes=15, num_sensors=3, seed=42):
    """
    Generate and save all sensor data to CSV files.
    
    Parameters:
    - days: Number of days of data to generate
    - frequency_minutes: Data recording frequency in minutes
    - num_sensors: Number of sensors to simulate
    - seed: Random seed for reproducibility
    
    Returns:
    - Dictionary with paths to saved files
    """
    # Create data directory if it doesn't exist
    data_dir = os.path.join(os.path.dirname(__file__), 'data')
    os.makedirs(data_dir, exist_ok=True)
    
    # Generate all sensor data
    all_data = generate_all_sensor_data(days, frequency_minutes, num_sensors, seed)
    
    # Generate sensor location information
    sensor_info = add_location_info(all_data, num_sensors)
    
    # Save combined data
    combined_path = os.path.join(data_dir, 'combined_sensor_data.csv')
    all_data.to_csv(combined_path, index=False)
    
    # Save sensor information
    sensor_info_path = os.path.join(data_dir, 'sensor_info.csv')
    sensor_info.to_csv(sensor_info_path, index=False)
    
    # Save individual sensor data
    individual_paths = {}
    for i in range(1, num_sensors + 1):
        # Extract data for this sensor
        sensor_cols = ['timestamp'] + [col for col in all_data.columns if col.startswith(f'sensor_{i}_')]
        sensor_data = all_data[sensor_cols]
        
        # Rename columns to remove sensor prefix
        new_cols = ['timestamp'] + [col.replace(f'sensor_{i}_', '') for col in sensor_cols if col != 'timestamp']
        sensor_data.columns = new_cols
        
        # Save to CSV
        sensor_path = os.path.join(data_dir, f'sensor_{i}_data.csv')
        sensor_data.to_csv(sensor_path, index=False)
        individual_paths[f'sensor_{i}'] = sensor_path
    
    # Create a daily summary
    daily_summary = all_data.copy()
    daily_summary['date'] = daily_summary['timestamp'].dt.date
    
    # Group by date and calculate statistics
    daily_stats = []
    
    for date, group in daily_summary.groupby('date'):
        date_stats = {'date': date}
        
        for i in range(1, num_sensors + 1):
            # Calculate statistics for each parameter
            for param in ['ph', 'humidity', 'temp', 'conductivity', 'nitrogen', 'phosphorus', 'potassium', 'dissolved_oxygen', 'turbidity']:
                col = f'sensor_{i}_{param}'
                if col in group.columns:
                    date_stats[f'sensor_{i}_{param}_min'] = group[col].min()
                    date_stats[f'sensor_{i}_{param}_max'] = group[col].max()
                    date_stats[f'sensor_{i}_{param}_avg'] = group[col].mean()
        
        daily_stats.append(date_stats)
    
    daily_summary_df = pd.DataFrame(daily_stats)
    daily_summary_path = os.path.join(data_dir, 'daily_summary.csv')
    daily_summary_df.to_csv(daily_summary_path, index=False)
    
    # Return paths to all saved files
    return {
        'combined_data': combined_path,
        'sensor_info': sensor_info_path,
        'daily_summary': daily_summary_path,
        'individual_sensors': individual_paths
    }

if __name__ == "__main__":
    # Generate and save sensor data for 30 days with readings every 15 minutes
    file_paths = save_sensor_data(days=30, frequency_minutes=15, num_sensors=5, seed=42)
    print("Sensor data generated and saved to:")
    for key, path in file_paths.items():
        if isinstance(path, dict):
            for sub_key, sub_path in path.items():
                print(f"  - {sub_key}: {sub_path}")
        else:
            print(f"  - {key}: {path}")
