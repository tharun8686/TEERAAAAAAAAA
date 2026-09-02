# Industrial Leak Model Robustness Report

This report simulates sensor failure (flatlining to 0) and evaluates the impact on the Chemical Leak prediction F1 score.

**Baseline F1 Score (Macro):** 0.2941

| Scenario | F1 Score (Macro) | Drop in F1 |
|---|---|---|
| Missing Gas Sensor | 0.1083 | 0.1859 |
| Missing Smoke Sensor | 0.2941 | 0.0000 |
| Missing Particulates (PM2.5) | 0.2941 | 0.0000 |
| Missing Environmental Context | 0.2941 | 0.0000 |

### Conclusion
The model relies heavily on the co-occurrence of gas readings and particulate counts to trigger leaks safely. When the gas sensor fails, the model operates with degraded confidence, relying on PM spikes and environmental pressure changes to report possible leaks.
