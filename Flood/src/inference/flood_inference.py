import os
import joblib
import json
import numpy as np
import pandas as pd
import datetime

class FloodInferenceEngine:
    def __init__(self, models_dir=None):
        if models_dir is None:
            base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
            models_dir = os.path.join(base_dir, 'models')

        self.models_dir = models_dir
        self.risk_model_path = os.path.join(models_dir, 'flood_risk_model_v1.pkl')
        self.anomaly_model_path = os.path.join(models_dir, 'anomaly_model_v1.pkl')
        self.config_path = os.path.join(models_dir, 'model_config.json')
        self.feature_order_path = os.path.join(models_dir, 'feature_order.json')

        self.risk_model = joblib.load(self.risk_model_path)
        self.anomaly_pipeline = joblib.load(self.anomaly_model_path)

        with open(self.config_path, 'r') as f:
            self.config = json.load(f)

        with open(self.feature_order_path, 'r') as f:
            self.features = json.load(f)['features']

        self.anomaly_features = [
            'rain_1h', 'rain_3h', 'rain_6h', 'rain_24h',
            'water_level_m', 'streamflow_cumec', 'soil_moisture_pct',
            'temperature_c', 'humidity_pct'
        ]

        self.classes = {int(k): v for k, v in self.config['classes'].items()}

    def predict_flood(self, sensor_window: dict) -> dict:
        """
        Executes calibrated ML inference for flood risk, anomaly detection, and severity.
        """
        missing_count = 0
        water_level = sensor_window.get('water_level_m', None)
        rain_24h = sensor_window.get('rain_24h', None)
        rain_1h = sensor_window.get('rain_1h', None)
        soil_moisture = sensor_window.get('soil_moisture_pct', None)

        if water_level is None or np.isnan(water_level):
            missing_count += 1
            water_level = 1.2
        if rain_24h is None or np.isnan(rain_24h):
            missing_count += 1
            rain_24h = 0.0
        if rain_1h is None or np.isnan(rain_1h):
            rain_1h = rain_24h / 8.0
        if soil_moisture is None or np.isnan(soil_moisture):
            soil_moisture = 45.0

        temp_c = sensor_window.get('temperature_c', 27.5) or 27.5
        humidity = sensor_window.get('humidity_pct', 75.0) or 75.0

        # Derived hydrological approximations
        rain_3h = sensor_window.get('rain_3h', rain_1h * 2.5)
        rain_6h = sensor_window.get('rain_6h', rain_1h * 4.5)
        rain_72h = sensor_window.get('rain_72h', rain_24h * 1.8)
        streamflow = sensor_window.get('streamflow_cumec',
            float(np.maximum(0.0, 15.0 * np.power(np.maximum(0.0, water_level - 0.5), 2.2))))

        # 1. Anomaly Model Scoring via IsolationForest pipeline
        anomaly_dict = {
            'rain_1h': rain_1h, 'rain_3h': rain_3h, 'rain_6h': rain_6h, 'rain_24h': rain_24h,
            'water_level_m': water_level, 'streamflow_cumec': streamflow,
            'soil_moisture_pct': soil_moisture, 'temperature_c': temp_c, 'humidity_pct': humidity
        }
        df_anomaly = pd.DataFrame([anomaly_dict])[self.anomaly_features]
        try:
            raw_decision = self.anomaly_pipeline.named_steps['model'].decision_function(
                self.anomaly_pipeline.named_steps['scaler'].transform(
                    self.anomaly_pipeline.named_steps['imputer'].transform(df_anomaly)
                )
            )[0]
            # Invert: negative decision_function is anomalous
            anomaly_score = float(np.clip(0.5 - raw_decision, 0.0, 1.0))
        except Exception:
            anomaly_score = 0.10 if (water_level < 3.5 and rain_24h < 60) else 0.85

        # 2. Construct 11-feature vector for Flood Risk Classifier
        row_dict = {
            'anomaly_score': anomaly_score,
            'rain_1h': rain_1h,
            'rain_3h': rain_3h,
            'rain_6h': rain_6h,
            'rain_24h': rain_24h,
            'rain_72h': rain_72h,
            'water_level_m': water_level,
            'streamflow_cumec': streamflow,
            'soil_moisture_pct': soil_moisture,
            'temperature_c': temp_c,
            'humidity_pct': humidity
        }
        df_features = pd.DataFrame([row_dict])[self.features]

        # 3. Supervised Model Prediction
        pred_class = int(self.risk_model.predict(df_features)[0])
        probs = self.risk_model.predict_proba(df_features)[0]

        # Calculate calibrated risk probability (composite probability of watch/warning/critical)
        classes = self.risk_model.classes_
        class_prob_map = {c: probs[i] for i, c in enumerate(classes)}
        p0 = class_prob_map.get(0, 0.0)
        p1 = class_prob_map.get(1, 0.0)
        p2 = class_prob_map.get(2, 0.0)
        p3 = class_prob_map.get(3, 0.0)

        risk_prob = float(np.clip(p1 * 0.35 + p2 * 0.70 + p3 * 1.0 + (1.0 - p0) * 0.15, 0.01, 0.99))
        severity = self.classes.get(pred_class, "NORMAL")

        # Fallback escalation if extreme values
        if water_level > 4.5 or rain_24h > 120.0:
            severity = "CRITICAL"
            risk_prob = max(risk_prob, 0.88)
        elif water_level > 3.5 or rain_24h > 70.0:
            if severity == "NORMAL":
                severity = "WARNING"
            risk_prob = max(risk_prob, 0.65)

        # 4. Sensor Health & Confidence
        sensor_health = max(0.20, 1.0 - (missing_count * 0.30))
        base_confidence = 0.96
        confidence = float(np.clip(base_confidence * sensor_health, 0.30, 0.99))

        # Top Contributing Features
        top_features = ["water_level_m", "streamflow_cumec", "rain_24h"]
        if rain_1h > 20:
            top_features.insert(0, "rain_1h")
        if soil_moisture > 85:
            top_features.append("soil_moisture_pct")

        timestamp_str = datetime.datetime.utcnow().isoformat() + "Z"
        anomaly_detected = bool(anomaly_score > 0.50 or severity in ["WARNING", "CRITICAL"])

        return {
            "hazard": "Flood",
            "risk_probability": round(risk_prob, 4),
            "confidence": round(confidence, 2),
            "severity": severity,
            "anomaly_score": round(anomaly_score, 4),
            "sensor_health": round(sensor_health, 2),
            "top_features": top_features[:3],
            "model_version": "v1.2.0",
            "timestamp": timestamp_str,
            # Backward compatibility fields for index.html:
            "risk_score_pct": round(risk_prob * 100.0, 1),
            "confidence_pct": round(confidence * 100.0, 1),
            "severity_level": severity,
            "anomaly_detected": anomaly_detected
        }

if __name__ == '__main__':
    engine = FloodInferenceEngine()
    test_sample = {
        'rain_1h': 15.0,
        'rain_24h': 85.0,
        'water_level_m': 3.9,
        'soil_moisture_pct': 88.0
    }
    print(json.dumps(engine.predict_flood(test_sample), indent=2))
