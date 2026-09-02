# Phase 1: USGS Cleveland Corral Landslide Dataset Audit Report

## Executive Summary
- **Total Monitoring Files:** `44` CSV workbooks across 3 physical landslide zones.
- **Landslide Monitoring Zones**:
  - **Middle Station**: 22 files (WY1997 – WY2018)
  - **Toe Station**: 20 files (WY1997 – WY2017)
  - **Upper Station**: 2 files (WY1998 – WY1999)

## Physical Sensor Parameters Available
1. **Downslope Ground Displacement (cm)**: Extensometers (`mid_E1`, `mid_E2_A`, `mid_E2_B`, `toe_E3`, `toe_E4_A`, `toe_E5_A`, `toe_E5_B`, `toe_E5_C`).
2. **Groundwater Pore Pressure / Head (cm)**: Piezometers (`mid_P1`, `mid_P2`, `mid_P3`, `toe_P7_A`, `toe_P8_A`, `toe_P9_A`).
3. **Rainfall Accumulation (mm)**: Rain Gauge (`mid_R`, 15-minute intensity & cumulative).
4. **Soil Water Content**: Volumetric soil moisture (`toe_M1_A`, `toe_M1_B`).

## Sensor Quality & Continuity Audit (Metadata Notes)
- **Sensor Replacements & Cable Breakages**: Metadata documents instrument destruction during major ground movement (e.g. `mid_E2_A` destroyed in 2002, replaced by `mid_E2_B`; `toe_E5_C` post toppled in 2017).
- **Rule Uheld**: Sensor periods with suffixes `_A`, `_B`, `_C` must NOT be concatenated as fake continuous sensors. They will be processed as distinct operational deployments.

## Hardware Mapping to Type-A Node
| Physical Parameter | Cleveland USGS Sensor | Type-A Hardware Equivalent | Edge Deployment Status |
| --- | --- | --- | --- |
| Soil Water Content | `toe_M1_A/B` | Capacitive Soil Moisture | **Local Primary Input** |
| Slope Displacement | Extensometers (`mid_E2_A`) | MPU6050 (Roll/Pitch/Tilt Rate) | **Local Deformation Proxy** |
| Microseismic / Vibration | Geophone / Strain | SW-420 Vibration Sensor | **Local Anomaly Support** |
| Ambient Weather | Weather station | DHT22 (Temp & Humidity) | **Local Weather Context** |
| Atmospheric Pressure | Barometer | BMP280 Pressure | **Local Weather Context** |
| Rainfall Accumulation | `mid_R` | External Rain Gauge / Weather API | **Optional External Context** |
| Pore-Water Pressure | `mid_P1..P5` | *None* | **Research Precursor Only** |
