import pandas as pd
import numpy as np
import os
import joblib
import json
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, confusion_matrix, classification_report

def validate_on_resisto():
    base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    resisto_path = os.path.join(base_dir, 'data', 'raw', 'forest_fire_resisto_raw.csv.csv')
    rf_model_path = os.path.join(base_dir, 'models', 'fire_random_forest.pkl')
    scaler_path = os.path.join(base_dir, 'models', 'fire_scaler.pkl')
    config_path = os.path.join(base_dir, 'models', 'fire_model_config.json')
    report_path = os.path.join(base_dir, 'reports', 'fire_resisto_validation.md')

    print("Loading Resisto OOD Validation Dataset...")
    df_resisto = pd.read_csv(resisto_path)
    print(f"Loaded Resisto dataset: {df_resisto.shape}")

    # Load Model, Scaler, and Config
    rf_model = joblib.load(rf_model_path)
    scaler = joblib.load(scaler_path)
    with open(config_path, 'r') as f:
        config = json.load(f)

    feature_names = config['feature_names']

    # Map Resisto columns
    df_resisto['temperature'] = df_resisto['temperature_c']
    df_resisto['humidity'] = df_resisto['humidity_percent']
    df_resisto['pressure'] = df_resisto['air_pressure_pa'] / 100.0 # Pa to hPa

    # Map ground truth: 0 = Normal (0), 1 (Pre-alert) & 2 (Fire alert) = Fire (1)
    df_resisto['binary_target'] = (df_resisto['fire_alert_status'] > 0).astype(int)

    # Sort by site and time
    df_resisto['time_dt'] = pd.to_datetime(df_resisto['time'], utc=True)
    df_resisto.sort_values(by=['site_id', 'time_dt'], inplace=True)
    df_resisto.reset_index(drop=True, inplace=True)

    # Fill missing sensor proxies with scaler training means
    mean_map = dict(zip(feature_names, scaler.mean_))

    X_resisto = pd.DataFrame(index=df_resisto.index)

    for col in feature_names:
        if col in df_resisto.columns:
            X_resisto[col] = df_resisto[col]
        elif 'temperature' in col and col.startswith('temperature_'):
            suffix = col.replace('temperature_', '')
            if suffix.startswith('delta_'):
                step = int(suffix.split('_')[1])
                X_resisto[col] = df_resisto.groupby('site_id')['temperature'].diff(step).fillna(0)
            elif suffix == 'rate':
                X_resisto[col] = (df_resisto.groupby('site_id')['temperature'].diff(1) / (df_resisto['temperature'].abs() + 1e-6)).fillna(0)
            else:
                X_resisto[col] = mean_map.get(col, 0.0)
        elif 'humidity' in col and col.startswith('humidity_'):
            suffix = col.replace('humidity_', '')
            if suffix.startswith('delta_'):
                step = int(suffix.split('_')[1])
                X_resisto[col] = df_resisto.groupby('site_id')['humidity'].diff(step).fillna(0)
            elif suffix == 'rate':
                X_resisto[col] = (df_resisto.groupby('site_id')['humidity'].diff(1) / (df_resisto['humidity'].abs() + 1e-6)).fillna(0)
            else:
                X_resisto[col] = mean_map.get(col, 0.0)
        elif 'pressure' in col and col.startswith('pressure_'):
            suffix = col.replace('pressure_', '')
            if suffix.startswith('delta_'):
                step = int(suffix.split('_')[1])
                X_resisto[col] = df_resisto.groupby('site_id')['pressure'].diff(step).fillna(0)
            elif suffix == 'rate':
                X_resisto[col] = (df_resisto.groupby('site_id')['pressure'].diff(1) / (df_resisto['pressure'].abs() + 1e-6)).fillna(0)
            else:
                X_resisto[col] = mean_map.get(col, 0.0)
        else:
            # Missing sensor proxy (e.g. PM2.5 or TVOC in Resisto) -> default to training mean
            X_resisto[col] = mean_map.get(col, 0.0)

    # Ensure feature column order matches exact training vector
    X_resisto = X_resisto[feature_names]

    # Transform using trained scaler
    X_resisto_scaled = scaler.transform(X_resisto)

    # Predict on Resisto
    print("Evaluating baseline Random Forest model on Resisto OOD dataset...")
    y_pred = rf_model.predict(X_resisto_scaled)
    y_true = df_resisto['binary_target']

    acc = accuracy_score(y_true, y_pred)
    prec = precision_score(y_true, y_pred, zero_division=0)
    rec = recall_score(y_true, y_pred, zero_division=0)
    f1 = f1_score(y_true, y_pred, zero_division=0)
    cm = confusion_matrix(y_true, y_pred)

    print("-" * 45)
    print("PHASE 5: RESISTO OUT-OF-DISTRIBUTION VALIDATION RESULTS")
    print("-" * 45)
    print(f"Accuracy:        {acc:.4f}")
    print(f"Precision:       {prec:.4f}")
    print(f"Recall (Fire):   {rec:.4f}")
    print(f"F1-Score:        {f1:.4f}")
    print("\nConfusion Matrix:")
    print(cm)
    print("-" * 45)

    # Breakdown by Resisto specific status codes
    status_0_mask = (df_resisto['fire_alert_status'] == 0)
    status_1_mask = (df_resisto['fire_alert_status'] == 1)
    status_2_mask = (df_resisto['fire_alert_status'] == 2)

    acc_0 = accuracy_score(y_true[status_0_mask], y_pred[status_0_mask])
    rec_1 = recall_score(y_true[status_1_mask], y_pred[status_1_mask], zero_division=0) if status_1_mask.sum() > 0 else 0.0
    rec_2 = recall_score(y_true[status_2_mask], y_pred[status_2_mask], zero_division=0) if status_2_mask.sum() > 0 else 0.0

    print(f"Specificity on Normal (Status 0):     {acc_0:.4f}")
    print(f"Recall on Pre-Alert (Status 1):       {rec_1:.4f} (Count: {status_1_mask.sum()})")
    print(f"Recall on Fire Alert (Status 2):      {rec_2:.4f} (Count: {status_2_mask.sum()})")

    # Write Markdown Report
    with open(report_path, 'w', encoding='utf-8') as f:
        f.write("# Phase 5: Resisto Out-of-Distribution Validation Report\n\n")
        f.write("## Overview\n")
        f.write(f"- **Dataset File:** `forest_fire_resisto_raw.csv.csv`\n")
        f.write(f"- **Total OOD Samples Tested:** `{len(df_resisto):,}` real-world European forest fire sensor records.\n\n")
        f.write("## Overall Binary Evaluation (Fire vs Normal)\n")
        f.write(f"- **Accuracy:** `{acc:.4f}`\n")
        f.write(f"- **Precision:** `{prec:.4f}`\n")
        f.write(f"- **Recall (Fire Alerts):** `{rec:.4f}`\n")
        f.write(f"- **F1-Score:** `{f1:.4f}`\n\n")
        f.write("## Detailed Breakdown by Resisto Alert Status\n")
        f.write(f"- **Status 0 (No Alert - 496,789 samples):** Normal Specificity = `{acc_0:.4f}`\n")
        f.write(f"- **Status 1 (Pre-Alert - 4 samples):** Pre-Alert Recall = `{rec_1:.4f}`\n")
        f.write(f"- **Status 2 (Fire Alert - 956 samples):** Fire Alert Recall = `{rec_2:.4f}`\n\n")
        f.write("## Confusion Matrix\n```text\n")
        f.write(str(cm))
        f.write("\n```\n")

    print("Phase 5 Resisto validation complete!")

if __name__ == '__main__':
    validate_on_resisto()
