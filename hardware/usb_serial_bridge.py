"""
TerraEdge — USB Serial Forwarding Bridge (Phase 3 Update)
=========================================================
Connects to the TerraEdge LoRa USB bridge device (ESP32 running
terraedge_bridge.ino) over USB serial, parses incoming LoRa packets,
and forwards them to the Type B gateway via POST /api/telemetry.

Packet flow:
  Type A ESP32 --[LoRa]--> Bridge ESP32 --[USB Serial]-->
  usb_serial_bridge.py --[HTTP POST]--> Type B Gateway

Bridge output format (one JSON line per packet):
  {"type":"RX","rssi":-81.0,"snr":7.5,"size":187,"data":"<hex>"}

Usage:
  python usb_serial_bridge.py --port COM4 --baud 115200
  python usb_serial_bridge.py --port COM4 --gateway http://127.0.0.1:8000
  python usb_serial_bridge.py --list

NOTE: This script is a development/debug utility.
      For production, the gateway uses the SerialLoRaRadio class directly.
"""

import sys
import time
import json
import argparse
import urllib.request

try:
    import serial
    import serial.tools.list_ports
except ImportError:
    serial = None


GATEWAY_URL = "http://127.0.0.1:8000"


def list_available_ports():
    print("\nAvailable Serial / COM Ports:")
    if serial:
        ports = serial.tools.list_ports.comports()
        for p in ports:
            print(f"  - {p.device}: {p.description}")
        if not ports:
            print("  No serial devices detected.")
    else:
        print("  pyserial not installed. Run: pip install pyserial")
    print()


def hex_to_text(hex_str: str) -> str:
    """Decode hex-encoded LoRa payload to UTF-8 text."""
    try:
        return bytes.fromhex(hex_str).decode("utf-8", errors="replace")
    except ValueError:
        return ""


def forward_to_gateway(payload_json: str, rssi: float, snr: float, gateway_url: str) -> bool:
    """POST decoded telemetry to Type B gateway."""
    try:
        # Parse the LoRa payload JSON
        pkt = json.loads(payload_json)

        # Map short keys to canonical field names (same as gateway/lora/packet.py)
        FIELD_MAP = {
            "id": "node_id", "ts": "timestamp",
            "lat": "latitude", "lon": "longitude",
            "bat": "battery_pct", "zt": "zone",
            "t": "temperature_c", "h": "humidity_pct",
            "p": "pressure_hpa", "gr": "gas_resistance_kohm",
            "p25": "pm25_ug_m3", "p10": "pm10_ug_m3",
            "mq": "mq135_raw",
            "rm": "rainfall_mm", "r1": "rainfall_1h_mm",
            "r3": "rainfall_3h_mm", "r6": "rainfall_6h_mm",
            "r24": "rainfall_24h_mm", "r72": "rainfall_72h_mm",
            "wl": "water_level_m", "ud": "ultrasonic_distance_cm",
            "sm": "soil_moisture_pct",
            "tm": "tilt_magnitude", "tr": "tilt_rate",
            "vr": "vibration_rate",
            "fd": "flame_detected",
            "ph": "ph", "td": "tds_ppm", "tb": "turbidity",
        }

        telemetry = {"node_type": "Type-A", "rssi_dbm": rssi}
        for short_k, canonical_k in FIELD_MAP.items():
            if short_k in pkt:
                val = pkt[short_k]
                if short_k == "fd":
                    telemetry["flame_detected"] = bool(val)
                    telemetry["flame"] = int(val)
                else:
                    telemetry[canonical_k] = val

        if "node_id" not in telemetry:
            print(f"  [WARN] Packet missing node id — skipping")
            return False

        body = json.dumps(telemetry).encode("utf-8")
        req = urllib.request.Request(
            f"{gateway_url}/api/telemetry",
            data=body,
            headers={"Content-Type": "application/json"},
        )
        with urllib.request.urlopen(req, timeout=10) as resp:
            result = json.loads(resp.read())
            node_id = result.get("node_id", "?")
            risk    = result.get("composite_risk_pct", 0)
            hazard  = result.get("primary_hazard", "?")
            sev     = result.get("primary_severity", "?")
            print(f"  -> Gateway: {node_id} | Risk={risk:.1f}% | {sev} | {hazard} | RSSI={rssi:.0f}dBm")
            return True
    except Exception as e:
        print(f"  [ERROR] Gateway forward failed: {e}")
        return False


def run_bridge(port_name: str, baud_rate: int, gateway_url: str):
    if not serial:
        print("ERROR: pyserial required. Run: pip install pyserial")
        return

    print(f"Opening {port_name} at {baud_rate} baud...")
    try:
        ser = serial.Serial(port_name, baud_rate, timeout=1.0)
        time.sleep(2)
        print(f"Connected to TerraEdge LoRa Bridge on {port_name}")
        print(f"Forwarding packets to {gateway_url}")
        print("Listening... (Ctrl+C to stop)\n")

        while True:
            if ser.in_waiting:
                raw_line = ser.readline()
                try:
                    line = raw_line.decode("utf-8", errors="ignore").strip()
                except Exception:
                    continue

                if not line:
                    continue

                try:
                    msg = json.loads(line)
                except json.JSONDecodeError:
                    print(f"  [Serial] {line}")
                    continue

                msg_type = msg.get("type", "")

                if msg_type == "RX":
                    rssi = msg.get("rssi", 0.0)
                    snr  = msg.get("snr", 0.0)
                    size = msg.get("size", 0)
                    hex_data = msg.get("data", "")
                    payload_text = hex_to_text(hex_data)

                    print(f"[{time.strftime('%H:%M:%S')}] RX {size}B | RSSI={rssi:.0f}dBm | SNR={snr:.1f}dB")
                    print(f"  Payload: {payload_text[:120]}")
                    forward_to_gateway(payload_text, rssi, snr, gateway_url)

                elif msg_type == "READY":
                    print(f"  Bridge: {msg.get('msg', 'ready')}")
                elif msg_type == "ERROR":
                    print(f"  [Bridge ERROR] {msg.get('msg', '')}")
                else:
                    print(f"  [Bridge] {line}")

            time.sleep(0.02)

    except KeyboardInterrupt:
        print("\nStopped by user.")
    except Exception as e:
        print(f"\nSerial Port Error: {e}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="TerraEdge LoRa USB Bridge Forwarder")
    parser.add_argument("--port",    default="COM4",                    help="Serial port (e.g. COM4 or /dev/ttyUSB0)")
    parser.add_argument("--baud",    type=int, default=115200,           help="Baud rate (default: 115200)")
    parser.add_argument("--gateway", default="http://127.0.0.1:8000",   help="Gateway URL")
    parser.add_argument("--list",    action="store_true",                help="List available ports and exit")
    args = parser.parse_args()

    if args.list:
        list_available_ports()
    else:
        list_available_ports()
        run_bridge(args.port, args.baud, args.gateway)
