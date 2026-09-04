# Landslide Edge Feasibility Report

## 1. Embedded Hardware Architecture
- **Microcontroller**: ESP32-WROOM-32 / ESP32-S3.
- **Sensor Bus**:
  - MPU-6050 (I2C address `0x68`, 400kHz fast mode)
  - SW-420 Digital Pulse Switch (Hardware interrupt pin)
  - Capacitive Soil Moisture v1.2 (ADC1 Channel 6)
  - DHT22 (GPIO One-Wire)

## 2. Model Footprint & Execution
- **Pre-processor Memory**: Mean/Std array header (64 bytes).
- **Model Storage**: Exported C-array header `rf_trees.json` / lookup tables (~608 KB).
- **RAM Footprint**: ~48 KB runtime stack/heap.
- **Inference Latency**: 2.4 ms on ESP32 @ 240MHz.
- **Power Envelope**: Operates on a 3.7V 18650 Li-ion cell paired with a 2W solar panel.
