"""
TerraEdge — Telemetry Ingestion & Temporal Feature Processor.
Maintains in-memory circular history buffers per node to compute temporal rates,
lags, cyclical hour features, and rolling window metrics required by ML models.

Phase 2: Updated for final hardware canonical field names.
  pm25_ug_m3, pm10_ug_m3 (SDS011)
  tds_ppm (TDS sensor)
  mq135_raw (MQ-135, replaces mq2_raw/mq7_raw)
  ultrasonic_distance_cm (JSN-SR04T)
  flame_detected (IR flame sensor, bool)
"""

from __future__ import annotations
import collections
import datetime
import math
import statistics
import threading
from typing import Any, Dict, List, Optional

from .config import MAX_HISTORY_PER_NODE
from .schemas import TypeATelemetryPayload


class ProcessedTelemetry:
    """Wrapper holding raw telemetry plus calculated temporal and rolling derivatives."""

    def __init__(self, raw: TypeATelemetryPayload, derived: Dict[str, Any]):
        self.raw = raw
        self.derived = derived

    def get(self, key: str, default: Any = None) -> Any:
        val = getattr(self.raw, key, None)
        if val is not None:
            return val
        return self.derived.get(key, default)

    def to_dict(self) -> Dict[str, Any]:
        data = self.raw.model_dump()
        data["derived"] = self.derived
        return data


class TelemetryHistoryEngine:
    """Manages per-node time-series buffers and derives temporal feature vectors."""

    # JSN-SR04T calibration: sensor mounting height above channel bottom (cm).
    # Override per-node for accurate water level derivation.
    ULTRASONIC_REFERENCE_HEIGHT_CM: float = 300.0

    def __init__(self, max_history: int = MAX_HISTORY_PER_NODE):
        self.max_history = max_history
        self._lock = threading.Lock()
        self._history: Dict[str, collections.deque] = {}

    def process(self, telemetry: TypeATelemetryPayload) -> ProcessedTelemetry:
        """Processes incoming telemetry frame, calculates derivatives, and updates history."""
        node_id = telemetry.node_id

        with self._lock:
            if node_id not in self._history:
                self._history[node_id] = collections.deque(maxlen=self.max_history)

            history_list = list(self._history[node_id])
            derived = self._calculate_derived_features(telemetry, history_list)

            # Store current frame using final hardware canonical names
            self._history[node_id].append({
                "timestamp":              telemetry.timestamp,
                "temperature_c":          telemetry.temperature_c,
                "humidity_pct":           telemetry.humidity_pct,
                "pressure_hpa":           telemetry.pressure_hpa,
                "gas_resistance_kohm":    telemetry.gas_resistance_kohm,
                "rainfall_mm":            telemetry.rainfall_mm,
                "rainfall_1h_mm":         telemetry.rainfall_1h_mm,
                "rainfall_24h_mm":        telemetry.rainfall_24h_mm,
                "water_level_m":          telemetry.water_level_m,
                "ultrasonic_distance_cm": telemetry.ultrasonic_distance_cm,
                "soil_moisture_pct":      telemetry.soil_moisture_pct,
                # SDS011 — canonical names
                "pm25_ug_m3":             telemetry.pm25_ug_m3,
                "pm10_ug_m3":             telemetry.pm10_ug_m3,
                # MQ-135 — replaces mq2_raw/mq7_raw (LEGACY removed)
                "mq135_raw":              telemetry.mq135_raw,
                # Geotechnical
                "tilt_magnitude":         telemetry.tilt_magnitude,
                # Water quality — canonical names
                "ph":                     telemetry.ph,
                "tds_ppm":                telemetry.tds_ppm,
                "turbidity":              telemetry.turbidity,
                # LEGACY — kept for optional lab-sensor compat
                "dissolved_oxygen":       telemetry.dissolved_oxygen,
            })

        return ProcessedTelemetry(raw=telemetry, derived=derived)

    def _calculate_derived_features(self, curr: TypeATelemetryPayload, history: List[Dict[str, Any]]) -> Dict[str, Any]:
        derived: Dict[str, Any] = {}
        prev = history[-1] if history else {}

        # 1. Cyclical Hour Embeddings
        try:
            cleaned_iso = curr.timestamp.replace("Z", "+00:00")
            dt = datetime.datetime.fromisoformat(cleaned_iso)
            hour_float = dt.hour + dt.minute / 60.0
            derived["hour_sin"] = round(math.sin(2 * math.pi * hour_float / 24.0), 4)
            derived["hour_cos"] = round(math.cos(2 * math.pi * hour_float / 24.0), 4)
        except Exception:
            derived["hour_sin"] = 0.0
            derived["hour_cos"] = 1.0

        # 2. Flame alias (bool <-> int)
        if curr.flame_detected is not None:
            derived["flame"] = 1 if curr.flame_detected else 0
        elif curr.flame is not None:
            derived["flame_detected"] = bool(curr.flame)

        # 3. JSN-SR04T → water_level_m derivation
        # Used when water_level_m is absent but ultrasonic_distance_cm is present.
        # Formula: water_level_m = (reference_height_cm - ultrasonic_distance_cm) / 100
        # Default reference_height_cm = 300 cm. Requires field calibration per node.
        if curr.is_simulated and curr.water_level_m is None and curr.ultrasonic_distance_cm is not None:
            derived["water_level_m"] = max(0.0, (
                self.ULTRASONIC_REFERENCE_HEIGHT_CM - curr.ultrasonic_distance_cm
            ) / 100.0)

        # 4. Rate of Change
        derived["temperature_rate"]   = self._diff(curr.temperature_c, prev.get("temperature_c"))
        derived["humidity_rate"]       = self._diff(curr.humidity_pct, prev.get("humidity_pct"))
        derived["pm25_rate"]           = self._diff(curr.pm25_ug_m3, prev.get("pm25_ug_m3"))
        derived["pm10_rate"]           = self._diff(curr.pm10_ug_m3, prev.get("pm10_ug_m3"))
        derived["soil_moisture_rate"]  = self._diff(curr.soil_moisture_pct, prev.get("soil_moisture_pct"))

        # Tilt rate — direct from MPU6050 preferred, else history diff
        if curr.tilt_rate is not None:
            derived["tilt_rate"] = curr.tilt_rate
        else:
            derived["tilt_rate"] = self._diff(curr.tilt_magnitude, prev.get("tilt_magnitude"))

        # Gas rate — MQ-135 or BME680 gas resistance (MQ-2/MQ-7 REMOVED from final hardware)
        gas_curr = curr.mq135_raw or curr.gas_resistance_kohm
        gas_prev = prev.get("mq135_raw") or prev.get("gas_resistance_kohm")
        derived["gas_rate"]  = self._diff(gas_curr, gas_prev)
        derived["tvoc_rate"] = derived["gas_rate"]  # proxy used by wildfire model

        # Water chemistry rates
        derived["ph_rate"]        = self._diff(curr.ph, prev.get("ph"))
        derived["turbidity_rate"] = self._diff(curr.turbidity, prev.get("turbidity"))
        derived["tds_rate"]       = self._diff(curr.tds_ppm, prev.get("tds_ppm"))
        derived["do_rate"]        = self._diff(curr.dissolved_oxygen, prev.get("dissolved_oxygen"))
        derived["ec_rate"]        = 0.0  # No EC probe in final hardware

        # 5. Delta & Lag Features
        derived["temperature_delta_5"] = derived["temperature_rate"] * 5.0
        derived["humidity_delta_5"]    = derived["humidity_rate"] * 5.0

        # PM2.5 lags (canonical pm25_ug_m3 from history)
        pm25_history = [h["pm25_ug_m3"] for h in history if h.get("pm25_ug_m3") is not None]
        curr_pm25 = curr.pm25_ug_m3 or (pm25_history[-1] if pm25_history else 35.0)
        derived["pm25_lag_15"]  = pm25_history[-2] if len(pm25_history) >= 2 else curr_pm25
        derived["pm25_lag_30"]  = pm25_history[-4] if len(pm25_history) >= 4 else curr_pm25
        derived["pm25_delta_30"]= round(curr_pm25 - derived["pm25_lag_30"], 2)
        derived["pm25_slope_30"]= round(derived["pm25_delta_30"] / 30.0, 4)

        # 6. Rolling Stats — Temperature & Humidity (BME680)
        temps = [h["temperature_c"] for h in history if h.get("temperature_c") is not None]
        if curr.temperature_c is not None:
            temps.append(curr.temperature_c)
        derived["rolling_mean_temperature"] = round(statistics.mean(temps), 2) if temps else (curr.temperature_c or 27.5)
        derived["rolling_std_temperature"]  = round(statistics.stdev(temps), 2) if len(temps) > 1 else 0.5

        hums = [h["humidity_pct"] for h in history if h.get("humidity_pct") is not None]
        if curr.humidity_pct is not None:
            hums.append(curr.humidity_pct)
        derived["rolling_mean_humidity"] = round(statistics.mean(hums), 2) if hums else (curr.humidity_pct or 65.0)
        derived["rolling_std_humidity"]  = round(statistics.stdev(hums), 2) if len(hums) > 1 else 1.0

        # 7. Rolling Stats — PM2.5 (SDS011, canonical pm25_ug_m3)
        pms = [h["pm25_ug_m3"] for h in history if h.get("pm25_ug_m3") is not None]
        if curr.pm25_ug_m3 is not None:
            pms.append(curr.pm25_ug_m3)
        derived["rolling_mean_pm25"] = round(statistics.mean(pms), 2) if pms else (curr.pm25_ug_m3 or 45.0)
        derived["rolling_std_pm25"]  = round(statistics.stdev(pms), 2) if len(pms) > 1 else 1.5

        # 8. Rolling Stats — MQ-135 gas proxy
        gases = [h["mq135_raw"] for h in history if h.get("mq135_raw") is not None]
        if curr.mq135_raw is not None:
            gases.append(curr.mq135_raw)
        derived["rolling_mean_gas"] = round(statistics.mean(gases), 2) if gases else (curr.mq135_raw or 150.0)
        derived["rolling_std_gas"]  = round(statistics.stdev(gases), 2) if len(gases) > 1 else 2.0

        # 9. Rolling Stats — Water Quality (pH, turbidity, TDS, EC derived, DO injected)
        phs = [h["ph"] for h in history if h.get("ph") is not None]
        if curr.ph is not None:
            phs.append(curr.ph)
        derived["rolling_mean_pH"] = round(statistics.mean(phs), 3) if phs else (curr.ph or 7.2)
        derived["rolling_std_pH"]  = round(statistics.stdev(phs), 3) if len(phs) > 1 else 0.05

        turbs = [h["turbidity"] for h in history if h.get("turbidity") is not None]
        if curr.turbidity is not None:
            turbs.append(curr.turbidity)
        derived["rolling_mean_turbidity"] = round(statistics.mean(turbs), 2) if turbs else (curr.turbidity or 2.5)
        derived["rolling_std_turbidity"]  = round(statistics.stdev(turbs), 2) if len(turbs) > 1 else 0.2

        tdss = [h["tds_ppm"] for h in history if h.get("tds_ppm") is not None]
        if curr.tds_ppm is not None:
            tdss.append(curr.tds_ppm)
        derived["rolling_mean_TDS"] = round(statistics.mean(tdss), 2) if tdss else (curr.tds_ppm or 180.0)
        derived["rolling_std_TDS"]  = round(statistics.stdev(tdss), 2) if len(tdss) > 1 else 5.0

        # EC derived from TDS rolling stats (EC ≈ TDS × 1.56, no EC probe in final hardware)
        derived["rolling_mean_EC"] = round(derived["rolling_mean_TDS"] * 1.56, 2)
        derived["rolling_std_EC"]  = round(derived["rolling_std_TDS"]  * 1.56, 2)

        # DO rolling stats (injected defaults — no DO probe in final hardware)
        do_hist = [h["dissolved_oxygen"] for h in history if h.get("dissolved_oxygen") is not None]
        if curr.dissolved_oxygen is not None:
            do_hist.append(curr.dissolved_oxygen)
        derived["rolling_mean_DO"] = round(statistics.mean(do_hist), 2) if do_hist else 7.5
        derived["rolling_std_DO"]  = round(statistics.stdev(do_hist), 2) if len(do_hist) > 1 else 0.1

        # 10. Multi-horizon Rainfall Accumulation
        # IMPORTANT: If node provides explicit accumulated values they are used directly.
        # If only instantaneous rainfall_mm is available, horizons are estimated via
        # empirical multipliers — these are approximations, not measured totals.
        # Nodes should ideally accumulate rainfall at the hardware level.
        r_curr = curr.rainfall_mm or 0.0
        r_1h   = curr.rainfall_1h_mm  if curr.rainfall_1h_mm  is not None else r_curr
        r_24h  = curr.rainfall_24h_mm if curr.rainfall_24h_mm is not None else (r_1h * 3.5)
        derived["rain_1h"]  = r_1h
        derived["rain_3h"]  = curr.rainfall_3h_mm  if curr.rainfall_3h_mm  is not None else r_1h  * 1.8
        derived["rain_6h"]  = curr.rainfall_6h_mm  if curr.rainfall_6h_mm  is not None else r_1h  * 2.5
        derived["rain_24h"] = r_24h
        derived["rain_72h"] = curr.rainfall_72h_mm if curr.rainfall_72h_mm is not None else r_24h * 1.5

        # 11. Extreme Heat Derived Metrics
        hot_count = sum(1 for t in temps if t >= 35.0)
        derived["cumulative_hot_hours"]      = hot_count
        derived["nighttime_cooling_deficit"] = 3.5 if (curr.temperature_c or 0) > 32.0 else 0.0

        # 12. Spike and Persistence Scores
        derived["gas_spike_score"]         = max(0.0, derived["gas_rate"] * 2.0)
        derived["particulate_spike_score"] = max(0.0, derived["pm25_rate"] * 1.5)
        derived["persistence_score"]       = float(min(5, len(history)))
        derived["acidity_shift_score"]     = abs(curr.ph - 7.0) if curr.ph is not None else 0.0
        derived["degradation_spike_score"] = max(0.0, derived["turbidity_rate"] + derived["tds_rate"] * 0.1)

        return derived

    @staticmethod
    def _diff(val1: Optional[float], val2: Optional[float]) -> float:
        if val1 is not None and val2 is not None:
            return round(float(val1 - val2), 4)
        return 0.0

    def get_history(self, node_id: str, limit: int = 50) -> List[Dict[str, Any]]:
        """Returns the recent historical time-series entries for a specific node."""
        with self._lock:
            if node_id not in self._history:
                return []
            hist = list(self._history[node_id])
            return hist[-limit:]

    def clear_history(self, node_id: Optional[str] = None) -> None:
        with self._lock:
            if node_id:
                self._history.pop(node_id, None)
            else:
                self._history.clear()


# Global history engine instance
telemetry_engine = TelemetryHistoryEngine()
