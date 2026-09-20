"""
TerraEdge — Autonomous LoRa Hardware Receiver Serial Bridge
============================================================
Reads incoming JSON packets from your physical LoRa Receiver ESP32 / Arduino 
over the USB COM port and forwards them directly to the TerraEdge Dashboard / Gateway.

Usage:
    python lora_serial_bridge.py [COM_PORT] [BAUD_RATE]
Example:
    python lora_serial_bridge.py COM3 115200
"""

import sys
import time
import json
import urllib.request
import urllib.error

GATEWAY_API_URL = "http://127.0.0.1:8000/api/telemetry"

def get_serial_module():
    try:
        import serial
        import serial.tools.list_ports
        return serial
    except ImportError:
        print("[!] 'pyserial' is not installed. To install it, run:")
        print("    pip install pyserial")
        sys.exit(1)

def auto_find_port(serial_mod):
    ports = list(serial_mod.tools.list_ports.comports())
    if not ports:
        return None
    for p in ports:
        desc = (p.description or "").lower()
        if any(keyword in desc for keyword in ["ch340", "cp210", "ftdi", "usb serial", "esp32", "arduino"]):
            return p.device
    return ports[0].device

def forward_to_gateway(sensor_data):
    try:
        payload = {
            "node_id": sensor_data.get("node_id", "TE-001"),
            "temperature_c": float(sensor_data.get("temp", sensor_data.get("t", 30.0))),
            "humidity_pct": float(sensor_data.get("hum", sensor_data.get("h", 50.0))),
            "pressure_hpa": float(sensor_data.get("press", sensor_data.get("p", 1011.0))),
            "mq135_raw": float(sensor_data.get("mq2", sensor_data.get("mq", 120.0))),
            "rainfall_mm": float(sensor_data.get("rain", sensor_data.get("rm", 0.0))),
            "water_level_m": float(sensor_data.get("water", sensor_data.get("wl", 0.0))),
            "soil_moisture_pct": float(sensor_data.get("soil", sensor_data.get("sm", 35.0))),
            "tilt_magnitude": float(sensor_data.get("tilt", sensor_data.get("tm", 0.0))),
            "vibration_rate": float(sensor_data.get("vib", sensor_data.get("vr", 0.0))),
            "flame_detected": bool(float(sensor_data.get("flame", sensor_data.get("fd", 0))) > 0.5),
            "latitude": float(sensor_data.get("lat", sensor_data.get("latitude", 13.0355))),
            "longitude": float(sensor_data.get("lon", sensor_data.get("longitude", 80.1838))),
            "battery_pct": float(sensor_data.get("bat", 95.0))
        }
        req = urllib.request.Request(
            GATEWAY_API_URL,
            data=json.dumps(payload).encode("utf-8"),
            headers={"Content-Type": "application/json"}
        )
        with urllib.request.urlopen(req, timeout=2) as resp:
            if resp.status == 200:
                print("   -> [FORWARDED TO GATEWAY] Dashboard risk-map updated.")
    except Exception as e:
        # Gateway may be offline, still output serial telemetry to console
        pass

def main():
    serial_mod = get_serial_module()
    
    port = sys.argv[1] if len(sys.argv) > 1 else None
    baud = int(sys.argv[2]) if len(sys.argv) > 2 else 115200

    if not port:
        port = auto_find_port(serial_mod)
        if not port:
            print("[!] CRITICAL ERROR: Your computer is detecting ZERO COM ports.")
            print("    This usually means:")
            print("      1. Your USB cable is 'Charge-Only' (no data wires). Try a different cable (like one that came with a phone).")
            print("      2. The CH340 or CP210x USB-to-Serial drivers are not installed on your laptop.")
            print("      3. The ESP32 is not fully plugged in.")
            print("    Please fix the connection and try again.")
            sys.exit(1)

    print("=================================================================")
    print("  TERRA EDGE — AUTONOMOUS LORA RECEIVER SERIAL BRIDGE")
    print(f"  Target Port : {port} @ {baud} baud")
    print(f"  Dashboard   : {GATEWAY_API_URL}")
    print("=================================================================")
    print("[*] Opening serial stream...")

    while True:
        try:
            with serial_mod.Serial(port, baud, timeout=1) as ser:
                print(f"[✓] Connected to {port}! Listening for SX1278 433MHz packets from receiver...")
                while True:
                    line = ser.readline().decode('utf-8', errors='ignore').strip()
                    if not line:
                        continue
                    print(f"[RAW-RX] {line}")
                    if line.startswith('{') and line.endswith('}'):
                        try:
                            data = json.loads(line)
                            node_id = data.get("node_id", "TE-001")
                            lat = data.get("lat", 13.0355)
                            lon = data.get("lon", 80.1838)
                            print(f"[LORA DETECTED] Node {node_id} | GPS: {lat}°N, {lon}°E | Temp: {data.get('temp')}°C")
                            forward_to_gateway(data)
                        except json.JSONDecodeError:
                            pass
        except Exception as err:
            print(f"[!] Serial connection lost ({err}). Reconnecting in 3s...")
            time.sleep(3)

if __name__ == "__main__":
    main()
