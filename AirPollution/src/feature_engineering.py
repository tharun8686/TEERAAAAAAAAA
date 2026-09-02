import pandas as pd
import numpy as np

def generate_features(df):
    print("Generating Lags, Rolling Windows, Slope Trends, and Circular Encodings...")
    
    station_dfs = []

    for station_id, group in df.groupby('station_id'):
        group = group.copy()
        group.sort_values(by='timestamp', inplace=True)

        # Lags for PM2.5 & PM10 (15m steps: 15m=1, 30m=2, 45m=3, 60m=4, 120m=8)
        for lag_min, lag_step in [(15, 1), (30, 2), (45, 3), (60, 4), (120, 8)]:
            group[f'pm25_lag_{lag_min}'] = group['pm25'].shift(lag_step)
            if lag_min in [15, 30, 60]:
                group[f'pm10_lag_{lag_min}'] = group['pm10'].shift(lag_step)

        # Lags for other pollutants
        for p in ['no2', 'so2', 'co', 'o3', 'nh3', 'nox']:
            if p in group.columns:
                group[f'{p}_lag_30'] = group[p].shift(2)

        # Rolling Statistics for PM2.5 (15m=1, 30m=2, 60m=4, 120m=8)
        for w_min, w_step in [(15, 1), (30, 2), (60, 4), (120, 8)]:
            group[f'pm25_mean_{w_min}'] = group['pm25'].rolling(window=w_step, min_periods=1).mean()
            if w_min in [15, 30, 60]:
                group[f'pm25_std_{w_min}'] = group['pm25'].rolling(window=w_step, min_periods=1).std().fillna(0.0)
            if w_min in [30, 60]:
                group[f'pm25_min_{w_min}'] = group['pm25'].rolling(window=w_step, min_periods=1).min()
                group[f'pm25_max_{w_min}'] = group['pm25'].rolling(window=w_step, min_periods=1).max()

        # Trend Deltas & Slopes
        group['pm25_delta_15'] = group['pm25'].diff(periods=1).fillna(0.0)
        group['pm25_delta_30'] = group['pm25'].diff(periods=2).fillna(0.0)
        group['pm25_delta_60'] = group['pm25'].diff(periods=4).fillna(0.0)

        group['pm25_slope_15'] = group['pm25_delta_15'] / 15.0
        group['pm25_slope_30'] = group['pm25_delta_30'] / 30.0
        group['pm25_slope_60'] = group['pm25_delta_60'] / 60.0

        group['pm10_delta_30'] = group['pm10'].diff(periods=2).fillna(0.0)
        group['pm10_slope_30'] = group['pm10_delta_30'] / 30.0

        if 'no2' in group.columns:
            group['no2_delta_30'] = group['no2'].diff(periods=2).fillna(0.0)
            group['no2_slope_30'] = group['no2_delta_30'] / 30.0

        if 'co' in group.columns:
            group['co_delta_30'] = group['co'].diff(periods=2).fillna(0.0)
            group['co_slope_30'] = group['co_delta_30'] / 30.0

        # Weather Trend Features
        if 'temperature' in group.columns:
            group['temperature_delta_30'] = group['temperature'].diff(periods=2).fillna(0.0)
        if 'relative_humidity' in group.columns:
            group['humidity_delta_30'] = group['relative_humidity'].diff(periods=2).fillna(0.0)
        if 'pressure' in group.columns:
            group['pressure_delta_30'] = group['pressure'].diff(periods=2).fillna(0.0)
        if 'wind_speed' in group.columns:
            group['wind_speed_delta_30'] = group['wind_speed'].diff(periods=2).fillna(0.0)

        # Circular Wind Direction Encoding (sin / cos)
        if 'wind_direction' in group.columns:
            wd_rad = np.radians(group['wind_direction'].fillna(0.0))
            group['wind_direction_sin'] = np.sin(wd_rad)
            group['wind_direction_cos'] = np.cos(wd_rad)
        else:
            group['wind_direction_sin'] = 0.0
            group['wind_direction_cos'] = 1.0

        # Gas Proxy for Edge Model (Combined CO + NO2 + SO2 proxy)
        co_val = group['co'].fillna(0.5) if 'co' in group.columns else 0.5
        no2_val = group['no2'].fillna(20.0) if 'no2' in group.columns else 20.0
        group['gas_proxy'] = (co_val * 20.0 + no2_val * 0.5).clip(1.0, 200.0)

        # Cyclic Time Features
        group['hour'] = group['timestamp'].dt.hour
        group['day_of_week'] = group['timestamp'].dt.dayofweek
        group['month'] = group['timestamp'].dt.month
        group['is_weekend'] = group['day_of_week'].apply(lambda x: 1 if x >= 5 else 0)

        group['hour_sin'] = np.sin(2 * np.pi * group['hour'] / 24.0)
        group['hour_cos'] = np.cos(2 * np.pi * group['hour'] / 24.0)
        group['day_sin'] = np.sin(2 * np.pi * group['day_of_week'] / 7.0)
        group['day_cos'] = np.cos(2 * np.pi * group['day_of_week'] / 7.0)
        group['month_sin'] = np.sin(2 * np.pi * group['month'] / 12.0)
        group['month_cos'] = np.cos(2 * np.pi * group['month'] / 12.0)

        station_dfs.append(group)

    master_engineered = pd.concat(station_dfs, ignore_index=True)
    print(f"Feature Engineering Complete! Derived {master_engineered.shape[1]} features.")
    return master_engineered
