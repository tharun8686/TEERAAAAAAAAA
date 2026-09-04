# Toxic Flame Edge Feasibility Report

## 1. Embedded Sensor Node Architecture
- **Microcontroller**: ESP32-S3 (Dual-core 240MHz).
- **Sensors**:
  - MQ-135 / MQ-2 / MQ-7 Gas Sensor Array (Multi-channel ADC with temperature compensation)
  - Plantower PMS5003 (UART)
  - IR Flame Phototransistor (Fast digital interrupt)
  - BME680 (I2C)

## 2. Resource Consumption
- **Storage**: 2.7 KB (Classifier) + 13 KB (Calibrator) + 1.0 MB (Isolation Forest).
- **RAM Heap Buffer**: < 16 KB.
- **Inference Latency**: 0.4 ms on ESP32-S3.
- **Intrinsic Safety**: Operates in an explosion-proof IP66 enclosure with Zener barrier circuit isolation.
