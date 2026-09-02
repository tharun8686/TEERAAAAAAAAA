import pandas as pd
import numpy as np
import os

def build_wide_sensor_table():
    base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    raw_fusion_path = os.path.join(base_dir, 'data', 'raw', 'forest_fire_sensor_fusion_raw.csv.gz.csv')
    output_wide_path = os.path.join(base_dir, 'data', 'intermediate', 'fire_sensor_wide.csv')

    print("Loading long-format primary sensor fusion dataset...")
    df_long = pd.read_csv(raw_fusion_path)
    print(f"Loaded long dataset: {df_long.shape} rows.")

    # Pivot long format table into wide format
    print("Pivoting long-format table to wide-format (one row per timestamp)...")
    df_wide = df_long.pivot(index='TIME', columns='NAME', values='VALUE').reset_index()

    # Column mapping to standard clean names
    column_mapping = {
        'TIME': 'timestamp',
        'Temperature[C]': 'temperature',
        'Humidity[%]': 'humidity',
        'Pressure[hPa]': 'pressure',
        'TVOC[ppb]': 'tvoc',
        'eCO2[ppm]': 'eco2',
        'Raw H2': 'raw_h2',
        'Raw Ethanol': 'raw_ethanol',
        'PM1.0': 'pm1',
        'PM2.5': 'pm25',
        'NC0.5': 'nc05',
        'NC1.0': 'nc10',
        'NC2.5': 'nc25',
        'CNT': 'cnt',
        'Fire Alarm': 'fire_alarm'
    }

    df_wide.rename(columns=column_mapping, inplace=True)

    # Reorder columns logically
    desired_cols = [
        'timestamp', 'temperature', 'humidity', 'pressure',
        'tvoc', 'eco2', 'raw_h2', 'raw_ethanol',
        'pm1', 'pm25', 'nc05', 'nc10', 'nc25', 'cnt', 'fire_alarm'
    ]
    
    # Filter columns present
    existing_cols = [c for c in desired_cols if c in df_wide.columns]
    df_wide = df_wide[existing_cols]

    # Sort chronologically by timestamp
    df_wide.sort_values(by='timestamp', inplace=True)
    df_wide.reset_index(drop=True, inplace=True)

    # Convert target to integer binary (0 or 1)
    df_wide['fire_alarm'] = df_wide['fire_alarm'].astype(int)

    print("-" * 40)
    print("PHASE 2 VALIDATION RESULTS")
    print("-" * 40)
    print(f"Wide Dataset Shape: {df_wide.shape}")
    print(f"Null Values Count:\n{df_wide.isnull().sum()}")
    print(f"\nTarget Class Distribution (`fire_alarm`):")
    print(df_wide['fire_alarm'].value_counts())
    print("-" * 40)

    # Save wide format CSV
    print(f"Saving wide dataset to: {output_wide_path}...")
    df_wide.to_csv(output_wide_path, index=False)
    print("Done building primary wide sensor table!")

if __name__ == '__main__':
    build_wide_sensor_table()
