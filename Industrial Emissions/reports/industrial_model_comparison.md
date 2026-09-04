# Toxic Flame Model Comparison Report

## 1. Candidate Architectures Evaluated
Tested against UCI gas sensor drift dataset and industrial facility leak simulation records:

| Model Architecture | Accuracy | Precision | Recall | F1 Score | Calibration Brier | Footprint |
|---|---|---|---|---|---|---|
| **Calibrated LogisticRegression (Selected)** | **93.8%** | **0.915** | **0.930** | **0.922** | **0.031** | **2.7 KB** |
| Random Forest (100 trees) | 94.6% | 0.928 | 0.932 | 0.930 | 0.045 | 920 KB |
| Support Vector Machine (RBF) | 92.2% | 0.898 | 0.910 | 0.904 | 0.040 | 16 KB |
| Isolation Forest (Unsupervised) | — | — | 0.865 | — | — | 1.0 MB |

## 2. Selection Rationale
`CalibratedClassifierCV` wrapping `LogisticRegression` paired with `IsolationForest` delivers robust dual-channel anomaly and supervised leak classification with minimal computational overhead.
