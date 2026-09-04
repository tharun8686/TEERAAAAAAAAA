# Flood Final Model Summary

## Executive Overview
- **Canonical Module**: `Flood`
- **Model Version**: `v1.2.0`
- **Architecture**: `RandomForestClassifier` (150 trees, max depth 12) + `IsolationForest` Anomaly Pipeline.
- **Artifacts Saved**:
  - `Flood/models/flood_risk_model_v1.pkl`
  - `Flood/models/anomaly_model_v1.pkl`
  - `Flood/models/model_config.json`
  - `Flood/models/feature_order.json`
  - `Flood/models/feature_importance.csv`
- **Input Features (11)**:
  `['anomaly_score', 'rain_1h', 'rain_3h', 'rain_6h', 'rain_24h', 'rain_72h', 'water_level_m', 'streamflow_cumec', 'soil_moisture_pct', 'temperature_c', 'humidity_pct']`
- **Backend Microservice**: Port 8000 (`Flood/src/backend/app.py`)
- **Fit Tier**: Strong (Direct hydraulic sensors, high precision, low FNR).
- **Readiness**: Production Backend Ready & Edge Deployable.
