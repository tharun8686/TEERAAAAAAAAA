import pandas as pd
import numpy as np
import os

def process_cwc():
    base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    raw_dir = os.path.join(base_dir, 'data', 'raw')
    output_path = os.path.join(base_dir, 'data', 'intermediate', 'cwc_rainfall_features.csv')

    manual_path = os.path.join(raw_dir, 'rainfall_manual_hr_cwc_tn_1991_2020.csv')
    tel_path = os.path.join(raw_dir, 'rainfall_tel_hr_cwc_tn_2021_2025.csv')

    print("Loading CWC datasets...")
    df_manual = pd.read_csv(manual_path)
    df_tel = pd.read_csv(tel_path)

    # Rename rainfall column to a common name
    df_manual['rain_1h'] = df_manual['Manual Hourly Rainfall (mm)']
    df_tel['rain_1h'] = df_tel['Telemetry Hourly Rainfall (mm)']

    # Select standard columns
    cols = ['Station', 'Latitude', 'Longitude', 'Data Acquisition Time', 'rain_1h']
    
    df_m = df_manual[cols].copy()
    df_t = df_tel[cols].copy()

    # Combine datasets
    print("Combining datasets...")
    df_combined = pd.concat([df_m, df_t], ignore_index=True)

    # Rename to standardized lowercase names
    df_combined.rename(columns={
        'Station': 'station',
        'Latitude': 'latitude',
        'Longitude': 'longitude',
        'Data Acquisition Time': 'timestamp_str'
    }, inplace=True)

    # Parse timestamps cleanly
    print("Parsing timestamps...")
    df_combined['timestamp'] = pd.to_datetime(df_combined['timestamp_str'], format='%d-%m-%Y %H:%M', errors='coerce')
    df_combined.drop(columns=['timestamp_str'], inplace=True)
    df_combined.dropna(subset=['timestamp'], inplace=True)

    # Clean duplicates & sort chronologically per station
    print("Cleaning duplicates and sorting chronologically...")
    df_combined.sort_values(by=['station', 'timestamp'], inplace=True)
    df_combined.drop_duplicates(subset=['station', 'timestamp'], keep='last', inplace=True)

    # Explicitly retain NaNs without filling with 0
    print("Computing rolling rainfall features (3h, 6h, 12h, 24h, 72h)...")
    
    # We set index to timestamp for rolling window calculations
    results = []
    
    for station, group in df_combined.groupby('station'):
        group = group.set_index('timestamp').sort_index()
        
        # Time-based rolling sums
        # min_periods=1 ensures that if at least 1 valid observation exists in the window, it's calculated
        group['rain_3h'] = group['rain_1h'].rolling('3h', min_periods=1).sum()
        group['rain_6h'] = group['rain_1h'].rolling('6h', min_periods=1).sum()
        group['rain_12h'] = group['rain_1h'].rolling('12h', min_periods=1).sum()
        group['rain_24h'] = group['rain_1h'].rolling('24h', min_periods=1).sum()
        group['rain_72h'] = group['rain_1h'].rolling('72h', min_periods=1).sum()
        
        # Intensity (mm/hr) is equal to hourly rainfall
        group['rainfall_intensity'] = group['rain_1h']
        
        results.append(group.reset_index())

    final_df = pd.concat(results, ignore_index=True)

    # Reorder columns
    output_cols = [
        'station', 'latitude', 'longitude', 'timestamp',
        'rain_1h', 'rain_3h', 'rain_6h', 'rain_12h', 'rain_24h', 'rain_72h',
        'rainfall_intensity'
    ]
    final_df = final_df[output_cols]

    print(f"Final processed dataset shape: {final_df.shape}")
    print(f"Saving to {output_path}...")
    final_df.to_csv(output_path, index=False)
    print("Done processing CWC rainfall!")

if __name__ == '__main__':
    process_cwc()
