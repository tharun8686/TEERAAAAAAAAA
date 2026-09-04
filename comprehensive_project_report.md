# Terra Edge — Environmental Intelligence Project Report

This document contains a comprehensive audit and technical architecture documentation of the **Terra Edge** Environmental Intelligence Platform. It outlines the repository hierarchy, machine learning pipelines, FastAPI backend microservices, Google Maps vector integration, interactive telemetry simulators, and emergency dispatch systems implemented across the project.

---

## 1. Project Directory Structure

The project is structured into 7 distinct module directories, each acting as a self-contained edge machine learning pipeline containing raw datasets, intermediate feature representations, serialized models, deployment reports, and FastAPI backend microservices.

```
Terra Edge/
│
├── .env                                     # Environment variables & Google Maps API key
├── index.html                               # Enterprise Control Center & Glassmorphic Dashboard
├── comprehensive_project_report.md          # Comprehensive Project Audit Report (This File)
│
├── Flood/                                   # 01/FLOOD MODULE
│   ├── data/
│   │   ├── raw/                             # Raw CAAQM & Tennessee WSN datasets
│   │   ├── intermediate/                    # Master precipitation matrices
│   │   └── final/                           # Labeled hydrometry sets
│   ├── models/                              # Serialized classifier weights
│   ├── reports/                             # Feature importance & test comparisons
│   └── src/
│       ├── backend/app.py                   # FastAPI Microservice (Port 8000)
│       └── inference/                       # Model prediction class
│
├── ForestWildFire/                          # 02/WILDFIRE MODULE
│   ├── data/
│   │   ├── raw/                             # Combustion gas & ambient weather files
│   │   ├── intermediate/                    # Resampled telemetry matrices
│   │   └── final/                           # Fire risk training tables
│   ├── models/                              # Serialized Random Forest classifier
│   ├── reports/                             # VPD and fire risk validation sheets
│   └── src/
│       ├── backend/app.py                   # FastAPI Microservice (Port 8001)
│       └── inference/                       # Combustion risk class
│
├── Landslide/                               # 03/LANDSLIDE MODULE
│   ├── data/
│   │   ├── raw/                             # Cleveland Corral geotechnical measurements
│   │   ├── intermediate/                    # Clean hourly movement timeseries
│   │   └── final/                           # Sliding risk classification tables
│   ├── models/                              # SVM and Decision Tree classifiers
│   ├── reports/                             # Pore pressure & movement lag graphs
│   └── src/
│       ├── backend/app.py                   # FastAPI Microservice (Port 8002)
│       └── inference/                       # Geotechnical movement warnings
│
├── AirPollution/                            # 04/AIR POLLUTION MODULE
│   ├── data/
│   │   ├── raw/                             # CAAQM particulate raw measurements
│   │   ├── intermediate/                    # Master AQI index alignments
│   │   └── final/                           # Classifier tables
│   ├── models/                              # Serialized HistGradientBoosting model
│   ├── reports/                             # PM2.5/PM10 forecast metrics
│   └── src/
│       ├── backend/app.py                   # FastAPI Microservice (Port 8003)
│       └── inference/                       # Air quality forecasting
│
├── Extreme Heat/                            # 05/EXTREME HEAT MODULE
│   ├── data/
│   │   ├── raw/                             # Pune CWPRS solar/humidity datasets
│   │   ├── intermediate/                    # Apparent temp timeseries
│   │   └── final/                           # Labeled heat-stress tables
│   ├── models/                              # Calibrated Logistic Regression classifier
│   ├── reports/                             # Heat-Index calibration sheets
│   └── src/
│       ├── backend/app.py                   # FastAPI Microservice (Port 8004)
│       └── inference/                       # Apparent temperature predictor
│
├── Industrial Emissions/                    # 06/TOXIC PLUME MODULE
│   ├── data/
│   │   ├── raw/                             # UCI gas sensor array & smoke profiles
│   │   ├── intermediate/                    # Aligned drift matrices
│   │   └── final/                           # Plume risk training tables
│   ├── models/                              # Calibrated Classifier + Anomaly detector
│   ├── reports/                             # Gas drift compensation parameters
│   └── src/
│       ├── backend/app.py                   # FastAPI Microservice (Port 8005)
│       └── inference/                       # Toxic dispersion class
│
└── Water Quality Degradation/               # 07/AQUATIC HEALTH MODULE
    ├── data/
    │   ├── raw/                             # CWC surface water & CGWB groundwater (AP)
    │   ├── intermediate/                    # Aligned timeseries & feature tables
    │   └── final/                           # Labeled water risk databases
    ├── models/                              # Calibrated Logistic Regression + Isolation Forest
    ├── reports/                             # WHO standard calibration reports
    └── src/
        ├── backend/app.py                   # FastAPI Microservice (Port 8006)
        └── inference/                       # Aquatic contamination risk class
```

---

## 2. Microservice & Machine Learning Portfolios

Each of the 7 modules contains a dedicated machine learning pipeline running a chronological train/val/test split. Here are the core specifications of the models:

### 01/Flood Hydrometry (Port 8000)
- **Mathematical Features**: Cumulative 1-hour rainfall ($mm/h$), Cumulative 24-hour rainfall ($mm/24h$), Volumetric Water Content (VWC) of soil ($\% \text{ or } m^3/m^3$), and River stage height ($m$).
- **Weak Label Strategy**: Labeled $0 \text{ to } 3$ depending on river level exceeding flood danger benchmarks: Normal ($<1.5m$), Watch ($1.5m - 2.5m$), Warning ($2.5m - 3.5m$), and Critical ($>3.5m$).
- **Model Architecture**: `HistGradientBoostingClassifier` with tree-based categorical handling and isotonic probability calibration.

### 02/Wildfire & Combustion (Port 8001)
- **Mathematical Features**: Ambient temperature ($^\circ C$), relative humidity ($\%$), Vapor Pressure Deficit ($VPD$, calculated from psychrometric formulas), and MQ-135 combustion gas readings (CO, Ethanol, Smoke proxy).
- **Weak Label Strategy**: Risk compiled from elevated temperatures, drought-stressed fuel beds ($VPD > 3.5 \text{ kPa}$), and combustion gas spikes.
- **Model Architecture**: `RandomForestClassifier` with balanced class weights and OOB risk estimation.

### 03/Landslide & Geotechnical Slope (Port 8002)
- **Mathematical Features**: MPU-6050 Accelerometer tilt deviation ($^\circ$), Soil moisture ($\% \text{ VWC}$), Pore water pressure ($kPa$), and rate of pressure displacement ($kPa/h$).
- **Weak Label Strategy**: Slope shear stress index exceeding sliding friction limits ($F_s < 1.0$) during rapid soil saturation and tilt excursions ($>5^\circ$).
- **Model Architecture**: Support Vector Machine (`SVC`) with RBF kernel combined with `IsolationForest` for micro-seismic vibration anomaly filtering.

### 04/Air Quality & CAAQM Aerosols (Port 8003)
- **Mathematical Features**: $PM_{2.5}$ concentration ($\mu g/m^3$), $PM_{10}$ concentration ($\mu g/m^3$), $NO_2$ electrochemical response ($ppb$), and PM ratio ($PM_{2.5} / PM_{10}$) with 15m/30m lag vectors.
- **Weak Label Strategy**: Indian National Air Quality Index (NAQI) bands: Good (0–50), Satisfactory (51–100), Moderate (101–200), Poor (201–300), Very Poor (301–400), Severe ($>400$).
- **Model Architecture**: `HistGradientBoostingClassifier` with multi-step forward vector forecasting.

### 05/Extreme Heat & Thermal Stress (Port 8004)
- **Mathematical Features**: Dry-bulb Temperature ($^\circ C$), Relative Humidity ($\%$), Solar Radiation ($W/m^2$), Wind Speed ($km/h$), calculated Apparent Heat Index (HI), and Nighttime Cooling Deficit.
- **Weak Label Strategy**: NOAA Heat Index boundaries: Normal ($<32^\circ C$), Watch ($32^\circ C - 39^\circ C$), Warning ($39^\circ C - 46^\circ C$), and Critical ($>46^\circ C$).
- **Model Architecture**: Calibrated `LogisticRegression` + `IsolationForest` Anomaly Detector.

### 06/Toxic Plume & Industrial Leaks (Port 8005)
- **Mathematical Features**: MQ Gas Sensor Array analog response ($\Omega \text{ / PPM}$), $PM_{2.5}$, $PM_{10}$, ambient temperature, atmospheric pressure, rate of gas concentration rise, and chemical co-occurrence score.
- **Weak Label Strategy**: Rate of rise in MQ gas sensor response ($>300$ Watch, $>500$ Warning, $>850$ Critical) co-occurring with ambient particulate matter spikes.
- **Model Architecture**: Calibrated Classifier + `IsolationForest` for rapid industrial VOC leak detection.

### 07/Aquatic Health & Water Quality (Port 8006)
- **Mathematical Features**: $pH$ level, Turbidity ($NTU$), Total Dissolved Solids ($TDS, mg/L$), Electrical Conductivity ($EC, \mu S/cm$), Dissolved Oxygen ($mg/L$), and acidity shift score ($|pH - 7.0|$).
- **Weak Label Strategy**: Mapped against WHO & IS 10500 drinking/surface water standards:
  - **Critical (3)**: $pH < 4.5 \text{ or } > 10.5$ | Turbidity $> 50 \text{ NTU}$ | TDS $> 1200 \text{ mg/L}$ | Dissolved Oxygen $< 2.0 \text{ mg/L}$.
  - **Warning (2)**: $pH < 5.5 \text{ or } > 9.5$ | Turbidity $> 15 \text{ NTU}$ | TDS $> 600 \text{ mg/L}$ | Dissolved Oxygen $< 4.0 \text{ mg/L}$.
  - **Watch (1)**: $pH < 6.5 \text{ or } > 8.5$ | Turbidity $> 5.0 \text{ NTU}$ | TDS $> 300 \text{ mg/L}$ | Dissolved Oxygen $< 6.0 \text{ mg/L}$.
- **Model Architecture**: Calibrated `LogisticRegression` + `IsolationForest`.

---

## 3. Google Maps Integration & Visual Architecture

The mapping layer across the platform is powered by the **Google Maps JavaScript API** with enterprise vector tiles and customized UI overlays.

### Key Map Implementations & Features:
1. **Vector Rendering Engine**:
   - Initialized with `renderingType: google.maps.RenderingType.VECTOR` for smooth 60fps interaction, sub-pixel rendering, and 3D terrain tilt/rotation.
2. **Dynamic Key Resolution**:
   - Configured with `window.GOOGLE_MAPS_API_KEY = "AIzaSyDJqH2YXyCtH8mvLcWw9sdUibxnmHkGkng"` for standalone execution (file protocol / static web servers) alongside an automated dynamic probe against backend microservices (`/api/config` across ports 8000–8006).
   - Async injection via `loadGoogleMaps(apiKey)` ensures asynchronous script loading without blocking the DOM.
3. **Custom Dark-Theme System (`GOOGLE_MAPS_DARK_STYLE`)**:
   - Deep slate and midnight navy palette (`#06070e`, `#0d111d`, `#141829`, `#1c2035`) matching the enterprise dashboard theme.
   - **Terrain View Dynamic Fix**: Dynamic listener automatically strips dark JSON styling when `TERRAIN` view is selected to reveal natural topographic hillshade, and re-engages dark styling when returning to `ROADMAP` or `HYBRID`.
4. **Interactive HUD Mode Switcher**:
   - Custom floating glassmorphic control in `TOP_RIGHT` corner of every map offering instantaneous one-click mode switching:
     - **Vector**: Clean dark-mode road and boundary vector network.
     - **Satellite**: High-resolution photogrammetric satellite imagery.
     - **Terrain**: Natural topographical contour shading and elevation ridges.
     - **Hybrid**: Combined satellite imagery with labeled road vectors.
5. **Custom HTML Pulse Markers (`CustomPulseMarker`)**:
   - Built on `google.maps.OverlayView` to project dynamic animated HTML/CSS nodes onto geographic coordinates.
   - Includes concentric radiating radar pulse rings (`.t-pin-ring`) and solid glowing cores (`.t-pin-core`).
   - Integrated click-activated `google.maps.InfoWindow` displaying telemetry station ID, coordinate lat/long, and real-time operational state.

### Geographic Node Deployment Coordinates

| Module | Div ID | Center Coordinates | Zoom | Deployed Sensor Nodes | Color Code |
|---|---|---|---|---|---|
| **01/Flood** | `#map-flood` | $25.5^\circ\text{N}, 82.0^\circ\text{E}$ | 5 | - Delhi Yamuna Node ($28.6139^\circ\text{N}, 77.2090^\circ\text{E}$)<br>- Varanasi Ganga Node ($25.3176^\circ\text{N}, 82.9739^\circ\text{E}$)<br>- Kolkata Hooghly Node ($22.5726^\circ\text{N}, 88.3639^\circ\text{E}$) | `#00d2ff` (Cyan) |
| **02/Wildfire** | `#map-fire` | $20.5^\circ\text{N}, 80.0^\circ\text{E}$ | 5 | - Goa Forest Zone ($15.2993^\circ\text{N}, 74.1240^\circ\text{E}$)<br>- Nilgiris Forest Node ($11.1085^\circ\text{N}, 77.3411^\circ\text{E}$)<br>- MP Reserve ($22.9734^\circ\text{N}, 78.6569^\circ\text{E}$) | `#ff5722` (Deep Orange) |
| **03/Landslide** | `#map-land` | $20.0^\circ\text{N}, 77.0^\circ\text{E}$ | 5 | - Western Ghats Station ($11.4100^\circ\text{N}, 76.6900^\circ\text{E}$)<br>- Valparai Hill Pass ($10.3270^\circ\text{N}, 76.9550^\circ\text{E}$)<br>- Manali Himalayan Node ($32.0845^\circ\text{N}, 77.1734^\circ\text{E}$) | `#f59e0b` (Amber) |
| **04/Air Quality** | `#map-air` | $22.0^\circ\text{N}, 79.0^\circ\text{E}$ | 5 | - Delhi ITO CAAQM ($28.6289^\circ\text{N}, 77.2408^\circ\text{E}$)<br>- Delhi IHBAS ($28.6812^\circ\text{N}, 77.3195^\circ\text{E}$)<br>- Mumbai Deonar ($19.0565^\circ\text{N}, 72.9150^\circ\text{E}$)<br>- Pune Shivajinagar ($18.5308^\circ\text{N}, 73.8475^\circ\text{E}$) | `#2dd4bf` (Mint Green) |
| **05/Extreme Heat** | `#map-heat` | $18.5^\circ\text{N}, 73.8^\circ\text{E}$ | 6 | - Pune CWPRS Campus Node ($18.4350^\circ\text{N}, 73.7915^\circ\text{E}$) | `#fbbf24` (Gold) |
| **06/Toxic Plume** | `#map-ind` | $17.68^\circ\text{N}, 83.21^\circ\text{E}$ | 6 | - Vizag Industrial Complex Node ($17.6868^\circ\text{N}, 83.2185^\circ\text{E}$) | `#a855f7` (Violet) |
| **07/Aquatic Health** | `#map-water` | $17.7285^\circ\text{N}, 83.3015^\circ\text{E}$ | 6 | - Vizag Municipal Reservoir Node ($17.7285^\circ\text{N}, 83.3015^\circ\text{E}$) | `#0ea5e9` (Sky Blue) |

---

## 4. Frontend Interface & Interactive Components (`index.html`)

The dashboard features a human-engineered glassmorphic dark theme built with pure semantic HTML5, Vanilla CSS, and modular JavaScript.

### Core Interface Elements:
1. **RDR2 Radial Selection Wheel Matrix (`#models-matrix`)**:
   - Circular radar selection interface featuring 7 interactive angular slice wedges with icons and labels.
   - Hovering over a slice or clicking dynamically updates the central HUD hub (`#rdr-center-hud`) with the module name, category classification, live description, and an instant navigation CTA.
   - Smooth transition directly into single-console view with synchronized ambient aura backdrop color shifts.
2. **Real-time Canvas Telemetry Simulation Background**:
   - An HTML5 60fps particle background canvas (`#bg-canvas`) running procedural multi-wave hydrometry curves, rising thermal combustion embers, seismic shock lines, and CAAQM particulate optical dispersion vectors.
3. **Pill-Bar Navigation & Layout Controller**:
   - Supports viewing individual isolated consoles (`openSingleModel()`) or continuous multi-hazard stream view (`openAllConsoles()`).
   - Automatically executes `google.maps.event.trigger(map, 'resize')` after tab transitions to guarantee zero map tile rendering artifacts.
4. **Interactive Telemetry Simulators & Dual-Mode Execution**:
   - Sliders dynamically synchronize with live numeric telemetry readouts.
   - **Backend Sync**: Dispatches structured POST requests to FastAPI endpoints.
   - **Offline Local Fallback**: When microservices are offline, an onboard mathematical inference engine computes calibrated risk scores, anomaly statuses, and severity levels in real-time, ensuring seamless demonstrations under any environment.
5. **Authority Routing & Emergency Dispatch Console**:
   - Real-time status indicators for NDMA CAP emergency gateway protocols, Public Advisory SMS geo-fencing, and Municipal Response webhooks.
   - **Test Broadcast Protocol Button**: Triggers simulated disaster broadcast alert toasts.
6. **Live Warnings Alerts System**:
   - Automated polling mechanism monitoring active warning thresholds across nodes, populating dismissible `CRITICAL` (red) and `WARNING` (amber) banner feeds with precise timestamps.

---

## 5. Telemetry Simulations & Parameter Mapping

When a user adjusts a range slider in the UI, the values are mapped to standard payload keys and sent to the microservice. Here is the exact parameter simulation mapping:

| Module | UI Sliders (Interactive Values) | Physical Range | FastAPI JSON Payload Mapping | Risk Threshold Logic |
|---|---|---|---|---|
| **01/Flood** | - River Level: `0m` to `5m`<br>- Soil Moisture: `10%` to `100%`<br>- 24h Rain: `0mm` to `200mm` | - `rain_1h` (Rain/8)<br>- `rain_24h`<br>- `water_level_m`<br>- `soil_moisture_pct` | Direct river hydrometry. Soil saturation decreases drainage speed. | High risk when `water_level_m` exceeds banks ($>3.5m$) and soil is saturated ($>85\%$). |
| **02/Wildfire** | - Air Temp: `10°C` to `50°C`<br>- Relative Hum: `5%` to `90%`<br>- Wind Vel: `0` to `50 km/h` | - `temperature`<br>- `humidity`<br>- `pm25`<br>- `tvoc`<br>- `rates/deltas` | Calculates VPD and TVOC/PM2.5 combustion signatures. | High risk when temperature $>40^\circ\text{C}$, humidity $<25\%$, and wind velocity is high. |
| **03/Landslide**| - Soil Moisture: `10%` to `100%`<br>- Tilt Rate: `0.0°/s` to `2.0°/s`<br>- Vibration: `0.0` to `5.0 RMS` | - `soil_moisture_vwc`<br>- `tilt_rate`<br>- `tilt_magnitude`<br>- `vibration_rate` | Accelerometer tilt and seismic vibration measure slope instability. | Tilt rate $>0.8^\circ/\text{step}$ combined with saturated soil ($>75\%$) triggers critical alarms. |
| **04/Air Quality**| - PM2.5: `5` to `350 µg/m³`<br>- PM10: `10` to `500 µg/m³`<br>- 30m Trend Delta: `-50` to `+100` | - `pm25`<br>- `pm10`<br>- `pm25_delta_30`<br>- `pm25_slope_30` | Real-time particulate density and short-term forward delta slope. | Exceeding standard AQI ranges ($PM_{2.5} > 150 \text{ µg/m}^3$) triggers critical warnings. |
| **05/Extreme Heat**| - Air Temp: `20°C` to `50°C`<br>- Humidity: `10%` to `95%`<br>- Solar Rad: `100` to `1200 W/m²`<br>- Wind Speed: `0` to `50 km/h` | - `temperature_c`<br>- `humidity`<br>- `solar_radiation`<br>- `wind_speed_kmh` | Apparent temp = Heat Index formula based on temperature and moisture values. | Heat Index exceeding $46^\circ\text{C}$ or wind stilling during extreme heat triggers warnings. |
| **06/Toxic Plume**| - MQ Gas: `50` to `1000`<br>- PM2.5: `5` to `300 µg/m³`<br>- PM10: `10` to `500 µg/m³` | - `gas_response`<br>- `pm25`<br>- `pm10`<br>- `temperature_c` (30°C)<br>- `humidity` (60%) | Evaluates chemical co-occurrence of VOCs and fine combustion particulates. | Gas response $>500$ (Warning) and $>850$ (Critical) triggers plume alarms. |
| **07/Aquatic Health**| - pH: `2.0` to `12.0`<br>- Turbidity: `0` to `100 NTU`<br>- TDS: `50` to `1500 mg/L`<br>- Dissolved O₂: `0` to `14 mg/L` | - `pH`<br>- `turbidity`<br>- `TDS`<br>- `EC` (TDS * 1.5)<br>- `dissolved_oxygen` | Mapped against baseline parameters. TDS * 1.5 approximates Electrical Conductivity. | pH $<4.5$ or $>10.5$ or Turbidity $>50 \text{ NTU}$ triggers reservoir contamination alarms. |

---

## 6. Commands to Run Backend Microservices

Each FastAPI microservice can be launched in a separate terminal window from the `Terra Edge` root folder:

```powershell
# Port 8000: Flood Early Warning
python "Flood\src\backend\app.py"

# Port 8001: Wildfire Early Warning
python "ForestWildFire\src\backend\app.py"

# Port 8002: Landslide Early Warning
python "Landslide\src\backend\app.py"

# Port 8003: Air Pollution Early Warning
python "AirPollution\src\backend\app.py"

# Port 8004: Extreme Heat Early Warning
python "Extreme Heat\src\backend\app.py"

# Port 8005: Toxic Plume Early Warning
python "Industrial Emissions\src\backend\app.py"

# Port 8006: Aquatic Health Early Warning
python "Water Quality Degradation\src\backend\app.py"
```

All backends automatically read `.env` configuration for credentials and port mappings and serve interactive OpenAPI documentation at `http://127.0.0.1:<PORT>/docs`.

---

## 7. Summary of Completed Improvements

1. **Google Maps API Integration**: Full implementation of vector-rendered Google Maps with dark theme styling, terrain mode visual fixes, pulsing CSS-based telemetry markers, and layer mode switcher HUDs.
2. **API Key & Config Pipeline**: Environment key synchronization with `.env`, direct frontend fallback, and dynamic REST discovery endpoints (`/api/config`).
3. **Radial Hazard Operations Matrix**: Interactive RDR2-inspired circular selection wheel linking all 7 environmental hazard domains to their respective telemetry consoles.
4. **Dual-Mode Simulator & Fallback**: Complete offline operational capability via client-side mathematical risk models paired with FastAPI endpoints.
5. **Authority & Emergency Telemetry**: NDMA CAP gateway simulators, automated alert feeds, and responsive enterprise dark UI.
