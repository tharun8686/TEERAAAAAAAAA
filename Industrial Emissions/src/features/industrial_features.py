import pandas as pd
import numpy as np
import os

def build_features(input_path, output_path):
    print("Loading master timeseries...")
    df = pd.read_csv(input_path, index_col='sample_id')
    
    print("Calculating rates of change...")
    df['gas_rate'] = df['gas_response'].diff().fillna(0)
    df['PM2.5_rate'] = df['PM2.5'].diff().fillna(0)
    df['PM10_rate'] = df['PM10'].diff().fillna(0)
    df['temperature_rate'] = df['temperature_c'].diff().fillna(0)
    df['humidity_rate'] = df['humidity'].diff().fillna(0)
    df['pressure_rate'] = df['pressure'].diff().fillna(0)
    
    print("Calculating rolling features...")
    # Using window=12 to represent a recent telemetry sequence
    df['rolling_mean_gas'] = df['gas_response'].rolling(window=12, min_periods=1).mean()
    df['rolling_mean_PM2.5'] = df['PM2.5'].rolling(window=12, min_periods=1).mean()
    df['rolling_mean_PM10'] = df['PM10'].rolling(window=12, min_periods=1).mean()
    
    df['rolling_std_gas'] = df['gas_response'].rolling(window=12, min_periods=1).std().fillna(0)
    df['rolling_std_PM2.5'] = df['PM2.5'].rolling(window=12, min_periods=1).std().fillna(0)
    df['rolling_std_PM10'] = df['PM10'].rolling(window=12, min_periods=1).std().fillna(0)
    
    print("Engineering risk spike scores...")
    df['gas_spike_score'] = (df['gas_response'] / (df['rolling_mean_gas'] + 1e-5)).clip(upper=10)
    df['particulate_spike_score'] = (df['PM2.5'] / (df['rolling_mean_PM2.5'] + 1e-5)).clip(upper=10)
    
    # Combined emission score: high gas AND high PM co-occurrence indicates a leak/plume
    df['combined_emission_score'] = (df['gas_response'] * df['PM2.5']) / 1000.0
    
    # Plume persistence score (count of successive samples above baseline in the window)
    is_above_baseline = ((df['gas_response'] > 300) | (df['PM2.5'] > 50)).astype(int)
    df['persistence_score'] = is_above_baseline.rolling(window=12, min_periods=1).sum()
    
    # Sensor drift proxy
    df['sensor_drift_score'] = df['rolling_mean_gas'] * 0.05
    
    # Save output
    df.to_csv(output_path)
    print(f"Features engineered and saved to {output_path}. Shape: {df.shape}")

if __name__ == "__main__":
    intermediate_dir = r"C:\Users\TEJESHWAR\OneDrive\Desktop\Terra Edge\Industrial Emissions\data\intermediate"
    in_path = os.path.join(intermediate_dir, "industrial_master_timeseries.csv")
    out_path = os.path.join(intermediate_dir, "industrial_features.csv")
    build_features(in_path, out_path)
