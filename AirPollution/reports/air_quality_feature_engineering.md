# Air Quality Feature Engineering Report

## 1. Aerosol Dynamics & Forward Vector Projections
Short-horizon air pollution forecasting requires accounting for diurnal atmospheric boundary layer collapse (evening thermal inversion trapping pollutants) and forward rate-of-deterioration trends.

## 2. Feature Vectors
1. **Direct Particulate Feeds**:
   - `pm25`: Current respirable fine aerosol concentration ($\mu g/m^3$).
   - `pm10`: Current coarse particulate concentration ($\mu g/m^3$).
   - `gas_proxy`: Mixed toxic reducing gas index (CO/NO2 proxy).
2. **Lagged Temporal Vectors**:
   - `pm25_lag_15`: 15-minute prior concentration.
   - `pm25_lag_30`: 30-minute prior concentration.
   - `pm25_delta_30`: Absolute 30-minute shift ($\Delta PM_{2.5}$).
   - `pm25_slope_30`: Rate of change ($\Delta PM_{2.5} / 30.0$).
3. **Diurnal Inversion Cycles**:
   - `hour_sin` & `hour_cos`: Continuous cyclical representation of solar time ($2\pi \cdot \text{hour} / 24$).

## 3. Explicit Feature Order for Inference
```json
[
  "pm25", "pm10", "gas_proxy", "temperature", "relative_humidity", "pressure",
  "pm25_lag_15", "pm25_lag_30", "pm25_delta_30", "pm25_slope_30",
  "hour_sin", "hour_cos"
]
```
