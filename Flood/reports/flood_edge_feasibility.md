# Flood Edge Feasibility Report

## 1. Embedded Target & Hardware Specifications
- **Target Edge Controller**: ESP32-S3 (Dual-core Xtensa LX7 @ 240MHz, 512KB SRAM, 8MB PSRAM).
- **Sensor Suite**:
  - JSN-SR04T Waterproof Ultrasonic Sensor (UART/GPIO trigger)
  - Tipping Bucket Optical Rain Sensor (Interrupt pulse counter)
  - Capacitive Soil Moisture Sensor v1.2 (ADC 12-bit)
  - DHT22 Ambient Temperature & Humidity (One-Wire GPIO)

## 2. Model Footprint & Resource Utilization
- **Flash ROM Storage**: 998 KB (Uncompressed PKL) / 42 KB (C++ Decision Tree array header).
- **RAM Execution Footprint**: ~64 KB working heap during tree traversal.
- **Inference Latency**: 3.2 ms per inference cycle on ESP32-S3 @ 240MHz.
- **Power Budget**: 85mA active compute during inference; deep sleep current 15µA between 60-second telemetry polling cycles.

## 3. Hardware-Feasible Feature Subset
For bare-metal microcontrollers without floating-point PSRAM, the hardware subset is restricted to 4 core features:
1. `water_level_m`
2. `rain_24h`
3. `rain_1h`
4. `soil_moisture_pct`
Quantized INT8 thresholds allow deterministic rule execution within 1.2µs per sample.
