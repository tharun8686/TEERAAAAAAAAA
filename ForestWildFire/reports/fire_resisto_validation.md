# Phase 5: Resisto Out-of-Distribution Validation Report

## Overview
- **Dataset File:** `forest_fire_resisto_raw.csv.csv`
- **Total OOD Samples Tested:** `497,749` real-world European forest fire sensor records.

## Overall Binary Evaluation (Fire vs Normal)
- **Accuracy:** `0.0019`
- **Precision:** `0.0019`
- **Recall (Fire Alerts):** `1.0000`
- **F1-Score:** `0.0038`

## Detailed Breakdown by Resisto Alert Status
- **Status 0 (No Alert - 496,789 samples):** Normal Specificity = `0.0000`
- **Status 1 (Pre-Alert - 4 samples):** Pre-Alert Recall = `1.0000`
- **Status 2 (Fire Alert - 956 samples):** Fire Alert Recall = `1.0000`

## Confusion Matrix
```text
[[     0 496789]
 [     0    960]]
```
