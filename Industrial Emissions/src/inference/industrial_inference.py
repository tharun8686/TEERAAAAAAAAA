import os
import joblib
import pandas as pd
import numpy as np
import json
import datetime

class IndustrialEmissionsPredictor:
    def __init__(self, models_dir):
        self.model = joblib.load(os.path.join(models_dir, "industrial_model.pkl"))
        self.calibrator = joblib.load(os.path.join(models_dir, "industrial_calibrator.pkl"))
        self.anomaly_detector = joblib.load(os.path.join(models_dir, "industrial_anomaly_detector.pkl"))
        
        with open(os.path.join(models_dir, "industrial_model_config.json"), "r") as f:
            self.config = json.load(f)
            
        self.features = self.config["features"]
        self.classes = {int(k): v for k, v in self.config["classes"].items()}

    def predict_industrial_risk(self, sensor_window: pd.DataFrame) -> dict:
        """
        Executes industrial emissions / chemical leak inference.
        """
        missing = [f for f in self.features if f not in sensor_window.columns]
        if missing:
            return {"error": f"Missing required features: {missing}"}
            
        X = sensor_window[self.features]
        
        # Supervised Class
        pred_class = self.model.predict(X)[0]
        
        # Calibrated Probability
        calibrated_probs = self.calibrator.predict_proba(X)[0]
        # Risk probability: probability of warning/critical (class >= 2) if present,
        # otherwise probability of class 1.
        classes = self.model.classes_
        high_risk_indices = [i for i, c in enumerate(classes) if c >= 2]
        if len(high_risk_indices) > 0:
            leak_risk_prob = float(calibrated_probs[high_risk_indices].sum())
        else:
            # Fallback to class 1
            leak_risk_prob = float(calibrated_probs[1]) if len(calibrated_probs) > 1 else 0.0
            
        # Anomaly Score
        anomaly_score_raw = self.anomaly_detector.decision_function(X)[0]
        anomaly_score = float(np.clip(0.5 - anomaly_score_raw, 0, 1))
        
        # Severity
        severity = self.classes.get(pred_class, "NORMAL")
        
        # Confidence penalties
        confidence = 1.0
        if X['gas_response'].iloc[0] == 0:
            confidence -= 0.5
        if X['PM2.5'].iloc[0] == 0:
            confidence -= 0.3
            
        return {
            "hazard": "Toxic Flame",
            "risk_probability": round(leak_risk_prob, 4),
            "leak_risk_probability": round(leak_risk_prob, 4),
            "confidence": round(max(0.0, confidence), 4),
            "severity": severity,
            "anomaly_score": round(anomaly_score, 4),
            "sensor_health": 1.0 if confidence == 1.0 else 0.5,
            "top_features": ["gas_response", "rolling_mean_gas", "persistence_score"],
            "model_version": "v1.2.0",
            "timestamp": datetime.datetime.now(datetime.timezone.utc).isoformat()
        }

if __name__ == "__main__":
    # Test script locally
    base_dir = r"C:\Users\TEJESHWAR\OneDrive\Desktop\Terra Edge\Industrial Emissions"
    models_dir = os.path.join(base_dir, "models")
    
    predictor = IndustrialEmissionsPredictor(models_dir)
    
    mock_input = pd.DataFrame([{
        'gas_response': 650.0,
        'smoke_or_proxy_response': 500.0,
        'PM2.5': 120.0,
        'PM10': 180.0,
        'temperature_c': 32.0,
        'humidity': 75.0,
        'pressure': 1008.0,
        'gas_rate': 20.0,
        'PM2.5_rate': 15.0,
        'PM10_rate': 25.0,
        'rolling_mean_gas': 600.0,
        'rolling_mean_PM2.5': 110.0,
        'rolling_std_gas': 10.0,
        'rolling_std_PM2.5': 5.0,
        'gas_spike_score': 1.1,
        'particulate_spike_score': 1.2,
        'persistence_score': 10
    }])
    
    res = predictor.predict_industrial_risk(mock_input)
    print(json.dumps(res, indent=2))
