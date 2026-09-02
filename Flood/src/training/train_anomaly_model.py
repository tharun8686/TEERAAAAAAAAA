import pandas as pd
import numpy as np
import os
import joblib
from sklearn.ensemble import IsolationForest
from sklearn.metrics import classification_report, roc_auc_score, confusion_matrix
from sklearn.impute import SimpleImputer
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler

def train_anomaly_model():
    base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    data_path = os.path.join(base_dir, 'data', 'intermediate', 'continuous_telemetry.csv')
    model_path = os.path.join(base_dir, 'models', 'anomaly_model_v1.pkl')

    print("Loading continuous telemetry dataset...")
    df = pd.read_csv(data_path)

    # Candidate input features for anomaly detection
    feature_cols = [
        'rain_1h', 'rain_3h', 'rain_6h', 'rain_24h',
        'water_level_m', 'streamflow_cumec', 'soil_moisture_pct',
        'temperature_c', 'humidity_pct'
    ]

    X = df[feature_cols].copy()
    y_true = df['is_anomaly']

    print(f"Training Isolation Forest model on {len(X)} records...")

    # Pipeline: Impute -> Scale -> Isolation Forest
    pipeline = Pipeline(steps=[
        ('imputer', SimpleImputer(strategy='median')),
        ('scaler', StandardScaler()),
        ('model', IsolationForest(
            n_estimators=150,
            contamination=0.18, # tuned based on baseline anomaly ratio (~18%)
            random_state=42,
            n_jobs=-1
        ))
    ])

    # Fit pipeline
    pipeline.fit(X)

    # Predict: IsolationForest outputs 1 for inliers (normal) and -1 for outliers (anomalies)
    preds_raw = pipeline.predict(X)
    y_pred_anomaly = (preds_raw == -1).astype(int)

    # Calculate continuous anomaly scores (higher score = more anomalous)
    # IsolationForest decision_function returns negative values for anomalies
    scores = -pipeline.named_steps['model'].decision_function(pipeline.named_steps['scaler'].transform(pipeline.named_steps['imputer'].transform(X)))

    print("-" * 30)
    print("ISOLATION FOREST ANOMALY MODEL EVALUATION")
    print("-" * 30)
    auc = roc_auc_score(y_true, scores)
    print(f"ROC-AUC Anomaly Score: {auc:.4f}")
    print("\nConfusion Matrix (Ground Truth Anomaly vs Predicted Anomaly):")
    print(confusion_matrix(y_true, y_pred_anomaly))
    print("\nClassification Report:")
    print(classification_report(y_true, y_pred_anomaly, target_names=['Normal', 'Abnormal/Flood']))

    print(f"Saving Anomaly Model to {model_path}...")
    joblib.dump(pipeline, model_path)
    print("Done training Anomaly Model!")

if __name__ == '__main__':
    train_anomaly_model()
