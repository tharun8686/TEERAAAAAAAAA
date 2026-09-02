import os
import sys
import pandas as pd

from data_loader import load_all_stations
from cleaning import clean_and_validate_data
from feature_engineering import generate_features
from labels import generate_future_labels
from train import train_and_evaluate_models
from export import export_esp32_header

def run_full_air_pollution_pipeline():
    print("=" * 70)
    print("   AIR POLLUTION EARLY WARNING EDGE-AI PIPELINE (CPCB CAAQM INDIA)")
    print("=" * 70)

    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    merged_dir = os.path.join(base_dir, 'data', 'merged')
    os.makedirs(merged_dir, exist_ok=True)

    # 1. Ingest
    df_raw = load_all_stations()

    # 2. Clean & Validate
    df_clean = clean_and_validate_data(df_raw)

    # 3. Feature Engineer
    df_feats = generate_features(df_clean)

    # 4. Generate Future Targets & Labels
    df_master = generate_future_labels(df_feats)

    # Save Master Datasets
    master_csv = os.path.join(merged_dir, 'india_cpcb_air_quality_15min_master.csv')
    master_parquet = os.path.join(merged_dir, 'india_cpcb_air_quality_15min_master.parquet')
    
    df_master.to_csv(master_csv, index=False)
    try:
        df_master.to_parquet(master_parquet, index=False)
        print(f"Master Parquet Dataset saved to: {master_parquet}")
    except Exception:
        pass
    print(f"Master CSV Dataset saved to: {master_csv}")

    # 5. Train & Evaluate Models
    train_and_evaluate_models(df_master)

    # 6. Export Hardware Deployment Artifacts
    export_esp32_header()

    print("\n" + "=" * 70)
    print("AIR POLLUTION EDGE-AI PIPELINE COMPLETED SUCCESSFULLY!")
    print("=" * 70)

if __name__ == '__main__':
    run_full_air_pollution_pipeline()
