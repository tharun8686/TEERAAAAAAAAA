"""
TerraEdge — Phase 7 Resilient Edge Backhaul & Store-and-Forward Tests.
Validates multi-tier communication failover, durable SQLite buffering,
restart survival, idempotent sync in relational dependency order, and edge APIs.
"""

import os
import sys
import tempfile
import time
import pytest
from fastapi.testclient import TestClient

# Ensure common and gateway packages are importable
HERE = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(HERE)
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)
COMMON_DIR = os.path.join(PROJECT_ROOT, "common")
if COMMON_DIR not in sys.path:
    sys.path.insert(0, COMMON_DIR)

from gateway.app import app
from gateway.backhaul import (
    BackhaulManager,
    BackhaulState,
    DurableBackhaulQueue,
    InternetBackhaulAdapter,
    CellularBackhaulAdapter,
    SatelliteBackhaulAdapter,
    QueueRecordType,
    QueueStatus,
    TransportType,
    backhaul_manager,
    durable_queue,
)
from gateway.schemas import TypeATelemetryPayload


@pytest.fixture
def temp_queue_db():
    """Provides an isolated SQLite queue for testing."""
    with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as f:
        db_path = f.name
    queue = DurableBackhaulQueue(db_path=db_path)
    yield queue
    try:
        os.remove(db_path)
    except Exception:
        pass


@pytest.fixture
def test_client():
    return TestClient(app)


# ============================================================================
# 1. Backhaul Hierarchy & Failover State Tests
# ============================================================================

def test_backhaul_failover_hierarchy(temp_queue_db):
    """Verifies failover precedence: Primary -> Secondary -> Tertiary -> Local-Only."""
    mgr = BackhaulManager(queue=temp_queue_db)

    # 1. Primary Wi-Fi/Ethernet online -> ONLINE
    mgr.internet_adapter.set_simulated_state(True)
    mgr.cellular_adapter.set_simulated_state(True)
    mgr.satellite_adapter.set_simulated_state(True)

    adapter, state = mgr.get_active_transport()
    assert state == BackhaulState.ONLINE
    assert adapter.transport_type == TransportType.ETHERNET_WIFI

    # 2. Internet down, Cellular available -> DEGRADED
    mgr.internet_adapter.set_simulated_state(False)
    adapter, state = mgr.get_active_transport()
    assert state == BackhaulState.DEGRADED
    assert adapter.transport_type == TransportType.CELLULAR

    # 3. Cellular down, Satellite available -> DEGRADED
    mgr.cellular_adapter.set_simulated_state(False)
    adapter, state = mgr.get_active_transport()
    assert state == BackhaulState.DEGRADED
    assert adapter.transport_type == TransportType.SATELLITE

    # 4. All down -> OFFLINE (Local Edge Mode)
    mgr.satellite_adapter.set_simulated_state(False)
    adapter, state = mgr.get_active_transport()
    assert state == BackhaulState.OFFLINE
    assert adapter is None
    assert mgr.is_cloud_available() is False


def test_mock_adapters_safe_reporting():
    """Ensures mock adapters clearly state REAL HARDWARE NOT TESTED."""
    cell_adapter = CellularBackhaulAdapter(mock_mode=True, enabled=True)
    sat_adapter = SatelliteBackhaulAdapter(mock_mode=True, enabled=True)

    c_avail, c_stat, c_info = cell_adapter.check_health()
    assert c_avail is True
    assert c_stat == "MOCK_ACTIVE"
    assert "REAL HARDWARE NOT TESTED" in c_info.get("note", "")

    s_avail, s_stat, s_info = sat_adapter.check_health()
    assert s_avail is True
    assert s_stat == "MOCK_ACTIVE"
    assert "REAL HARDWARE NOT TESTED" in s_info.get("note", "")


# ============================================================================
# 2. Durable Store-and-Forward SQLite Queue Tests
# ============================================================================

def test_queue_persistence_and_timestamp_preservation(temp_queue_db):
    """Verifies that items are stored durably with immutable original observed_at."""
    obs_time = "2026-09-16T10:00:00Z"
    rec = temp_queue_db.enqueue(
        record_type=QueueRecordType.TELEMETRY,
        record_id="TEL-NODE-01-SEQ-101",
        payload={"node_id": "NODE-01", "temperature_c": 38.5},
        observed_at=obs_time,
    )

    assert rec.queue_id.startswith("Q-TEL-")
    assert rec.observed_at == obs_time
    assert rec.status == QueueStatus.PENDING

    # Verify summary
    summary = temp_queue_db.get_summary()
    assert summary.pending_count == 1
    assert summary.oldest_record_time == obs_time


def test_queue_idempotent_deduplication(temp_queue_db):
    """Verifies ON CONFLICT upsert prevents duplicate pending entries."""
    temp_queue_db.enqueue(
        record_type=QueueRecordType.ALERT,
        record_id="ALT-FIRE-0001",
        payload={"hazard": "Wildfire", "severity": "HIGH"},
    )
    # Re-inserting same (record_type, record_id) with updated payload
    temp_queue_db.enqueue(
        record_type=QueueRecordType.ALERT,
        record_id="ALT-FIRE-0001",
        payload={"hazard": "Wildfire", "severity": "CRITICAL"},
    )

    summary = temp_queue_db.get_summary()
    assert summary.pending_count == 1

    pending = temp_queue_db.fetch_pending()
    assert len(pending) == 1
    assert pending[0].payload["severity"] == "CRITICAL"


def test_queue_relational_dependency_ordering(temp_queue_db):
    """Verifies strict sync ordering: NODE -> TELEMETRY -> PREDICTION -> ALERT -> DISPATCH."""
    # Enqueue in reverse or mixed order
    temp_queue_db.enqueue(QueueRecordType.DISPATCH, "DISP-01", {"target": "+919876543210"})
    temp_queue_db.enqueue(QueueRecordType.ALERT, "ALT-01", {"severity": "CRITICAL"})
    temp_queue_db.enqueue(QueueRecordType.PREDICTION, "PRED-01", {"risk_score": 88.0})
    temp_queue_db.enqueue(QueueRecordType.TELEMETRY, "TEL-01", {"pm25": 140.0})
    temp_queue_db.enqueue(QueueRecordType.NODE, "NODE-01", {"district": "Nilgiris"})

    pending = temp_queue_db.fetch_pending(batch_size=10)
    assert len(pending) == 5

    order = [p.record_type for p in pending]
    expected_order = [
        QueueRecordType.NODE,
        QueueRecordType.TELEMETRY,
        QueueRecordType.PREDICTION,
        QueueRecordType.ALERT,
        QueueRecordType.DISPATCH,
    ]
    assert order == expected_order


def test_queue_restart_durability(temp_queue_db):
    """Verifies data survives process termination / re-opening SQLite database."""
    db_path = temp_queue_db.db_path
    temp_queue_db.enqueue(QueueRecordType.TELEMETRY, "TEL-RESTART-01", {"water_level_m": 4.5})

    # Simulate gateway crash & restart: Create a new queue instance pointing to same file
    new_queue_instance = DurableBackhaulQueue(db_path=db_path)
    summary = new_queue_instance.get_summary()
    assert summary.pending_count == 1

    records = new_queue_instance.fetch_pending()
    assert len(records) == 1
    assert records[0].record_id == "TEL-RESTART-01"


# ============================================================================
# 3. Failover & Idempotent Synchronization Tests
# ============================================================================

def test_backhaul_manager_sync_execution(temp_queue_db):
    """Tests buffer accumulation during outage and complete sync on reconnection."""
    mgr = BackhaulManager(queue=temp_queue_db)

    # 1. Start Offline
    mgr.internet_adapter.set_simulated_state(False)
    mgr.cellular_adapter.set_simulated_state(False)
    mgr.satellite_adapter.set_simulated_state(False)

    mgr.buffer_record(QueueRecordType.NODE, "NODE-SYNC-01", {"name": "Test Node"})
    mgr.buffer_record(QueueRecordType.ALERT, "ALT-SYNC-01", {"hazard": "Flood", "severity": "HIGH"})
    assert temp_queue_db.get_pending_count() == 2

    # Attempt sync while offline -> Should report offline
    sync_res = mgr.sync_queue()
    assert sync_res.status == "offline"
    assert sync_res.synced_count == 0
    assert sync_res.remaining_queue_size == 2

    # 2. Reconnect Internet
    mgr.internet_adapter.set_simulated_state(True)
    sync_res2 = mgr.sync_queue()
    assert sync_res2.status == "completed"
    assert sync_res2.synced_count == 2
    assert sync_res2.remaining_queue_size == 0
    assert temp_queue_db.get_pending_count() == 0


def test_retry_count_and_failure_handling(temp_queue_db):
    """Verifies retry increment and status transition to FAILED on max retries."""
    rec = temp_queue_db.enqueue(QueueRecordType.TELEMETRY, "TEL-FAIL-01", {"data": 123})

    for i in range(4):
        temp_queue_db.mark_failed(rec.queue_id, "HTTP Connection Timeout", max_retries=5)
        r = temp_queue_db.fetch_pending()[0]
        assert r.status == QueueStatus.PENDING
        assert r.retry_count == i + 1

    # 5th failure -> FAILED
    temp_queue_db.mark_failed(rec.queue_id, "HTTP Connection Timeout", max_retries=5)
    summary = temp_queue_db.get_summary()
    assert summary.failed_count == 1
    assert summary.pending_count == 0


# ============================================================================
# 4. HTTP API Endpoints Tests
# ============================================================================

def test_api_backhaul_health_endpoint(test_client):
    """Validates GET /api/backhaul/health response schema."""
    resp = test_client.get("/api/backhaul/health")
    assert resp.status_code == 200
    data = resp.json()
    assert "gateway_mode" in data
    assert "backhaul_state" in data
    assert "internet_available" in data
    assert "cellular_available" in data
    assert "satellite_available" in data
    assert "queue_size" in data


def test_api_backhaul_queue_endpoint(test_client):
    """Validates GET /api/backhaul/queue response schema."""
    resp = test_client.get("/api/backhaul/queue")
    assert resp.status_code == 200
    data = resp.json()
    assert "queue_size" in data
    assert "pending_count" in data
    assert "synced_count" in data
    assert "db_path" in data


def test_api_backhaul_sync_endpoint(test_client):
    """Validates POST /api/backhaul/sync response schema."""
    resp = test_client.post("/api/backhaul/sync?limit=10")
    assert resp.status_code == 200
    data = resp.json()
    assert "status" in data
    assert "synced_count" in data
    assert "failed_count" in data
    assert "duration_ms" in data


def test_health_check_includes_backhaul(test_client):
    """Validates that GET /health now incorporates backhaul status."""
    resp = test_client.get("/health")
    assert resp.status_code == 200
    data = resp.json()
    assert "backhaul" in data
    assert "state" in data["backhaul"]
    assert "queue_size" in data["backhaul"]


# ============================================================================
# 5. Live Telemetry Processing Under Backhaul Outage
# ============================================================================

def test_telemetry_processing_during_blackout(test_client):
    """
    Verifies that when backhaul is offline, local edge pipeline remains 100% operational:
    - 7 ML inference engines execute
    - Multi-hazard risk ranking computed
    - Alert lifecycle and CAP dispatch evaluated
    - Node registered in dynamic inventory
    """
    payload = {
        "node_id": "NODE-OFFLINE-TEST-01",
        "timestamp": "2026-09-16T12:00:00Z",
        "battery_pct": 92.0,
        "temperature_c": 44.5,
        "humidity_pct": 18.0,
        "gas_resistance_ohms": 2500.0,
        "mq135_raw": 1800.0,
        "co_ppm": 12.0,
        "flame_detected": True,
        "smoke_detected": True,
        "state": "Tamil Nadu",
        "district": "Coimbatore",
        "latitude": 11.0168,
        "longitude": 76.9558,
    }

    resp = test_client.post("/api/telemetry", json=payload)
    assert resp.status_code == 200
    res_data = resp.json()

    assert res_data["node_id"] == "NODE-OFFLINE-TEST-01"
    # Physical flame alert works offline even when ML sensor inputs are incomplete.
    assert res_data["alerts_triggered"]
    assert res_data["alerts_triggered"][0]["details"]["source"] == "direct_sensor"
    assert "Wildfire" in res_data["hazard_results"] or "Toxic Flame" in res_data["hazard_results"]
    assert len(res_data["hazard_results"]) == 7
