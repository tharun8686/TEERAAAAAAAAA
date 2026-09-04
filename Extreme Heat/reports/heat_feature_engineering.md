# Extreme Heat Feature Engineering Report

## 1. Biometeorological Formulations
Extreme heat stress is governed by ambient dry-bulb temperature, relative humidity (controlling evaporative sweat dissipation), direct solar shortwave radiative flux, and convective wind cooling.

## 2. Telemetry & Derived Mathematical Indices
1. **Core Atmospheric Feeds**:
   - `temperature_c`: Dry-bulb temperature (°C).
   - `humidity`: Ambient relative humidity (%).
   - `solar_radiation`: Global horizontal solar irradiance ($W/m^2$).
   - `wind_speed_kmh`: Convective wind velocity ($km/h$).
2. **Dynamic Rates & Thermal Accumulation**:
   - `temperature_rate`: Rapid morning solar heating rate ($^\circ\text{C}/h$).
   - `cumulative_hot_hours`: Number of consecutive hours exceeding $35^\circ\text{C}$.
   - `nighttime_cooling_deficit`: Inability of nighttime minimum temperatures to drop below $25^\circ\text{C}$, elevating cardiac stress.
   - `rolling_mean_temperature` & `rolling_std_temperature`: Macro diurnal baseline tracking.

## 3. Explicit Feature Order for Inference
```json
[
  "temperature_c", "humidity", "solar_radiation", "rainfall_mm", "wind_speed_kmh",
  "temperature_rate", "humidity_rate", "solar_radiation_rate",
  "rolling_mean_temperature", "rolling_mean_humidity",
  "rolling_std_temperature", "rolling_std_humidity",
  "cumulative_hot_hours", "nighttime_cooling_deficit"
]
```
