# Phase 3: Baseline Random Forest Model Report

## Test Metrics (Unseen Chronological Split)
- **Accuracy:** `0.5839`
- **Precision:** `0.4810`
- **Recall (Fire Class = 1):** `0.9167` *(Focus Metric)*
- **F1-Score:** `0.6309`
- **ROC-AUC:** `0.8870`
- **PR-AUC:** `0.9161`
- **False Negative Rate:** `0.0833`
- **False Positive Rate:** `0.6271`

## Confusion Matrix
```text
True Normal (TN): 4,295  |  False Positive (FP): 7,222
False Negative (FN): 608  |  True Fire (TP): 6,693
```

## Top 10 Most Important Features
```text
          feature  importance
              cnt    0.075027
 tvoc_roll_max_60    0.070512
 tvoc_roll_min_60    0.065634
tvoc_roll_mean_15    0.058523
 tvoc_roll_min_15    0.050713
tvoc_roll_mean_60    0.045636
  tvoc_roll_max_5    0.038172
             nc05    0.033928
 tvoc_roll_max_15    0.032276
 tvoc_roll_mean_5    0.031694
```
