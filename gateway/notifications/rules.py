"""
TerraEdge — Phase 6 Alert Policy Engine & Target Matching Rules.
Determines dispatch eligibility, severity filtering, geographic routing, and message templating.
"""

from __future__ import annotations
import datetime
from typing import List, Optional, Tuple
from .schemas import CanonicalAlert, NotificationTarget

SEVERITY_RANKS = {
    "NORMAL": 0,
    "WATCH": 1,
    "WARNING": 2,
    "CRITICAL": 3,
}


def is_target_eligible(target: NotificationTarget, alert: CanonicalAlert) -> bool:
    """
    Evaluates whether a notification target qualifies to receive an alert
    based on enabled state, geographic scope, hazard type, and minimum severity threshold.
    """
    if not target.enabled:
        return False

    # 1. Severity Check
    alert_sev_rank = SEVERITY_RANKS.get(alert.severity.upper(), 0)
    target_min_rank = SEVERITY_RANKS.get(target.min_severity.upper(), 2)  # Default WARNING (2)
    if alert_sev_rank < target_min_rank:
        return False

    # 2. Hazard Type Check
    target_hazards_lower = [h.strip().lower() for h in target.hazards]
    if "all" not in target_hazards_lower and alert.hazard.strip().lower() not in target_hazards_lower:
        return False

    # 3. State Scope Check
    if target.state and target.state.strip().lower() not in ("all", ""):
        if alert.state and target.state.strip().lower() != alert.state.strip().lower():
            return False

    # 4. District Scope Check
    if target.district and target.district.strip().lower() not in ("all", ""):
        if not alert.district:
            return False
        if target.district.strip().lower() != alert.district.strip().lower():
            return False

    return True


def filter_targets(targets: List[NotificationTarget], alert: CanonicalAlert) -> List[NotificationTarget]:
    """Filters target list down to only matching and eligible recipients."""
    return [t for t in targets if is_target_eligible(t, alert)]


def should_dispatch_alert(alert: CanonicalAlert) -> bool:
    """
    Authoritative backend check: only alerts with severity >= WARNING or
    verified alert candidates should trigger multi-channel authority dispatches.
    """
    if alert.severity.upper() in ("NORMAL",):
        return False
    if alert.severity.upper() in ("CRITICAL", "WARNING"):
        return True
    return bool(alert.alert_candidate and alert.risk_pct >= 50.0)


def build_alert_title(alert: CanonicalAlert) -> str:
    """Constructs standardized headline for email subject, webhook, and CAP."""
    loc_str = alert.district or alert.state or "Regional"
    prefix = "[SIMULATED] " if alert.is_simulated else ""
    return f"{prefix}[TERRAEDGE] {alert.hazard.upper()} — {alert.severity.upper()} — {loc_str.upper()}"


def build_alert_message(alert: CanonicalAlert) -> str:
    """
    Constructs standardized, concise authority-grade notification message body.
    Avoids raw sensor telemetry dumps while providing exact risk, confidence, and node scope.
    """
    sim_tag = " [SIMULATED TEST ALERT]" if alert.is_simulated else ""
    loc_str = alert.district or alert.state or "Regional Zone"
    node_str = f"Node {alert.node_id}" if alert.node_id else f"{len(alert.affected_nodes)} node(s) ({', '.join(alert.affected_nodes[:5])})"

    return (
        f"TERRAEDGE ALERT{sim_tag}\n\n"
        f"HAZARD: {alert.hazard.upper()} — {alert.severity.upper()}\n"
        f"Location: {loc_str}, {alert.state}\n"
        f"Risk Score: {alert.risk_pct:.1f}%\n"
        f"Confidence: {alert.confidence_pct:.1f}%\n"
        f"Scope: {node_str}\n"
        f"Time: {alert.created_at}\n\n"
        f"Action: Review TerraEdge central dashboard for live spatial telemetry & hotspot map."
    )
