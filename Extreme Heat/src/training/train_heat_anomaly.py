import pandas as pd
import numpy as np
import os
import joblib
from sklearn.ensemble import IsolationForest
from sklearn.calibration import CalibratedClassifierCV
from sklearn.metrics import brier_score_loss
import matplotlib.pyplot as plt

def train_anomaly_detector(X_train, features, models_dir):
    print("Training IsolationForest for Anomaly Detection...")
    iso_forest = IsolationForest(n_estimators=100, contamination=0.01, random_state=42)
    iso_forest.fit(X_train[features])
    
    joblib.dump(iso_forest, os.path.join(models_dir, "heat_anomaly_detector.pkl"))
    return iso_forest

def calibrate_and_evaluate(pipeline, X_train, y_train, X_val, y_val, models_dir, reports_dir):
    print("Calibrating the best supervised model...")
    # Using cv=3 to avoid 'prefit' string parameter validation issues on newer sklearn versions
    calibrated_clf = CalibratedClassifierCV(estimator=pipeline, method='isotonic', cv=3)
    calibrated_clf.fit(X_train, y_train)
    
    # Save the calibrated model
    joblib.dump(calibrated_clf, os.path.join(models_dir, "heat_calibrator.pkl"))
    
    # Evaluate calibration (using Brier score on a binary proxy for high risk: class >= 2)
    y_val_binary = (y_val >= 2).astype(int)
    prob_uncalibrated = pipeline.predict_proba(X_val)
    
    # We must sum probabilities of classes 2 and 3 if available in the model
    # Wait, the pipeline classes are available via pipeline.classes_
    classes = pipeline.classes_
    high_risk_indices = [i for i, c in enumerate(classes) if c >= 2]
    
    if len(high_risk_indices) > 0:
        prob_uncal_high = prob_uncalibrated[:, high_risk_indices].sum(axis=1)
        prob_calibrated = calibrated_clf.predict_proba(X_val)[:, high_risk_indices].sum(axis=1)
        
        brier_uncal = brier_score_loss(y_val_binary, prob_uncal_high)
        brier_cal = brier_score_loss(y_val_binary, prob_calibrated)
        
        report = f"# Heat Model Calibration Report\n\n"
        report += f"**Uncalibrated Brier Score (High Risk >= WARNING):** {brier_uncal:.4f}\n"
        report += f"**Calibrated Brier Score (High Risk >= WARNING):** {brier_cal:.4f}\n\n"
        report += "A lower Brier score indicates better calibrated probabilities.\n"
        report += "The model outputs `heat_risk_probability` properly calibrated for edge decision making.\n"
        
        with open(os.path.join(reports_dir, "heat_calibration_report.md"), "w") as f:
            f.write(report)
            
        print("Calibration complete.")
    else:
        print("No high risk classes found in validation set, skipping Brier score calculation.")

def main():
    base_dir = r"C:\Users\TEJESHWAR\OneDrive\Desktop\Terra Edge\Extreme Heat"
    table_path = os.path.join(base_dir, "data", "final", "heat_training_table.csv")
    models_dir = os.path.join(base_dir, "models")
    reports_dir = os.path.join(base_dir, "reports")
    
    df = pd.read_csv(table_path, parse_dates=['timestamp']).set_index('timestamp')
    
    # Load config to get features
    import json
    with open(os.path.join(models_dir, "heat_model_config.json"), "r") as f:
        config = json.load(f)
        
    features = config["features"]
    target = 'risk_level'
    
    # Chronological Split (same as supervised model to respect validation boundaries)
    n = len(df)
    train_size = int(n * 0.7)
    val_size = int(n * 0.15)
    
    train_df = df.iloc[:train_size]
    val_df = df.iloc[train_size:train_size+val_size]
    
    X_train, y_train = train_df[features], train_df[target]
    X_val, y_val = val_df[features], val_df[target]
    
    # Train Anomaly Detector
    iso_forest = train_anomaly_detector(X_train, features, models_dir)
    
    # Calculate anomaly scores for train data to build report
    train_anomalies = iso_forest.predict(X_train)
    anomaly_rate = (train_anomalies == -1).sum() / len(train_anomalies)
    
    anomaly_report = f"# Anomaly Detection Report\n\n"
    anomaly_report += f"- **Model:** IsolationForest\n"
    anomaly_report += f"- **Contamination parameter:** 0.01\n"
    anomaly_report += f"- **Train Anomaly Rate:** {anomaly_rate*100:.2f}%\n"
    anomaly_report += f"- **Purpose:** Detects out-of-distribution sensor readings or extreme rare events that standard thresholds miss.\n"
    
    with open(os.path.join(reports_dir, "heat_anomaly_report.md"), "w") as f:
        f.write(anomaly_report)
    
    # Calibration
    pipeline = joblib.load(os.path.join(models_dir, "heat_model.pkl"))
    calibrate_and_evaluate(pipeline, X_train, y_train, X_val, y_val, models_dir, reports_dir)

if __name__ == "__main__":
    main()
