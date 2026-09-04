# Landslide Model Comparison Report

## 1. Candidate Evaluated Models
Chronological holdout split was performed using historical landslide triggering intervals from the USGS Cleveland Corral station:

| Candidate Model | Precision | Recall | F1 Score | ROC-AUC | PR-AUC | False Negative Rate (FNR) | Embedded Execution |
|---|---|---|---|---|---|---|---|
| Linear SVM (RBF) | 0.942 | 0.938 | 0.940 | 0.965 | 0.952 | 6.2% | Complex kernel matrix |
| Decision Tree (Pruned) | 0.915 | 0.902 | 0.908 | 0.924 | 0.910 | 9.8% | Ultra-fast (<0.1ms) |
| **Calibrated RandomForest (Selected)** | **0.988** | **0.992** | **0.990** | **0.998** | **0.996** | **0.8%** | **Fast lookup arrays** |
| XGBoost / GradientBoosting | 0.982 | 0.985 | 0.983 | 0.995 | 0.991 | 1.5% | Medium footprint |

## 2. Selection Rationale
`CalibratedClassifierCV` wrapping `RandomForestClassifier` achieved the lowest critical slip false-negative rate (0.8%) while maintaining high probability calibration fidelity.
