# Phase 1: WSN Landslide Dataset Audit Report

## Dataset Overview
- **Total Rows:** `9,864`
- **Total Columns:** `35`
- **Total Missing Values:** `0`
- **Duplicate Rows:** `0`
- **Target Column:** `Label`
- **Label Balance:** Class 0 (`4,905`) | Class 1 (`4,959`)

## Critical Audit Findings & Scope Restrictions
1. **No Temporal / Event Identity**: `wsn_landslide_data.csv` lacks timestamps, node IDs, or event IDs. It represents a synthetic/i.i.d. feature distribution.
2. **Supervised Baseline Role Only**: Suitable for Random Forest / XGBoost baseline feature importance and physical correlation analysis. **Cannot** be used to claim chronological lead-time or temporal early warning.
3. **Post-Event & Static Feature Warning**: Contains static GIS features (`Elevation_m`, `Aspect`, `NDVI_Index`, `Land_Use_*`) and historical indicators (`Historical_Landslide_Count`) that are NOT available on a local Type-A sensor node.

## Feature Group Classification
- **Hydrological**: `Rainfall_mm`, `Rainfall_3Day`, `Rainfall_7Day`, `Soil_Saturation`, `Pore_Water_Pressure_kPa`, `Soil_Moisture_Content`
- **Mechanical**: `Slope_Angle`, `Microseismic_Activity`, `Acoustic_Emission_dB`, `Soil_Strain`, `TDR_Reflection_Index`
- **Weather**: `Temperature_C`, `Humidity_percent`, `Soil_Temperature_C`
- **Terrain / Static**: `Elevation_m`, `Aspect`, `Vegetation_Cover`, `NDVI_Index`, `Proximity_to_Water`, `Distance_to_Road_m`
- **Soil Physics**: `Soil_pH`, `Clay_Content`, `Sand_Content`, `Silt_Content`, `Soil_Type_*`
- **Land Use & History**: `Land_Use_*`, `Earthquake_Activity`, `Historical_Landslide_Count`, `Soil_Erosion_Rate`

## Summary Statistics Preview
| Feature | Min | Max | Mean | Std | Nulls | Unique |
| --- | --- | --- | --- | --- | --- | --- |
| `Rainfall_mm` | `0.0006` | `299.9851` | `125.6436` | `105.8858` | `0` | `9864` |
| `Slope_Angle` | `5.0008` | `79.9878` | `36.0233` | `25.1501` | `0` | `9864` |
| `Soil_Saturation` | `0.1` | `0.9999` | `0.525` | `0.3331` | `0` | `9864` |
| `Vegetation_Cover` | `0.0001` | `1.0` | `0.476` | `0.342` | `0` | `9864` |
| `Rainfall_3Day` | `0.01` | `599.9833` | `298.3247` | `174.137` | `0` | `9864` |
| `Rainfall_7Day` | `0.0084` | `999.9397` | `503.3974` | `287.8079` | `0` | `9864` |
| `Aspect` | `0.0972` | `359.8884` | `179.6569` | `103.6354` | `0` | `9864` |
| `Elevation_m` | `100.377` | `2999.6378` | `1554.2779` | `830.1931` | `0` | `9864` |
| `NDVI_Index` | `-0.0998` | `0.8999` | `0.4016` | `0.2907` | `0` | `9864` |
| `Land_Use_Urban` | `0.0` | `1.0` | `0.5038` | `0.5` | `0` | `2` |

*(Full 35-feature statistics saved to [`reports/wsn_feature_summary.csv`](file:///c:/Users/TEJESHWAR/OneDrive/Desktop/Terra Edge/Landslide/reports/wsn_feature_summary.csv))*