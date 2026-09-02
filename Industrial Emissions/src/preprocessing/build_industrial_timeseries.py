import pandas as pd
import numpy as np
import os
import glob

def parse_libsvm_line(line):
    """Parses a LIBSVM line into label and feature dict."""
    parts = line.strip().split()
    if not parts:
        return None, {}
    label = float(parts[0])
    features = {}
    for part in parts[1:]:
        if ':' in part:
            idx, val = part.split(':')
            features[int(idx)] = float(val)
    return label, features

def build_timeseries(raw_dir, intermediate_dir):
    os.makedirs(intermediate_dir, exist_ok=True)
    canonical_rows = []
    
    # 1. Process MQ Gas Sensors Measurements (CSV)
    mq_path = os.path.join(raw_dir, "Gas-Sensors-Measurements-Dataset-v1.0.0", "TakMashhido-Gas-Sensors-Measurements-Dataset-a4f36db", "Gas_Sensors_Measurements.csv")
    if os.path.exists(mq_path):
        print("Processing MQ Gas Sensors...")
        df_mq = pd.read_csv(mq_path)
        for _, row in df_mq.iterrows():
            canonical_rows.append({
                "gas_response": row["MQ135"],
                "smoke_or_proxy_response": row["MQ2"],
                "PM2.5": 25.0,  # Ambient defaults
                "PM10": 45.0,
                "temperature_c": 28.0,
                "humidity": 65.0,
                "pressure": 1012.0,
                "gas_type": row["Gas"],
                "source": "MQ_Dataset"
            })
            
    # 2. Process India AQI (CSV)
    aqi_path = os.path.join(raw_dir, "3b01bcb8-0b14-4abf-b6f2-c1bfd384ba69.csv")
    if os.path.exists(aqi_path):
        print("Processing India AQI...")
        df_aqi = pd.read_csv(aqi_path)
        # Filter down to PM2.5 / PM10
        pm25_df = df_aqi[df_aqi["pollutant_id"] == "PM2.5"]
        pm10_df = df_aqi[df_aqi["pollutant_id"] == "PM10"]
        
        # Take a representative sample to avoid overfitting to pure ambient data
        sample_size = min(2000, len(pm25_df), len(pm10_df))
        pm25_vals = pm25_df["pollutant_avg"].sample(sample_size, random_state=42).values
        pm10_vals = pm10_df["pollutant_avg"].sample(sample_size, random_state=42).values
        
        for i in range(sample_size):
            # PM values sometimes contain NaNs
            p25 = pm25_vals[i] if not np.isnan(pm25_vals[i]) else 30.0
            p10 = pm10_vals[i] if not np.isnan(pm10_vals[i]) else 60.0
            
            canonical_rows.append({
                "gas_response": 150.0, # Low default background gas response
                "smoke_or_proxy_response": 120.0,
                "PM2.5": p25,
                "PM10": p10,
                "temperature_c": 30.0,
                "humidity": 70.0,
                "pressure": 1010.0,
                "gas_type": "Air",
                "source": "India_AQI"
            })

    # 3. Process UCI Gas Sensor Drift Batches (Sampled)
    # Read first 1000 lines from batch1.dat to get drift patterns
    drift_path = os.path.join(raw_dir, "gas+sensor+array+drift+dataset", "Dataset", "batch1.dat")
    if os.path.exists(drift_path):
        print("Processing UCI Drift Batch 1...")
        count = 0
        with open(drift_path, "r") as f:
            for line in f:
                if count >= 1500:
                    break
                label, features = parse_libsvm_line(line)
                if label is not None:
                    # Map feature index 1 (S1) and index 2 (S2) as gas/smoke proxies
                    gas = features.get(1, 200.0)
                    smoke = features.get(2, 150.0)
                    # Label 1 to 6 represent different chemical gases
                    gas_map = {1: "Ethanol", 2: "Ethylene", 3: "Ammonia", 4: "Acetaldehyde", 5: "Carbon Monoxide", 6: "Toluene"}
                    canonical_rows.append({
                        "gas_response": gas,
                        "smoke_or_proxy_response": smoke,
                        "PM2.5": 20.0,
                        "PM10": 40.0,
                        "temperature_c": 25.0,
                        "humidity": 55.0,
                        "pressure": 1013.0,
                        "gas_type": gas_map.get(int(label), "Unknown"),
                        "source": "UCI_Drift"
                    })
                    count += 1

    # 4. Process Flow Modulation features.csv
    flow_path = os.path.join(raw_dir, "gas+sensor+array+under+flow+modulation", "features.csv")
    if os.path.exists(flow_path):
        print("Processing Flow Modulation...")
        df_flow = pd.read_csv(flow_path)
        for _, row in df_flow.sample(min(1500, len(df_flow)), random_state=42).iterrows():
            canonical_rows.append({
                "gas_response": row["S1_max"],
                "smoke_or_proxy_response": row["S2_max"],
                "PM2.5": 18.0,
                "PM10": 35.0,
                "temperature_c": 27.0,
                "humidity": 60.0,
                "pressure": 1011.0,
                "gas_type": row["gas"] if isinstance(row["gas"], str) else "Mixed",
                "source": "Flow_Modulation"
            })
            
    # Build DataFrame
    master_df = pd.DataFrame(canonical_rows)
    master_df.index.name = "sample_id"
    
    # Save output
    out_path = os.path.join(intermediate_dir, "industrial_master_timeseries.csv")
    master_df.to_csv(out_path)
    print(f"Master timeseries built and saved to {out_path}. Shape: {master_df.shape}")

if __name__ == "__main__":
    raw_dir = r"C:\Users\TEJESHWAR\OneDrive\Desktop\Terra Edge\Industrial Emissions\data\raw"
    intermediate_dir = r"C:\Users\TEJESHWAR\OneDrive\Desktop\Terra Edge\Industrial Emissions\data\intermediate"
    build_timeseries(raw_dir, intermediate_dir)
