"""
TerraEdge — Phase 8 Model Metadata & Runtime Health Repository.
Tracks versioning, training pedigree, feature schemas, and execution statistics
for all 7 pre-trained ML hazard engines without modifying model weights.
"""

from __future__ import annotations
import datetime
import threading
from typing import Any, Dict, Optional


def _utc_now_iso() -> str:
    return datetime.datetime.now(datetime.timezone.utc).isoformat()


MODEL_REGISTRY: Dict[str, Dict[str, Any]] = {
    "Flood": {
        "model_version": "1.2.0",
        "artifact_version": "rf_flood_2025_v1",
        "algorithm": "RandomForest / XGBoost Ensemble",
        "feature_schema_version": "1.0",
        "trained_at": "2025-08-15T00:00:00Z",
        "primary_features": ["rainfall_mm_h", "water_level_m", "soil_moisture_pct", "flow_rate_m3_s"],
    },
    "Wildfire": {
        "model_version": "2.0.1",
        "artifact_version": "wildfire_multioutput_v2",
        "algorithm": "Multi-Output Random Forest + Isolation Forest",
        "feature_schema_version": "1.0",
        "trained_at": "2025-08-10T00:00:00Z",
        "primary_features": ["temperature_c", "humidity_pct", "wind_speed_km_h", "soil_moisture_pct", "flame_detected"],
    },
    "Landslide": {
        "model_version": "1.1.0",
        "artifact_version": "landslide_rf_v1",
        "algorithm": "RandomForestClassifier",
        "feature_schema_version": "1.0",
        "trained_at": "2025-08-12T00:00:00Z",
        "primary_features": ["rainfall_mm_h", "soil_moisture_pct", "tilt_angle_deg", "vibration_level_g"],
    },
    "Air Quality": {
        "model_version": "1.0.0",
        "artifact_version": "aqi_gb_v1",
        "algorithm": "GradientBoostingRegressor / AQI Classifier",
        "feature_schema_version": "1.0",
        "trained_at": "2025-08-05T00:00:00Z",
        "primary_features": ["pm2_5_ug_m3", "pm10_ug_m3", "co_ppm", "gas_resistance_ohms"],
    },
    "Extreme Heat": {
        "model_version": "1.0.0",
        "artifact_version": "heat_index_ensemble_v1",
        "algorithm": "Thermal Index & Heat Stress Classifier",
        "feature_schema_version": "1.0",
        "trained_at": "2025-08-08T00:00:00Z",
        "primary_features": ["temperature_c", "humidity_pct", "ambient_temp_c", "solar_radiation_w_m2"],
    },
    "Toxic Flame": {
        "model_version": "1.0.0",
        "artifact_version": "toxic_flame_dual_tree_v1",
        "algorithm": "Dual Flame & Hazardous Gas Ensemble",
        "feature_schema_version": "1.0",
        "trained_at": "2025-08-14T00:00:00Z",
        "primary_features": ["flame_detected", "co_ppm", "gas_resistance_ohms", "smoke_detected"],
    },
    "Water Quality": {
        "model_version": "1.0.0",
        "artifact_version": "wqi_multiclass_v1",
        "algorithm": "Water Quality Index Scoring & Classifier",
        "feature_schema_version": "1.0",
        "trained_at": "2025-08-11T00:00:00Z",
        "primary_features": ["ph", "turbidity_ntu", "water_temp_c", "tds_ppm", "flow_rate_m3_s"],
    },
}


class ModelHealthTracker:
    """Tracks runtime execution statistics and health for all ML models."""
    def __init__(self):
        self._lock = threading.Lock()
        self._stats: Dict[str, Dict[str, Any]] = {}
        for h_name, meta in MODEL_REGISTRY.items():
            self._stats[h_name] = {
                **meta,
                "loaded": True,
                "inference_count": 0,
                "error_count": 0,
                "last_inference_time": None,
                "last_error": None,
            }

    def record_inference(self, hazard: str, success: bool = True, error_msg: Optional[str] = None) -> None:
        with self._lock:
            if hazard not in self._stats:
                return
            entry = self._stats[hazard]
            entry["inference_count"] += 1
            entry["last_inference_time"] = _utc_now_iso()
            if not success:
                entry["error_count"] += 1
                entry["last_error"] = error_msg

    def get_model_health(self, hazard: str) -> Optional[Dict[str, Any]]:
        with self._lock:
            return dict(self._stats.get(hazard, {}))

    def get_all_models_health(self) -> Dict[str, Dict[str, Any]]:
        with self._lock:
            return {k: dict(v) for k, v in self._stats.items()}


# Global model health tracker singleton
model_health_tracker = ModelHealthTracker()
