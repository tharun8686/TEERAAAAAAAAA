"""
TerraEdge Phase 9 — Solar Panel & CN3791 MPPT Charger Telemetry Model.
Simulates solar harvesting and battery state of charge (SOC) based on irradiance,
MPPT conversion efficiency (88%), and Li-ion 18650 charge/discharge characteristics.

IMPORTANT: All outputs are SIMULATED/ESTIMATED models until physical ADC/current
sensors are measured on physical hardware.
"""

from __future__ import annotations
import math
from dataclasses import dataclass, field
from typing import Any, Dict, Optional, Tuple

from .config import DEFAULT_POWER_CONFIG, PowerConfig


def estimate_soc_from_voltage(voltage_v: float) -> float:
    """
    Estimates State of Charge (0.0 to 100.0%) for a 3.7V nominal Li-ion cell
    using a piecewise linear approximation of the OCV discharge curve.
    """
    if voltage_v >= 4.20:
        return 100.0
    elif voltage_v >= 4.05:
        return 90.0 + (voltage_v - 4.05) / (4.20 - 4.05) * 10.0
    elif voltage_v >= 3.85:
        return 60.0 + (voltage_v - 3.85) / (4.05 - 3.85) * 30.0
    elif voltage_v >= 3.70:
        return 40.0 + (voltage_v - 3.70) / (3.85 - 3.70) * 20.0
    elif voltage_v >= 3.50:
        return 15.0 + (voltage_v - 3.50) / (3.70 - 3.50) * 25.0
    elif voltage_v >= 3.20:
        return 5.0 + (voltage_v - 3.20) / (3.50 - 3.20) * 10.0
    elif voltage_v >= 3.00:
        return 0.0 + (voltage_v - 3.00) / (3.20 - 3.00) * 5.0
    else:
        return 0.0


def estimate_voltage_from_soc(soc_pct: float) -> float:
    """Estimates Open Circuit Voltage (V) from SOC percentage (0-100%)."""
    s = max(0.0, min(100.0, soc_pct))
    if s >= 90.0:
        return 4.05 + (s - 90.0) / 10.0 * (4.20 - 4.05)
    elif s >= 60.0:
        return 3.85 + (s - 60.0) / 30.0 * (4.05 - 3.85)
    elif s >= 40.0:
        return 3.70 + (s - 40.0) / 20.0 * (3.85 - 3.70)
    elif s >= 15.0:
        return 3.50 + (s - 15.0) / 25.0 * (3.70 - 3.50)
    elif s >= 5.0:
        return 3.20 + (s - 5.0) / 10.0 * (3.50 - 3.20)
    else:
        return 3.00 + s / 5.0 * (3.20 - 3.00)


def classify_battery_state(
    soc_pct: float,
    charging: bool,
    config: Optional[PowerConfig] = None
) -> str:
    """Classifies battery into: FULL, CHARGING, DISCHARGING, LOW, CRITICAL, UNKNOWN."""
    cfg = config or DEFAULT_POWER_CONFIG
    if soc_pct is None or math.isnan(soc_pct):
        return "UNKNOWN"

    if soc_pct <= cfg.battery_critical_pct:
        return "CRITICAL"
    elif soc_pct <= cfg.battery_low_pct:
        return "LOW"
    elif soc_pct >= cfg.battery_full_pct and charging:
        return "FULL"
    elif charging:
        return "CHARGING"
    else:
        return "DISCHARGING"


@dataclass
class SolarTelemetryModel:
    """Simulates or models the CN3791 MPPT charging system and battery state."""

    config: PowerConfig = field(default_factory=PowerConfig)
    current_soc_pct: float = 95.0
    is_hardware_measured: bool = False

    def simulate_solar_harvest(
        self,
        sunlight_factor: float = 1.0,  # 0.0 (night) to 1.0 (peak midday sun)
        node_load_ma: float = 25.0,    # current consumption of node
        elapsed_seconds: float = 300.0
    ) -> Dict[str, Any]:
        """
        Advances the solar & battery simulation by elapsed_seconds.
        Calculates MPPT harvest, net charge/discharge current, and updated battery SOC.
        """
        s_factor = max(0.0, min(1.0, sunlight_factor))
        solar_available = s_factor > 0.05
        
        # Solar panel generation
        solar_voltage_v = round(self.config.solar_mppt_v * (0.8 + 0.2 * s_factor) if solar_available else 0.0, 2)
        solar_power_w = round(self.config.solar_max_power_w * s_factor, 2)

        # CN3791 MPPT charging calculation
        # Harvest power converted to battery current: P_in * efficiency / V_bat
        bat_v = estimate_voltage_from_soc(self.current_soc_pct)
        mppt_power_w = solar_power_w * self.config.mppt_efficiency
        charge_current_a = (mppt_power_w / bat_v) if (solar_available and bat_v > 0) else 0.0
        charge_current_ma = charge_current_a * 1000.0

        # Net current into/out of battery
        net_current_ma = charge_current_ma - node_load_ma
        charging = net_current_ma > 0.0

        # Update SOC
        delta_hours = elapsed_seconds / 3600.0
        delta_mah = net_current_ma * delta_hours
        delta_pct = (delta_mah / self.config.battery_capacity_mah) * 100.0

        new_soc = max(0.0, min(100.0, self.current_soc_pct + delta_pct))
        self.current_soc_pct = round(new_soc, 2)
        updated_v = round(estimate_voltage_from_soc(self.current_soc_pct), 2)
        bat_state = classify_battery_state(self.current_soc_pct, charging, self.config)

        # Power figures
        bat_power_w = round(abs(net_current_ma / 1000.0) * updated_v, 3)

        return {
            "solar_available": solar_available,
            "solar_input_voltage_v": solar_voltage_v,
            "solar_input_power_w": solar_power_w,
            "charging": charging,
            "battery_voltage_v": updated_v,
            "battery_soc_pct": self.current_soc_pct,
            "battery_state": bat_state,
            "battery_current_a": round(net_current_ma / 1000.0, 3),
            "battery_power_w": bat_power_w,
            "estimated_charge_rate": round(charge_current_ma, 1),
            "estimated_discharge_rate": round(node_load_ma, 1),
            "is_simulated": not self.is_hardware_measured,
            "measurement_status": "HARDWARE-MEASURED" if self.is_hardware_measured else "SIMULATED",
        }
