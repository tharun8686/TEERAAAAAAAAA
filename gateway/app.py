"""
TerraEdge — Type B Edge Gateway API (Phase 8 Production Hardening).
Central FastAPI server providing unified telemetry ingestion, multi-hazard ML routing,
dynamic node registry lifecycle management, district risk aggregation,
spatial hotspot clustering, live GIS feeds, RBAC security, and observability metrics.
"""

from __future__ import annotations
import asyncio
import datetime
import os
import sys
import time
from typing import Any, Dict, List, Optional

from fastapi import Depends, FastAPI, HTTPException, Query, Request, status
from fastapi.middleware.cors import CORSMiddleware

# Ensure imports work from current and parent directory
HERE = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(HERE)
COMMON_DIR = os.path.join(PROJECT_ROOT, "common")
if COMMON_DIR not in sys.path:
    sys.path.append(COMMON_DIR)

try:
    import terra_supabase as db
except ImportError:
    db = None

from .config import (
    ALLOWED_ORIGINS, GATEWAY_HOST, GATEWAY_PORT, GATEWAY_ID, GATEWAY_ENV,
    TERRAEDGE_ENV, LOG_PREDICTIONS,
    LORA_ENABLED, LORA_MOCK_MODE, LORA_SERIAL_PORT, LORA_BAUD_RATE,
    LORA_ACK_ENABLED, LORA_ACK_TIMEOUT_MS, LORA_DEDUP_CACHE_SIZE,
    validate_configuration,
)
from .backhaul import (
    backhaul_manager,
    durable_queue,
    BackhaulHealthResponse,
    BackhaulState,
    QueueSummaryResponse,
    SyncResponse,
    QueueRecordType,
)
from .district_aggregation import district_engine
from .hazard_router import hazard_router
from .metrics import metrics_collector
from .models_meta import model_health_tracker
from .node_manager import node_manager
from .notifications import (
    alert_dispatcher,
    AlertAcknowledgeRequest,
    AlertLifecycleState,
    CanonicalAlert,
    ChannelType,
    DispatchRecord,
    ManualDispatchRequest,
    NotificationTarget,
    TargetCreateRequest,
    TargetUpdateRequest,
)
from .observability import logger, RequestCorrelationMiddleware
from .risk_engine import risk_engine
from .schemas import (
    DistrictHazardSummary,
    DistrictRiskResponse,
    HazardPredictionResult,
    HazardRanking,
    HotspotCluster,
    LoRaTransportMetadata,
    NodeDetailResponse,
    NodeRegistrationRequest,
    NodeUpdateRequest,
    RiskMapResponse,
    TypeATelemetryPayload,
    UnifiedGatewayResponse,
)
from .security import (
    require_admin,
    require_operator,
    rate_limiter,
    RequestSizeLimitMiddleware,
)
from .telemetry import telemetry_engine


app = FastAPI(
    title="TerraEdge Type B Edge Gateway API",
    description="Central Edge AI Gateway & Multi-Node Environmental Intelligence Backbone (Hardened)",
    version="8.0.0"
)

# 1. Request Correlation Middleware (Generates & Propagates X-Request-ID)
app.add_middleware(RequestCorrelationMiddleware)

# 2. Request Payload Size Limiting Middleware
app.add_middleware(RequestSizeLimitMiddleware)

# 3. Configurable CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS if ALLOWED_ORIGINS else ["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# In-memory latest telemetry & risk cache per node
_latest_node_evaluations: Dict[str, UnifiedGatewayResponse] = {}

# Global LoRa receiver instance
_lora_receiver = None


# ============================================================================
# Shared Telemetry Processing Function
# Called by BOTH the HTTP endpoint AND the LoRa receiver.
# ============================================================================

def process_type_a_telemetry(
    payload: TypeATelemetryPayload,
    transport_meta: Optional[LoRaTransportMetadata] = None,
) -> UnifiedGatewayResponse:
    """
    Core telemetry processing pipeline — transport-agnostic and multi-node isolated.

    Steps:
        1. Register/update node in dynamic inventory
        2. Compute temporal derivatives per node via telemetry engine
        3. Evaluate all 7 hazard models & update model health
        4. Aggregate multi-hazard risk and rank threats
        5. Update node-level risk cache in node manager
        6. Persist to Supabase / SQLite WAL fallback
        7. Record metrics & return unified composite response
    """
    start_time = time.perf_counter()
    node_id = payload.node_id

    # Track metrics
    metrics_collector.inc_telemetry_received(1)
    if transport_meta is not None:
        metrics_collector.inc_lora_packets(received=1, lost=0)

    # 1. Update Node Inventory
    node_info = node_manager.register_or_update(payload, transport_meta=transport_meta)

    # 2. Process Telemetry & Compute Derivatives (strictly per-node buffer)
    proc = telemetry_engine.process(payload)

    # 3. Execute Hazard Routing & Model Inferences
    infer_start = time.perf_counter()
    hazard_results: Dict[str, HazardPredictionResult] = hazard_router.evaluate_all(proc)
    infer_duration_ms = round((time.perf_counter() - infer_start) * 1000.0, 2)
    metrics_collector.record_inference_latency(infer_duration_ms)

    # Update model health registry
    for h_name, h_res in hazard_results.items():
        is_success = h_res.model_status == "success"
        model_health_tracker.record_inference(
            hazard=h_name,
            success=is_success,
            error_msg=h_res.error if not is_success else None
        )
    metrics_collector.inc_ml_inference(len(hazard_results), errors=sum(1 for r in hazard_results.values() if r.model_status != "success"))

    # 4. Multi-Hazard Risk Aggregation & Ranking
    composite_risk, primary_hazard, primary_severity, priority_score, ranked_hazards, alert_candidates = (
        risk_engine.evaluate_node_risk(node_id, hazard_results)
    )

    # Calculate top confidence for node summary
    top_conf = 0.0
    if primary_hazard and primary_hazard in hazard_results:
        top_conf = hazard_results[primary_hazard].confidence_pct
    elif ranked_hazards:
        top_conf = ranked_hazards[0].confidence_pct

    # 5. Cache risk summary in node registry
    node_manager.update_node_latest_predictions(
        node_id=node_id,
        primary_hazard=primary_hazard,
        risk_pct=composite_risk,
        severity=primary_severity,
        confidence_pct=top_conf
    )

    # 6. Database Persistence (Supabase / SQLite WAL Fallback)
    alerts_persisted = []
    payload_dict = payload.model_dump()
    db_mode = "in-memory"

    if db is not None:
        db_stat = db.status()
        db_mode = db_stat.get("mode", "in-memory")

        if LOG_PREDICTIONS:
            for h_name, h_res in hazard_results.items():
                if h_res.model_status == "success":
                    db.log_prediction(
                        hazard=h_name.lower().replace(" ", "_"),
                        node_id=node_id,
                        payload=payload_dict,
                        result=h_res.model_dump()
                    )

        for alert_entry in alert_candidates:
            h_name = alert_entry["hazard"]
            alert_row = {
                "alert_id": db.next_alert_id(h_name.lower(), "ALT-") if db else f"ALT-{h_name[:4].upper()}-{time.time_ns() % 1000000:06d}",
                "node_id": node_id,
                "severity": alert_entry["severity"],
                "risk_score_pct": alert_entry["risk_score_pct"],
                "confidence_pct": alert_entry["confidence_pct"],
                "top_features": alert_entry["top_features"],
                "timestamp": alert_entry["timestamp"],
                "details": alert_entry["details"]
            }
            if db is not None:
                db.insert_alert(h_name.lower(), alert_row)
            alerts_persisted.append(alert_row)
            metrics_collector.inc_alerts_generated(1)

            # Automated Multi-Channel Alert & Dispatch Pipeline
            alert_dispatcher.dispatch(
                alert_in={
                    **alert_row,
                    "state": node_info.get("state", "Tamil Nadu"),
                    "district": node_info.get("district"),
                    "zone": node_info.get("zone"),
                    "latitude": node_info.get("latitude"),
                    "longitude": node_info.get("longitude"),
                    "is_simulated": node_info.get("is_simulated", False),
                    "affected_nodes": [node_id],
                },
                source="node_telemetry"
            )

    duration_ms = round((time.perf_counter() - start_time) * 1000.0, 2)
    metrics_collector.record_ingest_latency(duration_ms)

    # Structured logging
    logger.info(
        event="telemetry_processed",
        node_id=node_id,
        hazard=primary_hazard,
        risk_pct=composite_risk,
        severity=primary_severity,
        alerts_count=len(alerts_persisted),
        latency_ms=duration_ms,
    )

    # 7. Build Composite Response
    response = UnifiedGatewayResponse(
        node_id=node_id,
        node_type=node_info.get("node_type", "Type-A"),
        state=node_info.get("state", "Tamil Nadu"),
        district=node_info.get("district"),
        zone=node_info.get("zone"),
        gateway_id=node_info.get("gateway_id", GATEWAY_ID),
        is_simulated=node_info.get("is_simulated", False),
        node_status=node_info.get("status", "ONLINE"),
        timestamp=payload.timestamp,
        location={
            "latitude": node_info.get("latitude"),
            "longitude": node_info.get("longitude")
        },
        battery_pct=node_info.get("battery_pct"),
        node_profile=node_info.get("node_profile", "UNKNOWN_NODE"),
        capabilities=node_info.get("capabilities", []),
        composite_risk_pct=composite_risk,
        primary_hazard=primary_hazard,
        primary_severity=primary_severity,
        priority_score=priority_score,
        ranked_hazards=ranked_hazards,
        hazard_results=hazard_results,
        alerts_triggered=alerts_persisted,
        processing_time_ms=duration_ms,
        db_status=db_mode,
        transport=transport_meta,
        raw_telemetry=payload_dict,
    )

    # Cache latest evaluation for node
    _latest_node_evaluations[node_id] = response
    return response


# ============================================================================
# HTTP Endpoints — Public / Read Health & Status (Phase 8)
# ============================================================================

@app.get("/")
def root():
    return {
        "service": "TerraEdge Type B Edge Gateway",
        "gateway_id": GATEWAY_ID,
        "version": "8.0.0",
        "status": "operational",
        "environment": TERRAEDGE_ENV,
        "lora_enabled": LORA_ENABLED,
        "active_nodes": len(node_manager.get_all_nodes(status="ONLINE")),
        "total_nodes": len(node_manager.get_all_nodes()),
        "docs_url": "/docs"
    }


@app.get("/health")
def health_check():
    """Aggregated system health inspection."""
    db_stat = db.status() if db is not None else {"mode": "in-memory", "connected": False}
    lora_status = "disabled"
    if LORA_ENABLED:
        lora_status = "mock" if LORA_MOCK_MODE else f"serial:{LORA_SERIAL_PORT}"
        if _lora_receiver is not None:
            lora_status = ("running/" + lora_status)

    backhaul_health = backhaul_manager.get_health()

    return {
        "status": "healthy",
        "gateway_id": GATEWAY_ID,
        "environment": TERRAEDGE_ENV,
        "timestamp": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        "database": db_stat,
        "models_loaded": {
            hazard: (hazard in hazard_router.engines)
            for hazard in ["Flood", "Wildfire", "Landslide", "Air Quality", "Extreme Heat", "Toxic Flame", "Water Quality"]
        },
        "engine_errors": hazard_router.engine_errors,
        "active_nodes_count": len(node_manager.get_all_nodes()),
        "lora": lora_status,
        "backhaul": {
            "state": backhaul_health.backhaul_state.value,
            "active_transport": backhaul_health.active_transport.value if backhaul_health.active_transport else "none",
            "queue_size": backhaul_health.queue_size,
            "sync_state": backhaul_health.sync_state,
        }
    }


@app.get("/health/live")
def liveness_probe():
    """Liveness probe: verifies gateway process is running and responding."""
    return {
        "status": "alive",
        "gateway_id": GATEWAY_ID,
        "timestamp": datetime.datetime.now(datetime.timezone.utc).isoformat(),
    }


@app.get("/health/ready")
def readiness_probe():
    """
    Readiness probe: verifies local edge intelligence is ready to serve predictions.
    Note: Does NOT require cloud internet connection (Edge-First design).
    """
    loaded_models_cnt = len(hazard_router.engines)
    is_ready = loaded_models_cnt == 7
    return {
        "status": "ready" if is_ready else "not_ready",
        "gateway_id": GATEWAY_ID,
        "local_edge_operational": True,
        "models_loaded_count": loaded_models_cnt,
        "queue_ready": True,
        "timestamp": datetime.datetime.now(datetime.timezone.utc).isoformat(),
    }


@app.get("/api/system/status")
def get_system_status():
    """Returns detailed operational status of gateway components and workers."""
    metrics = metrics_collector.get_metrics()
    queue_summary = durable_queue.get_summary()
    backhaul_health = backhaul_manager.get_health()

    return {
        "gateway_id": GATEWAY_ID,
        "version": "8.0.0",
        "environment": TERRAEDGE_ENV,
        "uptime_seconds": metrics["uptime_seconds"],
        "active_nodes": len(node_manager.get_all_nodes(status="ONLINE")),
        "total_nodes": len(node_manager.get_all_nodes()),
        "models_loaded": len(hazard_router.engines),
        "lora_receiver_running": _lora_receiver is not None and getattr(_lora_receiver, "_running", False),
        "backhaul_state": backhaul_health.backhaul_state.value,
        "active_transport": backhaul_health.active_transport.value if backhaul_health.active_transport else "none",
        "queue_pending_records": queue_summary.pending_count,
        "queue_storage": durable_queue.get_storage_metrics(),
        "metrics_summary": metrics["counters"],
        "timestamp": datetime.datetime.now(datetime.timezone.utc).isoformat(),
    }


@app.get("/api/system/metrics")
def get_system_metrics():
    """Returns in-memory operational performance counters and latency statistics."""
    return metrics_collector.get_metrics()


@app.get("/api/models/health")
def get_models_health():
    """Returns versioning, feature schemas, and execution statistics for all 7 ML models."""
    return model_health_tracker.get_all_models_health()


# ============================================================================
# HTTP Endpoints — Telemetry Ingestion (Public / Field Path)
# ============================================================================

@app.post("/api/telemetry", response_model=UnifiedGatewayResponse)
def ingest_telemetry(payload: TypeATelemetryPayload, request: Request):
    """
    Core Telemetry Ingestion Endpoint (HTTP path).
    Applies rate limiting and delegates to shared process_type_a_telemetry().
    """
    rate_limiter.check_rate_limit(request)
    return process_type_a_telemetry(payload, transport_meta=None)


# ============================================================================
# HTTP Endpoints — Dynamic Node Registry (Public Read / Admin Write)
# ============================================================================

@app.get("/api/nodes")
def get_nodes(
    state: Optional[str] = Query(None, description="Filter by state name"),
    district: Optional[str] = Query(None, description="Filter by district name"),
    status: Optional[str] = Query(None, description="Filter by status: ONLINE, STALE, OFFLINE")
):
    """Returns list of all registered field sensor nodes with dynamic health status."""
    return node_manager.get_all_nodes(state=state, district=district, status=status)


@app.get("/api/nodes/{node_id}")
def get_node_by_id(node_id: str):
    """Returns detailed status and profile for a specific node."""
    node = node_manager.get_node(node_id)
    if not node:
        raise HTTPException(status_code=404, detail=f"Node '{node_id}' not found in registry")
    return node


@app.post("/api/nodes", status_code=201, dependencies=[Depends(require_admin)])
def register_node(req: NodeRegistrationRequest):
    """Dynamically registers a new sensor node (Admin only)."""
    return node_manager.register_node(req)


@app.patch("/api/nodes/{node_id}", dependencies=[Depends(require_admin)])
def update_node(node_id: str, updates: NodeUpdateRequest):
    """Partially updates attributes for an existing node (Admin only)."""
    updated = node_manager.update_node(node_id, updates)
    if not updated:
        raise HTTPException(status_code=404, detail=f"Node '{node_id}' not found in registry")
    return updated


@app.get("/api/nodes/{node_id}/latest", response_model=UnifiedGatewayResponse)
@app.get("/api/latest/{node_id}", response_model=UnifiedGatewayResponse)
def get_latest_node_telemetry(node_id: str):
    """Returns the most recent telemetry and multi-hazard risk evaluation for a node."""
    if node_id not in _latest_node_evaluations:
        raise HTTPException(status_code=404, detail=f"No telemetry received yet for node '{node_id}'")
    return _latest_node_evaluations[node_id]


@app.get("/api/nodes/{node_id}/history")
def get_node_history(node_id: str, limit: int = Query(50, ge=1, le=200)):
    """Returns recent historical time series for a specific node."""
    node = node_manager.get_node(node_id)
    if not node:
        raise HTTPException(status_code=404, detail=f"Node '{node_id}' not found in registry")
    history = telemetry_engine.get_history(node_id, limit=limit)
    return {
        "node_id": node_id,
        "history_count": len(history),
        "history": history
    }


# ============================================================================
# HTTP Endpoints — District Intelligence & Spatial Aggregation (Public Read)
# ============================================================================

@app.get("/api/districts")
def get_districts(state: Optional[str] = Query(None, description="State filter, e.g. 'Tamil Nadu'")):
    """Returns list of all active districts and their quick health status."""
    districts = node_manager.get_all_districts(state=state)
    summaries = []
    for d in districts:
        res = district_engine.aggregate_district(d, state_name=state or "Tamil Nadu", evaluations=_latest_node_evaluations)
        summaries.append({
            "district": res.district,
            "state": res.state,
            "node_count": res.node_count,
            "active_nodes_count": res.active_nodes_count,
            "composite_risk_pct": res.composite_risk_pct,
            "primary_hazard": res.primary_hazard,
            "primary_severity": res.primary_severity,
        })
    return summaries


@app.get("/api/districts/{district}/risk", response_model=DistrictRiskResponse)
def get_district_risk(
    district: str,
    state: Optional[str] = Query("Tamil Nadu", description="State name")
):
    """Returns comprehensive multi-node aggregated environmental intelligence for a district."""
    return district_engine.aggregate_district(
        district_name=district,
        state_name=state or "Tamil Nadu",
        evaluations=_latest_node_evaluations
    )


@app.get("/api/risk-map", response_model=RiskMapResponse)
def get_risk_map(
    state: Optional[str] = Query(None, description="Optional state filter"),
    district: Optional[str] = Query(None, description="Optional district filter")
):
    """Authoritative GIS risk map endpoint."""
    return district_engine.build_risk_map_response(
        state=state,
        district=district,
        evaluations=_latest_node_evaluations
    )


@app.get("/api/hotspots", response_model=List[HotspotCluster])
def get_hotspots():
    """Returns all active geographic risk concentration hotspots."""
    all_nodes = node_manager.get_all_nodes()
    return district_engine.detect_hotspots(all_nodes, _latest_node_evaluations)


# ============================================================================
# HTTP Endpoints — Alerts & Notifications (Public Read / Role-Protected Write)
# ============================================================================

@app.get("/api/alerts")
def get_recent_alerts(
    hazard: Optional[str] = None,
    severity: Optional[str] = None,
    district: Optional[str] = None,
    limit: int = Query(50, ge=1, le=200)
):
    """Fetches recent multi-hazard alerts."""
    cached = alert_dispatcher.get_all_alerts(hazard=hazard, severity=severity, district=district, limit=limit)
    if cached:
        return [c.model_dump() for c in cached]
    if db is None:
        return []
    target_hazard = hazard.lower() if hazard else "all"
    return db.fetch_alerts(target_hazard, limit=limit)


@app.get("/api/alerts/{alert_id}")
def get_alert_by_id(alert_id: str):
    """Returns detailed status, lifecycle state, and dispatch audit for a specific alert."""
    alert = alert_dispatcher.get_alert(alert_id)
    if not alert:
        raise HTTPException(status_code=404, detail=f"Alert '{alert_id}' not found in registry")
    return alert


@app.post("/api/alerts/{alert_id}/acknowledge", dependencies=[Depends(require_operator)])
def acknowledge_alert(alert_id: str, req: AlertAcknowledgeRequest):
    """Records operator acknowledgement for an active alert (Operator or Admin)."""
    alert = alert_dispatcher.acknowledge_alert(alert_id, operator_id=req.operator_id, notes=req.notes)
    if not alert:
        raise HTTPException(status_code=404, detail=f"Alert '{alert_id}' not found in registry")
    return alert


@app.post("/api/alerts/{alert_id}/dispatch", dependencies=[Depends(require_admin)])
def manual_dispatch_alert(alert_id: str, req: ManualDispatchRequest):
    """Manually triggers an authority notification dispatch (Admin only)."""
    alert = alert_dispatcher.get_alert(alert_id)
    if not alert:
        raise HTTPException(status_code=404, detail=f"Alert '{alert_id}' not found in registry")
    updated_alert, dispatches = alert_dispatcher.dispatch(
        alert,
        source="manual_dispatch",
        force=True if req.force else False,
        target_channels=req.channels
    )
    return {
        "alert_id": alert_id,
        "status": "dispatched",
        "dispatches_count": len(dispatches),
        "dispatches": [d.model_dump() for d in dispatches]
    }


@app.get("/api/alerts/{alert_id}/dispatches")
def get_alert_dispatches(alert_id: str):
    """Returns all channel dispatch audit logs for an alert."""
    dispatches = alert_dispatcher.get_dispatches_for_alert(alert_id)
    return {
        "alert_id": alert_id,
        "dispatches_count": len(dispatches),
        "dispatches": [d.model_dump() for d in dispatches]
    }


@app.get("/api/alerts/{alert_id}/cap")
def get_alert_cap_xml(alert_id: str):
    """Returns OASIS CAP v1.2 compliant XML document for the alert."""
    from fastapi.responses import Response
    cap_xml = alert_dispatcher.get_cap_xml_for_alert(alert_id)
    if not cap_xml:
        raise HTTPException(status_code=404, detail=f"CAP record for alert '{alert_id}' not found")
    return Response(content=cap_xml, media_type="application/xml")


@app.get("/api/notification-targets")
def get_notification_targets(
    target_type: Optional[ChannelType] = None,
    district: Optional[str] = None,
    enabled: Optional[bool] = None
):
    """Returns list of configured authority notification destinations."""
    return alert_dispatcher.get_targets(target_type=target_type, district=district, enabled=enabled)


@app.post("/api/notification-targets", status_code=201, dependencies=[Depends(require_admin)])
def create_notification_target(req: TargetCreateRequest):
    """Registers a new authority notification target (Admin only)."""
    return alert_dispatcher.add_target(req)


@app.patch("/api/notification-targets/{target_id}", dependencies=[Depends(require_admin)])
def update_notification_target(target_id: str, req: TargetUpdateRequest):
    """Updates configuration for an existing notification target (Admin only)."""
    updated = alert_dispatcher.update_target(target_id, req)
    if not updated:
        raise HTTPException(status_code=404, detail=f"Target '{target_id}' not found")
    return updated


@app.delete("/api/notification-targets/{target_id}", dependencies=[Depends(require_admin)])
def delete_notification_target(target_id: str):
    """Removes a notification target (Admin only)."""
    success = alert_dispatcher.delete_target(target_id)
    if not success:
        raise HTTPException(status_code=404, detail=f"Target '{target_id}' not found")
    return {"status": "deleted", "target_id": target_id}


# ============================================================================
# HTTP Endpoints — Resilient Backhaul & Queue Maintenance
# ============================================================================

@app.get("/api/backhaul/health", response_model=BackhaulHealthResponse)
def get_backhaul_health():
    """Returns real-time health, active transport route, and failover state of gateway backhauls."""
    return backhaul_manager.get_health()


@app.get("/api/backhaul/queue", response_model=QueueSummaryResponse)
def get_backhaul_queue():
    """Returns persistent store-and-forward SQLite buffer statistics and record counts."""
    return backhaul_manager.get_queue_summary()


@app.post("/api/backhaul/sync", response_model=SyncResponse, dependencies=[Depends(require_admin)])
def trigger_backhaul_sync(limit: int = Query(50, ge=1, le=500, description="Max batch size to sync")):
    """Manually triggers store-and-forward flush over available backhaul (Admin only)."""
    return backhaul_manager.sync_queue(batch_size=limit)


@app.post("/api/queue/maintenance", dependencies=[Depends(require_admin)])
def run_queue_maintenance(retention_days: int = Query(7, ge=1, le=90)):
    """Purges completed/synced records older than retention_days (Admin only)."""
    purged_cnt = durable_queue.purge_synced(retention_days=retention_days)
    purged_failed = durable_queue.purge_failed(max_age_days=30)
    storage = durable_queue.get_storage_metrics()
    return {
        "status": "completed",
        "synced_records_purged": purged_cnt,
        "failed_records_purged": purged_failed,
        "retention_days_applied": retention_days,
        "storage": storage,
    }


# ============================================================================
# Background Tasks & Lifecycle Handlers (Startup / Shutdown)
# ============================================================================

@app.on_event("startup")
async def start_gateway_background_tasks():
    """Validate configuration, launch LoRa receiver and Backhaul synchronization tasks."""
    global _lora_receiver

    # 1. Startup configuration validation
    cfg_report = validate_configuration()
    print(f"[gateway] Startup configuration status: {cfg_report['overall_status']} (Environment: {TERRAEDGE_ENV})", flush=True)
    if cfg_report["warnings"]:
        for w in cfg_report["warnings"]:
            print(f"[gateway] [WARNING] {w}", flush=True)

    # 2. Backhaul periodic store-and-forward sync task (error isolated)
    asyncio.create_task(backhaul_manager.start_background_sync())
    print("[gateway] Backhaul background sync worker launched", flush=True)

    # 3. LoRa receiver task (if enabled)
    if not LORA_ENABLED:
        print("[gateway] LoRa receiver DISABLED (LORA_ENABLED=false)", flush=True)
        return

    from .lora.receiver import LoRaReceiver
    from .lora.radio import MockLoRaRadio, SerialLoRaRadio

    try:
        if LORA_MOCK_MODE:
            radio = MockLoRaRadio()
            print("[gateway] Starting LoRa receiver in MOCK mode (no hardware)", flush=True)
        else:
            radio = SerialLoRaRadio(port=LORA_SERIAL_PORT, baud=LORA_BAUD_RATE)
            print(f"[gateway] Starting LoRa receiver on {LORA_SERIAL_PORT}", flush=True)

        _lora_receiver = LoRaReceiver(
            radio=radio,
            ingest_fn=process_type_a_telemetry,
            node_manager=node_manager,
            ack_enabled=LORA_ACK_ENABLED,
            ack_timeout_ms=LORA_ACK_TIMEOUT_MS,
            dedup_cache_size=LORA_DEDUP_CACHE_SIZE,
        )

        asyncio.create_task(_lora_receiver.run())
        print("[gateway] LoRa receiver task launched", flush=True)
    except Exception as exc:
        print(f"[gateway] [ERROR] Failed to start LoRa receiver: {exc}", flush=True)


@app.on_event("shutdown")
async def stop_gateway_background_tasks():
    """Gracefully terminate background tasks and flush buffers on shutdown."""
    if _lora_receiver is not None:
        _lora_receiver.stop()
    backhaul_manager.stop_background_sync()
    print("[gateway] Graceful shutdown completed", flush=True)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("gateway.app:app", host=GATEWAY_HOST, port=GATEWAY_PORT, reload=True)
