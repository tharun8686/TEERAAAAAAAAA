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
_seq_counters: Dict[str, int] = {}


def _log(msg: str) -> None:
    print(f"[terra-supabase] {msg}", flush=True)


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
            _client_error = "SUPABASE_URL / SUPABASE_SERVICE_KEY not set"
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

    client = get_client()
    if client is None:
        return alert

    row = {
        "alert_id": alert.get("alert_id"),
        "hazard": hazard,
        "node_id": alert.get("node_id") or alert.get("station_id"),
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

    try:
        client.table(ALERTS_TABLE).insert(row).execute()
    except Exception as exc:  # noqa: BLE001 - a DB hiccup must not fail a prediction
        _log(f"alert insert failed for '{hazard}' ({exc}) - kept in memory only")

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
            .select("alert_id, severity, node_id, risk_score, details, created_at")
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
            .select("severity, risk_score, created_at")
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
    client = get_client()
    if client is None:
        return

    row = {
        "hazard": hazard,
        "node_id": node_id,
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

    try:
        client.table(PREDICTIONS_TABLE).insert(row).execute()
    except Exception as exc:  # noqa: BLE001
        _log(f"prediction log failed for '{hazard}' ({exc})")


# ──────────────────────────────────────────────────────────────────────
# Nodes (the hardcoded sensor inventories)
# ──────────────────────────────────────────────────────────────────────

def fetch_nodes(hazard: str, fallback: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Read the sensor inventory from Supabase, falling back to the built-in list."""
    client = get_client()
    if client is None:
        return fallback
    try:
        res = (
            client.table(NODES_TABLE)
            .select("node_id, type, zone, lat, lon, status, last_ping")
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

    The services describe their nodes slightly differently (some use `zone`,
    others `location`, some omit `last_ping`), so each entry is normalised down
    to the columns the `nodes` table actually has.
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
            "type": n.get("type"),
            "zone": (n.get("zone") or n.get("location")
                     or n.get("name") or n.get("city")),
            "lat": n.get("lat"),
            "lon": n.get("lon"),
            "status": n.get("status") or "ONLINE",
            "last_ping": n.get("last_ping") or _utc_now_iso(),
        })

    if not rows:
        return

    try:
        client.table(NODES_TABLE).upsert(rows, on_conflict="node_id").execute()
        _log(f"seeded {len(rows)} '{hazard}' nodes")
    except Exception as exc:  # noqa: BLE001
        _log(f"node seed failed for '{hazard}' ({exc})")


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
