# Water Quality Final Model Summary

## Executive Overview
- **Canonical Module**: `Water Quality`
- **Model Version**: `v1.2.0`
- **Architecture**: Calibrated `LogisticRegression` (26 features) + `IsolationForest` Anomaly Detector.
- **Artifacts Saved**:
  - `Water Quality Degradation/models/water_model.pkl`
  - `Water Quality Degradation/models/water_calibrator.pkl`
  - `Water Quality Degradation/models/water_anomaly_detector.pkl`
  - `Water Quality Degradation/models/water_preprocessor.pkl`
  - `Water Quality Degradation/models/water_model_config.json`
  - `Water Quality Degradation/models/feature_order.json`
  - `Water Quality Degradation/models/feature_importance.csv`
- **Input Features (26)**:
  `['pH', 'turbidity', 'EC', 'TDS', 'dissolved_oxygen', 'temperature_c', 'pH_rate', 'turbidity_rate', 'EC_rate', 'TDS_rate', 'DO_rate', 'rolling_mean_pH', 'rolling_mean_turbidity', 'rolling_mean_EC', 'rolling_mean_TDS', 'rolling_mean_DO', 'rolling_std_pH', 'rolling_std_turbidity', 'rolling_std_EC', 'rolling_std_TDS', 'rolling_std_DO', 'acidity_shift_score', 'degradation_spike_score', 'conductivity_shift_score', 'oxygen_drop_score', 'persistence_score']`
- **Backend Microservice**: Port 8006 (`Water Quality Degradation/src/backend/app.py`)
- **Fit Tier**: Weak Physical Hardware / Full Chemistry ML (Graceful confidence degradation when physical chemistry sensors are absent).
- **Readiness**: Production Backend Ready with graceful hardware degradation.
