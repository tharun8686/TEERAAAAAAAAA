"""
TerraEdge Phase 3 — LoRa Radio Abstraction Layer.

Defines the LoRaRadioBase interface and two concrete implementations:

  MockLoRaRadio
      In-process loopback for unit tests and CI.
      No hardware required.  send() pushes to internal queue;
      receive() pops from it.

  SerialLoRaRadio
      Communicates with a second ESP32 acting as a USB-UART LoRa bridge.
      The bridge ESP32 runs terraedge_bridge.ino, forwards received LoRa
      packets to the PC over USB serial as JSON lines:
          {"type":"RX","rssi":-81,"snr":7.5,"data":"<hex>"}
      And accepts ACK commands:
          {"type":"TX","data":"<hex>"}

Note:
    The Type B gateway server runs on a PC/server that has no SPI pins.
    The SX1278 radio is physically attached to the bridge ESP32.
    This architecture is correct for a real SIH prototype setup.
"""
from __future__ import annotations
import json
import queue
import threading
import time
from abc import ABC, abstractmethod
from typing import Optional


# ---------------------------------------------------------------------------
# Abstract Interface
# ---------------------------------------------------------------------------
class LoRaRadioBase(ABC):
    """Base interface for all LoRa radio implementations."""

    @abstractmethod
    def initialize(self) -> bool:
        """Initialize the radio.  Returns True on success."""

    @abstractmethod
    def send(self, data: bytes) -> bool:
        """Transmit data bytes.  Returns True if transmission was accepted."""

    @abstractmethod
    def receive(self, timeout_ms: int = 1000) -> Optional[bytes]:
        """
        Listen for an incoming packet.
        Returns raw bytes on success, None on timeout or error.
        timeout_ms: how long to wait in milliseconds.
        """

    @abstractmethod
    def get_rssi(self) -> Optional[float]:
        """Return RSSI of the last received packet in dBm, or None."""

    @abstractmethod
    def get_snr(self) -> Optional[float]:
        """Return SNR of the last received packet in dB, or None."""

    @abstractmethod
    def close(self) -> None:
        """Release resources."""

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__}>"


# ---------------------------------------------------------------------------
# MockLoRaRadio — in-process loopback (no hardware needed)
# ---------------------------------------------------------------------------
class MockLoRaRadio(LoRaRadioBase):
    """
    In-process mock radio for testing without hardware.

    send() pushes data to an internal queue.
    receive() pops from the same queue (loopback) — or from an external
    injection queue if inject_packet() is called.

    Usage in tests:
        radio = MockLoRaRadio()
        radio.initialize()
        radio.send(encoded_bytes)
        raw = radio.receive()   # returns the same bytes
    """

    def __init__(self):
        self._queue: queue.Queue[bytes] = queue.Queue()
        self._last_rssi: float = -72.0
        self._last_snr: float = 9.5
        self._initialized = False

    def initialize(self) -> bool:
        self._initialized = True
        print("[MockLoRaRadio] Initialized (loopback mode — no hardware)", flush=True)
        return True

    def send(self, data: bytes) -> bool:
        if not self._initialized:
            return False
        self._queue.put(data)
        return True

    def receive(self, timeout_ms: int = 1000) -> Optional[bytes]:
        try:
            return self._queue.get(timeout=timeout_ms / 1000.0)
        except queue.Empty:
            return None

    def inject_packet(self, data: bytes, rssi: float = -72.0, snr: float = 9.5) -> None:
        """Externally inject a packet (simulates incoming radio packet from Type A)."""
        self._last_rssi = rssi
        self._last_snr = snr
        self._queue.put(data)

    def get_rssi(self) -> Optional[float]:
        return self._last_rssi

    def get_snr(self) -> Optional[float]:
        return self._last_snr

    def close(self) -> None:
        self._initialized = False


# ---------------------------------------------------------------------------
# SerialLoRaRadio — USB-UART bridge to SX1278 ESP32
# ---------------------------------------------------------------------------
class SerialLoRaRadio(LoRaRadioBase):
    """
    Communicates with a second ESP32 running terraedge_bridge.ino over USB serial.

    The bridge ESP32 receives LoRa packets from Type A nodes and forwards them
    as JSON lines on USB serial:
        {"type":"RX","rssi":-81.0,"snr":7.5,"data":"<hex-encoded-payload>"}

    This class reads those lines, parses RSSI/SNR, and returns the raw payload bytes.

    For ACK transmission, it sends:
        {"type":"TX","data":"<hex-encoded-ack>"}

    NOTE: Requires pyserial.  Install with: pip install pyserial
    """

    def __init__(self, port: str, baud: int = 115200):
        self._port = port
        self._baud = baud
        self._serial = None
        self._last_rssi: Optional[float] = None
        self._last_snr: Optional[float] = None
        self._lock = threading.Lock()

    def initialize(self) -> bool:
        try:
            import serial
        except ImportError:
            print("[SerialLoRaRadio] ERROR: pyserial not installed. Run: pip install pyserial", flush=True)
            return False
        try:
            self._serial = serial.Serial(self._port, self._baud, timeout=0.1)
            time.sleep(2)   # Wait for ESP32 reset
            print(f"[SerialLoRaRadio] Connected to LoRa bridge on {self._port} @ {self._baud} baud", flush=True)
            return True
        except Exception as e:
            print(f"[SerialLoRaRadio] Failed to open {self._port}: {e}", flush=True)
            return False

    def send(self, data: bytes) -> bool:
        """Send a raw packet to be transmitted by the bridge (e.g., ACK)."""
        if not self._serial:
            return False
        try:
            hex_data = data.hex()
            cmd = json.dumps({"type": "TX", "data": hex_data}) + "\n"
            with self._lock:
                self._serial.write(cmd.encode("utf-8"))
            return True
        except Exception as e:
            print(f"[SerialLoRaRadio] send error: {e}", flush=True)
            return False

    def receive(self, timeout_ms: int = 1000) -> Optional[bytes]:
        """
        Wait for an incoming JSON line from the bridge.
        Returns decoded payload bytes or None on timeout/error.
        """
        if not self._serial:
            return None

        deadline = time.monotonic() + timeout_ms / 1000.0
        while time.monotonic() < deadline:
            try:
                with self._lock:
                    line = self._serial.readline()
            except Exception as e:
                print(f"[SerialLoRaRadio] read error: {e}", flush=True)
                return None

            if not line:
                continue

            try:
                msg = json.loads(line.decode("utf-8", errors="ignore").strip())
            except json.JSONDecodeError:
                continue

            if msg.get("type") != "RX":
                continue

            self._last_rssi = msg.get("rssi")
            self._last_snr = msg.get("snr")
            hex_data = msg.get("data", "")
            try:
                return bytes.fromhex(hex_data)
            except ValueError as e:
                print(f"[SerialLoRaRadio] hex decode error: {e}", flush=True)
                return None

        return None     # timeout

    def get_rssi(self) -> Optional[float]:
        return self._last_rssi

    def get_snr(self) -> Optional[float]:
        return self._last_snr

    def close(self) -> None:
        if self._serial:
            try:
                self._serial.close()
            except Exception:
                pass
            self._serial = None
