"""
TerraEdge — Base Backhaul Adapter Interface.
"""

from __future__ import annotations
from abc import ABC, abstractmethod
from typing import Any, Dict, Tuple
from ..schemas import TransportType


class BaseBackhaulAdapter(ABC):
    """Abstract interface implemented by Internet (Wi-Fi/Ethernet), Cellular, and Satellite adapters."""

    @property
    @abstractmethod
    def transport_type(self) -> TransportType:
        """Returns the hardware/network transport classification."""
        pass

    @abstractmethod
    def is_available(self) -> bool:
        """Returns True if the transport is currently connected and capable of sending data."""
        pass

    @abstractmethod
    def check_health(self) -> Tuple[bool, str, Dict[str, Any]]:
        """
        Performs active connectivity check.
        Returns:
            (is_healthy, status_code, metadata_dict)
            status_code in ('AVAILABLE', 'NETWORK_TIMEOUT', 'AUTH_FAILURE', 'SERVER_ERROR', 'MODEM_OFFLINE', 'MOCK_ACTIVE')
        """
        pass

    @abstractmethod
    def send(self, payload: Dict[str, Any], record_type: str) -> Tuple[bool, str]:
        """
        Transmits a payload through this backhaul channel.
        Returns:
            (success, message_or_error)
        """
        pass
