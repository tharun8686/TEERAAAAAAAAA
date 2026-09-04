# Landslide Feature Engineering Report

## 1. Feature Representation & Geotechnical Mechanics
Slope stability depends fundamentally on the Mohr-Coulomb failure criterion:
$$\tau_f = c' + (\sigma_n - u) \tan \phi'$$
Where rising pore-water pressure ($u$) and soil saturation reduce effective shear resistance until failure occurs ($F_s < 1.0$).

## 2. Engineered Telemetry Vectors
1. **Saturation Dynamics**:
   - `soil_moisture_vwc`: Instantaneous saturation.
   - `soil_moisture_rate`: Rapid infiltration indicates loss of matric suction.
2. **Kinematic Deformation**:
   - `tilt_magnitude`: Angular excursion relative to gravitational plumb line.
   - `tilt_rate`: Acceleration of slope creep, signaling progressive shearing.
3. **Seismic & Acoustic Emission**:
   - `vibration_rate`: Micro-fracture energy and grain-to-grain frictional acoustic pulses.
4. **Hydrometeorological Forcing**:
   - `rainfall_24h`: Macro-inundation driving pore pressure buildup.
   - `temperature` & `humidity`: Evapotranspiration moisture loss indicators.

## 3. Explicit Feature Order for Inference
```json
[
  "soil_moisture_vwc", "soil_moisture_rate",
  "tilt_magnitude", "tilt_rate", "vibration_rate",
  "temperature", "humidity", "rainfall_24h"
]
```
