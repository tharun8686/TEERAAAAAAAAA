import pandas as pd
import os

def load_and_standardize(file_path, value_col_name, new_col_name):
    """Loads a dataset, standardizes time and columns."""
    df = pd.read_csv(file_path)
    
    time_col = None
    target_val_col = None
    for col in df.columns:
        if "Time" in col or "Date" in col:
            time_col = col
        if value_col_name in col:
            target_val_col = col
            
    if time_col is None:
        raise ValueError(f"Could not find time column in {file_path}")
    if target_val_col is None:
        raise ValueError(f"Could not find value column matching {value_col_name} in {file_path}")
        
    df['timestamp'] = pd.to_datetime(df[time_col], format='mixed', dayfirst=True)
    # Round to nearest hour for the hourly grid
    df['timestamp'] = df['timestamp'].dt.floor('h')
    
    # We will just take the mean if there are multiple readings in the same hour
    df_grouped = df.groupby('timestamp')[target_val_col].mean().reset_index()
    df_grouped.rename(columns={target_val_col: new_col_name}, inplace=True)
    df_grouped.set_index('timestamp', inplace=True)
    return df_grouped

def build_master_timeseries(raw_dir, intermediate_dir):
    os.makedirs(intermediate_dir, exist_ok=True)
    
    print("Loading datasets...")
    # Paths
    temp_path = os.path.join(raw_dir, "temprature_tel_hr_cwprs_mh_2021_2025.csv")
    humid_path = os.path.join(raw_dir, "humid_tel_hr_cwprs_mh_2021_2025.csv")
    solar_path = os.path.join(raw_dir, "solar_rediation_tel_hr_cwprs_mh_2021_2025.csv")
    rain_path = os.path.join(raw_dir, "rainfall_manual_hr_maharashtra_sw_mh_2021_2025.csv")
    wind_path = os.path.join(raw_dir, "wind_speed_manual_twicedaily_maharashtra_sw_mh_1970_2025.csv")
    
    # Load and resample hourly
    print("Processing Temperature...")
    df_temp = load_and_standardize(temp_path, "Air Temperature", "temperature_c")
    
    print("Processing Humidity...")
    df_humid = load_and_standardize(humid_path, "Relative Humidity", "humidity")
    
    print("Processing Solar Radiation...")
    df_solar = load_and_standardize(solar_path, "Solar Radiation", "solar_radiation")
    
    print("Processing Rainfall...")
    df_rain = load_and_standardize(rain_path, "Rainfall", "rainfall_mm")
    
    print("Processing Wind Speed...")
    df_wind = load_and_standardize(wind_path, "Wind Speed", "wind_speed_kmh")
    
    # Merge on the common index
    print("Merging datasets into master time grid...")
    # Outer join to ensure we keep the full timeframe
    master_df = df_temp.join(df_humid, how='outer')
    master_df = master_df.join(df_solar, how='outer')
    master_df = master_df.join(df_rain, how='outer')
    master_df = master_df.join(df_wind, how='outer')
    
    # Handle missing values & interpolation
    print("Handling missing values & interpolating wind...")
    # For rainfall, missing often means 0
    master_df['rainfall_mm'] = master_df['rainfall_mm'].fillna(0)
    
    # For wind speed (twice daily), interpolate over the hourly gaps
    master_df['wind_speed_kmh'] = master_df['wind_speed_kmh'].interpolate(method='linear', limit_direction='both')
    
    # For others, we can linearly interpolate small gaps (e.g., max 3 hours)
    cols_to_interpolate = ['temperature_c', 'humidity', 'solar_radiation']
    master_df[cols_to_interpolate] = master_df[cols_to_interpolate].interpolate(method='linear', limit=3)
    
    # Drop rows where critical sensors (temp/humid) are entirely missing
    master_df.dropna(subset=['temperature_c', 'humidity'], inplace=True)
    
    # Save the output
    out_path = os.path.join(intermediate_dir, "heat_master_timeseries.csv")
    master_df.to_csv(out_path)
    print(f"Master timeseries saved to {out_path}")
    print(f"Final shape: {master_df.shape}")

if __name__ == "__main__":
    raw_dir = r"C:\Users\TEJESHWAR\OneDrive\Desktop\Terra Edge\Extreme Heat\data\raw"
    intermediate_dir = r"C:\Users\TEJESHWAR\OneDrive\Desktop\Terra Edge\Extreme Heat\data\intermediate"
    build_master_timeseries(raw_dir, intermediate_dir)
