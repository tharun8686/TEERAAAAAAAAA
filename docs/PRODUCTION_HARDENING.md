# TerraEdge — Phase 8 Production Hardening Specification

## 1. Overview & Objectives
Phase 8 hardens TerraEdge from an experimental prototype into a field-deployable, secure, observable, and recoverable architecture suitable for critical SIH operational demonstrations.

---

## 2. Hardening Matrix

| Domain | Development Baseline | Production Hardened State |
|---|---|---|
| **API Security** | Unauthenticated mutation routes | RBAC with `ADMIN` and `OPERATOR` tokens |
| **CORS** | `allow_origins=["*"]` | Configurable `TERRAEDGE_ALLOWED_ORIGINS` |
| **Logging** | Unstructured `print()` | JSON structured logs with `request_id`, `node_id`, `hazard` |
| **Request Tracking** | No correlation IDs | Injected `X-Request-ID` tracing HTTP to ML to CAP |
| **Metrics** | None | In-memory `MetricsCollector` (inferences, latencies, alerts) |
| **Health Checks** | Basic `/health` | Dedicated `/health/live`, `/health/ready`, `/api/system/status` |
| **Model Metadata** | Hardcoded configs | Versioned model registry with schema tracking & error counts |
| **Queue Protection** | Unbounded growth | Retention purges, disk size monitoring, hot backup CLI |
| **Containerization** | Host execution only | Production `Dockerfile` and `docker-compose.yml` |

---

## 3. Environment Modes

1. **`DEVELOPMENT`**: Open access, local in-memory fallbacks, relaxed token checking, debug logging.
2. **`TEST`**: Deterministic mocks, external notifications disabled, isolated SQLite databases.
3. **`DEMO`**: Multi-node simulator active, dry-run notifications, explicit `SIMULATED` badging.
4. **`PRODUCTION`**: Simulator disabled, real provider credentials validated, strict RBAC enforcement, hardware indicators explicit.
