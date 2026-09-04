# Wildfire Edge Feasibility Report

## 1. Edge Node Hardware Platform
- **MCU**: ESP32-S3 / ESP32-WROOM-32.
- **Peripherals**:
  - Sensirion SGP40 / BME680 (VOC index, Temperature, Humidity, Pressure via I2C)
  - Plantower PMS5003 / SDS011 (Laser particulate optical sensor via UART)
  - IR Flame Photodiode Sensor (Digital Interrupt Pin)

## 2. Resource Utilization
- **Flash ROM Storage**: 330 KB (Compact Random Forest PKL) / 48 KB (C-tree header).
- **RAM Heap Consumption**: ~32 KB during tree inference.
- **Inference Execution Time**: 1.8 ms on ESP32 @ 240MHz.
- **Duty Cycle**: Sensor fan pulse 10s every 60s to conserve optical laser lifespan and power.
