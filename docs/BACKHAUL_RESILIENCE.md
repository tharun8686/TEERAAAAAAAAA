# TerraEdge — Resilient Edge Backhaul & Communication Failover

## 1. Executive Summary & Philosophy

In remote environmental hazard monitoring (deep forests, mountain ranges, river basins), communication infrastructure is inherently fragile. Severe weather, seismic events, or forest fires frequently sever terrestrial telecommunications (Wi-Fi, Ethernet, Fiber) at the exact moment early warnings are most critical.

TerraEdge implements a strict **Edge-First Architecture**:
- The Type B Edge Gateway is a fully self-contained compute node.
- All 7 ML hazard inference engines, spatial risk calculations, dynamic node lifecycle tracking, and OASIS CAP v1.2 emergency alerts execute **locally in real-time**, completely independent of cloud availability.
- Cloud connectivity is treated as an eventual synchronization channel rather than an operational dependency.

---

## 2. Multi-Tier Backhaul Hierarchy

TerraEdge supports a 4-tier communication failover hierarchy:

```
                  ┌─────────────────────────────────────┐
                  │      Type B Edge Gateway Core       │
                  │ (7 ML Models + Risk Engine + Queue) │
                  └──────────────────┬──────────────────┘
                                     │
         ┌───────────────────────────┼───────────────────────────┐
         ▼                           ▼                           ▼
┌──────────────────┐       ┌──────────────────┐       ┌──────────────────┐
│  Tier 1: Primary │       │ Tier 2: Secondary│       │ Tier 3: Tertiary │
│ Wi-Fi / Ethernet │       │  Cellular 4G/LTE │       │  Satellite SBD   │
│  (High Bandwidth)│       │(Medium Bandwidth)│       │  (Low Bandwidth) │
└────────┬─────────┘       └────────┬─────────┘       └────────┬─────────┘
         │                          │                          │
         ▼                          ▼                          ▼
   [State: ONLINE]          [State: DEGRADED]          [State: DEGRADED]
         │                          │                          │
         └──────────────────────────┼──────────────────────────┘
                                    │ (All Blacked Out)
                                    ▼
                          ┌──────────────────┐
                          │ Tier 4: Fallback │
                          │ Local-Only Mode  │
                          │  (Zero Data Loss │
                          │   SQLite Buffer) │
                          └─────────┬────────┘
                                    ▼
                            [State: OFFLINE]
```

### Backhaul States
| State | Description | Ingestion & ML | Cloud Synchronization |
|---|---|---|---|
| `ONLINE` | Primary broadband (Wi-Fi / Ethernet) functional | Full Local Edge AI (7 models) | Real-time direct cloud sync |
| `DEGRADED` | Primary down; running over Cellular (4G) or Satellite | Full Local Edge AI (7 models) | Priority-compressed sync |
| `OFFLINE` | All external links severed | Full Local Edge AI (7 models) | Zero cloud sync; 100% durable local buffer |
| `SYNCING` | Network link restored; flushing backlog | Full Local Edge AI (7 models) | Relational batch store-and-forward |

---

## 3. Modular Transport Adapters

### 3.1 Internet (Wi-Fi / Ethernet) Adapter
- **File**: `gateway/backhaul/adapters/internet.py`
- **Class**: `InternetBackhaulAdapter`
- **Protocol**: HTTP/HTTPS ping & REST Supabase Client
- **Health Check**: Fast HEAD/GET requests against cloud endpoints with configurable timeout (`BACKHAUL_PING_TIMEOUT_S=3.0`).

### 3.2 Cellular (4G/LTE) Adapter
- **File**: `gateway/backhaul/adapters/cellular.py`
- **Class**: `CellularBackhaulAdapter`
- **Hardware Profile**: Quectel EC25 / SIM7600 UART AT-command interface (`CELLULAR_PORT`, `CELLULAR_APN`).
- **Status Reporting**: In development mode or without attached hardware, runs in modular `MOCK_ACTIVE` mode and returns:
  `"REAL HARDWARE NOT TESTED — MOCK CELLULAR MODEM"`.

### 3.3 Satellite (LEO / Iridium SBD) Adapter
- **File**: `gateway/backhaul/adapters/satellite.py`
- **Class**: `SatelliteBackhaulAdapter`
- **Hardware Profile**: Iridium 9602/9603 Short Burst Data (SBD) transceiver.
- **Status Reporting**: In development mode or without attached transceiver, runs in modular `MOCK_ACTIVE` mode and returns:
  `"REAL HARDWARE NOT TESTED — MOCK SATELLITE SBD TRANSCEIVER"`.

---

## 4. Operational Health & Telemetry Ingestion

### REST Endpoints
- `GET /health`: Surfaces gateway health, 7 loaded models, and real-time backhaul summary (`state`, `active_transport`, `queue_size`).
- `GET /api/backhaul/health`: Detailed backhaul diagnostics, per-adapter latency, and failover status.
- `GET /api/backhaul/queue`: Summary of pending, synced, and failed records in local SQLite WAL buffer.
- `POST /api/backhaul/sync`: Trigger on-demand sync batch flush.

### Resilient LoRa and HTTP Ingestion
When physical Type A sensor packets arrive via SX1278 LoRa or HTTP:
1. `node_manager` registers/updates node metadata locally.
2. `telemetry_engine` computes local rolling differentials ($dT/dt$, $dH/dt$, etc.).
3. `hazard_router` runs all 7 ML inference engines.
4. `risk_engine` ranks composite hazards and generates local canonical alerts and CAP v1.2 XML.
5. Ingest pipeline calls database persistence — if Supabase is offline, records automatically fall back to the durable SQLite store-and-forward queue.
