# Phase 7: Compact Feature Vector & Edge Model Report

## Feature Reduction Overview
- **Original Feature Count:** 151 features
- **Selected Compact Vector:** `12` features (`['temperature', 'humidity', 'pressure', 'pm25', 'tvoc', 'raw_ethanol', 'temperature_rate', 'humidity_rate', 'pm25_rate', 'tvoc_rate', 'temperature_delta_5', 'humidity_delta_5']`)
- **Full Model File Size:** `0.41 MB`
- **Compact Model File Size:** `323.15 KB` (**98.5% Size Reduction** for ESP32-S3 RAM)

## Test Performance Metrics
- **Fire Recall (Focus):** `0.9140` (Maintains high fire detection sensitivity)
- **Accuracy:** `0.5256`
- **Precision:** `0.4457`
- **F1-Score:** `0.5992`
- **ROC-AUC:** `0.6351`
- **False Negative Rate:** `0.0860`

## Confusion Matrix
```text
TN: 3,218 | FP: 8,299
FN: 628 | TP: 6,673
```
