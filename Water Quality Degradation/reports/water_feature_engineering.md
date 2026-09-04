# Water Quality Feature Engineering Report

## 1. Aquatic Chemistry & Contamination Dynamics
Aquatic health analysis evaluates multi-parameter physicochemical standards (WHO Guidelines & Indian Standard IS 10500):
- Acid/Alkali excursions ($|pH - 7.0|$) indicating chemical runoff.
- Particulate optical scattering ($Turbidity, NTU$) indicating sediment suspension or microbial blooms.
- Electrolyte conduction ($EC$) and mineralization ($TDS$).
- Biological respiration deficit ($Dissolved\ Oxygen < 4.0\ mg/L$).

## 2. Feature Vectors (26 Full Chemistry Features)
1. **Primary Physicochemical Feeds**:
   - `pH`, `turbidity`, `EC`, `TDS`, `dissolved_oxygen`, `temperature_c`.
2. **Derivative Kinetics & Temporal Spikes**:
   - `pH_rate`, `turbidity_rate`, `EC_rate`, `TDS_rate`, `DO_rate`.
3. **Rolling Baselines & Deviations**:
   - `rolling_mean_pH`, `rolling_mean_turbidity`, `rolling_mean_EC`, `rolling_mean_TDS`, `rolling_mean_DO`.
   - `rolling_std_pH`, `rolling_std_turbidity`, `rolling_std_EC`, `rolling_std_TDS`, `rolling_std_DO`.
4. **Non-linear Derived Scores**:
   - `acidity_shift_score` ($|pH - 7.0|$).
   - `degradation_spike_score` ($Turbidity / Rolling\_Mean$).
   - `conductivity_shift_score` ($EC / Rolling\_Mean$).
   - `oxygen_drop_score` ($\max(0.0, 8.0 - DO)$).
   - `persistence_score` (Continuous contamination duration).

## 3. Explicit Feature Order for Inference
```json
[
  "pH", "turbidity", "EC", "TDS", "dissolved_oxygen", "temperature_c",
  "pH_rate", "turbidity_rate", "EC_rate", "TDS_rate", "DO_rate",
  "rolling_mean_pH", "rolling_mean_turbidity", "rolling_mean_EC", "rolling_mean_TDS", "rolling_mean_DO",
  "rolling_std_pH", "rolling_std_turbidity", "rolling_std_EC", "rolling_std_TDS", "rolling_std_DO",
  "acidity_shift_score", "degradation_spike_score", "conductivity_shift_score", "oxygen_drop_score", "persistence_score"
]
```
