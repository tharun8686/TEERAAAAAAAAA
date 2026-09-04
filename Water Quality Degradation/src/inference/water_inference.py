import os
import joblib
import pandas as pd
import numpy as np
import json
import datetime

class WaterQualityPredictor:
    def __init__(self, models_dir):
        self.model = joblib.load(os.path.join(models_dir, "water_model.pkl"))
        self.calibrator = joblib.load(os.path.join(models_dir, "water_calibrator.pkl"))
        self.anomaly_detector = joblib.load(os.path.join(models_dir, "water_anomaly_detector.pkl"))
        
        with open(os.path.join(models_dir, "water_model_config.json"), "r") as f:
            self.config = json.load(f)
            
        self.features = self.config["features"]
        self.classes = {int(k): v for k, v in self.config["classes"].items()}

    def predict_water_quality_risk(self, sensor_window: pd.DataFrame) -> dict:
        """
        Executes water quality degradation / contamination inference.
        """
        missing = [f for f in self.features if f not in sensor_window.columns]
        if missing:
            return {"error": f"Missing required features: {missing}"}
            
        X = sensor_window[self.features]
        
        # Supervised Class
        pred_class = self.model.predict(X)[0]
        
        # Calibrated Probability
        calibrated_probs = self.calibrator.predict_proba(X)[0]
        classes = self.model.classes_
        high_risk_indices = [i for i, c in enumerate(classes) if c >= 2]
        if len(high_risk_indices) > 0:
            water_quality_risk_prob = float(calibrated_probs[high_risk_indices].sum())
        else:
            water_quality_risk_prob = float(calibrated_probs[1]) if len(calibrated_probs) > 1 else 0.0
            
        # Anomaly Score
        anomaly_score_raw = self.anomaly_detector.decision_function(X)[0]
        anomaly_score = float(np.clip(0.5 - anomaly_score_raw, 0, 1))
        
        # Severity
        severity = self.classes.get(pred_class, "NORMAL")
        
        # Confidence penalties reflecting prototype hardware constraints
        confidence = 1.0
        ph_val = X['pH'].iloc[0]
        tur_val = X['turbidity'].iloc[0]
        do_val = X['dissolved_oxygen'].iloc[0] if 'dissolved_oxygen' in X.columns else 7.5

        if ph_val == 0 or np.isnan(ph_val):
            confidence -= 0.35
        if tur_val == 0 or np.isnan(tur_val):
            confidence -= 0.35
        if do_val == 0 or np.isnan(do_val):
            confidence -= 0.15

        confidence = round(max(0.30, confidence), 2)
        sensor_health = round(confidence, 2)

        return {
            "hazard": "Water Quality",
            "risk_probability": round(water_quality_risk_prob, 4),
            "water_quality_risk_probability": round(water_quality_risk_prob, 4),
            "confidence": confidence,
            "severity": severity,
            "anomaly_score": round(anomaly_score, 4),
            "sensor_health": sensor_health,
            "top_features": ["pH", "turbidity", "oxygen_drop_score"],
            "model_version": "v1.2.0",
            "timestamp": datetime.datetime.now(datetime.timezone.utc).isoformat()
        }

if __name__ == "__main__":
    # Test script locally
    base_dir = r"C:\Users\TEJESHWAR\OneDrive\Desktop\Terra Edge\Water Quality Degradation"
    models_dir = os.path.join(base_dir, "models")
    
    predictor = WaterQualityPredictor(models_dir)
    
    mock_input = pd.DataFrame([{
        'pH': 4.2,
        'turbidity': 65.0,
        'EC': 900.0,
        'TDS': 1400.0,
        'dissolved_oxygen': 1.8,
        'temperature_c': 28.0,
        'pH_rate': -1.2,
        'turbidity_rate': 25.0,
        'EC_rate': 100.0,
        'TDS_rate': 200.0,
        'DO_rate': -3.0,
        'rolling_mean_pH': 6.8,
        'rolling_mean_turbidity': 15.0,
        'rolling_mean_EC': 450.0,
        'rolling_mean_TDS': 350.0,
        'rolling_mean_DO': 6.5,
        'rolling_std_pH': 0.5,
        'rolling_std_turbidity': 2.0,
        'rolling_std_EC': 15.0,
        'rolling_std_TDS': 20.0,
        'rolling_std_DO': 0.8,
        'acidity_shift_score': 2.8,
        'degradation_spike_score': 4.3,
        'conductivity_shift_score': 2.0,
        'oxygen_drop_score': 6.2,
        'persistence_score': 8
    }])
    
    res = predictor.predict_water_quality_risk(mock_input)
    print(json.dumps(res, indent=2))
