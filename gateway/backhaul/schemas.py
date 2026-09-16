"""
TerraEdge — Phase 7 Backhaul & Resilient Queue Schemas.
Defines data models for communication states, transports, durable queue items,
health inspection, and synchronization metrics.
"""

from __future__ import annotations
import datetime
from enum import Enum
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


def _utc_now_iso() -> str:
    return datetime.datetime.now(datetime.timezone.utc).isoformat()


class BackhaulState(str, Enum):
    ONLINE = "ONLINE"          # Cloud connectivity active and healthy
    DEGRADED = "DEGRADED"      # Primary down, running on secondary/tertiary backhaul
    OFFLINE = "OFFLINE"        # All backhauls down, local-only edge operation active
    SYNCING = "SYNCING"        # Reconnected, synchronizing buffered local records


class TransportType(str, Enum):
    ETHERNET_WIFI = "ethernet_wifi"
    CELLULAR = "cellular"
    SATELLITE = "satellite"
    LOCAL_ONLY = "local_only"


class QueueRecordType(str, Enum):
    NODE = "node"                  # Priority 1: Parent node dynamic registration
    TELEMETRY = "telemetry"        # Priority 2: Raw / derivative sensor telemetry
    PREDICTION = "prediction"      # Priority 3: 7-hazard ML inference results
    ALERT = "alert"                # Priority 4: Threshold breaches & canonical alerts
    DISPATCH = "dispatch"          # Priority 5: Notification channel audit records


class QueueStatus(str, Enum):
    PENDING = "PENDING"
    SYNCING = "SYNCING"
    SYNCED = "SYNCED"
    FAILED = "FAILED"


class QueueRecord(BaseModel):
    """Represents a single persistent item buffered in the SQLite store-and-forward queue."""
    queue_id: str
    record_type: QueueRecordType
    record_id: str = Field(..., description="Unique idempotency identifier (e.g. node_id, alert_id, dispatch_id)")
    payload: Dict[str, Any] = Field(default_factory=dict)
    observed_at: str = Field(default_factory=_utc_now_iso, description="Original physical sensor timestamp (immutable)")
    created_at: str = Field(default_factory=_utc_now_iso, description="Queue insertion timestamp")
    synced_at: Optional[str] = None
    retry_count: int = 0
    status: QueueStatus = QueueStatus.PENDING
    last_error: Optional[str] = None


class BackhaulHealthResponse(BaseModel):
    """Safe operational summary returned by GET /api/backhaul/health."""
    gateway_mode: str = "LOCAL_EDGE"
    backhaul_state: BackhaulState
    active_transport: Optional[TransportType] = None
    internet_available: bool = False
    cellular_available: bool = False
    satellite_available: bool = False
    queue_size: int = 0
    sync_state: str = "SYNCED"
    last_sync_time: Optional[str] = None
    last_failure_reason: Optional[str] = None
    timestamp: str = Field(default_factory=_utc_now_iso)


class QueueSummaryResponse(BaseModel):
    """Summary of local durable queue returned by GET /api/backhaul/queue."""
    queue_size: int
    pending_count: int
    synced_count: int
    failed_count: int
    oldest_record_time: Optional[str] = None
    record_types: Dict[str, int] = Field(default_factory=dict)
    db_path: str


class SyncResponse(BaseModel):
    """Response from manual or scheduled sync execution (POST /api/backhaul/sync)."""
    status: str
    synced_count: int
    failed_count: int
    remaining_queue_size: int
    duration_ms: float
    transport_used: Optional[str] = None
    timestamp: str = Field(default_factory=_utc_now_iso)
