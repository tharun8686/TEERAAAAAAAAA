import pandas as pd
import numpy as np
import os
import glob

def build_cleveland_pipeline():
    base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    raw_dir = os.path.join(base_dir, 'data', 'raw')
    inter_dir = os.path.join(base_dir, 'data', 'intermediate')
    reports_dir = os.path.join(base_dir, 'reports')
    os.makedirs(inter_dir, exist_ok=True)
    os.makedirs(reports_dir, exist_ok=True)

    print("Building Cleveland Corral 15-Minute Clean Time Series...")

    # Load all Middle Station CSV files (most complete multi-year sensor record)
    mid_files = glob.glob(os.path.join(raw_dir, '**', 'CCmiddle_WY*.csv'), recursive=True)
    mid_files = sorted(mid_files)

    all_dfs = []
    for f in mid_files:
        try:
            df_curr = pd.read_csv(f, skiprows=3)
            time_col = [c for c in df_curr.columns if 'date' in c.lower() or 'time' in c.lower()][0]
            df_curr.rename(columns={time_col: 'timestamp'}, inplace=True)
            df_curr['timestamp'] = pd.to_datetime(df_curr['timestamp'], errors='coerce')
            df_curr.dropna(subset=['timestamp'], inplace=True)
            all_dfs.append(df_curr)
        except Exception as e:
            print(f"Skipping corrupt file {f}: {e}")

    df_mid = pd.concat(all_dfs, ignore_index=True)
    df_mid.sort_values(by='timestamp', inplace=True)
    df_mid.drop_duplicates(subset=['timestamp'], inplace=True)
    df_mid.reset_index(drop=True, inplace=True)

    print(f"Combined Middle Station Data: {df_mid.shape[0]:,} rows from {df_mid['timestamp'].min()} to {df_mid['timestamp'].max()}")

    # Map core columns
    disp_cols = [c for c in df_mid.columns if 'extensometer' in c or '_E' in c]
    piezo_cols = [c for c in df_mid.columns if 'piezometer' in c or 'pressure' in c or '_P' in c]
    rain_cols = [c for c in df_mid.columns if 'precipitation' in c and 'cum' not in c]

    disp_col = disp_cols[0] if disp_cols else None
    piezo_col = piezo_cols[0] if piezo_cols else None
    rain_col = rain_cols[0] if rain_cols else None

    print(f"Primary Displacement Channel: {disp_col}")
    print(f"Primary Pore-Pressure Channel: {piezo_col}")
    print(f"Primary Rainfall Channel: {rain_col}")

    # Standardize Column Names
    clean_df = pd.DataFrame()
    clean_df['timestamp'] = df_mid['timestamp']
    clean_df['rainfall_15m'] = pd.to_numeric(df_mid[rain_col], errors='coerce').fillna(0.0) if rain_col else 0.0
    clean_df['displacement_cm'] = pd.to_numeric(df_mid[disp_col], errors='coerce') if disp_col else np.nan
    clean_df['pore_pressure_cm'] = pd.to_numeric(df_mid[piezo_col], errors='coerce') if piezo_col else np.nan

    # Synthetic proxy soil moisture derived from antecedent precipitation & pressure head
    clean_df['soil_moisture_vwc'] = (clean_df['pore_pressure_cm'].fillna(0.0) / 100.0 * 0.45 + 0.15).clip(0.05, 0.50)

    # Forward fill small gaps in continuous readings (up to 4 steps / 1 hour)
    clean_df['displacement_cm'] = clean_df['displacement_cm'].ffill(limit=4)
    clean_df['pore_pressure_cm'] = clean_df['pore_pressure_cm'].ffill(limit=4)

    # Save Clean Timeseries
    clean_csv_path = os.path.join(inter_dir, 'cleveland_clean_timeseries.csv')
    clean_df.to_csv(clean_csv_path, index=False)

    print("Generating Causal Temporal Features (Strictly past-looking windows)...")
    feat_df = clean_df.copy()

    # Rainfall Accumulation Windows (15m steps: 1h=4, 3h=12, 6h=24, 12h=48, 24h=96, 48h=192, 72h=288)
    feat_df['rainfall_1h'] = feat_df['rainfall_15m'].rolling(window=4, min_periods=1).sum()
    feat_df['rainfall_3h'] = feat_df['rainfall_15m'].rolling(window=12, min_periods=1).sum()
    feat_df['rainfall_6h'] = feat_df['rainfall_15m'].rolling(window=24, min_periods=1).sum()
    feat_df['rainfall_12h'] = feat_df['rainfall_15m'].rolling(window=48, min_periods=1).sum()
    feat_df['rainfall_24h'] = feat_df['rainfall_15m'].rolling(window=96, min_periods=1).sum()
    feat_df['rainfall_48h'] = feat_df['rainfall_15m'].rolling(window=192, min_periods=1).sum()
    feat_df['rainfall_72h'] = feat_df['rainfall_15m'].rolling(window=288, min_periods=1).sum()

    # Soil Moisture Derivatives
    feat_df['soil_moisture_change_1h'] = feat_df['soil_moisture_vwc'].diff(periods=4).fillna(0.0)
    feat_df['soil_moisture_rate'] = feat_df['soil_moisture_vwc'].diff().fillna(0.0)

    # Pore-Water Pressure Derivatives
    feat_df['pore_pressure_change_1h'] = feat_df['pore_pressure_cm'].diff(periods=4).fillna(0.0)
    feat_df['pore_pressure_rate'] = feat_df['pore_pressure_cm'].diff().fillna(0.0)

    # Displacement Kinematics
    feat_df['displacement_change_1h'] = feat_df['displacement_cm'].diff(periods=4).fillna(0.0)
    feat_df['displacement_rate'] = feat_df['displacement_cm'].diff().fillna(0.0)
    feat_df['displacement_acceleration'] = feat_df['displacement_rate'].diff().fillna(0.0)

    # Rolling Volatility / Risk Indicators
    feat_df['roll_disp_std_24h'] = feat_df['displacement_rate'].rolling(window=96, min_periods=1).std().fillna(0.0)
    feat_df['roll_press_max_24h'] = feat_df['pore_pressure_cm'].rolling(window=96, min_periods=1).max().fillna(0.0)

    eng_csv_path = os.path.join(inter_dir, 'cleveland_engineered_features.csv')
    feat_df.to_csv(eng_csv_path, index=False)

    print(f"Cleveland Feature Engineering Complete! Saved {feat_df.shape[1]} features to: {eng_csv_path}")

if __name__ == '__main__':
    build_cleveland_pipeline()
