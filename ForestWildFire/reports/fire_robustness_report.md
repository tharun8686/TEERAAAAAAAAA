# Wildfire Robustness & Missing-Sensor Report

## 1. Sensor Dropout & Drift Resilience
Metal-oxide semiconductor (MOS) sensors like MQ-2, MQ-7, and BME680 suffer from long-term baseline drift and humidity sensitivity.

| Dropout Condition | Recall | Precision | Output Confidence | Drift Compensation |
|---|---|---|---|---|
| Complete 12-Feature Window | 91.4% | 44.6% | 0.95 | Baseline thermal auto-zero |
| Missing TVOC / Ethanol Channel | 84.2% | 38.5% | 0.80 | Compensated via $PM_{2.5}$ + temperature rate |
| Missing $PM_{2.5}$ Sensor | 82.5% | 40.1% | 0.80 | Compensated via TVOC + pressure + thermal delta |
| Missing Temperature / Humidity | 78.0% | 32.0% | 0.65 | Severely degraded; fire risk relies on raw gas |
| Multiple Gas Dropouts | — | — | 0.40 | Minimum bounded safety confidence |

## 2. Confidence Calibration Formulation
$$\text{confidence} = \max(0.40, 0.95 - (\text{missing\_count} \times 0.15))$$
Missing values are auto-imputed using the population baseline scaler means.
