# Landslide Geotechnical Data Audit Report

## 1. Data Sources & Geological Testbeds
- **Cleveland Corral Geotechnical Station (USGS)**: 23,400 hours of continuous slope deformation, pore-water pressure, volumetric water content, and rainfall monitoring.
- **WSN Sub-surface Borehole Mesh**: Multi-depth capacitive moisture array (10cm, 30cm, 60cm, 100cm), triaxial MPU-6050 inclinometer logs, and SW-420 micro-seismic geophone pulse records.

## 2. Telemetry Variables & Audit Summary

| Feature Name | Sensor / Origin | Engineering Unit | Nominal Range | Missing (%) | Processing Method |
|---|---|---|---|---|---|
| `soil_moisture_vwc` | Capacitive VWC Probes | Volumetric ($m^3/m^3$) | 0.08 to 0.58 | 0.42% | Cubic Hermite splines |
| `soil_moisture_rate` | Derivative $\Delta VWC / \Delta t$ | $1/h$ | -0.05 to +0.08 | 0.00% | 15-minute backward backward finite difference |
| `tilt_magnitude` | MPU-6050 Accelerometer | Degrees (°) | 0.0° to 48.0° | 0.15% | Vector magnitude $\sqrt{a_x^2 + a_y^2 + a_z^2}$ |
| `tilt_rate` | Derivative $\Delta \theta / \Delta t$ | °/s or °/h | 0.0 to 5.5 | 0.00% | Rolling 5-minute angular velocity |
| `vibration_rate` | SW-420 Geophone Switch | RMS Pulse Count | 0.0 to 120.0 | 0.10% | Moving acoustic energy window |
| `rainfall_24h` | Tipping Bucket Gauge | mm | 0.0 to 240.0 mm | 1.10% | External context; fallback to 0 if absent |
| `temperature` | DHT22 / BME280 | °C | 8.0°C to 38.0°C | 0.05% | Linear interpolation |
| `humidity` | DHT22 / BME280 | % RH | 30.0% to 99.0% | 0.05% | Relative humidity bounds clip |

## 3. Data Integrity & Proxy Considerations
- MPU-6050 and SW-420 operate as non-invasive surface proxies for sub-surface inclinometer displacement and acoustic shear strain.
- Zero-drift offset calibration applied to gyro axes to prevent false tilt creep alarms.
