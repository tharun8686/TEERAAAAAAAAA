# Toxic Flame Final Model Summary

## Executive Overview
- **Canonical Module**: `Toxic Flame`
- **Model Version**: `v1.2.0`
- **Architecture**: Calibrated `LogisticRegression` + `IsolationForest` Plume Anomaly Detector.
- **Artifacts Saved**:
  - `Industrial Emissions/models/industrial_model.pkl`
  - `Industrial Emissions/models/industrial_calibrator.pkl`
  - `Industrial Emissions/models/industrial_anomaly_detector.pkl`
  - `Industrial Emissions/models/industrial_preprocessor.pkl`
  - `Industrial Emissions/models/industrial_model_config.json`
  - `Industrial Emissions/models/feature_order.json`
  - `Industrial Emissions/models/feature_importance.csv`
- **Input Features (17)**:
  `['gas_response', 'smoke_or_proxy_response', 'PM2.5', 'PM10', 'temperature_c', 'humidity', 'pressure', 'gas_rate', 'PM2.5_rate', 'PM10_rate', 'rolling_mean_gas', 'rolling_mean_PM2.5', 'rolling_std_gas', 'rolling_std_PM2.5', 'gas_spike_score', 'particulate_spike_score', 'persistence_score']`
- **Backend Microservice**: Port 8005 (`Industrial Emissions/src/backend/app.py`)
- **Fit Tier**: Moderate (Separated from wildfire via rapid VOC slope rates & co-occurrence).
- **Readiness**: Production Backend Ready & Edge Deployed.
