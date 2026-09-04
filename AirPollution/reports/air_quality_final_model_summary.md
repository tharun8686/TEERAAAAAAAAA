# Air Quality Final Model Summary

## Executive Overview
- **Canonical Module**: `Air Quality`
- **Model Version**: `v1.2.0`
- **Architecture**: `RandomForestClassifier` (100 estimators, max depth 12) + 60-Minute Forward Vector Projection.
- **Artifacts Saved**:
  - `AirPollution/models/edge/air_quality_model.pkl`
  - `AirPollution/models/edge/scaler.pkl`
  - `AirPollution/models/edge/model_config.json`
  - `AirPollution/models/edge/feature_order.json`
  - `AirPollution/models/edge/feature_importance.csv`
- **Input Features (12)**:
  `['pm25', 'pm10', 'gas_proxy', 'temperature', 'relative_humidity', 'pressure', 'pm25_lag_15', 'pm25_lag_30', 'pm25_delta_30', 'pm25_slope_30', 'hour_sin', 'hour_cos']`
- **Backend Microservice**: Port 8003 (`AirPollution/src/backend/app.py`)
- **Fit Tier**: Moderate to Strong (Reliable particulate forecasting, humidity compensation).
- **Readiness**: Production Backend Ready & Edge Deployed.
