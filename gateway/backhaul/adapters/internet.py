"""
TerraEdge — Internet (Wi-Fi / Ethernet) Backhaul Adapter.
Provides primary cloud connectivity monitoring and data synchronization to Supabase.
"""

from __future__ import annotations
import time
import urllib.error
import urllib.request
from typing import Any, Dict, Optional, Tuple

from ...config import BACKHAUL_MODE, BACKHAUL_PING_TIMEOUT_S, SUPABASE_URL
from ..schemas import TransportType
from .base import BaseBackhaulAdapter


class InternetBackhaulAdapter(BaseBackhaulAdapter):
    def __init__(
        self,
        target_url: Optional[str] = None,
        timeout_s: float = BACKHAUL_PING_TIMEOUT_S,
    ):
        self.target_url = target_url or SUPABASE_URL or "https://1.1.1.1"
        self.timeout_s = timeout_s
        self._simulated_state: Optional[bool] = None  # None = dynamic check; True/False = override

    @property
    def transport_type(self) -> TransportType:
        return TransportType.ETHERNET_WIFI

    def set_simulated_state(self, online: Optional[bool]) -> None:
        """Allows test scenarios to simulate cloud dropouts dynamically."""
        self._simulated_state = online

    def is_available(self) -> bool:
        if self._simulated_state is not None:
            return self._simulated_state
        if BACKHAUL_MODE == "mock_offline":
            return False
        if BACKHAUL_MODE == "mock_reconnect":
            return True

        healthy, _, _ = self.check_health()
        return healthy

    def check_health(self) -> Tuple[bool, str, Dict[str, Any]]:
        start_time = time.perf_counter()

        if self._simulated_state is False or BACKHAUL_MODE == "mock_offline":
            duration_ms = round((time.perf_counter() - start_time) * 1000.0, 2)
            return False, "NETWORK_TIMEOUT", {
                "transport": "ethernet_wifi",
                "mode": "simulated_offline",
                "latency_ms": duration_ms
            }

        if not self.target_url or not self.target_url.startswith("http"):
            # When unconfigured in local dev/demo mode, report available for local simulation
            return True, "AVAILABLE", {"transport": "ethernet_wifi", "mode": "local_dev", "latency_ms": 0.1}

        try:
            req = urllib.request.Request(
                self.target_url,
                headers={"User-Agent": "TerraEdge-Gateway-Ping/5.0"},
                method="HEAD"
            )
            with urllib.request.urlopen(req, timeout=self.timeout_s) as response:
                status_code = response.status
                duration_ms = round((time.perf_counter() - start_time) * 1000.0, 2)
                if 200 <= status_code < 400:
                    return True, "AVAILABLE", {"http_status": status_code, "latency_ms": duration_ms}
                elif status_code in (401, 403):
                    return True, "AUTH_FAILURE", {"http_status": status_code, "latency_ms": duration_ms}
                else:
                    return False, "SERVER_ERROR", {"http_status": status_code, "latency_ms": duration_ms}
        except urllib.error.HTTPError as he:
            duration_ms = round((time.perf_counter() - start_time) * 1000.0, 2)
            if he.code in (401, 403, 404):  # Host reached, auth/route response
                return True, "AVAILABLE", {"http_status": he.code, "latency_ms": duration_ms}
            return False, "SERVER_ERROR", {"http_status": he.code, "latency_ms": duration_ms}
        except Exception as exc:
            duration_ms = round((time.perf_counter() - start_time) * 1000.0, 2)
            return False, "NETWORK_TIMEOUT", {"error": str(exc), "latency_ms": duration_ms}

    def send(self, payload: Dict[str, Any], record_type: str) -> Tuple[bool, str]:
        if not self.is_available():
            return False, "Internet backhaul is offline"

        try:
            from common import terra_supabase as db
            if db is None:
                return True, "In-memory database updated (local development)"

            if record_type == "node":
                db.seed_nodes(payload.get("hazard", "all"), [payload])
            elif record_type == "telemetry" or record_type == "prediction":
                db.log_prediction(
                    hazard=payload.get("hazard", "environmental"),
                    node_id=payload.get("node_id"),
                    payload=payload.get("payload", {}),
                    result=payload.get("result", {})
                )
            elif record_type == "alert":
                db.insert_alert(payload.get("hazard", "alert").lower(), payload)
            elif record_type == "dispatch":
                db.insert_dispatches([payload])

            return True, "Synchronized to Supabase"
        except Exception as exc:
            return False, f"Supabase write error: {str(exc)}"
