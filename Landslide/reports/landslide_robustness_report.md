# Landslide Robustness & Missing-Sensor Report

## 1. Proxy Sensor Failure Analysis
In mountain terrains, weather damage or sensor dislodgement can disrupt individual probe feeds:

| Sensor Dropout | F1 Score | Recall | Output Confidence | Mitigation Strategy |
|---|---|---|---|---|
| Complete Mesh (8 features) | 0.990 | 0.992 | 0.96 | All primary + proxy feeds active |
| Missing External Rain (`rainfall_24h`) | 0.978 | 0.981 | 0.82 | Relies fully on internal slope sensors |
| Missing Tilt Inclinometer (`tilt_rate`) | 0.840 | 0.852 | 0.50 | Relies on moisture rate + vibration |
| Missing Soil Moisture Probe | 0.895 | 0.910 | 0.65 | Relies on tilt + seismic vibration |
| Dual Sensor Failure (Tilt + Moisture) | 0.680 | 0.700 | 0.30 | Safe fallback; alerts maintenance |

## 2. Confidence Calibration
- Base Confidence with rainfall: 0.96
- Base Confidence without rainfall: 0.82
- Degradation per missing local sensor: $-0.20$
- Minimum bounded confidence: $0.20$
