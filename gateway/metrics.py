"""
TerraEdge — Phase 8 Lightweight In-Memory Metrics Collector.
Tracks real-time system performance, model inferences, packet loss,
alert volumes, and processing latencies without heavy external monitoring dependencies.
"""

from __future__ import annotations
import datetime
import threading
import time
from typing import Any, Dict, List


def _utc_now_iso() -> str:
    return datetime.datetime.now(datetime.timezone.utc).isoformat()


class MetricsCollector:
    """Thread-safe in-memory operational metrics repository."""
    def __init__(self):
        self._lock = threading.Lock()
        self._start_time = time.time()

        # Operational Counters
        self.telemetry_received_total = 0
        self.telemetry_rejected_total = 0
        self.lora_packets_received = 0
        self.lora_packets_lost = 0
        self.ml_inference_total = 0
        self.ml_inference_errors = 0
        self.alerts_generated = 0
        self.notifications_attempted = 0
        self.notifications_failed = 0
        self.backhaul_failovers = 0

        # Latency samples (keep last 50 samples for moving averages)
        self._ingest_latencies: List[float] = []
        self._inference_latencies: List[float] = []

    def inc_telemetry_received(self, count: int = 1) -> None:
        with self._lock:
            self.telemetry_received_total += count

    def inc_telemetry_rejected(self, count: int = 1) -> None:
        with self._lock:
            self.telemetry_rejected_total += count

    def inc_lora_packets(self, received: int = 1, lost: int = 0) -> None:
        with self._lock:
            self.lora_packets_received += received
            self.lora_packets_lost += lost

    def inc_ml_inference(self, count: int = 1, errors: int = 0) -> None:
        with self._lock:
            self.ml_inference_total += count
            self.ml_inference_errors += errors

    def inc_alerts_generated(self, count: int = 1) -> None:
        with self._lock:
            self.alerts_generated += count

    def inc_notifications(self, attempted: int = 1, failed: int = 0) -> None:
        with self._lock:
            self.notifications_attempted += attempted
            self.notifications_failed += failed

    def inc_backhaul_failovers(self, count: int = 1) -> None:
        with self._lock:
            self.backhaul_failovers += count

    def record_ingest_latency(self, latency_ms: float) -> None:
        with self._lock:
            self._ingest_latencies.append(latency_ms)
            if len(self._ingest_latencies) > 50:
                self._ingest_latencies.pop(0)

    def record_inference_latency(self, latency_ms: float) -> None:
        with self._lock:
            self._inference_latencies.append(latency_ms)
            if len(self._inference_latencies) > 50:
                self._inference_latencies.pop(0)

    def get_metrics(self) -> Dict[str, Any]:
        with self._lock:
            uptime_seconds = round(time.time() - self._start_time, 2)
            avg_ingest_ms = round(sum(self._ingest_latencies) / len(self._ingest_latencies), 2) if self._ingest_latencies else 0.0
            avg_infer_ms = round(sum(self._inference_latencies) / len(self._inference_latencies), 2) if self._inference_latencies else 0.0

            return {
                "uptime_seconds": uptime_seconds,
                "timestamp": _utc_now_iso(),
                "counters": {
                    "telemetry_received_total": self.telemetry_received_total,
                    "telemetry_rejected_total": self.telemetry_rejected_total,
                    "lora_packets_received": self.lora_packets_received,
                    "lora_packets_lost": self.lora_packets_lost,
                    "ml_inference_total": self.ml_inference_total,
                    "ml_inference_errors": self.ml_inference_errors,
                    "alerts_generated": self.alerts_generated,
                    "notifications_attempted": self.notifications_attempted,
                    "notifications_failed": self.notifications_failed,
                    "backhaul_failovers": self.backhaul_failovers,
                },
                "latencies_ms": {
                    "avg_ingestion_latency_ms": avg_ingest_ms,
                    "avg_inference_latency_ms": avg_infer_ms,
                    "recent_samples_count": len(self._ingest_latencies),
                },
            }

    def reset(self) -> None:
        with self._lock:
            self._start_time = time.time()
            self.telemetry_received_total = 0
            self.telemetry_rejected_total = 0
            self.lora_packets_received = 0
            self.lora_packets_lost = 0
            self.ml_inference_total = 0
            self.ml_inference_errors = 0
            self.alerts_generated = 0
            self.notifications_attempted = 0
            self.notifications_failed = 0
            self.backhaul_failovers = 0
            self._ingest_latencies.clear()
            self._inference_latencies.clear()


# Global metrics collector singleton
metrics_collector = MetricsCollector()
