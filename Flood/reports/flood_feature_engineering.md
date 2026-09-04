# Flood Hydrometry Feature Engineering Report

## 1. Feature Transformation Rationale
Hydrological early warning demands multi-timescale precipitation accumulation and catchment saturation integration to model non-linear runoff peaks.

## 2. Feature Definitions & Causal Flow
1. **Precipitation Windows**:
   - `rain_1h`: Immediate rainfall intensity ($mm/h$).
   - `rain_3h`: Short-term convective storm accumulation ($mm$).
   - `rain_6h`: Catchment concentration time accumulation ($mm$).
   - `rain_24h`: Sub-basin saturation driver ($mm$).
   - `rain_72h`: Antecedent soil moisture saturation envelope ($mm$).
2. **Hydraulic Dynamics**:
   - `water_level_m`: Current river stage ($m$) from ultrasonic / pressure transducers.
   - `streamflow_cumec`: Non-linear volumetric discharge ($Q = c \cdot (H - H_0)^{2.2}$).
   - `soil_moisture_pct`: Antecedent Precipitation Index indicating infiltration capacity.
3. **Atmospheric Context**:
   - `temperature_c` & `humidity_pct`: Atmospheric evaporative demand and storm presence indicators.
4. **Anomaly Scoring**:
   - `anomaly_score`: Mahalanobis/IsolationForest multidimensional distance score indicating unusual water level vs rainfall divergence.

## 3. Explicit Feature Order for Inference
```json
[
  "anomaly_score", "rain_1h", "rain_3h", "rain_6h", "rain_24h", "rain_72h",
  "water_level_m", "streamflow_cumec", "soil_moisture_pct",
  "temperature_c", "humidity_pct"
]
```
