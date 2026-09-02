import pandas as pd
import numpy as np
import os
import json

def clean_and_validate_data(df):
    print("Performing Data Cleaning & Physical Sanity Validation...")

    # Convert Timestamp
    df['timestamp'] = pd.to_datetime(df['timestamp'], format='mixed', utc=True, errors='coerce')
    df.dropna(subset=['timestamp'], inplace=True)
    df.sort_values(by=['station_id', 'timestamp'], inplace=True)
    df.drop_duplicates(subset=['station_id', 'timestamp'], inplace=True)
    df.reset_index(drop=True, inplace=True)

    # Physical Range Validation
    pollutant_cols = ['pm25', 'pm10', 'no', 'no2', 'nox', 'nh3', 'so2', 'co', 'o3']
    for p in pollutant_cols:
        if p in df.columns:
            df[p] = pd.to_numeric(df[p], errors='coerce')
            df[p] = df[p].apply(lambda x: np.nan if x < 0 or x > 2000 else x)

    if 'relative_humidity' in df.columns:
        df['relative_humidity'] = pd.to_numeric(df['relative_humidity'], errors='coerce')
        df['relative_humidity'] = df['relative_humidity'].apply(lambda x: np.nan if x < 0 or x > 100 else x)

    if 'temperature' in df.columns:
        df['temperature'] = pd.to_numeric(df['temperature'], errors='coerce')
        df['temperature'] = df['temperature'].apply(lambda x: np.nan if x < -10 or x > 60 else x)

    if 'wind_speed' in df.columns:
        df['wind_speed'] = pd.to_numeric(df['wind_speed'], errors='coerce')
        df['wind_speed'] = df['wind_speed'].apply(lambda x: np.nan if x < 0 or x > 50 else x)

    # Station-wise Interpolation (max gap = 4 samples / 1 hour)
    cleaned_dfs = []
    quality_records = []

    for station_id, group in df.groupby('station_id'):
        group = group.copy()
        station_name = group['station_name'].iloc[0]
        
        # Calculate Data Quality Metrics
        total_rows = len(group)
        start_t = str(group['timestamp'].min())
        end_t = str(group['timestamp'].max())

        num_cols = [c for c in group.columns if c not in ['station_id', 'state', 'city', 'station_name', 'timestamp']]
        
        # Missingness Indicators before interpolation
        for col in ['pm25', 'pm10', 'temperature', 'relative_humidity', 'pressure', 'wind_speed']:
            if col in group.columns:
                group[f'{col}_missing'] = group[col].isnull().astype(int)
                # Station-wise short gap interpolation
                group[col] = group[col].interpolate(method='linear', limit=4)

        cleaned_dfs.append(group)

        quality_records.append({
            'station_id': station_id,
            'station_name': station_name,
            'total_observations': total_rows,
            'start_timestamp': start_t,
            'end_timestamp': end_t,
            'pm25_missing_pct': round(float(group['pm25_missing'].mean() * 100), 2) if 'pm25_missing' in group else 0.0,
            'pm10_missing_pct': round(float(group['pm10_missing'].mean() * 100), 2) if 'pm10_missing' in group else 0.0
        })

    master_cleaned = pd.concat(cleaned_dfs, ignore_index=True)
    
    # Save Quality Reports
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    reports_dir = os.path.join(base_dir, 'reports')
    os.makedirs(reports_dir, exist_ok=True)

    df_qual = pd.DataFrame(quality_records)
    df_qual.to_csv(os.path.join(reports_dir, 'data_quality_report.csv'), index=False)
    
    with open(os.path.join(reports_dir, 'data_quality_report.json'), 'w') as f:
        json.dump(quality_records, f, indent=2)

    print(f"Cleaning Complete! Processed {len(master_cleaned):,} observations. Quality report saved to: {reports_dir}")
    return master_cleaned
