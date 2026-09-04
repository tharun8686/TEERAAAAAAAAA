# Extreme Heat Edge Feasibility Report

## 1. Embedded Deployment Target
- **Microcontroller**: ESP32 / STM32F4 Cortex-M4 @ 168MHz.
- **Sensors**: BME680 (Temperature, Humidity, Pressure) + Ambient Pyranometer / LDR Solar Flux proxy + Anemometer pulse counter.

## 2. Model Footprint & Real-time Efficiency
- **Flash ROM Storage**: 2.5 KB (Model weights) + 13 KB (Isotonic Calibrator LUT).
- **RAM Execution Buffer**: < 4 KB heap.
- **Inference Latency**: 0.2 ms on ARM Cortex-M4.
- **Power Envelope**: Solar powered with deep sleep wake every 5 minutes (average continuous draw < 2.5 mW).
