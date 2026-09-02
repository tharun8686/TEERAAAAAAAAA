import pandas as pd
import numpy as np
import os

def build_features(input_path, output_path):
    print("Loading master timeseries...")
    df = pd.read_csv(input_path, index_col='sample_id')
    
    print("Calculating rates of change...")
    df['pH_rate'] = df['pH'].diff().fillna(0)
    df['turbidity_rate'] = df['turbidity'].diff().fillna(0)
    df['EC_rate'] = df['EC'].diff().fillna(0)
    df['TDS_rate'] = df['TDS'].diff().fillna(0)
    df['DO_rate'] = df['dissolved_oxygen'].diff().fillna(0)
    df['temperature_rate'] = df['temperature_c'].diff().fillna(0)
    
    print("Calculating rolling features...")
    window_sz = 12
    df['rolling_mean_pH'] = df['pH'].rolling(window=window_sz, min_periods=1).mean()
    df['rolling_mean_turbidity'] = df['turbidity'].rolling(window=window_sz, min_periods=1).mean()
    df['rolling_mean_EC'] = df['EC'].rolling(window=window_sz, min_periods=1).mean()
    df['rolling_mean_TDS'] = df['TDS'].rolling(window=window_sz, min_periods=1).mean()
    df['rolling_mean_DO'] = df['dissolved_oxygen'].rolling(window=window_sz, min_periods=1).mean()
    
    df['rolling_std_pH'] = df['pH'].rolling(window=window_sz, min_periods=1).std().fillna(0)
    df['rolling_std_turbidity'] = df['turbidity'].rolling(window=window_sz, min_periods=1).std().fillna(0)
    df['rolling_std_EC'] = df['EC'].rolling(window=window_sz, min_periods=1).std().fillna(0)
    df['rolling_std_TDS'] = df['TDS'].rolling(window=window_sz, min_periods=1).std().fillna(0)
    df['rolling_std_DO'] = df['dissolved_oxygen'].rolling(window=window_sz, min_periods=1).std().fillna(0)
    
    print("Calculating anomaly and shift scores...")
    # Acidity shift: deviation from neutral water pH (7.0)
    df['acidity_shift_score'] = np.abs(df['pH'] - 7.0)
    
    # Turbidity spike: ratio of current to rolling average
    df['degradation_spike_score'] = (df['turbidity'] / (df['rolling_mean_turbidity'] + 1e-5)).clip(upper=15)
    
    # EC shift: ratio of current to rolling average
    df['conductivity_shift_score'] = (df['EC'] / (df['rolling_mean_EC'] + 1e-5)).clip(upper=15)
    
    # Dissolved oxygen drop score (higher score = lower oxygen, i.e. more degraded)
    df['oxygen_drop_score'] = (8.0 - df['dissolved_oxygen']).clip(lower=0)
    
    # Combined water quality index proxy
    # High turbidity + high TDS + low oxygen indicates major degradation
    df['combined_water_quality_score'] = (df['turbidity'] * df['TDS']) / (df['dissolved_oxygen'] + 1e-5)
    
    # Persistence score: how many samples in the window violate standard limits (pH < 6.5 or pH > 8.5 or Turbidity > 10 NTU or TDS > 500)
    violates_limits = ((df['pH'] < 6.5) | (df['pH'] > 8.5) | (df['turbidity'] > 10.0) | (df['TDS'] > 500.0)).astype(int)
    df['persistence_score'] = violates_limits.rolling(window=window_sz, min_periods=1).sum()
    
    df.to_csv(output_path)
    print(f"Features engineered and saved to {output_path}. Shape: {df.shape}")

if __name__ == "__main__":
    intermediate_dir = r"C:\Users\TEJESHWAR\OneDrive\Desktop\Terra Edge\Water Quality Degradation\data\intermediate"
    in_path = os.path.join(intermediate_dir, "water_master_timeseries.csv")
    out_path = os.path.join(intermediate_dir, "water_features.csv")
    build_features(in_path, out_path)
