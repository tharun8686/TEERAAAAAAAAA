"""Transport and model-unit regressions; no real sensors or external services."""
import json
from datetime import datetime, timezone
import pytest
from gateway.hardware_ingest import FrameAssembler, decode_envelope
from gateway.schemas import TypeATelemetryPayload
from gateway.live_models import LiveModels


def envelope(data, part=0, last=True, seq=1, boot=42, node="TEST-HW"):
    raw = json.dumps(dict(v=4, id=node, boot=boot, seq=seq, up=5000,
                         part=part, last=last, d=data), separators=(",", ":")).encode()
    assert len(raw) <= 250
    return dict(type="RX", data=raw.hex(), size=len(raw), rssi=-82, snr=7.25)


def test_round_trip_out_of_order_missing_and_duplicate():
    assembler = FrameAssembler()
    a = envelope({"t": 0, "h": 51.123456, "p": 1007.52}, last=False)
    b = envelope({"fd": 0, "lat": 13.082712, "lon": 80.270745, "rain_adc": 3050}, part=1)
    assert assembler.accept(b)[0] == "pending"
    state, raw, identity = assembler.accept(a)
    assert state == "complete"
    assert raw["temperature_c"] == 0
    assert raw["humidity_pct"] == 51.123456
    assert raw["latitude"] == 13.082712
    assert raw["flame_detected"] == 0
    assert raw["sensor_diagnostics"]["rain_adc"] == 3050
    assert "rainfall_mm" not in raw and "timestamp" not in raw
    assert TypeATelemetryPayload(**raw).timestamp.startswith(str(datetime.now().year))
    assembler.commit(identity)
    assert assembler.accept(a)[0] == "duplicate"
    assert assembler.accept(envelope({"t": 20}, boot=43))[0] == "complete"


@pytest.mark.parametrize("packet", [{"type":"READY"},{"type":"SCORES"},{"type":"ERROR"}])
def test_diagnostics_never_become_measurements(packet):
    assert decode_envelope(packet) is None


def test_invalid_size_nonfinite_conflicts_and_timeout():
    timer = [0]
    assembler = FrameAssembler(clock=lambda: timer[0])
    bad = envelope({"t": 12})
    bad["size"] += 1
    with pytest.raises(ValueError): assembler.accept(bad)
    with pytest.raises(ValueError): assembler.accept(envelope({"t": float('nan')}))
    assembler.accept(envelope({"t": 12}, last=False))
    with pytest.raises(ValueError): assembler.accept(envelope({"t": 13}, last=False))
    timer[0] = 21
    assert assembler.accept(envelope({"h": 50}, part=1))[0] == "pending"


def test_units_and_real_history_for_landslide():
    adapter = LiveModels()
    row = dict(soil_moisture_pct=42, tilt_magnitude=10, vibration_rate=30,
               temperature_c=25, humidity_pct=80, rainfall_24h_mm=12, _time=900)
    prev = dict(row, soil_moisture_pct=40, tilt_magnitude=8, _time=0)
    features, _ = adapter.build("Landslide", row, [], {"quarter":[prev]})
    assert features["soil_moisture_vwc"] == .42
    assert features["soil_moisture_rate"] == .02
    assert features["tilt_rate"] == 2
    with pytest.raises(ValueError, match="15-minute"):
        adapter.build("Landslide", dict(row, _time=5), [], {"quarter":[prev]})


def test_mq135_cannot_be_used_as_trained_air_gas_proxy():
    row = dict(pm25_ug_m3=40, pm10_ug_m3=60, temperature_c=30,
               humidity_pct=60, pressure_hpa=1010, mq135_raw=150)
    with pytest.raises(ValueError, match="co_mg_m3"):
        LiveModels().build("Air Quality", row, [], {})


def test_water_features_match_training_and_zero_values():
    row = dict(ph=7, turbidity=0, electrical_conductivity=0, tds_ppm=0,
               dissolved_oxygen=8, water_temperature_c=0)
    frame, _ = LiveModels().build("Water Quality", row, [], {})
    assert frame.iloc[0]["temperature_c"] == 0
    assert frame.iloc[0]["oxygen_drop_score"] == 0
    assert frame.iloc[0]["conductivity_shift_score"] == 0
    assert frame.iloc[0]["rolling_std_DO"] == 0
    with pytest.raises(ValueError, match="water_temperature_c"):
        LiveModels().build("Water Quality", dict(row, water_temperature_c=None, temperature_c=25), [], {})


def test_gateway_complete_frame_to_live_dashboard(monkeypatch):
    import gateway.app as gateway
    from gateway.hardware_ingest import assembler
    from fastapi.testclient import TestClient
    # No outgoing notifications or remote database calls in an integration test.
    monkeypatch.setattr(gateway.alert_dispatcher, "dispatch", lambda **kwargs: None)
    assembler.pending.clear()
    assembler.completed.clear()
    assembler.latest_sequence.clear()
    client = TestClient(gateway.app)
    first = client.post('/api/hardware', json=envelope({"t": 28.123456, "h": 61.5, "m7": 1234, "m7_mv": 987}, last=False))
    assert first.status_code == 200 and first.json()["status"] == "pending"
    final = client.post('/api/hardware', json=envelope({"fd": 1, "ph_mv": 2311}, part=1))
    assert final.status_code == 200, final.text
    evaluation = final.json()["evaluation"]
    assert evaluation["raw_telemetry"]["temperature_c"] == 28.123456
    assert evaluation["raw_telemetry"]["mq7_raw"] == 1234
    assert evaluation["raw_telemetry"]["mq135_raw"] is None
    assert evaluation["raw_telemetry"]["co_mg_m3"] is None
    assert evaluation["raw_telemetry"]["sensor_diagnostics"]["m7_mv"] == 987
    assert evaluation["raw_telemetry"]["ph"] is None
    assert evaluation["primary_severity"] == "UNKNOWN"
    assert all(r["model_status"] == "skipped" for r in evaluation["hazard_results"].values())
    assert evaluation["alerts_triggered"][0]["details"]["source"] == "direct_sensor"
    assert client.post('/api/hardware', json=envelope({"fd": 1, "ph_mv": 2311}, part=1)).json()["status"] == "duplicate"
    feed = client.get('/api/hardware/latest').json()
    assert any(n["node_id"] == "TEST-HW" for n in feed["nodes"])
    assert feed["units"]["pressure_hpa"] == "hPa"
    assert client.get('/live').status_code == 200


def test_serial_bridge_ignores_non_rx(monkeypatch):
    import lora_serial_bridge as bridge
    monkeypatch.setattr(bridge.urllib.request, 'urlopen', lambda *args, **kwargs: pytest.fail('Unexpected HTTP request'))
    assert bridge.forward_to_gateway({'type':'READY'}) is None
    assert bridge.forward_to_gateway({'type':'SCORES'}) is None


def test_late_frames_do_not_overwrite_newer_measurements():
    assembler = FrameAssembler()
    _, _, identity = assembler.accept(envelope({"t": 30}, seq=10))
    assembler.commit(identity)
    assert assembler.accept(envelope({"t": 20}, seq=9))[0] == "duplicate"
    assert assembler.accept(envelope({"t": 31}, seq=11))[0] == "complete"


def test_heat_hourly_features_and_gap_rejection():
    from collections import deque
    adapter = LiveModels()
    row = dict(temperature_c=36, humidity_pct=50, solar_radiation_w_m2=400,
               wind_speed_kmh=4, rainfall_1h_mm=0)
    hours = [dict(row, _complete=True, _slot=i) for i in range(72)]
    features, method = adapter.build("Extreme Heat", row, [], {"hour": hours})
    assert method == "predict_heat_risk"
    assert features.iloc[0]["cumulative_hot_hours"] == 72
    assert features.iloc[0]["nighttime_cooling_deficit"] == 8
    assert features.iloc[0]["rolling_std_temperature"] == 0
    hours[10]["_complete"] = False
    with pytest.raises(ValueError, match="72 complete"):
        adapter.build("Extreme Heat", row, [], {"hour": hours})
    history = {"hour": deque(maxlen=72)}
    adapter.accumulate_hour(dict(row, _time=-19800), history)
    adapter.accumulate_hour(dict(row, _time=-19800+3600), history)
    assert history["hour"][0]["_complete"] is False


def test_real_model_execution_with_complete_water_inputs():
    from gateway.hazard_router import hazard_router
    adapter = LiveModels()
    payload = TypeATelemetryPayload(node_id="TEST-COMPLETE-WATER", ph=7, turbidity=2,
        electrical_conductivity=280, tds_ppm=180, dissolved_oxygen=8, water_temperature_c=24)
    results = adapter.evaluate(payload, hazard_router)
    water = results["Water Quality"]
    assert water.model_status == "success", water.error
    assert 0 <= water.risk_pct <= 100
    assert water.confidence_pct == water.details["confidence"] * 100
    assert "heuristic" in water.details["confidence_basis"]


def test_builtin_lora_receiver_accepts_v4(monkeypatch):
    import asyncio
    from gateway.lora.receiver import LoRaReceiver
    from gateway.hardware_ingest import assembler
    accepted = []
    receiver = LoRaReceiver(radio=None, ingest_fn=lambda payload, meta: accepted.append(payload))
    message = envelope({"t": 19.25, "fd": 0}, node="TEST-BUILTIN")
    assembler.latest_sequence.clear()
    assembler.completed.clear()
    asyncio.run(receiver._handle_packet(bytes.fromhex(message['data']), -80, 9))
    assert len(accepted) == 1
    assert accepted[0].temperature_c == 19.25


@pytest.mark.parametrize("value", [0, 4095])
def test_mq7_preserves_adc_boundaries_without_gas_conversion(value):
    _, raw, _ = FrameAssembler().accept(envelope({"m7": value, "m7_mv": 1200}))
    payload = TypeATelemetryPayload(**raw)
    assert payload.mq7_raw == value
    assert payload.mq135_raw is None and payload.co_mg_m3 is None
    assert raw["sensor_diagnostics"]["m7_mv"] == 1200
    with pytest.raises(ValueError, match="co_mg_m3"):
        LiveModels().build("Air Quality", dict(pm25_ug_m3=40, pm10_ug_m3=60,
            temperature_c=30, humidity_pct=60, pressure_hpa=1010, mq7_raw=value), [], {})


@pytest.mark.parametrize("data", [{"m7": 4096}, {"m7": -1}, {"m7_mv": 3301}])
def test_mq7_rejects_invalid_adc_data(data):
    with pytest.raises(ValueError):
        FrameAssembler().accept(envelope(data))
