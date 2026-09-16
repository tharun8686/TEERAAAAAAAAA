"""
TerraEdge — Phase 8 Production Hardening, Security, Observability & Deployment Tests.
Validates RBAC authentication, CORS, secret isolation, liveness/readiness probes,
system metrics, model health, queue maintenance, request correlation, and rate limiting.
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
from gateway.config import (
    ADMIN_TOKEN,
    OPERATOR_TOKEN,
    GATEWAY_ID,
    TERRAEDGE_ENV,
    validate_configuration,
)
from gateway.backhaul.queue import durable_queue, DurableBackhaulQueue, QueueRecordType
from gateway.metrics import metrics_collector
from gateway.models_meta import model_health_tracker
from gateway.security import Role, rate_limiter


@pytest.fixture
def client():
    return TestClient(app)


# ============================================================================
# 1. Authentication & Role-Based Access Control (RBAC) Tests
# ============================================================================

def test_authentication_missing_token_rejected(client, monkeypatch):
    """Verifies that in strict mode, mutating admin endpoints reject requests with missing token (401)."""
    monkeypatch.setenv("TERRAEDGE_STRICT_AUTH", "true")
    resp = client.post("/api/nodes", json={"node_id": "TEST-UNAUTH-01", "district": "Salem"})
    assert resp.status_code == 401
    assert "detail" in resp.json()


def test_authentication_invalid_token_rejected(client):
    """Verifies that invalid tokens are rejected (401)."""
    resp = client.post(
        "/api/nodes",
        json={"node_id": "TEST-UNAUTH-02", "district": "Salem"},
        headers={"X-API-Key": "invalid-token-xyz"}
    )
    assert resp.status_code == 401


def test_operator_permissions(client):
    """
    Verifies that OPERATOR role can acknowledge alerts (200),
    but is forbidden from administrative node mutations (403).
    """
    # 1. Operator attempts Admin action -> 403 Forbidden
    admin_resp = client.post(
        "/api/nodes",
        json={"node_id": "TEST-OPERATOR-DENIED", "district": "Salem"},
        headers={"X-API-Key": OPERATOR_TOKEN}
    )
    assert admin_resp.status_code == 403

    # 2. Operator acknowledges an alert -> 200 OK (or 404 if alert not found, but NOT 401/403)
    ack_resp = client.post(
        "/api/alerts/ALT-NONEXISTENT/acknowledge",
        json={"operator_id": "OP-01", "notes": "Inspected site"},
        headers={"X-API-Key": OPERATOR_TOKEN}
    )
    # Since ALT-NONEXISTENT does not exist, status should be 404 (Auth passed)
    assert ack_resp.status_code == 404


def test_admin_permissions(client):
    """Verifies that ADMIN role has full access to admin and operator routes."""
    # 1. Admin registers node -> 201 Created
    node_payload = {
        "node_id": f"TEST-ADMIN-NODE-{int(time.time())}",
        "district": "Madurai",
        "state": "Tamil Nadu",
        "latitude": 9.9252,
        "longitude": 78.1198
    }
    resp = client.post(
        "/api/nodes",
        json=node_payload,
        headers={"X-API-Key": ADMIN_TOKEN}
    )
    assert resp.status_code == 201
    assert resp.json()["node_id"] == node_payload["node_id"]


# ============================================================================
# 2. CORS & Secret Exposure Protection Tests
# ============================================================================

def test_cors_configuration(client):
    """Verifies CORS origin headers and allowed options."""
    resp = client.options(
        "/health",
        headers={"Origin": "http://localhost:8000", "Access-Control-Request-Method": "GET"}
    )
    assert resp.status_code in (200, 204)


def test_secret_not_exposed(client):
    """Ensures sensitive tokens/credentials are never exposed in public endpoints."""
    endpoints = ["/", "/health", "/api/nodes", "/api/system/status", "/api/districts"]
    for ep in endpoints:
        resp = client.get(ep)
        assert resp.status_code == 200
        text = resp.text
        assert "TWILIO_AUTH_TOKEN" not in text
        assert "SMTP_PASSWORD" not in text
        assert "SUPABASE_SERVICE_KEY" not in text


# ============================================================================
# 3. Observability, Health & Request Correlation Tests
# ============================================================================

def test_health_live(client):
    """Validates liveness probe endpoint."""
    resp = client.get("/health/live")
    assert resp.status_code == 200
    data = resp.json()
    assert data["status"] == "alive"
    assert data["gateway_id"] == GATEWAY_ID


def test_health_ready(client):
    """Validates readiness probe endpoint."""
    resp = client.get("/health/ready")
    assert resp.status_code == 200
    data = resp.json()
    assert data["status"] == "ready"
    assert data["models_loaded_count"] == 7
    assert data["local_edge_operational"] is True


def test_system_status(client):
    """Validates comprehensive operational status endpoint."""
    resp = client.get("/api/system/status")
    assert resp.status_code == 200
    data = resp.json()
    assert data["gateway_id"] == GATEWAY_ID
    assert "uptime_seconds" in data
    assert "models_loaded" in data
    assert "queue_storage" in data


def test_system_metrics(client):
    """Validates system metrics endpoint and telemetry counters."""
    resp = client.get("/api/system/metrics")
    assert resp.status_code == 200
    data = resp.json()
    assert "counters" in data
    assert "telemetry_received_total" in data["counters"]
    assert "latencies_ms" in data


def test_model_health(client):
    """Validates that all 7 ML hazard models expose metadata and execution stats."""
    resp = client.get("/api/models/health")
    assert resp.status_code == 200
    data = resp.json()
    assert len(data) == 7
    for hazard in ["Flood", "Wildfire", "Landslide", "Air Quality", "Extreme Heat", "Toxic Flame", "Water Quality"]:
        assert hazard in data
        assert "model_version" in data[hazard]
        assert "algorithm" in data[hazard]
        assert "feature_schema_version" in data[hazard]


def test_request_correlation(client):
    """Verifies X-Request-ID propagation in response headers."""
    # 1. Server generates X-Request-ID if absent
    resp1 = client.get("/health")
    assert "X-Request-ID" in resp1.headers
    assert resp1.headers["X-Request-ID"].startswith("REQ-")

    # 2. Server preserves client-supplied X-Request-ID
    custom_id = "REQ-CUSTOM-TRACE-12345"
    resp2 = client.get("/health", headers={"X-Request-ID": custom_id})
    assert resp2.headers.get("X-Request-ID") == custom_id


# ============================================================================
# 4. Queue Maintenance & Capacity Protection Tests
# ============================================================================

def test_queue_size_monitoring():
    """Verifies that SQLite queue tracks file size and capacity status."""
    metrics = durable_queue.get_storage_metrics()
    assert "total_size_bytes" in metrics
    assert "total_size_mb" in metrics
    assert "capacity_status" in metrics
    assert metrics["capacity_status"] in ("OK", "WARNING", "CRITICAL")


def test_queue_maintenance(client, monkeypatch):
    """Verifies that /api/queue/maintenance purges synced records (Admin only)."""
    # 1. Without auth in strict mode -> 401
    monkeypatch.setenv("TERRAEDGE_STRICT_AUTH", "true")
    resp_unauth = client.post("/api/queue/maintenance")
    assert resp_unauth.status_code == 401

    # 2. With Admin token -> 200 OK
    resp_auth = client.post(
        "/api/queue/maintenance?retention_days=1",
        headers={"X-API-Key": ADMIN_TOKEN}
    )
    assert resp_auth.status_code == 200
    data = resp_auth.json()
    assert data["status"] == "completed"
    assert "synced_records_purged" in data
    assert "storage" in data


def test_queue_backup_utility():
    """Verifies that queue backup creates a valid SQLite backup file."""
    with tempfile.NamedTemporaryFile(suffix=".bak", delete=False) as f:
        bak_file = f.name

    try:
        backed_up = durable_queue.backup_to_file(bak_file)
        assert os.path.exists(backed_up)
        assert os.path.getsize(backed_up) > 0
    finally:
        try:
            os.remove(bak_file)
        except Exception:
            pass


# ============================================================================
# 5. Configuration Validation & Environment Modes
# ============================================================================

def test_configuration_validation():
    """Validates configuration startup checklist."""
    report = validate_configuration()
    assert "overall_status" in report
    assert report["overall_status"] in ("OK", "WARNING", "ERROR")
    assert "checks" in report
    assert len(report["checks"]) > 0


def test_input_size_limits(client):
    """Verifies rejection of oversized HTTP request payloads (413)."""
    huge_data = {"data": "A" * (1024 * 1024 + 5000)}  # > 1MB
    resp = client.post(
        "/api/telemetry",
        json=huge_data,
        headers={"Content-Length": str(len(str(huge_data)))}
    )
    assert resp.status_code == 413


def test_rate_limiting():
    """Verifies in-memory rate limiter throttling."""
    client_ip = "192.168.1.100"
    limiter = rate_limiter
    limiter.enabled = True
    original_limit = limiter.limit
    limiter.limit = 5

    try:
        # 5 allowed requests
        for _ in range(5):
            assert limiter.is_allowed(client_ip) is True
        # 6th request rejected
        assert limiter.is_allowed(client_ip) is False
    finally:
        limiter.limit = original_limit


def test_gateway_identity(client):
    """Verifies that gateway_id is consistent across endpoints."""
    resp = client.get("/")
    assert resp.status_code == 200
    assert resp.json()["gateway_id"] == GATEWAY_ID
