"""
TerraEdge Phase 9 — Field Node Power Management Configuration.
Authoritative, single-source-of-truth configuration for autonomous power states,
LoRa duty-cycling, battery thresholds, sensor policies, and power budgeting.
"""

from __future__ import annotations
import os
from dataclasses import dataclass, field
from typing import Any, Dict


@dataclass
class PowerConfig:
    # 1. Telemetry & Sleep Intervals (seconds)
    interval_normal_s: int = int(os.getenv("POWER_NORMAL_INTERVAL", "300"))
    interval_watch_s: int = int(os.getenv("POWER_WATCH_INTERVAL", "60"))
    interval_warning_s: int = int(os.getenv("POWER_WARNING_INTERVAL", "30"))
    interval_critical_s: int = int(os.getenv("POWER_CRITICAL_INTERVAL", "10"))
    interval_emergency_s: int = int(os.getenv("POWER_EMERGENCY_INTERVAL", "10"))

    # 2. State Transition Risk Thresholds (%)
    watch_risk_threshold: float = float(os.getenv("POWER_WATCH_THRESHOLD", "40.0"))
    warning_risk_threshold: float = float(os.getenv("POWER_WARNING_THRESHOLD", "60.0"))
    critical_risk_threshold: float = float(os.getenv("POWER_CRITICAL_THRESHOLD", "80.0"))

    # 3. Hysteresis & Recovery Protection
    recovery_samples_required: int = int(os.getenv("POWER_RECOVERY_SAMPLES", "3"))
    recovery_time_seconds: float = float(os.getenv("POWER_RECOVERY_TIME_S", "180.0"))

    # 4. Battery Thresholds & Electrical Characteristics (2x 18650 parallel pack)
    battery_full_pct: float = float(os.getenv("BATTERY_FULL_PCT", "95.0"))
    battery_low_pct: float = float(os.getenv("BATTERY_LOW_PCT", "25.0"))
    battery_critical_pct: float = float(os.getenv("BATTERY_CRITICAL_PCT", "10.0"))
    battery_nominal_voltage_v: float = float(os.getenv("BATTERY_NOMINAL_V", "3.7"))
    battery_max_voltage_v: float = float(os.getenv("BATTERY_MAX_V", "4.2"))
    battery_min_voltage_v: float = float(os.getenv("BATTERY_MIN_V", "3.0"))
    battery_capacity_mah: float = float(os.getenv("BATTERY_CAPACITY_MAH", "5200.0"))  # 2x 2600mAh

    # 5. Solar / CN3791 MPPT Charger Model Characteristics
    solar_max_power_w: float = float(os.getenv("SOLAR_MAX_POWER_W", "5.0"))
    solar_voc_v: float = float(os.getenv("SOLAR_VOC_V", "6.0"))
    solar_mppt_v: float = float(os.getenv("SOLAR_MPPT_V", "5.0"))
    mppt_efficiency: float = float(os.getenv("SOLAR_MPPT_EFFICIENCY", "0.88"))

    # 6. GPS Duty-Cycling (seconds)
    gps_interval_normal_s: int = int(os.getenv("GPS_INTERVAL_NORMAL", "3600"))  # 1 hr in normal
    gps_interval_watch_s: int = int(os.getenv("GPS_INTERVAL_WATCH", "600"))     # 10 min
    gps_interval_warning_s: int = int(os.getenv("GPS_INTERVAL_WARNING", "120")) # 2 min
    gps_interval_critical_s: int = int(os.getenv("GPS_INTERVAL_CRITICAL", "30"))# 30 sec

    # 7. Local Emergency Triggers
    emergency_wakeup_enabled: bool = os.getenv("EMERGENCY_WAKEUP_ENABLED", "true").lower() in ("1", "true", "yes")
    emergency_water_level_m: float = float(os.getenv("EMERGENCY_WATER_LEVEL_M", "3.5"))
    emergency_water_level_pct: float = float(os.getenv("EMERGENCY_WATER_LEVEL_PCT", "85.0"))
    emergency_vibration_rate: float = float(os.getenv("EMERGENCY_VIBRATION_RATE", "50.0"))
    emergency_tilt_magnitude_deg: float = float(os.getenv("EMERGENCY_TILT_MAG", "25.0"))
    emergency_tilt_rate_deg: float = float(os.getenv("EMERGENCY_TILT_RATE", "5.0"))

    # 8. Estimated Power Consumption Baseline (mA @ 3.7V nominal)
    cpu_active_ma: float = 45.0          # ESP32-S3 active running Wi-Fi/LoRa tasks
    cpu_light_sleep_ma: float = 2.5      # Light sleep (fast wake)
    cpu_deep_sleep_ma: float = 0.05      # Deep sleep RTC timer wake
    lora_tx_ma: float = 90.0             # SX1278 TX @ 17dBm (~200ms duration)
    lora_rx_ma: float = 13.0             # SX1278 RX listen
    lora_sleep_ma: float = 0.001         # SX1278 sleep
    gps_active_ma: float = 45.0          # NEO-6M active search/fix
    gps_standby_ma: float = 1.0          # NEO-6M backup mode

    power_estimation_enabled: bool = True

    def to_dict(self) -> Dict[str, Any]:
        return {k: getattr(self, k) for k in self.__dataclass_fields__}


# Authoritative global instance
DEFAULT_POWER_CONFIG = PowerConfig()
