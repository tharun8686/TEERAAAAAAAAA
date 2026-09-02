import pandas as pd
import numpy as np
import os

def calculate_heat_index(T_C, RH):
    """
    Calculate Heat Index using the Rothfusz regression.
    T_C is temperature in Celsius, RH is relative humidity in %.
    Formula expects Fahrenheit, so we convert back and forth.
    """
    T = (T_C * 9/5) + 32
    
    # Simple formula for lower temps
    HI = 0.5 * (T + 61.0 + ((T - 68.0) * 1.2) + (RH * 0.094))
    
    # If HI >= 80 F, use the full Rothfusz regression
    mask = HI >= 80
    
    # Create arrays to handle vectorized operations
    HI_full = np.zeros_like(T)
    
    c1, c2, c3 = -42.379, 2.04901523, 10.14333127
    c4, c5, c6 = -0.22475541, -6.83783e-3, -5.481717e-2
    c7, c8, c9 = 1.22874e-3, 8.5282e-4, -1.99e-6
    
    HI_full = (c1 + (c2 * T) + (c3 * RH) + (c4 * T * RH) + 
               (c5 * T**2) + (c6 * RH**2) + (c7 * T**2 * RH) + 
               (c8 * T * RH**2) + (c9 * T**2 * RH**2))
    
    # Adjustments
    adj1 = ((13 - RH) / 4) * np.sqrt((17 - np.abs(T - 95.)) / 17)
    HI_full = np.where((RH < 13) & (T >= 80) & (T <= 112), HI_full - adj1, HI_full)
    
    adj2 = ((RH - 85) / 10) * ((87 - T) / 5)
    HI_full = np.where((RH > 85) & (T >= 80) & (T <= 87), HI_full + adj2, HI_full)
    
    HI_final = np.where(mask, HI_full, HI)
    
    # Convert back to Celsius
    HI_C = (HI_final - 32) * 5/9
    return HI_C

def build_features(input_path, output_path):
    print("Loading master timeseries...")
    df = pd.read_csv(input_path, parse_dates=['timestamp'])
    df = df.sort_values('timestamp').set_index('timestamp')
    
    print("Engineering rates of change...")
    df['temperature_rate'] = df['temperature_c'].diff()
    df['humidity_rate'] = df['humidity'].diff()
    df['solar_radiation_rate'] = df['solar_radiation'].diff()
    df['rainfall_rate'] = df['rainfall_mm'].diff()
    # Assuming pressure isn't available in these datasets based on audit, skipping pressure_rate
    
    print("Engineering rolling statistics (24h)...")
    df['rolling_mean_temperature'] = df['temperature_c'].rolling(window=24, min_periods=12).mean()
    df['rolling_mean_humidity'] = df['humidity'].rolling(window=24, min_periods=12).mean()
    df['rolling_mean_solar_radiation'] = df['solar_radiation'].rolling(window=24, min_periods=12).mean()
    
    df['rolling_std_temperature'] = df['temperature_c'].rolling(window=24, min_periods=12).std()
    df['rolling_std_humidity'] = df['humidity'].rolling(window=24, min_periods=12).std()
    df['rolling_std_solar_radiation'] = df['solar_radiation'].rolling(window=24, min_periods=12).std()
    
    print("Engineering Heat Index and Apparent Temperature...")
    df['heat_index'] = calculate_heat_index(df['temperature_c'].values, df['humidity'].values)
    
    # Simple apparent temperature incorporating wind speed (if available)
    # AT = Ta + 0.33×e − 0.70×ws − 4.00, where e = water vapour pressure
    # e = (rh / 100) * 6.105 * exp(17.27 * Ta / (237.7 + Ta))
    ws_ms = df.get('wind_speed_kmh', 0) * (1000 / 3600)  # km/h to m/s
    e = (df['humidity'] / 100) * 6.105 * np.exp(17.27 * df['temperature_c'] / (237.7 + df['temperature_c']))
    df['apparent_temperature'] = df['temperature_c'] + 0.33 * e - 0.70 * ws_ms - 4.00
    
    print("Engineering Heatwave Persistence & Stress metrics...")
    # cumulative_hot_hours (temps > 35C in last 72h)
    is_hot = (df['temperature_c'] > 35).astype(int)
    df['cumulative_hot_hours'] = is_hot.rolling(window=72, min_periods=1).sum()
    
    # Nighttime cooling deficit (min temp between 10PM and 6AM was > 28C)
    # We create a daily min temp for nighttime hours, then forward fill to the day
    night_mask = (df.index.hour >= 22) | (df.index.hour <= 6)
    night_temps = df.loc[night_mask, 'temperature_c']
    night_mins = night_temps.resample('D').min()
    night_mins_reindexed = night_mins.reindex(df.index.normalize(), method='ffill')
    
    # Fill any remaining NaNs with a safe baseline (e.g., 25C)
    night_mins_reindexed = night_mins_reindexed.fillna(25)
    
    df['nighttime_cooling_deficit'] = np.maximum(0, night_mins_reindexed.values - 28)
    
    # Daytime heat load (sum of temp * solar rad in daylight)
    day_mask = (df.index.hour >= 8) & (df.index.hour <= 18)
    day_heat_load = df.loc[day_mask, 'temperature_c'] * df.loc[day_mask, 'solar_radiation']
    # Rolling 12h sum to capture the load
    df['daytime_heat_load'] = day_heat_load.reindex(df.index).rolling(window=12, min_periods=1).sum().fillna(0)
    
    # Heat stress score: HI + persistence + cooling deficit
    df['heat_stress_score'] = (df['heat_index'] - 30).clip(lower=0) * 1.5 + (df['cumulative_hot_hours'] * 0.5) + (df['nighttime_cooling_deficit'] * 2.0)
    
    # heatwave_persistence_score
    is_heatwave_condition = (df['heat_index'] > 40).astype(int)
    df['heatwave_persistence_score'] = is_heatwave_condition.rolling(window=48, min_periods=1).sum()
    
    print("Dropping initial NaN rows caused by rolling windows...")
    df.dropna(subset=['rolling_mean_temperature', 'rolling_std_temperature'], inplace=True)
    
    # Re-fill NaNs in rate columns with 0
    df.fillna(0, inplace=True)
    
    print("Saving features...")
    df.to_csv(output_path)
    print(f"Features saved to {output_path}. Shape: {df.shape}")

if __name__ == "__main__":
    intermediate_dir = r"C:\Users\TEJESHWAR\OneDrive\Desktop\Terra Edge\Extreme Heat\data\intermediate"
    in_path = os.path.join(intermediate_dir, "heat_master_timeseries.csv")
    out_path = os.path.join(intermediate_dir, "heat_features.csv")
    
    if os.path.exists(in_path):
        build_features(in_path, out_path)
    else:
        print(f"Error: {in_path} not found. Run build_heat_timeseries.py first.")
