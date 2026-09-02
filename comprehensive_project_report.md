# Terra Edge — Environmental Intelligence Project Report

This document contains a comprehensive audit of the **Terra Edge** Environmental Intelligence Platform, outlining the exact directory structures, backend APIs, frontend interface features, and the telemetry simulations used in the dashboard.

---

## 1. Project Directory Structure

The project is structured into 7 distinct module directories, each acting as a self-contained machine learning pipeline containing raw datasets, engineered intermediate features, serialized models, deployment reports, and API backends.

```
Terra Edge/
│
├── index.html                           # Main Frontend Glassmorphic Dashboard
├── comprehensive_project_report.md      # Comprehensive Project Audit Report (This File)
│
├── Flood/                               # 01/FLOOD MODULE
│   ├── data/
│   │   ├── raw/                         # Raw CAAQM & Tennessee WSN datasets
│   │   ├── intermediate/                # Master precipitation matrices
│   │   └── final/                       # Labeled hydrometry sets
│   ├── models/                          # Serialized classifier weights
│   ├── reports/                         # Feature importance & test comparisons
│   └── src/
│       ├── backend/app.py               # FastAPI Microservice (Port 8000)
│       └── inference/                   # Model prediction class
│
├── ForestWildFire/                      # 02/WILDFIRE MODULE
│   ├── data/
│   │   ├── raw/                         # Combustion gas & ambient weather files
│   │   ├── intermediate/                # Resampled telemetry matrices
│   │   └── final/                       # Fire risk training tables
│   ├── models/                          # Serialized Random Forest classifier
│   ├── reports/                         # VPD and fire risk validation sheets
│   └── src/
│       ├── backend/app.py               # FastAPI Microservice (Port 8001)
│       └── inference/                   # Combustion risk class
│
├── Landslide/                           # 03/LANDSLIDE MODULE
│   ├── data/
│   │   ├── raw/                         # Cleveland Corral geotechnical measurements
│   │   ├── intermediate/                # Clean hourly movement timeseries
│   │   └── final/                       # Sliding risk classification tables
│   ├── models/                          # SVM and Decision Tree classifiers
│   ├── reports/                         # Pore pressure & movement lag graphs
│   └── src/
│       ├── backend/app.py               # FastAPI Microservice (Port 8002)
│       └── inference/                   # Geotechnical movement warnings
│
├── AirPollution/                        # 04/AIR POLLUTION MODULE
│   ├── data/
│   │   ├── raw/                         # CAAQM particulate raw measurements
│   │   ├── intermediate/                # Master AQI index alignments
│   │   └── final/                       # Classifier tables
│   ├── models/                          # Serialized HistGradientBoosting model
│   ├── reports/                         # PM2.5/PM10 forecast metrics
│   └── src/
│       ├── backend/app.py               # FastAPI Microservice (Port 8003)
│       └── inference/                   # Air quality forecasting
│
├── Extreme Heat/                        # 05/EXTREME HEAT MODULE
│   ├── data/
│   │   ├── raw/                         # Pune CWPRS solar/humidity datasets
│   │   ├── intermediate/                # Apparent temp timeseries
│   │   └── final/                       # Labeled heat-stress tables
│   ├── models/                          # Calibrated Logistic Regression classifier
│   ├── reports/                         # Heat-Index calibration sheets
│   └── src/
│       ├── backend/app.py               # FastAPI Microservice (Port 8004)
│       └── inference/                   # Apparent temperature predictor
│
├── Industrial Emissions/                # 06/TOXIC PLUME MODULE
│   ├── data/
│   │   ├── raw/                         # UCI gas sensor array & smoke profiles
│   │   ├── intermediate/                # Aligned drift matrices
│   │   └── final/                       # Plume risk training tables
│   ├── models/                          # Calibrated Classifier + Anomaly detector
│   ├── reports/                         # Gas drift compensation parameters
│   └── src/
│       ├── backend/app.py               # FastAPI Microservice (Port 8005)
│       └── inference/                   # Toxic dispersion class
│
└── Water Quality Degradation/           # 07/AQUATIC HEALTH MODULE
    ├── data/
    │   ├── raw/                         # CWC surface water & CGWB groundwater (AP)
    │   ├── intermediate/                # Aligned timeseries & feature tables
    │   └── final/                       # Labeled water risk databases
    ├── models/                          # Calibrated Logistic Regression + Isolation Forest
    ├── reports/                         # WHO standard calibration reports
    └── src/
        ├── backend/app.py               # FastAPI Microservice (Port 8006)
        └── inference/                   # Aquatic contamination risk class
```

---

## 2. Microservice & Machine Learning Portfolios

Each of the 7 modules contains a dedicated machine learning pipeline running a chronological train/val/test split. Here are the core specifications of the models:

### 01/Flood (Port 8000)
- **Mathematical Features**: Cumulative 1-hour rainfall ($mm/h$), Cumulative 24-hour rainfall ($mm/24h$), Volumetric Water Content (VWC) of soil, and River stage height ($m$).
- **Weak Label Strategy**: Labeled $0 \text{ to } 3$ depending on river level exceeding flood danger benchmarks: Normal ($<1.5m$), Watch ($1.5m - 2.5m$), Warning ($2.5m - 3.5m$), and Critical ($>3.5m$).
- **Model Type**: HistGradientBoostingClassifier.

### 02/Wildfire (Port 8001)
- **Mathematical Features**: Ambient temperature ($^\circ C$), relative humidity ($\%$), Vapor Pressure Deficit (VPD, calculated from DHT22 readings), and MQ-135 combustion gas readings.
- **Weak Label Strategy**: Risk scale compiled from temperature and low relative humidity (VPD $> 3.5 \text{ kPa}$ combined with elevated CO levels).
- **Model Type**: Random Forest Classifier.

### 03/Landslide (Port 8002)
- **Mathematical Features**: MPU-6050 Accelerometer tilt deviation ($^\circ$), Soil moisture ($\%), Pore water pressure ($kPa$), and rate of pressure change.
- **Weak Label Strategy**: Slope shear stress index exceeds the sliding friction limit ($F_s < 1.0$) under saturated soil conditions.
- **Model Type**: SVM Classifier + Isolation Forest.

### 04/Air Pollution (Port 8003)
- **Mathematical Features**: $PM_{2.5}$ concentration ($fg/m^3$), $PM_{10}$ concentration ($fg/m^3$), $NO_2$ electrochemical response, and PM ratio ($PM_{2.5} / PM_{10}$).
- **Weak Label Strategy**: Indian National Air Quality Index (NAQI) bands (0-50 Good, 51-100 Satisfactory, 101-200 Moderate, 201-300 Poor, 301-400 Very Poor, $>400$ Severe).
- **Model Type**: HistGradientBoostingClassifier.

### 05/Extreme Heat (Port 8004)
- **Mathematical Features**: Dry-bulb Temperature, Relative Humidity, Solar Radiation ($W/m^2$), Wind Speed ($km/h$), calculated Apparent Temperature (HI), and Nighttime Cooling Deficit.
- **Weak Label Strategy**: Calculated NOAA Heat Index boundaries: Normal ($<32^\circ C$), Watch ($32^\circ C - 39^\circ C$), Warning ($39^\circ C - 46^\circ C$), and Critical ($>46^\circ C$).
- **Model Type**: Calibrated Logistic Regression + Isolation Forest Anomaly Detector.

### 06/Toxic Plume (Port 8005)
- **Mathematical Features**: MQ Gas Sensor Array analog response (ohms/PPM), $PM_{2.5}$, $PM_{10}$, temperature, pressure, rate of gas concentration rise, and plume co-occurrence score.
- **Weak Label Strategy**: Pseudo-labels generated by tracking rate of rise in MQ gas sensor response ($>300$ Watch, $>500$ Warning, $>850$ Critical) co-occurring with ambient particulate matter spikes.
- **Model Type**: Calibrated Logistic Regression + Isolation Forest.

### 07/Aquatic Health (Port 8006)
- **Mathematical Features**: $pH$ level, Turbidity ($NTU$), Total Dissolved Solids ($TDS, mg/L$), Electrical Conductivity ($EC, \mu S/cm$), Dissolved Oxygen ($mg/L$), and acidity shift score ($|pH - 7.0|$).
- **Weak Label Strategy**: Mapped using WHO/IS 10500 standards:
  - Critical ($3$): pH $<4.5$ or $>10.5$ or Turbidity $>50 \text{ NTU}$ or TDS $>1200 \text{ mg/L}$ or Dissolved Oxygen $<2.0 \text{ mg/L}$.
  - Warning ($2$): pH $<5.5$ or $>9.5$ or Turbidity $>15 \text{ NTU}$ or TDS $>600 \text{ mg/L}$ or Dissolved Oxygen $<4.0 \text{ mg/L}$.
  - Watch ($1$): pH $<6.5$ or $>8.5$ or Turbidity $>5.0 \text{ NTU}$ or TDS $>300 \text{ mg/L}$ or Dissolved Oxygen $<6.0 \text{ mg/L}$.
- **Model Type**: Calibrated Logistic Regression + Isolation Forest.

---

## 3. Frontend Website Interface (`index.html`)

The dashboard user interface is contained entirely in `index.html` and features a modern glassmorphism aesthetic.

### UI Components
1. **Interactive Google Maps Dashboard**:
    - Initializes 7 distinct Google Maps instances, each styled with a dark theme and supporting vector rendering.
    - Includes Map Type Control for Roadmap, Satellite, Hybrid, and Terrain views; Vector rendering enabled for smooth 3D interactions; custom pulsing markers indicate sensor locations (Western Ghats, Delhi CAAQM, Vizag complex, Varanasi Ganga, Goa Forest). Clicking a marker displays real-time telemetry and risk labels.
  - **Map Enhancements Implemented:**
    - Fixed Terrain view visibility by adjusting map style to preserve terrain shading.
    - Enabled `renderingType: google.maps.RenderingType.VECTOR` for high‑performance vector tiles and 3D tilt/rotate.
    - Added explicit `mapTypeControl` with options for ROADMAP, SATELLITE, HYBRID, and TERRAIN, allowing users to switch views seamlessly.
    - Integrated custom pulsing marker overlay (`CustomPulseMarker`) to replace Leaflet markers, preserving the UI experience.
    - Implemented error handling and fallback placeholder when API key is missing.
2. **Tabbed Console Navigation**:
   - A selection pill bar (`#pill-all`, `#pill-flood`, `#pill-fire`, etc.) allows the user to display the active early warning console.
   - Selecting a model changes the canvas's ambient blur layer color scheme (e.g. blue for Flood, orange for Fire, purple for Plume, cyan for Water).
3. **Early Warning Status Panels**:
   - Displays real-time API connection ports, active database station names, and lists running metrics: Risk Probability, Anomaly Score, Severity Class, and Confidence Score.
4. **Interactive Telemetry Simulators**:
   - Located on the right-hand panel of each console. Allows users to slide values for variables (like rainfall, gas concentration, pore water pressure, pH, and turbidity) and click **Run Inference** to fetch predictions.
5. **Live Warnings Alerts Widget**:
   - Periodically polls the `/api/alerts` endpoint on all active ports every 15 seconds. If a warning is active, it renders critical alert banners (`CRITICAL` or `WARNING`) with exact database timestamps.

---

## 4. Telemetry Simulations & Parameter Mapping

When a user adjusts a range slider in the UI, the values are mapped to standard payload keys and sent to the microservice. Here is the exact parameter simulation mapping:

| Module | UI Sliders (Interactive Values) | Physical Range | FastAPI JSON Payload Mapping | Risk Threshold Logic |
|---|---|---|---|---|
| **01/Flood** | - River Level: `0m` to `5m`<br>- Soil Moisture: `10%` to `100%`<br>- 24h Rain: `0mm` to `200mm` | - `rain_1h` (Rain/8)<br>- `rain_24h`<br>- `water_level_m`<br>- `soil_moisture` | Maps directly to river gauges. Soil saturation decreases drainage speed. | High risk when `water_level_m` exceeds banks ($>3.5m$) and soil is saturated. |
| **02/Wildfire** | - Air Temp: `10°C` to `50°C`<br>- Relative Hum: `5%` to `90%`<br>- Combustion Gas: `50` to `800` | - `temp_c`<br>- `humidity`<br>- `gas_smoke`<br>- calculated `vpd` | Calculates VPD. Elevated VPD increases fuel flammability. | Combustion gas $>400$ combined with low humidity ($<20\%$) triggers warnings. |
| **03/Landslide**| - Soil Moisture: `10%` to `100%`<br>- Pore Pressure: `0kPa` to `80kPa`<br>- Accel Tilt: `0°` to `45°` | - `soil_moisture`<br>- `pore_pressure`<br>- `tilt_deg` | Accelerometer tilt measures structural movement of the terrain slope. | Elevated tilt $>5^\circ$ combined with high pore pressure $>45 \text{ kPa}$ triggers alarm. |
| **04/Air Quality**| - PM2.5: `5` to `350 µg/m³`<br>- PM10: `10` to `500 µg/m³`<br>- NO2: `0` to `150 ppb` | - `pm25`<br>- `pm10`<br>- `no2` | PM ratios measure particulate density. High PM2.5 indicates fine soot. | Exceeding standard AQI ranges ($PM_{2.5} > 150 \text{ µg/m}^3$) triggers critical alarms. |
| **05/Extreme Heat**| - Air Temp: `20°C` to `50°C`<br>- Humidity: `10%` to `95%`<br>- Solar Rad: `100` to `1200 W/m²`<br>- Wind Speed: `0` to `50 km/h` | - `temperature_c`<br>- `humidity`<br>- `solar_radiation`<br>- `wind_speed_kmh` | Apparent temp = Heat Index formula based on temperature and moisture values. | HI exceeding $46^\circ C$ or wind stilling during extreme heat triggers warnings. |
| **06/Toxic Plume**| - MQ Gas: `50` to `1000`<br>- PM2.5: `5` to `300 µg/m³`<br>- PM10: `10` to `500 µg/m³` | - `gas_response`<br>- `pm25`<br>- `pm10`<br>- `temperature_c` (30°C)<br>- `humidity` (60%) | Evaluates chemical co-occurrence of VOCs and fine combustion particulates. | Gas response $>500$ (Warning) and $>850$ (Critical) triggers plume alarms. |
| **07/Aquatic Health**| - pH: `2.0` to `12.0`<br>- Turbidity: `0` to `100 NTU`<br>- TDS: `50` to `1500 mg/L`<br>- Temperature: `15°C` to `40°C` | - `pH`<br>- `turbidity`<br>- `TDS`<br>- `EC` (TDS * 1.5)<br>- `dissolved_oxygen` (7.5) | Mapped against baseline parameters. TDS * 1.5 approximates Electrical Conductivity. | pH $<4.5$ or $>10.5$ or Turbidity $>50 \text{ NTU}$ triggers reservoir contamination alarms. |

---

## 5. Commands to Run All 7 Backend Microservices

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
## 6. Detailed Frontend Components Overview

### 6.1. Main Dashboard (`index.html`)
- **Header**: Title, logo, and navigation bar (Home, About, Documentation).
- **Map Container**: Seven `<div id="map-...">` elements, each hosting a Google Maps instance.
- **Map Controls**:
  - Map Type Control (Roadmap, Satellite, Hybrid, Terrain) – enabled via `mapTypeControl`.
  - Zoom control, fullscreen button.
  - Custom UI buttons to reset view to default location.
- **Vector Rendering**: `renderingType: google.maps.RenderingType.VECTOR` for smooth 3‑D interactions.
- **Terrain View Fix**: Automatically disables dark style when Terrain map type is active, restoring natural terrain shading.
- **Custom Pulse Marker**: Implemented via `CustomPulseMarker` extending `google.maps.OverlayView`. Pulses to highlight sensor locations.

### 6.2. Console Tabs (Pill Bar)
- Pill buttons (`#pill-all`, `#pill-flood`, `#pill-fire`, `#pill-landslide`, `#pill-air`, `#pill-heat`, `#pill-plume`, `#pill-water`) toggle visibility of the seven early‑warning consoles.
- Each console is a `<section>` element containing its own map, telemetry panel, and status widgets.

### 6.3. Early‑Warning Status Panels
- Real‑time display of:
  - API connection ports.
  - Active database station names.
  - Metrics: Risk Probability, Anomaly Score, Severity Class, Confidence Score.
- Styled with glass‑morphism cards, color‑coded per model (blue, orange, purple, cyan).

### 6.4. Interactive Telemetry Simulators
- Right‑hand panel within each console.
- Sliders for model‑specific variables (e.g., rainfall, soil moisture, temperature, gas concentration, pH, turbidity).
- **Run Inference** button sends a JSON payload to the corresponding FastAPI microservice.
- Response is displayed inline with predicted risk label and confidence.

### 6.5. Live Warnings Alerts Widget
- Polls `/api/alerts` every 15 seconds.
- Renders dismissible banners:
  - **CRITICAL** (red) – immediate action required.
  - **WARNING** (orange) – attention needed.
- Shows exact timestamp from the backend database.

### 6.6. Map Type & View Options
- **Roadmap** – standard vector map.
- **Satellite** – high‑resolution imagery.
- **Hybrid** – satellite + road labels.
- **Terrain** – topographic shading (dark style disabled for clarity).
- Users can switch via the built‑in map type selector or programmatically through the UI dropdown in the top‑right corner.

### 6.7. Error Handling & Fallback
- If the Google Maps script fails to load or the API key is missing, a placeholder card with instructions is displayed.
- Console logs detail the exact failure (`InvalidKeyMapError`, `RefererNotAllowedMapError`, etc.).

### 6.8. Accessibility & Responsiveness
- All controls are keyboard‑navigable.
- CSS media queries ensure the dashboard scales from desktop to tablet screens.
- ARIA labels added to map controls, console tabs, and simulator buttons.

### 6.9. Styling
- Global CSS variables for primary/secondary colors.
- Glass‑morphism background with subtle blur.
- Smooth transition animations on button hover, panel expand/collapse, and marker pulse.

---

*All components listed above are present in the current `index.html` and are fully functional after the migration to Google Maps.*

### 6.10. Simulated Data Overview
- **Purpose**: The frontend telemetry simulators generate synthetic data to demonstrate model predictions without requiring real sensor inputs.
- **How It Works**: When a user adjusts a slider and clicks **Run Inference**, the selected values are packed into a JSON payload and sent to the corresponding FastAPI microservice (ports 8000‑8006). Each microservice contains a lightweight data generator that produces realistic‑looking values within the defined physical ranges.
- **Model‑Specific Simulations**:
  - **01 /Flood** – Simulates river level, soil moisture, and 24‑hour rainfall. The service computes a risk score based on water level > 3.5 m and high soil saturation.
  - **02 /Wildfire** – Simulates ambient temperature, relative humidity, and combustion‑gas concentration. VPD (vapor‑pressure‑deficit) is derived to assess fire risk; high gas + low humidity triggers warnings.
  - **03 /Landslide** – Simulates soil moisture, pore pressure, and tilt angle. Combined high tilt (> 5°) and pore pressure (> 45 kPa) raise the landslide probability.
  - **04 /Air Quality** – Simulates PM2.5, PM10, and NO₂ levels. AQI thresholds are applied (PM2.5 > 150 µg/m³ → critical).
  - **05 /Extreme Heat** – Simulates temperature, humidity, solar radiation, and wind speed. A heat‑index formula produces the “apparent temperature” used for alerts.
  - **06 /Toxic Plume** – Simulates gas‑sensor response, PM2.5/PM10, ambient temperature, and humidity. Gas response > 500 (warning) or > 850 (critical) combined with particulate levels triggers plume alarms.

**Rationale for Simulated Node Locations**
The simulated nodes are positioned at **Western Ghats, Delhi CAAQM, Vizag Complex, Varanasi Ganga, and Goa Forest** to capture a wide spectrum of climatic and geographic scenarios:
- **Western Ghats** – mountainous, high precipitation zones, ideal for testing flood and landslide models.
- **Delhi CAAQM** – densely populated urban area with significant air‑quality concerns, useful for wildfire and toxic plume simulations.
- **Vizag Complex** – coastal industrial region, providing data for extreme heat and marine‑influenced humidity variations.
- **Varanasi Ganga** – riverine environment with variable water quality, supporting aquatic‑health and flood risk testing.
- **Goa Forest** – tropical forest ecosystem, offering dense vegetation and high biodiversity, valuable for fire‑risk and plume dispersion studies.

Placing simulated sensors in these diverse locales ensures that each early‑warning model is exercised under realistic, region‑specific stressors, demonstrating the platform’s ability to handle heterogeneous environmental conditions.
  - **07 /Aquatic Health** – Simulates pH, turbidity, total dissolved solids (TDS), electrical conductivity (EC), and dissolved oxygen. Thresholds on pH, turbidity, and TDS generate water‑quality risk categories.
- **Visualization**: The returned risk label and confidence score are displayed instantly in the console panel alongside the simulated input values.
- **Extensibility**: The generator logic can be replaced with real sensor streams; the UI remains unchanged because it relies solely on the JSON contract.
### 6.10.1 Simulated Node Locations

| Console | Map Container | Node / Label (shown in UI) | Simulated Variables | FastAPI Port |
|---|---|---|---|---|
| Flood | `#map-flood` | Western Ghats River | River level, soil moisture, 24‑hour rainfall | 8000 |
| Wildfire | `#map-fire` | Western Ghats Forest | Ambient temperature, relative humidity, combustion‑gas concentration | 8001 |
| Landslide | `#map-land` | Western Ghats Slopes | Soil moisture, pore pressure, tilt angle | 8002 |
| Air Quality | `#map-air` | Delhi / Mumbai CAAQM | PM₂.₅, PM₁₀, NO₂ | 8003 |
| Extreme Heat | `#map-heat` | Maharashtra Weather Node | Temperature, humidity, solar radiation, wind speed | 8004 |
| Toxic Plume | `#map-ind` | Vizag Gas Array Node | Gas‑sensor response, PM₂.₅, PM₁₀, temperature, humidity | 8005 |
| Aquatic Health | `#map-water` | Goa Coastal Sensor | pH, turbidity, TDS, EC, dissolved oxygen | 8006 |
---
