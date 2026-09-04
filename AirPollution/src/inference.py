import pandas as pd
import numpy as np
import os
import joblib
import json
import datetime

class AirPollutionInferenceEngine:
    def __init__(self):
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        models_edge_dir = os.path.join(base_dir, 'models', 'edge')

        self.model_path = os.path.join(models_edge_dir, 'air_quality_model.pkl')
        self.scaler_path = os.path.join(models_edge_dir, 'scaler.pkl')
        self.schema_path = os.path.join(models_edge_dir, 'feature_schema.json')

        self.model = joblib.load(self.model_path)
        self.scaler = joblib.load(self.scaler_path)

        with open(self.schema_path, 'r') as f:
            self.features = json.load(f)['edge_features']

    def predict_air_pollution(self, sensor_window: dict) -> dict:
        """
        Input sensor_window expects keys:
        pm25, pm10, gas_proxy, temperature, relative_humidity, pressure,
        pm25_lag_15, pm25_lag_30, pm25_delta_30, pm25_slope_30, hour_sin, hour_cos
        """
        missing_cnt = 0
        vector = []

        mean_map = dict(zip(self.features, self.scaler.mean_))

        for feat in self.features:
            val = sensor_window.get(feat, None)
            if val is None or np.isnan(val):
                missing_cnt += 1
                val = mean_map.get(feat, 0.0)
            vector.append(val)

        df_feat = pd.DataFrame([vector], columns=self.features)
        scaled_feat = self.scaler.transform(df_feat)

        # Deterioration Probability (0-1)
        prob = float(self.model.predict_proba(scaled_feat)[0][1])

        pm25_curr = sensor_window.get('pm25', 45.0)
        pm10_curr = sensor_window.get('pm10', 85.0)
        delta_30 = sensor_window.get('pm25_delta_30', 0.0)
        gas_proxy = sensor_window.get('gas_proxy', 25.0)

        # Forecasts
        pred_pm25_30m = round(float(max(0.0, pm25_curr + delta_30 * 0.8 + gas_proxy * 0.15)), 1)
        pred_pm25_60m = round(float(max(0.0, pm25_curr + delta_30 * 1.5 + gas_proxy * 0.25)), 1)
        pred_pm10_30m = round(float(max(0.0, pm10_curr + delta_30 * 1.2)), 1)

        # Risk Score (0 - 100)
        risk_score = min(100, max(0, int(prob * 70 + (pred_pm25_60m / 250.0) * 30)))

        # Confidence (0 - 100) based on sensor health
        sensor_health = max(0.20, 1.0 - (missing_cnt * 0.15))
        confidence = int(93 * sensor_health)

        # Severity Category
        if pred_pm25_60m > 250.0:
            severity = "CRITICAL"
        elif pred_pm25_60m > 120.0:
            severity = "WARNING"
        elif pred_pm25_60m > 60.0:
            severity = "WATCH"
        else:
            severity = "NORMAL"

        return {
            "hazard": "Air Quality",
            "risk_probability": round(float(risk_score / 100.0), 4),
            "confidence": confidence,
            "severity": severity,
            "anomaly_score": round(float(prob), 4),
            "sensor_health": round(float(sensor_health), 2),
            "top_features": ["pm25", "pm10", "pm25_delta_30"],
            "model_version": "v1.2.0",
            "timestamp": datetime.datetime.now(datetime.timezone.utc).isoformat(),
            # Legacy compatibility fields:
            "risk_score": risk_score,
            "predicted_pm25_30m": pred_pm25_30m,
            "predicted_pm25_60m": pred_pm25_60m,
            "predicted_pm10_30m": pred_pm10_30m,
            "horizon_minutes": 60
        }

if __name__ == '__main__':
    engine = AirPollutionInferenceEngine()
    test_sample = {
        "pm25": 115.0, "pm10": 185.0, "gas_proxy": 35.0, "temperature": 28.5,
        "relative_humidity": 72.0, "pressure": 1012.0, "pm25_lag_15": 95.0,
        "pm25_lag_30": 80.0, "pm25_delta_30": 35.0, "pm25_slope_30": 1.16,
        "hour_sin": 0.5, "hour_cos": -0.86
    }
    print(json.dumps(engine.predict_air_pollution(test_sample), indent=2))
