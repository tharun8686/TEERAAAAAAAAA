"""
TerraEdge — Satellite Backhaul Adapter (Iridium SBD / Low-Earth Orbit).
Provides tertiary failover communication path for remote deep-forest & mountainous deployments.
Includes modular mock driver when physical satellite transceiver is not attached.
"""

from __future__ import annotations
import time
from typing import Any, Dict, Optional, Tuple

from ...config import SATELLITE_ENABLED, SATELLITE_MOCK_MODE, SATELLITE_PORT
from ..schemas import TransportType
from .base import BaseBackhaulAdapter


class SatelliteBackhaulAdapter(BaseBackhaulAdapter):
    def __init__(
        self,
        port: str = SATELLITE_PORT,
        mock_mode: bool = SATELLITE_MOCK_MODE,
        enabled: bool = SATELLITE_ENABLED,
    ):
        self.port = port
        self.mock_mode = mock_mode
        self.enabled = enabled
        self._simulated_state: Optional[bool] = None

    @property
    def transport_type(self) -> TransportType:
        return TransportType.SATELLITE

    def set_simulated_state(self, online: Optional[bool]) -> None:
        self._simulated_state = online

    def is_available(self) -> bool:
        if not self.enabled:
            return False
        if self._simulated_state is not None:
            return self._simulated_state
        if self.mock_mode:
            return True  # Mock adapter available for failover testing
        return False

    def check_health(self) -> Tuple[bool, str, Dict[str, Any]]:
        start_time = time.perf_counter()

        if not self.enabled:
            return False, "DISABLED", {"transport": "satellite", "enabled": False}

        if self._simulated_state is False:
            return False, "MODEM_OFFLINE", {
                "transport": "satellite",
                "status": "SIMULATED_SATELLITE_OFFLINE",
                "port": self.port,
            }

        if self.mock_mode:
            duration_ms = round((time.perf_counter() - start_time) * 1000.0, 2)
            return True, "MOCK_ACTIVE", {
                "transport": "satellite",
                "mock": True,
                "note": "REAL HARDWARE NOT TESTED — MOCK SATELLITE SBD TRANSCEIVER",
                "simulated_constellation": "Iridium LEO",
                "latency_ms": duration_ms,
            }

        return False, "MODEM_OFFLINE", {
            "transport": "satellite",
            "port": self.port,
            "error": "No physical satellite transceiver detected on serial port"
        }

    def send(self, payload: Dict[str, Any], record_type: str) -> Tuple[bool, str]:
        if not self.is_available():
            return False, "Satellite backhaul unavailable"

        if self.mock_mode:
            return True, "Transmitted via Mock Satellite SBD packet (REAL HARDWARE NOT TESTED)"

        return False, "Real satellite transmission failed: Hardware not connected"
