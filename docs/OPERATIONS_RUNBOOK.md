# TerraEdge — Operations & Disaster Recovery Runbook

## 1. Routine Operational Commands

### Check System Status & Metrics
```bash
# High-level system health
curl http://localhost:8000/health

# Readiness probe
curl http://localhost:8000/health/ready

# Detailed operational overview
curl http://localhost:8000/api/system/status

# In-memory performance metrics
curl http://localhost:8000/api/system/metrics
```

### Hot Backup of Store-and-Forward Queue
```bash
python gateway/tools/backup_queue.py --output-dir /opt/backups/gateway
```

### Queue Maintenance & Retention Purge
```bash
curl -X POST "http://localhost:8000/api/queue/maintenance?retention_days=7" \
     -H "X-API-Key: terraedge-admin-secret-2026"
```

---

## 2. Disaster Recovery Procedures

### Scenario A: Network Blackout & Backlog Accumulation
1. **Diagnosis**: `GET /api/backhaul/health` reports `OFFLINE` and `queue_size > 0`.
2. **Action**: No manual intervention needed. Gateway operates in Local Edge Mode with full ML predictions.
3. **Recovery**: When link is restored, background worker flushes the backlog in relational order (`NODE` $\to$ `TELEMETRY` $\to$ `PREDICTION` $\to$ `ALERT` $\to$ `DISPATCH`).

### Scenario B: Process Crash / Power Loss Recovery
1. **Diagnosis**: Gateway unexpectedly reboots.
2. **Action**: Systemd or Docker automatically restarts `gateway.app`.
3. **Verification**: SQLite WAL checkpoint loads automatically from `gateway/data/backhaul_queue.db`. Check `GET /api/system/status` to verify 100% of pending records were recovered without data loss.

### Scenario C: Corrupted Database Recovery
1. Restore the most recent backup:
```bash
cp /opt/backups/gateway/backhaul_queue_YYYYMMDD_HHMMSS.bak gateway/data/backhaul_queue.db
python -m gateway.app
```
