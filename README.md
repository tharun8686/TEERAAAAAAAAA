# Terra Edge — Environmental Intelligence Platform

## Live hardware setup

On a new Windows computer, double-click `INSTALL_ARDUINO_WINDOWS.bat` to install
Arduino IDE, the ESP32 board package and all firmware libraries, then compile both
sketches. See [the one-click setup guide](setup/README.md) for USB-driver handling.

For `SENDER.ino` → LoRa → `RECEIVER.ino` → USB → gateway → dashboard, follow
[the hardware setup and model compatibility guide](docs/HARDWARE_TO_DASHBOARD.md).
Start `python -m uvicorn gateway.app:app --host 127.0.0.1 --port 8000`, then open
**http://127.0.0.1:8000/live**. Use its USB connection or `python lora_serial_bridge.py COM4`.
The overview and live pages include Connect receiver USB and Disconnect controls.
Use Chrome or Edge, select the receiver port and keep the connection tab open.
Prepare the two standalone Arduino files with `python hardware/prepare_sketches.py`:
open `build/arduino/SENDER/SENDER.ino` for ESP32-S3 and
`build/arduino/RECEIVER/RECEIVER.ino` for ESP32. No project header is required.
Sensor enable flags and calibration settings are at the top of `SENDER.ino`.
Analog/digital probe presence cannot be reliably auto-detected: disable unwired
channels. I2C devices are probed automatically; raw probe values remain visible.
Missing sensors and uncalibrated values are explicitly unavailable. Several trained
models require instruments or field retraining beyond the current sender's sensor
set; see the guide before interpreting predictions. Existing model confidence
formulas are input-health heuristics, not validated accuracy estimates.

India's distributed **Edge-AI environmental hazard early-warning system**, covering **flood, wildfire, landslide, air pollution, extreme heat, toxic gas plume (industrial emissions), and water quality degradation** risks.

Each hazard is a self-contained module with its own ML training pipeline, serialized edge-deployable model, FastAPI microservice, calibration reports, and ESP32 firmware. A single glassmorphic **Enterprise Control Center** (`index.html`) unifies telemetry, live maps, risk dashboards, and a conversational assistant.

---

## Features

- **7 hazard microservices** — each with a trained, calibrated, edge-exportable model
- **Edge deployment** — onboard ESP32 inference (serialized `.pkl` → generated C/C++ headers + Arduino sketches)
- **Anomaly detection** — IsolationForest / divergence detectors flag deviations before thresholds are hit
- **Enterprise dashboard** — dark/light glassmorphic UI with Live Map, real-time gauges, telemetry simulators, and module switcher
- **Emergency dispatch** — CRITICAL/WARNING events trigger automated alert flows
- **Conversational assistant** — Node.js/Express chatbot backend with a drop-in web widget
- **Supabase integration** — schema + client for alerts, predictions, and node inventory
- **Verification manifest** — reproducible model/verification artifacts and readiness audit

---

## Repository Structure

```
TerraEdge/
├── index.html                          # Enterprise Control Center dashboard
├── module_registry.json                # Single source of truth for all modules
├── requirements.txt                    # Python deps (all 7 microservices)
├── VERIFICATION_MANIFEST.md            # Model readiness verification
├── comprehensive_project_report.md     # Full architecture & pipeline audit
│
├── Flood/                              # Module 01 — Flood  (port 8000)
├── ForestWildFire/                     # Module 02 — Wildfire (port 8001)
├── Landslide/                          # Module 03 — Landslide (port 8002)
├── AirPollution/                       # Module 04 — Air Quality (port 8003)
├── Extreme Heat/                       # Module 05 — Extreme Heat (port 8004)
├── Industrial Emissions/               # Module 06 — Toxic Flame / Industrial Plume (port 8005)
├── Water Quality Degradation/          # Module 07 — Water Quality (port 8006)
│
├── hardware/                           # Shared firmware & USB serial bridge
├── common/                             # Shared Supabase schema & client
├── assets/                             # Video/images for the dashboard
├── chatbot-backend/                    # Express chatbot API (node)
└── chatbot-widget/                     # Client-side chat widget
```

Each `Module/` directory is self-contained:

```
├── models/      # Serialized model, preprocessor, calibrator, anomaly detector, config JSON
├── reports/     # Data audit, feature engineering, model comparison, calibration, edge feasibility
├── src/
│   ├── data/            # raw / intermediate / final pipeline inputs
│   ├── preprocessing/   # data builders, audits, timeseries construction
│   ├── features/        # feature engineering
│   ├── training/        # model & anomaly training
│   ├── inference/       # prediction classes
│   ├── validation/      # robustness validation
│   ├── backend/app.py   # FastAPI microservice
│   └── embedded/        # edge config generation
└── hardware/    # ESP32 inference headers / Arduino sketches
```

---

## Hazard Modules

| Module | Directory | Port | Model | Hardware |
|--------|-----------|------|-------|----------|
| Flood | `Flood/` | 8000 | RandomForest | Water level, rain gauge, soil moisture |
| Wildfire | `ForestWildFire/` | 8001 | Compact RandomForest | MQ-2, MQ-7, BME680, IR flame |
| Landslide | `Landslide/` | 8002 | Calibrated RandomForest | MPU-6050 inclinometer, SW-420 seismic, soil moisture |
| Air Quality | `AirPollution/` | 8003 | RandomForest | PMS5003, MQ-135, BME280 |
| Extreme Heat | `Extreme Heat/` | 8004 | Logistic Regression | BME680, pyranometer, anemometer |
| Toxic Plume | `Industrial Emissions/` | 8005 | Logistic Regression | MQ-135/2/7, PMS5003 |
| Water Quality | `Water Quality Degradation/` | 8006 | Logistic Regression | pH, TDS, turbidity, DO probes |

All models are probability-calibrated and thresholded into **NORMAL / WATCH / WARNING / CRITICAL** risk tiers (`module_registry.json` defines exact thresholds per module).

---

## Tech Stack

- **Backends:** FastAPI, Uvicorn, Pydantic
- **ML:** scikit-learn, pandas, numpy, joblib, pyarrow
- **Edge:** Generated C/C++ inference code for ESP32 (Arduino sketches in `hardware/`)
- **Frontend:** Vanilla HTML/CSS/JS, Leaflet map, glassmorphic control-center design
- **Backend services:** Supabase (Postgres), Node.js + Express (chatbot)
- **Cloud/config:** `.env`, `python-dotenv`

---

## Quick Start

### 1. Python (hazard microservices)

```bash
python -m venv .venv
.venv\Scripts\activate          # Windows
# source .venv/bin/activate    # macOS / Linux

python -m pip install -r requirements.txt

# Start a single microservice, e.g. Flood on port 8000
uvicorn Flood.src.backend.app:app --host 0.0.0.0 --port 8000
```

> Each module has its own `requirements.txt` and `src/backend/app.py` for standalone deployment.

### 2. Node (chatbot backend)

```bash
cd chatbot-backend
npm install
npm start
```

### 3. Environment variables

Copy `.env.example` to `.env` and add your keys:

```
GOOGLE_MAPS_API_KEY=...
SUPABASE_URL=...
SUPABASE_ANON_KEY=...
```

### 4. Dashboard

Open `index.html` in a browser while at least one microservice is running. The control center auto-detects the module endpoints.
      
---

## Edge Deployment

1. Train / verify the module (`src/training/*.py`, `src/validation/*.py`)
2. Export the edge model — generated headers sit in `Module/hardware/` (e.g. `esp32_flood_risk.h`)
3. Flash the Arduino sketch from `hardware/` — see `Landslide/hardware/arduino/LandslideEdge/` for a full standalone example
4. Stream telemetry back to the dashboard via `hardware/usb_serial_bridge.py`

---

## Documentation

- `comprehensive_project_report.md` — full architecture, pipeline, and audit write-up
- `system_integration_report.md` — how modules integrate into the dashboard
- `VERIFICATION_MANIFEST.md` — readiness matrix per module
- `Module/reports/*.md` — per-module feature engineering, calibration, and edge feasibility reports

---

## License

Proprietary / for project evaluation. See the respective report files for data-source attributions (CWC, IMD, CPCB, NIST, USGS, UCI, WHO).
