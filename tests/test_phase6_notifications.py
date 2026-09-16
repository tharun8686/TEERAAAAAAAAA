"""
TerraEdge — Phase 6 Automated Multi-Channel Alert & Authority Dispatch Test Suite.
Tests alert normalization, policy rules, deduplication, lifecycle states,
SMS/Email/Webhook dry-run modes, CAP v1.2 XML generation & validation,
channel failure isolation, target management, and REST APIs.
"""

import datetime
import pytest
from fastapi.testclient import TestClient

from gateway.app import app
from gateway.notifications.channels.cap import CapChannel, generate_cap_xml, validate_cap_xml
from gateway.notifications.channels.email import EmailChannel
from gateway.notifications.channels.sms import SmsChannel
from gateway.notifications.channels.webhook import WebhookChannel
from gateway.notifications.deduplication import AlertDeduplicator
from gateway.notifications.dispatcher import AlertDispatcher, alert_dispatcher
from gateway.notifications.rules import (
    build_alert_message,
    build_alert_title,
    filter_targets,
    is_target_eligible,
    should_dispatch_alert,
)
from gateway.notifications.schemas import (
    AlertLifecycleState,
    CanonicalAlert,
    ChannelType,
    DispatchRecord,
    DispatchStatus,
    NotificationTarget,
    TargetCreateRequest,
    TargetUpdateRequest,
)


@pytest.fixture
def client():
    return TestClient(app)


@pytest.fixture
def sample_flood_alert():
    return CanonicalAlert(
        alert_id="ALT-FLOOD-TEST-001",
        event_id="flood:chennai",
        hazard="Flood",
        severity="CRITICAL",
        risk_pct=85.4,
        confidence_pct=91.2,
        node_id="TE-001",
        affected_nodes=["TE-001", "TE-002"],
        state="Tamil Nadu",
        district="Chennai",
        zone="Adyar Basin",
        latitude=13.0827,
        longitude=80.2707,
        radius_km=7.5,
        created_at=datetime.datetime.now(datetime.timezone.utc).isoformat(),
        source="district_aggregation",
        is_simulated=False,
        alert_candidate=True,
    )


# ============================================================================
# 1. Alert Normalization & Formatting Tests
# ============================================================================

def test_alert_normalization():
    dispatcher = AlertDispatcher()
    raw_alert = {
        "alert_id": "ALT-FIRE-1001",
        "hazard": "Wildfire",
        "severity": "CRITICAL",
        "risk_score_pct": 88.0,
        "confidence_pct": 92.5,
        "node_id": "TE-WLD-01",
        "state": "Tamil Nadu",
        "district": "Nilgiris",
        "timestamp": "2026-09-16T15:00:00Z",
        "top_features": [{"feature": "temp", "value": 44.5}],
    }
    canonical = dispatcher.normalize_alert(raw_alert, source="node_telemetry")
    assert canonical.alert_id == "ALT-FIRE-1001"
    assert canonical.hazard == "Wildfire"
    assert canonical.severity == "CRITICAL"
    assert canonical.risk_pct == 88.0
    assert canonical.confidence_pct == 92.5
    assert canonical.district == "Nilgiris"
    assert canonical.node_id == "TE-WLD-01"
    assert "TE-WLD-01" in canonical.affected_nodes
    assert "[TERRAEDGE] WILDFIRE — CRITICAL" in canonical.title
    assert "Risk Score: 88.0%" in canonical.message


# ============================================================================
# 2. Alert Policy & Target Eligibility Tests
# ============================================================================

def test_alert_policy(sample_flood_alert):
    # CRITICAL & WARNING should dispatch
    assert should_dispatch_alert(sample_flood_alert) is True

    warning_alert = sample_flood_alert.model_copy(update={"severity": "WARNING", "risk_pct": 65.0})
    assert should_dispatch_alert(warning_alert) is True

    # NORMAL should not dispatch externally
    normal_alert = sample_flood_alert.model_copy(update={"severity": "NORMAL", "risk_pct": 15.0, "alert_candidate": False})
    assert should_dispatch_alert(normal_alert) is False


def test_notification_target_filtering(sample_flood_alert):
    t_matching_all = NotificationTarget(
        target_id="T1", target_type=ChannelType.SMS, name="All SMS", destination="+919999999999",
        state="Tamil Nadu", district=None, hazards=["all"], min_severity="WARNING", enabled=True
    )
    t_matching_chennai = NotificationTarget(
        target_id="T2", target_type=ChannelType.EMAIL, name="Chennai Ops", destination="ops@chennai.gov.in",
        state="Tamil Nadu", district="Chennai", hazards=["Flood"], min_severity="WARNING", enabled=True
    )
    t_unmatching_district = NotificationTarget(
        target_id="T3", target_type=ChannelType.EMAIL, name="Coimbatore Ops", destination="ops@cbe.gov.in",
        state="Tamil Nadu", district="Coimbatore", hazards=["Flood"], min_severity="WARNING", enabled=True
    )
    t_unmatching_hazard = NotificationTarget(
        target_id="T4", target_type=ChannelType.WEBHOOK, name="Fire Webhook", destination="http://hook.local",
        state="Tamil Nadu", district="Chennai", hazards=["Wildfire"], min_severity="WARNING", enabled=True
    )
    t_disabled = NotificationTarget(
        target_id="T5", target_type=ChannelType.SMS, name="Disabled Target", destination="+918888888888",
        state="Tamil Nadu", district="Chennai", hazards=["all"], min_severity="WARNING", enabled=False
    )

    targets = [t_matching_all, t_matching_chennai, t_unmatching_district, t_unmatching_hazard, t_disabled]
    filtered = filter_targets(targets, sample_flood_alert)

    assert len(filtered) == 2
    assert t_matching_all in filtered
    assert t_matching_chennai in filtered
    assert t_unmatching_district not in filtered
    assert t_unmatching_hazard not in filtered
    assert t_disabled not in filtered


# ============================================================================
# 3. Alert Deduplication & Lifecycle State Tests
# ============================================================================

def test_alert_deduplication(sample_flood_alert):
    dedup = AlertDeduplicator(dedup_window_seconds=300)

    # 1. First event -> DISPATCH_INITIAL
    action, reason = dedup.evaluate_alert(sample_flood_alert)
    assert action == "DISPATCH_INITIAL"
    dedup.record_dispatch_success(sample_flood_alert)

    # 2. Repeated event on immediate polling cycle -> SUPPRESS_DUPLICATE
    action2, reason2 = dedup.evaluate_alert(sample_flood_alert)
    assert action2 == "SUPPRESS_DUPLICATE"
    assert "suppressed" in reason2.lower()


def test_alert_update_on_severity_escalation(sample_flood_alert):
    dedup = AlertDeduplicator(dedup_window_seconds=300)

    # Start at WARNING
    warn_alert = sample_flood_alert.model_copy(update={"severity": "WARNING", "risk_pct": 58.0})
    action1, _ = dedup.evaluate_alert(warn_alert)
    assert action1 == "DISPATCH_INITIAL"
    dedup.record_dispatch_success(warn_alert)

    # Escalate to CRITICAL -> DISPATCH_UPDATE
    crit_alert = sample_flood_alert.model_copy(update={"severity": "CRITICAL", "risk_pct": 84.0})
    action2, reason2 = dedup.evaluate_alert(crit_alert)
    assert action2 == "DISPATCH_UPDATE"
    assert "escalated" in reason2.lower()


def test_alert_update_on_material_risk_jump(sample_flood_alert):
    dedup = AlertDeduplicator(dedup_window_seconds=300)

    initial_alert = sample_flood_alert.model_copy(update={"severity": "WARNING", "risk_pct": 50.0})
    dedup.evaluate_alert(initial_alert)
    dedup.record_dispatch_success(initial_alert)

    # Material risk jump (+18%) within same severity -> DISPATCH_UPDATE
    jumped_alert = sample_flood_alert.model_copy(update={"severity": "WARNING", "risk_pct": 68.0})
    action, reason = dedup.evaluate_alert(jumped_alert)
    assert action == "DISPATCH_UPDATE"
    assert "jumped" in reason.lower()


def test_alert_resolution(sample_flood_alert):
    dedup = AlertDeduplicator(dedup_window_seconds=300)

    dedup.evaluate_alert(sample_flood_alert)
    dedup.record_dispatch_success(sample_flood_alert)

    # Hazard subsides to NORMAL -> RESOLVED
    subsided = sample_flood_alert.model_copy(update={"severity": "NORMAL", "risk_pct": 12.0})
    action, reason = dedup.evaluate_alert(subsided)
    assert action == "RESOLVED"
    assert "subsided" in reason.lower()


# ============================================================================
# 4. Multi-Channel Dry-Run Tests (SMS, Email, Webhook, CAP)
# ============================================================================

def test_sms_dry_run(sample_flood_alert):
    sms = SmsChannel(mode="dry_run", provider="mock")
    target = NotificationTarget(
        target_id="TGT-SMS-1", target_type=ChannelType.SMS, name="SMS Ops",
        destination="+919876543210", hazards=["all"], min_severity="WARNING", enabled=True
    )
    rec = sms.send(sample_flood_alert, target)
    assert rec.status == DispatchStatus.DRY_RUN
    assert rec.dry_run is True
    assert rec.channel == ChannelType.SMS
    assert "DRYRUN-TWILIO" in rec.provider_message_id
    assert rec.latency_ms >= 0.0


def test_email_dry_run(sample_flood_alert):
    email = EmailChannel(mode="dry_run", smtp_username="", smtp_password="")
    target = NotificationTarget(
        target_id="TGT-EML-1", target_type=ChannelType.EMAIL, name="Email Ops",
        destination="ops@tn.gov.in", hazards=["all"], min_severity="WARNING", enabled=True
    )
    rec = email.send(sample_flood_alert, target)
    assert rec.status == DispatchStatus.DRY_RUN
    assert rec.dry_run is True
    assert rec.channel == ChannelType.EMAIL
    assert "DRYRUN-SMTP" in rec.provider_message_id


def test_webhook_dry_run(sample_flood_alert):
    whk = WebhookChannel(mode="dry_run")
    target = NotificationTarget(
        target_id="TGT-WHK-1", target_type=ChannelType.WEBHOOK, name="Webhook GIS",
        destination="http://localhost:8000/api/mock-hook", hazards=["all"], min_severity="WARNING", enabled=True
    )
    rec = whk.send(sample_flood_alert, target)
    assert rec.status == DispatchStatus.DRY_RUN
    assert rec.dry_run is True
    assert rec.channel == ChannelType.WEBHOOK
    assert "DRYRUN-WHK" in rec.provider_message_id


def test_cap_generation_and_validation(sample_flood_alert):
    cap = CapChannel(sender="terraedge-gateway@emergency.gov.in", scope="Public")
    rec = cap.send(sample_flood_alert)
    assert rec.status == DispatchStatus.SENT
    assert rec.channel == ChannelType.CAP
    assert "cap_xml" in rec.response_metadata

    cap_xml = rec.response_metadata["cap_xml"]
    assert "<identifier>ALT-FLOOD-TEST-001</identifier>" in cap_xml
    assert "<event>Flood</event>" in cap_xml
    assert "<urgency>Immediate</urgency>" in cap_xml
    assert "<severity>Extreme</severity>" in cap_xml
    assert "<certainty>Observed</certainty>" in cap_xml
    assert "13.082700,80.270700 7.5" in cap_xml

    is_valid, err = validate_cap_xml(cap_xml)
    assert is_valid is True
    assert err is None


def test_cap_xml_invalid_rejection():
    invalid_xml = "<invalidRoot><notCap>Content</notCap></invalidRoot>"
    is_valid, err = validate_cap_xml(invalid_xml)
    assert is_valid is False
    assert "Root tag must be 'alert'" in err


# ============================================================================
# 5. Channel Failure Isolation & Audit Logging Tests
# ============================================================================

def test_dispatch_failure_isolation(sample_flood_alert):
    dispatcher = AlertDispatcher()
    # Add a target with bad/broken destination
    bad_whk_target = NotificationTarget(
        target_id="TGT-BAD", target_type=ChannelType.WEBHOOK, name="Bad Hook",
        destination="http://127.0.0.1:59999/nonexistent", hazards=["all"], min_severity="WARNING", enabled=True
    )
    dispatcher._targets["TGT-BAD"] = bad_whk_target

    # Dispatch should complete without raising, isolating the webhook failure
    alert, records = dispatcher.dispatch(sample_flood_alert, force=True)
    assert len(records) >= 3  # SMS, Email, Webhook(s), CAP

    # CAP and dry-run SMS/Email should succeed despite any broken target
    cap_records = [r for r in records if r.channel == ChannelType.CAP]
    assert len(cap_records) == 1
    assert cap_records[0].status == DispatchStatus.SENT


def test_simulated_vs_live_alert_distinction(sample_flood_alert):
    sim_alert = sample_flood_alert.model_copy(update={"is_simulated": True})
    assert "[SIMULATED]" in build_alert_title(sim_alert)
    assert "[SIMULATED TEST ALERT]" in build_alert_message(sim_alert)

    cap_xml = generate_cap_xml(sim_alert)
    assert "<status>Test</status>" in cap_xml


# ============================================================================
# 6. REST API Endpoints Tests
# ============================================================================

def test_alerts_api(client, sample_flood_alert):
    alert_dispatcher.dispatch(sample_flood_alert, force=True)

    # 1. GET /api/alerts
    res = client.get("/api/alerts")
    assert res.status_code == 200
    data = res.json()
    assert isinstance(data, list)
    assert len(data) >= 1

    # 2. GET /api/alerts/{id}
    res_single = client.get(f"/api/alerts/{sample_flood_alert.alert_id}")
    assert res_single.status_code == 200
    alert_obj = res_single.json()
    assert alert_obj["alert_id"] == sample_flood_alert.alert_id
    assert alert_obj["hazard"] == "Flood"

    # 3. GET /api/alerts/{id}/dispatches
    res_disp = client.get(f"/api/alerts/{sample_flood_alert.alert_id}/dispatches")
    assert res_disp.status_code == 200
    disp_data = res_disp.json()
    assert disp_data["alert_id"] == sample_flood_alert.alert_id
    assert disp_data["dispatches_count"] >= 1

    # 4. GET /api/alerts/{id}/cap
    res_cap = client.get(f"/api/alerts/{sample_flood_alert.alert_id}/cap")
    assert res_cap.status_code == 200
    assert "application/xml" in res_cap.headers.get("content-type", "")
    assert "<alert" in res_cap.text
    assert "<identifier>ALT-FLOOD-TEST-001</identifier>" in res_cap.text


def test_alert_acknowledgement_api(client, sample_flood_alert):
    alert_dispatcher.dispatch(sample_flood_alert, force=True)

    res = client.post(
        f"/api/alerts/{sample_flood_alert.alert_id}/acknowledge",
        json={"operator_id": "OPERATOR-TNSDMA-42", "notes": "Reviewed and dispatch verified"}
    )
    assert res.status_code == 200
    data = res.json()
    assert data["lifecycle_state"] == "ACKNOWLEDGED"
    assert data["details"]["acknowledged_by"] == "OPERATOR-TNSDMA-42"


def test_manual_dispatch_api(client, sample_flood_alert):
    alert_dispatcher.dispatch(sample_flood_alert, force=True)

    res = client.post(
        f"/api/alerts/{sample_flood_alert.alert_id}/dispatch",
        json={"channels": ["sms", "email"], "force": True}
    )
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == "dispatched"
    assert data["dispatches_count"] >= 1


def test_notification_target_crud_api(client):
    # 1. Create Target
    res = client.post(
        "/api/notification-targets",
        json={
            "target_type": "sms",
            "name": "Coimbatore Collectorate SMS",
            "destination": "+919444455555",
            "state": "Tamil Nadu",
            "district": "Coimbatore",
            "hazards": ["Flood", "Landslide"],
            "min_severity": "WARNING",
            "enabled": True,
        }
    )
    assert res.status_code == 201
    created = res.json()
    t_id = created["target_id"]
    assert created["district"] == "Coimbatore"

    # 2. Get Targets
    res_list = client.get("/api/notification-targets?district=Coimbatore")
    assert res_list.status_code == 200
    assert any(t["target_id"] == t_id for t in res_list.json())

    # 3. Patch Target
    res_patch = client.patch(
        f"/api/notification-targets/{t_id}",
        json={"min_severity": "CRITICAL", "enabled": False}
    )
    assert res_patch.status_code == 200
    assert res_patch.json()["min_severity"] == "CRITICAL"
    assert res_patch.json()["enabled"] is False

    # 4. Delete Target
    res_del = client.delete(f"/api/notification-targets/{t_id}")
    assert res_del.status_code == 200
    assert res_del.json()["status"] == "deleted"


# ============================================================================
# 7. End-to-End Ingestion to Dispatch Pipeline Integration Test
# ============================================================================

def test_end_to_end_simulated_alert_pipeline(client):
    """
    Verifies full path:
    Simulated Telemetry -> Gateway Ingest -> 7 ML Inferences -> Hazard Ranking
    -> Alert Candidate -> Alert Dispatcher -> Dry-run SMS/Email/Webhook -> CAP XML
    """
    # High-risk wildfire scenario payload for SRM Node
    wildfire_payload = {
        "node_id": "TE-SRM-WLD-99",
        "node_type": "Type-A",
        "state": "Tamil Nadu",
        "district": "Chennai",
        "zone": "SRM Live Edge",
        "firmware_version": "1.0.0",
        "timestamp": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        "battery_pct": 88.0,
        "is_simulated": True,
        "temperature_c": 58.5,
        "humidity_pct": 14.0,
        "flame": 1,
        "flame_detected": True,
        "gas_resistance_kohm": 3.2,
        "pressure_hpa": 1002.5,
        "soil_moisture_pct": 8.0,
        "latitude": 12.8231,
        "longitude": 80.0455,
    }

    res = client.post("/api/telemetry", json=wildfire_payload)
    assert res.status_code == 200
    data = res.json()
    assert data["node_id"] == "TE-SRM-WLD-99"
    assert data["primary_hazard"] in ("Wildfire", "Toxic Flame", "Extreme Heat")
    assert data["primary_severity"] in ("WARNING", "CRITICAL")
    assert len(data["alerts_triggered"]) >= 1

    # Verify that the alert was passed to alert_dispatcher and CAP XML was created
    recent_alerts = client.get("/api/alerts?limit=5").json()
    assert len(recent_alerts) >= 1
    top_alert = recent_alerts[0]
    assert top_alert["lifecycle_state"] in ("DISPATCHED", "ACTIVE", "UPDATED")

    # Verify CAP generation
    cap_res = client.get(f"/api/alerts/{top_alert['alert_id']}/cap")
    assert cap_res.status_code == 200
    assert "<alert" in cap_res.text
    assert "<status>Test</status>" in cap_res.text  # Because is_simulated=True

