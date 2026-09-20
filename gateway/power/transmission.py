"""
TerraEdge Phase 9 — Adaptive LoRa Transmission & Dynamic Duty-Cycle Scheduler.
Provides single authoritative logic for selecting transmission intervals, retry policies,
packet priorities, and sensor sampling profiles across all node states.
"""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

from .config import DEFAULT_POWER_CONFIG, PowerConfig
from .sensor_policy import SENSOR_POLICIES


@dataclass
class TransmissionProfile:
    power_state: str
    battery_state: str
    emergency_state: bool
    telemetry_interval_s: int
    retry_policy: Dict[str, Any]
    priority: str
    allowed_immediate_tx: bool
    sensor_sample_profile: List[str]
    gps_active: bool

    def to_dict(self) -> Dict[str, Any]:
        return {
            "power_state": self.power_state,
            "battery_state": self.battery_state,
            "emergency_state": self.emergency_state,
            "telemetry_interval_s": self.telemetry_interval_s,
            "retry_policy": self.retry_policy,
            "priority": self.priority,
            "allowed_immediate_tx": self.allowed_immediate_tx,
            "sensor_sample_profile": self.sensor_sample_profile,
            "gps_active": self.gps_active,
        }


def get_transmission_profile(
    power_state: str = "NORMAL",
    battery_state: str = "DISCHARGING",
    emergency_state: bool = False,
    config: Optional[PowerConfig] = None
) -> TransmissionProfile:
    """
    Authoritative selector for node transmission and duty-cycle parameters.
    Ensures consistent behavior across firmware and edge gateway.
    """
    cfg = config or DEFAULT_POWER_CONFIG
    p_state = (power_state or "NORMAL").upper()
    b_state = (battery_state or "DISCHARGING").upper()

    # 1. Telemetry Interval determination
    if emergency_state or p_state == "CRITICAL":
        interval = cfg.interval_critical_s
        priority = "EMERGENCY" if emergency_state else "HIGH"
        allowed_immediate = True
    elif p_state == "WARNING":
        interval = cfg.interval_warning_s
        priority = "ELEVATED"
        allowed_immediate = False
    elif p_state == "WATCH":
        interval = cfg.interval_watch_s
        priority = "NORMAL"
        allowed_immediate = False
    else:
        interval = cfg.interval_normal_s
        priority = "NORMAL"
        allowed_immediate = False

    # 2. Battery Protection Adjustments
    if b_state == "CRITICAL":
        # Emergency sensing preserved, but interval stretched slightly and retries disabled
        interval = max(interval, 60)
        retries = 0
        retry_timeout_ms = 1000
    elif b_state == "LOW":
        # Conserve battery
        interval = max(interval, 30)
        retries = 1
        retry_timeout_ms = 1500
    else:
        # Normal or Full battery
        if emergency_state or p_state == "CRITICAL":
            retries = 3
            retry_timeout_ms = 2500
        elif p_state == "WARNING":
            retries = 2
            retry_timeout_ms = 2000
        else:
            retries = 1
            retry_timeout_ms = 2000

    retry_policy = {
        "max_retries": retries,
        "ack_timeout_ms": retry_timeout_ms,
        "backoff_multiplier": 1.5,
    }

    # 3. Sensor sampling profile selection
    allowed_sensors: List[str] = []
    for sid, policy in SENSOR_POLICIES.items():
        if b_state == "CRITICAL":
            # Only vital hazard / trigger sensors
            if policy.emergency_priority == 1:
                allowed_sensors.append(sid)
        elif b_state == "LOW":
            # Priority 1 and 2 sensors
            if policy.emergency_priority <= 2:
                allowed_sensors.append(sid)
        elif p_state == "NORMAL":
            # Standard monitoring, nonessential sensors duty-cycled
            allowed_sensors.append(sid)
        else:
            # Elevated state (WATCH, WARNING, CRITICAL)
            allowed_sensors.append(sid)

    # 4. GPS Fix Determination
    if emergency_state or p_state in ("CRITICAL", "WARNING"):
        gps_active = True
    elif b_state in ("CRITICAL", "LOW"):
        gps_active = False  # Shut down GPS to preserve power
    else:
        gps_active = True

    return TransmissionProfile(
        power_state=p_state,
        battery_state=b_state,
        emergency_state=emergency_state,
        telemetry_interval_s=interval,
        retry_policy=retry_policy,
        priority=priority,
        allowed_immediate_tx=allowed_immediate,
        sensor_sample_profile=allowed_sensors,
        gps_active=gps_active,
    )
