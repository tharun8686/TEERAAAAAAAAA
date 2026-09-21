# Sensor-to-dashboard setup and audit

The supported live path is:

`SENDER.ino → SX1278 LoRa → RECEIVER.ino → USB → /api/hardware → model readiness checks → /live`

The receiver forwards the exact received bytes. It does not run the trained models:
those model artifacts run in the Python gateway. JSON float serialization limits
decimal precision; this is not a guarantee of laboratory sensor accuracy. No layer
replaces missing values with plausible-looking readings.

## Start the software

From the project directory in PowerShell:

```powershell
python -m venv .venv
.venv\Scripts\python -m pip install -r requirements.txt
.venv\Scripts\python -m uvicorn gateway.app:app --host 127.0.0.1 --port 8000
```

Open **http://127.0.0.1:8000/live** in Chrome or Edge. Click **Connect receiver USB**
and select the receiver. The existing `index.html` links to this live dashboard.
Port 8000 must run `gateway.app`, not the standalone Flood service.

Alternatively, keep the gateway running and start this in another terminal:

```powershell
.venv\Scripts\python lora_serial_bridge.py COM4
```

Replace COM4 with the receiver's actual port. In this mode the dashboard polls the
gateway; do not also click its USB button. Close Arduino Serial Monitor first.
Only one program can own the serial port. Both bridges use 115200 baud.

The built-in gateway receiver also understands v4 when `LORA_ENABLED=true` and
`LORA_SERIAL_PORT` is set. Choose **one** serial owner. LoRa ACK/downlink is not
implemented by the root receiver: keep `LORA_ACK_ENABLED=false` for these sketches.
Neither packet delivery nor offline buffering is guaranteed. HTTP retries are
bounded; failed delivery is logged. Partial RF frames expire after 20 seconds.

## Prepare and flash separate sketches

Arduino must not compile SENDER and RECEIVER together in the root folder:

```powershell
.venv\Scripts\python hardware/prepare_sketches.py
```

Open `build/arduino/SENDER/SENDER.ino` and
`build/arduino/RECEIVER/RECEIVER.ino` separately in Arduino IDE. Edit the maintained
root files and `hardware_config.h`, then rerun the copy command after edits.

Required libraries: Arduino ESP32 core, LoRa by Sandeep Mistry, ArduinoJson **6.x**,
Adafruit BME680, Adafruit MPU6050, Adafruit Unified Sensor and Adafruit BusIO.
TinyGPSPlus is needed only when ENABLE_GPS is enabled. Select the actual ESP32 Dev Module or ESP32S3 Dev Module for each board.
Other ESP32 families deliberately fail compilation until a verified pin map exists.
For S3 native USB, enable USB CDC On Boot. Select the port corresponding to the board
you are flashing. Firmware compilation and physical flashing are still required;
they were not verified in the agent session.

Both radios use 433 MHz, SF7, 125 kHz bandwidth, CR4/5, sync word 0x34 and CRC.
LoRa packets are bounded to 250 bytes. The sender splits larger snapshots by field;
the gateway requires every fragment before exposing the snapshot. `(node, boot,
sequence)` identifies a reading, allowing sequence reset after reboot. Late frames,
duplicates and conflicting fragments are rejected. No reassembly state survives
a gateway restart. Give every sender a unique `NODE_ID`.

## Wiring profiles to verify against your actual boards

These are GPIO numbers, not header positions. The S3 profile matches the supplied
wiring; the ESP32 Dev profile is retained for a separately wired legacy board.

| Signal | ESP32-S3 sender | ESP32 Dev sender |
|---|---:|---:|
| I²C SDA / SCL | 8 / 9 | 21 / 22 |
| LoRa SCK / MISO / MOSI | 13 / 12 / 11 | 18 / 19 / 23 |
| LoRa NSS / RESET / DIO0 | 10 / 14 / 47 | 5 / 14 / 2 |
| MQ-7 analog through divider | 7 | 34 |
| Rain plate analog | 1 | 35 |
| Water probe analog | 2 | 32 |
| Soil analog | 3 | 33 |
| pH / TDS / turbidity analog | 4 / 5 / 6 | 36 / 39 / 25 |
| Flame / SW420 digital | 15 / 16 | 27 / 13 |
| Ultrasonic TRIG / ECHO | 17 / 18 | 12 / 4 |
| GPS receiver input (disabled) | unassigned | 16 |

Receiver LoRa pins use the same profile for its selected board. Do not drive GPIO2
as an LED on the ESP32 receiver: it is DIO0. The old sketch did both. S3 GPIO0 is not
an ADC input. Battery sensing is disabled until a free ADC pin and divider are
configured. Keep S3 native USB GPIO19/20 free. GPIO18 belongs to ultrasonic ECHO;
GPS is disabled and requires a new verified free RX pin before enabling.
Pin availability depends on module flash/PSRAM and board wiring. ESP32 GPIO12 is a
boot strapping pin; verify the ultrasonic module does not force an invalid boot level.

Use a common ground, suitable regulated power, and a LoRa antenna. Match the actual
probe board's supply and logic specifications. Protect ESP32 ADC and ECHO inputs
from 5 V signals with the appropriate divider or level shifter. A software change
cannot compensate for wrong wiring, insufficient heater current, or overvoltage.

In `hardware_config.h`, disable every sensor that is not connected. Analog pins
cannot reliably detect a disconnected sensor. MQ-7, rain, water, soil, pH, flame,
SW420 and ultrasonic are enabled for the supplied wiring. TDS on GPIO5 is optional
and disabled until connected. Turbidity on GPIO6 is only a reserved optional pin:
no signal wire was specified, so it is disabled. GPS and battery are disabled.
OLED and DS18B20 drivers are not included; a TDS board NTC connector does not provide
a separate measured water temperature to the ESP32. BME680 probes 0x76/0x77; MPU6050 probes
0x68/0x69. A failed read is omitted and its health flag is shown in diagnostics.

## Supplied power and divider details

Use one common ground. Power ESP32 VIN, MQ-7 and the pH/optional TDS/turbidity/
ultrasonic boards from their specified 5V rail. LoRa and the listed 3.3V sensors
use the regulated 3.3V rail. BME680 CS goes to 3.3V and SDO to GND (address 0x76);
optional MPU6050 AD0 goes to GND (0x68).

**Before connecting inputs:** 10k from output to GPIO and 20k from GPIO to GND
produces 3.333V from 5V. The ESP32-S3 documented ADC range at 11dB is up to 3.1V;
software cannot repair saturation. A 15k upper / 20k lower divider produces about
2.86V at 5V. Verify actual maximum voltages, resistor tolerances, and module logic
levels for each analog input and ultrasonic ECHO. Recalibrate pH/TDS whenever the
divider changes. The code reports millivolts **at the GPIO**, so calibration points
must be measured there; do not enter voltages measured before the divider.
Ultrasonic distance depends on pulse duration, not the divider ratio.
See [Espressif ADC documentation](https://docs.espressif.com/projects/arduino-esp32/en/latest/api/adc.html).

MQ-7 with constant 5V board power is transmitted as a raw response only. Establish
whether your exact module controls its heater cycle internally. The
[Winsen MQ-7B manual](https://www.winsen-sensor.com/d/files/manual/mq-7b.pdf)
specifies alternating heater phases; consult the matching datasheet for your
actual MQ-7 module. No heater-control wire was supplied, so this firmware cannot
implement that hardware cycle or claim calibrated CO ppm / mg/m³.

## Units and calibration

| Sensor | Transmitted / displayed | Required before ML use |
|---|---|---|
| BME680 | °C, % RH, hPa, kΩ | Verify against references; gas resistance is not TVOC |
| MQ-7 | 12-bit ADC counts and GPIO7 mV diagnostics | Correct heater cycle, calibration and circuit required for CO; never relabelled MQ-135 or ppm |
| Rain plate | ADC counts | Cannot measure rainfall mm; install a calibrated rain gauge |
| Analog water probe | ADC counts | No generic conversion to river depth |
| JSN-SR04T | cm to surface | Measured mounting reference → `(reference_cm − distance_cm)/100` metres |
| Soil probe | ADC counts; calibrated % VWC if enabled | Calibration against actual volumetric water content, not dry/wet relative % |
| MPU6050 | inclination 0–180° from +Z | Verify mounting orientation; static tilt assumes gravity dominates acceleration |
| SW420 | debounced pulses/min over actual sample interval | Configure debounce and validate pulse response; not seismic acceleration |
| Flame | digital detected/clear | Verify active-low module polarity; a trigger is an observation, not ML probability |
| pH | GPIO4 mV; calibrated pH if enabled | At least two certified buffers; PH_MV_1/2 are measured after the divider at GPIO4 |
| TDS | mV; ppm if enabled | Validate probe-specific transfer function, calibration range and temperature response |
| Turbidity | mV; NTU if enabled | Validate with reference standards over the operating range |
| GPS | degrees, only with a recent valid fix | No fallback city; no rounding to 2 decimal places |

Calibration switches default to false. The linear pH/soil and TDS/turbidity
coefficients are configurable examples, **not factory calibration**. Analog physical
conversions are suppressed at or above 3100mV; the raw diagnostics remain visible. Use a validated
probe-specific curve and temperature compensation when required; a linear fit is
only defensible over its verified range. Failed, uncalibrated or absent readings
remain unavailable. The sender currently has no SDS011, rain-gauge, dissolved-oxygen,
EC, water-temperature, solar or wind driver. The original code claimed broader
hardware coverage than it implemented; adding those requires the exact modules,
wiring and calibration details.

## Trained-model compatibility

Physical packets use `gateway/live_models.py`; explicit simulations retain the demo
adapters. The model artifacts are loaded with scikit-learn 1.9.0, their saved version.

| Model | Physical readiness / remaining requirement |
|---|---|
| Flood | Requires measured depth, streamflow m³/s, VWC %, °C, % RH, and actual 1/3/6/24/72-hour rainfall totals. No `depth × 12` streamflow or rain-plate mm substitution. |
| Landslide | Requires calibrated VWC, tilt, vibration, temperature, humidity and 24-hour rainfall. VWC % is divided by 100; rates use the training 15-minute interval. Training tilt/vibration/context include synthetic proxies; field validation remains necessary. |
| Air | Requires PM2.5/PM10 µg/m³, temperature, humidity, pressure, CO mg/m³ and NO₂ µg/m³. Gas feature uses training formula `clip(CO*20 + NO2*0.5,1,200)`; real 15/30-minute lags required. MQ-7 or MQ-135 raw ADC is not a substitute. |
| Wildfire | Unavailable for current hardware. Model needs TVOC and raw ethanol from its source sensor domain. Obtain matched sensors or retrain on labelled installed-sensor recordings. Direct optical flame alerts operate independently. |
| Extreme heat | Requires solar W/m², wind km/h, hourly rainfall and 72 complete hourly temperature/humidity windows. The adapter computes hourly means and real persistence; partial hours or gaps over 30 seconds block inference. The current sender lacks solar/wind/gauge instruments. |
| Industrial | Unavailable pending validation/retraining of mixed MQ-135/MQ-2/UCI response scales. An MQ-135 reading times 0.85 is not a measured smoke signal. |
| Water quality | Requires calibrated pH, NTU, TDS ppm, measured EC µS/cm, DO mg/L and **water** °C. Features now follow the training 12-sample formulas. BME680 ambient temperature and assumed DO/EC are not substituted. Validate deployment sampling against training samples. |

The project’s `confidence` outputs are largely hand-written sensor-health scores
(for example, 0.95 minus missing-feature penalties). They are displayed explicitly
as input-health heuristics, not calibrated accuracy. Unsupported models report
`skipped`, a concrete reason, and `UNKNOWN` severity. Zero placeholders in the legacy
numeric API schema must not be interpreted as zero risk; the live UI shows unavailable.
Direct flame alerts have no ML confidence and are labeled `direct_sensor`.

## Acceptance procedure

1. Confirm board models, pin map, sensor models and power levels. Compile both
   separate sketches and flash the correct ports.
2. Inspect sender diagnostics: BME680 and MPU6050 initialization, raw ADC/mV readings,
   JSON fragments under 251 bytes. Stimulate one sensor at a time and check changes.
3. Inspect receiver: `READY` followed by `RX` envelopes. Its hex `data` must decode
   byte-for-byte to the sender's JSON fragment. If not, inspect power, SPI pins,
   antenna and matching radio settings.
4. Start the gateway and exactly one USB bridge. Verify sequence, RSSI/SNR and values
   in `/live`. Disconnect a sensor: it must not be replaced by a synthetic value.
5. Verify each calibrated sensor against a reference instrument at several points.
   Record coefficients, residual error, temperature and valid operating range.
6. Trigger the optical flame input in a controlled bench test; verify the explicit
   direct alert. Stop telemetry for 30 seconds: the UI must label readings STALE.
7. For ML acceptance, provide the missing instruments and correctly timed recordings;
   compare feature vectors to training, then validate/retrain and calibrate probabilities
   on labelled field data. Software transport tests cannot establish model accuracy.

Software checks: `python -m pytest tests -q`. The dedicated hardware tests exercise
fragment reassembly, missing/duplicate/conflicting packets, preserved zero/decimal
values, unit conversion, missing-input rejection, direct alerts and the dashboard API.

## Source references

- [LoRa API: maximum 255 bytes](https://github.com/sandeepmistry/arduino-LoRa/blob/master/API.md)
- [ESP32 ADC API: calibrated millivolt readings](https://docs.espressif.com/projects/arduino-esp32/en/latest/api/adc.html)
- Training contracts are defined in each module's `src/features` and `src/training`
  files. Reports alone are insufficient to establish sensor compatibility.
