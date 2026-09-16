"""
TerraEdge — Phase 7 Failover Backhaul Manager & Store-and-Forward Orchestrator.
Monitors multi-tier backhaul paths (Ethernet/Wi-Fi -> Cellular -> Satellite),
manages seamless failover to Local-Only mode, and synchronizes queued records
in strict relational dependency order when connectivity returns.
"""

from __future__ import annotations
import asyncio
import datetime
import threading
import time
from typing import Any, Dict, List, Optional, Tuple

from ..config import (
    BACKHAUL_MAX_RETRIES,
    BACKHAUL_MODE,
    BACKHAUL_SYNC_INTERVAL_S,
    CELLULAR_ENABLED,
    CELLULAR_MOCK_MODE,
    CELLULAR_PORT,
    SATELLITE_ENABLED,
    SATELLITE_MOCK_MODE,
    SATELLITE_PORT,
)
from .adapters.base import BaseBackhaulAdapter
from .adapters.cellular import CellularBackhaulAdapter
from .adapters.internet import InternetBackhaulAdapter
from .adapters.satellite import SatelliteBackhaulAdapter
from .queue import DurableBackhaulQueue, durable_queue
from .schemas import (
    BackhaulHealthResponse,
    BackhaulState,
    QueueRecord,
    QueueRecordType,
    SyncResponse,
    TransportType,
)


def _utc_now_iso() -> str:
    return datetime.datetime.now(datetime.timezone.utc).isoformat()


class BackhaulManager:
    """
    Central backhaul failover orchestrator for the Type B Edge Gateway.
    Guarantees continuous local edge intelligence and zero-data-loss buffering.
    """

    def __init__(
        self,
        queue: Optional[DurableBackhaulQueue] = None,
        sync_interval_s: float = BACKHAUL_SYNC_INTERVAL_S,
        max_retries: int = BACKHAUL_MAX_RETRIES,
    ):
        self.queue = queue or durable_queue
        self.sync_interval_s = sync_interval_s
        self.max_retries = max_retries
        self._lock = threading.Lock()

        # Initialize Adapters
        self.internet_adapter = InternetBackhaulAdapter()
        self.cellular_adapter = CellularBackhaulAdapter(
            port=CELLULAR_PORT,
            mock_mode=CELLULAR_MOCK_MODE,
            enabled=CELLULAR_ENABLED,
        )
        self.satellite_adapter = SatelliteBackhaulAdapter(
            port=SATELLITE_PORT,
            mock_mode=SATELLITE_MOCK_MODE,
            enabled=SATELLITE_ENABLED,
        )

        self.transports: List[BaseBackhaulAdapter] = [
            self.internet_adapter,
            self.cellular_adapter,
            self.satellite_adapter,
        ]

        self.last_sync_time: Optional[str] = None
        self.last_failure_reason: Optional[str] = None
        self._sync_in_progress = False
        self._bg_task: Optional[asyncio.Task] = None

    # ========================================================================
    # 1. Backhaul State & Failover Evaluation
    # ========================================================================

    def get_active_transport(self) -> Tuple[Optional[BaseBackhaulAdapter], BackhaulState]:
        """
        Evaluates prioritized backhaul hierarchy:
        1. Wi-Fi / Ethernet -> ONLINE
        2. Cellular -> DEGRADED
        3. Satellite -> DEGRADED
        4. None -> OFFLINE (Local Edge Mode)
        """
        if BACKHAUL_MODE == "mock_offline":
            return None, BackhaulState.OFFLINE
        if BACKHAUL_MODE == "mock_reconnect":
            return self.internet_adapter, BackhaulState.ONLINE

        # Primary: Wi-Fi / Ethernet
        if self.internet_adapter.is_available():
            return self.internet_adapter, BackhaulState.ONLINE

        # Secondary: Cellular
        if self.cellular_adapter.is_available():
            return self.cellular_adapter, BackhaulState.DEGRADED

        # Tertiary: Satellite
        if self.satellite_adapter.is_available():
            return self.satellite_adapter, BackhaulState.DEGRADED

        # All down -> Local Edge Mode
        return None, BackhaulState.OFFLINE

    def is_cloud_available(self) -> bool:
        """Returns True if any external backhaul path is functional."""
        adapter, _ = self.get_active_transport()
        return adapter is not None

    def get_health(self) -> BackhaulHealthResponse:
        """Constructs safe operational health summary of all backhaul paths."""
        adapter, state = self.get_active_transport()
        queue_cnt = self.queue.get_pending_count()

        sync_state = "SYNCED" if queue_cnt == 0 else ("SYNCING" if self._sync_in_progress else "PENDING")

        active_t = adapter.transport_type if adapter else None
        return BackhaulHealthResponse(
            gateway_mode="LOCAL_EDGE",
            backhaul_state=state,
            active_transport=active_t,
            internet_available=self.internet_adapter.is_available(),
            cellular_available=self.cellular_adapter.is_available(),
            satellite_available=self.satellite_adapter.is_available(),
            queue_size=queue_cnt,
            sync_state=sync_state,
            last_sync_time=self.last_sync_time,
            last_failure_reason=self.last_failure_reason,
            timestamp=_utc_now_iso(),
        )

    # ========================================================================
    # 2. Store-and-Forward Ingestion & Enqueueing
    # ========================================================================

    def buffer_record(
        self,
        record_type: QueueRecordType,
        record_id: str,
        payload: Dict[str, Any],
        observed_at: Optional[str] = None,
    ) -> QueueRecord:
        """Buffers a record into the durable SQLite queue."""
        return self.queue.enqueue(
            record_type=record_type,
            record_id=record_id,
            payload=payload,
            observed_at=observed_at,
        )

    # ========================================================================
    # 3. Synchronous / Batch Synchronization Worker
    # ========================================================================

    def sync_queue(self, batch_size: int = 50) -> SyncResponse:
        """
        Executes idempotent synchronization of pending records over active backhaul.
        Respects relational dependency ordering: NODE -> TELEMETRY -> PREDICTION -> ALERT -> DISPATCH.
        """
        start_time = time.perf_counter()
        adapter, state = self.get_active_transport()

        if not adapter:
            duration_ms = round((time.perf_counter() - start_time) * 1000.0, 2)
            self.last_failure_reason = "No active backhaul connection available for synchronization"
            return SyncResponse(
                status="offline",
                synced_count=0,
                failed_count=0,
                remaining_queue_size=self.queue.get_pending_count(),
                duration_ms=duration_ms,
                transport_used=None,
            )

        with self._lock:
            self._sync_in_progress = True

        synced = 0
        failed = 0

        try:
            pending_records = self.queue.fetch_pending(batch_size=batch_size)
            if pending_records:
                self.queue.mark_syncing([r.queue_id for r in pending_records])

            for record in pending_records:
                success, msg = adapter.send(record.payload, record.record_type.value)
                if success:
                    self.queue.mark_synced(record.queue_id)
                    synced += 1
                else:
                    self.queue.mark_failed(record.queue_id, msg, max_retries=self.max_retries)
                    failed += 1
                    self.last_failure_reason = msg

            if synced > 0:
                self.last_sync_time = _utc_now_iso()

        finally:
            with self._lock:
                self._sync_in_progress = False

        duration_ms = round((time.perf_counter() - start_time) * 1000.0, 2)
        remaining = self.queue.get_pending_count()

        return SyncResponse(
            status="completed" if failed == 0 else "partial",
            synced_count=synced,
            failed_count=failed,
            remaining_queue_size=remaining,
            duration_ms=duration_ms,
            transport_used=adapter.transport_type.value,
        )

    def get_queue_summary(self) -> QueueSummaryResponse:
        """Returns safe operational summary of the underlying durable queue."""
        return self.queue.get_summary()

    # ========================================================================
    # 4. Background Synchronization Loop
    # ========================================================================

    async def start_background_sync(self) -> None:
        """Runs periodic store-and-forward synchronization in background."""
        while True:
            try:
                await asyncio.sleep(self.sync_interval_s)
                if self.is_cloud_available() and self.queue.get_pending_count() > 0:
                    self.sync_queue(batch_size=50)
            except asyncio.CancelledError:
                break
            except Exception as exc:
                print(f"[backhaul] Background sync error: {exc}", flush=True)

    def stop_background_sync(self) -> None:
        """Cancels background sync task if active."""
        if self._bg_task and not self._bg_task.done():
            self._bg_task.cancel()


# Global backhaul manager singleton
backhaul_manager = BackhaulManager()

