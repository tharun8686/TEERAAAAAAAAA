"""
TerraEdge Phase 3 — LoRa Packet Codec.

Packet format: compact JSON with short keys to stay within SX1278 FIFO limit.

The SX1278 FIFO is 256 bytes. The sandeepmistry/LoRa library supports up to 255 bytes.
We target MAX_PAYLOAD_BYTES = 250 (5-byte safety margin).

SENSOR-FLAG-GATED ENCODING:
Fields are only included when the corresponding sensor_flags bit is set.
A universal-node with all sensors fills ~272 bytes — too large for a single packet.
In practice, each deployed node only has a subset of sensors, keeping packets well within limit.
The encoder enforces this: only sensor_flags-enabled fields are serialized.

TIMESTAMP:
Unix epoch integer (10 bytes) instead of ISO-8601 string (30 bytes).
Decoded back to ISO on the gateway.

FIELD_MAP: short_key -> (canonical_schema_field, python_type, sensor_flag_bit or 0)
  flag=0 means always included regardless of sensor_flags.
SENSOR_FLAGS: bitmask definitions for the "sf" field.

Encoding: TypeATelemetryPayload + sensor_flags -> bytes (UTF-8 JSON)
Decoding: bytes -> (TypeATelemetryPayload, sequence_number: int)
"""
from __future__ import annotations
import calendar
import datetime
import json
import time as _time
from typing import Any, Dict, Optional, Tuple

# ---------------------------------------------------------------------------
# Sensor presence bitmask definitions
# ---------------------------------------------------------------------------
class SENSOR_FLAGS:
    BME680    = 1 << 0    # 0x0001
    SDS011    = 1 << 1    # 0x0002
    MQ135     = 1 << 2    # 0x0004
    RAIN      = 1 << 3    # 0x0008
    WATER     = 1 << 4    # 0x0010
    ULTRASONIC= 1 << 5    # 0x0020
    SOIL      = 1 << 6    # 0x0040
    MPU6050   = 1 << 7    # 0x0080
    SW420     = 1 << 8    # 0x0100
    FLAME     = 1 << 9    # 0x0200
    PH        = 1 << 10   # 0x0400
    TDS       = 1 << 11   # 0x0800
    TURBIDITY = 1 << 12   # 0x1000
    GPS       = 1 << 13   # 0x2000
    BATTERY   = 1 << 14   # 0x4000
    UNIVERSAL = 0x7FFF    # all 15 sensors
    # Common node profiles
    AIR_WILDFIRE = BME680 | SDS011 | MQ135 | FLAME | GPS | BATTERY
    FLOOD        = BME680 | RAIN | WATER | ULTRASONIC | SOIL | GPS | BATTERY
    WATER_QUAL   = BME680 | PH | TDS | TURBIDITY | GPS | BATTERY
    LANDSLIDE    = BME680 | RAIN | SOIL | MPU6050 | SW420 | GPS | BATTERY


# ---------------------------------------------------------------------------
# Field map: short_key -> (canonical_field_name, cast_type, sensor_flag_bit)
#   flag=0 means always included in every packet (metadata fields)
# ---------------------------------------------------------------------------
FIELD_MAP: Dict[str, Tuple[str, Any, int]] = {
    # Always included metadata (flag=0)
    "v":   ("_version",             int,   0),
    "id":  ("node_id",              str,   0),
    "seq": ("_sequence",            int,   0),
    "ts":  ("timestamp",            str,   0),   # epoch int in packet
    "sf":  ("_sensor_flags",        int,   0),
    "zt":  ("zone",                 str,   0),
    # GPS
    "lat": ("latitude",             float, SENSOR_FLAGS.GPS),
    "lon": ("longitude",            float, SENSOR_FLAGS.GPS),
    # Battery & Power (Phase 9)
    "bat": ("battery_pct",          float, SENSOR_FLAGS.BATTERY),
    "bv":  ("battery_voltage_v",    float, SENSOR_FLAGS.BATTERY),
    "pw":  ("power_mode",           str,   0),
    "ti":  ("telemetry_interval_s", int,   0),
    "tp":  ("telemetry_priority",   str,   0),
    "es":  ("emergency_state",      bool,  0),
    # BME680
    "t":   ("temperature_c",        float, SENSOR_FLAGS.BME680),
    "h":   ("humidity_pct",         float, SENSOR_FLAGS.BME680),
    "p":   ("pressure_hpa",         float, SENSOR_FLAGS.BME680),
    "gr":  ("gas_resistance_kohm",  float, SENSOR_FLAGS.BME680),
    # SDS011
    "p25": ("pm25_ug_m3",           float, SENSOR_FLAGS.SDS011),
    "p10": ("pm10_ug_m3",           float, SENSOR_FLAGS.SDS011),
    # MQ-135
    "mq":  ("mq135_raw",            float, SENSOR_FLAGS.MQ135),
    # Rain
    "rm":  ("rainfall_mm",          float, SENSOR_FLAGS.RAIN),
    "r1":  ("rainfall_1h_mm",       float, SENSOR_FLAGS.RAIN),
    "r3":  ("rainfall_3h_mm",       float, SENSOR_FLAGS.RAIN),
    "r6":  ("rainfall_6h_mm",       float, SENSOR_FLAGS.RAIN),
    "r24": ("rainfall_24h_mm",      float, SENSOR_FLAGS.RAIN),
    "r72": ("rainfall_72h_mm",      float, SENSOR_FLAGS.RAIN),
    # Water level / Ultrasonic
    "wl":  ("water_level_m",        float, SENSOR_FLAGS.WATER),
    "ud":  ("ultrasonic_distance_cm", float, SENSOR_FLAGS.ULTRASONIC),
    # Soil
    "sm":  ("soil_moisture_pct",    float, SENSOR_FLAGS.SOIL),
    # MPU6050
    "tm":  ("tilt_magnitude",       float, SENSOR_FLAGS.MPU6050),
    "tr":  ("tilt_rate",            float, SENSOR_FLAGS.MPU6050),
    # SW420
    "vr":  ("vibration_rate",       float, SENSOR_FLAGS.SW420),
    # IR Flame
    "fd":  ("flame_detected",       bool,  SENSOR_FLAGS.FLAME),
    # Water quality
    "ph":  ("ph",                   float, SENSOR_FLAGS.PH),
    "td":  ("tds_ppm",              float, SENSOR_FLAGS.TDS),
    "tb":  ("turbidity",            float, SENSOR_FLAGS.TURBIDITY),
}

# Reverse map: canonical -> short_key (for encoding)
_CANONICAL_TO_SHORT: Dict[str, str] = {v[0]: k for k, v in FIELD_MAP.items() if not v[0].startswith("_")}


# ---------------------------------------------------------------------------
# Encoder
# ---------------------------------------------------------------------------
def _derive_sensor_flags(payload) -> int:
    """
    Auto-derive a sensor_flags bitmask from which fields are actually non-null
    on the payload.  Used when the caller passes UNIVERSAL or None.

    This ensures the encoded packet only contains sensors that the node actually
    populated, keeping packet size within the SX1278 250-byte limit even when
    a payload object has been created with all fields filled in (e.g. in tests).
    """
    flags = 0
    if payload.latitude is not None or payload.longitude is not None:
        flags |= SENSOR_FLAGS.GPS
    if payload.battery_pct is not None or payload.battery_voltage_v is not None or payload.battery_soc_pct is not None:
        flags |= SENSOR_FLAGS.BATTERY
    if any(v is not None for v in [
        payload.temperature_c, payload.humidity_pct,
        payload.pressure_hpa, payload.gas_resistance_kohm
    ]):
        flags |= SENSOR_FLAGS.BME680
    if payload.pm25_ug_m3 is not None or payload.pm10_ug_m3 is not None:
        flags |= SENSOR_FLAGS.SDS011
    if payload.mq135_raw is not None:
        flags |= SENSOR_FLAGS.MQ135
    if any(v is not None for v in [
        payload.rainfall_mm, payload.rainfall_1h_mm, payload.rainfall_24h_mm
    ]):
        flags |= SENSOR_FLAGS.RAIN
    if payload.water_level_m is not None:
        flags |= SENSOR_FLAGS.WATER
    if payload.ultrasonic_distance_cm is not None:
        flags |= SENSOR_FLAGS.ULTRASONIC
    if payload.soil_moisture_pct is not None:
        flags |= SENSOR_FLAGS.SOIL
    if payload.tilt_magnitude is not None or payload.tilt_rate is not None:
        flags |= SENSOR_FLAGS.MPU6050
    if payload.vibration_rate is not None:
        flags |= SENSOR_FLAGS.SW420
    if payload.flame_detected is not None:
        flags |= SENSOR_FLAGS.FLAME
    if payload.ph is not None:
        flags |= SENSOR_FLAGS.PH
    if payload.tds_ppm is not None:
        flags |= SENSOR_FLAGS.TDS
    if payload.turbidity is not None:
        flags |= SENSOR_FLAGS.TURBIDITY
    return flags


def encode_packet(
    payload,                       # TypeATelemetryPayload
    sequence: int,
    sensor_flags: Optional[int] = None,
) -> bytes:
    """
    Serialize a TypeATelemetryPayload into a compact JSON byte string for LoRa TX.

    Only fields whose sensor_flag bit is SET are included.
    This ensures packets fit within the SX1278 250-byte FIFO limit.

    Args:
        payload: TypeATelemetryPayload instance
        sequence: monotonically increasing packet sequence number
        sensor_flags: bitmask of physically present sensors on this node.
            • Pass None (default) or SENSOR_FLAGS.UNIVERSAL to auto-derive
              flags from non-null fields, keeping packet size minimal.
            • Pass a specific profile (e.g. SENSOR_FLAGS.FLOOD) to explicitly
              restrict which sensors are encoded.

    Returns:
        UTF-8 encoded JSON bytes.

    Raises:
        ValueError if encoded size > MAX_PAYLOAD_BYTES even after flag-gating.
    """
    from .config import MAX_PAYLOAD_BYTES, PACKET_VERSION

    # Auto-derive flags when caller passes None or UNIVERSAL
    if sensor_flags is None or sensor_flags == SENSOR_FLAGS.UNIVERSAL:
        sensor_flags = _derive_sensor_flags(payload)
        # If still zero (completely empty payload), use UNIVERSAL so metadata is sent
        if sensor_flags == 0:
            sensor_flags = SENSOR_FLAGS.UNIVERSAL

    # Encode timestamp as Unix epoch integer (saves ~20 bytes vs ISO string)
    ts_str = payload.timestamp or _utc_now_iso()
    try:
        ts_clean = ts_str.replace("Z", "+00:00")
        dt_obj = datetime.datetime.fromisoformat(ts_clean)
        ts_epoch = int(calendar.timegm(dt_obj.utctimetuple()))
    except Exception:
        ts_epoch = int(_time.time())

    pkt: Dict[str, Any] = {
        "v":   PACKET_VERSION,
        "id":  payload.node_id,
        "seq": sequence,
        "ts":  ts_epoch,
        "sf":  sensor_flags,
    }

    if payload.zone:
        pkt["zt"] = payload.zone[:8]    # Truncate zone to 8 chars

    # Add fields gated by sensor_flags — only include if sensor bit is SET
    def _add(short_key: str, value: Any, flag_bit: int) -> None:
        if value is None:
            return
        if flag_bit != 0 and not (sensor_flags & flag_bit):
            return    # Sensor not present on this node
        if short_key == "fd":
            pkt[short_key] = int(bool(value))
        else:
            pkt[short_key] = value

    _add("lat", payload.latitude,               SENSOR_FLAGS.GPS)
    _add("lon", payload.longitude,              SENSOR_FLAGS.GPS)
    _add("bat", payload.battery_pct,            SENSOR_FLAGS.BATTERY)
    _add("bv",  payload.battery_voltage_v,      SENSOR_FLAGS.BATTERY)
    if payload.power_mode and payload.power_mode != "NORMAL":
        pkt["pw"] = payload.power_mode
    if payload.emergency_state:
        pkt["es"] = 1
    if payload.telemetry_priority and payload.telemetry_priority != "NORMAL":
        pkt["tp"] = payload.telemetry_priority
    if payload.telemetry_interval_s and payload.telemetry_interval_s != 300:
        pkt["ti"] = payload.telemetry_interval_s
    _add("t",   payload.temperature_c,          SENSOR_FLAGS.BME680)
    _add("h",   payload.humidity_pct,           SENSOR_FLAGS.BME680)
    _add("p",   payload.pressure_hpa,           SENSOR_FLAGS.BME680)
    _add("gr",  payload.gas_resistance_kohm,    SENSOR_FLAGS.BME680)
    _add("p25", payload.pm25_ug_m3,             SENSOR_FLAGS.SDS011)
    _add("p10", payload.pm10_ug_m3,             SENSOR_FLAGS.SDS011)
    _add("mq",  payload.mq135_raw,              SENSOR_FLAGS.MQ135)
    _add("rm",  payload.rainfall_mm,            SENSOR_FLAGS.RAIN)
    _add("r1",  payload.rainfall_1h_mm,         SENSOR_FLAGS.RAIN)
    _add("r24", payload.rainfall_24h_mm,        SENSOR_FLAGS.RAIN)
    _add("wl",  payload.water_level_m,          SENSOR_FLAGS.WATER)
    _add("ud",  payload.ultrasonic_distance_cm, SENSOR_FLAGS.ULTRASONIC)
    _add("sm",  payload.soil_moisture_pct,      SENSOR_FLAGS.SOIL)
    _add("tm",  payload.tilt_magnitude,         SENSOR_FLAGS.MPU6050)
    _add("tr",  payload.tilt_rate,              SENSOR_FLAGS.MPU6050)
    _add("vr",  payload.vibration_rate,         SENSOR_FLAGS.SW420)
    _add("fd",  payload.flame_detected,         SENSOR_FLAGS.FLAME)
    _add("ph",  payload.ph,                     SENSOR_FLAGS.PH)
    _add("td",  payload.tds_ppm,               SENSOR_FLAGS.TDS)
    _add("tb",  payload.turbidity,              SENSOR_FLAGS.TURBIDITY)

    encoded = json.dumps(pkt, separators=(",", ":")).encode("utf-8")

    if len(encoded) > MAX_PAYLOAD_BYTES:
        raise ValueError(
            f"LoRa packet too large: {len(encoded)} bytes "
            f"(max {MAX_PAYLOAD_BYTES}). "
            f"Reduce sensor_flags to a node-specific profile or reduce field count."
        )
    return encoded


# ---------------------------------------------------------------------------
# Decoder
# ---------------------------------------------------------------------------
def decode_packet(raw: bytes) -> Tuple[Any, int]:
    """
    Parse a raw LoRa packet into (TypeATelemetryPayload, sequence_number).

    Args:
        raw: bytes received from SX1278

    Returns:
        (TypeATelemetryPayload, int)  — parsed telemetry + sequence number.

    Raises:
        ValueError: if packet is malformed, missing required fields, or version mismatch.
    """
    from gateway.schemas import TypeATelemetryPayload
    from .config import PACKET_VERSION

    try:
        pkt = json.loads(raw.decode("utf-8"))
    except (json.JSONDecodeError, UnicodeDecodeError) as e:
        raise ValueError(f"LoRa packet JSON parse error: {e}") from e

    if not isinstance(pkt, dict):
        raise ValueError("LoRa packet must be a JSON object")

    version = pkt.get("v")
    if version != PACKET_VERSION:
        raise ValueError(f"Packet version mismatch: got {version}, expected {PACKET_VERSION}")

    node_id = pkt.get("id")
    sequence = pkt.get("seq")
    if not node_id:
        raise ValueError("Packet missing required field 'id' (node_id)")
    if sequence is None:
        raise ValueError("Packet missing required field 'seq' (sequence)")

    kwargs: Dict[str, Any] = {"node_id": str(node_id)}

    for short_key, (canonical, cast, _flag) in FIELD_MAP.items():
        if canonical.startswith("_"):
            continue
        if short_key not in pkt:
            continue

        raw_val = pkt[short_key]
        if raw_val is None:
            kwargs[canonical] = None
        elif short_key == "ts":
            # Epoch int -> ISO string
            if isinstance(raw_val, (int, float)):
                kwargs[canonical] = datetime.datetime.fromtimestamp(
                    int(raw_val), tz=datetime.timezone.utc
                ).isoformat()
            else:
                kwargs[canonical] = str(raw_val)
        elif cast is bool:
            kwargs[canonical] = bool(raw_val)
        elif cast:
            try:
                kwargs[canonical] = cast(raw_val)
            except (TypeError, ValueError):
                kwargs[canonical] = None
        else:
            kwargs[canonical] = raw_val

    # Apply sensor_flags to set absent sensors explicitly to None
    sensor_flags = pkt.get("sf", SENSOR_FLAGS.UNIVERSAL)
    kwargs = _apply_sensor_flags(kwargs, sensor_flags)

    try:
        payload = TypeATelemetryPayload(**kwargs)
    except Exception as e:
        raise ValueError(f"Schema validation failed: {e}") from e

    return payload, int(sequence)


def _apply_sensor_flags(kwargs: Dict[str, Any], flags: int) -> Dict[str, Any]:
    """For absent sensors (bit not set), ensure fields are None, not zero."""
    flag_to_fields = {
        SENSOR_FLAGS.BME680:    ("temperature_c", "humidity_pct", "pressure_hpa", "gas_resistance_kohm"),
        SENSOR_FLAGS.SDS011:    ("pm25_ug_m3", "pm10_ug_m3"),
        SENSOR_FLAGS.MQ135:     ("mq135_raw",),
        SENSOR_FLAGS.RAIN:      ("rainfall_mm", "rainfall_1h_mm", "rainfall_24h_mm"),
        SENSOR_FLAGS.WATER:     ("water_level_m",),
        SENSOR_FLAGS.ULTRASONIC:("ultrasonic_distance_cm",),
        SENSOR_FLAGS.SOIL:      ("soil_moisture_pct",),
        SENSOR_FLAGS.MPU6050:   ("tilt_magnitude", "tilt_rate"),
        SENSOR_FLAGS.SW420:     ("vibration_rate",),
        SENSOR_FLAGS.FLAME:     ("flame_detected",),
        SENSOR_FLAGS.PH:        ("ph",),
        SENSOR_FLAGS.TDS:       ("tds_ppm",),
        SENSOR_FLAGS.TURBIDITY: ("turbidity",),
        SENSOR_FLAGS.BATTERY:   ("battery_pct", "battery_voltage_v"),
    }
    for bit, fields in flag_to_fields.items():
        if not (flags & bit):
            for f in fields:
                kwargs.setdefault(f, None)
    return kwargs


def _utc_now_iso() -> str:
    return datetime.datetime.now(datetime.timezone.utc).isoformat()
