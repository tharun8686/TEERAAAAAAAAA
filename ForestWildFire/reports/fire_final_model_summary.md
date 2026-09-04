# Wildfire Final Model Summary

## Executive Overview
- **Canonical Module**: `Wildfire`
- **Model Version**: `v1.2.0`
- **Architecture**: `CompactRandomForestClassifier` (50 trees, max depth 10) + `IsolationForest` Anomaly Detector.
- **Artifacts Saved**:
  - `ForestWildFire/models/fire_compact_model.pkl`
  - `ForestWildFire/models/fire_compact_scaler.pkl`
  - `ForestWildFire/models/fire_anomaly_model.pkl`
  - `ForestWildFire/models/fire_compact_config.json`
  - `ForestWildFire/models/feature_order.json`
  - `ForestWildFire/models/feature_importance.csv`
- **Input Features (12)**:
  `['temperature', 'humidity', 'pressure', 'pm25', 'tvoc', 'raw_ethanol', 'temperature_rate', 'humidity_rate', 'pm25_rate', 'tvoc_rate', 'temperature_delta_5', 'humidity_delta_5']`
- **Backend Microservice**: Port 8001 (`ForestWildFire/src/backend/app.py`)
- **Fit Tier**: Moderate (Compact 12-feature subset optimized for low-power edge nodes with high recall).
- **Readiness**: Production Backend Ready & Edge Deployed.
