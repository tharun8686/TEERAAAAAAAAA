"""
TerraEdge — Cellular Backhaul Adapter (4G/LTE / GSM).
Provides secondary failover communication path when primary Wi-Fi/Ethernet fails.
Includes modular mock driver when physical cellular modem is not attached.
"""

from __future__ import annotations
import time
from typing import Any, Dict, Optional, Tuple

from ...config import CELLULAR_APN, CELLULAR_ENABLED, CELLULAR_MOCK_MODE, CELLULAR_PORT
from ..schemas import TransportType
from .base import BaseBackhaulAdapter


class CellularBackhaulAdapter(BaseBackhaulAdapter):
    def __init__(
        self,
        port: str = CELLULAR_PORT,
        apn: str = CELLULAR_APN,
        mock_mode: bool = CELLULAR_MOCK_MODE,
        enabled: bool = CELLULAR_ENABLED,
    ):
        self.port = port
        self.apn = apn
        self.mock_mode = mock_mode
        self.enabled = enabled
        self._simulated_state: Optional[bool] = None

    @property
    def transport_type(self) -> TransportType:
        return TransportType.CELLULAR

    def set_simulated_state(self, online: Optional[bool]) -> None:
        self._simulated_state = online

    def is_available(self) -> bool:
        if not self.enabled:
            return False
        if self._simulated_state is not None:
            return self._simulated_state
        if self.mock_mode:
            return True  # Mock adapter available for failover simulation
        return False  # Real modem not detected

    def check_health(self) -> Tuple[bool, str, Dict[str, Any]]:
        start_time = time.perf_counter()

        if not self.enabled:
            return False, "DISABLED", {"transport": "cellular", "enabled": False}

        if self._simulated_state is False:
            return False, "MODEM_OFFLINE", {
                "transport": "cellular",
                "status": "SIMULATED_CELLULAR_OFFLINE",
                "port": self.port,
            }

        if self.mock_mode:
            duration_ms = round((time.perf_counter() - start_time) * 1000.0, 2)
            return True, "MOCK_ACTIVE", {
                "transport": "cellular",
                "mock": True,
                "note": "REAL HARDWARE NOT TESTED — MOCK CELLULAR MODEM",
                "simulated_apn": self.apn,
                "latency_ms": duration_ms,
            }

        # Real Hardware Probe (Simulated check)
        return False, "MODEM_OFFLINE", {
            "transport": "cellular",
            "port": self.port,
            "error": "No physical cellular modem detected on serial port"
        }

    def send(self, payload: Dict[str, Any], record_type: str) -> Tuple[bool, str]:
        if not self.is_available():
            return False, "Cellular backhaul unavailable"

        if self.mock_mode:
            return True, "Buffered via Mock Cellular PPP tunnel (REAL HARDWARE NOT TESTED)"

        return False, "Real cellular modem transmission failed: Hardware not connected"
