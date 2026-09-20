"""
TerraEdge Phase 9 — Local Emergency Wake-up & Immediate Dispatch Detector.
Monitors high-priority physical sensor thresholds:
1. Flame detected (IR flame comparator trigger)
2. Severe flood water level / ultrasonic breach
3. Extreme seismic vibration pulse rate (SW-420)
4. Critical slope tilt magnitude or sudden acceleration tilt rate (MPU6050)
"""

from __future__ import annotations
from typing import Any, Dict, List, Optional, Tuple

from .config import DEFAULT_POWER_CONFIG, PowerConfig


def check_emergency_conditions(
    telemetry: Any,
    config: Optional[PowerConfig] = None
) -> Tuple[bool, List[str]]:
    """
    Evaluates whether incoming telemetry contains any critical localized emergency triggers.
    Supports Pydantic model or dict representation.

    Returns:
        (is_emergency: bool, trigger_reasons: List[str])
    """
    cfg = config or DEFAULT_POWER_CONFIG
    if not cfg.emergency_wakeup_enabled:
        return False, []

    reasons: List[str] = []

    def _get(key: str, default: Any = None) -> Any:
        if isinstance(telemetry, dict):
            return telemetry.get(key, default)
        return getattr(telemetry, key, default)

    # 1. Flame detection (Active fire)
    fd = _get("flame_detected")
    fl = _get("flame")
    if fd is True or fl == 1:
        reasons.append("Optical flame detected (Active Fire Threat)")

    # 2. Water level / Ultrasonic bankfull stage breach
    wl_m = _get("water_level_m")
    wl_pct = _get("water_level_pct")
    if wl_m is not None and wl_m >= cfg.emergency_water_level_m:
        reasons.append(f"Severe water level threshold breach ({wl_m:.2f}m >= {cfg.emergency_water_level_m}m)")
    elif wl_pct is not None and wl_pct >= cfg.emergency_water_level_pct:
        reasons.append(f"Water bankfull percentage breach ({wl_pct:.1f}% >= {cfg.emergency_water_level_pct}%)")

    # 3. Seismic / Structural vibration pulses
    vib = _get("vibration_rate")
    if vib is not None and vib >= cfg.emergency_vibration_rate:
        reasons.append(f"Extreme seismic vibration event ({vib:.1f} pulses/min >= {cfg.emergency_vibration_rate})")

    # 4. Slope tilt magnitude & sudden ground displacement rate
    tilt_mag = _get("tilt_magnitude")
    tilt_rate = _get("tilt_rate")
    if tilt_mag is not None and tilt_mag >= cfg.emergency_tilt_magnitude_deg:
        reasons.append(f"Critical slope tilt inclination ({tilt_mag:.1f}° >= {cfg.emergency_tilt_magnitude_deg}°)")
    if tilt_rate is not None and abs(tilt_rate) >= cfg.emergency_tilt_rate_deg:
        reasons.append(f"Rapid slope failure rate ({tilt_rate:.1f}°/min >= {cfg.emergency_tilt_rate_deg}°/min)")

    is_emergency = len(reasons) > 0
    return is_emergency, reasons


def prepare_emergency_telemetry(telemetry_dict: Dict[str, Any], reasons: List[str]) -> Dict[str, Any]:
    """
    Augments telemetry packet for immediate high-priority LoRa transmission.
    Sets telemetry_priority='EMERGENCY', power_mode='CRITICAL', emergency_state=True.
    """
    updated = dict(telemetry_dict)
    updated["telemetry_priority"] = "EMERGENCY"
    updated["power_mode"] = "CRITICAL"
    updated["emergency_state"] = True
    updated["telemetry_interval_s"] = 10
    updated["emergency_reasons"] = reasons
    return updated
