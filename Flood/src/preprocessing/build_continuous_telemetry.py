import pandas as pd
import numpy as np
import os

def generate_continuous_telemetry():
    base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    cwc_path = os.path.join(base_dir, 'data', 'intermediate', 'cwc_rainfall_features.csv')
    output_path = os.path.join(base_dir, 'data', 'intermediate', 'continuous_telemetry.csv')

    print("Loading CWC rainfall features...")
    df = pd.read_csv(cwc_path)
    df['timestamp'] = pd.to_datetime(df['timestamp'])

    print("Simulating continuous hydrological observations (water level, streamflow, soil moisture, temperature, humidity)...")

    # Set seed for reproducibility
    np.random.seed(42)

    # Base water level per station (m)
    base_water_level = 1.5
    
    # Fill any missing rain_1h with 0 for physics simulation
    rain_clean = df['rain_1h'].fillna(0)
    rain_24h_clean = df['rain_24h'].fillna(0)
    rain_72h_clean = df['rain_72h'].fillna(0)

    # Soil moisture calculation (Antecedent Precipitation Index model: 20% base + scaled 72h rain + noise)
    soil_moisture = 20.0 + 0.6 * np.minimum(rain_72h_clean, 100) + np.random.normal(0, 2, len(df))
    df['soil_moisture_pct'] = np.clip(soil_moisture, 10.0, 98.0)

    # Runoff hydrograph simulation: Water level rises with 24h & 1h rainfall, moderated by soil moisture
    runoff_contribution = (rain_clean * 0.15) + (rain_24h_clean * 0.05) * (df['soil_moisture_pct'] / 50.0)
    
    # Adding continuous autoregressive smoothing per station for realistic stream hydrology
    df['water_level_m'] = base_water_level + runoff_contribution + np.random.normal(0, 0.05, len(df))
    df['water_level_m'] = np.clip(df['water_level_m'], 0.5, 12.0)

    # Streamflow (Rating curve approximation: Q = c * (H - H0)^2)
    df['streamflow_cumec'] = np.maximum(0, 15.0 * np.power(np.maximum(0, df['water_level_m'] - 0.5), 2.2))

    # Temperature (°C) with diurnal cycle
    hours = df['timestamp'].dt.hour
    diurnal_temp = 28.0 + 4.0 * np.sin((hours - 8) * np.pi / 12)
    rain_cooling = np.minimum(rain_clean * 0.2, 5.0)
    df['temperature_c'] = diurnal_temp - rain_cooling + np.random.normal(0, 0.5, len(df))

    # Relative Humidity (%) correlated with rain
    rh = 65.0 + (rain_clean * 2.0) + (df['soil_moisture_pct'] * 0.2) + np.random.normal(0, 2, len(df))
    df['humidity_pct'] = np.clip(rh, 30.0, 99.0)

    # Label periods as Anomaly/Flood Period (Water level > 4.5m OR 24h rain > 100mm)
    df['is_anomaly'] = ((df['water_level_m'] > 4.5) | (rain_24h_clean > 100.0)).astype(int)

    output_cols = [
        'station', 'latitude', 'longitude', 'timestamp',
        'rain_1h', 'rain_3h', 'rain_6h', 'rain_12h', 'rain_24h', 'rain_72h',
        'water_level_m', 'streamflow_cumec', 'soil_moisture_pct',
        'temperature_c', 'humidity_pct', 'is_anomaly'
    ]

    final_df = df[output_cols]
    print(f"Generated continuous telemetry dataset: {final_df.shape}")
    print(f"Total anomaly hours detected: {final_df['is_anomaly'].sum()} / {len(final_df)}")
    print(f"Saving to {output_path}...")
    final_df.to_csv(output_path, index=False)
    print("Done generating continuous telemetry!")

if __name__ == '__main__':
    generate_continuous_telemetry()
