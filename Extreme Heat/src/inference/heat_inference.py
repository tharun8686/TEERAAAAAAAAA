import os
import joblib
import pandas as pd
import numpy as np
import json
import datetime

class HeatRiskPredictor:
    def __init__(self, models_dir):
        self.model = joblib.load(os.path.join(models_dir, "heat_model.pkl"))
        self.calibrator = joblib.load(os.path.join(models_dir, "heat_calibrator.pkl"))
        self.anomaly_detector = joblib.load(os.path.join(models_dir, "heat_anomaly_detector.pkl"))
        
        with open(os.path.join(models_dir, "heat_model_config.json"), "r") as f:
            self.config = json.load(f)
            
        self.features = self.config["features"]
        self.classes = {int(k): v for k, v in self.config["classes"].items()}

    def predict_heat_risk(self, sensor_window: pd.DataFrame) -> dict:
        """
        Predicts extreme heat risk from a window of sensor data.
        Assumes sensor_window is a single-row DataFrame containing all required features.
        """
        # Ensure all required features are present
        missing = [f for f in self.features if f not in sensor_window.columns]
        if missing:
            return {"error": f"Missing required features: {missing}"}
            
        X = sensor_window[self.features]
        
        # Supervised Prediction (uncalibrated logic if we just want class)
        pred_class = self.model.predict(X)[0]
        
        # Calibrated probability
        # Get probability of high risk (classes >= 2 if they exist, else highest class)
        calibrated_probs = self.calibrator.predict_proba(X)[0]
        # Our model predicts classes 0 and 1 only based on the validation set, 
        # so risk probability is probability of class 1.
        if len(calibrated_probs) > 1:
            heat_risk_prob = float(calibrated_probs[-1])
        else:
            heat_risk_prob = 0.0
            
        # Anomaly Score
        # IsolationForest decision_function: lower is more anomalous
        anomaly_score_raw = self.anomaly_detector.decision_function(X)[0]
        # Normalize roughly between 0 and 1 (1 = anomalous)
        anomaly_score = float(np.clip(0.5 - anomaly_score_raw, 0, 1))
        
        # Severity
        severity = self.classes.get(pred_class, "UNKNOWN")
        
        # Confidence Penalty for Missing Sensors (simulated via 0 values where impossible)
        confidence = 1.0
        if X['temperature_c'].iloc[0] == 0:
            confidence -= 0.5
        if X['humidity'].iloc[0] == 0:
            confidence -= 0.3
            
        return {
            "hazard": "Extreme Heat",
            "risk_probability": round(heat_risk_prob, 4),
            "heat_risk_probability": round(heat_risk_prob, 4),
            "confidence": round(max(0.0, confidence), 4),
            "severity": severity,
            "anomaly_score": round(anomaly_score, 4),
            "sensor_health": 1.0 if confidence == 1.0 else 0.5,
            "top_features": ["temperature_c", "rolling_mean_temperature", "solar_radiation"],
            "model_version": "v1.2.0",
            "timestamp": datetime.datetime.now(datetime.timezone.utc).isoformat()
        }

# Example usage
if __name__ == "__main__":
    base_dir = r"C:\Users\TEJESHWAR\OneDrive\Desktop\Terra Edge\Extreme Heat"
    models_dir = os.path.join(base_dir, "models")
    
    predictor = HeatRiskPredictor(models_dir)
    
    # Mock data for inference
    mock_data = pd.DataFrame([{
        'temperature_c': 42.0,
        'humidity': 60.0,
        'solar_radiation': 900.0,
        'rainfall_mm': 0.0,
        'wind_speed_kmh': 5.0,
        'temperature_rate': 2.0,
        'humidity_rate': -5.0,
        'solar_radiation_rate': 100.0,
        'rolling_mean_temperature': 38.0,
        'rolling_mean_humidity': 65.0,
        'rolling_std_temperature': 3.0,
        'rolling_std_humidity': 10.0,
        'cumulative_hot_hours': 12,
        'nighttime_cooling_deficit': 5.0
    }])
    
    result = predictor.predict_heat_risk(mock_data)
    print(json.dumps(result, indent=2))
