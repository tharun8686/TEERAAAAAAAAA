"""
Terra Edge — shared Supabase data layer.

Every hazard microservice (Flood, Wildfire, Landslide, Air Pollution, Extreme Heat,
Industrial Emissions, Water Quality) used to keep its alerts in a plain Python list,
which meant all history was lost on restart and no two services could see each
other's data. This module replaces that with a single Supabase (Postgres) backend.

Design rules
------------
1. Never break the API. If Supabase is not configured, or a query fails, every
   function transparently falls back to the in-process list it replaced. The
   services keep serving predictions either way.
2. Preserve response shapes. `fetch_alerts()` returns the exact dicts the old
   in-memory `alerts_db` returned, so existing clients and docs stay valid.
3. Server-side only. Use the SERVICE ROLE key here; it bypasses row level
   security and must never be shipped to the browser.

Environment (read from the repo-root .env):
    SUPABASE_URL          https://<project-ref>.supabase.co
    SUPABASE_SERVICE_KEY  service_role key (preferred for backends)
    SUPABASE_KEY          fallback if SUPABASE_SERVICE_KEY is unset (e.g. anon key)
"""

from __future__ import annotations

import os
import threading
import datetime
import uuid
from typing import Any, Dict, List, Optional

# ──────────────────────────────────────────────────────────────────────
# Environment loading — walk up from this file to find the repo-root .env
# ──────────────────────────────────────────────────────────────────────

def _load_dotenv() -> None:
    try:
        from dotenv import load_dotenv
    except ImportError:
        return
    here = os.path.dirname(os.path.abspath(__file__))
    for _ in range(6):
        candidate = os.path.join(here, ".env")
        if os.path.exists(candidate):
            load_dotenv(candidate, override=False)
            return
        parent = os.path.dirname(here)
        if parent == here:
            return
        here = parent


_load_dotenv()

SUPABASE_URL = (os.getenv("SUPABASE_URL") or "").strip()
SUPABASE_KEY = (
    os.getenv("SUPABASE_SERVICE_KEY")
    or os.getenv("SUPABASE_SERVICE_ROLE_KEY")
    or os.getenv("SUPABASE_KEY")
    or ""
).strip()

ALERTS_TABLE = os.getenv("SUPABASE_ALERTS_TABLE", "alerts").strip() or "alerts"
PREDICTIONS_TABLE = os.getenv("SUPABASE_PREDICTIONS_TABLE", "predictions").strip() or "predictions"
NODES_TABLE = os.getenv("SUPABASE_NODES_TABLE", "nodes").strip() or "nodes"
NOTIFICATION_TARGETS_TABLE = os.getenv("SUPABASE_NOTIFICATION_TARGETS_TABLE", "notification_targets").strip() or "notification_targets"
NOTIFICATION_DISPATCHES_TABLE = os.getenv("SUPABASE_NOTIFICATION_DISPATCHES_TABLE", "notification_dispatches").strip() or "notification_dispatches"

# Logging every prediction is useful history but doubles the write volume.
# Set SUPABASE_LOG_PREDICTIONS=false to record only alerts.
LOG_PREDICTIONS = (os.getenv("SUPABASE_LOG_PREDICTIONS", "true").strip().lower()
                   not in ("false", "0", "no", "off"))

# ──────────────────────────────────────────────────────────────────────
# Client (created once, lazily, and never re-raises into request handlers)
# ──────────────────────────────────────────────────────────────────────

_client = None
_client_ready = False
_client_error: Optional[str] = None
_lock = threading.Lock()

# Per-hazard in-memory mirror. Also the fallback store when Supabase is off.
_memory_alerts: Dict[str, List[Dict[str, Any]]] = {}
_memory_targets: Dict[str, Dict[str, Any]] = {}
_memory_dispatches: List[Dict[str, Any]] = []
_seq_counters: Dict[str, int] = {}


def _log(msg: str) -> None:
    print(f"[terra-supabase] {msg}", flush=True)


def _enqueue_offline(record_type: str, record_id: str, payload: Dict[str, Any], observed_at: Optional[str] = None) -> None:
    """Safely enqueues record to Phase 7 durable SQLite store-and-forward queue."""
    try:
        from gateway.backhaul import durable_queue
        durable_queue.enqueue(record_type, record_id, payload, observed_at)
    except Exception:
        pass


def is_configured() -> bool:
    """True when both a project URL and an API key are present in the environment."""
    return bool(SUPABASE_URL and SUPABASE_KEY)


def get_client():
    """Return a cached Supabase client, or None if unconfigured/unreachable."""
    global _client, _client_ready, _client_error

    if _client_ready:
        return _client

    with _lock:
        if _client_ready:
            return _client
        _client_ready = True

        if not is_configured():
            _client_error = "Database URL or API key not configured (in-memory mode)"
            _log("not configured - falling back to in-memory storage")
            return None

        try:
            from supabase import create_client
            _client = create_client(SUPABASE_URL, SUPABASE_KEY)
            _log(f"connected to {SUPABASE_URL}")
        except Exception as exc:  # noqa: BLE001 - never break startup
            _client = None
            _client_error = str(exc)
            _log(f"client init failed ({exc}) - falling back to in-memory storage")

        return _client


def status() -> Dict[str, Any]:
    """Connection summary, surfaced by each service on /health and /api/db-status."""
    client = get_client()
    return {
        "configured": is_configured(),
        "connected": client is not None,
        "url": SUPABASE_URL or None,
        "alerts_table": ALERTS_TABLE,
        "predictions_table": PREDICTIONS_TABLE,
        "log_predictions": LOG_PREDICTIONS,
        "error": _client_error,
        "mode": "supabase" if client is not None else "in-memory",
    }


def _utc_now_iso() -> str:
    return datetime.datetime.now(datetime.timezone.utc).isoformat()


# ──────────────────────────────────────────────────────────────────────
# Alert IDs — preserve the original "FIRE-ALT-0007" style numbering
# ──────────────────────────────────────────────────────────────────────

def next_alert_id(hazard: str, prefix: str) -> str:
    """
    Build the next sequential alert id for a hazard, e.g. "FIRE-ALT-0004".

    The counter is seeded once from the row count already in Supabase, so
    numbering continues across restarts instead of resetting to 0001.
    """
    with _lock:
        if hazard not in _seq_counters:
            _seq_counters[hazard] = _count_alerts(hazard)
        _seq_counters[hazard] += 1
        seq = _seq_counters[hazard]
    return f"{prefix}{seq:04d}"


def _count_alerts(hazard: str) -> int:
    client = get_client()
    if client is None:
        return len(_memory_alerts.get(hazard, []))
    try:
        res = (
            client.table(ALERTS_TABLE)
            .select("id", count="exact")
            .eq("hazard", hazard)
            .limit(1)
            .execute()
        )
        return int(res.count or 0)
    except Exception as exc:  # noqa: BLE001
        _log(f"count failed for '{hazard}' ({exc}) - starting sequence at 0")
        return len(_memory_alerts.get(hazard, []))


# ──────────────────────────────────────────────────────────────────────
# Alerts
# ──────────────────────────────────────────────────────────────────────

def insert_alert(hazard: str, alert: Dict[str, Any]) -> Dict[str, Any]:
    """
    Persist one alert and return it unchanged.

    The full original dict is stored in the `details` JSONB column, so each
    hazard keeps its own fields (top_features, trigger_values, predicted_pm25_60m …)
    without needing seven different tables. The common fields are also lifted into
    real columns so they can be indexed, filtered and sorted in SQL.
    """
    # Always keep the in-memory mirror in sync so reads work even if the DB is down.
    _memory_alerts.setdefault(hazard, []).append(alert)

    row = {
        "alert_id": alert.get("alert_id"),
        "hazard": hazard,
        "node_id": alert.get("node_id") or alert.get("station_id"),
        "state": alert.get("state", "Tamil Nadu"),
        "district": alert.get("district"),
        "gateway_id": alert.get("gateway_id", "GW-01"),
        "severity": alert.get("severity"),
        "risk_score": _first_number(
            alert.get("risk_score_pct"),
            alert.get("risk_score"),
            _as_pct(alert.get("risk_probability")),
            _as_pct(alert.get("fire_probability")),
            _as_pct(alert.get("heat_risk_probability")),
            _as_pct(alert.get("leak_risk_probability")),
            _as_pct(alert.get("probability")),
        ),
        "details": alert,
        "created_at": alert.get("timestamp") or _utc_now_iso(),
    }

    client = get_client()
    if client is None:
        _enqueue_offline("alert", alert.get("alert_id") or f"ALT-{hazard[:4].upper()}-{uuid.uuid4().hex[:6].upper()}", row, row.get("created_at"))
        return alert

    try:
        client.table(ALERTS_TABLE).insert(row).execute()
    except Exception as exc:  # noqa: BLE001 - a DB hiccup must not fail a prediction
        _log(f"alert insert failed for '{hazard}' ({exc}) - kept in memory only")
        _enqueue_offline("alert", alert.get("alert_id") or f"ALT-{hazard[:4].upper()}-{uuid.uuid4().hex[:6].upper()}", row, row.get("created_at"))

    return alert


def fetch_alerts(hazard: str, limit: int = 200) -> List[Dict[str, Any]]:
    """
    Return alerts for one hazard, oldest first, in the same shape the old
    in-memory list returned.
    """
    client = get_client()
    if client is None:
        return _memory_alerts.get(hazard, [])

    try:
        res = (
            client.table(ALERTS_TABLE)
            .select("alert_id, severity, node_id, state, district, risk_score, details, created_at")
            .eq("hazard", hazard)
            .order("created_at", desc=True)
            .limit(limit)
            .execute()
        )
        rows = list(res.data or [])
        out: List[Dict[str, Any]] = []
        for row in reversed(rows):  # back to oldest-first
            details = row.get("details")
            if isinstance(details, dict) and details:
                out.append(details)
            else:
                out.append({
                    "alert_id": row.get("alert_id"),
                    "node_id": row.get("node_id"),
                    "state": row.get("state"),
                    "district": row.get("district"),
                    "severity": row.get("severity"),
                    "risk_score": row.get("risk_score"),
                    "timestamp": row.get("created_at"),
                })
        return out
    except Exception as exc:  # noqa: BLE001
        _log(f"alert fetch failed for '{hazard}' ({exc}) - serving in-memory copy")
        return _memory_alerts.get(hazard, [])


# ──────────────────────────────────────────────────────────────────────
# Predictions (full inference history, not just threshold breaches)
# ──────────────────────────────────────────────────────────────────────

def fetch_predictions(hazard: str, hours: int = 24, limit: int = 200) -> List[Dict[str, Any]]:
    """Recent prediction history for one hazard, oldest first. Powers the Analytics trend charts."""
    client = get_client()
    if client is None:
        return []

    try:
        cutoff = (datetime.datetime.now(datetime.timezone.utc)
                  - datetime.timedelta(hours=hours)).isoformat()
        res = (
            client.table(PREDICTIONS_TABLE)
            .select("severity, risk_score, node_id, state, district, created_at")
            .eq("hazard", hazard)
            .gte("created_at", cutoff)
            .order("created_at", desc=False)
            .limit(limit)
            .execute()
        )
        return list(res.data or [])
    except Exception as exc:  # noqa: BLE001
        _log(f"prediction history fetch failed for '{hazard}' ({exc})")
        return []


def log_prediction(hazard: str, node_id: Optional[str],
                   payload: Dict[str, Any], result: Dict[str, Any]) -> None:
    """Fire-and-forget record of a single inference. Never raises."""
    if not LOG_PREDICTIONS:
        return

    row = {
        "hazard": hazard,
        "node_id": node_id,
        "state": payload.get("state") or result.get("state", "Tamil Nadu"),
        "district": payload.get("district") or result.get("district"),
        "gateway_id": payload.get("gateway_id") or result.get("gateway_id", "GW-01"),
        "severity": result.get("severity"),
        "risk_score": _first_number(
            result.get("risk_score_pct"),
            result.get("risk_score"),
            _as_pct(result.get("risk_probability")),
            _as_pct(result.get("fire_probability")),
            _as_pct(result.get("heat_risk_probability")),
            _as_pct(result.get("leak_risk_probability")),
            _as_pct(result.get("water_quality_risk_probability")),
        ),
        "payload": _jsonable(payload),
        "result": _jsonable(result),
        "created_at": result.get("timestamp") or _utc_now_iso(),
    }

    client = get_client()
    if client is None:
        _enqueue_offline("prediction", f"PRED-{hazard}-{node_id or 'anon'}-{row['created_at']}", row, row["created_at"])
        return

    try:
        client.table(PREDICTIONS_TABLE).insert(row).execute()
    except Exception as exc:  # noqa: BLE001
        _log(f"prediction log failed for '{hazard}' ({exc})")
        _enqueue_offline("prediction", f"PRED-{hazard}-{node_id or 'anon'}-{row['created_at']}", row, row["created_at"])


# ──────────────────────────────────────────────────────────────────────
# Nodes (the sensor inventory supporting dynamic multi-node tracking)
# ──────────────────────────────────────────────────────────────────────

def fetch_nodes(hazard: str, fallback: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Read the sensor inventory from Supabase, falling back to the built-in list."""
    client = get_client()
    if client is None:
        return fallback
    try:
        res = (
            client.table(NODES_TABLE)
            .select("node_id, type, state, district, zone, lat, lon, battery, status, capabilities, firmware_version, is_simulated, gateway_id, last_ping")
            .eq("hazard", hazard)
            .execute()
        )
        rows = list(res.data or [])
        return rows if rows else fallback
    except Exception as exc:  # noqa: BLE001
        _log(f"node fetch failed for '{hazard}' ({exc}) - serving built-in list")
        return fallback


def seed_nodes(hazard: str, nodes: List[Dict[str, Any]]) -> None:
    """
    Upsert the built-in node inventory so the table is populated on first run.
    """
    client = get_client()
    if client is None or not nodes:
        return

    rows = []
    for n in nodes:
        node_id = n.get("node_id") or n.get("station_id")
        if not node_id:
            continue
        rows.append({
            "node_id": node_id,
            "hazard": hazard,
            "type": n.get("type") or "Type-A",
            "state": n.get("state") or "Tamil Nadu",
            "district": n.get("district"),
            "zone": (n.get("zone") or n.get("location")
                     or n.get("name") or n.get("city")),
            "lat": n.get("lat") or n.get("latitude"),
            "lon": n.get("lon") or n.get("longitude"),
            "battery": n.get("battery") or n.get("battery_pct"),
            "capabilities": n.get("capabilities") or [],
            "firmware_version": n.get("firmware_version") or "1.0.0",
            "is_simulated": n.get("is_simulated", False),
            "gateway_id": n.get("gateway_id", "GW-01"),
            "status": n.get("status") or "ONLINE",
            "last_ping": n.get("last_ping") or n.get("last_seen") or _utc_now_iso(),
        })

    if client is None or not nodes:
        for r in rows:
            _enqueue_offline("node", r["node_id"], r, r.get("last_ping"))
        return

    try:
        client.table(NODES_TABLE).upsert(rows, on_conflict="node_id").execute()
        _log(f"seeded {len(rows)} '{hazard}' nodes")
    except Exception as exc:  # noqa: BLE001
        _log(f"node seed failed for '{hazard}' ({exc})")
        for r in rows:
            _enqueue_offline("node", r["node_id"], r, r.get("last_ping"))


# ──────────────────────────────────────────────────────────────────────
# Notification Targets & Dispatches (Phase 6)
# ──────────────────────────────────────────────────────────────────────

def insert_notification_target(target: Dict[str, Any]) -> Dict[str, Any]:
    """Persists a notification target recipient to Supabase with in-memory fallback."""
    target_id = target.get("target_id")
    if target_id:
        _memory_targets[target_id] = target

    client = get_client()
    if client is None:
        return target

    try:
        client.table(NOTIFICATION_TARGETS_TABLE).upsert(target, on_conflict="target_id").execute()
    except Exception as exc:  # noqa: BLE001
        _log(f"target upsert failed ({exc}) - stored in memory")
    return target


def fetch_notification_targets() -> List[Dict[str, Any]]:
    """Retrieves all registered notification targets."""
    client = get_client()
    if client is None:
        return list(_memory_targets.values())

    try:
        res = client.table(NOTIFICATION_TARGETS_TABLE).select("*").execute()
        rows = list(res.data or [])
        return rows if rows else list(_memory_targets.values())
    except Exception as exc:  # noqa: BLE001
        _log(f"targets fetch failed ({exc}) - returning memory copy")
        return list(_memory_targets.values())


def delete_notification_target(target_id: str) -> bool:
    """Deletes a notification target."""
    if target_id in _memory_targets:
        del _memory_targets[target_id]

    client = get_client()
    if client is None:
        return True

    try:
        client.table(NOTIFICATION_TARGETS_TABLE).delete().eq("target_id", target_id).execute()
        return True
    except Exception as exc:  # noqa: BLE001
        _log(f"target delete failed ({exc})")
        return False


def insert_dispatches(dispatches: List[Dict[str, Any]]) -> None:
    """Records dispatch audit entries to Supabase with in-memory mirror."""
    if not dispatches:
        return

    _memory_dispatches.extend(dispatches)

    rows = []
    for d in dispatches:
        rows.append({
            "dispatch_id": d.get("dispatch_id"),
            "alert_id": d.get("alert_id"),
            "channel": d.get("channel"),
            "target": d.get("target"),
            "attempted_at": d.get("attempted_at") or _utc_now_iso(),
            "status": d.get("status"),
            "provider_message_id": d.get("provider_message_id"),
            "error": d.get("error"),
            "latency_ms": d.get("latency_ms", 0.0),
            "dry_run": d.get("dry_run", True),
            "response_metadata": _jsonable(d.get("response_metadata") or {}),
        })

    client = get_client()
    if client is None:
        for r in rows:
            _enqueue_offline("dispatch", r["dispatch_id"], r, r["attempted_at"])
        return

    try:
        client.table(NOTIFICATION_DISPATCHES_TABLE).insert(rows).execute()
    except Exception as exc:  # noqa: BLE001
        _log(f"dispatch audit insert failed ({exc}) - kept in memory only")
        for r in rows:
            _enqueue_offline("dispatch", r["dispatch_id"], r, r["attempted_at"])


def fetch_dispatches(alert_id: Optional[str] = None, limit: int = 200) -> List[Dict[str, Any]]:
    """Fetches dispatch audit logs, optionally filtered by alert_id."""
    client = get_client()
    if client is None:
        if alert_id:
            return [d for d in _memory_dispatches if d.get("alert_id") == alert_id][:limit]
        return _memory_dispatches[-limit:]

    try:
        q = client.table(NOTIFICATION_DISPATCHES_TABLE).select("*").order("attempted_at", desc=True).limit(limit)
        if alert_id:
            q = q.eq("alert_id", alert_id)
        res = q.execute()
        return list(res.data or [])
    except Exception as exc:  # noqa: BLE001
        _log(f"dispatches fetch failed ({exc}) - returning memory copy")
        if alert_id:
            return [d for d in _memory_dispatches if d.get("alert_id") == alert_id][:limit]
        return _memory_dispatches[-limit:]


# ──────────────────────────────────────────────────────────────────────
# Helpers
# ──────────────────────────────────────────────────────────────────────

def _as_pct(value: Any) -> Optional[float]:
    """Convert a 0..1 probability to a 0..100 score; pass through None."""
    if isinstance(value, (int, float)):
        return round(float(value) * 100.0, 2)
    return None


def _first_number(*values: Any) -> Optional[float]:
    for v in values:
        if isinstance(v, (int, float)):
            return float(v)
    return None


def _jsonable(obj: Any) -> Any:
    """Coerce numpy scalars / arrays and datetimes into JSON-safe values."""
    if isinstance(obj, dict):
        return {str(k): _jsonable(v) for k, v in obj.items()}
    if isinstance(obj, (list, tuple)):
        return [_jsonable(v) for v in obj]
    if isinstance(obj, (datetime.datetime, datetime.date)):
        return obj.isoformat()
    if hasattr(obj, "item") and callable(getattr(obj, "item", None)):
        try:
            return obj.item()  # numpy scalar -> python scalar
        except Exception:  # noqa: BLE001
            return str(obj)
    if isinstance(obj, (str, int, float, bool)) or obj is None:
        return obj
    return str(obj)
