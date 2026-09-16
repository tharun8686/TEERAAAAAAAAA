# REAL HARDWARE TEST PLAN — TERRAEDGE PHASE 4

This document outlines the 22 required physical tests to verify end-to-end functionality from the ESP32-S3 sensor node to the live web dashboard.

| Test | Objective | Result | Notes |
|---|---|---|---|
| **Test 1: ESP32 boots** | Verify the ESP32-S3 powers on and initializes Serial output. | [ ] | Check Serial Monitor at 115200 baud. |
| **Test 2: BME680 reading** | Verify temperature, humidity, pressure, and gas resistance. | [ ] | Confirm plausible I2C readings on Serial. |
| **Test 3: SDS011 reading** | Verify PM2.5 and PM10 values. | [ ] | Confirm UART communication and valid checksums. |
| **Test 4: MQ135 reading** | Verify raw gas proxy ADC value. | [ ] | Breathe on sensor; confirm ADC value changes. |
| **Test 5: Rain reading** | Verify rain/wetness analog percentage. | [ ] | Drop water on the sensor board. |
| **Test 6: Water level** | Verify analog water level percentage (if wired). | [ ] | Submerge analog sensor to different depths. |
| **Test 7: JSN-SR04T** | Verify ultrasonic distance & derived water level. | [ ] | Place object in front of sensor, check `ud` and `wl`. |
| **Test 8: Soil moisture** | Verify capacitive soil moisture percentage. | [ ] | Insert into dry vs. wet soil. |
| **Test 9: MPU6050** | Verify accelerometer tilt magnitude. | [ ] | Tilt the breadboard; verify `tm` changes (I2C). |
| **Test 10: SW420** | Verify vibration rate (pulses/min). | [ ] | Tap the sensor; verify `vr` > 0. |
| **Test 11: Flame** | Verify IR flame detection. | [ ] | Point a lighter at the sensor (carefully!). |
| **Test 12: pH** | Verify pH analog voltage to pH scale. | [ ] | Test in pH 4, 7, 10 buffer solutions. |
| **Test 13: TDS** | Verify TDS ppm reading. | [ ] | Test in distilled vs. tap vs. salty water. |
| **Test 14: Turbidity** | Verify NTU reading. | [ ] | Test in clear vs. muddy water. |
| **Test 15: GPS** | Verify NEO-6M gets a fix. | [ ] | Test outdoors; verify `lat` and `lon` are populated. |
| **Test 16: Battery** | Verify battery voltage/percentage. | [ ] | Verify ADC correctly reads the voltage divider. |
| **Test 17: LoRa transmit** | Verify ESP32 transmits LoRa packet. | [ ] | Check "TX seq=..." in Serial Monitor. |
| **Test 18: LoRa receive** | Verify Type B Gateway receives LoRa packet. | [ ] | Check gateway terminal for `[LORA RX]`. |
| **Test 19: Gateway inference** | Verify packet routes to ML models. | [ ] | Check gateway terminal for `Flood inference success` etc. |
| **Test 20: Supabase persistence** | Verify telemetry and predictions save to DB. | [ ] | Check Supabase tables (`telemetry`, `predictions`). |
| **Test 21: Dashboard update** | Verify web dashboard updates with new data. | [ ] | Open `index.html` and wait for polling interval. |
| **Test 22: Web alert** | Verify high severity creates dashboard alert. | [ ] | Simulate fire or flood; verify `🚨 ALERT` banner on UI. |

## Execution Protocol
1. Flash `terraedge_node.ino` to the ESP32-S3.
2. Start the Gateway (`python -m gateway.app`).
3. If using a real SX1278 on the gateway, start the bridge script (`python hardware/usb_serial_bridge.py`). If not, use the simulator.
4. Mark the results in the table above (PASS/FAIL/NOT TESTED).
