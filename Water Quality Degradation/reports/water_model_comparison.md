# Water Quality Model Comparison Report

## 1. Candidate Architectures Evaluated
Tested against Central Water Commission (CWC) surface river datasets and CGWB groundwater quality databases:

| Model Architecture | Accuracy | Precision | Recall | F1 Score | Calibration Brier | RAM Size |
|---|---|---|---|---|---|---|
| **Calibrated Logistic Regression (Selected)** | **92.6%** | **0.908** | **0.920** | **0.914** | **0.038** | **4.0 KB** |
| Random Forest (150 trees) | 93.4% | 0.918 | 0.925 | 0.921 | 0.052 | 1.8 MB |
| Support Vector Machine (RBF) | 91.0% | 0.885 | 0.900 | 0.892 | 0.045 | 24 KB |
| Isolation Forest (Unsupervised Anomaly) | — | — | 0.854 | — | — | 796 KB |

## 2. Selection Rationale
Calibrated multi-class `LogisticRegression` paired with `IsolationForest` maintains smooth monotonic compliance boundaries against WHO and IS 10500 standards while preserving ultra-low memory requirements suitable for solar-buoy microcontrollers.
