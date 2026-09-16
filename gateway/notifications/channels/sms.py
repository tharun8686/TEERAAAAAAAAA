"""
TerraEdge — SMS Notification Channel.
Supports Twilio REST API integration and simulated safe dry-run mode.
"""

from __future__ import annotations
import base64
import json
import time
import urllib.parse
import urllib.request
import uuid
from typing import Optional

from ..rules import build_alert_message
from ..schemas import (
    CanonicalAlert,
    ChannelType,
    DispatchRecord,
    DispatchStatus,
    NotificationTarget,
)
from .base import BaseNotificationChannel


class SmsChannel(BaseNotificationChannel):
    def __init__(
        self,
        mode: str = "dry_run",
        provider: str = "mock",
        twilio_sid: str = "",
        twilio_token: str = "",
        twilio_from: str = "",
        enabled: bool = True
    ):
        self.mode = mode.lower()
        self.provider = provider.lower()
        self.twilio_sid = twilio_sid
        self.twilio_token = twilio_token
        self.twilio_from = twilio_from
        self.enabled = enabled

    def send(self, alert: CanonicalAlert, target: Optional[NotificationTarget] = None) -> DispatchRecord:
        start_time = time.perf_counter()
        destination = target.destination if target else "DEFAULT_SMS_TARGET"
        dispatch_id = f"DSP-SMS-{uuid.uuid4().hex[:8].upper()}"

        if not self.enabled:
            return DispatchRecord(
                dispatch_id=dispatch_id,
                alert_id=alert.alert_id,
                channel=ChannelType.SMS,
                target=destination,
                status=DispatchStatus.DISABLED,
                error="SMS channel is disabled in gateway configuration",
                latency_ms=0.0,
                dry_run=True,
            )

        msg_body = build_alert_message(alert)

        # 1. Dry Run Mode or Unconfigured Credentials
        is_dry_run = (self.mode == "dry_run") or (self.provider == "mock") or not (self.twilio_sid and self.twilio_token and self.twilio_from)

        if is_dry_run:
            duration_ms = round((time.perf_counter() - start_time) * 1000.0, 2)
            mock_msg_id = f"DRYRUN-TWILIO-SM{uuid.uuid4().hex[:16].upper()}"
            return DispatchRecord(
                dispatch_id=dispatch_id,
                alert_id=alert.alert_id,
                channel=ChannelType.SMS,
                target=destination,
                status=DispatchStatus.DRY_RUN,
                provider_message_id=mock_msg_id,
                latency_ms=duration_ms,
                dry_run=True,
                response_metadata={
                    "provider": "twilio_mock",
                    "mode": "dry_run",
                    "preview_body": msg_body[:160],
                    "simulated_destination": destination
                }
            )

        # 2. Live Twilio API Dispatch
        try:
            url = f"https://api.twilio.com/2010-04-01/Accounts/{self.twilio_sid}/Messages.json"
            data = urllib.parse.urlencode({
                "To": destination,
                "From": self.twilio_from,
                "Body": msg_body,
            }).encode("utf-8")

            req = urllib.request.Request(url, data=data, method="POST")
            auth_str = f"{self.twilio_sid}:{self.twilio_token}"
            auth_b64 = base64.b64encode(auth_str.encode("ascii")).decode("ascii")
            req.add_header("Authorization", f"Basic {auth_b64}")
            req.add_header("Content-Type", "application/x-www-form-urlencoded")

            with urllib.request.urlopen(req, timeout=8.0) as response:
                res_body = response.read().decode("utf-8")
                res_json = json.loads(res_body)
                duration_ms = round((time.perf_counter() - start_time) * 1000.0, 2)
                return DispatchRecord(
                    dispatch_id=dispatch_id,
                    alert_id=alert.alert_id,
                    channel=ChannelType.SMS,
                    target=destination,
                    status=DispatchStatus.ACCEPTED,
                    provider_message_id=res_json.get("sid"),
                    latency_ms=duration_ms,
                    dry_run=False,
                    response_metadata={
                        "status": res_json.get("status"),
                        "date_created": res_json.get("date_created")
                    }
                )
        except Exception as exc:
            duration_ms = round((time.perf_counter() - start_time) * 1000.0, 2)
            return DispatchRecord(
                dispatch_id=dispatch_id,
                alert_id=alert.alert_id,
                channel=ChannelType.SMS,
                target=destination,
                status=DispatchStatus.FAILED,
                error=f"SMS dispatch failed: {str(exc)}",
                latency_ms=duration_ms,
                dry_run=False,
            )
