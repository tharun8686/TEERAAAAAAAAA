"""
TerraEdge — Phase 6 Notifications & Authority Dispatch Package.
"""

from .dispatcher import AlertDispatcher, alert_dispatcher
from .schemas import (
    AlertAcknowledgeRequest,
    AlertLifecycleState,
    CanonicalAlert,
    ChannelType,
    DispatchRecord,
    DispatchStatus,
    ManualDispatchRequest,
    NotificationTarget,
    TargetCreateRequest,
    TargetUpdateRequest,
)

__all__ = [
    "AlertDispatcher",
    "alert_dispatcher",
    "CanonicalAlert",
    "NotificationTarget",
    "DispatchRecord",
    "AlertLifecycleState",
    "DispatchStatus",
    "ChannelType",
    "TargetCreateRequest",
    "TargetUpdateRequest",
    "ManualDispatchRequest",
    "AlertAcknowledgeRequest",
]
