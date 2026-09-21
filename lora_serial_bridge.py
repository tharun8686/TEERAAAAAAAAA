"""Forward RX envelopes: python lora_serial_bridge.py COM4 --gateway http://127.0.0.1:8000"""
import argparse
import json
import logging
import time
import urllib.error
import urllib.request

log = logging.getLogger("lora-bridge")


def forward_to_gateway(envelope, gateway="http://127.0.0.1:8000", attempts=3):
    if not isinstance(envelope, dict) or envelope.get("type") != "RX":
        return None
    encoded = json.dumps(envelope, allow_nan=False).encode("utf-8")
    for attempt in range(attempts):
        request = urllib.request.Request(gateway.rstrip("/") + "/api/hardware", data=encoded,
                                         headers={"Content-Type": "application/json"})
        try:
            with urllib.request.urlopen(request, timeout=5) as response:
                result = json.load(response)
                log.info("Gateway: %s", result.get("status"))
                return result
        except urllib.error.HTTPError as error:
            if error.code < 500 and error.code != 429:
                log.error("Gateway rejected frame (%s): %s", error.code, error.read(2048).decode(errors="replace"))
                return None
            log.warning("Gateway HTTP %s; retry %s/%s", error.code, attempt + 1, attempts)
        except (OSError, ValueError) as error:
            log.warning("Gateway unavailable: %s; retry %s/%s", error, attempt + 1, attempts)
        if attempt + 1 < attempts:
            time.sleep(1)
    log.error("Frame delivery failed after retries; check gateway. This reading was not displayed.")
    return None


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("port", nargs="?")
    parser.add_argument("baud", nargs="?", type=int, default=115200)
    parser.add_argument("--gateway", default="http://127.0.0.1:8000")
    args = parser.parse_args()
    import serial
    from serial.tools.list_ports import comports
    if not args.port:
        ports = list(comports())
        if len(ports) != 1:
            parser.error("Specify the RECEIVER port; available: " + ", ".join(p.device for p in ports))
        args.port = ports[0].device
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
    log.info("Receiver %s -> %s/live", args.port, args.gateway)
    while True:
        try:
            with serial.Serial(args.port, args.baud, timeout=1) as connection:
                buffer = bytearray()
                while True:
                    buffer.extend(connection.read(connection.in_waiting or 1))
                    while b"\n" in buffer:
                        line, _, remainder = buffer.partition(b"\n")
                        buffer = bytearray(remainder)
                        try:
                            envelope = json.loads(line)
                            if isinstance(envelope, dict) and envelope.get("type") == "RX":
                                forward_to_gateway(envelope, args.gateway)
                            else:
                                log.info("Receiver diagnostic: %s", line.decode(errors="replace"))
                        except (ValueError, UnicodeError) as error:
                            log.warning("Ignored malformed serial line: %s", error)
                    if len(buffer) > 4096:
                        log.warning("Discarding oversized/unterminated serial line")
                        buffer.clear()
        except (serial.SerialException, OSError) as error:
            log.error("Serial connection failed: %s; retrying in 3 seconds", error)
            time.sleep(3)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        pass
