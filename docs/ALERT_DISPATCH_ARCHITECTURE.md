# TerraEdge — Automated Multi-Channel Alert & Authority Dispatch Architecture (Phase 6)

## 1. Executive Summary

Phase 6 transitions verified environmental hazard predictions and district risk alert candidates (`alert_candidate = true`) into an authority-grade multi-channel emergency notification pipeline. The Type B Edge Gateway serves as the single source of truth for risk, confidence, severity, and alert qualification, dispatching notifications across SMS, Email, Outbound Webhooks, and OASIS Common Alerting Protocol (CAP v1.2) XML feeds.

---

## 2. End-to-End Notification Pipeline

```
TYPE A SENSOR NODE (ESP32-S3)
             │
             │ SX1278 / RA-02 LoRa (433 MHz)
             ▼
TYPE B EDGE GATEWAY (FastAPI)
             │
             ▼
7 AI/ML INFERENCE ENGINES
(Flood, Wildfire, Landslide, Air Quality, Extreme Heat, Industrial, Water Quality)
             │
             ▼
MULTI-HAZARD RISK ENGINE & PRIORITY RANKING
             │
             ▼
DISTRICT AGGREGATION & SPATIAL HOTSPOT DETECTOR
             │
             ▼ (alert_candidate = true, Severity >= WARNING)
CANONICAL ALERT NORMALIZATION (`CanonicalAlert`)
             │
             ▼
ALERT POLICY & TARGET MATCHING ENGINE (`rules.py`)
             │
             ▼
DEDUPLICATION & STATE MACHINE (`deduplication.py`)
    ├── Initial Breach: DISPATCH_INITIAL
    ├── Repeat Polling Cycle (No Change): SUPPRESS_DUPLICATE
    ├── Severity Escalation / +15% Risk Jump: DISPATCH_UPDATE
    └── Hazard Subsides to NORMAL: RESOLVED
             │
             ▼
MULTI-CHANNEL DISPATCH ORCHESTRATOR (`dispatcher.py`)
    ├── SMS Channel (Twilio REST / Safe Dry-Run)
    ├── Email Channel (SMTP TLS / Safe Dry-Run)
    ├── Webhook Channel (HTTP POST JSON / Retry & Timeout)
    └── CAP v1.2 XML Generator (OASIS Compliant Emergency Feed)
             │
             ▼
SUPABASE / IN-MEMORY AUDIT PERSISTENCE (`notification_dispatches`)
             │
             ▼
LIVE WEB DASHBOARD (Real-Time Badge Sync & Operator Acknowledgment)
```

---

## 3. Canonical Alert Object (`CanonicalAlert`)

All alert instances—whether generated from point node threshold breaches, regional district aggregations, or spatial hotspot clusters—are normalized into the unified `CanonicalAlert` data structure:

| Field | Type | Description | Example |
|---|---|---|---|
| `alert_id` | `str` | Unique sequential identifier | `ALT-FLOO-0042` |
| `event_id` | `str` | Composite deduplication key | `flood:chennai` |
| `hazard` | `str` | Primary hazard classification | `Flood` |
| `severity` | `str` | Authoritative severity level | `CRITICAL`, `WARNING`, `WATCH` |
| `risk_pct` | `float` | Calibrated threat risk (0–100%) | `85.4%` |
| `confidence_pct` | `float` | ML model confidence score | `91.2%` |
| `node_id` | `Optional[str]` | Originating physical node ID | `TE-001` |
| `affected_nodes` | `List[str]` | Contributing field nodes | `["TE-001", "TE-002"]` |
| `state` | `str` | State administrative jurisdiction | `Tamil Nadu` |
| `district` | `Optional[str]` | District administrative boundary | `Chennai` |
| `zone` | `Optional[str]` | Micro-zone or river basin | `Adyar River Basin` |
| `latitude` / `longitude` | `float` | Centroid coordinates | `13.0827, 80.2707` |
| `radius_km` | `float` | Estimated impact perimeter | `7.5 km` |
| `lifecycle_state` | `Enum` | Current event lifecycle state | `DISPATCHED`, `ACTIVE`, `UPDATED`, `RESOLVED` |
| `is_simulated` | `bool` | Physical vs simulated flag | `False` (Live Hardware) |
| `dispatches` | `List[dict]` | Audit trail of sent dispatches | `[...]` |

---

## 4. Alert Lifecycle State Machine

```
[ TELEMETRY INGEST ]
        │
        ▼
   (DETECTED) ──[ Policy Match & Severity >= WARNING ]──► (DISPATCH_PENDING)
        │                                                         │
        │                                                         ▼
        │                                                   (DISPATCHED)
        │                                                         │
        ▼                                                         ▼
 (SUPPRESS_DUPLICATE) ◄────[ Repeat Cycle (< 300s) ]───────── (ACTIVE)
        │                                                         │
        │                                                         │ (Escalation / +15% Jump)
        │                                                         ▼
        └──────────────────────────────────────────────────► (UPDATED)
                                                                  │
                                                                  │ (Operator Action)
                                                                  ▼
                                                           (ACKNOWLEDGED)
                                                                  │
                                                                  │ (Severity -> NORMAL)
                                                                  ▼
                                                             (RESOLVED)
```

---

## 5. Deduplication & Rate-Limiting Policy

To protect emergency personnel and API quotas from notification storms during 2.5-second dashboard polling cycles:

1. **Deduplication Window**: Default `ALERT_DEDUP_WINDOW_SECONDS = 300` (5 minutes).
2. **Identical Severity & Risk**: If an alert for the same hazard and district is received within the window without material change, dispatch is suppressed (`SUPPRESS_DUPLICATE`).
3. **Escalation Trigger**: If severity jumps from `WARNING` $\to$ `CRITICAL`, immediate notification is triggered (`DISPATCH_UPDATE`).
4. **Material Risk Jump**: If risk score increases by $\ge +15.0\%$ within the same severity level, an updated dispatch is fired.
5. **Resolution Handling**: When sensor inputs return below threshold levels (`severity = NORMAL`), the event is closed as `RESOLVED`.

---

## 6. Multi-Channel Provider Implementations

### 6.1 SMS Channel (`SmsChannel`)
- **Provider**: Twilio REST API via `urllib.request` (zero extra dependencies).
- **Format**: Concise authority summary with hazard, severity, risk %, confidence %, location, and node count.
- **Dry-Run Mode**: When `TERRAEDGE_NOTIFICATION_MODE=dry_run` or credentials are unset, returns simulated acceptance (`DRYRUN-TWILIO-SMxxxx`) without carrier transmission.

### 6.2 Email Channel (`EmailChannel`)
- **Provider**: Standard SMTP with TLS support (`smtplib`).
- **Subject**: `[TERRAEDGE] {HAZARD} — {SEVERITY} — {DISTRICT}`
- **Body**: Plain text and HTML formatted advisory with detailed sensor indicators, confidence metrics, and dashboard links.
- **Dry-Run Mode**: Simulates email generation with message ID `DRYRUN-SMTP-MSG-xxxx`.

### 6.3 Webhook Channel (`WebhookChannel`)
- **Provider**: Outbound HTTP/HTTPS POST with JSON payload.
- **Headers**: `Content-Type: application/json`, `X-TerraEdge-Event: {Hazard}`, `X-TerraEdge-Severity: {Severity}`.
- **Resilience**: Configurable timeout (`WEBHOOK_TIMEOUT_SECONDS = 5.0`) with exponential backoff retry (`WEBHOOK_MAX_RETRIES = 2`).

### 6.4 Common Alerting Protocol (CAP v1.2) XML Channel (`CapChannel`)
- **Standard**: OASIS CAP v1.2 XML (`urn:oasis:names:tc:emergency:cap:1.2`).
- **Geographic Area**: Ingests district centroid coordinates and radius into `<circle>` geometry tags.
- **Schema Validation**: Built-in XML syntax and schema compliance verification.

---

## 7. Channel Failure Isolation

Every notification channel executes within an isolated error boundary. If SMS carrier credentials fail or an external webhook endpoint times out:
1. The error is captured in `notification_dispatches` audit log (`status = FAILED`).
2. Email, CAP XML, and other targets proceed without interruption.
3. The core Type B Gateway server never crashes or hangs.
4. The underlying alert remains fully active and accessible on the dashboard.

---

## 8. Notification Target Management & Routing

Recipients are configured dynamically via REST API:
- `GET /api/notification-targets`: List targets.
- `POST /api/notification-targets`: Register new authority recipient.
- `PATCH /api/notification-targets/{id}`: Update routing filters.
- `DELETE /api/notification-targets/{id}`: Decommission recipient.

Routing filters check:
- `target.enabled == True`
- `alert.severity >= target.min_severity`
- `alert.hazard in target.hazards` (or target has `"all"`)
- `alert.district == target.district` (or target has state-wide scope `None` / `"all"`)

---

## 9. Security & Credentials Protection

1. **Zero Hardcoded Secrets**: All API keys, tokens, and passwords originate from environment variables (`.env`).
2. **Safe Serialization**: Outbound payloads and API responses sanitize internal credentials and token values.
3. **Safe Dry-Run Default**: The default mode is `TERRAEDGE_NOTIFICATION_MODE=dry_run`, guaranteeing that automated test suites never send external messages.
