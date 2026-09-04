# Wildfire Probability Calibration Report

## 1. Calibration Method & Threshold Boundaries
Tree voting probabilities are post-calibrated with an empirical rate-of-rise threshold policy to prevent false alarms from temporary transient dust or cooking smoke.

## 2. Decision Logic & Severity Mapping
- `NORMAL`: Fire probability $< 0.30$ and rates within nominal baseline.
- `WATCH`: Fire probability $\ge 0.30$ with minor particulate or TVOC rise ($PM_{2.5} \text{ rate} > 0.2$).
- `WARNING`: Fire probability $\ge 0.65$ OR ($P \ge 0.35$ with $PM_{2.5} \text{ rate} > 0.5$ and thermal acceleration $>0.1^\circ\text{C}/s$).
- `CRITICAL`: Fire probability $\ge 0.85$ OR ($P \ge 0.35$ with rapid plume burst $PM_{2.5} \text{ rate} > 1.0$ or anomaly score $>0.60$).
