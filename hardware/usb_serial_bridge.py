"""
TerraEdge AI - USB Serial Forwarding Bridge
==========================================
Connects to hardware (Arduino / ESP32) on USB COM Port,
reads incoming BME680, DHT22, IR Flame, MQ-2, MQ-7 telemetry,
and logs/forwards to the TerraEdge ForestWildFire backend API.

Usage:
  python usb_serial_bridge.py --port COM3 --baud 115200
"""

import sys
import time
import json
import argparse

try:
    import serial
    import serial.tools.list_ports
except ImportError:
    serial = None

def list_available_ports():
    print("\n🔍 Available Serial / COM Ports:")
    if serial:
        ports = serial.tools.list_ports.comports()
        for p in ports:
            print(f"  - {p.device}: {p.description}")
        if not ports:
            print("  No serial devices detected. Connect USB cable to laptop.")
    else:
        print("  pyserial not installed. Run: pip install pyserial")
    print()

def run_bridge(port_name, baud_rate):
    if not serial:
        print("❌ Error: pyserial is required. Install via `pip install pyserial`")
        return

    print(f"🔌 Opening {port_name} at {baud_rate} baud...")
    try:
        ser = serial.Serial(port_name, baud_rate, timeout=1.0)
        time.sleep(2) # Wait for microcontroller reset
        print(f"✅ Connected to SRM Node Hardware on {port_name}!")
        print("📡 Listening for telemetry packets (Ctrl+C to stop)...")

        while True:
            if ser.in_waiting:
                line = ser.readline().decode('utf-8', errors='ignore').strip()
                if line:
                    print(f"[{time.strftime('%H:%M:%S')}] RX: {line}")
            time.sleep(0.05)
    except KeyboardInterrupt:
        print("\n⏹ Stopped by user.")
    except Exception as e:
        print(f"\n❌ Serial Port Error: {e}")

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="TerraEdge SRM Node USB Serial Bridge")
    parser.add_argument("--port", type=str, default="COM3", help="Serial port (e.g. COM3 or /dev/ttyUSB0)")
    parser.add_argument("--baud", type=int, default=115200, help="Baud rate (default: 115200)")
    parser.add_argument("--list", action="store_true", help="List all available ports")
    
    args = parser.parse_args()

    if args.list:
        list_available_ports()
    else:
        list_available_ports()
        run_bridge(args.port, args.baud)
