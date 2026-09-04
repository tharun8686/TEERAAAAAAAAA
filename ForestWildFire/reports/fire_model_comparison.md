# Wildfire Model Comparison Report

## 1. Candidate Architectures Evaluated
Evaluated on NIST fire dataset and indoor/outdoor open combustion benchmark matrices:

| Model Architecture | Features | Precision | Recall | F1 Score | ROC-AUC | Size | Edge Latency |
|---|---|---|---|---|---|---|---|
| Full Random Forest | 149 | 0.481 | 0.917 | 0.631 | 0.887 | 435 KB | 18.5 ms |
| **Compact Random Forest (Selected)** | **12** | **0.446** | **0.914** | **0.599** | **0.865** | **330 KB** | **1.8 ms** |
| Logistic Regression (L1 Lasso) | 12 | 0.380 | 0.820 | 0.519 | 0.792 | 8 KB | 0.2 ms |
| Isolation Forest (Unsupervised) | 12 | — | 0.840 | — | 0.812 | 2.5 MB | 4.2 ms |

## 2. Selection Rationale
`CompactRandomForestClassifier` (50 trees, max depth 10, 12 selected features) maintains over 91.4% fire recall while dramatically slashing input dimensionality from 149 to 12 features, eliminating 90% of sensor bus overhead on the edge.
