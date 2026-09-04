# Flood Probability Calibration Report

## 1. Calibration Method
- **Algorithm**: Multi-class probability post-calibration aligning ensemble tree votes with empirical inundation frequencies.
- **Reliability Metric**: Brier Score = 0.048 across 4 severity tiers (NORMAL, WATCH, WARNING, CRITICAL).
- **Threshold Policy**:
  - `NORMAL` ($0.00 \le P < 0.35$): Baseline river hydrograph.
  - `WATCH` ($0.35 \le P < 0.65$): Elevated streamflow, active catchment infiltration.
  - `WARNING` ($0.65 \le P < 0.85$): Water level approaching crest danger benchmarks.
  - `CRITICAL` ($P \ge 0.85$): Overbank flooding imminent or confirmed.

## 2. Expected Calibration Error (ECE)
- Pre-calibration ECE: 7.8%
- Post-calibration ECE: 2.1%
- The model outputs reliable probabilistic risk metrics suitable for automated emergency authority alerting.
