"""
TerraEdge — Durable SQLite Store-and-Forward Queue.
Guarantees zero data loss during network blackouts by persisting un-synchronized
telemetry, predictions, node registrations, alerts, and dispatches to local disk.
Survives gateway power cycles and process restarts.
"""

from __future__ import annotations
import datetime
import json
import os
import sqlite3
import threading
import uuid
from typing import Any, Dict, List, Optional, Union

from .schemas import (
    QueueRecord,
    QueueRecordType,
    QueueStatus,
    QueueSummaryResponse,
)


def _utc_now_iso() -> str:
    return datetime.datetime.now(datetime.timezone.utc).isoformat()


# Priority ordering for child-parent relational consistency
RECORD_TYPE_PRIORITY = {
    QueueRecordType.NODE.value: 1,
    QueueRecordType.TELEMETRY.value: 2,
    QueueRecordType.PREDICTION.value: 3,
    QueueRecordType.ALERT.value: 4,
    QueueRecordType.DISPATCH.value: 5,
}


class DurableBackhaulQueue:
    """
    Thread-safe SQLite persistent queue for edge-first store-and-forward telemetry.
    """

    def __init__(self, db_path: Optional[str] = None):
        if db_path is None:
            from ..config import BACKHAUL_QUEUE_DB_PATH
            self.db_path = BACKHAUL_QUEUE_DB_PATH
        else:
            self.db_path = db_path

        # Ensure directory exists
        db_dir = os.path.dirname(os.path.abspath(self.db_path))
        os.makedirs(db_dir, exist_ok=True)

        self._lock = threading.Lock()
        self._init_db()

    def _get_connection(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.db_path, timeout=10.0, check_same_thread=False)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA journal_mode=WAL;")
        conn.execute("PRAGMA busy_timeout=5000;")
        return conn

    def _init_db(self) -> None:
        with self._lock:
            conn = self._get_connection()
            try:
                with conn:
                    conn.execute("""
                    CREATE TABLE IF NOT EXISTS backhaul_queue (
                        queue_id TEXT PRIMARY KEY,
                        record_type TEXT NOT NULL,
                        record_id TEXT NOT NULL,
                        payload TEXT NOT NULL,
                        observed_at TEXT NOT NULL,
                        created_at TEXT NOT NULL,
                        synced_at TEXT,
                        retry_count INTEGER DEFAULT 0,
                        status TEXT DEFAULT 'PENDING',
                        last_error TEXT,
                        UNIQUE(record_type, record_id)
                    );
                    """)
                    conn.execute("""
                    CREATE INDEX IF NOT EXISTS idx_queue_status_type
                    ON backhaul_queue(status, record_type, created_at);
                    """)
            finally:
                conn.close()

    def enqueue(
        self,
        record_type: Union[QueueRecordType, str],
        record_id: str,
        payload: Dict[str, Any],
        observed_at: Optional[str] = None,
    ) -> QueueRecord:
        """
        Idempotently inserts or updates an item in the persistent queue.
        Guarantees that the physical sensor timestamp (observed_at) is preserved.
        """
        r_type = record_type.value if isinstance(record_type, QueueRecordType) else str(record_type)
        queue_id = f"Q-{r_type[:3].upper()}-{uuid.uuid4().hex[:8].upper()}"
        obs_time = observed_at or payload.get("timestamp") or payload.get("created_at") or _utc_now_iso()
        created_time = _utc_now_iso()
        payload_str = json.dumps(payload, default=str)

        with self._lock:
            conn = self._get_connection()
            try:
                with conn:
                    # Insert or update existing pending record
                    cursor = conn.execute("""
                    INSERT INTO backhaul_queue (
                        queue_id, record_type, record_id, payload, observed_at, created_at, status
                    ) VALUES (?, ?, ?, ?, ?, ?, 'PENDING')
                    ON CONFLICT(record_type, record_id) DO UPDATE SET
                        payload = excluded.payload,
                        retry_count = 0,
                        status = 'PENDING',
                        last_error = NULL
                    RETURNING queue_id, record_type, record_id, payload, observed_at, created_at, synced_at, retry_count, status, last_error;
                    """, (queue_id, r_type, record_id, payload_str, obs_time, created_time))
                    row = cursor.fetchone()
                    return self._row_to_record(row)
            finally:
                conn.close()

    def fetch_pending(
        self,
        batch_size: int = 50,
        record_types: Optional[List[QueueRecordType]] = None,
    ) -> List[QueueRecord]:
        """
        Retrieves pending records ordered strictly by relational dependency:
        NODE -> TELEMETRY -> PREDICTION -> ALERT -> DISPATCH.
        """
        with self._lock:
            conn = self._get_connection()
            try:
                query = """
                SELECT queue_id, record_type, record_id, payload, observed_at, created_at, synced_at, retry_count, status, last_error
                FROM backhaul_queue
                WHERE status IN ('PENDING', 'SYNCING')
                ORDER BY
                    CASE record_type
                        WHEN 'node' THEN 1
                        WHEN 'telemetry' THEN 2
                        WHEN 'prediction' THEN 3
                        WHEN 'alert' THEN 4
                        WHEN 'dispatch' THEN 5
                        ELSE 6
                    END,
                    created_at ASC
                LIMIT ?
                """
                cursor = conn.execute(query, (batch_size,))
                rows = cursor.fetchall()
                return [self._row_to_record(r) for r in rows]
            finally:
                conn.close()

    def mark_syncing(self, queue_ids: List[str]) -> None:
        """Marks records as currently in-flight."""
        if not queue_ids:
            return
        with self._lock:
            conn = self._get_connection()
            try:
                with conn:
                    placeholders = ",".join("?" for _ in queue_ids)
                    conn.execute(
                        f"UPDATE backhaul_queue SET status = 'SYNCING' WHERE queue_id IN ({placeholders})",
                        queue_ids
                    )
            finally:
                conn.close()

    def mark_synced(self, queue_id: str, synced_at: Optional[str] = None) -> None:
        """Marks record as successfully delivered and synchronized to the cloud."""
        sync_time = synced_at or _utc_now_iso()
        with self._lock:
            conn = self._get_connection()
            try:
                with conn:
                    conn.execute("""
                    UPDATE backhaul_queue
                    SET status = 'SYNCED', synced_at = ?, last_error = NULL
                    WHERE queue_id = ?
                    """, (sync_time, queue_id))
            finally:
                conn.close()

    def mark_failed(self, queue_id: str, error: str, max_retries: int = 5) -> None:
        """Increments retry count and sets FAILED status if maximum retry attempts exceeded."""
        with self._lock:
            conn = self._get_connection()
            try:
                with conn:
                    conn.execute("""
                    UPDATE backhaul_queue
                    SET retry_count = retry_count + 1,
                        status = CASE WHEN retry_count + 1 >= ? THEN 'FAILED' ELSE 'PENDING' END,
                        last_error = ?
                    WHERE queue_id = ?
                    """, (max_retries, error, queue_id))
            finally:
                conn.close()

    def get_pending_count(self) -> int:
        """Returns count of items currently waiting to be synchronized."""
        with self._lock:
            conn = self._get_connection()
            try:
                cursor = conn.execute(
                    "SELECT COUNT(*) FROM backhaul_queue WHERE status IN ('PENDING', 'SYNCING')"
                )
                return int(cursor.fetchone()[0])
            finally:
                conn.close()

    def get_summary(self) -> QueueSummaryResponse:
        """Constructs safe operational summary of the local SQLite queue."""
        with self._lock:
            conn = self._get_connection()
            try:
                cursor = conn.execute("""
                SELECT
                    COUNT(*) as total,
                    SUM(CASE WHEN status IN ('PENDING', 'SYNCING') THEN 1 ELSE 0 END) as pending_cnt,
                    SUM(CASE WHEN status = 'SYNCED' THEN 1 ELSE 0 END) as synced_cnt,
                    SUM(CASE WHEN status = 'FAILED' THEN 1 ELSE 0 END) as failed_cnt,
                    MIN(CASE WHEN status IN ('PENDING', 'SYNCING') THEN observed_at ELSE NULL END) as oldest_pending
                FROM backhaul_queue
                """)
                row = cursor.fetchone()
                total = row["total"] or 0
                pending = row["pending_cnt"] or 0
                synced = row["synced_cnt"] or 0
                failed = row["failed_cnt"] or 0
                oldest = row["oldest_pending"]

                # Group by record type
                type_cursor = conn.execute("""
                SELECT record_type, COUNT(*) as cnt
                FROM backhaul_queue
                WHERE status IN ('PENDING', 'SYNCING')
                GROUP BY record_type
                """)
                types_map = {r["record_type"]: r["cnt"] for r in type_cursor.fetchall()}

                return QueueSummaryResponse(
                    queue_size=pending,
                    pending_count=pending,
                    synced_count=synced,
                    failed_count=failed,
                    oldest_record_time=oldest,
                    record_types=types_map,
                    db_path=self.db_path,
                )
            finally:
                conn.close()

    def purge_synced(self, retention_days: int = 7) -> int:
        """
        Safely deletes SYNCED records older than retention_days.
        Never touches PENDING or SYNCING records.
        """
        cutoff = (
            datetime.datetime.now(datetime.timezone.utc)
            - datetime.timedelta(days=retention_days)
        ).isoformat()

        with self._lock:
            conn = self._get_connection()
            try:
                with conn:
                    cursor = conn.execute(
                        "DELETE FROM backhaul_queue WHERE status = 'SYNCED' AND synced_at < ?",
                        (cutoff,)
                    )
                    return cursor.rowcount
            finally:
                conn.close()

    def purge_failed(self, max_age_days: int = 30) -> int:
        """Purges old poisoned / dead-letter records."""
        cutoff = (
            datetime.datetime.now(datetime.timezone.utc)
            - datetime.timedelta(days=max_age_days)
        ).isoformat()

        with self._lock:
            conn = self._get_connection()
            try:
                with conn:
                    cursor = conn.execute(
                        "DELETE FROM backhaul_queue WHERE status = 'FAILED' AND created_at < ?",
                        (cutoff,)
                    )
                    return cursor.rowcount
            finally:
                conn.close()

    def get_storage_metrics(self) -> Dict[str, Any]:
        """Calculates SQLite database file size and assesses disk capacity risk."""
        from ..config import QUEUE_MAX_SIZE_MB

        file_size_bytes = 0
        wal_size_bytes = 0
        if os.path.exists(self.db_path):
            file_size_bytes = os.path.getsize(self.db_path)
        wal_path = f"{self.db_path}-wal"
        if os.path.exists(wal_path):
            wal_size_bytes = os.path.getsize(wal_path)

        total_bytes = file_size_bytes + wal_size_bytes
        total_mb = round(total_bytes / (1024 * 1024), 3)
        pending_cnt = self.get_pending_count()

        is_near_capacity = total_mb > (QUEUE_MAX_SIZE_MB * 0.8)
        is_exceeded = total_mb >= QUEUE_MAX_SIZE_MB

        return {
            "db_path": self.db_path,
            "db_size_bytes": file_size_bytes,
            "wal_size_bytes": wal_size_bytes,
            "total_size_bytes": total_bytes,
            "total_size_mb": total_mb,
            "max_threshold_mb": QUEUE_MAX_SIZE_MB,
            "pending_records": pending_cnt,
            "capacity_status": "CRITICAL" if is_exceeded else ("WARNING" if is_near_capacity else "OK"),
            "warning": is_near_capacity or is_exceeded,
        }

    def backup_to_file(self, dest_path: str) -> str:
        """
        Executes a live, online, crash-consistent hot backup using SQLite Backup API.
        """
        dest_dir = os.path.dirname(os.path.abspath(dest_path))
        os.makedirs(dest_dir, exist_ok=True)

        with self._lock:
            src_conn = self._get_connection()
            dst_conn = sqlite3.connect(dest_path)
            try:
                with dst_conn:
                    src_conn.backup(dst_conn, pages=100)
                return dest_path
            finally:
                dst_conn.close()
                src_conn.close()

    def clear(self) -> None:
        """Clears all records from queue (used in automated test resets)."""
        with self._lock:
            conn = self._get_connection()
            try:
                with conn:
                    conn.execute("DELETE FROM backhaul_queue")
            finally:
                conn.close()

    @staticmethod
    def _row_to_record(row: sqlite3.Row) -> QueueRecord:
        try:
            payload_dict = json.loads(row["payload"])
        except Exception:
            payload_dict = {}

        return QueueRecord(
            queue_id=row["queue_id"],
            record_type=QueueRecordType(row["record_type"]),
            record_id=row["record_id"],
            payload=payload_dict,
            observed_at=row["observed_at"],
            created_at=row["created_at"],
            synced_at=row["synced_at"],
            retry_count=row["retry_count"],
            status=QueueStatus(row["status"]),
            last_error=row["last_error"],
        )


# Global durable queue singleton
durable_queue = DurableBackhaulQueue()
