"""Copy the two root sketches to separate Arduino sketch directories."""
from pathlib import Path
import shutil
import zipfile

root = Path(__file__).resolve().parents[1]
for name in ("SENDER", "RECEIVER"):
    target = root / "build" / "arduino" / name
    target.mkdir(parents=True, exist_ok=True)
    shutil.copy2(root / (name + ".ino"), target / (name + ".ino"))
    # Remove only the obsolete generated header; sketches are self-contained.
    (target / "hardware_config.h").unlink(missing_ok=True)
    print(target)

instructions = """TerraEdge complete Arduino sketches

Extract this ZIP first. Do not paste a selected section into a new sketch.
Open SENDER/SENDER.ino for the ESP32-S3 sender.
Open RECEIVER/RECEIVER.ino for the standard ESP32/WROOM-32 receiver.
Each sketch is a single self-contained file. Settings are inside SENDER.ino.
Never place both .ino files in the same sketch directory.

Arduino IDE board selections:
  Sender: ESP32S3 Dev Module; enable USB CDC On Boot for native USB.
  Receiver: ESP32 Dev Module.

Install the Espressif ESP32 board package and these Library Manager libraries:
  Both: LoRa by Sandeep Mistry; ArduinoJson version 6.x.
  Sender: Adafruit BME680 Library, Adafruit MPU6050, Adafruit Unified Sensor,
          Adafruit BusIO (including offered dependencies).
  TinyGPSPlus is needed only if you enable the optional GPS configuration.

Use Verify separately for each sketch before Upload. Select the correct board
and USB port each time. Serial baud: 115200.

An error at line 1 beginning with 'if (TDS_CALIBRATED ...)' means a fragment
was pasted instead of the complete sender. Close that incomplete sketch and
open SENDER/SENDER.ino from this extracted folder.

Sensor calibration is still required. See docs/HARDWARE_TO_DASHBOARD.md in
the project for wiring, units, calibration and receiver-to-dashboard setup.
Verified with ESP32 core 3.3.11 for ESP32-S3 sender (USB CDC enabled) and ESP32
receiver. These revised files have not been flashed or physically tested.
"""
base = root / "build" / "arduino"
(base / "READ_ME_FIRST.txt").write_text(instructions, encoding="utf-8")
archive = root / "build" / "TerraEdge-Sender-S3-Receiver-ESP32.zip"
with zipfile.ZipFile(archive, "w", zipfile.ZIP_DEFLATED) as bundle:
    bundle.write(base / "READ_ME_FIRST.txt", "READ_ME_FIRST.txt")
    for name in ("SENDER", "RECEIVER"):
        for filename in (name + ".ino",):
            path = base / name / filename
            assert path.read_bytes() == (root / filename).read_bytes()
            bundle.write(path, f"{name}/{filename}")
print(archive)
