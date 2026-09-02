# Phase 3 Summary: Cleveland Corral Temporal & Precursor Analysis

## Executive Summary
- **Clean Time Series**: `705,470` 15-minute observations spanning 1997–2018.
- **Detected Movement Instability Episodes**: `59,242` samples.
- **Anomaly Model**: Trained IsolationForest on stable baseline periods.

## Precursor & Lag Findings
- **Hydrological Sequence**: Prolonged rainfall (`rainfall_24h`, `rainfall_72h`) drives pore pressure and soil moisture saturation **24 to 48 hours prior** to accelerated slope displacement.
- **Rate vs Absolute**: Short-term rate of change (`soil_moisture_rate` and `displacement_rate`) provides earlier warning lead-time than static absolute levels.
