"""
TerraEdge — Phase 8 SQLite Queue Backup Utility.
CLI tool to generate live, crash-consistent hot backups of the store-and-forward queue.
"""

from __future__ import annotations
import argparse
import datetime
import os
import sys

# Ensure imports work from project root
HERE = os.path.dirname(os.path.abspath(__file__))
GATEWAY_DIR = os.path.dirname(HERE)
PROJECT_ROOT = os.path.dirname(GATEWAY_DIR)
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from gateway.backhaul.queue import durable_queue
from gateway.config import BACKHAUL_DATA_DIR, BACKHAUL_QUEUE_DB_PATH


def main():
    parser = argparse.ArgumentParser(description="TerraEdge SQLite Queue Backup Utility")
    parser.add_argument(
        "--output-dir",
        default=os.path.join(BACKHAUL_DATA_DIR, "backups"),
        help="Target directory for backup snapshot (default: gateway/data/backups)"
    )
    args = parser.parse_args()

    os.makedirs(args.output_dir, exist_ok=True)
    timestamp_str = datetime.datetime.now(datetime.timezone.utc).strftime("%Y%m%d_%H%M%S")
    dest_file = os.path.join(args.output_dir, f"backhaul_queue_{timestamp_str}.bak")

    print(f"[*] Initiating hot backup from: {BACKHAUL_QUEUE_DB_PATH}")
    try:
        backed_up_path = durable_queue.backup_to_file(dest_file)
        size_kb = round(os.path.getsize(backed_up_path) / 1024, 2)
        print(f"[OK] Backup completed successfully: {backed_up_path} ({size_kb} KB)")
        summary = durable_queue.get_summary()
        print(f"    - Pending records : {summary.pending_count}")
        print(f"    - Synced records  : {summary.synced_count}")
    except Exception as exc:
        print(f"[X] Backup failed: {exc}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
