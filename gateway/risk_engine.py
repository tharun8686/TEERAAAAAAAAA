"""
TerraEdge — Gateway Multi-Hazard Risk & Ranking Engine.
Aggregates individual model predictions, normalizes cross-hazard threat metrics,
calculates composite risk, and computes hazard priority rankings.
"""

from __future__ import annotations
import datetime
from typing import Any, Dict, List, Optional, Tuple

from .schemas import HazardPredictionResult, HazardRanking

SEVERITY_LEVEL_MAP = {
    "CRITICAL": 4,
    "WARNING": 3,
    "WATCH": 2,
    "NORMAL": 1,
    "UNKNOWN": 0
}

SEVERITY_WEIGHT_MAP = {
    "CRITICAL": 2.5,
    "WARNING": 1.8,
    "WATCH": 1.2,
    "NORMAL": 0.8,
    "UNKNOWN": 0.5
}


class RiskEngine:
    """Computes cross-hazard priority ranking, composite threat levels, and alert candidates."""

    def evaluate_node_risk(
        self,
        node_id: str,
        hazard_results: Dict[str, HazardPredictionResult]
    ) -> Tuple[float, Optional[str], str, float, List[HazardRanking], List[Dict[str, Any]]]:
        """
        Processes normalized hazard results and returns:
        (composite_risk_pct, primary_hazard, primary_severity, top_priority_score, ranked_hazards, alerts)
        """
        active_candidates: List[Tuple[float, HazardPredictionResult]] = []
        highest_severity_level = 0
        primary_severity = "NORMAL"
        alerts: List[Dict[str, Any]] = []

        for name, res in hazard_results.items():
            # Skip non-successful inferences from priority ranking
            if res.model_status != "success":
                continue

            sev_upper = res.severity.upper() if res.severity else "NORMAL"
            sev_level = SEVERITY_LEVEL_MAP.get(sev_upper, 1)
            sev_weight = SEVERITY_WEIGHT_MAP.get(sev_upper, 0.8)

            if sev_level > highest_severity_level:
                highest_severity_level = sev_level
                primary_severity = sev_upper

            # Transparent priority score formula:
            # - 50% weighted by calibrated risk percentage
            # - 25% weighted by model confidence
            # - 25% weighted by severity multiplier
            priority_score = (res.risk_pct * 0.50) + (res.confidence_pct * 0.25) + (sev_weight * 10.0)
            active_candidates.append((priority_score, res))

            # Threshold breach alert candidate
            if sev_upper in ("WARNING", "CRITICAL"):
                alerts.append({
                    "hazard": res.hazard or name,
                    "hazard_type": name,
                    "node_id": node_id,
                    "severity": sev_upper,
                    "risk_score_pct": res.risk_pct,
                    "confidence_pct": res.confidence_pct,
                    "top_features": res.top_features,
                    "timestamp": res.timestamp,
                    "details": res.details
                })

        # Sort descending by priority score
        active_candidates.sort(key=lambda x: x[0], reverse=True)

        ranked_hazards: List[HazardRanking] = []
        for idx, (score, res) in enumerate(active_candidates, start=1):
            ranked_hazards.append(
                HazardRanking(
                    hazard=res.hazard,
                    rank=idx,
                    risk_pct=res.risk_pct,
                    confidence_pct=res.confidence_pct,
                    severity=res.severity,
                    priority_score=round(score, 2)
                )
            )

        if active_candidates:
            top_score, top_res = active_candidates[0]
            primary_hazard = top_res.hazard
            top_priority_score = round(top_score, 2)
            # Composite risk is maximum risk among active hazards
            composite_risk_pct = round(max(r.risk_pct for _, r in active_candidates), 1)
        else:
            primary_hazard = None
            top_priority_score = 0.0
            composite_risk_pct = 0.0
            primary_severity = "UNKNOWN"

        return composite_risk_pct, primary_hazard, primary_severity, top_priority_score, ranked_hazards, alerts


# Global risk engine instance
risk_engine = RiskEngine()
