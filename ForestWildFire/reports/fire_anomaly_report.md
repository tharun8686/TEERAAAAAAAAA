# Phase 4: Isolation Forest Anomaly Detector Report

## Overview
- **Training Dataset:** Trained strictly on `3,178` Normal (`fire_alarm == 0`) baseline samples.
- **Test Set Evaluation:** Tested on `18,818` unseen chronological samples.
- **ROC-AUC Anomaly Score:** `0.5287`

## Confusion Matrix (Normal vs Abnormal State)
```text
[[    0 11517]
 [    0  7301]]
```

## Classification Report
```text
               precision    recall  f1-score   support

       Normal       0.00      0.00      0.00     11517
Abnormal/Fire       0.39      1.00      0.56      7301

     accuracy                           0.39     18818
    macro avg       0.19      0.50      0.28     18818
 weighted avg       0.15      0.39      0.22     18818

```
