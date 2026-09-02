# ForestWildFire AI - Comprehensive Data Audit Report

**Generated Date:** 2026-08-26

## Executive Summary

This report presents a thorough data audit across all 8 uploaded datasets for the Forest Wildfire Edge-AI Module. Every dataset was analyzed for shape, data types, missing values, duplicates, time ranges, sampling frequencies, target class distributions, and sensor ranges.


---
## 1. Primary Dataset (Long Format): `forest_fire_sensor_fusion_raw.csv.gz.csv`

- **Total Rows:** `876,820`
- **Columns:** `['NAME', 'TIME', 'VALUE']` (Dtypes: `{'NAME': <StringDtype(storage='python', na_value=nan)>, 'TIME': dtype('int64'), 'VALUE': dtype('float64')}`)
- **Missing Values:** `{'NAME': 0, 'TIME': 0, 'VALUE': 0}`
- **Duplicate Rows:** `0`
- **Unique Sensor Signals (`NAME`):** `14` signals
```text
  - Temperature[C]: 62,630 readings
  - Humidity[%]: 62,630 readings
  - TVOC[ppb]: 62,630 readings
  - eCO2[ppm]: 62,630 readings
  - Raw H2: 62,630 readings
  - Raw Ethanol: 62,630 readings
  - Pressure[hPa]: 62,630 readings
  - PM1.0: 62,630 readings
  - PM2.5: 62,630 readings
  - NC0.5: 62,630 readings
  - NC1.0: 62,630 readings
  - NC2.5: 62,630 readings
  - CNT: 62,630 readings
  - Fire Alarm: 62,630 readings
```
- **Time Range (assuming unix epoch seconds):** `55041857723-05-16 00:00:00` to `55043842357-05-17 04:26:40`
- **Target (`Fire Alarm`) Class Distribution:** `{1.0: 44757, 0.0: 17873}`

---
## 2. Compact Baseline Dataset: `fire_data.csv`

- **Total Rows:** `6,121`
- **Columns:** `['eco2', 'humidity', 'pressure', 'raw_ethanol', 'raw_h2', 'temperature', 'timestamp', 'fire_alarm']`
- **Missing Values:** `{'eco2': 0, 'humidity': 0, 'pressure': 0, 'raw_ethanol': 0, 'raw_h2': 0, 'temperature': 0, 'timestamp': 0, 'fire_alarm': 0}`
- **Duplicate Rows:** `0`
- **Target (`fire_alarm`) Class Distribution:** `{0: 3263, 1: 2858}` (Normal 0: 3,263, Fire 1: 2,858)

### Numerical Summary Statistics (`fire_data.csv`):
```text
                    min         mean          std         50%          max
eco2          400.00000  1295.999510  2748.151382   676.00000  65000.00000
humidity       23.12517    53.587865    15.887435    57.08742     77.46019
pressure     1005.50000  1006.083358     0.217600  1006.09003   1006.70001
raw_ethanol  1606.00000  2994.812286   273.917184  3041.00000   3603.00000
raw_h2         25.00000   116.727986   102.059461    70.00000    862.00000
temperature    31.40011    41.140102     9.687304    37.46166     67.10129
timestamp       9.00000  1963.403365  1368.102618  1591.00000   4707.00000
fire_alarm      0.00000     0.466917     0.498945     0.00000      1.00000
```

---
## 3. Resisto OOD Dataset: `forest_fire_resisto_raw.csv.csv`

- **Total Rows:** `497,749`
- **Columns:** `['id', 'time', 'site_id', 'sensor_ns_id', 'fire_alert_status', 'temperature_c', 'humidity_percent', 'air_pressure_pa', 'latitude', 'longitude']`
- **Missing Values:** `{'id': 0, 'time': 0, 'site_id': 0, 'sensor_ns_id': 0, 'fire_alert_status': 0, 'temperature_c': 0, 'humidity_percent': 0, 'air_pressure_pa': 0, 'latitude': 0, 'longitude': 0}`
- **Duplicate Rows:** `0`
- **Labels (`fire_alert_status`):** `{0: 496789, 2: 956, 1: 4}` (0 = no alert, 1 = pre-alert, 2 = fire alert)

### Resisto Numerical Summary Statistics:
```text
                           min           mean          std            50%            max
temperature_c        -1.000000      21.103289     7.104843      20.000000      53.400000
humidity_percent     -1.000000      29.109774    36.667668      -1.000000     100.000000
air_pressure_pa   62081.000000  101251.217935  1208.919231  101127.000000  103691.000000
latitude             37.136984      37.201002     0.431534      37.163786      42.655321
longitude            -6.694643      -6.559145     0.522433      -6.646633      -0.096548
```

---
## 4. Gas & Optical Experiment Workbooks (.xlsx)

### `cng_sensor.xlsx`
- **Sheet Count:** `4` sheets: `['cng_concentration_2022_03_08', 'cng_concentration_2022_03_09', 'cng_concentration_2022_03_10', 'cng_concentration_2022_03_11']...`
- **Sample Sheet (`cng_concentration_2022_03_08`) Rows:** `2,035` | **Columns:** `['time', 'data_type', 'unit', 'data_value']`
- **Missing Values:** `{'time': 0, 'data_type': 0, 'unit': 0, 'data_value': 0}`
---
### `co_sensor.xlsx`
- **Sheet Count:** `4` sheets: `['co_concentration_2022_03_08', 'co_concentration_2022_03_09', 'co_concentration_2022_03_10', 'co_concentration_2022_03_11']...`
- **Sample Sheet (`co_concentration_2022_03_08`) Rows:** `2,036` | **Columns:** `['time', 'data_type', 'unit', 'data_value']`
- **Missing Values:** `{'time': 0, 'data_type': 0, 'unit': 0, 'data_value': 0}`
---
### `flame_sensor.xlsx`
- **Sheet Count:** `4` sheets: `['flame_indicator_2022_03_08', 'flame_indicator_2022_03_09', 'flame_indicator_2022_03_10', 'flame_indicator_2022_03_11']...`
- **Sample Sheet (`flame_indicator_2022_03_08`) Rows:** `2,035` | **Columns:** `['time', 'data_type', 'unit', 'data_value']`
- **Missing Values:** `{'time': 0, 'data_type': 0, 'unit': 0, 'data_value': 0}`
---
### `lpg_sensor.xlsx`
- **Sheet Count:** `4` sheets: `['lpg_concentration_2022_03_08', 'lpg_concentration_2022_03_09', 'lpg_concentration_2022_03_10', 'lpg_concentration_2022_03_11']...`
- **Sample Sheet (`lpg_concentration_2022_03_08`) Rows:** `2,035` | **Columns:** `['time', 'data_type', 'unit', 'data_value']`
- **Missing Values:** `{'time': 0, 'data_type': 0, 'unit': 0, 'data_value': 0}`
---
### `smoke_sensor.xlsx`
- **Sheet Count:** `4` sheets: `['smoke_concentration_2022_03_08', 'smoke_concentration_2022_03_09', 'smoke_concentration_2022_03_10', 'smoke_concentration_2022_03_11']...`
- **Sample Sheet (`smoke_concentration_2022_03_08`) Rows:** `2,036` | **Columns:** `['time', 'data_type', 'unit', 'data_value']`
- **Missing Values:** `{'time': 0, 'data_type': 0, 'unit': 0, 'data_value': 0}`
---

---
## 5. Audit Decisions & Next Steps (Phase 1 Conclusion)

1. **Primary Dataset Pivoting (Phase 2):** `forest_fire_sensor_fusion_raw.csv.gz.csv` contains 876,820 long-format entries across 14 signals. In Phase 2, we will pivot this into wide format (`data/intermediate/fire_sensor_wide.csv`) where each row represents an exact timestamp.

2. **Label Integrity:** No synthetic labels were fabricated. The `fire_alarm` signal from the sensor fusion dataset will serve as ground truth for Phase 3 (baseline model training).

3. **Resisto & Sensor Experiments Separation:** Resisto and individual gas sensor Excel files will be strictly kept separate and reserved for Phase 5 (OOD Validation) and Phase 6 (Robustness Analysis) respectively.
