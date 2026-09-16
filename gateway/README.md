# TerraEdge — Type B Edge Gateway & Multi-Hazard Pipeline

## 1. Overview & Role in TerraEdge

The **Type B Edge Gateway** serves as the central integration and intelligence backbone of the TerraEdge Environmental Intelligence Network. It bridges distributed field sensing (Type A nodes) with machine learning inference, multi-hazard risk fusion, hazard priority ranking, and database persistence.

```text
[ TYPE A SENSOR NODE / SIMULATOR ]
                │
                │ Telemetry Payload (HTTP JSON / LoRa Bridge)
                ▼
      ┌────────────────────────────────────────────────────────┐
      │                  TYPE B EDGE GATEWAY                   │
      │                                                        │
      │ 1. Telemetry Validation (schemas.py)                   │
      │ 2. Node Manager & Inventory (node_manager.py)          │
      │ 3. Temporal History & Rates of Change (telemetry.py)   │
      │ 4. Hazard-Specific Feature Adapters (feature_builder)  │
      │ 5. Hazard Router (hazard_router.py)                    │
      │    ├── Flood ML Model                                  │
      │    ├── Wildfire ML Model                               │
      │    ├── Landslide ML Model                              │
      │    ├── Air Quality ML Model                            │
      │    ├── Extreme Heat ML Model                           │
      │    ├── Toxic Flame ML Model                            │
      │    └── Water Quality ML Model                          │
      │ 6. Multi-Hazard Risk & Ranking Engine (risk_engine.py) │
      │ 7. Supabase / In-Memory Persistence Layer              │
      └───────────────────────────┬────────────────────────────┘
                                  │
                                  ▼
         [ Unified REST API Response & Database Logs ]
```

---

## 2. Directory Structure

```text
gateway/
├── __init__.py            # Package root
├── app.py                 # FastAPI application & REST endpoints
├── config.py              # Environment configuration loader
├── schemas.py             # Pydantic schemas (TypeATelemetryPayload, UnifiedGatewayResponse)
├── node_manager.py        # Node inventory, health, battery & status tracking
├── telemetry.py           # In-memory time-series buffer & temporal derivative calculator
├── feature_builder.py     # Explicit feature adapters for all 7 hazard models
├── hazard_router.py       # Collision-free dynamic importer & isolated ML execution
├── risk_engine.py         # Multi-hazard risk normalization & priority ranking
├── simulator.py           # Multi-scenario synthetic telemetry generator CLI
└── README.md              # Technical documentation & guide
```

---

## 3. Installation & Setup

Ensure all dependencies from the root `requirements.txt` are installed:

```bash
python -m pip install -r requirements.txt
```

### Environment Configuration (`.env`)

Copy `.env.example` to `.env` in the repository root:

```env
GATEWAY_HOST=0.0.0.0
GATEWAY_PORT=8000
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_SERVICE_KEY=your-service-role-key
SUPABASE_LOG_PREDICTIONS=true
```

*(Note: If `SUPABASE_URL` is omitted, the gateway automatically falls back to an in-memory store so testing works out of the box with zero external configuration).*

---

## 4. Starting the Type B Gateway

Launch the FastAPI gateway server:

```bash
python -m uvicorn gateway.app:app --host 0.0.0.0 --port 8000 --reload
```

- **API Documentation (Swagger UI)**: `http://localhost:8000/docs`
- **Health Check**: `http://localhost:8000/health`

---

## 5. Running the Telemetry Simulator

The simulator streams realistic telemetry scenarios directly into the gateway:

### A. Individual Disaster Scenarios
```bash
# Flood / Monsoon Deluge Scenario
python gateway/simulator.py --scenario flood --count 5 --interval 2

# Dry Scrub Wildfire Scenario
python gateway/simulator.py --scenario wildfire --count 5 --interval 2

# Landslide Slope Instability Scenario
python gateway/simulator.py --scenario landslide --count 5 --interval 2

# Severe Air Quality / Smog Scenario
python gateway/simulator.py --scenario air_pollution --count 5 --interval 2

# Extreme Heatwave Scenario
python gateway/simulator.py --scenario extreme_heat --count 5 --interval 2

# Industrial Stack Leak / Toxic Plume Scenario
python gateway/simulator.py --scenario industrial_emissions --count 5 --interval 2

# Water Quality Contamination Scenario
python gateway/simulator.py --scenario water_quality --count 5 --interval 2

# Nominal Environmental Baseline (Normal Conditions)
python gateway/simulator.py --scenario normal --count 3 --interval 2
```

### B. Continuous Multi-Hazard Demonstration
```bash
# Cycle through all scenarios sequentially
python gateway/simulator.py --scenario all --count 16 --interval 2
```

---

## 6. Example API Requests & Responses

### Ingest Telemetry (`POST /api/telemetry`)

**Sample Request Body**:
```json
{
  "node_id": "TYPE-A-101",
  "node_type": "Type-A",
  "zone": "Kaveri Basin - Zone 1",
  "latitude": 10.7905,
  "longitude": 78.7047,
  "battery_pct": 94.5,
  "temperature_c": 28.4,
  "humidity_pct": 82.0,
  "pressure_hpa": 1004.2,
  "rainfall_1h_mm": 35.0,
  "rainfall_24h_mm": 115.0,
  "water_level_m": 3.42,
  "soil_moisture_pct": 86.0,
  "pm25": 18.0,
  "pm10": 35.0,
  "flame": 0,
  "tilt_magnitude": 2.1
}
```

**Unified Response**:
```json
{
  "node_id": "TYPE-A-101",
  "node_type": "Type-A",
  "zone": "Kaveri Basin - Zone 1",
  "timestamp": "2026-09-16T09:30:00Z",
  "location": {
    "latitude": 10.7905,
    "longitude": 78.7047
  },
  "battery_pct": 94.5,
  "composite_risk_pct": 88.5,
  "primary_hazard": "Flood",
  "primary_severity": "CRITICAL",
  "priority_score": 92.55,
  "ranked_hazards": [
    {
      "hazard": "Flood",
      "rank": 1,
      "risk_pct": 88.5,
      "confidence_pct": 90.0,
      "severity": "CRITICAL",
      "priority_score": 92.55
    },
    {
      "hazard": "Landslide",
      "rank": 2,
      "risk_pct": 42.0,
      "confidence_pct": 92.0,
      "severity": "WATCH",
      "priority_score": 56.0
    },
    {
      "hazard": "Extreme Heat",
      "rank": 3,
      "risk_pct": 15.0,
      "confidence_pct": 90.0,
      "severity": "NORMAL",
      "priority_score": 38.0
    }
  ],
  "hazard_results": {
    "Flood": {
      "hazard": "Flood",
      "risk_pct": 88.5,
      "confidence_pct": 90.0,
      "severity": "CRITICAL",
      "anomaly_score": 0.42,
      "top_features": ["water_level_m", "rain_24h"],
      "model_status": "success",
      "timestamp": "2026-09-16T09:30:00.100Z"
    },
    "Water Quality": {
      "hazard": "Water Quality",
      "risk_pct": 0.0,
      "confidence_pct": 0.0,
      "severity": "NORMAL",
      "model_status": "skipped",
      "skip_reason": "No water chemistry sensors detected (missing pH, TDS, Turbidity, DO probes)"
    }
  ],
  "alerts_triggered": [
    {
      "alert_id": "ALT-0008",
      "node_id": "TYPE-A-101",
      "severity": "CRITICAL",
      "risk_score_pct": 88.5,
      "timestamp": "2026-09-16T09:30:00.100Z"
    }
  ],
  "processing_time_ms": 14.8,
  "db_status": "in-memory"
}
```

---

## 7. Model Routing & Feature Adapters

1. **Direct In-Memory ML Execution**:
   - The gateway imports and executes the existing trained scikit-learn models directly in Python, bypassing HTTP network overhead.
   - Dynamic module loading prevents `sys.modules` collisions across directories.
2. **Missing Sensor Handling**:
   - If a node lacks sensors required by a specific hazard (e.g., a pure Flood node sending no pH/TDS data), `feature_builder.py` marks the hazard as `ready=False`.
   - The router records the model as `model_status: "skipped"` with an explicit reason, without fabricating risk numbers or failing other hazard inferences.
3. **Temporal Derivative Buffer**:
   - The gateway maintains a bounded history buffer per node (`collections.deque(maxlen=30)`) to calculate instantaneous rates of change, lag terms (`pm25_lag_30`), rolling standard deviations, and cyclical hour embeddings (`hour_sin`, `hour_cos`).

---

## 8. Database Persistence Layer

- Uses `common/terra_supabase.py` with automatic graceful fallback to in-memory store if credentials are not configured.
- Seeds node inventory into the `public.nodes` table on startup.
- Logs prediction records to `public.predictions` for historical analytics.
- Inserts threshold breach records into `public.alerts` whenever a hazard reaches `WARNING` or `CRITICAL`.

---

## 9. Current Limitations & Next Steps

### What is Completed in Phase 1:
- ✅ Type A Telemetry Ingestion & Pydantic Validation
- ✅ Node Manager & Dynamic Inventory Registry
- ✅ Temporal History & Derivative Calculation
- ✅ Explicit Feature Adapters for all 7 Hazards
- ✅ Multi-Hazard Inference Orchestration (Zero Collisions)
- ✅ Multi-Hazard Risk Normalization & Priority Ranking
- ✅ Supabase / In-Memory Data Persistence
- ✅ Multi-Scenario Telemetry Simulator

### What Remains for Future Phases:
- ⏳ **Physical SX1278 LoRa Receiver Hardware Driver**: A LoRa SPI receiver script to forward decoded packets into `/api/telemetry`.
- ⏳ **Live Dashboard WebSocket / Polling Integration**: Updating `index.html` to consume `/api/telemetry` instead of simulated timers.
- ⏳ **Alert Dispatcher**: External SMS/Email/Push notification dispatchers.
