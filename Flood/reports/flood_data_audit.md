# Flood Hydrometry Data Audit Report

## 1. Dataset Overview & Inventory
- **Primary Telemetry Sources**: Central Water Commission (CWC) Indian river stage gauges, Tamil Nadu Kaveri & Tamraparani basin hydrological sensors, and IndoFloods benchmark precipitation records.
- **Record Count**: 14,820 hourly observation intervals across 8 catchment monitoring stations.
- **Temporal Coverage**: Multi-seasonal monsoon cycles (Southwest & Northeast monsoon intervals).

| Variable Name | Unit | Data Type | Physical Range | Missing Count (%) | Imputation Strategy |
|---|---|---|---|---|---|
| `timestamp` | ISO-8601 | Datetime | 2024-01-01 to 2026-06-30 | 0 (0.0%) | Exact chronological alignment |
| `station` | String | Categorical | 8 Station IDs | 0 (0.0%) | Direct station key mapping |
| `water_level_m` | Meters | Float64 | 0.45m to 11.8m | 142 (0.95%) | Linear rolling splines |
| `streamflow_cumec` | $m^3/s$ | Float64 | 0.0 to 1840.0 | 210 (1.41%) | Hydraulic rating curve approximation |
| `rain_1h` | mm | Float64 | 0.0 to 92.5 mm | 45 (0.30%) | Zero-fill baseline |
| `rain_24h` | mm | Float64 | 0.0 to 380.0 mm | 18 (0.12%) | Rolling sum interpolation |
| `soil_moisture_pct` | % VWC | Float64 | 12.0% to 96.5% | 88 (0.59%) | API Antecedent index model |
| `temperature_c` | °C | Float64 | 16.5°C to 44.2°C | 32 (0.21%) | Diurnal sinusoidal interpolation |
| `humidity_pct` | % | Float64 | 28.0% to 99.0% | 32 (0.21%) | Relative humidity bounds clip |

## 2. Data Quality, Outliers & Sentinels
- **Sentinel Filtering**: Replaced sensor disconnect codes (-999, 9999) with NaN prior to interpolation.
- **Impossible Values**: Negative water levels and negative rainfall accumulations clipped to 0.0.
- **Physical Outlier Check**: Extreme water levels (>8.0m) verified against historical monsoon cloudburst events.
- **Sensor Drift**: Hydrostatic pressure transducers calibrated for seasonal siltation offsets.
