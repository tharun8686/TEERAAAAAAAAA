# TerraEdge — Common Alerting Protocol (CAP v1.2) Implementation Specification

## 1. Overview

TerraEdge generates authority-grade emergency alert documents adhering strictly to the **OASIS Common Alerting Protocol (CAP) Version 1.2** standard (Standard Namespace: `urn:oasis:names:tc:emergency:cap:1.2`).

The CAP feed allows state disaster management authorities (e.g. TNSDMA, NDMA, Integrated Public Alert and Warning System) to automatically consume real-time environmental hazard intelligence from the TerraEdge Type B Edge Gateway.

---

## 2. Field-by-Field Mapping Specification

| CAP Element | TerraEdge Source Field | Mapping & Transformation Logic | Example Output |
|---|---|---|---|
| `<identifier>` | `alert.alert_id` | Canonical alert ID string | `ALT-FLOO-0042` |
| `<sender>` | `CAP_SENDER` config | Gateway authority sender email | `terraedge-gateway@emergency.gov.in` |
| `<sent>` | `alert.created_at` | ISO-8601 UTC timestamp | `2026-09-16T15:00:00+00:00` |
| `<status>` | `alert.is_simulated` | `Actual` if physical node; `Test` if simulated | `Actual` |
| `<msgType>` | `alert.lifecycle_state` | `Update` if state is `UPDATED`; `Alert` otherwise | `Alert` |
| `<scope>` | `CAP_SCOPE` config | Geographic dissemination scope | `Public` |
| `<category>` | `alert.hazard` | Standard CAP category mapping (see table below) | `Met` |
| `<event>` | `alert.hazard` | Canonical hazard name | `Flood` |
| `<urgency>` | `alert.severity` | `CRITICAL` $\to$ `Immediate`<br>`WARNING` $\to$ `Expected`<br>`WATCH` $\to$ `Future`<br>`NORMAL` $\to$ `Past` | `Immediate` |
| `<severity>` | `alert.severity` | `CRITICAL` $\to$ `Extreme`<br>`WARNING` $\to$ `Severe`<br>`WATCH` $\to$ `Moderate`<br>`NORMAL` $\to$ `Minor` | `Extreme` |
| `<certainty>` | `alert.confidence_pct` | $\ge 80\% \to$ `Observed`<br>$\ge 60\% \to$ `Likely`<br>$\ge 40\% \to$ `Possible`<br>$< 40\% \to$ `Unlikely` | `Observed` |
| `<eventCode>` | `alert.hazard` | Formatted event identifier | `TERRAEDGE:FLOOD` |
| `<expires>` | `alert.expires_at` | Scheduled expiration (+6 hours default) | `2026-09-16T21:00:00+00:00` |
| `<headline>` | `build_alert_title()` | Standard headline summary | `[TERRAEDGE] FLOOD — CRITICAL — CHENNAI` |
| `<description>` | `build_alert_message()` | Detailed intelligence advisory | `HAZARD: FLOOD — CRITICAL ...` |
| `<parameter>` | `risk_pct`, `confidence_pct`, `affected_nodes` | Machine-readable ML metrics block | `<valueName>RiskScorePct</valueName><value>85.4</value>` |
| `<areaDesc>` | `district`, `state` | Plain text geographic area description | `Chennai, Tamil Nadu` |
| `<circle>` | `latitude`, `longitude`, `radius_km` | WGS84 point and radius format: `{lat},{lon} {radius_km}` | `13.082700,80.270700 7.5` |
| `<geocode>` | `district` | Administrative district code | `<valueName>DISTRICT</valueName><value>CHENNAI</value>` |

---

## 3. Hazard Category Mapping

| TerraEdge Hazard | CAP Category | Rationale |
|---|---|---|
| **Flood** | `Met` | Meteorological hydrologic hazard |
| **Wildfire** | `Env` | Environmental biomass combustion |
| **Landslide** | `Geo` | Geological geotechnical slope failure |
| **Air Quality** | `Env` | Environmental atmospheric pollutant dispersion |
| **Extreme Heat** | `Met` | Meteorological thermal extreme |
| **Industrial Emissions** | `Safety` | Chemical / industrial hazard |
| **Water Quality** | `Env` | Aquatic environmental contamination |

---

## 4. Sample CAP 1.2 XML Document

```xml
<?xml version="1.0" encoding="utf-8"?>
<alert xmlns="urn:oasis:names:tc:emergency:cap:1.2">
  <identifier>ALT-FLOOD-2026-0042</identifier>
  <sender>terraedge-gateway@emergency.gov.in</sender>
  <sent>2026-09-16T15:05:00+00:00</sent>
  <status>Actual</status>
  <msgType>Alert</msgType>
  <scope>Public</scope>
  <code>IPAWS-1.0</code>
  <info>
    <category>Met</category>
    <event>Flood</event>
    <responseType>Execute</responseType>
    <urgency>Immediate</urgency>
    <severity>Extreme</severity>
    <certainty>Observed</certainty>
    <eventCode>TERRAEDGE:FLOOD</eventCode>
    <expires>2026-09-16T21:05:00+00:00</expires>
    <headline>[TERRAEDGE] FLOOD — CRITICAL — CHENNAI</headline>
    <description>TERRAEDGE ALERT

HAZARD: FLOOD — CRITICAL
Location: Chennai, Tamil Nadu
Risk Score: 85.4%
Confidence: 91.2%
Scope: 2 node(s) (TE-001, TE-002)
Time: 2026-09-16T15:05:00+00:00

Action: Review TerraEdge central dashboard for live spatial telemetry &amp; hotspot map.</description>
    <instruction>Observe local emergency services advisories and refer to TerraEdge real-time sensor GIS portal.</instruction>
    <parameter>
      <valueName>RiskScorePct</valueName>
      <value>85.4</value>
    </parameter>
    <parameter>
      <valueName>ConfidencePct</valueName>
      <value>91.2</value>
    </parameter>
    <parameter>
      <valueName>AffectedNodes</valueName>
      <value>TE-001,TE-002</value>
    </parameter>
    <area>
      <areaDesc>Chennai, Tamil Nadu</areaDesc>
      <circle>13.082700,80.270700 7.5</circle>
      <geocode>
        <valueName>DISTRICT</valueName>
        <value>CHENNAI</value>
      </geocode>
    </area>
  </info>
</alert>
```

---

## 5. API Access Endpoint

- **Endpoint**: `GET /api/alerts/{alert_id}/cap`
- **Response Content-Type**: `application/xml`
- **Output**: Returns the full validated OASIS CAP v1.2 XML document string ready for consumption by external emergency warning gateways.
