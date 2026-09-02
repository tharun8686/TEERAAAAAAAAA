# Industrial Emissions Data Audit Report

## India AQI Baseline
- **Rows:** 3493
- **Cols:** 11
- **Columns:** ['country', 'state', 'city', 'station', 'last_update', 'latitude', 'longitude', 'pollutant_id', 'pollutant_min', 'pollutant_max', 'pollutant_avg']
- **Missing Values:**
  - `pollutant_min`: 320
  - `pollutant_max`: 320
  - `pollutant_avg`: 320

## MQ-Series Gas Sensor Measurements
- **Rows:** 6400
- **Cols:** 9
- **Columns:** ['Serial Number', 'MQ2', 'MQ3', 'MQ5', 'MQ6', 'MQ7', 'MQ8', 'MQ135', 'Gas']
- **Gas Distribution:**
  - `NoGas`: 1600
  - `Perfume`: 1600
  - `Smoke`: 1600
  - `Mixture`: 1600

## Flow Modulation Features
- **Rows:** 58
- **Cols:** 439
- **Ethylene Conc Range:** 0.0 to 1.0

## UCI Gas Sensor Array Drift
- Found 10 batch files (.dat in LIBSVM format).
- Represents long-term drift robustness over 36 months.

## UCI Dynamic Gas Mixtures
- Found 2 massive time-series files (Ethylene/CO and Ethylene/Methane mixes).

