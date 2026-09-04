# Landslide Final Model Summary

## Executive Overview
- **Canonical Module**: `Landslide`
- **Model Version**: `v1.2.0`
- **Architecture**: `CalibratedClassifierCV` (RandomForest base) + `IsolationForest` Anomaly Filter.
- **Artifacts Saved**:
  - `Landslide/models/final_landslide_model.pkl`
  - `Landslide/models/final_landslide_preprocessor.pkl`
  - `Landslide/models/cleveland_isolation_forest.pkl`
  - `Landslide/models/landslide_model_config.json`
  - `Landslide/models/feature_order.json`
  - `Landslide/models/feature_importance.csv`
- **Input Features (8)**:
  `['soil_moisture_vwc', 'soil_moisture_rate', 'tilt_magnitude', 'tilt_rate', 'vibration_rate', 'temperature', 'humidity', 'rainfall_24h']`
- **Backend Microservice**: Port 8002 (`Landslide/src/backend/app.py`)
- **Fit Tier**: Strong but Proxy-based (Calibrated MPU-6050 & SW-420 for physical strain).
- **Readiness**: Production Backend Ready & Edge Validated.
