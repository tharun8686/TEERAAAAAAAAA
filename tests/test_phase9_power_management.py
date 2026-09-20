"""
TerraEdge Phase 9 — Comprehensive Autonomous Power Management & Duty-Cycle Test Suite.
Verifies power states, transition logic, hysteresis recovery, emergency wake-up,
sensor power policies, warm-up scheduling, solar/MPPT model, power budgeting,
autonomy estimation, API overrides, backwards compatibility, and non-regression.
"""

import os
import sys
import time
import pytest
from fastapi.testclient import TestClient

HERE = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(HERE)
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)
COMMON_DIR = os.path.join(PROJECT_ROOT, "common")
if COMMON_DIR not in sys.path:
    sys.path.insert(0, COMMON_DIR)

from gateway.app import app
from gateway.config import ADMIN_TOKEN, OPERATOR_TOKEN
from gateway.node_manager import node_manager
from gateway.power import (
    DEFAULT_POWER_CONFIG,
    NodePowerStateMachine,
    PowerBudgetEngine,
    PowerConfig,
    PowerState,
    SENSOR_POLICIES,
    SensorWarmupScheduler,
    SolarTelemetryModel,
    check_emergency_conditions,
    classify_battery_state,
    estimate_soc_from_voltage,
    estimate_voltage_from_soc,
    get_transmission_profile,
    prepare_emergency_telemetry,
)
from gateway.lora.packet import encode_packet, decode_packet, SENSOR_FLAGS
from gateway.schemas import (
    PowerProfileUpdateRequest,
    TypeATelemetryPayload,
    UnifiedGatewayResponse,
)
from gateway.simulator import (
    generate_healthy_solar_packet,
    generate_cloudy_solar_packet,
    generate_flood_escalation_packet,
    generate_wildfire_emergency_packet,
    generate_landslide_precursor_packet,
    generate_battery_depletion_packet,
    generate_recovery_packet,
)


@pytest.fixture
def client():
    return TestClient(app)


# ---------------------------------------------------------------------------
# 1. Power State Transitions & Escalation
# ---------------------------------------------------------------------------
def test_power_state_transitions():
    """State machine deterministically escalates based on risk thresholds."""
    sm = NodePowerStateMachine(node_id="TEST-NODE-01")
    assert sm.current_state == PowerState.NORMAL

    # Normal risk (< 40%)
    state, changed, _ = sm.update(risk_pct=25.0)
    assert state == PowerState.NORMAL
    assert not changed

    # Watch threshold (>= 40%)
    state, changed, _ = sm.update(risk_pct=45.0)
    assert state == PowerState.WATCH
    assert changed

    # Warning threshold (>= 60%)
    state, changed, _ = sm.update(risk_pct=65.0)
    assert state == PowerState.WARNING
    assert changed

    # Critical threshold (>= 80%)
    state, changed, _ = sm.update(risk_pct=85.0)
    assert state == PowerState.CRITICAL
    assert changed


# ---------------------------------------------------------------------------
# 2. Hysteresis & Recovery Protection
# ---------------------------------------------------------------------------
def test_hysteresis_recovery():
    """Single low reading does NOT instantly de-escalate; requires stabilization time & consecutive samples."""
    cfg = PowerConfig(recovery_samples_required=3, recovery_time_seconds=10.0)
    sm = NodePowerStateMachine(node_id="TEST-NODE-02", config=cfg)

    # Escalate to CRITICAL
    t0 = 1000.0
    sm.update(risk_pct=85.0, current_time=t0)
    assert sm.current_state == PowerState.CRITICAL

    # First lower reading immediately after: held by hysteresis
    state, changed, reason = sm.update(risk_pct=20.0, current_time=t0 + 1.0)
    assert state == PowerState.CRITICAL
    assert not changed
    assert "held by hysteresis" in reason

    # Second lower reading before recovery time: still held
    state, changed, _ = sm.update(risk_pct=20.0, current_time=t0 + 5.0)
    assert state == PowerState.CRITICAL
    assert not changed

    # Third lower reading AFTER recovery time (15s > 10s): steps down gracefully to WARNING
    state, changed, reason = sm.update(risk_pct=20.0, current_time=t0 + 15.0)
    assert state == PowerState.WARNING
    assert changed
    assert "Hysteresis recovery passed" in reason


# ---------------------------------------------------------------------------
# 3. Telemetry Interval Selection
# ---------------------------------------------------------------------------
def test_telemetry_interval_selection():
    """Telemetry intervals adhere to authoritative configuration."""
    sm = NodePowerStateMachine(node_id="TEST-NODE-03")
    sm.current_state = PowerState.NORMAL
    assert sm.get_telemetry_interval() == 300

    sm.current_state = PowerState.WATCH
    assert sm.get_telemetry_interval() == 60

    sm.current_state = PowerState.WARNING
    assert sm.get_telemetry_interval() == 30

    sm.current_state = PowerState.CRITICAL
    assert sm.get_telemetry_interval() == 10


# ---------------------------------------------------------------------------
# 4. Local Emergency Wake-up Triggers
# ---------------------------------------------------------------------------
def test_emergency_wakeup():
    """Emergency conditions (flame, water surge, vibration, tilt) trigger immediate CRITICAL."""
    # 1. Flame detection
    p_flame = {"node_id": "TEST-EMERG", "flame_detected": True}
    is_emerg, reasons = check_emergency_conditions(p_flame)
    assert is_emerg
    assert any("flame" in r.lower() for r in reasons)

    # 2. Water level threshold
    p_flood = {"node_id": "TEST-EMERG", "water_level_m": 4.2}
    is_emerg, reasons = check_emergency_conditions(p_flood)
    assert is_emerg
    assert any("water" in r.lower() for r in reasons)

    # 3. Vibration pulse rate
    p_vib = {"node_id": "TEST-EMERG", "vibration_rate": 75.0}
    is_emerg, reasons = check_emergency_conditions(p_vib)
    assert is_emerg
    assert any("vibration" in r.lower() for r in reasons)

    # 4. Tilt inclination
    p_tilt = {"node_id": "TEST-EMERG", "tilt_magnitude": 30.0}
    is_emerg, reasons = check_emergency_conditions(p_tilt)
    assert is_emerg
    assert any("tilt" in r.lower() for r in reasons)

    # 5. Snapshot preparation
    emerg_pkt = prepare_emergency_telemetry(p_flame, reasons)
    assert emerg_pkt["telemetry_priority"] == "EMERGENCY"
    assert emerg_pkt["power_mode"] == "CRITICAL"
    assert emerg_pkt["emergency_state"] is True
    assert emerg_pkt["telemetry_interval_s"] == 10


# ---------------------------------------------------------------------------
# 5. Battery Thresholds & Estimation
# ---------------------------------------------------------------------------
def test_battery_thresholds():
    """Battery voltages accurately map to SOC% and discrete states."""
    # 4.2V -> 100%
    assert estimate_soc_from_voltage(4.20) == 100.0
    # 3.7V nominal -> ~40%
    assert 35.0 <= estimate_soc_from_voltage(3.70) <= 45.0
    # 3.0V -> 0%
    assert estimate_soc_from_voltage(3.00) == 0.0

    # Classifications
    assert classify_battery_state(soc_pct=98.0, charging=True) == "FULL"
    assert classify_battery_state(soc_pct=60.0, charging=True) == "CHARGING"
    assert classify_battery_state(soc_pct=60.0, charging=False) == "DISCHARGING"
    assert classify_battery_state(soc_pct=20.0, charging=False) == "LOW"
    assert classify_battery_state(soc_pct=8.0, charging=False) == "CRITICAL"


# ---------------------------------------------------------------------------
# 6. Low Battery Protection Behavior
# ---------------------------------------------------------------------------
def test_low_battery_behavior():
    """Under CRITICAL battery state, nonessential sensors are disabled and vital emergency triggers preserved."""
    profile_crit = get_transmission_profile(power_state="NORMAL", battery_state="CRITICAL")
    # Only emergency priority 1 sensors allowed
    allowed = profile_crit.sensor_sample_profile
    assert "flame" in allowed
    assert "sw420" in allowed
    assert "water_level" in allowed
    assert "sds011" not in allowed
    assert "mq135" not in allowed
    assert "ph" not in allowed
    # Interval stretched to preserve remaining cell charge
    assert profile_crit.telemetry_interval_s >= 60


# ---------------------------------------------------------------------------
# 7. Sensor Duty-Cycling Policies
# ---------------------------------------------------------------------------
def test_sensor_duty_cycling():
    """Metadata policies define warm-up, active current, and sleep current for all sensors."""
    assert "sds011" in SENSOR_POLICIES
    assert "bme680" in SENSOR_POLICIES
    assert "mq135" in SENSOR_POLICIES

    sds = SENSOR_POLICIES["sds011"]
    assert sds.warmup_ms == 10000
    assert sds.active_power_estimate_ma == 80.0
    assert sds.duty_cycle_allowed is True

    flame = SENSOR_POLICIES["flame"]
    assert flame.always_on is True
    assert flame.emergency_priority == 1


# ---------------------------------------------------------------------------
# 8. Sensor Warm-up Scheduling
# ---------------------------------------------------------------------------
def test_warmup_scheduling():
    """Non-blocking warm-up scheduler correctly identifies when warm-up has elapsed."""
    scheduler = SensorWarmupScheduler()
    t0 = 100.0

    scheduler.power_on_sensor("bme680", timestamp=t0)
    assert scheduler.is_powered("bme680")
    # 500ms elapsed (< 1000ms warm-up) -> Not ready
    assert not scheduler.is_warmed_up("bme680", current_time=t0 + 0.5)
    # 1200ms elapsed (>= 1000ms warm-up) -> Ready
    assert scheduler.is_warmed_up("bme680", current_time=t0 + 1.2)

    scheduler.power_off_sensor("bme680")
    assert not scheduler.is_powered("bme680")


# ---------------------------------------------------------------------------
# 9. GPS Scheduling
# ---------------------------------------------------------------------------
def test_gps_scheduling():
    """GPS duty-cycling interval adapts to power state."""
    sm = NodePowerStateMachine(node_id="TEST-GPS")
    sm.current_state = PowerState.NORMAL
    assert sm.get_gps_interval() == 3600  # 1 hr in normal

    sm.current_state = PowerState.CRITICAL
    assert sm.get_gps_interval() == 30    # 30s in critical


# ---------------------------------------------------------------------------
# 10. Power Budget Calculation
# ---------------------------------------------------------------------------
def test_power_budget_calculation():
    """Power budget calculates time-weighted average current and daily consumption."""
    engine = PowerBudgetEngine()
    result = engine.calculate_budget(
        telemetry_interval_s=300,
        battery_soc_pct=90.0,
        battery_voltage_v=3.95,
        active_sensor_ids=["bme680", "rainfall", "flame"],
        average_sunlight_hours_per_day=5.0
    )

    assert result.estimated_average_current_ma > 0.0
    assert result.estimated_power_w > 0.0
    assert result.estimated_daily_energy_use_wh > 0.0
    assert result.estimated_daily_solar_input_wh > 0.0
    assert result.data_classification == "ESTIMATED"


# ---------------------------------------------------------------------------
# 11. Autonomy Estimation
# ---------------------------------------------------------------------------
def test_autonomy_estimation():
    """Autonomy hours scale inversely with sampling frequency and directly with battery capacity."""
    engine = PowerBudgetEngine()
    # High frequency (10s) vs Low frequency (300s)
    res_normal = engine.calculate_budget(telemetry_interval_s=300, battery_soc_pct=100.0)
    res_critical = engine.calculate_budget(telemetry_interval_s=10, battery_soc_pct=100.0)

    # Normal mode has longer battery autonomy than continuous critical mode
    assert res_normal.estimated_autonomy_hours > res_critical.estimated_autonomy_hours
    assert res_normal.estimated_autonomy_days > 1.0


# ---------------------------------------------------------------------------
# 12. Solar Telemetry Model
# ---------------------------------------------------------------------------
def test_solar_simulation():
    """Solar harvesting increases battery SOC in full sun and drops in darkness."""
    model = SolarTelemetryModel(current_soc_pct=50.0)

    # Full sun (factor 1.0)
    res_day = model.simulate_solar_harvest(sunlight_factor=1.0, node_load_ma=20.0, elapsed_seconds=3600.0)
    assert res_day["solar_available"] is True
    assert res_day["charging"] is True
    assert res_day["battery_soc_pct"] > 50.0

    # Night (factor 0.0)
    res_night = model.simulate_solar_harvest(sunlight_factor=0.0, node_load_ma=20.0, elapsed_seconds=3600.0)
    assert res_night["solar_available"] is False
    assert res_night["charging"] is False


# ---------------------------------------------------------------------------
# 13. LoRa Transmission Profile Selector
# ---------------------------------------------------------------------------
def test_lora_interval_selection():
    """Transmission profile selector yields valid retry and priority policies."""
    prof_norm = get_transmission_profile("NORMAL", "DISCHARGING", emergency_state=False)
    assert prof_norm.telemetry_interval_s == 300
    assert prof_norm.priority == "NORMAL"

    prof_crit = get_transmission_profile("CRITICAL", "DISCHARGING", emergency_state=False)
    assert prof_crit.telemetry_interval_s == 10
    assert prof_crit.priority == "HIGH"


# ---------------------------------------------------------------------------
# 14. Emergency LoRa Transmission Packet Compatibility
# ---------------------------------------------------------------------------
def test_emergency_lora_transmission():
    """Emergency telemetry is encoded into LoRa packet within the 250-byte FIFO limit."""
    payload = TypeATelemetryPayload(
        node_id="TE-EMERG-TX",
        power_mode="CRITICAL",
        battery_pct=88.0,
        battery_voltage_v=3.95,
        flame_detected=True,
        emergency_state=True,
        telemetry_priority="EMERGENCY",
        telemetry_interval_s=10,
        temperature_c=42.5,
        latitude=11.5034,
        longitude=77.2412,
    )

    raw_bytes = encode_packet(payload, sequence=42)
    assert len(raw_bytes) <= 250
    decoded_payload, seq = decode_packet(raw_bytes)

    assert seq == 42
    assert decoded_payload.node_id == "TE-EMERG-TX"
    assert decoded_payload.power_mode == "CRITICAL"
    assert decoded_payload.flame_detected is True
    assert decoded_payload.emergency_state is True
    assert decoded_payload.telemetry_priority == "EMERGENCY"


# ---------------------------------------------------------------------------
# 15. Remote Power Profile API Configuration & Authorization
# ---------------------------------------------------------------------------
def test_remote_power_profile_api(client):
    """Operators can remotely set node power profile; rejects invalid tokens."""
    # 1. Invalid token -> 401 Unauthorized
    resp = client.post(
        "/api/nodes/TE-001/power-profile",
        json={"mode": "WATCH"},
        headers={"X-API-Key": "invalid-token-xyz"}
    )
    assert resp.status_code == 401

    # 2. Authorized (Operator token) -> 200
    headers = {"Authorization": f"Bearer {OPERATOR_TOKEN}"}
    resp = client.post(
        "/api/nodes/TE-001/power-profile",
        json={"mode": "WATCH", "telemetry_interval_s": 45},
        headers=headers
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["status"] == "success"
    assert data["desired_power_profile"]["mode"] == "WATCH"

    # 3. GET power status reflects update
    resp_get = client.get("/api/nodes/TE-001/power")
    assert resp_get.status_code == 200
    p_data = resp_get.json()
    assert p_data["node_id"] == "TE-001"
    assert p_data["power_state"] == "WATCH"
    assert p_data["telemetry_interval_s"] == 45


# ---------------------------------------------------------------------------
# 16. Backwards-Compatible Telemetry Ingestion
# ---------------------------------------------------------------------------
def test_backwards_compatible_telemetry(client):
    """Legacy payloads without Phase 9 fields ingest cleanly with safe defaults."""
    legacy_payload = {
        "node_id": "LEGACY-NODE-01",
        "node_type": "Type-A",
        "temperature_c": 28.5,
        "humidity_pct": 65.0,
        "battery_pct": 91.0
    }
    resp = client.post("/api/telemetry", json=legacy_payload)
    assert resp.status_code == 200
    res = resp.json()
    assert res["node_id"] == "LEGACY-NODE-01"
    assert res["power_mode"] == "NORMAL"
    assert res["telemetry_priority"] == "NORMAL"


# ---------------------------------------------------------------------------
# 17. Simulator Scenarios (1 to 7)
# ---------------------------------------------------------------------------
def test_simulator_scenarios(client):
    """All 7 Phase 9 simulator scenarios generate valid payloads accepted by gateway."""
    generators = [
        ("healthy_solar", generate_healthy_solar_packet),
        ("cloudy_solar", generate_cloudy_solar_packet),
        ("flood_escalation", generate_flood_escalation_packet),
        ("wildfire_emergency", generate_wildfire_emergency_packet),
        ("landslide_precursor", generate_landslide_precursor_packet),
        ("battery_depletion", generate_battery_depletion_packet),
        ("recovery", generate_recovery_packet),
    ]

    for name, gen_fn in generators:
        pkt = gen_fn(node_id=f"SIM-{name[:4].upper()}", step=2)
        resp = client.post("/api/telemetry", json=pkt)
        assert resp.status_code == 200, f"Scenario {name} failed: {resp.text}"
        data = resp.json()
        assert "composite_risk_pct" in data
        assert "power_mode" in data


# ---------------------------------------------------------------------------
# 18. Multi-Node Isolated Power Profiles
# ---------------------------------------------------------------------------
def test_multi_node_power_profiles(client):
    """Distinct nodes maintain independent power states and intervals."""
    # Node A is in Flood CRITICAL
    pkt_a = generate_flood_escalation_packet(node_id="NODE-PWR-A", step=4)
    client.post("/api/telemetry", json=pkt_a)

    # Node B is in Healthy Solar NORMAL
    pkt_b = generate_healthy_solar_packet(node_id="NODE-PWR-B", step=1)
    client.post("/api/telemetry", json=pkt_b)

    resp_a = client.get("/api/nodes/NODE-PWR-A/power").json()
    resp_b = client.get("/api/nodes/NODE-PWR-B/power").json()

    assert resp_a["power_state"] == "CRITICAL"
    assert resp_a["telemetry_interval_s"] == 10
    assert resp_b["power_state"] == "NORMAL"
    assert resp_b["telemetry_interval_s"] == 300


# ---------------------------------------------------------------------------
# 19. Non-Regression: Hazard Models, Alerts, and CAP
# ---------------------------------------------------------------------------
def test_no_regression_hazard_and_alerts(client):
    """Inference engines, risk ranking, and alert dispatch operate without regression."""
    pkt = generate_wildfire_emergency_packet(node_id="REGRESS-01", step=1)
    resp = client.post("/api/telemetry", json=pkt)
    assert resp.status_code == 200
    data = resp.json()

    # Hazard inference succeeded
    assert data["composite_risk_pct"] > 50.0
    assert len(data["ranked_hazards"]) > 0
    # Alerts generated
    assert len(data["alerts_triggered"]) > 0

    # Verify CAP generation endpoint works
    alert_id = data["alerts_triggered"][0]["alert_id"]
    cap_resp = client.get(f"/api/alerts/{alert_id}/cap")
    assert cap_resp.status_code == 200
    assert "<alert" in cap_resp.text
