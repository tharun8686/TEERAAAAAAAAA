"""
TerraEdge — Base Notification Channel Abstract Interface.
"""

from __future__ import annotations
from abc import ABC, abstractmethod
from typing import Optional
from ..schemas import CanonicalAlert, DispatchRecord, NotificationTarget


class BaseNotificationChannel(ABC):
    """Abstract interface implemented by SMS, Email, Webhook, and CAP channels."""

    @abstractmethod
    def send(self, alert: CanonicalAlert, target: Optional[NotificationTarget] = None) -> DispatchRecord:
        """Dispatches an alert to a target or generates an export artifact."""
        pass
