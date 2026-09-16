"""
TerraEdge — Regional & District Environmental Intelligence Aggregation Engine (Phase 5).

Computes district-level multi-hazard risk, freshness-weighted risk aggregation,
independent multi-node confidence synthesis, derived severity levels,
hazard priority rankings, and spatial hazard hotspot detection.
"""

from __future__ import annotations
import datetime
import math
from typing import Any, Dict, List, Optional, Tuple

from .node_manager import node_manager
from .schemas import (
    DistrictHazardSummary,
    DistrictRiskResponse,
    HotspotCluster,
    RiskMapResponse,
    UnifiedGatewayResponse,
)


def _utc_now_iso() -> str:
    return datetime.datetime.now(datetime.timezone.utc).isoformat()


# Canonical list of the 7 supported environmental hazards
SUPPORTED_HAZARDS = [
    "Flood",
    "Wildfire",
    "Landslide",
    "Air Quality",
    "Extreme Heat",
    "Industrial Emissions",
    "Water Quality",
]

SEVERITY_WEIGHT_MAP = {
    "CRITICAL": 3.0,
    "WARNING": 2.0,
    "WATCH": 1.0,
    "NORMAL": 0.0,
}

SEVERITY_ORDER = ["NORMAL", "WATCH", "WARNING", "CRITICAL"]


class DistrictAggregationEngine:
    """
    Synthesizes regional and district-level intelligence from live multi-node telemetry.
    Acts as the backend single source of truth for spatial risk calculation.
    """

    def __init__(
        self,
        freshness_decay_tau_sec: float = 300.0,
        elevated_risk_threshold_pct: float = 60.0,
        hotspot_max_distance_km: float = 25.0
    ):
        self.freshness_decay_tau_sec = freshness_decay_tau_sec
        self.elevated_risk_threshold_pct = elevated_risk_threshold_pct
        self.hotspot_max_distance_km = hotspot_max_distance_km

    # ========================================================================
    # 1. Freshness Factor Calculation
    # ========================================================================

    def calculate_freshness_factor(self, last_seen_iso: Optional[str]) -> float:
        """
        Calculates a temporal freshness weight w_freshness in [0.0, 1.0].
        - If last_seen is missing or node is OFFLINE (> 300s): returns 0.0 (no contribution).
        - If node is STALE (120s - 300s): returns smooth decay from 0.8 down to 0.1.
        - If node is ONLINE (<= 120s): returns high weight in [0.85, 1.0].
        """
        if not last_seen_iso:
            return 0.0

        try:
            cleaned = last_seen_iso.replace("Z", "+00:00")
            dt = datetime.datetime.fromisoformat(cleaned)
            now = datetime.datetime.now(datetime.timezone.utc)
            if dt.tzinfo is None:
                dt = dt.replace(tzinfo=datetime.timezone.utc)
            delta_sec = max(0.0, (now - dt).total_seconds())

            if delta_sec > 300.0:
                # Fully offline nodes do not contribute to live district calculations
                return 0.0
            elif delta_sec > 120.0:
                # Stale range: linear ramp down
                fraction = (delta_sec - 120.0) / 180.0
                return round(0.8 - (fraction * 0.65), 3)
            else:
                # Online range: exponential / linear preservation
                return round(1.0 - (delta_sec / 120.0) * 0.15, 3)
        except Exception:
            return 0.0

    # ========================================================================
    # 2. District Hazard Aggregation
    # ========================================================================

    def aggregate_district_hazards(
        self,
        nodes: List[Dict[str, Any]],
        evaluations: Dict[str, UnifiedGatewayResponse]
    ) -> List[DistrictHazardSummary]:
        """
        Synthesizes district-level risk, confidence, severity, and ranking for each hazard.
        Formula:
            DistrictRisk = sum(w_i * Conf_i * Risk_i) / sum(w_i * Conf_i)
        """
        summaries: List[DistrictHazardSummary] = []

        for hazard_name in SUPPORTED_HAZARDS:
            total_reporting = 0
            affected_nodes = 0
            weighted_risk_sum = 0.0
            weighted_conf_sum = 0.0
            weight_sum = 0.0
            node_severities: List[str] = []
            contributing_nodes: List[Tuple[str, float]] = []

            for n in nodes:
                node_id = n["node_id"]
                status = n.get("status", "OFFLINE")
                if status == "OFFLINE":
                    continue

                eval_res = evaluations.get(node_id)
                if not eval_res or hazard_name not in eval_res.hazard_results:
                    continue

                h_res = eval_res.hazard_results[hazard_name]
                if h_res.model_status != "success":
                    continue

                freshness = self.calculate_freshness_factor(n.get("last_seen"))
                if freshness <= 0.0:
                    continue

                total_reporting += 1
                n_risk = float(h_res.risk_pct)
                n_conf = float(h_res.confidence_pct)
                node_severities.append(h_res.severity)

                if n_risk >= 40.0 or h_res.severity in ("WATCH", "WARNING", "CRITICAL"):
                    affected_nodes += 1

                node_weight = freshness * (n_conf / 100.0)
                weighted_risk_sum += (node_weight * n_risk)
                weighted_conf_sum += (freshness * n_conf)
                weight_sum += freshness

                contributing_nodes.append((node_id, n_risk))

            # If no active nodes reported for this hazard in the district
            if total_reporting == 0 or weight_sum == 0.0:
                summaries.append(DistrictHazardSummary(
                    hazard=hazard_name,
                    rank=99,
                    risk_pct=0.0,
                    confidence_pct=0.0,
                    severity="NORMAL",
                    affected_nodes=0,
                    total_reporting_nodes=0,
                    priority_score=0.0,
                    alert_candidate=False,
                    top_contributing_nodes=[]
                ))
                continue

            # Compute weighted District Risk
            effective_weight = weighted_conf_sum / 100.0 if weighted_conf_sum > 0 else weight_sum
            district_risk = round(weighted_risk_sum / effective_weight, 1) if effective_weight > 0 else 0.0
            district_risk = min(100.0, max(0.0, district_risk))

            # Compute aggregated District Confidence with sample size scaling
            base_conf = weighted_conf_sum / weight_sum
            # Multi-node support multiplier: S(N) = min(1.0, 0.80 + 0.12 * log2(N + 1))
            support_multiplier = min(1.0, 0.80 + 0.12 * math.log2(total_reporting + 1))
            district_conf = round(min(100.0, max(10.0, base_conf * support_multiplier)), 1)

            # Synthesize District Severity
            crit_count = sum(1 for s in node_severities if s == "CRITICAL")
            warn_count = sum(1 for s in node_severities if s == "WARNING")
            watch_count = sum(1 for s in node_severities if s == "WATCH")

            if (crit_count >= 1 and district_risk >= 65.0) or crit_count >= 2 or district_risk >= 75.0:
                district_sev = "CRITICAL"
            elif (warn_count >= 1 and district_risk >= 45.0) or crit_count >= 1 or district_risk >= 55.0:
                district_sev = "WARNING"
            elif watch_count >= 1 or warn_count >= 1 or district_risk >= 30.0:
                district_sev = "WATCH"
            else:
                district_sev = "NORMAL"

            # Compute priority score for ranking:
            # Priority = Risk * (1.0 + 0.25 * SevWeight) * sqrt(1 + AffectedNodes)
            sev_w = SEVERITY_WEIGHT_MAP.get(district_sev, 0.0)
            priority_score = round(district_risk * (1.0 + 0.25 * sev_w) * math.sqrt(1.0 + affected_nodes), 2)

            # Identify alert candidate
            is_alert_cand = (district_sev in ("WARNING", "CRITICAL")) and (affected_nodes >= 1 or district_risk >= 60.0)

            # Top contributing nodes sorted by risk
            contributing_nodes.sort(key=lambda x: x[1], reverse=True)
            top_node_ids = [nid for nid, _ in contributing_nodes[:5]]

            summaries.append(DistrictHazardSummary(
                hazard=hazard_name,
                rank=1,  # Will be adjusted after sorting
                risk_pct=district_risk,
                confidence_pct=district_conf,
                severity=district_sev,
                affected_nodes=affected_nodes,
                total_reporting_nodes=total_reporting,
                priority_score=priority_score,
                alert_candidate=is_alert_cand,
                top_contributing_nodes=top_node_ids
            ))

        # Sort hazards by priority score descending and assign 1-based rank
        summaries.sort(key=lambda x: x.priority_score, reverse=True)
        for idx, h in enumerate(summaries, start=1):
            h.rank = idx

        return summaries

    # ========================================================================
    # 3. Hotspot Detection
    # ========================================================================

    def detect_hotspots(
        self,
        nodes: List[Dict[str, Any]],
        evaluations: Dict[str, UnifiedGatewayResponse]
    ) -> List[HotspotCluster]:
        """
        Identifies spatial risk concentration hotspots where multiple nearby nodes
        report elevated risk (>= elevated_risk_threshold_pct) for identical hazards.
        """
        hotspots: List[HotspotCluster] = []
        node_map = {n["node_id"]: n for n in nodes if n.get("status") != "OFFLINE"}

        # Group elevated detections per hazard
        for hazard_name in SUPPORTED_HAZARDS:
            elevated_nodes: List[Tuple[str, float, float, float, float, str]] = []

            for nid, n in node_map.items():
                ev = evaluations.get(nid)
                if not ev or hazard_name not in ev.hazard_results:
                    continue

                h_res = ev.hazard_results[hazard_name]
                if h_res.model_status != "success":
                    continue

                lat, lon = n.get("latitude"), n.get("longitude")
                if lat is None or lon is None:
                    continue

                if float(h_res.risk_pct) >= self.elevated_risk_threshold_pct or h_res.severity in ("WARNING", "CRITICAL"):
                    elevated_nodes.append((nid, lat, lon, float(h_res.risk_pct), float(h_res.confidence_pct), h_res.severity))

            if not elevated_nodes:
                continue

            # Cluster elevated nodes geographically (single cluster if <= 5 nodes or within distance)
            clusters: List[List[Tuple[str, float, float, float, float, str]]] = []
            visited = set()

            for i, node_a in enumerate(elevated_nodes):
                if node_a[0] in visited:
                    continue
                cluster = [node_a]
                visited.add(node_a[0])

                for j, node_b in enumerate(elevated_nodes):
                    if node_b[0] in visited:
                        continue
                    dist_km = self._haversine_distance_km(node_a[1], node_a[2], node_b[1], node_b[2])
                    if dist_km <= self.hotspot_max_distance_km:
                        cluster.append(node_b)
                        visited.add(node_b[0])

                clusters.append(cluster)

            # Build HotspotCluster objects
            for c_idx, cluster in enumerate(clusters, start=1):
                c_nids = [c[0] for c in cluster]
                avg_lat = sum(c[1] for c in cluster) / len(cluster)
                avg_lon = sum(c[2] for c in cluster) / len(cluster)
                avg_risk = round(sum(c[3] for c in cluster) / len(cluster), 1)
                avg_conf = round(sum(c[4] for c in cluster) / len(cluster), 1)
                
                # Determine cluster severity
                highest_sev = "WATCH"
                for c in cluster:
                    if c[5] == "CRITICAL":
                        highest_sev = "CRITICAL"
                        break
                    elif c[5] == "WARNING" and highest_sev != "CRITICAL":
                        highest_sev = "WARNING"

                h_id = f"HS-{hazard_name[:3].upper()}-{int(avg_lat*100)}_{int(avg_lon*100)}"
                hotspots.append(HotspotCluster(
                    hotspot_id=h_id,
                    hazard=hazard_name,
                    center_lat=round(avg_lat, 6),
                    center_lon=round(avg_lon, 6),
                    radius_km=round(max(3.0, len(cluster) * 2.5), 1),
                    risk_pct=avg_risk,
                    confidence_pct=avg_conf,
                    severity=highest_sev,
                    affected_nodes=c_nids,
                    timestamp=_utc_now_iso()
                ))

        # Sort hotspots by risk descending
        hotspots.sort(key=lambda h: h.risk_pct, reverse=True)
        return hotspots

    # ========================================================================
    # 4. District & Regional Aggregation APIs
    # ========================================================================

    def aggregate_district(
        self,
        district_name: str,
        state_name: str = "Tamil Nadu",
        evaluations: Optional[Dict[str, UnifiedGatewayResponse]] = None
    ) -> DistrictRiskResponse:
        """Computes comprehensive aggregated intelligence for a single district."""
        from .app import _latest_node_evaluations
        eval_cache = evaluations if evaluations is not None else _latest_node_evaluations

        # Retrieve nodes in district
        nodes = node_manager.get_nodes_by_district(district_name)
        
        # Count health states
        active_cnt = sum(1 for n in nodes if n.get("status") == "ONLINE")
        stale_cnt = sum(1 for n in nodes if n.get("status") == "STALE")
        offline_cnt = sum(1 for n in nodes if n.get("status") == "OFFLINE")

        # Aggregate hazards
        hazards = self.aggregate_district_hazards(nodes, eval_cache)
        hotspots = self.detect_hotspots(nodes, eval_cache)

        top_hazard = hazards[0] if hazards else None
        composite_risk = top_hazard.risk_pct if top_hazard else 0.0
        primary_hazard = top_hazard.hazard if top_hazard and top_hazard.risk_pct > 0 else None
        primary_severity = top_hazard.severity if top_hazard else "NORMAL"

        return DistrictRiskResponse(
            state=state_name,
            district=district_name,
            node_count=len(nodes),
            active_nodes_count=active_cnt,
            stale_nodes_count=stale_cnt,
            offline_nodes_count=offline_cnt,
            composite_risk_pct=composite_risk,
            primary_hazard=primary_hazard,
            primary_severity=primary_severity,
            hazards=hazards,
            hotspots=hotspots,
            nodes=nodes,
            timestamp=_utc_now_iso()
        )

    def aggregate_all_districts(
        self,
        state_name: Optional[str] = None,
        evaluations: Optional[Dict[str, UnifiedGatewayResponse]] = None
    ) -> List[DistrictRiskResponse]:
        """Computes aggregated intelligence across all districts."""
        districts = node_manager.get_all_districts(state=state_name)
        results = []
        for d in districts:
            res = self.aggregate_district(d, state_name=state_name or "Tamil Nadu", evaluations=evaluations)
            results.append(res)
        return results

    def build_risk_map_response(
        self,
        state: Optional[str] = None,
        district: Optional[str] = None,
        evaluations: Optional[Dict[str, UnifiedGatewayResponse]] = None
    ) -> RiskMapResponse:
        """Constructs the complete GIS payload used by the live map dashboard."""
        from .app import _latest_node_evaluations
        eval_cache = evaluations if evaluations is not None else _latest_node_evaluations

        nodes = node_manager.get_all_nodes(state=state, district=district)
        total_cnt = len(nodes)
        active_cnt = sum(1 for n in nodes if n.get("status") == "ONLINE")
        stale_cnt = sum(1 for n in nodes if n.get("status") == "STALE")
        offline_cnt = sum(1 for n in nodes if n.get("status") == "OFFLINE")

        if district:
            districts_data = [self.aggregate_district(district, state_name=state or "Tamil Nadu", evaluations=eval_cache)]
        else:
            districts_data = self.aggregate_all_districts(state_name=state, evaluations=eval_cache)

        hotspots = self.detect_hotspots(nodes, eval_cache)

        return RiskMapResponse(
            state=state,
            district=district,
            total_nodes=total_cnt,
            active_nodes=active_cnt,
            stale_nodes=stale_cnt,
            offline_nodes=offline_cnt,
            districts=districts_data,
            nodes=nodes,
            hotspots=hotspots,
            timestamp=_utc_now_iso()
        )

    @staticmethod
    def _haversine_distance_km(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
        """Calculates great-circle distance between two WGS84 coordinates in kilometers."""
        r = 6371.0  # Earth radius in km
        phi1 = math.radians(lat1)
        phi2 = math.radians(lat2)
        delta_phi = math.radians(lat2 - lat1)
        delta_lambda = math.radians(lon2 - lon1)

        a = (
            math.sin(delta_phi / 2.0) ** 2
            + math.cos(phi1) * math.cos(phi2) * math.sin(delta_lambda / 2.0) ** 2
        )
        c = 2.0 * math.atan2(math.sqrt(a), math.sqrt(1.0 - a))
        return r * c


# Global district aggregation engine instance
district_engine = DistrictAggregationEngine()
