"""
TerraEdge — Phase 6 Automated Multi-Channel Alert & Dispatch Schemas.
Defines canonical alert representations, notification targets, dispatch audit records,
and lifecycle state machines.
"""

from __future__ import annotations
import datetime
from enum import Enum
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


def _utc_now_iso() -> str:
    return datetime.datetime.now(datetime.timezone.utc).isoformat()


class AlertLifecycleState(str, Enum):
    DETECTED = "DETECTED"
    DISPATCH_PENDING = "DISPATCH_PENDING"
    DISPATCHED = "DISPATCHED"
    ACTIVE = "ACTIVE"
    UPDATED = "UPDATED"
    ACKNOWLEDGED = "ACKNOWLEDGED"
    RESOLVED = "RESOLVED"
    EXPIRED = "EXPIRED"


class DispatchStatus(str, Enum):
    ACCEPTED = "ACCEPTED"
    SENT = "SENT"
    FAILED = "FAILED"
    DRY_RUN = "DRY_RUN"
    DISABLED = "DISABLED"
    SKIPPED = "SKIPPED"


class ChannelType(str, Enum):
    SMS = "sms"
    EMAIL = "email"
    WEBHOOK = "webhook"
    CAP = "cap"


class CanonicalAlert(BaseModel):
    """
    Unified canonical alert object across node-level and district-level detections.
    Authoritative backend representation passed into the notification pipeline.
    """
    alert_id: str
    event_id: str = Field(..., description="Deduplication key, e.g. 'Flood:Chennai' or 'Wildfire:TE-001'")
    hazard: str
    severity: str = "WARNING"
    risk_pct: float = 0.0
    confidence_pct: float = 0.0

    node_id: Optional[str] = None
    affected_nodes: List[str] = Field(default_factory=list)

    state: str = "Tamil Nadu"
    district: Optional[str] = None
    zone: Optional[str] = None

    latitude: Optional[float] = None
    longitude: Optional[float] = None
    radius_km: Optional[float] = None

    title: str = ""
    message: str = ""

    created_at: str = Field(default_factory=_utc_now_iso)
    updated_at: str = Field(default_factory=_utc_now_iso)
    expires_at: Optional[str] = None

    source: str = "node_telemetry"  # 'node_telemetry' | 'district_aggregation' | 'manual_dispatch'
    is_simulated: bool = False
    alert_candidate: bool = True
    lifecycle_state: AlertLifecycleState = AlertLifecycleState.DETECTED

    top_features: List[Any] = Field(default_factory=list)
    details: Dict[str, Any] = Field(default_factory=dict)
    dispatches: List[Dict[str, Any]] = Field(default_factory=list)


class NotificationTarget(BaseModel):
    """Configuration for an authorized authority dispatch destination."""
    target_id: str
    target_type: ChannelType
    name: str
    destination: str  # E.164 phone, email, or webhook URL
    state: Optional[str] = "Tamil Nadu"
    district: Optional[str] = None  # None / "all" = state-wide
    hazards: List[str] = Field(default_factory=lambda: ["all"])
    min_severity: str = "WARNING"  # WATCH, WARNING, CRITICAL
    enabled: bool = True
    created_at: str = Field(default_factory=_utc_now_iso)


class DispatchRecord(BaseModel):
    """Audit log entry for an individual channel dispatch attempt."""
    dispatch_id: str
    alert_id: str
    channel: ChannelType
    target: str
    attempted_at: str = Field(default_factory=_utc_now_iso)
    status: DispatchStatus
    provider_message_id: Optional[str] = None
    error: Optional[str] = None
    latency_ms: float = 0.0
    dry_run: bool = True
    response_metadata: Dict[str, Any] = Field(default_factory=dict)


class TargetCreateRequest(BaseModel):
    target_type: ChannelType
    name: str
    destination: str
    state: Optional[str] = "Tamil Nadu"
    district: Optional[str] = None
    hazards: Optional[List[str]] = Field(default_factory=lambda: ["all"])
    min_severity: Optional[str] = "WARNING"
    enabled: Optional[bool] = True


class TargetUpdateRequest(BaseModel):
    name: Optional[str] = None
    destination: Optional[str] = None
    state: Optional[str] = None
    district: Optional[str] = None
    hazards: Optional[List[str]] = None
    min_severity: Optional[str] = None
    enabled: Optional[bool] = None


class ManualDispatchRequest(BaseModel):
    channels: Optional[List[ChannelType]] = None
    custom_message: Optional[str] = None
    force: bool = False


class AlertAcknowledgeRequest(BaseModel):
    operator_id: str
    notes: Optional[str] = None
