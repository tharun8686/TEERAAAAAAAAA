"""
TerraEdge — Phase 6 Master Alert Dispatcher & Notification Orchestrator.
Coordinates canonical alert normalization, policy rules, deduplication,
multi-channel delivery, failure isolation, and audit logging.
"""

from __future__ import annotations
import datetime
import threading
import time
import uuid
from typing import Any, Dict, List, Optional, Tuple, Union

from ..config import (
    ALERT_AUTO_RESOLVE_WINDOW_SECONDS,
    ALERT_DEDUP_WINDOW_SECONDS,
    CAP_ENABLED,
    CAP_SCOPE,
    CAP_SENDER,
    EMAIL_ENABLED,
    NOTIFICATION_MODE,
    SMS_ENABLED,
    SMS_PROVIDER,
    SMTP_FROM,
    SMTP_HOST,
    SMTP_PASSWORD,
    SMTP_PORT,
    SMTP_USE_TLS,
    SMTP_USERNAME,
    TWILIO_ACCOUNT_SID,
    TWILIO_AUTH_TOKEN,
    TWILIO_FROM_NUMBER,
    WEBHOOK_ENABLED,
    WEBHOOK_MAX_RETRIES,
    WEBHOOK_TIMEOUT_SECONDS,
)
from .channels.cap import CapChannel, generate_cap_xml
from .channels.email import EmailChannel
from .channels.sms import SmsChannel
from .channels.webhook import WebhookChannel
from .deduplication import AlertDeduplicator
from .rules import (
    build_alert_message,
    build_alert_title,
    filter_targets,
    should_dispatch_alert,
)
from .schemas import (
    AlertLifecycleState,
    CanonicalAlert,
    ChannelType,
    DispatchRecord,
    DispatchStatus,
    NotificationTarget,
    TargetCreateRequest,
    TargetUpdateRequest,
)


def _utc_now_iso() -> str:
    return datetime.datetime.now(datetime.timezone.utc).isoformat()


class AlertDispatcher:
    """
    Central authority dispatch orchestrator for the Type B Edge Gateway.
    Guarantees channel failure isolation and prevents notification storms.
    """

    def __init__(self):
        self._lock = threading.Lock()
        self.deduplicator = AlertDeduplicator(
            dedup_window_seconds=ALERT_DEDUP_WINDOW_SECONDS,
            auto_resolve_seconds=ALERT_AUTO_RESOLVE_WINDOW_SECONDS,
        )

        # Initialize Channel Handlers
        self.sms_channel = SmsChannel(
            mode=NOTIFICATION_MODE,
            provider=SMS_PROVIDER,
            twilio_sid=TWILIO_ACCOUNT_SID,
            twilio_token=TWILIO_AUTH_TOKEN,
            twilio_from=TWILIO_FROM_NUMBER,
            enabled=SMS_ENABLED,
        )

        self.email_channel = EmailChannel(
            mode=NOTIFICATION_MODE,
            smtp_host=SMTP_HOST,
            smtp_port=SMTP_PORT,
            smtp_username=SMTP_USERNAME,
            smtp_password=SMTP_PASSWORD,
            smtp_from=SMTP_FROM,
            smtp_use_tls=SMTP_USE_TLS,
            enabled=EMAIL_ENABLED,
        )

        self.webhook_channel = WebhookChannel(
            mode=NOTIFICATION_MODE,
            timeout_seconds=WEBHOOK_TIMEOUT_SECONDS,
            max_retries=WEBHOOK_MAX_RETRIES,
            enabled=WEBHOOK_ENABLED,
        )

        self.cap_channel = CapChannel(
            sender=CAP_SENDER,
            scope=CAP_SCOPE,
            enabled=CAP_ENABLED,
        )

        # In-memory storage caches
        self._alerts_cache: Dict[str, CanonicalAlert] = {}
        self._dispatches_cache: List[DispatchRecord] = []
        self._targets: Dict[str, NotificationTarget] = {}

        self._seed_default_targets()

    def _seed_default_targets(self) -> None:
        """Seeds default authority recipients if target registry is empty."""
        defaults = [
            NotificationTarget(
                target_id="TGT-SMS-DISASTER-OPS",
                target_type=ChannelType.SMS,
                name="State Disaster Response Ops SMS",
                destination="+919876543210",
                state="Tamil Nadu",
                district=None,  # All districts
                hazards=["all"],
                min_severity="WARNING",
                enabled=True,
            ),
            NotificationTarget(
                target_id="TGT-EML-SEOC",
                target_type=ChannelType.EMAIL,
                name="State Emergency Operations Center (SEOC)",
                destination="seoc-alerts@tnsdma.gov.in",
                state="Tamil Nadu",
                district=None,
                hazards=["all"],
                min_severity="WARNING",
                enabled=True,
            ),
            NotificationTarget(
                target_id="TGT-WHK-GIS",
                target_type=ChannelType.WEBHOOK,
                name="Central Command GIS Webhook",
                destination="mock://emergency-dispatch.tn.gov.in/v1/alerts",
                state="Tamil Nadu",
                district=None,
                hazards=["all"],
                min_severity="WARNING",
                enabled=True,
            ),
        ]
        for t in defaults:
            self._targets[t.target_id] = t

    # ========================================================================
    # 1. Alert Normalization
    # ========================================================================

    def normalize_alert(
        self,
        alert_data: Union[Dict[str, Any], CanonicalAlert],
        source: str = "node_telemetry",
        state_name: str = "Tamil Nadu",
        district_name: Optional[str] = None,
        is_simulated: bool = False,
    ) -> CanonicalAlert:
        """Converts heterogeneous raw alert dicts into a canonical alert object."""
        if isinstance(alert_data, CanonicalAlert):
            return alert_data

        hazard = alert_data.get("hazard") or alert_data.get("hazard_type") or "Unknown"
        node_id = alert_data.get("node_id") or alert_data.get("station_id")
        district = alert_data.get("district") or district_name
        state = alert_data.get("state") or state_name
        severity = (alert_data.get("severity") or "WARNING").upper()

        risk_pct = float(
            alert_data.get("risk_score_pct")
            or alert_data.get("risk_pct")
            or alert_data.get("risk_score")
            or 0.0
        )
        conf_pct = float(
            alert_data.get("confidence_pct")
            or alert_data.get("confidence")
            or 85.0
        )

        alert_id = alert_data.get("alert_id") or f"ALT-{hazard[:4].upper()}-{uuid.uuid4().hex[:6].upper()}"
        event_id = f"{hazard.lower()}:{(district or node_id or 'global').lower()}"

        top_feats = alert_data.get("top_features") or []
        details = alert_data.get("details") or {}
        aff_nodes = alert_data.get("affected_nodes") or ([node_id] if node_id else [])

        lat = alert_data.get("latitude") or alert_data.get("lat")
        lon = alert_data.get("longitude") or alert_data.get("lon")

        alert = CanonicalAlert(
            alert_id=alert_id,
            event_id=event_id,
            hazard=hazard,
            severity=severity,
            risk_pct=round(risk_pct, 1),
            confidence_pct=round(conf_pct, 1),
            node_id=node_id,
            affected_nodes=aff_nodes,
            state=state,
            district=district,
            zone=alert_data.get("zone"),
            latitude=lat,
            longitude=lon,
            radius_km=alert_data.get("radius_km"),
            created_at=alert_data.get("timestamp") or _utc_now_iso(),
            updated_at=_utc_now_iso(),
            source=source,
            is_simulated=is_simulated or alert_data.get("is_simulated", False),
            alert_candidate=alert_data.get("alert_candidate", True),
            lifecycle_state=AlertLifecycleState.DETECTED,
            top_features=top_feats,
            details=details,
            dispatches=[],
        )

        alert.title = build_alert_title(alert)
        alert.message = build_alert_message(alert)
        return alert

    # ========================================================================
    # 2. Core Multi-Channel Dispatch Execution
    # ========================================================================

    def dispatch(
        self,
        alert_in: Union[CanonicalAlert, Dict[str, Any]],
        source: str = "node_telemetry",
        force: bool = False,
        target_channels: Optional[List[ChannelType]] = None,
    ) -> Tuple[CanonicalAlert, List[DispatchRecord]]:
        """
        Main entry point for authority notification dispatch.
        Performs policy check, deduplication, channel fan-out with failure isolation,
        and persistence.
        """
        alert = self.normalize_alert(alert_in, source=source)

        # 1. Policy check: should this alert be dispatched?
        if not force and not should_dispatch_alert(alert):
            alert.lifecycle_state = AlertLifecycleState.DETECTED
            with self._lock:
                self._alerts_cache[alert.alert_id] = alert
            return alert, []

        # 2. Deduplication check
        with self._lock:
            action, reason = self.deduplicator.evaluate_alert(alert, force=force)

        if action == "SUPPRESS_DUPLICATE" and not force:
            alert.lifecycle_state = AlertLifecycleState.ACTIVE
            with self._lock:
                self._alerts_cache[alert.alert_id] = alert
            return alert, []

        if action == "RESOLVED":
            alert.lifecycle_state = AlertLifecycleState.RESOLVED
            with self._lock:
                self._alerts_cache[alert.alert_id] = alert
            return alert, []

        # Update lifecycle state
        alert.lifecycle_state = (
            AlertLifecycleState.UPDATED if action == "DISPATCH_UPDATE"
            else AlertLifecycleState.DISPATCHED
        )
        alert.updated_at = _utc_now_iso()

        # 3. Target filtering
        eligible_targets = filter_targets(list(self._targets.values()), alert)
        dispatch_records: List[DispatchRecord] = []

        # 4. Multi-channel dispatch with failure isolation
        # Target channels restriction if specified
        allowed_types = set(target_channels) if target_channels else None

        # Dispatch to matching SMS / Email / Webhook targets
        for tgt in eligible_targets:
            if allowed_types and tgt.target_type not in allowed_types:
                continue

            try:
                if tgt.target_type == ChannelType.SMS:
                    rec = self.sms_channel.send(alert, tgt)
                elif tgt.target_type == ChannelType.EMAIL:
                    rec = self.email_channel.send(alert, tgt)
                elif tgt.target_type == ChannelType.WEBHOOK:
                    rec = self.webhook_channel.send(alert, tgt)
                else:
                    continue
                dispatch_records.append(rec)
            except Exception as exc:  # Safety isolation — one target error never halts others
                dispatch_records.append(
                    DispatchRecord(
                        dispatch_id=f"DSP-ERR-{uuid.uuid4().hex[:8].upper()}",
                        alert_id=alert.alert_id,
                        channel=tgt.target_type,
                        target=tgt.destination,
                        status=DispatchStatus.FAILED,
                        error=f"Unhandled target exception: {str(exc)}",
                        dry_run=False,
                    )
                )

        # Always generate CAP record for archival / feed if not restricted
        if not allowed_types or ChannelType.CAP in allowed_types:
            try:
                cap_rec = self.cap_channel.send(alert)
                dispatch_records.append(cap_rec)
            except Exception as exc:
                dispatch_records.append(
                    DispatchRecord(
                        dispatch_id=f"DSP-CAP-ERR-{uuid.uuid4().hex[:8].upper()}",
                        alert_id=alert.alert_id,
                        channel=ChannelType.CAP,
                        target="CAP_FEED_ARCHIVE",
                        status=DispatchStatus.FAILED,
                        error=f"Unhandled CAP generation exception: {str(exc)}",
                        dry_run=False,
                    )
                )

        # 5. Record outcome & update state
        alert.dispatches = [r.model_dump() for r in dispatch_records]

        with self._lock:
            self._alerts_cache[alert.alert_id] = alert
            self._dispatches_cache.extend(dispatch_records)
            self.deduplicator.record_dispatch_success(alert)

        # 6. Database persistence fallback & integration
        try:
            from common import terra_supabase as db
            if db is not None:
                # Save dispatches to DB if helper exists
                if hasattr(db, "insert_dispatches"):
                    db.insert_dispatches([r.model_dump() for r in dispatch_records])
        except Exception:
            pass

        return alert, dispatch_records

    # ========================================================================
    # 3. Notification Target Management APIs
    # ========================================================================

    def get_targets(
        self,
        target_type: Optional[ChannelType] = None,
        district: Optional[str] = None,
        enabled: Optional[bool] = None,
    ) -> List[NotificationTarget]:
        with self._lock:
            targets = list(self._targets.values())
        if target_type:
            targets = [t for t in targets if t.target_type == target_type]
        if district:
            targets = [t for t in targets if not t.district or t.district.lower() == district.lower()]
        if enabled is not None:
            targets = [t for t in targets if t.enabled == enabled]
        return targets

    def add_target(self, req: TargetCreateRequest) -> NotificationTarget:
        target_id = f"TGT-{req.target_type.value[:3].upper()}-{uuid.uuid4().hex[:6].upper()}"
        target = NotificationTarget(
            target_id=target_id,
            target_type=req.target_type,
            name=req.name,
            destination=req.destination,
            state=req.state or "Tamil Nadu",
            district=req.district,
            hazards=req.hazards or ["all"],
            min_severity=req.min_severity or "WARNING",
            enabled=req.enabled if req.enabled is not None else True,
            created_at=_utc_now_iso(),
        )
        with self._lock:
            self._targets[target.target_id] = target
        return target

    def update_target(self, target_id: str, req: TargetUpdateRequest) -> Optional[NotificationTarget]:
        with self._lock:
            if target_id not in self._targets:
                return None
            target = self._targets[target_id]
            if req.name is not None:
                target.name = req.name
            if req.destination is not None:
                target.destination = req.destination
            if req.state is not None:
                target.state = req.state
            if req.district is not None:
                target.district = req.district
            if req.hazards is not None:
                target.hazards = req.hazards
            if req.min_severity is not None:
                target.min_severity = req.min_severity
            if req.enabled is not None:
                target.enabled = req.enabled
            return target

    def delete_target(self, target_id: str) -> bool:
        with self._lock:
            if target_id in self._targets:
                del self._targets[target_id]
                return True
            return False

    # ========================================================================
    # 4. Alert Query & Lifecycle APIs
    # ========================================================================

    def get_alert(self, alert_id: str) -> Optional[CanonicalAlert]:
        with self._lock:
            return self._alerts_cache.get(alert_id)

    def get_all_alerts(
        self,
        hazard: Optional[str] = None,
        severity: Optional[str] = None,
        district: Optional[str] = None,
        limit: int = 50,
    ) -> List[CanonicalAlert]:
        with self._lock:
            alerts = list(self._alerts_cache.values())
        if hazard:
            alerts = [a for a in alerts if a.hazard.lower() == hazard.lower()]
        if severity:
            alerts = [a for a in alerts if a.severity.lower() == severity.lower()]
        if district:
            alerts = [a for a in alerts if a.district and a.district.lower() == district.lower()]
        alerts.sort(key=lambda a: a.created_at, reverse=True)
        return alerts[:limit]

    def get_dispatches_for_alert(self, alert_id: str) -> List[DispatchRecord]:
        with self._lock:
            return [d for d in self._dispatches_cache if d.alert_id == alert_id]

    def acknowledge_alert(self, alert_id: str, operator_id: str, notes: Optional[str] = None) -> Optional[CanonicalAlert]:
        with self._lock:
            alert = self._alerts_cache.get(alert_id)
            if not alert:
                return None
            alert.lifecycle_state = AlertLifecycleState.ACKNOWLEDGED
            alert.updated_at = _utc_now_iso()
            alert.details["acknowledged_by"] = operator_id
            alert.details["acknowledgement_notes"] = notes
            alert.details["acknowledged_at"] = _utc_now_iso()
            return alert

    def get_cap_xml_for_alert(self, alert_id: str) -> Optional[str]:
        alert = self.get_alert(alert_id)
        if not alert:
            return None
        # Check if CAP was already generated in dispatches
        for d in alert.dispatches:
            if d.get("channel") == "cap" and d.get("response_metadata", {}).get("cap_xml"):
                return d["response_metadata"]["cap_xml"]
        return generate_cap_xml(alert, sender=CAP_SENDER, scope=CAP_SCOPE)


# Global alert dispatcher singleton
alert_dispatcher = AlertDispatcher()
