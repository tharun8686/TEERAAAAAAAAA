# TerraEdge Multi-Node Environmental Intelligence Architecture

## 1. Executive Summary
Phase 5 converts the TerraEdge system from a single-point sensor pipeline into a distributed, multi-node edge intelligence network. The architecture establishes a clear separation of concerns between:
- **Node-Level Intelligence**: High-resolution, local multi-hazard machine learning inference executed continuously per field station.
- **District & Regional Intelligence**: Freshness-weighted spatial risk aggregation, confidence synthesis, multi-hazard priority ranking, and geographic hotspot clustering.

```
       ┌─────────────────────────────────────────────────────────┐
       │                 FIELD SENSOR NETWORK                     │
       └─────────────────────────────────────────────────────────┘
              │                           │
       [Physical Node]             [Simulated Nodes]
       ESP32-S3 + Sensors          TE-SIM-001 ... TE-SIM-N
       (Marked LIVE)               (Marked SIMULATED)
              │                           │
         LoRa 433 MHz                    HTTP
              │                           │
              ▼                           ▼
       ┌─────────────────────────────────────────────────────────┐
       │             TYPE B EDGE GATEWAY (:8000)                 │
       │                                                         │
       │  ┌────────────────┐     ┌────────────────────────────┐  │
       │  │ Dynamic Node   │     │ Per-Node Isolated History  │  │
       │  │ Registry       │     │ (Rain, PM2.5, Tilt, Gas)   │  │
       │  └────────┬───────┘     └─────────────┬──────────────┘  │
       │           │                           │                 │
       │           ▼                           ▼                 │
       │  ┌──────────────────────────────────────────────────┐   │
       │  │          7 Hazard ML Inference Engines           │   │
       │  │  Flood · Wildfire · Landslide · Air Quality ·    │   │
       │  │  Extreme Heat · Toxic Flame · Water Quality      │   │
       │  └──────────────────────┬───────────────────────────┘   │
       │                         │                               │
       │                         ▼                               │
       │  ┌──────────────────────────────────────────────────┐   │
       │  │    District Aggregation & Hotspot Engine         │   │
       │  │  • Freshness decay weighting                     │   │
       │  │  • Independent multi-node confidence scaling     │   │
       │  │  • Derived district severity synthesis           │   │
       │  │  • Spatial hotspot proximity clustering          │   │
       │  └──────────────────────┬───────────────────────────┘   │
       └─────────────────────────┼───────────────────────────────┘
                                 │
                   ┌─────────────┴─────────────┐
                   ▼                           ▼
       ┌───────────────────────┐   ┌───────────────────────┐
       │   SUPABASE DATABASE   │   │  LIVE GIS DASHBOARD   │
       │ • nodes               │   │ • Node markers        │
       │ • predictions         │   │ • District selector   │
       │ • alerts              │   │ • Hotspot alerts      │
       └───────────────────────┘   └───────────────────────┘
```

---

## 2. Dynamic Node Registry & Health Lifecycle
Every node is tracked in the gateway registry (`gateway/node_manager.py`) with dynamic health states based on elapsed time $\Delta t$ since `last_seen`:

| Status | Elapsed Time ($\Delta t$) | Description |
| :--- | :--- | :--- |
| **ONLINE** | $\Delta t \le 120\text{s}$ | Node active and transmitting healthy telemetry. |
| **STALE** | $120\text{s} < \Delta t \le 300\text{s}$ | Telemetry delayed; freshness weight smoothly decays. |
| **OFFLINE** | $\Delta t > 300\text{s}$ | Node unresponsive; excluded from real-time district risk aggregation. |

### Tracked Node Attributes
- `node_id`: Unique identifier (e.g. `TE-001`, `TYPE-A-101`)
- `node_type`: Hardware class (`Type-A`, `Type-B`, `Virtual`)
- `state` & `district`: Geographic administrative anchors (e.g. `Tamil Nadu`, `Tiruchirappalli`)
- `zone`: Local basin or catchment description
- `latitude` & `longitude`: WGS84 coordinates
- `status`: Dynamic lifecycle state (`ONLINE`, `STALE`, `OFFLINE`)
- `battery_pct`: Battery charge percentage
- `capabilities`: Active sensor hardware groups (e.g. `bme680`, `sds011`, `rainfall`, `water_level`)
- `node_profile`: Inferred profile (`FLOOD_HYDROLOGICAL`, `AIR_QUALITY_STATION`, etc.)
- `firmware_version`: Firmware release string
- `is_simulated`: `False` for physical LoRa/ESP32 nodes, `True` for synthetic streams
- `gateway_id`: Ingesting edge gateway ID
- `rssi_dbm` & `snr_db`: LoRa RF signal strength and quality
- `packets_received` & `packets_lost`: Transmission reliability metrics

---

## 3. Multi-Node Telemetry Isolation
To prevent cross-contamination of time-series features (such as multi-horizon rainfall accumulation, PM2.5 trends, soil moisture rates, and tilt velocity), the gateway maintains strictly segregated in-memory circular history buffers per `node_id` in `gateway/telemetry.py`.

---

## 4. District Risk Aggregation Mathematical Formulation

### 4.1. Freshness Weighting
For node $i$ reporting at timestamp $t_i$, the elapsed time $\Delta t_i = t_{\text{now}} - t_i$ produces weight $w_i \in [0.0, 1.0]$:
$$w_{\text{freshness}}(i) = \begin{cases} 
1.0 - \left(\frac{\Delta t_i}{120}\right) \times 0.15 & \text{if } \Delta t_i \le 120\text{s (ONLINE)} \\
0.80 - \left(\frac{\Delta t_i - 120}{180}\right) \times 0.65 & \text{if } 120\text{s} < \Delta t_i \le 300\text{s (STALE)} \\
0.0 & \text{if } \Delta t_i > 300\text{s (OFFLINE)}
\end{cases}$$

### 4.2. Aggregated District Risk
For each hazard $H$ in a district:
$$\text{DistrictRisk}(H) = \frac{\sum_{i \in \text{Active}} w_i \cdot \left(\frac{\text{Confidence}_i}{100}\right) \cdot \text{Risk}_i(H)}{\sum_{i \in \text{Active}} w_i \cdot \left(\frac{\text{Confidence}_i}{100}\right)}$$

### 4.3. Independent District Confidence Synthesis
District confidence is synthesized independently from risk, scaling with active node support:
$$\text{DistrictConfidence}(H) = \left(\frac{\sum_{i} w_i \cdot \text{Confidence}_i}{\sum_i w_i}\right) \times \min\left(1.0, 0.80 + 0.12 \cdot \log_2(N_{\text{active}} + 1)\right)$$

### 4.4. Synthesized District Severity
- **CRITICAL**: If ($\text{DistrictRisk} \ge 65\%$ AND at least 1 node is `CRITICAL`) OR (at least 2 nodes are `CRITICAL`) OR ($\text{DistrictRisk} \ge 75\%$).
- **WARNING**: If ($\text{DistrictRisk} \ge 45\%$ AND at least 1 node is `WARNING`) OR (at least 1 node is `CRITICAL`) OR ($\text{DistrictRisk} \ge 55\%$).
- **WATCH**: If ($\text{DistrictRisk} \ge 30\%$) OR (at least 1 node is `WATCH`).
- **NORMAL**: Otherwise.

### 4.5. Multi-Hazard Priority Ranking
Hazards are sorted descending by Priority Score:
$$\text{PriorityScore}(H) = \text{DistrictRisk}(H) \times \left(1.0 + 0.25 \times \text{Weight}_{\text{sev}}\right) \times \sqrt{1 + N_{\text{affected}}}$$
where $\text{Weight}_{\text{sev}} \in \{0, 1, 2, 3\}$ for $\{\text{NORMAL}, \text{WATCH}, \text{WARNING}, \text{CRITICAL}\}$.

---

## 5. Spatial Hotspot Detection
Hotspots are geographic clusters where multiple active nodes within $25\text{km}$ report elevated threat ($\text{Risk} \ge 60\%$ or Severity $\in \{\text{WARNING}, \text{CRITICAL}\}$) for the same hazard.
Centroid calculation:
$$\text{Lat}_{\text{center}} = \frac{1}{K}\sum_{k=1}^K \text{Lat}_k, \quad \text{Lon}_{\text{center}} = \frac{1}{K}\sum_{k=1}^K \text{Lon}_k$$

---

## 6. Live Hardware vs Simulated Nodes
- **Live Hardware Nodes** (e.g. `TE-001` transmitting via ESP32-S3 + LoRa) are tagged `is_simulated: False` and rendered with a vibrant green `LIVE HARDWARE` badge.
- **Simulated Nodes** (e.g. synthetic demonstration streams) are tagged `is_simulated: True` and rendered with a `SIMULATED` badge.
- Both types seamlessly coexist in the backend aggregation pipeline without distorting physical deployment truth.
