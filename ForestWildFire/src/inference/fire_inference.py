import pandas as pd
import numpy as np
import os
import joblib
import json

class FireInferenceEngine:
    def __init__(self):
        base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        models_dir = os.path.join(base_dir, 'models')

        self.model_path = os.path.join(models_dir, 'fire_compact_model.pkl')
        self.scaler_path = os.path.join(models_dir, 'fire_compact_scaler.pkl')
        self.anomaly_path = os.path.join(models_dir, 'fire_anomaly_model.pkl')
        self.config_path = os.path.join(models_dir, 'fire_compact_config.json')

        self.model = joblib.load(self.model_path)
        self.scaler = joblib.load(self.scaler_path)
        self.anomaly_model = joblib.load(self.anomaly_path)

        with open(self.config_path, 'r') as f:
            self.config = json.load(f)

        self.features = self.config['selected_features']

    def predict_fire(self, sensor_window: dict) -> dict:
        """
        Executes fire hazard inference on recent sensor window.
        Input sensor_window expects keys:
        temperature, humidity, pressure, pm25, tvoc, raw_ethanol,
        temperature_rate, humidity_rate, pm25_rate, tvoc_rate,
        temperature_delta_5, humidity_delta_5
        """
        missing_count = 0
        feature_vector = []

        mean_map = dict(zip(self.features, self.scaler.mean_))

        for feat in self.features:
            val = sensor_window.get(feat, None)
            if val is None or np.isnan(val):
                missing_count += 1
                val = mean_map.get(feat, 0.0) # Impute with baseline mean
            feature_vector.append(val)

        # Build DataFrame & Scale
        df_feat = pd.DataFrame([feature_vector], columns=self.features)
        scaled_feat = self.scaler.transform(df_feat)

        # Raw Model Probability
        raw_prob = self.model.predict_proba(scaled_feat)[0][1]

        # Trend rates
        pm25_rate = sensor_window.get("pm25_rate") or 0.0
        tvoc_rate = sensor_window.get("tvoc_rate") or 0.0
        temp_rate = sensor_window.get("temperature_rate") or 0.0

        # Anomaly score calculation
        anomaly_val = float(raw_prob * 1.1 + max(0, pm25_rate * 0.2))

        # Confidence Calibration (Degrades gracefully if sensors are missing)
        base_confidence = 0.95
        confidence = max(0.40, base_confidence - (missing_count * 0.15))

        # Severity Mapping Policy:
        # Incorporates model probability, anomaly score, and rate-of-change trend indicators
        if raw_prob >= 0.85 or (raw_prob >= 0.35 and (pm25_rate > 1.0 or anomaly_val > 0.60)):
            severity = "CRITICAL"
        elif raw_prob >= 0.65 or (raw_prob >= 0.35 and (pm25_rate > 0.5 or temp_rate > 0.1)):
            severity = "WARNING"
        elif raw_prob >= 0.30 and (pm25_rate > 0.2 or tvoc_rate > 0.2 or temp_rate > 0.05):
            severity = "WATCH"
        else:
            severity = "NORMAL"

        # Identify top contributing trend features
        rates = {
            "pm25_rate": pm25_rate,
            "humidity_rate": sensor_window.get("humidity_rate") or 0.0,
            "tvoc_rate": tvoc_rate,
            "temperature_rate": temp_rate
        }
        sorted_rates = sorted(rates.items(), key=lambda x: abs(x[1]), reverse=True)
        top_features = [k for k, v in sorted_rates[:3] if abs(v) > 0]
        if not top_features:
            top_features = ["humidity", "temperature", "pm25"]

        return {
            "hazard": "forest_fire",
            "fire_probability": round(float(raw_prob), 2),
            "confidence": round(float(confidence), 2),
            "severity": severity,
            "anomaly_score": round(float(anomaly_val), 2),
            "top_features": top_features
        }

if __name__ == '__main__':
    engine = FireInferenceEngine()
    test_sample = {
        'temperature': 45.0, 'humidity': 25.0, 'pressure': 1005.0,
        'pm25': 350.0, 'tvoc': 1500.0, 'raw_ethanol': 3200.0,
        'temperature_rate': 0.15, 'humidity_rate': -0.20, 'pm25_rate': 0.85, 'tvoc_rate': 0.60,
        'temperature_delta_5': 4.5, 'humidity_delta_5': -8.0
    }
    result = engine.predict_fire(test_sample)
    print(json.dumps(result, indent=2))
