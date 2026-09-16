"""
TerraEdge — Outbound Webhook Notification Channel.
Delivers standardized JSON alert payloads to emergency response systems and dashboards.
"""

from __future__ import annotations
import json
import time
import urllib.error
import urllib.request
import uuid
from typing import Optional

from ..schemas import (
    CanonicalAlert,
    ChannelType,
    DispatchRecord,
    DispatchStatus,
    NotificationTarget,
)
from .base import BaseNotificationChannel


class WebhookChannel(BaseNotificationChannel):
    def __init__(
        self,
        mode: str = "dry_run",
        timeout_seconds: float = 5.0,
        max_retries: int = 2,
        enabled: bool = True,
    ):
        self.mode = mode.lower()
        self.timeout_seconds = timeout_seconds
        self.max_retries = max_retries
        self.enabled = enabled

    def send(self, alert: CanonicalAlert, target: Optional[NotificationTarget] = None) -> DispatchRecord:
        start_time = time.perf_counter()
        destination = target.destination if target else "http://localhost:8000/api/mock-webhook"
        dispatch_id = f"DSP-WHK-{uuid.uuid4().hex[:8].upper()}"

        if not self.enabled:
            return DispatchRecord(
                dispatch_id=dispatch_id,
                alert_id=alert.alert_id,
                channel=ChannelType.WEBHOOK,
                target=destination,
                status=DispatchStatus.DISABLED,
                error="Webhook channel is disabled in gateway configuration",
                latency_ms=0.0,
                dry_run=True,
            )

        payload = {
            "alert_id": alert.alert_id,
            "event_id": alert.event_id,
            "hazard": alert.hazard,
            "severity": alert.severity,
            "risk_pct": alert.risk_pct,
            "confidence_pct": alert.confidence_pct,
            "district": alert.district,
            "state": alert.state,
            "zone": alert.zone,
            "node_id": alert.node_id,
            "affected_nodes": alert.affected_nodes,
            "timestamp": alert.created_at,
            "source": alert.source,
            "is_simulated": alert.is_simulated,
            "lifecycle_state": alert.lifecycle_state.value if hasattr(alert.lifecycle_state, "value") else str(alert.lifecycle_state),
            "top_features": alert.top_features,
            "details": alert.details,
        }

        # 1. Dry Run Mode
        if self.mode == "dry_run" or destination.startswith("mock://") or "mock" in destination:
            duration_ms = round((time.perf_counter() - start_time) * 1000.0, 2)
            mock_msg_id = f"DRYRUN-WHK-{uuid.uuid4().hex[:12].upper()}"
            return DispatchRecord(
                dispatch_id=dispatch_id,
                alert_id=alert.alert_id,
                channel=ChannelType.WEBHOOK,
                target=destination,
                status=DispatchStatus.DRY_RUN,
                provider_message_id=mock_msg_id,
                latency_ms=duration_ms,
                dry_run=True,
                response_metadata={
                    "mode": "dry_run",
                    "destination": destination,
                    "payload_keys": list(payload.keys()),
                }
            )

        # 2. Live HTTP POST Delivery
        data = json.dumps(payload).encode("utf-8")
        req = urllib.request.Request(
            destination,
            data=data,
            headers={
                "Content-Type": "application/json",
                "User-Agent": "TerraEdge-Gateway/5.0",
                "X-TerraEdge-Event": alert.hazard,
                "X-TerraEdge-Severity": alert.severity,
            },
            method="POST"
        )

        last_error = None
        for attempt in range(self.max_retries + 1):
            try:
                with urllib.request.urlopen(req, timeout=self.timeout_seconds) as response:
                    status_code = response.status
                    duration_ms = round((time.perf_counter() - start_time) * 1000.0, 2)
                    if 200 <= status_code < 300:
                        return DispatchRecord(
                            dispatch_id=dispatch_id,
                            alert_id=alert.alert_id,
                            channel=ChannelType.WEBHOOK,
                            target=destination,
                            status=DispatchStatus.ACCEPTED,
                            provider_message_id=f"HTTP-{status_code}-{uuid.uuid4().hex[:6].upper()}",
                            latency_ms=duration_ms,
                            dry_run=False,
                            response_metadata={"http_status": status_code, "attempt": attempt + 1}
                        )
                    else:
                        last_error = f"HTTP {status_code}"
            except Exception as exc:
                last_error = str(exc)
                if attempt < self.max_retries:
                    time.sleep(0.5 * (attempt + 1))

        duration_ms = round((time.perf_counter() - start_time) * 1000.0, 2)
        return DispatchRecord(
            dispatch_id=dispatch_id,
            alert_id=alert.alert_id,
            channel=ChannelType.WEBHOOK,
            target=destination,
            status=DispatchStatus.FAILED,
            error=f"Webhook delivery failed after {self.max_retries + 1} attempts: {last_error}",
            latency_ms=duration_ms,
            dry_run=False,
        )
