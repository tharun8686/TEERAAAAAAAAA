import os
import joblib
import pandas as pd

def demonstrate_trained_models():
    base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    models_dir = os.path.join(base_dir, 'models')

    print("=" * 60)
    print("      SENTINLEDGE AI - TRAINED MODEL VERIFICATION")
    print("=" * 60)

    model_files = [
        ('Flood Severity Model (Model A)', 'severity_model_v1.pkl'),
        ('Flood Anomaly Detector (Isolation Forest)', 'anomaly_model_v1.pkl'),
        ('Early Warning Flood Risk Classifier', 'flood_risk_model_v1.pkl')
    ]

    for name, filename in model_files:
        path = os.path.join(models_dir, filename)
        if os.path.exists(path):
            size_mb = os.path.getsize(path) / (1024 * 1024)
            model_obj = joblib.load(path)
            print(f"\n[SUCCESS] {name}")
            print(f"  |-- Saved File: {filename}")
            print(f"  |-- File Size:  {size_mb:.2f} MB")
            print(f"  |-- Architecture: {type(model_obj).__name__}")
        else:
            print(f"\n[MISSING] {name} - Not found at {filename}")

    print("\n" + "=" * 60)
    print("  LIVE INFERENCE TEST SAMPLE")
    print("=" * 60)
    
    risk_model_path = os.path.join(models_dir, 'flood_risk_model_v1.pkl')
    if os.path.exists(risk_model_path):
        rf_model = joblib.load(risk_model_path)
        # Sample test input: High rain, high water level
        sample_input = pd.DataFrame([{
            'anomaly_score': 0.85, 'rain_1h': 45.0, 'rain_3h': 85.0, 'rain_6h': 110.0,
            'rain_24h': 145.0, 'rain_72h': 190.0, 'water_level_m': 5.8, 'streamflow_cumec': 450.0,
            'soil_moisture_pct': 88.0, 'temperature_c': 24.5, 'humidity_pct': 92.0
        }])

        pred_class = rf_model.predict(sample_input)[0]
        class_names = {0: 'NORMAL', 1: 'WATCH', 2: 'WARNING', 3: 'CRITICAL'}
        print(f"  Input Scenario: Extreme Rainfall (145mm/24h) & High River Stage (5.8m)")
        print(f"  Model Prediction Output: {class_names.get(pred_class, 'UNKNOWN')}")
        print("=" * 60)

if __name__ == '__main__':
    demonstrate_trained_models()
