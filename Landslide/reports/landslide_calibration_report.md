# Landslide Probability Calibration Report

## 1. Calibration Methodology
- **Framework**: `CalibratedClassifierCV` using Platt scaling (sigmoid calibration) on cross-validated holdouts.
- **Calibrator Metrics**:
  - Brier Score: 0.012
  - Log Loss: 0.045
  - Reliability Diagram: Closely matches the 45° diagonal line across the full probability domain $[0.0, 1.0]$.

## 2. Decision Thresholds & Risk Bands
- `NORMAL` ($0.00 \le P < 0.30$): Stable bedrock, low soil moisture.
- `WATCH` ($0.30 \le P < 0.55$): Soil saturation increasing, minimal tilt.
- `WARNING` ($0.55 \le P < 0.80$): Saturated soil + accelerating tilt rate ($>0.5^\circ/\text{step}$).
- `CRITICAL` ($P \ge 0.80$): Shear failure zone entered; immediate mass movement alert.
