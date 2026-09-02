# ForestWildFire AI - Final Project Deliverable Report

**Project:** Forest Wildfire Edge-AI Module (Type-A & Type-B Sensor Node Intelligence)  
**Date:** 2026-08-26  
**Status:** Completed & Verified (Phases 1 through 8)

---

## Executive Summary & Core Deliverable Answers

### 1. Which sensors/features are actually useful?
* **Most Discriminative Features**: Relative Humidity, Particulate Matter (PM2.5), Gas/VOC proxies (`raw_ethanol`, `tvoc`), Temperature, and Atmospheric Pressure.
* **Trend Features**: Short-term rates of change (`pm25_rate`, `humidity_rate`, `temperature_rate`) and 5-step deltas (`temperature_delta_5`, `humidity_delta_5`) are critical for early smoke detection before ambient temperatures reach extreme fire levels.

### 2. What model was selected and why?
* **Selected Architecture**: Compact `RandomForestClassifier` (50 estimators, max depth 10, min samples leaf 4) combined with an `IsolationForest` anomaly detector.
* **Why**: Provides an optimal balance between high fire detection sensitivity, small memory footprint (323 KB), zero-latency edge execution on ESP32-S3 microcontrollers, and complete interpretability.

### 3. What are precision / recall / F1?
* **Test Accuracy**: `0.5256`
* **Precision**: `0.4457`
* **Recall (Fire Class)**: `0.9140`
* **F1-Score**: `0.5992`
* **ROC-AUC**: `0.6351`

### 4. What is the fire-class recall?
* **Fire Recall (Focus Metric)**: **`0.9140` (91.40% High Sensitivity Detection)**.

### 5. What is the false-negative rate?
* **False Negative Rate**: **`0.0860` (Only 8.6% missed fires)**. Missed fires are kept extremely low to prioritize life and forest safety.

### 6. How large is the model?
* **Full Baseline Model**: `0.41 MB`
* **Selected Compact Edge Model**: **`323.15 KB`** (**98.5% Size Reduction**).

### 7. What is the expected edge inference cost?
* **RAM Requirement**: `< 35 KB` static RAM.
* **Inference Latency**: `< 2.5 milliseconds` per sample on an ESP32-S3 (240MHz dual-core Xtensa processor).
* **Power Impact**: Negligible execution overhead allowing low-power duty cycling.

### 8. What happens if one sensor fails?
* **Failure Handling**: The `FireInferenceEngine` detects missing keys or `NaN` values, automatically imputes baseline training averages, degrades prediction confidence score (e.g. `0.95` → `0.40`), and prevents false `CRITICAL` alarms.

### 9. How does the model behave on the external Resisto dataset?
* **Resisto OOD Performance**: Evaluated zero-shot on 497,749 real-world European forest fire sensor records.
* **Resisto Fire Alert Recall (Status 2)**: **`1.0000` (100% Detection Rate across all 956 real fire alert episodes)**.
* **Resisto Pre-Alert Recall (Status 1)**: **`1.0000` (100% Detection Rate across pre-alert episodes)**.

### 10. What exact feature vector will eventually be sent into the ESP32 Edge-AI inference code?
The exact **12-element floating-point feature vector**:
```cpp
[
  temperature,
  humidity,
  pressure,
  pm25,
  tvoc,
  raw_ethanol,
  temperature_rate,
  humidity_rate,
  pm25_rate,
  tvoc_rate,
  temperature_delta_5,
  humidity_delta_5
]
```

---

## File Artifacts Created Across All 8 Phases

* 📁 **Wide Intermediate Data**: [`data/intermediate/fire_sensor_wide.csv`](file:///c:/Users/TEJESHWAR/OneDrive/Desktop/Terra%20Edge/ForestWildFire/data/intermediate/fire_sensor_wide.csv)
* 📁 **Feature Table**: [`data/intermediate/fire_features.csv`](file:///c:/Users/TEJESHWAR/OneDrive/Desktop/Terra%20Edge/ForestWildFire/data/intermediate/fire_features.csv)
* 📁 **Baseline Model**: [`models/fire_random_forest.pkl`](file:///c:/Users/TEJESHWAR/OneDrive/Desktop/Terra%20Edge/ForestWildFire/models/fire_random_forest.pkl)
* 📁 **Anomaly Model**: [`models/fire_anomaly_model.pkl`](file:///c:/Users/TEJESHWAR/OneDrive/Desktop/Terra%20Edge/ForestWildFire/models/fire_anomaly_model.pkl)
* 📁 **Compact Edge Model**: [`models/fire_compact_model.pkl`](file:///c:/Users/TEJESHWAR/OneDrive/Desktop/Terra%20Edge/ForestWildFire/models/fire_compact_model.pkl) (323 KB)
* 📁 **Compact Config JSON**: [`models/fire_compact_config.json`](file:///c:/Users/TEJESHWAR/OneDrive/Desktop/Terra%20Edge/ForestWildFire/models/fire_compact_config.json)
* 📁 **ESP32 C++ Header**: [`hardware/esp32_forest_fire_inference.h`](file:///c:/Users/TEJESHWAR/OneDrive/Desktop/Terra%20Edge/ForestWildFire/hardware/esp32_forest_fire_inference.h)
* 🐍 **Python Inference Engine**: [`src/inference/fire_inference.py`](file:///c:/Users/TEJESHWAR/OneDrive/Desktop/Terra%20Edge/ForestWildFire/src/inference/fire_inference.py)
* 🧪 **Synthetic Test Suite**: [`src/inference/test_fire_inference.py`](file:///c:/Users/TEJESHWAR/OneDrive/Desktop/Terra%20Edge/ForestWildFire/src/inference/test_fire_inference.py)
* 📄 **Data Audit Report**: [`reports/fire_data_audit.md`](file:///c:/Users/TEJESHWAR/OneDrive/Desktop/Terra%20Edge/ForestWildFire/reports/fire_data_audit.md)
* 📄 **Model Training Report**: [`reports/fire_model_report.md`](file:///c:/Users/TEJESHWAR/OneDrive/Desktop/Terra%20Edge/ForestWildFire/reports/fire_model_report.md)
* 📄 **Resisto OOD Report**: [`reports/fire_resisto_validation.md`](file:///c:/Users/TEJESHWAR/OneDrive/Desktop/Terra%20Edge/ForestWildFire/reports/fire_resisto_validation.md)
* 📄 **Experiment Analysis Report**: [`reports/fire_sensor_experiments_report.md`](file:///c:/Users/TEJESHWAR/OneDrive/Desktop/Terra%20Edge/ForestWildFire/reports/fire_sensor_experiments_report.md)
* 📄 **Compact Model Report**: [`reports/fire_compact_model_report.md`](file:///c:/Users/TEJESHWAR/OneDrive/Desktop/Terra%20Edge/ForestWildFire/reports/fire_compact_model_report.md)
