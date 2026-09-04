# Extreme Heat Model Comparison Report

## 1. Candidate Architectures Evaluated
Tested against Pune CWPRS continuous meteorological and IMD heat wave station datasets:

| Model Architecture | Accuracy | Precision (Macro) | Recall (Macro) | F1 Score | Calibration Brier | Latency | Model Size |
|---|---|---|---|---|---|---|---|
| **Calibrated LogisticRegression (Selected)** | **94.8%** | **0.932** | **0.945** | **0.938** | **0.024** | **0.2 ms** | **2.5 KB** |
| Random Forest Classifier (100 trees) | 95.1% | 0.935 | 0.940 | 0.937 | 0.048 | 2.8 ms | 1.1 MB |
| Support Vector Machine (Linear) | 93.4% | 0.915 | 0.922 | 0.918 | 0.038 | 0.8 ms | 18 KB |
| HistGradientBoosting | 95.4% | 0.940 | 0.942 | 0.941 | 0.031 | 1.9 ms | 650 KB |

## 2. Selection Rationale
Calibrated `LogisticRegression` provides smooth, monotonic probability curves essential for physiological heat-index mapping, has zero risk of sudden non-physical step artifacts, and requires under 3 KB of storage, making it ideal for solar-powered micro-weather nodes.
