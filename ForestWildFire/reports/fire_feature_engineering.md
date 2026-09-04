# Wildfire Feature Engineering Report

## 1. Physical Combustion & Gas Physics
Forest wildfires undergo smoldering pyrolysis before flaming combustion, releasing carbon monoxide ($CO$), volatile organic compounds ($TVOC$), fine carbonaceous particulates ($PM_{2.5}$), and altering local vapor pressure deficits ($VPD$).

## 2. Feature Vectors & Rate Differentials
1. **Thermodynamic Indices**:
   - `temperature`: Ambient dry bulb temperature (°C).
   - `humidity`: Ambient moisture (%), inversely driving fuel flammability.
   - `pressure`: Atmospheric barometric pressure (hPa).
   - `temperature_rate` & `humidity_rate`: Rapid short-term derivative shifts ($\Delta / \Delta t$).
2. **Pyrolysis & Combustion Products**:
   - `pm25`: Fine particulate concentration ($\mu g/m^3$).
   - `tvoc`: Total volatile organic compounds ($ppb$).
   - `raw_ethanol`: Micro-machined gas sensor resistive proxy for organic combustion.
   - `pm25_rate` & `tvoc_rate`: Temporal slopes confirming active combustion plume vs ambient dust.
3. **Short-Horizon Step Shifts**:
   - `temperature_delta_5` & `humidity_delta_5`: 5-minute step change indicators capturing sudden flame fronts.

## 3. Explicit Feature Order for Inference (12 Features)
```json
[
  "temperature", "humidity", "pressure", "pm25", "tvoc", "raw_ethanol",
  "temperature_rate", "humidity_rate", "pm25_rate", "tvoc_rate",
  "temperature_delta_5", "humidity_delta_5"
]
```
