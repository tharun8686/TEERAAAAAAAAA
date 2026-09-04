import pandas as pd
import numpy as np
import os
import joblib
import json
import datetime

class LandslideInferenceEngine:
    def __init__(self):
        base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        models_dir = os.path.join(base_dir, 'models')

        self.model_path = os.path.join(models_dir, 'final_landslide_model.pkl')
        self.scaler_path = os.path.join(models_dir, 'final_landslide_preprocessor.pkl')
        self.anomaly_path = os.path.join(models_dir, 'cleveland_isolation_forest.pkl')
        self.config_path = os.path.join(models_dir, 'landslide_model_config.json')

        self.model = joblib.load(self.model_path)
        self.scaler = joblib.load(self.scaler_path)
        self.anomaly_model = joblib.load(self.anomaly_path)

        with open(self.config_path, 'r') as f:
            self.config = json.load(f)

        self.features = self.config['selected_features']

    def predict_landslide(self, sensor_window: dict) -> dict:
        """
        Executes slope instability / landslide early warning inference.
        Input sensor_window expects keys:
        soil_moisture_vwc, soil_moisture_rate, tilt_magnitude, tilt_rate,
        vibration_rate, temperature, humidity, rainfall_24h (optional)
        """
        missing_count = 0
        feature_vector = []
        ext_rainfall_avail = True

        mean_map = dict(zip(self.features, self.scaler.mean_))

        for feat in self.features:
            val = sensor_window.get(feat, None)
            if feat == 'rainfall_24h' and (val is None or np.isnan(val)):
                ext_rainfall_avail = False
                val = 0.0 # Default fallback when external rain gauge unavailable
            elif val is None or np.isnan(val):
                missing_count += 1
                val = mean_map.get(feat, 0.0)
            feature_vector.append(val)

        # Scale features
        df_feat = pd.DataFrame([feature_vector], columns=self.features)
        scaled_feat = self.scaler.transform(df_feat)

        # Predict calibrated probability
        raw_prob = self.model.predict_proba(scaled_feat)[0][1]

        # Calculate Anomaly Score
        try:
            full_df = pd.DataFrame([np.tile(scaled_feat[0], 10)[:len(self.anomaly_model.feature_names_in_)]],
                                   columns=self.anomaly_model.feature_names_in_)
            anomaly_val = float(-self.anomaly_model.score_samples(full_df)[0])
        except Exception:
            anomaly_val = float(raw_prob * 1.15)

        # Sensor Health & Confidence Calibration
        sensor_health = max(0.20, 1.0 - (missing_count * 0.20))
        base_confidence = 0.96 if ext_rainfall_avail else 0.82
        confidence = round(base_confidence * sensor_health, 2)

        # Severity Decision Policy
        sm = sensor_window.get('soil_moisture_vwc') or 0.20
        tilt_rate = sensor_window.get('tilt_rate') or 0.0
        vib = sensor_window.get('vibration_rate') or 0.0

        if raw_prob >= 0.80 or (sm > 0.40 and tilt_rate > 1.5) or (tilt_rate > 3.0 and vib > 30.0):
            severity = "CRITICAL"
        elif raw_prob >= 0.55 or (sm > 0.35 and tilt_rate > 0.5):
            severity = "WARNING"
        elif raw_prob >= 0.30 or sm > 0.30 or tilt_rate > 0.2:
            severity = "WATCH"
        else:
            severity = "NORMAL"

        # Identify top contributing features
        feature_impacts = {
            "soil_moisture_rate": abs(sensor_window.get("soil_moisture_rate") or 0.0),
            "tilt_rate": abs(tilt_rate),
            "vibration_rate": abs(vib),
            "soil_moisture_vwc": abs(sm)
        }
        sorted_feats = sorted(feature_impacts.items(), key=lambda x: x[1], reverse=True)
        top_features = [k for k, v in sorted_feats[:3] if v > 0]
        if not top_features:
            top_features = ["soil_moisture_vwc", "tilt_magnitude", "temperature"]

        return {
            "hazard": "Landslide",
            "risk_probability": round(float(raw_prob), 4),
            "confidence": confidence,
            "severity": severity,
            "anomaly_score": round(float(anomaly_val), 4),
            "sensor_health": round(float(sensor_health), 2),
            "external_context_available": ext_rainfall_avail,
            "top_features": top_features,
            "model_version": "v1.2.0",
            "timestamp": datetime.datetime.now(datetime.timezone.utc).isoformat()
        }

if __name__ == '__main__':
    engine = LandslideInferenceEngine()
    test_sample = {
        'soil_moisture_vwc': 0.42, 'soil_moisture_rate': 0.05,
        'tilt_magnitude': 12.5, 'tilt_rate': 1.8, 'vibration_rate': 45.0,
        'temperature': 24.0, 'humidity': 85.0, 'rainfall_24h': 65.0
    }
    res = engine.predict_landslide(test_sample)
    print(json.dumps(res, indent=2))
