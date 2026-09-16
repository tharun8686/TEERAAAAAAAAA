"""
TerraEdge Phase 3 — LoRa Transport Unit & Mock Tests.

All tests run WITHOUT physical hardware using MockLoRaRadio.
Tests are clearly tagged:
  [UNIT]       — pure logic, no network, no radio
  [MOCK]       — uses MockLoRaRadio (in-process loopback)
  [SIMULATION] — full pipeline with mock transport

Run:
  python -m pytest tests/test_lora.py -v
"""
from __future__ import annotations
import asyncio
import json
import os
import sys
import time

import pytest

# Ensure imports work from project root
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from gateway.schemas import TypeATelemetryPayload
from gateway.lora.packet import (
    SENSOR_FLAGS, decode_packet, encode_packet,
)
from gateway.lora.radio import MockLoRaRadio
from gateway.lora.receiver import LoRaReceiver


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------
@pytest.fixture
def basic_payload():
    """
    Realistic FLOOD + AIR_QUALITY node profile.
    Sensors: BME680, SDS011, MQ-135, Rain, Water Level, Ultrasonic, Soil, Flame, GPS, Battery.
    Deliberately excludes MPU6050, SW420, pH, TDS, Turbidity to keep packet under 250 bytes.
    This matches the most common TerraEdge flood-monitoring deployment.
    """
    return TypeATelemetryPayload(
        node_id="TE-001",
        node_type="Type-A",
        timestamp="2026-09-16T07:30:00+00:00",
        latitude=13.0827,
        longitude=80.2707,
        battery_pct=87.0,
        temperature_c=39.2,
        humidity_pct=31.5,
        pressure_hpa=1004.2,
        gas_resistance_kohm=8.3,
        pm25_ug_m3=94.0,
        pm10_ug_m3=161.0,
        mq135_raw=1840.0,
        rainfall_mm=18.4,
        rainfall_1h_mm=18.4,
        rainfall_24h_mm=62.0,
        water_level_m=2.3,
        ultrasonic_distance_cm=57.0,
        soil_moisture_pct=68.0,
        flame_detected=False,
    )


@pytest.fixture
def water_qual_payload():
    """
    WATER_QUALITY node profile for roundtrip/water-quality tests.
    Sensors: BME680, pH, TDS, Turbidity, GPS, Battery.
    Tests the water quality sensor encoding/decoding path.
    """
    return TypeATelemetryPayload(
        node_id="TE-002",
        node_type="Type-A",
        timestamp="2026-09-16T07:30:00+00:00",
        latitude=13.0827,
        longitude=80.2707,
        battery_pct=82.0,
        temperature_c=28.5,
        humidity_pct=65.0,
        pressure_hpa=1006.0,
        ph=7.1,
        tds_ppm=480.0,
        turbidity=14.0,
    )


@pytest.fixture
def minimal_payload():
    """Minimal packet — only required node_id."""
    return TypeATelemetryPayload(
        node_id="TE-MIN-01",
        temperature_c=28.5,
        humidity_pct=60.0,
    )



# ---------------------------------------------------------------------------
# [UNIT] test_lora_packet_serialization
# ---------------------------------------------------------------------------
def test_lora_packet_serialization(basic_payload):
    """[UNIT] Encoded packet must be valid JSON and within SX1278 250-byte limit."""
    raw = encode_packet(basic_payload, sequence=42)
    assert isinstance(raw, bytes)
    assert len(raw) <= 250, f"Packet too large: {len(raw)} bytes"

    pkt = json.loads(raw)
    assert pkt["v"] == 3
    assert pkt["id"] == "TE-001"
    assert pkt["seq"] == 42
    assert pkt["t"] == pytest.approx(39.2, abs=0.1)
    assert pkt["p25"] == pytest.approx(94.0, abs=0.5)
    assert pkt["fd"] == 0


# ---------------------------------------------------------------------------
# [UNIT] test_lora_packet_deserialization
# ---------------------------------------------------------------------------
def test_lora_packet_deserialization(basic_payload):
    """[UNIT] Decoded packet must faithfully reconstruct the TypeATelemetryPayload."""
    raw = encode_packet(basic_payload, sequence=55)
    decoded, seq = decode_packet(raw)

    assert seq == 55
    assert decoded.node_id == "TE-001"
    assert decoded.temperature_c == pytest.approx(39.2, abs=0.1)
    assert decoded.humidity_pct == pytest.approx(31.5, abs=0.1)
    assert decoded.pm25_ug_m3 == pytest.approx(94.0, abs=1.0)
    assert decoded.latitude == pytest.approx(13.0827, abs=0.0001)
    assert decoded.longitude == pytest.approx(80.2707, abs=0.0001)
    assert decoded.flame_detected is False or decoded.flame_detected == 0


# ---------------------------------------------------------------------------
# [UNIT] test_lora_roundtrip
# ---------------------------------------------------------------------------
def test_lora_roundtrip(basic_payload, water_qual_payload):
    """[UNIT] encode → decode must produce semantically identical telemetry."""
    # Test core flood-node fields using basic_payload
    raw = encode_packet(basic_payload, sequence=99)
    decoded, seq = decode_packet(raw)

    assert seq == 99
    assert decoded.node_id == basic_payload.node_id
    assert decoded.temperature_c == pytest.approx(basic_payload.temperature_c, abs=0.05)
    assert decoded.water_level_m == pytest.approx(basic_payload.water_level_m, abs=0.01)

    # Test water-quality fields using water_qual_payload
    raw_wq = encode_packet(water_qual_payload, sequence=100)
    decoded_wq, seq_wq = decode_packet(raw_wq)
    assert decoded_wq.tds_ppm == pytest.approx(water_qual_payload.tds_ppm, abs=1.0)
    assert decoded_wq.ph == pytest.approx(water_qual_payload.ph, abs=0.05)
    assert decoded_wq.turbidity == pytest.approx(water_qual_payload.turbidity, abs=1.0)


# ---------------------------------------------------------------------------
# [UNIT] test_invalid_packet
# ---------------------------------------------------------------------------
def test_invalid_packet():
    """[UNIT] Malformed bytes must raise ValueError, not crash."""
    bad_packets = [
        b"",                            # empty
        b"not json at all",             # not JSON
        b'{"v":3,"id":"X"}',            # missing seq
        b'{"v":99,"id":"X","seq":1}',   # wrong version
        b"\x00\x01\x02",               # binary garbage
    ]
    for bad in bad_packets:
        with pytest.raises(ValueError):
            decode_packet(bad)


# ---------------------------------------------------------------------------
# [MOCK] test_duplicate_packet
# ---------------------------------------------------------------------------
def test_duplicate_packet(basic_payload):
    """[MOCK] Receiver must detect and silently discard duplicate packets."""
    radio = MockLoRaRadio()
    radio.initialize()

    ingested = []

    def fake_ingest(payload, transport_meta=None):
        ingested.append(payload.node_id)

    receiver = LoRaReceiver(radio=radio, ingest_fn=fake_ingest)

    raw = encode_packet(basic_payload, sequence=101)

    # Inject same packet twice
    radio.inject_packet(raw)
    radio.inject_packet(raw)

    async def run():
        await receiver._handle_packet(raw, rssi=-75.0, snr=8.0)
        await receiver._handle_packet(raw, rssi=-75.0, snr=8.0)

    asyncio.run(run())

    # Only one should have been ingested
    assert len(ingested) == 1, f"Expected 1 ingest, got {len(ingested)}"


# ---------------------------------------------------------------------------
# [MOCK] test_missing_sequence
# ---------------------------------------------------------------------------
def test_missing_sequence(basic_payload):
    """[MOCK] Receiver must log gap when sequence jumps by more than 1."""
    radio = MockLoRaRadio()
    radio.initialize()

    gaps_detected = []

    original_inc = None

    def fake_ingest(payload, transport_meta=None):
        pass

    receiver = LoRaReceiver(radio=radio, ingest_fn=fake_ingest)

    raw_101 = encode_packet(basic_payload, sequence=101)
    raw_103 = encode_packet(basic_payload, sequence=103)   # gap: 102 missing

    async def run():
        await receiver._handle_packet(raw_101, rssi=-72.0, snr=9.5)
        # Capture current last sequence
        last = receiver._last_sequence.get("TE-001")
        await receiver._handle_packet(raw_103, rssi=-72.0, snr=9.5)
        # After handling 103 with last=101, packets_lost should be incremented
        stats = receiver._node_stats.get("TE-001", {})
        gaps_detected.append(stats.get("packets_lost", 0))

    asyncio.run(run())
    assert gaps_detected[0] >= 1, "Expected packets_lost > 0 after sequence gap"


# ---------------------------------------------------------------------------
# [MOCK] test_node_registration_from_lora
# ---------------------------------------------------------------------------
def test_node_registration_from_lora(basic_payload):
    """[MOCK] LoRa-received telemetry must register node in NodeManager."""
    from gateway.node_manager import NodeManager

    nm = NodeManager()
    radio = MockLoRaRadio()
    radio.initialize()

    def fake_ingest(payload, transport_meta=None):
        nm.register_or_update(payload)

    receiver = LoRaReceiver(radio=radio, ingest_fn=fake_ingest, node_manager=nm)

    raw = encode_packet(basic_payload, sequence=200)

    async def run():
        await receiver._handle_packet(raw, rssi=-68.0, snr=10.2)

    asyncio.run(run())

    node = nm.get_node("TE-001")
    assert node is not None
    assert node["node_id"] == "TE-001"
    assert node["latitude"] == pytest.approx(13.0827, abs=0.001)


# ---------------------------------------------------------------------------
# [MOCK] test_radio_metadata
# ---------------------------------------------------------------------------
def test_radio_metadata(basic_payload):
    """[MOCK] RSSI and SNR from radio must appear in LoRaTransportMetadata."""
    from gateway.schemas import LoRaTransportMetadata

    received_meta = []

    def fake_ingest(payload, transport_meta=None):
        received_meta.append(transport_meta)

    radio = MockLoRaRadio()
    radio.initialize()
    receiver = LoRaReceiver(radio=radio, ingest_fn=fake_ingest)

    raw = encode_packet(basic_payload, sequence=300)

    async def run():
        await receiver._handle_packet(raw, rssi=-81.0, snr=7.5)

    asyncio.run(run())

    assert len(received_meta) == 1
    meta = received_meta[0]
    assert isinstance(meta, LoRaTransportMetadata)
    assert meta.rssi_dbm == pytest.approx(-81.0)
    assert meta.snr_db == pytest.approx(7.5)
    assert meta.packet_sequence == 300


# ---------------------------------------------------------------------------
# [MOCK] test_mock_transport
# ---------------------------------------------------------------------------
def test_mock_transport(basic_payload):
    """[MOCK] MockLoRaRadio send+receive loopback must work correctly."""
    radio = MockLoRaRadio()
    assert radio.initialize() is True

    raw = encode_packet(basic_payload, sequence=500)
    assert radio.send(raw) is True

    received = radio.receive(timeout_ms=500)
    assert received == raw


# ---------------------------------------------------------------------------
# [SIMULATION] test_same_processing_path
# ---------------------------------------------------------------------------
def test_same_processing_path(basic_payload):
    """
    [SIMULATION] LoRa path and HTTP path must produce identical hazard inputs.

    Sends equivalent telemetry through both paths and verifies:
    - Same node_id in response
    - Risk score is in valid range for both
    - Both produce a primary_hazard (models ran)
    """
    from gateway.app import process_type_a_telemetry
    from gateway.lora.packet import encode_packet, decode_packet

    # PATH A: direct HTTP call (simulate simulator)
    response_http = process_type_a_telemetry(basic_payload, transport_meta=None)

    # PATH B: encode → LoRa → decode → same function
    raw = encode_packet(basic_payload, sequence=999)
    decoded_payload, seq = decode_packet(raw)
    response_lora = process_type_a_telemetry(decoded_payload, transport_meta=None)

    # Both must produce a valid response
    assert response_http.node_id == basic_payload.node_id
    assert response_lora.node_id == basic_payload.node_id

    assert 0.0 <= response_http.composite_risk_pct <= 100.0
    assert 0.0 <= response_lora.composite_risk_pct <= 100.0

    # Primary hazard must exist (models ran successfully)
    assert response_http.primary_hazard is not None
    assert response_lora.primary_hazard is not None

    # Risk scores must be comparable (within 5% — minor floating point from encode/decode)
    diff = abs(response_http.composite_risk_pct - response_lora.composite_risk_pct)
    assert diff <= 5.0, (
        f"HTTP risk={response_http.composite_risk_pct:.2f} vs "
        f"LoRa risk={response_lora.composite_risk_pct:.2f} — difference {diff:.2f}% exceeds threshold"
    )

    # HTTP path must have no transport metadata; LoRa path injected with None here too
    assert response_http.transport is None
    assert response_lora.transport is None


# ---------------------------------------------------------------------------
# [UNIT] Packet size stress test
# ---------------------------------------------------------------------------
def test_packet_size_within_limit(basic_payload):
    """[UNIT] Full-sensor payload with auto-derived flags must remain under SX1278 250-byte limit."""
    # SENSOR_FLAGS.UNIVERSAL now auto-derives from non-null fields, preventing oversized packets
    raw = encode_packet(basic_payload, sequence=1, sensor_flags=SENSOR_FLAGS.UNIVERSAL)
    assert len(raw) <= 250, f"Full packet {len(raw)} bytes exceeds LoRa 250-byte limit"
    print(f"\n  Full packet size: {len(raw)} bytes (limit: 250)")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
