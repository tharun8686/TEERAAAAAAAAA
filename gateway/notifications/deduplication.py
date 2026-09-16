"""
TerraEdge — Phase 6 Alert Deduplication & Lifecycle State Machine.
Prevents notification storms on high-frequency polling cycles while ensuring
meaningful risk escalations and event resolutions trigger immediate dispatches.
"""

from __future__ import annotations
import datetime
import time
from typing import Dict, Optional, Tuple
from .schemas import AlertLifecycleState, CanonicalAlert

SEVERITY_RANKS = {
    "NORMAL": 0,
    "WATCH": 1,
    "WARNING": 2,
    "CRITICAL": 3,
}


class ActiveEventState:
    def __init__(self, alert: CanonicalAlert):
        self.event_id: str = alert.event_id
        self.alert_id: str = alert.alert_id
        self.hazard: str = alert.hazard
        self.district: Optional[str] = alert.district
        self.node_id: Optional[str] = alert.node_id
        self.last_severity: str = alert.severity
        self.last_risk_pct: float = alert.risk_pct
        self.last_dispatched_at: float = time.time()
        self.first_detected_at: float = time.time()
        self.lifecycle_state: AlertLifecycleState = AlertLifecycleState.ACTIVE
        self.dispatch_count: int = 1


class AlertDeduplicator:
    """
    Tracks active environmental hazard events across the edge gateway and suppresses
    redundant authority dispatches unless a material escalation occurs.
    """

    def __init__(self, dedup_window_seconds: int = 300, auto_resolve_seconds: int = 600):
        self.dedup_window_seconds = dedup_window_seconds
        self.auto_resolve_seconds = auto_resolve_seconds
        self._active_events: Dict[str, ActiveEventState] = {}

    def get_event_key(self, alert: CanonicalAlert) -> str:
        """Derives canonical grouping key from hazard and location/node."""
        loc = (alert.district or alert.node_id or "global").strip().lower()
        return f"{alert.hazard.strip().lower()}:{loc}"

    def evaluate_alert(self, alert: CanonicalAlert, force: bool = False) -> Tuple[str, Optional[str]]:
        """
        Evaluates whether the alert warrants a new dispatch.
        Returns:
            (action, reason)
            where action in ('DISPATCH_INITIAL', 'DISPATCH_UPDATE', 'SUPPRESS_DUPLICATE', 'RESOLVED')
        """
        if force:
            return "DISPATCH_INITIAL", "Manual force dispatch requested"

        event_key = self.get_event_key(alert)
        now = time.time()

        # Handle explicit resolution
        if alert.severity.upper() == "NORMAL":
            if event_key in self._active_events:
                ev = self._active_events[event_key]
                ev.lifecycle_state = AlertLifecycleState.RESOLVED
                del self._active_events[event_key]
                return "RESOLVED", f"Hazard '{alert.hazard}' in '{alert.district}' subsided to NORMAL"
            return "SUPPRESS_DUPLICATE", "Severity is NORMAL and no active event was found"

        # Check if event is brand new
        if event_key not in self._active_events:
            self._active_events[event_key] = ActiveEventState(alert)
            return "DISPATCH_INITIAL", f"New environmental event detected for {alert.hazard} in {alert.district or alert.node_id}"

        # Existing active event found — evaluate escalation or time decay
        existing = self._active_events[event_key]
        time_since_dispatch = now - existing.last_dispatched_at

        old_rank = SEVERITY_RANKS.get(existing.last_severity.upper(), 0)
        new_rank = SEVERITY_RANKS.get(alert.severity.upper(), 0)
        risk_diff = alert.risk_pct - existing.last_risk_pct

        # 1. Severity Escalation (e.g. WARNING -> CRITICAL)
        if new_rank > old_rank:
            existing.last_severity = alert.severity
            existing.last_risk_pct = alert.risk_pct
            existing.last_dispatched_at = now
            existing.dispatch_count += 1
            existing.lifecycle_state = AlertLifecycleState.UPDATED
            return "DISPATCH_UPDATE", f"Severity escalated from {existing.last_severity} to {alert.severity}"

        # 2. Material Risk Escalation (>= 15% increase)
        if risk_diff >= 15.0:
            existing.last_risk_pct = alert.risk_pct
            existing.last_dispatched_at = now
            existing.dispatch_count += 1
            existing.lifecycle_state = AlertLifecycleState.UPDATED
            return "DISPATCH_UPDATE", f"Risk score jumped by +{risk_diff:.1f}% (now {alert.risk_pct:.1f}%)"

        # 3. Deduplication Window Check
        if time_since_dispatch < self.dedup_window_seconds:
            # Suppress notification storm
            return "SUPPRESS_DUPLICATE", f"Duplicate event suppressed (last sent {int(time_since_dispatch)}s ago, window is {self.dedup_window_seconds}s)"

        # 4. Periodic Refresh after window expiry
        existing.last_severity = alert.severity
        existing.last_risk_pct = alert.risk_pct
        existing.last_dispatched_at = now
        existing.dispatch_count += 1
        return "DISPATCH_UPDATE", f"Periodic alert status refresh after {int(time_since_dispatch)}s"

    def record_dispatch_success(self, alert: CanonicalAlert) -> None:
        """Updates internal state following successful dispatch."""
        event_key = self.get_event_key(alert)
        if event_key in self._active_events:
            self._active_events[event_key].last_dispatched_at = time.time()
            self._active_events[event_key].lifecycle_state = AlertLifecycleState.DISPATCHED
        else:
            self._active_events[event_key] = ActiveEventState(alert)

    def mark_resolved(self, event_key: str) -> bool:
        """Explicitly resolves and closes an active event."""
        if event_key in self._active_events:
            self._active_events[event_key].lifecycle_state = AlertLifecycleState.RESOLVED
            del self._active_events[event_key]
            return True
        return False

    def get_active_events(self) -> Dict[str, ActiveEventState]:
        """Returns dictionary of all currently active environmental alert states."""
        return dict(self._active_events)
