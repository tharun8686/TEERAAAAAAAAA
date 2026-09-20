"""
TerraEdge Phase 9 — Power Budget & Node Autonomy Calculation Engine.
Calculates time-weighted average current draw, daily energy consumption (Wh),
solar energy harvesting balance, and remaining operational autonomy (hours/days).

IMPORTANT: Every figure computed here is explicitly marked as ESTIMATED based on
datasheet assumptions and will be calibrated when real hardware measurements are taken.
"""

from __future__ import annotations
from dataclasses import dataclass
from typing import Any, Dict, List, Optional

from .config import DEFAULT_POWER_CONFIG, PowerConfig
from .sensor_policy import SENSOR_POLICIES, SensorPowerPolicy


@dataclass
class PowerBudgetResult:
    estimated_average_current_ma: float
    estimated_power_w: float
    estimated_energy_per_hour_wh: float
    estimated_daily_energy_use_wh: float
    estimated_daily_solar_input_wh: float
    estimated_autonomy_hours: float
    estimated_autonomy_days: float
    estimated_energy_balance_wh_per_day: float
    data_classification: str = "ESTIMATED"

    def to_dict(self) -> Dict[str, Any]:
        return {
            "estimated_average_current_ma": round(self.estimated_average_current_ma, 2),
            "estimated_power_w": round(self.estimated_power_w, 3),
            "estimated_energy_per_hour_wh": round(self.estimated_energy_per_hour_wh, 3),
            "estimated_daily_energy_use_wh": round(self.estimated_daily_energy_use_wh, 2),
            "estimated_daily_solar_input_wh": round(self.estimated_daily_solar_input_wh, 2),
            "estimated_autonomy_hours": round(self.estimated_autonomy_hours, 1),
            "estimated_autonomy_days": round(self.estimated_autonomy_days, 2),
            "estimated_energy_balance_wh_per_day": round(self.estimated_energy_balance_wh_per_day, 2),
            "data_classification": self.data_classification,
        }


class PowerBudgetEngine:
    """Calculates power budget and battery autonomy for field node configurations."""

    def __init__(self, config: Optional[PowerConfig] = None):
        self.config = config or DEFAULT_POWER_CONFIG

    def calculate_budget(
        self,
        telemetry_interval_s: int,
        battery_soc_pct: float = 100.0,
        battery_voltage_v: Optional[float] = None,
        active_sensor_ids: Optional[List[str]] = None,
        average_sunlight_hours_per_day: float = 5.0,
        solar_peak_power_w: Optional[float] = None,
        cpu_active_seconds_per_sample: float = 1.5,
        gps_interval_s: Optional[int] = None,
    ) -> PowerBudgetResult:
        """
        Calculates comprehensive node energy budget and autonomy.

        Args:
            telemetry_interval_s: Interval between sensor wake-up and LoRa transmission (s).
            battery_soc_pct: Current battery state of charge (0-100%).
            battery_voltage_v: Operating battery voltage (defaults to 3.7V).
            active_sensor_ids: List of sensors configured/present on node.
            average_sunlight_hours_per_day: Equivalent peak sun hours per day.
            solar_peak_power_w: Solar panel rating (defaults to config).
            cpu_active_seconds_per_sample: Time ESP32 is awake per telemetry cycle.
            gps_interval_s: Interval between GPS fixes (defaults to config).
        """
        interval = max(5, telemetry_interval_s)
        v_bat = battery_voltage_v or self.config.battery_nominal_voltage_v
        v_bat = max(3.0, min(4.2, v_bat))
        sensor_ids = active_sensor_ids or list(SENSOR_POLICIES.keys())
        p_solar = solar_peak_power_w if solar_peak_power_w is not None else self.config.solar_max_power_w

        # --- 1. Sensor Power Calculation per Telemetry Cycle ---
        cycle_sensor_energy_ma_s = 0.0
        cycle_sleep_sensor_energy_ma_s = 0.0

        for sid in sensor_ids:
            policy = SENSOR_POLICIES.get(sid)
            if not policy:
                continue
            if policy.always_on:
                # Continuous load
                cycle_sensor_energy_ma_s += policy.active_power_estimate_ma * interval
            else:
                # Active only during warm-up + sampling
                active_duration_s = max(0.5, policy.warmup_ms / 1000.0 + 0.5)
                active_duration_s = min(float(interval), active_duration_s)
                sleep_duration_s = max(0.0, interval - active_duration_s)

                cycle_sensor_energy_ma_s += policy.active_power_estimate_ma * active_duration_s
                cycle_sleep_sensor_energy_ma_s += policy.sleep_power_estimate_ma * sleep_duration_s

        total_sensor_ma_s = cycle_sensor_energy_ma_s + cycle_sleep_sensor_energy_ma_s

        # --- 2. CPU / MCU Energy per Telemetry Cycle ---
        active_time_s = min(float(interval), cpu_active_seconds_per_sample)
        sleep_time_s = max(0.0, interval - active_time_s)
        cpu_ma_s = (self.config.cpu_active_ma * active_time_s) + (self.config.cpu_light_sleep_ma * sleep_time_s)

        # --- 3. LoRa TX/RX Energy per Telemetry Cycle ---
        lora_tx_time_s = 0.25  # ~250ms packet TX
        lora_rx_time_s = 0.10  # ~100ms ACK listen window
        lora_sleep_time_s = max(0.0, interval - (lora_tx_time_s + lora_rx_time_s))
        lora_ma_s = (
            (self.config.lora_tx_ma * lora_tx_time_s)
            + (self.config.lora_rx_ma * lora_rx_time_s)
            + (self.config.lora_sleep_ma * lora_sleep_time_s)
        )

        # --- 4. GPS Duty-Cycled Energy ---
        gps_int = gps_interval_s or self.config.gps_interval_normal_s
        gps_active_per_fix_s = 5.0  # 5 seconds to acquire fix
        gps_duty_fraction = min(1.0, gps_active_per_fix_s / max(10, gps_int))
        gps_avg_ma = (self.config.gps_active_ma * gps_duty_fraction) + (self.config.gps_standby_ma * (1.0 - gps_duty_fraction))
        gps_ma_s = gps_avg_ma * interval

        # --- 5. Total Cycle Current & Power ---
        total_cycle_ma_s = total_sensor_ma_s + cpu_ma_s + lora_ma_s + gps_ma_s
        avg_current_ma = total_cycle_ma_s / interval
        avg_power_w = (avg_current_ma / 1000.0) * v_bat

        # Energy metrics
        energy_per_hour_wh = (avg_current_ma / 1000.0) * v_bat
        daily_energy_use_wh = energy_per_hour_wh * 24.0

        # Solar input calculation
        # Daily solar Wh = Peak solar power * efficiency * equivalent sun hours
        daily_solar_input_wh = p_solar * self.config.mppt_efficiency * average_sunlight_hours_per_day
        daily_energy_balance_wh = daily_solar_input_wh - daily_energy_use_wh

        # Autonomy calculation (without solar, relying purely on battery capacity)
        # Usable remaining capacity = Total Capacity * (SOC% / 100) * 0.9 (90% DoD safe limit)
        usable_capacity_mah = self.config.battery_capacity_mah * (max(0.0, battery_soc_pct) / 100.0) * 0.90
        if avg_current_ma > 0:
            autonomy_hours = usable_capacity_mah / avg_current_ma
            autonomy_days = autonomy_hours / 24.0
        else:
            autonomy_hours = 999.0
            autonomy_days = 41.6

        return PowerBudgetResult(
            estimated_average_current_ma=avg_current_ma,
            estimated_power_w=avg_power_w,
            estimated_energy_per_hour_wh=energy_per_hour_wh,
            estimated_daily_energy_use_wh=daily_energy_use_wh,
            estimated_daily_solar_input_wh=daily_solar_input_wh,
            estimated_autonomy_hours=autonomy_hours,
            estimated_autonomy_days=autonomy_days,
            estimated_energy_balance_wh_per_day=daily_energy_balance_wh,
            data_classification="ESTIMATED",
        )
