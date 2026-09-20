"""
TerraEdge Phase 9 — Power Management State Machine.
Implements deterministic Type A power states (NORMAL, WATCH, WARNING, CRITICAL),
priority escalation, hysteresis / recovery stabilization, and telemetry interval derivation.
"""

from __future__ import annotations
import time
from enum import Enum
from typing import Any, Dict, Optional, Tuple

from .config import DEFAULT_POWER_CONFIG, PowerConfig


class PowerState(str, Enum):
    NORMAL = "NORMAL"
    WATCH = "WATCH"
    WARNING = "WARNING"
    CRITICAL = "CRITICAL"


# Severity / priority weight mapping (higher is more critical)
STATE_PRIORITY: Dict[PowerState, int] = {
    PowerState.NORMAL: 1,
    PowerState.WATCH: 2,
    PowerState.WARNING: 3,
    PowerState.CRITICAL: 4,
}


class NodePowerStateMachine:
    """
    Deterministic power state machine for an individual Type A field node.
    Tracks state transitions, consecutive recovery samples, and stabilization timers.
    """

    def __init__(
        self,
        node_id: str,
        config: Optional[PowerConfig] = None,
        initial_state: PowerState = PowerState.NORMAL
    ):
        self.node_id = node_id
        self.config = config or DEFAULT_POWER_CONFIG
        self.current_state: PowerState = initial_state
        
        # Hysteresis & recovery tracking
        self.consecutive_normal_samples: int = 0
        self.last_escalation_time: float = time.time()
        self.last_transition_time: float = time.time()
        self.last_risk_pct: float = 0.0
        self.last_severity: str = "NORMAL"
        self.emergency_active: bool = False

    def get_telemetry_interval(self) -> int:
        """Returns authoritative transmission interval in seconds for current state."""
        if self.emergency_active or self.current_state == PowerState.CRITICAL:
            return self.config.interval_critical_s
        elif self.current_state == PowerState.WARNING:
            return self.config.interval_warning_s
        elif self.current_state == PowerState.WATCH:
            return self.config.interval_watch_s
        else:
            return self.config.interval_normal_s

    def get_gps_interval(self) -> int:
        """Returns GPS duty-cycle interval in seconds for current state."""
        if self.emergency_active or self.current_state == PowerState.CRITICAL:
            return self.config.gps_interval_critical_s
        elif self.current_state == PowerState.WARNING:
            return self.config.gps_interval_warning_s
        elif self.current_state == PowerState.WATCH:
            return self.config.gps_interval_watch_s
        else:
            return self.config.gps_interval_normal_s

    def evaluate_target_state(
        self,
        risk_pct: float,
        severity: Optional[str] = None,
        emergency_trigger: bool = False
    ) -> PowerState:
        """Calculates instantaneous target state based on risk score and thresholds."""
        if emergency_trigger:
            return PowerState.CRITICAL

        sev = (severity or "NORMAL").upper()
        if sev == "CRITICAL" or risk_pct >= self.config.critical_risk_threshold:
            return PowerState.CRITICAL
        elif sev == "WARNING" or risk_pct >= self.config.warning_risk_threshold:
            return PowerState.WARNING
        elif sev == "WATCH" or risk_pct >= self.config.watch_risk_threshold:
            return PowerState.WATCH
        else:
            return PowerState.NORMAL

    def update(
        self,
        risk_pct: float,
        severity: Optional[str] = None,
        emergency_trigger: bool = False,
        current_time: Optional[float] = None
    ) -> Tuple[PowerState, bool, str]:
        """
        Ingests a new risk reading and transitions the power state.

        Returns:
            (new_state, state_changed_bool, transition_reason_string)
        """
        now = current_time if current_time is not None else time.time()
        self.last_risk_pct = risk_pct
        self.last_severity = severity or "NORMAL"
        self.emergency_active = emergency_trigger

        target_state = self.evaluate_target_state(
            risk_pct=risk_pct,
            severity=severity,
            emergency_trigger=emergency_trigger
        )

        current_weight = STATE_PRIORITY[self.current_state]
        target_weight = STATE_PRIORITY[target_state]

        # 1. ESCALATION (Higher priority state -> Instant transition)
        if target_weight > current_weight:
            old_state = self.current_state
            self.current_state = target_state
            self.consecutive_normal_samples = 0
            self.last_escalation_time = now
            self.last_transition_time = now
            reason = f"Risk escalated to {risk_pct:.1f}% ({target_state.value}): {old_state.value} -> {target_state.value}"
            return self.current_state, True, reason

        # 2. EQUAL STATE (Maintains current level)
        if target_weight == current_weight:
            self.consecutive_normal_samples = 0
            return self.current_state, False, "State maintained"

        # 3. DE-ESCALATION (Target state is lower -> Hysteresis / Recovery protection)
        self.consecutive_normal_samples += 1
        time_since_escalation = now - self.last_escalation_time

        # Recovery requires BOTH consecutive low-risk samples AND stabilization time
        samples_ok = self.consecutive_normal_samples >= self.config.recovery_samples_required
        time_ok = time_since_escalation >= self.config.recovery_time_seconds

        if samples_ok and time_ok:
            # Step down one tier at a time for graceful recovery
            if self.current_state == PowerState.CRITICAL:
                next_state = PowerState.WARNING
            elif self.current_state == PowerState.WARNING:
                next_state = PowerState.WATCH
            else:
                next_state = PowerState.NORMAL

            old_state = self.current_state
            self.current_state = next_state
            self.consecutive_normal_samples = 0
            self.last_escalation_time = now
            self.last_transition_time = now
            reason = (
                f"Hysteresis recovery passed ({self.config.recovery_samples_required} samples, "
                f"{time_since_escalation:.1f}s stabilization): {old_state.value} -> {next_state.value}"
            )
            return self.current_state, True, reason
        else:
            reason = (
                f"De-escalation held by hysteresis: target={target_state.value}, "
                f"samples={self.consecutive_normal_samples}/{self.config.recovery_samples_required}, "
                f"time={time_since_escalation:.1f}s/{self.config.recovery_time_seconds}s"
            )
            return self.current_state, False, reason

    def to_dict(self) -> Dict[str, Any]:
        return {
            "node_id": self.node_id,
            "power_state": self.current_state.value,
            "telemetry_interval_s": self.get_telemetry_interval(),
            "gps_interval_s": self.get_gps_interval(),
            "emergency_active": self.emergency_active,
            "last_risk_pct": self.last_risk_pct,
            "last_severity": self.last_severity,
            "consecutive_normal_samples": self.consecutive_normal_samples,
            "last_transition_time": self.last_transition_time,
        }
