# India-Specific Air-Pollution Early-Warning & TinyML Module

This module provides a production-grade time-series machine-learning and Edge AI pipeline for predicting **air quality deterioration** 30 to 60 minutes into the future across Indian CPCB CAAQM monitoring stations.

---

## 🚀 Quick Start / Reproduction

To run the complete pipeline end-to-end from raw ingestion to model training, evaluation, and C++ ESP32 export:

```bash
cd AirPollution
pip install -r requirements.txt
python src/run_pipeline.py
```

To run synthetic real-time streaming inference:
```bash
python src/inference.py
```

To generate HTML reports:
```bash
python src/evaluate.py
```

---

## 📁 Repository Structure

```text
AirPollution/
├── config/                  # Thresholds, Labels & Feature Configurations
│   ├── features.yaml
│   ├── labels.yaml
│   └── thresholds.yaml
├── data/
│   ├── raw/                 # CPCB CAAQM Raw CSV Datasets
│   ├── cleaned/             # Sanitized Data
│   ├── processed/           # Feature Matrix
│   └── merged/              # Master Unified Parquet & CSV Datasets
├── hardware/
│   └── esp32_air_pollution_inference.h  # C++ Header for ESP32-S3 Microcontroller
├── models/
│   ├── baseline/            # Persistence & Ridge Baseline Models
│   ├── reference/           # Track A Multi-Pollutant Reference Model
│   └── edge/                # Track B Compact Edge Random Forest & Scaler
├── reports/                 # Quality, Comparison & Calibration Reports
│   ├── data_quality_report.csv
│   ├── data_quality_report.html
│   ├── model_comparison.csv
│   └── model_comparison.html
├── src/
│   ├── schema.py            # CPCB CAAQM Schema Standardizer
│   ├── data_loader.py       # Multi-station CSV Ingestor
│   ├── cleaning.py          # Physical Validation & Short-Gap Interpolation
│   ├── feature_engineering.py  # Lags, Rolling Windows, Trends & Circular Encodings
│   ├── labels.py            # 30m / 60m Future Forecast Targets & Sustained Labels
│   ├── train.py             # Model Training (Persistence, Ridge, Random Forest, XGBoost)
│   ├── evaluate.py          # Evaluation & HTML Report Generator
│   ├── export.py            # ESP32-S3 C++ Header Generator
│   ├── inference.py         # Production Inference Engine
│   └── run_pipeline.py      # Master End-to-End Execution Script
└── requirements.txt
```

---

## 🎯 Model Capabilities & Outputs

Given current local sensor readings (PM2.5, PM10, Gas Proxy, Temp, Humidity, Pressure, Lags, Trends), the model outputs:

```json
{
  "hazard": "air_quality_deterioration",
  "risk_score": 88,
  "confidence": 93,
  "predicted_pm25_30m": 142,
  "predicted_pm25_60m": 171,
  "predicted_pm10_30m": 208,
  "severity": "WARNING",
  "horizon_minutes": 60
}
```

---

## ⚡ ESP32-S3 Microcontroller Deployment

The C++ embedded header is stored at [`hardware/esp32_air_pollution_inference.h`](file:///c:/Users/TEJESHWAR/OneDrive/Desktop/Terra%20Edge/AirPollution/hardware/esp32_air_pollution_inference.h) and can be directly included in Arduino / ESP-IDF C++ projects:

```cpp
#include "esp32_air_pollution_inference.h"

AirPollutionPrediction result = predict_air_quality_esp32(
    pm25, pm10, gas_proxy, temp, humidity, pressure,
    pm25_lag15, pm25_lag30, delta_30, slope_30, hour_sin, hour_cos
);

// result.severity -> AIR_NORMAL, AIR_WATCH, AIR_WARNING, AIR_CRITICAL
```
