"""
TerraEdge — Common Alerting Protocol (CAP v1.2) XML Channel.
Generates, validates, and archives OASIS CAP v1.2 compliant environmental emergency alerts.
Standard namespace: urn:oasis:names:tc:emergency:cap:1.2
"""

from __future__ import annotations
import datetime
import time
import uuid
import xml.etree.ElementTree as ET
from typing import Optional, Tuple

from ..rules import build_alert_message, build_alert_title
from ..schemas import (
    CanonicalAlert,
    ChannelType,
    DispatchRecord,
    DispatchStatus,
    NotificationTarget,
)
from .base import BaseNotificationChannel

CAP_NAMESPACE = "urn:oasis:names:tc:emergency:cap:1.2"

# Hazard to CAP Category Mapping
HAZARD_CATEGORY_MAP = {
    "Flood": "Met",
    "Wildfire": "Env",
    "Landslide": "Geo",
    "Air Quality": "Env",
    "Extreme Heat": "Met",
    "Industrial Emissions": "Safety",
    "Toxic Flame": "Safety",
    "Water Quality": "Env",
}

# Severity to CAP Urgency & Severity Mapping
CAP_SEVERITY_MAP = {
    "CRITICAL": {"urgency": "Immediate", "severity": "Extreme", "certainty": "Observed"},
    "WARNING": {"urgency": "Expected", "severity": "Severe", "certainty": "Likely"},
    "WATCH": {"urgency": "Future", "severity": "Moderate", "certainty": "Possible"},
    "NORMAL": {"urgency": "Past", "severity": "Minor", "certainty": "Unlikely"},
}


def generate_cap_xml(
    alert: CanonicalAlert,
    sender: str = "terraedge-gateway@emergency.gov.in",
    scope: str = "Public"
) -> str:
    """
    Constructs well-formed OASIS CAP v1.2 XML document string for the alert.
    """
    root = ET.Element("alert", xmlns=CAP_NAMESPACE)

    # Top-Level Identification & Routing
    ET.SubElement(root, "identifier").text = alert.alert_id
    ET.SubElement(root, "sender").text = sender
    ET.SubElement(root, "sent").text = alert.created_at
    ET.SubElement(root, "status").text = "Test" if alert.is_simulated else "Actual"
    
    msg_type = "Update" if alert.lifecycle_state.value == "UPDATED" else "Alert"
    ET.SubElement(root, "msgType").text = msg_type
    ET.SubElement(root, "scope").text = scope
    ET.SubElement(root, "code").text = "IPAWS-1.0"

    # Info Block
    info = ET.SubElement(root, "info")
    category = HAZARD_CATEGORY_MAP.get(alert.hazard, "Env")
    ET.SubElement(info, "category").text = category
    ET.SubElement(info, "event").text = alert.hazard
    ET.SubElement(info, "responseType").text = "Monitor" if alert.severity in ("WATCH", "NORMAL") else "Execute"

    cap_ratings = CAP_SEVERITY_MAP.get(alert.severity.upper(), CAP_SEVERITY_MAP["WARNING"])
    ET.SubElement(info, "urgency").text = cap_ratings["urgency"]
    ET.SubElement(info, "severity").text = cap_ratings["severity"]

    # Refine certainty based on ML confidence score
    if alert.confidence_pct >= 80.0:
        certainty = "Observed"
    elif alert.confidence_pct >= 60.0:
        certainty = "Likely"
    elif alert.confidence_pct >= 40.0:
        certainty = "Possible"
    else:
        certainty = "Unlikely"
    ET.SubElement(info, "certainty").text = certainty

    ET.SubElement(info, "eventCode").text = f"TERRAEDGE:{alert.hazard.upper()}"
    
    # Expiration: default +6 hours if not provided
    expires_time = alert.expires_at
    if not expires_time:
        try:
            created_dt = datetime.datetime.fromisoformat(alert.created_at.replace("Z", "+00:00"))
            expires_time = (created_dt + datetime.timedelta(hours=6)).isoformat()
        except Exception:
            expires_time = alert.created_at
    ET.SubElement(info, "expires").text = expires_time

    ET.SubElement(info, "headline").text = build_alert_title(alert)
    ET.SubElement(info, "description").text = build_alert_message(alert)
    ET.SubElement(info, "instruction").text = "Observe local emergency services advisories and refer to TerraEdge real-time sensor GIS portal."

    # Parameters (ML risk score, confidence, affected nodes)
    p_risk = ET.SubElement(info, "parameter")
    ET.SubElement(p_risk, "valueName").text = "RiskScorePct"
    ET.SubElement(p_risk, "value").text = f"{alert.risk_pct:.1f}"

    p_conf = ET.SubElement(info, "parameter")
    ET.SubElement(p_conf, "valueName").text = "ConfidencePct"
    ET.SubElement(p_conf, "value").text = f"{alert.confidence_pct:.1f}"

    if alert.affected_nodes:
        p_nodes = ET.SubElement(info, "parameter")
        ET.SubElement(p_nodes, "valueName").text = "AffectedNodes"
        ET.SubElement(p_nodes, "value").text = ",".join(alert.affected_nodes)

    # Geographic Area Information
    area = ET.SubElement(info, "area")
    loc_desc = f"{alert.district or 'Regional'}, {alert.state}"
    ET.SubElement(area, "areaDesc").text = loc_desc

    if alert.latitude is not None and alert.longitude is not None:
        radius = alert.radius_km if alert.radius_km is not None else 5.0
        # Format: lat,lon radius
        ET.SubElement(area, "circle").text = f"{alert.latitude:.6f},{alert.longitude:.6f} {radius:.1f}"

    # Geocode standard identifier
    if alert.district:
        geo = ET.SubElement(area, "geocode")
        ET.SubElement(geo, "valueName").text = "DISTRICT"
        ET.SubElement(geo, "value").text = alert.district.upper()

    return ET.tostring(root, encoding="utf-8", xml_declaration=True).decode("utf-8")


def validate_cap_xml(xml_str: str) -> Tuple[bool, Optional[str]]:
    """
    Validates that the generated XML adheres to OASIS CAP v1.2 syntax and required fields.
    """
    try:
        root = ET.fromstring(xml_str)
        tag_name = root.tag.split("}")[-1] if "}" in root.tag else root.tag
        if tag_name != "alert":
            return False, f"Root tag must be 'alert', got '{tag_name}'"

        # Check required CAP fields
        required_top = ["identifier", "sender", "sent", "status", "msgType", "scope"]
        for field in required_top:
            found = False
            for child in root:
                child_tag = child.tag.split("}")[-1] if "}" in child.tag else child.tag
                if child_tag == field and (child.text or "").strip():
                    found = True
                    break
            if not found:
                return False, f"Missing required top-level field: <{field}>"

        # Check info block
        info = None
        for child in root:
            if (child.tag.split("}")[-1] if "}" in child.tag else child.tag) == "info":
                info = child
                break
        if info is None:
            return False, "Missing required <info> block"

        required_info = ["category", "event", "urgency", "severity", "certainty", "headline", "description", "area"]
        for field in required_info:
            found = False
            for child in info:
                child_tag = child.tag.split("}")[-1] if "}" in child.tag else child.tag
                if child_tag == field:
                    found = True
                    break
            if not found:
                return False, f"Missing required info field: <{field}>"

        return True, None
    except Exception as exc:
        return False, f"XML parsing error: {str(exc)}"


class CapChannel(BaseNotificationChannel):
    def __init__(
        self,
        sender: str = "terraedge-gateway@emergency.gov.in",
        scope: str = "Public",
        enabled: bool = True
    ):
        self.sender = sender
        self.scope = scope
        self.enabled = enabled

    def send(self, alert: CanonicalAlert, target: Optional[NotificationTarget] = None) -> DispatchRecord:
        start_time = time.perf_counter()
        destination = target.destination if target else "CAP_FEED_ARCHIVE"
        dispatch_id = f"DSP-CAP-{uuid.uuid4().hex[:8].upper()}"

        if not self.enabled:
            return DispatchRecord(
                dispatch_id=dispatch_id,
                alert_id=alert.alert_id,
                channel=ChannelType.CAP,
                target=destination,
                status=DispatchStatus.DISABLED,
                error="CAP channel is disabled in gateway configuration",
                latency_ms=0.0,
                dry_run=True,
            )

        try:
            cap_xml = generate_cap_xml(alert, sender=self.sender, scope=self.scope)
            is_valid, err = validate_cap_xml(cap_xml)
            duration_ms = round((time.perf_counter() - start_time) * 1000.0, 2)

            if not is_valid:
                return DispatchRecord(
                    dispatch_id=dispatch_id,
                    alert_id=alert.alert_id,
                    channel=ChannelType.CAP,
                    target=destination,
                    status=DispatchStatus.FAILED,
                    error=f"CAP schema validation failed: {err}",
                    latency_ms=duration_ms,
                    dry_run=False,
                )

            return DispatchRecord(
                dispatch_id=dispatch_id,
                alert_id=alert.alert_id,
                channel=ChannelType.CAP,
                target=destination,
                status=DispatchStatus.SENT,
                provider_message_id=f"CAP-{alert.alert_id}",
                latency_ms=duration_ms,
                dry_run=False,
                response_metadata={
                    "cap_bytes": len(cap_xml),
                    "cap_xml": cap_xml,
                    "version": "1.2",
                    "namespace": CAP_NAMESPACE
                }
            )
        except Exception as exc:
            duration_ms = round((time.perf_counter() - start_time) * 1000.0, 2)
            return DispatchRecord(
                dispatch_id=dispatch_id,
                alert_id=alert.alert_id,
                channel=ChannelType.CAP,
                target=destination,
                status=DispatchStatus.FAILED,
                error=f"CAP generation error: {str(exc)}",
                latency_ms=duration_ms,
                dry_run=False,
            )
