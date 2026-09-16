# TerraEdge — Security & Access Control Policy

## 1. Authentication & Role-Based Access Control (RBAC)

TerraEdge protects all mutating and administrative endpoints with lightweight token-based authentication via `X-API-Key` or `Authorization: Bearer <token>`.

### Role Matrix

| Endpoint | Method | Required Role | Description |
|---|---|---|---|
| `/health`, `/health/live`, `/health/ready` | `GET` | **Public** | Health & readiness inspection |
| `/api/nodes`, `/api/nodes/{id}` | `GET` | **Public** | Public telemetry & node inventory |
| `/api/districts`, `/api/risk-map`, `/api/hotspots` | `GET` | **Public** | Public GIS risk intelligence |
| `/api/alerts`, `/api/alerts/{id}/cap` | `GET` | **Public** | Public emergency alert feeds |
| `/api/telemetry` | `POST` | **Public / Sensor** | Sensor ingest (Rate limited) |
| `/api/alerts/{id}/acknowledge` | `POST` | **OPERATOR** | Incident operator acknowledgement |
| `/api/nodes`, `/api/nodes/{id}` | `POST / PATCH` | **ADMIN** | Dynamic node registration & config |
| `/api/alerts/{id}/dispatch` | `POST` | **ADMIN** | Manual authority alert dispatch |
| `/api/notification-targets` | `POST / PATCH / DELETE` | **ADMIN** | Destination management |
| `/api/backhaul/sync` | `POST` | **ADMIN** | Manual store-and-forward flush |
| `/api/queue/maintenance` | `POST` | **ADMIN** | Queue purge & storage maintenance |

---

## 2. Secret & Credential Isolation

- **Service Role Secrets**: `SUPABASE_SERVICE_KEY` resides strictly on the gateway server and is never passed to frontend browsers.
- **Log Sanitization**: Sensitive keys (`password`, `token`, `secret`, `api_key`, `auth`) are automatically redacted from structured JSON logs.
- **Public Feeds**: OASIS CAP XML and `/api/alerts` payloads are stripped of internal database credentials.

---

## 3. Threat Mitigation

- **Denial of Service (DoS)**: In-memory sliding window rate limiter protects expensive ingestion and dispatch endpoints.
- **Payload Bombing**: `RequestSizeLimitMiddleware` enforces a strict 1MB maximum body limit on HTTP JSON payloads.
- **Cross-Origin Resource Sharing (CORS)**: Restricts origin headers to explicitly configured domains (`TERRAEDGE_ALLOWED_ORIGINS`).
