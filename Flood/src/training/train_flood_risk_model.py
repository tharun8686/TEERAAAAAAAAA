import pandas as pd
import numpy as np
import os
import joblib
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report, accuracy_score
from sklearn.model_selection import train_test_split

def train_risk_model():
    base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    data_path = os.path.join(base_dir, 'data', 'intermediate', 'continuous_telemetry.csv')
    anomaly_model_path = os.path.join(base_dir, 'models', 'anomaly_model_v1.pkl')
    risk_model_path = os.path.join(base_dir, 'models', 'flood_risk_model_v1.pkl')

    print("Loading continuous telemetry dataset...")
    df = pd.read_csv(data_path)

    print("Loading Anomaly Model to calculate anomaly scores...")
    anomaly_pipeline = joblib.load(anomaly_model_path)
    
    anomaly_features = [
        'rain_1h', 'rain_3h', 'rain_6h', 'rain_24h',
        'water_level_m', 'streamflow_cumec', 'soil_moisture_pct',
        'temperature_c', 'humidity_pct'
    ]
    
    # Calculate anomaly score feature
    X_anomaly = df[anomaly_features]
    df['anomaly_score'] = -anomaly_pipeline.named_steps['model'].decision_function(
        anomaly_pipeline.named_steps['scaler'].transform(
            anomaly_pipeline.named_steps['imputer'].transform(X_anomaly)
        )
    )

    # Define Risk Severity Target based on physical thresholds:
    # 0 = Normal (< 2.5m water level, rain_24h < 30mm)
    # 1 = Watch (2.5m - 3.8m water level OR rain_24h 30-60mm)
    # 2 = Warning (3.8m - 5.0m water level OR rain_24h 60-100mm)
    # 3 = Critical (> 5.0m water level OR rain_24h > 100mm)
    conditions = [
        (df['water_level_m'] > 5.0) | (df['rain_24h'] > 100.0),
        (df['water_level_m'] > 3.8) | (df['rain_24h'] > 60.0),
        (df['water_level_m'] > 2.5) | (df['rain_24h'] > 30.0)
    ]
    choices = [3, 2, 1] # 3: Critical, 2: Warning, 1: Watch
    df['risk_class'] = np.select(conditions, choices, default=0) # 0: Normal

    features = [
        'anomaly_score', 'rain_1h', 'rain_3h', 'rain_6h', 'rain_24h', 'rain_72h',
        'water_level_m', 'streamflow_cumec', 'soil_moisture_pct',
        'temperature_c', 'humidity_pct'
    ]

    X = df[features]
    y = df['risk_class']

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)

    print(f"Training Flood Risk Classifier on {len(X_train)} samples...")
    model = RandomForestClassifier(n_estimators=150, max_depth=12, random_state=42, n_jobs=-1)
    model.fit(X_train, y_train)

    y_pred = model.predict(X_test)
    print("-" * 30)
    print("FLOOD RISK CLASSIFIER EVALUATION")
    print("-" * 30)
    print(f"Accuracy: {accuracy_score(y_test, y_pred):.4f}")
    print("\nClassification Report:")
    print(classification_report(y_test, y_pred, target_names=['Normal', 'Watch', 'Warning', 'Critical']))

    print(f"Saving Flood Risk Model to {risk_model_path}...")
    joblib.dump(model, risk_model_path)
    print("Done training Flood Risk Model!")

if __name__ == '__main__':
    train_risk_model()
