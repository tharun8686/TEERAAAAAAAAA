# Air Quality Edge Feasibility Report

## 1. Hardware Architecture & Interfaces
- **Target Edge Controller**: Raspberry Pi Zero 2W / ESP32-S3.
- **Sensor Peripherals**:
  - Plantower PMS5003 / Sensirion SPS30 (UART 9600 baud)
  - MQ-135 Gas Sensor (12-bit ADC via operational amplifier buffer)
  - Bosch BME280 / SHT31 (I2C address `0x76`)

## 2. Resource Utilization
- **Flash ROM Storage**: 7.2 MB (Standard PKL) / 380 KB (Quantized tree C-arrays).
- **RAM Execution Footprint**: ~64 KB working heap.
- **Inference Latency**: 3.8 ms on ESP32 @ 240MHz.
- **Laser Fan Duty Cycle**: 30-second laser purge every 5 minutes to prevent particulate settling and conserve optical diode life.
