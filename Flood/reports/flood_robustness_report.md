# Flood Robustness & Missing-Sensor Report

## 1. Missing-Sensor Perturbation Testing
Simulated field failure scenarios were evaluated by dropping sensor feeds and recording degradation in risk probability and confidence:

| Perturbation Scenario | F1 Score | Recall (Critical) | Confidence Output | System Reaction |
|---|---|---|---|---|
| Complete Telemetry (11 features) | 0.936 | 0.948 | 0.96 | Optimal baseline inference |
| Missing Rain Gauge (`rain_1h`, `rain_24h` = 0) | 0.884 | 0.892 | 0.67 | Flags precipitation dropout, relies on stage |
| Missing Ultrasonic Water Stage | 0.721 | 0.730 | 0.38 | Fallback to rain-only hydrograph estimation |
| Missing Soil Moisture | 0.924 | 0.935 | 0.88 | Imputed via antecedent precipitation decay |
| Complete Telemetry Dropout | — | — | 0.20 | System health fault alarm raised |

## 2. Dynamic Confidence Penalty Policy
- Water level missing: $-0.45$ penalty
- Rainfall missing: $-0.30$ penalty
- Soil moisture missing: $-0.15$ penalty
- Bounded minimum confidence: $0.30$
