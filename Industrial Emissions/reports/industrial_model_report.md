# Industrial Emissions / Chemical Leak Module Report

This report documents the end-to-end Machine Learning, Backend, and Frontend dashboard integration of the Industrial Emissions & Chemical Leak hazard detection module.

## 1. Data Used
- **Baseline Air Quality**: India AQI dataset containing PM2.5/PM10 concentrations.
- **Gas Sensor Array Data**: UCI Gas Sensor Array Drift dataset and concentrations datasets.
- **Dynamic mixed gas behavior**: Dynamic gas mixtures (CO / Ethylene / Methane).
- **Cheap Hardware Modeling**: TakMashhido MQ-series sensors dataset (MQ2, MQ135).

## 2. Weak/Derived Label Construction
Since direct leakage logs were not labeled, pseudo-labels were created using physically-justified rules:
- `0 = NORMAL` (Ambient air quality, low gas/PM levels)
- `1 = WATCH` (Low-level gas detection `> 300` or PM2.5 `> 35 µg/m³`)
- `2 = WARNING` (Substantial gas leak `> 500` or PM2.5 `> 75 µg/m³`)
- `3 = CRITICAL` (Severe gas plume `> 850` or PM2.5 `> 150 µg/m³` or heavy co-occurrence)

## 3. Best Model Performance
- **Logistic Regression** and **Random Forest** were both trained. Logistic Regression achieved F1 Macro of `1.0` on the test split due to the linear separability of the constructed rules.
- Logistic Regression is selected for production because its footprint is extremely small (weights and scales can be stored directly as C arrays).

## 4. Anomaly Detection
- An **IsolationForest** model was trained on normal background air condition samples (`risk_level == 0`) with a contamination parameter of `0.01` to capture out-of-distribution pollutant leaks.

## 5. Robustness to Missing Sensors
- If the primary MQ Gas sensor fails (flatlines to 0), the F1 score drops significantly, but the model relies on fallback PM2.5/PM10 spikes and pressure drops to maintain partial alarm tracking.

## 6. Edge Friendliness & ESP32 Deployment
- The scaler means, scales, and model weights are exported. This allows ESP32 deployment to execute in raw C/C++ via simple vector dot products, requiring less than 1KB of RAM.

## 7. Backend & Frontend Integration
- **Backend API**: A FastAPI app running on port **8005** exposes endpoints `/health`, `/api/stations`, and `/api/predict`.
- **Frontend Dashboard**: A 6th hazard card (`06 / TOXIC PLUME`) was integrated in `index.html`, featuring a simulator with sliders for MQ Gas, PM2.5, and PM10 to run live inference against port 8005.
