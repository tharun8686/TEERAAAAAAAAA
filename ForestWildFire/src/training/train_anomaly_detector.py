import pandas as pd
import numpy as np
import os
import joblib
from sklearn.preprocessing import StandardScaler
from sklearn.ensemble import IsolationForest
from sklearn.metrics import roc_auc_score, classification_report, confusion_matrix

def train_anomaly_detector():
    base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    features_path = os.path.join(base_dir, 'data', 'intermediate', 'fire_features.csv')
    models_dir = os.path.join(base_dir, 'models')
    reports_dir = os.path.join(base_dir, 'reports')

    print("Loading engineered features dataset...")
    df = pd.read_csv(features_path)

    # Sort chronologically
    df.sort_values(by='timestamp', inplace=True)
    df.reset_index(drop=True, inplace=True)

    X = df.drop(columns=['timestamp', 'fire_alarm'])
    y = df['fire_alarm']

    # Chronological Split (matching Phase 3 Episode-based split)
    train_end = 24994
    val_end = 43812

    X_train, y_train = X.iloc[:train_end], y.iloc[:train_end]
    X_test, y_test = X.iloc[val_end:], y.iloc[val_end:]

    # Filter ONLY normal fire-free samples from training set
    X_train_normal = X_train[y_train == 0]
    print(f"Training Isolation Forest strictly on Normal fire-free data ({len(X_train_normal)} samples)...")

    # Fit scaler on normal training data
    scaler = StandardScaler()
    X_train_normal_scaled = scaler.fit_transform(X_train_normal)
    X_test_scaled = scaler.transform(X_test)

    # Train Isolation Forest with auto contamination
    iso_forest = IsolationForest(
        n_estimators=200,
        contamination='auto',
        random_state=42,
        n_jobs=-1
    )
    iso_forest.fit(X_train_normal_scaled)

    # Evaluate on Test Set
    # score_samples returns opposite of anomaly score (lower value = more abnormal)
    scores = -iso_forest.score_samples(X_test_scaled)
    raw_preds = iso_forest.predict(X_test_scaled)
    pred_anomalies = (raw_preds == -1).astype(int)

    auc_score = roc_auc_score(y_test, scores)
    cm = confusion_matrix(y_test, pred_anomalies)

    print("-" * 45)
    print("PHASE 4: ISOLATION FOREST ANOMALY DETECTOR RESULTS")
    print("-" * 45)
    print(f"ROC-AUC Anomaly Score: {auc_score:.4f}")
    print("\nConfusion Matrix (Ground Truth Fire vs Predicted Anomaly):")
    print(cm)
    print("\nClassification Report:")
    print(classification_report(y_test, pred_anomalies, target_names=['Normal', 'Abnormal/Fire'], zero_division=0))
    print("-" * 45)

    # Save Anomaly Model
    model_path = os.path.join(models_dir, 'fire_anomaly_model.pkl')
    joblib.dump(iso_forest, model_path)

    # Save Anomaly Report
    report_path = os.path.join(reports_dir, 'fire_anomaly_report.md')
    with open(report_path, 'w', encoding='utf-8') as f:
        f.write("# Phase 4: Isolation Forest Anomaly Detector Report\n\n")
        f.write("## Overview\n")
        f.write(f"- **Training Dataset:** Trained strictly on `{len(X_train_normal):,}` Normal (`fire_alarm == 0`) baseline samples.\n")
        f.write(f"- **Test Set Evaluation:** Tested on `{len(X_test):,}` unseen chronological samples.\n")
        f.write(f"- **ROC-AUC Anomaly Score:** `{auc_score:.4f}`\n\n")
        f.write("## Confusion Matrix (Normal vs Abnormal State)\n")
        f.write(f"```text\n{cm}\n```\n\n")
        f.write("## Classification Report\n")
        f.write(f"```text\n{classification_report(y_test, pred_anomalies, target_names=['Normal', 'Abnormal/Fire'], zero_division=0)}\n```\n")

    print("Phase 4 anomaly detector training complete!")

if __name__ == '__main__':
    train_anomaly_detector()
