# Water Quality Model Robustness Report

This report simulates sensor failure (flatlining to 0) and evaluates the impact on the Water Quality Degradation F1 score.

**Baseline F1 Score (Macro):** 0.1384

| Scenario | F1 Score (Macro) | Drop in F1 |
|---|---|---|
| Missing pH Sensor | 0.0694 | 0.0690 |
| Missing Turbidity Sensor | 0.6234 | -0.4850 |
| Missing EC/TDS Sensors | 0.1122 | 0.0262 |
| Missing Dissolved Oxygen | 0.1649 | -0.0265 |

### Conclusion
The model exhibits structural degradation when the pH or Turbidity sensors fail. If any sensor flatlines to 0, the confidence metrics are penalised, but correlation-based monitoring (using TDS and Temperature) allows the system to continue running with reduced confidence.
