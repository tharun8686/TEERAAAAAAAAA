# Water Quality Degradation / Contamination Module Report

This report documents the end-to-end Machine Learning, Backend, and Frontend dashboard integration of the Water Quality Degradation early warning detection module.

## 1. Data Used
- **Surface Water Physical Parameters**: Contains turbidity, temperature, and total solids measurements.
- **Surface Water Chemical Parameters**: Contains dissolved oxygen, pH, and TDS measurements.
- **Groundwater Physical Parameters**: Contains temperature and turbidity measurements.
- **Groundwater Chemical Parameters**: Contains pH, TDS, ions, and chemical baseline.

## 2. Weak/Derived Label Construction
Since direct contamination logs were not labeled, pseudo-labels were created using physically-justified water safety rules matching WHO/IS 10500 standards:
- `0 = NORMAL` (pH in [6.5, 8.5], turbidity < 5 NTU, TDS < 300 mg/L, dissolved oxygen > 6.0 mg/L)
- `1 = WATCH` (pH in [5.5, 9.5], turbidity < 15 NTU, TDS < 600 mg/L, dissolved oxygen > 4.0 mg/L)
- `2 = WARNING` (pH in [4.5, 10.5], turbidity < 50 NTU, TDS < 1200 mg/L, dissolved oxygen > 2.0 mg/L)
- `3 = CRITICAL` (Severe deviation outside these limits or high co-occurrence)

## 3. Best Model Performance
- **Logistic Regression** and **Random Forest** were both trained. Logistic Regression achieved F1 Macro of `0.63` on the val split and was chosen as the edge deployment model due to its clean linear interpretability and lightweight C weight representation.

## 4. Anomaly Detection
- An **IsolationForest** model was trained on normal background water samples (`risk_level == 0`) with a contamination parameter of `0.01` to capture out-of-distribution pollutant leaks.

## 5. Robustness to Missing Sensors
- If the pH or Turbidity sensor fails (flatlines to 0), the F1 score drops significantly, but the model relies on fallback TDS and temperature spikes to maintain partial hazard tracking.

## 6. Edge Friendliness & ESP32 Deployment
- The scaler means, scales, and model weights are exported. This allows ESP32 deployment to execute in raw C/C++ via simple vector dot products, requiring less than 1KB of RAM.

## 7. Backend & Frontend Integration
- **Backend API**: A FastAPI app running on port **8006** exposes endpoints `/health`, `/api/stations`, and `/api/predict`.
- **Frontend Dashboard**: A 7th hazard card (`07 / AQUATIC HEALTH`) was integrated in `index.html`, featuring a simulator with sliders for pH, Turbidity, TDS, and Temperature to run live inference against port 8006.
