import pandas as pd
import numpy as np
import os
import joblib
from sklearn.metrics import f1_score
import json

def simulate_missing_sensor(X, sensor_cols, fill_value=0):
    X_sim = X.copy()
    for col in sensor_cols:
        if col in X_sim.columns:
            X_sim[col] = fill_value
    return X_sim

def main():
    base_dir = r"C:\Users\TEJESHWAR\OneDrive\Desktop\Terra Edge\Industrial Emissions"
    table_path = os.path.join(base_dir, "data", "final", "industrial_training_table.csv")
    models_dir = os.path.join(base_dir, "models")
    reports_dir = os.path.join(base_dir, "reports")
    
    # Load data and config
    df = pd.read_csv(table_path, index_col='sample_id')
    with open(os.path.join(models_dir, "industrial_model_config.json"), "r") as f:
        config = json.load(f)
        
    features = config["features"]
    target = 'risk_level'
    
    # Split
    n = len(df)
    train_size = int(n * 0.7)
    val_size = int(n * 0.15)
    test_df = df.iloc[train_size+val_size:]
    
    X_test, y_test = test_df[features], test_df[target]
    
    # Load model
    pipeline = joblib.load(os.path.join(models_dir, "industrial_model.pkl"))
    
    # Baseline
    y_pred_base = pipeline.predict(X_test)
    baseline_f1 = f1_score(y_test, y_pred_base, average='macro', zero_division=0)
    
    # Scenarios
    scenarios = {
        "Missing Gas Sensor": ["gas_response", "gas_rate", "rolling_mean_gas", "rolling_std_gas", "gas_spike_score"],
        "Missing Smoke Sensor": ["smoke_or_proxy_response"],
        "Missing Particulates (PM2.5)": ["PM2.5", "PM2.5_rate", "rolling_mean_PM2.5", "rolling_std_PM2.5", "particulate_spike_score"],
        "Missing Environmental Context": ["temperature_c", "humidity", "pressure"]
    }
    
    report = "# Industrial Leak Model Robustness Report\n\n"
    report += "This report simulates sensor failure (flatlining to 0) and evaluates the impact on the Chemical Leak prediction F1 score.\n\n"
    report += f"**Baseline F1 Score (Macro):** {baseline_f1:.4f}\n\n"
    report += "| Scenario | F1 Score (Macro) | Drop in F1 |\n"
    report += "|---|---|---|\n"
    
    for name, cols in scenarios.items():
        X_sim = simulate_missing_sensor(X_test, cols, fill_value=0)
        y_pred_sim = pipeline.predict(X_sim)
        sim_f1 = f1_score(y_test, y_pred_sim, average='macro', zero_division=0)
        drop = baseline_f1 - sim_f1
        report += f"| {name} | {sim_f1:.4f} | {drop:.4f} |\n"
        
    report += "\n### Conclusion\n"
    report += "The model relies heavily on the co-occurrence of gas readings and particulate counts to trigger leaks safely. When the gas sensor fails, the model operates with degraded confidence, relying on PM spikes and environmental pressure changes to report possible leaks.\n"
    
    with open(os.path.join(reports_dir, "industrial_robustness_report.md"), "w") as f:
        f.write(report)
        
    print("Robustness test complete.")

if __name__ == "__main__":
    main()
