"""
TerraEdge Phase 9 — Sensor Power Policy & Warm-up Scheduling Abstraction.
Encapsulates metadata, estimated current draw (active vs sleep), warm-up requirements,
and duty-cycling constraints for each environmental sensor in the hardware catalog.

IMPORTANT: All electrical ratings (mA) are ESTIMATED/SIMULATED based on datasheet
baselines and will be calibrated when physical hardware arrives.
"""

from __future__ import annotations
import time
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional


@dataclass
class SensorPowerPolicy:
    sensor_id: str
    hazard_domain: str
    warmup_ms: int
    active_power_estimate_ma: float
    sleep_power_estimate_ma: float
    always_on: bool
    duty_cycle_allowed: bool
    emergency_priority: int  # 1 = Highest (Critical trigger) to 5 = Low/deferrable
    switched_power_rail: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "sensor_id": self.sensor_id,
            "hazard_domain": self.hazard_domain,
            "warmup_ms": self.warmup_ms,
            "active_power_estimate_ma": self.active_power_estimate_ma,
            "sleep_power_estimate_ma": self.sleep_power_estimate_ma,
            "always_on": self.always_on,
            "duty_cycle_allowed": self.duty_cycle_allowed,
            "emergency_priority": self.emergency_priority,
            "switched_power_rail": self.switched_power_rail,
        }


# Authoritative catalog of sensor power policies
SENSOR_POLICIES: Dict[str, SensorPowerPolicy] = {
    "bme680": SensorPowerPolicy(
        sensor_id="bme680",
        hazard_domain="Atmospheric / Weather",
        warmup_ms=1000,
        active_power_estimate_ma=12.0,
        sleep_power_estimate_ma=0.005,
        always_on=False,
        duty_cycle_allowed=True,
        emergency_priority=3,
        switched_power_rail="SENSOR_POWER_I2C",
    ),
    "sds011": SensorPowerPolicy(
        sensor_id="sds011",
        hazard_domain="Air Quality (PM2.5/PM10)",
        warmup_ms=10000,  # 10s fan stabilization
        active_power_estimate_ma=80.0,
        sleep_power_estimate_ma=0.5,
        always_on=False,
        duty_cycle_allowed=True,
        emergency_priority=4,
        switched_power_rail="SENSOR_POWER_SDS011",
    ),
    "mq135": SensorPowerPolicy(
        sensor_id="mq135",
        hazard_domain="Toxic Gas / Air Quality",
        warmup_ms=5000,  # Pulsed heater cycle (or preheat)
        active_power_estimate_ma=160.0,  # Heater current @ 5V
        sleep_power_estimate_ma=0.0,
        always_on=False,
        duty_cycle_allowed=True,
        emergency_priority=3,
        switched_power_rail="SENSOR_POWER_MQ135",
    ),
    "rainfall": SensorPowerPolicy(
        sensor_id="rainfall",
        hazard_domain="Hydrological (Precipitation)",
        warmup_ms=50,
        active_power_estimate_ma=5.0,
        sleep_power_estimate_ma=0.0,
        always_on=False,
        duty_cycle_allowed=True,
        emergency_priority=2,
        switched_power_rail="SENSOR_POWER_ADC_RAIL",
    ),
    "water_level": SensorPowerPolicy(
        sensor_id="water_level",
        hazard_domain="Flood / Hydrological",
        warmup_ms=100,
        active_power_estimate_ma=15.0,
        sleep_power_estimate_ma=0.0,
        always_on=False,
        duty_cycle_allowed=True,
        emergency_priority=1,  # Critical emergency trigger
        switched_power_rail="SENSOR_POWER_ADC_RAIL",
    ),
    "ultrasonic": SensorPowerPolicy(
        sensor_id="ultrasonic",
        hazard_domain="Flood (JSN-SR04T Stage)",
        warmup_ms=200,
        active_power_estimate_ma=30.0,
        sleep_power_estimate_ma=0.0,
        always_on=False,
        duty_cycle_allowed=True,
        emergency_priority=2,
        switched_power_rail="SENSOR_POWER_5V_BOOST",
    ),
    "soil_moisture": SensorPowerPolicy(
        sensor_id="soil_moisture",
        hazard_domain="Landslide / Hydrological",
        warmup_ms=100,
        active_power_estimate_ma=8.0,
        sleep_power_estimate_ma=0.0,
        always_on=False,
        duty_cycle_allowed=True,
        emergency_priority=2,
        switched_power_rail="SENSOR_POWER_ADC_RAIL",
    ),
    "mpu6050": SensorPowerPolicy(
        sensor_id="mpu6050",
        hazard_domain="Geotechnical (Tilt / Landslide)",
        warmup_ms=150,
        active_power_estimate_ma=3.8,
        sleep_power_estimate_ma=0.05,
        always_on=True,  # Low-power motion interrupt or continuous sampling
        duty_cycle_allowed=False,
        emergency_priority=1,
        switched_power_rail="SENSOR_POWER_I2C",
    ),
    "sw420": SensorPowerPolicy(
        sensor_id="sw420",
        hazard_domain="Geotechnical (Vibration / Seismic)",
        warmup_ms=10,
        active_power_estimate_ma=0.5,
        sleep_power_estimate_ma=0.05,
        always_on=True,  # Low-power hardware interrupt
        duty_cycle_allowed=False,
        emergency_priority=1,
        switched_power_rail="SENSOR_POWER_3V3",
    ),
    "flame": SensorPowerPolicy(
        sensor_id="flame",
        hazard_domain="Wildfire / Optical Flame",
        warmup_ms=20,
        active_power_estimate_ma=5.0,
        sleep_power_estimate_ma=0.05,
        always_on=True,  # Immediate fire comparator interrupt
        duty_cycle_allowed=False,
        emergency_priority=1,
        switched_power_rail="SENSOR_POWER_3V3",
    ),
    "ph": SensorPowerPolicy(
        sensor_id="ph",
        hazard_domain="Water Quality (Acidity)",
        warmup_ms=1500,
        active_power_estimate_ma=20.0,
        sleep_power_estimate_ma=0.0,
        duty_cycle_allowed=True,
        always_on=False,
        emergency_priority=4,
        switched_power_rail="SENSOR_POWER_PH",
    ),
    "tds": SensorPowerPolicy(
        sensor_id="tds",
        hazard_domain="Water Quality (Dissolved Solids)",
        warmup_ms=1000,
        active_power_estimate_ma=20.0,
        sleep_power_estimate_ma=0.0,
        duty_cycle_allowed=True,
        always_on=False,
        emergency_priority=4,
        switched_power_rail="SENSOR_POWER_TDS",
    ),
    "turbidity": SensorPowerPolicy(
        sensor_id="turbidity",
        hazard_domain="Water Quality (Turbidity)",
        warmup_ms=1000,
        active_power_estimate_ma=40.0,
        sleep_power_estimate_ma=0.0,
        duty_cycle_allowed=True,
        always_on=False,
        emergency_priority=4,
        switched_power_rail="SENSOR_POWER_TURBIDITY",
    ),
    "gps": SensorPowerPolicy(
        sensor_id="gps",
        hazard_domain="Geospatial / Navigation",
        warmup_ms=5000,  # 5s hot fix
        active_power_estimate_ma=45.0,
        sleep_power_estimate_ma=1.0,
        duty_cycle_allowed=True,
        always_on=False,
        emergency_priority=2,
        switched_power_rail="SENSOR_POWER_GPS",
    ),
}


class SensorWarmupScheduler:
    """
    Non-blocking sensor warm-up scheduler and power manager.
    Tracks state transitions: OFF -> POWERING_ON -> WARMING_UP -> READY -> READING -> POWERING_OFF.
    """

    def __init__(self, policies: Optional[Dict[str, SensorPowerPolicy]] = None):
        self.policies = policies or SENSOR_POLICIES
        self._sensor_power_state: Dict[str, bool] = {s: False for s in self.policies}
        self._warmup_start_times: Dict[str, float] = {}

    def is_powered(self, sensor_id: str) -> bool:
        return self._sensor_power_state.get(sensor_id, False)

    def power_on_sensor(self, sensor_id: str, timestamp: Optional[float] = None) -> None:
        """Enables power rail for the given sensor and marks warm-up start."""
        now = timestamp if timestamp is not None else time.time()
        self._sensor_power_state[sensor_id] = True
        self._warmup_start_times[sensor_id] = now

    def power_off_sensor(self, sensor_id: str) -> None:
        """Disables power rail for the given sensor if duty-cycling allows."""
        policy = self.policies.get(sensor_id)
        if policy and not policy.always_on:
            self._sensor_power_state[sensor_id] = False
            self._warmup_start_times.pop(sensor_id, None)

    def is_warmed_up(self, sensor_id: str, current_time: Optional[float] = None) -> bool:
        """Checks if configured warm-up delay has elapsed since power on."""
        if not self.is_powered(sensor_id):
            return False
        policy = self.policies.get(sensor_id)
        if not policy:
            return True
        start = self._warmup_start_times.get(sensor_id)
        if start is None:
            return True
        now = current_time if current_time is not None else time.time()
        elapsed_ms = (now - start) * 1000.0
        return elapsed_ms >= policy.warmup_ms

    def get_active_sensors(self, power_mode: str, battery_state: str, is_emergency: bool = False) -> List[str]:
        """
        Calculates which sensors should be sampled/powered for the current power state,
        battery state, and emergency condition.
        """
        active: List[str] = []
        for sid, policy in self.policies.items():
            if is_emergency:
                # Emergency mode activates critical triggers and situational sensors
                if policy.emergency_priority <= 3:
                    active.append(sid)
                continue

            if battery_state == "CRITICAL":
                # Only priority 1 emergency detection sensors remain active
                if policy.emergency_priority == 1:
                    active.append(sid)
                continue

            if battery_state == "LOW":
                # Priority 1 and 2 sensors active, heavy sensors skipped
                if policy.emergency_priority <= 2:
                    active.append(sid)
                continue

            # Standard power modes (NORMAL, WATCH, WARNING, CRITICAL)
            if power_mode == "NORMAL":
                # In NORMAL mode, heavy sensors like SDS011 / MQ135 are duty-cycled intermittently
                active.append(sid)
            elif power_mode == "WATCH":
                active.append(sid)
            elif power_mode in ("WARNING", "CRITICAL"):
                active.append(sid)

        return active
