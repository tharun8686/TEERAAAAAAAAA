"""
TerraEdge Phase 9 — Power Management and LoRa Duty-Cycle Optimization Package.
"""

from .config import DEFAULT_POWER_CONFIG, PowerConfig
from .state_machine import NodePowerStateMachine, PowerState
from .sensor_policy import SENSOR_POLICIES, SensorPowerPolicy, SensorWarmupScheduler
from .emergency import check_emergency_conditions, prepare_emergency_telemetry
from .solar_model import (
    SolarTelemetryModel,
    classify_battery_state,
    estimate_soc_from_voltage,
    estimate_voltage_from_soc,
)
from .budget import PowerBudgetEngine, PowerBudgetResult
from .transmission import TransmissionProfile, get_transmission_profile

__all__ = [
    "DEFAULT_POWER_CONFIG",
    "PowerConfig",
    "NodePowerStateMachine",
    "PowerState",
    "SENSOR_POLICIES",
    "SensorPowerPolicy",
    "SensorWarmupScheduler",
    "check_emergency_conditions",
    "prepare_emergency_telemetry",
    "SolarTelemetryModel",
    "classify_battery_state",
    "estimate_soc_from_voltage",
    "estimate_voltage_from_soc",
    "PowerBudgetEngine",
    "PowerBudgetResult",
    "TransmissionProfile",
    "get_transmission_profile",
]
