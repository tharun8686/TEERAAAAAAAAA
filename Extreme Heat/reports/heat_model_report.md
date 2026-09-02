# Extreme Heat Module — Final Report

## 1. Data Used
- **Sources**: 
  - Hourly Temperature, Humidity, and Solar Radiation data from CWPRS telemetry.
  - Hourly manual rainfall measurements.
  - Twice-daily manual wind speed data (interpolated to hourly).
- **Timeframe**: 2021-2025 (wind from 1970).
- **Region**: CWPRS, Maharashtra, India.
- **Preprocessing**: Data aligned onto a standard hourly grid with forward filling/interpolation applied to handle missing values and lower-resolution wind data.

## 2. Weak Labels Construction
Given the lack of a ground-truth "heatwave" label file, pseudo-labels were created systematically using:
- **Heat Index**: Rothfusz regression formula to calculate perceived temperature.
- **Persistence & Nighttime Cooling**: Penalized low nighttime cooling (min temp > 28°C) and sustained periods (cumulative hot hours) to define risk.
- **Severity Thresholds**: 
  - 0: NORMAL (HI < 35°C)
  - 1: WATCH (HI 35-40°C)
  - 2: WARNING (HI 40-45°C)
  - 3: CRITICAL (HI > 45°C)

## 3. Best Performing Model
- **Logistic Regression** achieved the highest validation F1 score (Macro F1 = ~0.91). Random Forest was also trained but underperformed in tracking class boundaries for the chronological test split. Logistic Regression's linear boundaries are also extremely lightweight.

## 4. Feature Importance
- **Top Features**: 
  - `temperature_c` (Base driver)
  - `rolling_mean_temperature` (Persistence indicator)
  - `nighttime_cooling_deficit` (Heat retention indicator)
  - `humidity` (Drives heat stress index)

## 5. Sensor Robustness
- **Temperature/Humidity Failure**: F1 score degrades but maintains partial operability if standard interpolation fallbacks exist.
- **Missing Solar/Wind**: Negligible impact on core Heat Index, though solar affects daytime load metrics.

## 6. Edge Friendliness
- **Model Size**: Extremely compact. The Logistic Regression model is merely an array of weights and biases.
- **Deployment**: `generate_heat_config.py` outputs C-compatible arrays containing scaler means, scales, and class weights, meaning it can run natively on an ESP32 using just dot products—no ML library required.

## 7. Limitations & Future Improvements
- **Regional Bias**: Model trained specifically on Maharashtra (CWPRS) data. Needs nationwide data (e.g., Delhi/Rajasthan) for generalization.
- **Wind Speed Sparsity**: The twice-daily nature of the wind data reduces its hourly predictive power. High-resolution telemetry for wind is needed.
- **AQI Integration**: AQI was provided but not integrated as a core feature due to inconsistent time formatting and missing location linkages. Future versions should model Heat + Pollution stress.
