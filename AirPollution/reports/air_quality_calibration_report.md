# Air Quality Calibration Report

## 1. Probability Calibration & AQI Bands
The model probability output reflects the likelihood of forward 60-minute air quality deterioration transitioning into adverse NAQI categories:

- `NORMAL` (NAQI Good / Satisfactory, $PM_{2.5} \le 60 \mu g/m^3$): Risk Score 0–35.
- `WATCH` (NAQI Moderate, $60 < PM_{2.5} \le 120 \mu g/m^3$): Risk Score 36–60.
- `WARNING` (NAQI Poor / Very Poor, $120 < PM_{2.5} \le 250 \mu g/m^3$): Risk Score 61–85.
- `CRITICAL` (NAQI Severe, $PM_{2.5} > 250 \mu g/m^3$): Risk Score 86–100.

## 2. Dynamic Slope Mapping
Forward 30-minute and 60-minute forecasts incorporate the empirical 30-minute trend slope and gas proxy concentration to project near-term particulate peaks before regional haze sweeps through the monitoring radius.
