"""Version 4 field-boundary fragmentation. Never infer from incomplete frames."""
from __future__ import annotations
import json
import math
import re
import threading
import time

# Wire units are part of the contract, not a sensor-dependent guess.
FIELDS = {
    "t": ("temperature_c", "°C"), "h": ("humidity_pct", "% RH"),
    "p": ("pressure_hpa", "hPa"), "gr": ("gas_resistance_kohm", "kΩ"),
    "m7": ("mq7_raw", "ADC counts"), "m7_mv": ("m7_mv", "mV at GPIO7"),
    "mq": ("mq135_raw", "ADC counts"), "rain_adc": ("rain_adc", "ADC counts"),
    "water_adc": ("water_adc", "ADC counts"), "soil_adc": ("soil_adc", "ADC counts"),
    "ph_mv": ("ph_mv", "mV"), "tds_mv": ("tds_mv", "mV"), "turb_mv": ("turb_mv", "mV"),
    "rm": ("rainfall_mm", "mm per sampling interval"),
    "r24": ("rainfall_24h_mm", "mm / 24 h"),
    "r1": ("rainfall_1h_mm", "mm / 1 h"), "r3": ("rainfall_3h_mm", "mm / 3 h"),
    "r6": ("rainfall_6h_mm", "mm / 6 h"), "r72": ("rainfall_72h_mm", "mm / 72 h"),
    "flow": ("streamflow_cumec", "m³/s"),
    "wl": ("water_level_m", "m"), "ud": ("ultrasonic_distance_cm", "cm"),
    "sm": ("soil_moisture_pct", "% VWC"), "tm": ("tilt_magnitude", "°"),
    "vr": ("vibration_rate", "pulses/min"), "fd": ("flame_detected", "boolean"),
    "ph": ("ph", "pH"), "td": ("tds_ppm", "ppm"), "tb": ("turbidity", "NTU"),
    "p25": ("pm25_ug_m3", "µg/m³"), "p10": ("pm10_ug_m3", "µg/m³"),
    "lat": ("latitude", "°"), "lon": ("longitude", "°"),
    "bv": ("battery_voltage_v", "V"),
    "co": ("co_mg_m3", "mg/m³"), "no2": ("no2_ug_m3", "µg/m³"),
    "wt": ("water_temperature_c", "°C"), "do": ("dissolved_oxygen", "mg/L"),
    "ec": ("electrical_conductivity", "µS/cm"),
    "sun": ("solar_radiation_w_m2", "W/m²"), "wind": ("wind_speed_kmh", "km/h"),
}
UNITS = {name: unit for name, unit in FIELDS.values()}
DIAGNOSTICS = {"m7_mv", "rain_adc", "water_adc", "soil_adc", "ph_mv", "tds_mv", "turb_mv", "bme_ok", "mpu_ok"}


def decode_envelope(envelope):
    if not isinstance(envelope, dict):
        raise ValueError("Expected a receiver JSON object")
    if envelope.get("type") != "RX":
        return None  # READY, ERROR and old SCORES messages are not telemetry.
    data = envelope.get("data")
    if not isinstance(data, str) or not re.fullmatch(r"[0-9a-fA-F]{2,510}", data) or len(data) % 2:
        raise ValueError("Invalid LoRa hex payload")
    raw = bytes.fromhex(data)
    if type(envelope.get("size")) is not int or envelope["size"] != len(raw):
        raise ValueError("LoRa size does not match received bytes")
    packet = json.loads(raw.decode("utf-8"))
    if not isinstance(packet, dict) or packet.get("v") != 4:
        raise ValueError("Flash protocol v4 SENDER.ino; legacy v3 has ambiguous rain units")
    for field in ("rssi", "snr"):
        value = envelope.get(field)
        if type(value) not in (int, float) or not math.isfinite(value):
            raise ValueError("Missing/invalid radio metadata")
    return packet


class FrameAssembler:
    def __init__(self, clock=time.monotonic, timeout=20, capacity=256):
        self.clock, self.timeout, self.capacity = clock, timeout, capacity
        self.pending = {}
        self.completed = {}
        self.latest_sequence = {}
        self.lock = threading.RLock()

    def accept(self, envelope):
        packet = decode_envelope(envelope)
        if packet is None:
            return "ignored", None, None
        node = packet.get("id")
        if not isinstance(node, str) or not re.fullmatch(r"[A-Za-z0-9_-]{1,32}", node):
            raise ValueError("Invalid node id")
        for key in ("boot", "seq", "up", "part"):
            if type(packet.get(key)) is not int or not 0 <= packet[key] <= 0xffffffff:
                raise ValueError("Invalid frame metadata: " + key)
        if packet["part"] >= 16 or type(packet.get("last")) is not bool:
            raise ValueError("Invalid fragment index/last marker")
        data = packet.get("d")
        if not isinstance(data, dict) or not data or len(data) > 40:
            raise ValueError("Missing sensor fields")
        for key, value in data.items():
            if key not in FIELDS and key not in DIAGNOSTICS:
                raise ValueError("Unknown sensor field: " + key)
            if type(value) not in (int, float, bool) or not math.isfinite(value):
                raise ValueError("Sensor values must be finite numbers")
            if key in ("fd", "bme_ok", "mpu_ok") and value not in (0, 1):
                raise ValueError("Invalid boolean sensor state")
            if type(value) is bool and key not in ("fd", "bme_ok", "mpu_ok"):
                raise ValueError("Boolean cannot stand in for a numeric measurement")
            if (key.endswith("_adc") or key in ("mq", "m7")) and not 0 <= value <= 4095:
                raise ValueError("12-bit ADC reading outside 0..4095")
            if key.endswith("_mv") and not 0 <= value <= 3300:
                raise ValueError("ADC millivolts outside 0..3300")
        now = self.clock()
        self.pending = {k: v for k, v in self.pending.items() if now - v["time"] < self.timeout}
        self.completed = {k: v for k, v in self.completed.items() if now - v < 3600}
        identity = (node, packet["boot"], packet["seq"])
        if identity in self.completed:
            return "duplicate", None, identity
        previous = self.latest_sequence.get(identity[:2])
        if previous is not None and not 0 < ((packet["seq"] - previous) & 0xffffffff) < 0x80000000:
            return "duplicate", None, identity
        if identity not in self.pending and len(self.pending) >= self.capacity:
            raise ValueError("Too many incomplete frames")
        frame = self.pending.setdefault(identity, {"time": now, "up": packet["up"], "parts": {}, "last": None})
        i = packet["part"]
        if frame["up"] != packet["up"]:
            raise ValueError("Inconsistent frame uptime")
        part_value = (data, packet["last"])
        if i in frame["parts"] and frame["parts"][i] != part_value:
            raise ValueError("Conflicting duplicate fragment")
        if packet["last"]:
            if frame["last"] is not None and frame["last"] != i:
                raise ValueError("Conflicting final fragments")
            frame["last"] = i
        frame["parts"][i] = part_value
        end = frame["last"]
        if end is not None and max(frame["parts"]) > end:
            raise ValueError("Fragment after final marker")
        if end is None or len(frame["parts"]) != end + 1:
            return "pending", None, identity
        values = {}
        for j in range(end + 1):
            fragment = frame["parts"][j][0]
            if values.keys() & fragment.keys():
                raise ValueError("Repeated field across fragments")
            values.update(fragment)
        if not (values.keys() & FIELDS.keys()):
            raise ValueError("Frame contains no measurements")
        payload = {FIELDS[k][0]: v for k, v in values.items() if k in FIELDS and k not in DIAGNOSTICS}
        payload.update(node_id=node, sequence=packet["seq"], firmware_version="4.0.0",
                       source="hardware_v4", boot_id=str(packet["boot"]), uptime_ms=packet["up"],
                       sensor_diagnostics={k: v for k, v in values.items() if k in DIAGNOSTICS},
                       rssi_dbm=envelope["rssi"], snr_db=envelope["snr"], is_simulated=False)
        # ADC saturation is diagnostic evidence, not a measurement in ppm or mm.
        return "complete", payload, identity

    def commit(self, identity):
        self.pending.pop(identity, None)
        self.completed[identity] = self.clock()
        self.latest_sequence[identity[:2]] = identity[2]
        while len(self.latest_sequence) > 4096:
            self.latest_sequence.pop(next(iter(self.latest_sequence)))
        while len(self.completed) > 4096:
            self.completed.pop(next(iter(self.completed)))


assembler = FrameAssembler()
