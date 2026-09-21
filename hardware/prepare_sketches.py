"""Copy the two root sketches to separate Arduino sketch directories."""
from pathlib import Path
import shutil

root = Path(__file__).resolve().parents[1]
for name in ("SENDER", "RECEIVER"):
    target = root / "build" / "arduino" / name
    target.mkdir(parents=True, exist_ok=True)
    shutil.copy2(root / (name + ".ino"), target / (name + ".ino"))
    shutil.copy2(root / "hardware_config.h", target / "hardware_config.h")
    print(target)
