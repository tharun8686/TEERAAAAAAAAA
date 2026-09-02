import pandas as pd
import numpy as np
import os

def engineer_time_series_features():
    base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    wide_path = os.path.join(base_dir, 'data', 'intermediate', 'fire_sensor_wide.csv')
    output_features_path = os.path.join(base_dir, 'data', 'intermediate', 'fire_features.csv')

    print("Loading wide sensor table...")
    df = pd.read_csv(wide_path)
    df.sort_values(by='timestamp', inplace=True)
    df.reset_index(drop=True, inplace=True)

    print("Engineering time-series trend, delta, and rolling features...")

    # Key numeric sensors for feature engineering
    target_sensors = ['temperature', 'humidity', 'pressure', 'pm25', 'tvoc', 'eco2', 'raw_h2', 'raw_ethanol']

    # 1. Delta features (short-term & medium-term shifts: 1 step, 5 steps, 10 steps, 30 steps)
    for col in target_sensors:
        df[f'{col}_delta_1'] = df[col].diff(1).fillna(0)
        df[f'{col}_delta_5'] = df[col].diff(5).fillna(0)
        df[f'{col}_delta_10'] = df[col].diff(10).fillna(0)
        df[f'{col}_delta_30'] = df[col].diff(30).fillna(0)

        # 2. Rate of change (percentage / step)
        df[f'{col}_rate'] = (df[col].diff(1) / (df[col].shift(1).abs() + 1e-6)).fillna(0)

        # 3. Rolling statistics (windows: 5, 15, 60 samples)
        for w in [5, 15, 60]:
            df[f'{col}_roll_mean_{w}'] = df[col].rolling(window=w, min_periods=1).mean()
            df[f'{col}_roll_std_{w}'] = df[col].rolling(window=w, min_periods=1).std().fillna(0)
            df[f'{col}_roll_min_{w}'] = df[col].rolling(window=w, min_periods=1).min()
            df[f'{col}_roll_max_{w}'] = df[col].rolling(window=w, min_periods=1).max()

    print(f"Engineered dataset shape: {df.shape}")
    print(f"Saving engineered features to: {output_features_path}...")
    df.to_csv(output_features_path, index=False)
    print("Done time-series feature engineering!")

if __name__ == '__main__':
    engineer_time_series_features()
