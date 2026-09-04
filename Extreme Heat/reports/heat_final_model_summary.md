# Extreme Heat Final Model Summary

## Executive Overview
- **Canonical Module**: `Extreme Heat`
- **Model Version**: `v1.2.0`
- **Architecture**: Calibrated `LogisticRegression` + `IsolationForest` Anomaly Detector.
- **Artifacts Saved**:
  - `Extreme Heat/models/heat_model.pkl`
  - `Extreme Heat/models/heat_calibrator.pkl`
  - `Extreme Heat/models/heat_anomaly_detector.pkl`
  - `Extreme Heat/models/heat_preprocessor.pkl`
  - `Extreme Heat/models/heat_model_config.json`
  - `Extreme Heat/models/feature_order.json`
  - `Extreme Heat/models/feature_importance.csv`
- **Input Features (14)**:
  `['temperature_c', 'humidity', 'solar_radiation', 'rainfall_mm', 'wind_speed_kmh', 'temperature_rate', 'humidity_rate', 'solar_radiation_rate', 'rolling_mean_temperature', 'rolling_mean_humidity', 'rolling_std_temperature', 'rolling_std_humidity', 'cumulative_hot_hours', 'nighttime_cooling_deficit']`
- **Backend Microservice**: Port 8004 (`Extreme Heat/src/backend/app.py`)
- **Fit Tier**: Strong (High-precision biometeorological formula calibration, ultra-compact footprint).
- **Readiness**: Production Backend Ready & Embedded Deployable.
