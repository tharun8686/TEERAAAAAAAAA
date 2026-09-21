"""
TerraEdge — Gateway Hazard Router.
Dynamically imports and orchestrates the 7 existing machine learning hazard inference engines.
Ensures zero namespace collisions, isolated fault containment, and clean output normalization.
"""

from __future__ import annotations
import importlib.util
import os
import sys
import threading
from typing import Any, Dict, Optional

from .config import PROJECT_ROOT
from .feature_builder import (
    build_air_pollution_features,
    build_flood_features,
    build_heat_features,
    build_industrial_features,
    build_landslide_features,
    build_water_quality_features,
    build_wildfire_features,
)
from .schemas import HazardPredictionResult
from .telemetry import ProcessedTelemetry


def _load_module_by_path(module_name: str, file_path: str):
    """Dynamically loads a Python module from an absolute path avoiding sys.modules collisions."""
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"Module file not found: {file_path}")
    spec = importlib.util.spec_from_file_location(module_name, file_path)
    if spec is None or spec.loader is None:
        raise ImportError(f"Could not load spec for: {file_path}")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


class HazardRouter:
    """Orchestrates feature adaptation and execution across all 7 environmental hazard models."""

    def __init__(self):
        self._lock = threading.Lock()
        self.engines: Dict[str, Any] = {}
        self.engine_errors: Dict[str, str] = {}
        self._load_all_engines()

    def _load_all_engines(self) -> None:
        """Initializes all 7 hazard inference engines."""
        # 1. Flood
        try:
            p = os.path.join(PROJECT_ROOT, "Flood", "src", "inference", "flood_inference.py")
            m = _load_module_by_path("terra_flood_inference", p)
            models_dir = os.path.join(PROJECT_ROOT, "Flood", "models")
            self.engines["Flood"] = m.FloodInferenceEngine(models_dir)
            print("[hazard-router] Flood model loaded successfully", flush=True)
        except Exception as e:
            self.engine_errors["Flood"] = str(e)
            print(f"[hazard-router] Error loading Flood model: {e}", flush=True)

        # 2. Wildfire
        try:
            p = os.path.join(PROJECT_ROOT, "ForestWildFire", "src", "inference", "fire_inference.py")
            m = _load_module_by_path("terra_fire_inference", p)
            self.engines["Wildfire"] = m.FireInferenceEngine()
            print("[hazard-router] Wildfire model loaded successfully", flush=True)
        except Exception as e:
            self.engine_errors["Wildfire"] = str(e)
            print(f"[hazard-router] Error loading Wildfire model: {e}", flush=True)

        # 3. Landslide
        try:
            p = os.path.join(PROJECT_ROOT, "Landslide", "src", "inference", "landslide_inference.py")
            m = _load_module_by_path("terra_landslide_inference", p)
            self.engines["Landslide"] = m.LandslideInferenceEngine()
            print("[hazard-router] Landslide model loaded successfully", flush=True)
        except Exception as e:
            self.engine_errors["Landslide"] = str(e)
            print(f"[hazard-router] Error loading Landslide model: {e}", flush=True)

        # 4. Air Quality
        try:
            p = os.path.join(PROJECT_ROOT, "AirPollution", "src", "inference.py")
            m = _load_module_by_path("terra_air_inference", p)
            self.engines["Air Quality"] = m.AirPollutionInferenceEngine()
            print("[hazard-router] Air Quality model loaded successfully", flush=True)
        except Exception as e:
            self.engine_errors["Air Quality"] = str(e)
            print(f"[hazard-router] Error loading Air Quality model: {e}", flush=True)

        # 5. Extreme Heat
        try:
            p = os.path.join(PROJECT_ROOT, "Extreme Heat", "src", "inference", "heat_inference.py")
            m = _load_module_by_path("terra_heat_inference", p)
            models_dir = os.path.join(PROJECT_ROOT, "Extreme Heat", "models")
            self.engines["Extreme Heat"] = m.HeatRiskPredictor(models_dir)
            print("[hazard-router] Extreme Heat model loaded successfully", flush=True)
        except Exception as e:
            self.engine_errors["Extreme Heat"] = str(e)
            print(f"[hazard-router] Error loading Extreme Heat model: {e}", flush=True)

        # 6. Toxic Flame / Industrial Emissions
        try:
            p = os.path.join(PROJECT_ROOT, "Industrial Emissions", "src", "inference", "industrial_inference.py")
            m = _load_module_by_path("terra_industrial_inference", p)
            models_dir = os.path.join(PROJECT_ROOT, "Industrial Emissions", "models")
            self.engines["Toxic Flame"] = m.IndustrialEmissionsPredictor(models_dir)
            print("[hazard-router] Toxic Flame model loaded successfully", flush=True)
        except Exception as e:
            self.engine_errors["Toxic Flame"] = str(e)
            print(f"[hazard-router] Error loading Toxic Flame model: {e}", flush=True)

        # 7. Water Quality
        try:
            p = os.path.join(PROJECT_ROOT, "Water Quality Degradation", "src", "inference", "water_inference.py")
            m = _load_module_by_path("terra_water_inference", p)
            models_dir = os.path.join(PROJECT_ROOT, "Water Quality Degradation", "models")
            self.engines["Water Quality"] = m.WaterQualityPredictor(models_dir)
            print("[hazard-router] Water Quality model loaded successfully", flush=True)
        except Exception as e:
            self.engine_errors["Water Quality"] = str(e)
            print(f"[hazard-router] Error loading Water Quality model: {e}", flush=True)

    def evaluate_all(self, proc: ProcessedTelemetry) -> Dict[str, HazardPredictionResult]:
        """Runs all 7 hazard models in isolated try-except blocks and normalizes their outputs."""
        if not proc.raw.is_simulated:
            from .live_models import live_models
            return live_models.evaluate(proc.raw, self)
        results: Dict[str, HazardPredictionResult] = {}

        # 1. Flood
        results["Flood"] = self._eval_flood(proc)

        # 2. Wildfire
        results["Wildfire"] = self._eval_wildfire(proc)

        # 3. Landslide
        results["Landslide"] = self._eval_landslide(proc)

        # 4. Air Quality
        results["Air Quality"] = self._eval_air_quality(proc)

        # 5. Extreme Heat
        results["Extreme Heat"] = self._eval_heat(proc)

        # 6. Toxic Flame
        results["Toxic Flame"] = self._eval_industrial(proc)

        # 7. Water Quality
        results["Water Quality"] = self._eval_water_quality(proc)

        return results

    # ========================================================================
    # Hazard Evaluator Helpers
    # ========================================================================

    def _eval_flood(self, proc: ProcessedTelemetry) -> HazardPredictionResult:
        hazard = "Flood"
        feat_res = build_flood_features(proc)
        if not feat_res.ready:
            return self._skipped_result(hazard, feat_res.reason)

        engine = self.engines.get(hazard)
        if not engine:
            return self._error_result(hazard, self.engine_errors.get(hazard, "Engine not loaded"))

        try:
            raw = engine.predict_flood(feat_res.features)
            # Normalize risk
            risk_pct = float(raw.get("risk_score_pct") or (raw.get("risk_probability", 0.0) * 100.0))
            conf_pct = float(raw.get("confidence_pct") or (raw.get("confidence", 0.90) * 100.0))
            sev = str(raw.get("severity") or raw.get("severity_level", "NORMAL"))
            anomaly = float(raw.get("anomaly_score", 0.0))
            top_feats = raw.get("top_features", ["water_level_m", "rain_24h"])

            return HazardPredictionResult(
                hazard=hazard,
                risk_pct=round(min(100.0, max(0.0, risk_pct)), 1),
                confidence_pct=round(min(100.0, max(0.0, conf_pct)), 1),
                severity=sev,
                anomaly_score=round(anomaly, 4),
                top_features=top_feats,
                model_status="success",
                details=raw
            )
        except Exception as e:
            return self._error_result(hazard, str(e))

    def _eval_wildfire(self, proc: ProcessedTelemetry) -> HazardPredictionResult:
        hazard = "Wildfire"
        feat_res = build_wildfire_features(proc)
        if not feat_res.ready:
            return self._skipped_result(hazard, feat_res.reason)

        engine = self.engines.get(hazard)
        if not engine:
            return self._error_result(hazard, self.engine_errors.get(hazard, "Engine not loaded"))

        try:
            raw = engine.predict_fire(feat_res.features)
            risk_pct = float(raw.get("fire_probability", 0.0) * 100.0)
            conf_pct = float(raw.get("confidence", 0.95) * 100.0)
            sev = str(raw.get("severity", "NORMAL"))
            anomaly = float(raw.get("anomaly_score", 0.0))
            top_feats = raw.get("top_features", ["temperature", "humidity", "tvoc_rate"])
            
            # If optical flame is directly asserted by physical switch, escalate severity
            if proc.get("flame") == 1:
                risk_pct = max(95.0, risk_pct)
                sev = "CRITICAL"
                top_feats = ["optical_flame_sensor"] + top_feats

            return HazardPredictionResult(
                hazard=hazard,
                risk_pct=round(min(100.0, max(0.0, risk_pct)), 1),
                confidence_pct=round(min(100.0, max(0.0, conf_pct)), 1),
                severity=sev,
                anomaly_score=round(anomaly, 4),
                top_features=top_feats,
                model_status="success",
                details=raw
            )
        except Exception as e:
            return self._error_result(hazard, str(e))

    def _eval_landslide(self, proc: ProcessedTelemetry) -> HazardPredictionResult:
        hazard = "Landslide"
        feat_res = build_landslide_features(proc)
        if not feat_res.ready:
            return self._skipped_result(hazard, feat_res.reason)

        engine = self.engines.get(hazard)
        if not engine:
            return self._error_result(hazard, self.engine_errors.get(hazard, "Engine not loaded"))

        try:
            raw = engine.predict_landslide(feat_res.features)
            risk_pct = float(raw.get("risk_probability", 0.0) * 100.0)
            conf_pct = float(raw.get("confidence", 0.92) * 100.0)
            sev = str(raw.get("severity", "NORMAL"))
            anomaly = float(raw.get("anomaly_score", 0.0))
            top_feats = raw.get("top_features", ["soil_moisture_vwc", "tilt_magnitude", "tilt_rate"])

            return HazardPredictionResult(
                hazard=hazard,
                risk_pct=round(min(100.0, max(0.0, risk_pct)), 1),
                confidence_pct=round(min(100.0, max(0.0, conf_pct)), 1),
                severity=sev,
                anomaly_score=round(anomaly, 4),
                top_features=top_feats,
                model_status="success",
                details=raw
            )
        except Exception as e:
            return self._error_result(hazard, str(e))

    def _eval_air_quality(self, proc: ProcessedTelemetry) -> HazardPredictionResult:
        hazard = "Air Quality"
        feat_res = build_air_pollution_features(proc)
        if not feat_res.ready:
            return self._skipped_result(hazard, feat_res.reason)

        engine = self.engines.get(hazard)
        if not engine:
            return self._error_result(hazard, self.engine_errors.get(hazard, "Engine not loaded"))

        try:
            raw = engine.predict_air_pollution(feat_res.features)
            risk_pct = float(raw.get("risk_score") or (raw.get("risk_probability", 0.0) * 100.0))
            conf_pct = float(raw.get("confidence", 90.0))
            sev = str(raw.get("severity", "NORMAL"))
            anomaly = float(raw.get("anomaly_score", 0.0))
            top_feats = raw.get("top_features", ["pm25", "pm10", "gas_proxy"])

            return HazardPredictionResult(
                hazard=hazard,
                risk_pct=round(min(100.0, max(0.0, risk_pct)), 1),
                confidence_pct=round(min(100.0, max(0.0, conf_pct)), 1),
                severity=sev,
                anomaly_score=round(anomaly, 4),
                top_features=top_feats,
                model_status="success",
                details=raw
            )
        except Exception as e:
            return self._error_result(hazard, str(e))

    def _eval_heat(self, proc: ProcessedTelemetry) -> HazardPredictionResult:
        hazard = "Extreme Heat"
        feat_res = build_heat_features(proc)
        if not feat_res.ready:
            return self._skipped_result(hazard, feat_res.reason)

        engine = self.engines.get(hazard)
        if not engine:
            return self._error_result(hazard, self.engine_errors.get(hazard, "Engine not loaded"))

        try:
            raw = engine.predict_heat_risk(feat_res.features)
            risk_pct = float(raw.get("heat_risk_probability", raw.get("risk_probability", 0.0)) * 100.0)
            conf_pct = float(raw.get("confidence", 0.90) * 100.0)
            sev = str(raw.get("severity", "NORMAL"))
            anomaly = float(raw.get("anomaly_score", 0.0))
            top_feats = raw.get("top_features", ["temperature_c", "rolling_mean_temperature"])

            return HazardPredictionResult(
                hazard=hazard,
                risk_pct=round(min(100.0, max(0.0, risk_pct)), 1),
                confidence_pct=round(min(100.0, max(0.0, conf_pct)), 1),
                severity=sev,
                anomaly_score=round(anomaly, 4),
                top_features=top_feats,
                model_status="success",
                details=raw
            )
        except Exception as e:
            return self._error_result(hazard, str(e))

    def _eval_industrial(self, proc: ProcessedTelemetry) -> HazardPredictionResult:
        hazard = "Toxic Flame"
        feat_res = build_industrial_features(proc)
        if not feat_res.ready:
            return self._skipped_result(hazard, feat_res.reason)

        engine = self.engines.get(hazard)
        if not engine:
            return self._error_result(hazard, self.engine_errors.get(hazard, "Engine not loaded"))

        try:
            raw = engine.predict_industrial_risk(feat_res.features)
            risk_pct = float(raw.get("leak_risk_probability", raw.get("risk_probability", 0.0)) * 100.0)
            conf_pct = float(raw.get("confidence", 0.88) * 100.0)
            sev = str(raw.get("severity", "NORMAL"))
            anomaly = float(raw.get("anomaly_score", 0.0))
            top_feats = raw.get("top_features", ["gas_response", "PM2.5", "gas_spike_score"])

            return HazardPredictionResult(
                hazard=hazard,
                risk_pct=round(min(100.0, max(0.0, risk_pct)), 1),
                confidence_pct=round(min(100.0, max(0.0, conf_pct)), 1),
                severity=sev,
                anomaly_score=round(anomaly, 4),
                top_features=top_feats,
                model_status="success",
                details=raw
            )
        except Exception as e:
            return self._error_result(hazard, str(e))

    def _eval_water_quality(self, proc: ProcessedTelemetry) -> HazardPredictionResult:
        hazard = "Water Quality"
        feat_res = build_water_quality_features(proc)
        if not feat_res.ready:
            return self._skipped_result(hazard, feat_res.reason)

        engine = self.engines.get(hazard)
        if not engine:
            return self._error_result(hazard, self.engine_errors.get(hazard, "Engine not loaded"))

        try:
            raw = engine.predict_water_quality_risk(feat_res.features)
            risk_pct = float(raw.get("water_quality_risk_probability", raw.get("risk_probability", 0.0)) * 100.0)
            conf_pct = float(raw.get("confidence", 0.85) * 100.0)
            sev = str(raw.get("severity", "NORMAL"))
            anomaly = float(raw.get("anomaly_score", 0.0))
            top_feats = raw.get("top_features", ["pH", "turbidity", "TDS"])

            return HazardPredictionResult(
                hazard=hazard,
                risk_pct=round(min(100.0, max(0.0, risk_pct)), 1),
                confidence_pct=round(min(100.0, max(0.0, conf_pct)), 1),
                severity=sev,
                anomaly_score=round(anomaly, 4),
                top_features=top_feats,
                model_status="success",
                details=raw
            )
        except Exception as e:
            return self._error_result(hazard, str(e))

    def _skipped_result(self, hazard: str, reason: Optional[str]) -> HazardPredictionResult:
        return HazardPredictionResult(
            hazard=hazard,
            risk_pct=0.0,
            confidence_pct=0.0,
            severity="NORMAL",
            anomaly_score=0.0,
            top_features=[],
            model_status="skipped",
            skip_reason=reason or "Required sensor inputs absent",
            details={}
        )

    def _error_result(self, hazard: str, err_msg: str) -> HazardPredictionResult:
        return HazardPredictionResult(
            hazard=hazard,
            risk_pct=0.0,
            confidence_pct=0.0,
            severity="NORMAL",
            anomaly_score=0.0,
            top_features=[],
            model_status="error",
            error=err_msg,
            details={}
        )


# Global hazard router instance
hazard_router = HazardRouter()
