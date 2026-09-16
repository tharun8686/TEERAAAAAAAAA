# TerraEdge GIS Risk Mapping & API Guide (Phase 5)

## 1. Overview
TerraEdge Phase 5 establishes the Type B Edge Gateway as the backend source of truth for geographical environmental intelligence. The frontend dashboard operates purely as a visualization client, querying REST endpoints to render spatial risk maps, district aggregates, and hotspot clusters.

---

## 2. API Endpoints

### 2.1. GIS Risk Map Feed
- **Endpoint**: `GET /api/risk-map`
- **Query Parameters**:
  - `state` (optional): Filter nodes and districts by state (e.g. `Tamil Nadu`)
  - `district` (optional): Filter by district name (e.g. `Tiruchirappalli`)
- **Response Shape**:
```json
{
  "state": "Tamil Nadu",
  "district": null,
  "total_nodes": 10,
  "active_nodes": 8,
  "stale_nodes": 1,
  "offline_nodes": 1,
  "districts": [
    {
      "state": "Tamil Nadu",
      "district": "Tiruchirappalli",
      "node_count": 2,
      "active_nodes_count": 2,
      "composite_risk_pct": 78.5,
      "primary_hazard": "Flood",
      "primary_severity": "HIGH",
      "hazards": [
        {
          "hazard": "Flood",
          "rank": 1,
          "risk_pct": 78.5,
          "confidence_pct": 86.2,
          "severity": "HIGH",
          "affected_nodes": 2,
          "total_reporting_nodes": 2,
          "priority_score": 192.3,
          "alert_candidate": true,
          "top_contributing_nodes": ["TE-001", "TE-002"]
        }
      ],
      "hotspots": [
        {
          "hotspot_id": "HS-FLO-1079_7870",
          "hazard": "Flood",
          "center_lat": 10.8053,
          "center_lon": 78.6979,
          "radius_km": 5.0,
          "risk_pct": 78.5,
          "confidence_pct": 86.2,
          "severity": "HIGH",
          "affected_nodes": ["TE-001", "TE-002"]
        }
      ],
      "nodes": [...]
    }
  ],
  "nodes": [...],
  "hotspots": [...],
  "timestamp": "2026-09-16T10:30:00Z"
}
```

### 2.2. District Risk Aggregation
- **Endpoint**: `GET /api/districts/{district}/risk?state=Tamil%20Nadu`
- **Response Shape**: `DistrictRiskResponse` model containing the district composite score, ranked hazard list, active hotspots, and node statuses.

### 2.3. Active Districts Directory
- **Endpoint**: `GET /api/districts?state=Tamil%20Nadu`
- **Response Shape**: List of registered districts with node counts and current peak hazard.

### 2.4. Dynamic Node Registry
- **Endpoint**: `POST /api/nodes` — Dynamic node registration
- **Endpoint**: `GET /api/nodes` — Filter by state, district, or status
- **Endpoint**: `GET /api/nodes/{node_id}` — Node profile & radio health
- **Endpoint**: `PATCH /api/nodes/{node_id}` — Partial attribute update
- **Endpoint**: `GET /api/nodes/{node_id}/latest` — Latest inference and raw telemetry
- **Endpoint**: `GET /api/nodes/{node_id}/history` — Recent time series history

---

## 3. Simulator Multi-Node Operations

### 3.1. Launching Concurrent Multi-Hazard Demo
```bash
python gateway/simulator.py --multi-node-demo
```
This spawns 4 concurrent simulated nodes:
- `TE-001` (Tiruchirappalli Floodplain — Flood 82%)
- `TE-002` (Tiruchirappalli Canal — Flood 76%)
- `TE-003` (Chennai Industrial — Air Pollution 71%)
- `TE-004` (Coimbatore Foothills — Normal 12%)

### 3.2. Launching Specific Node Scenarios
```bash
# Specific Flood Node
python gateway/simulator.py --scenario flood --node-id TE-001 --district Tiruchirappalli

# Specific Air Pollution Node
python gateway/simulator.py --scenario air_pollution --node-id TE-003 --district Chennai
```

---

## 4. Live Dashboard Verification Procedure
1. **Start Type B Gateway**:
   ```bash
   python -m gateway.app
   ```
2. **Launch Multi-Node Simulator**:
   ```bash
   python gateway/simulator.py --multi-node-demo --interval 2.0
   ```
3. **Open Dashboard**:
   Open `index.html` in browser.
   - Gateway status indicator connects to `:8000`.
   - Map pins populate with live markers colored by backend severity.
   - Selecting `Tiruchirappalli` displays `Flood` as Rank #1 with Active Hotspot alert.
   - Selecting `Chennai` displays `Air Quality` as dominant threat.
