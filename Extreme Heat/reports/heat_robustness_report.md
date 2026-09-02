# Heat Model Sensor Robustness Report

This report simulates sensor failure (flatlining to 0 or mean) and evaluates the impact on the Heat Risk prediction F1 score.

**Baseline F1 Score (Macro):** 0.6094

| Scenario | F1 Score (Macro) | Drop in F1 |
|---|---|---|
| Missing Temperature | 0.2828 | 0.3266 |
| Missing Humidity | 0.3705 | 0.2389 |
| Missing Solar | 0.6019 | 0.0075 |
| Missing Wind | 0.6112 | -0.0018 |

### Conclusion
The model exhibits standard degradation when primary sensors (Temperature/Humidity) fail, but maintains some operational capacity through correlated features if fallback mechanisms are provided. Solar and Wind sensors have smaller impacts.
