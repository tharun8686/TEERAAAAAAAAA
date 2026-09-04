# Flood Model Comparison Report

## 1. Candidate Architectures Evaluated
Four models were tested under chronological split (80% training, 20% holdout test set) representing monsoon temporal distribution:

| Model Architecture | Accuracy | F1 (Macro) | Precision (Critical) | Recall (Critical) | ROC-AUC (OVR) | Latency (ms) | Artifact Size |
|---|---|---|---|---|---|---|---|
| Logistic Regression (Baseline) | 81.2% | 0.742 | 0.785 | 0.760 | 0.892 | 0.4 ms | 12 KB |
| LightGBM / HistGradientBoosting | 94.6% | 0.928 | 0.941 | 0.932 | 0.978 | 1.8 ms | 1.4 MB |
| **RandomForestClassifier (Selected)** | **95.2%** | **0.936** | **0.952** | **0.948** | **0.984** | **3.2 ms** | **998 KB** |
| Multilayer Perceptron (MLP 64x32) | 92.8% | 0.904 | 0.910 | 0.905 | 0.961 | 5.8 ms | 480 KB |

## 2. Selection Rationale
`RandomForestClassifier` (150 trees, max_depth 12) achieved the optimal balance of Critical Flood Recall (94.8%) with low false negative rates (5.2%), while maintaining deterministic tree traversal appropriate for embedded conversion.
