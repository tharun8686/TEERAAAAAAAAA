"""
TerraEdge — Email Notification Channel.
Supports SMTP standard email dispatch and safe dry-run simulation mode.
"""

from __future__ import annotations
import email.mime.text
import smtplib
import time
import uuid
from typing import Optional

from ..rules import build_alert_message, build_alert_title
from ..schemas import (
    CanonicalAlert,
    ChannelType,
    DispatchRecord,
    DispatchStatus,
    NotificationTarget,
)
from .base import BaseNotificationChannel


class EmailChannel(BaseNotificationChannel):
    def __init__(
        self,
        mode: str = "dry_run",
        smtp_host: str = "smtp.gmail.com",
        smtp_port: int = 587,
        smtp_username: str = "",
        smtp_password: str = "",
        smtp_from: str = "alerts@terraedge.io",
        smtp_use_tls: bool = True,
        enabled: bool = True,
    ):
        self.mode = mode.lower()
        self.smtp_host = smtp_host
        self.smtp_port = smtp_port
        self.smtp_username = smtp_username
        self.smtp_password = smtp_password
        self.smtp_from = smtp_from
        self.smtp_use_tls = smtp_use_tls
        self.enabled = enabled

    def send(self, alert: CanonicalAlert, target: Optional[NotificationTarget] = None) -> DispatchRecord:
        start_time = time.perf_counter()
        destination = target.destination if target else "DEFAULT_EMAIL_TARGET"
        dispatch_id = f"DSP-EML-{uuid.uuid4().hex[:8].upper()}"

        if not self.enabled:
            return DispatchRecord(
                dispatch_id=dispatch_id,
                alert_id=alert.alert_id,
                channel=ChannelType.EMAIL,
                target=destination,
                status=DispatchStatus.DISABLED,
                error="Email channel is disabled in gateway configuration",
                latency_ms=0.0,
                dry_run=True,
            )

        subject = build_alert_title(alert)
        body = build_alert_message(alert)

        # 1. Dry Run Mode or Unconfigured Credentials
        is_dry_run = (self.mode == "dry_run") or not (self.smtp_username and self.smtp_password)

        if is_dry_run:
            duration_ms = round((time.perf_counter() - start_time) * 1000.0, 2)
            mock_msg_id = f"DRYRUN-SMTP-MSG-{uuid.uuid4().hex[:12].upper()}"
            return DispatchRecord(
                dispatch_id=dispatch_id,
                alert_id=alert.alert_id,
                channel=ChannelType.EMAIL,
                target=destination,
                status=DispatchStatus.DRY_RUN,
                provider_message_id=mock_msg_id,
                latency_ms=duration_ms,
                dry_run=True,
                response_metadata={
                    "provider": "smtp_mock",
                    "mode": "dry_run",
                    "subject": subject,
                    "simulated_destination": destination
                }
            )

        # 2. Live SMTP Dispatch
        try:
            msg = email.mime.text.MIMEText(body, "plain", "utf-8")
            msg["Subject"] = subject
            msg["From"] = self.smtp_from
            msg["To"] = destination

            with smtplib.SMTP(self.smtp_host, self.smtp_port, timeout=8.0) as server:
                if self.smtp_use_tls:
                    server.starttls()
                if self.smtp_username and self.smtp_password:
                    server.login(self.smtp_username, self.smtp_password)
                server.sendmail(self.smtp_from, [destination], msg.as_string())

            duration_ms = round((time.perf_counter() - start_time) * 1000.0, 2)
            return DispatchRecord(
                dispatch_id=dispatch_id,
                alert_id=alert.alert_id,
                channel=ChannelType.EMAIL,
                target=destination,
                status=DispatchStatus.ACCEPTED,
                provider_message_id=f"SMTP-{uuid.uuid4().hex[:10].upper()}",
                latency_ms=duration_ms,
                dry_run=False,
                response_metadata={
                    "smtp_host": self.smtp_host,
                    "from": self.smtp_from,
                }
            )
        except Exception as exc:
            duration_ms = round((time.perf_counter() - start_time) * 1000.0, 2)
            return DispatchRecord(
                dispatch_id=dispatch_id,
                alert_id=alert.alert_id,
                channel=ChannelType.EMAIL,
                target=destination,
                status=DispatchStatus.FAILED,
                error=f"SMTP dispatch failed: {str(exc)}",
                latency_ms=duration_ms,
                dry_run=False,
            )
