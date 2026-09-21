"""Conservative physical-sensor adapters, separate from legacy demo adapters.

Missing instruments never turn into training means or cross-sensor proxies.
Confidence returned by existing models is a heuristic input-health score, not
empirically calibrated accuracy; expose that provenance to the dashboard.
"""
from collections import deque
from datetime import datetime, timezone
import math
import statistics
import threading
import pandas as pd
from .schemas import HazardPredictionResult

HAZARDS = ("Flood", "Wildfire", "Landslide", "Air Quality", "Extreme Heat", "Toxic Flame", "Water Quality")


class LiveModels:
    def __init__(self):
        self.history = {}
        self.lock = threading.RLock()

    def evaluate(self, raw, router):
        with self.lock:
            return self._evaluate(raw, router)

    def _evaluate(self, raw, router):
        current = raw.model_dump()
        now = datetime.fromisoformat(raw.timestamp.replace("Z", "+00:00")).timestamp()
        # Physical history is independent of demo traffic and is reset on node reboot.
        key = (raw.node_id, raw.boot_id)
        if key not in self.history:
            for old in list(self.history):
                if old[0] == raw.node_id:
                    del self.history[old]
            if len(self.history) >= 256:
                self.history.pop(next(iter(self.history)))
            self.history[key] = {"recent": deque(maxlen=12), "quarter": deque(maxlen=40), "hour": deque(maxlen=72)}
        history = self.history[key]
        current["_time"] = now
        recent = list(history["recent"])
        history["recent"].append(current)
        # Minute checkpoints preserve real 15/30-minute lags at 5-second reporting.
        for period, seconds in (("quarter", 60),):
            bucket = history[period]
            if not bucket or now - bucket[-1]["_time"] >= seconds:
                bucket.append(current)
        self.accumulate_hour(current, history)
        results = {}
        for hazard in HAZARDS:
            try:
                features, method = self.build(hazard, current, recent, history)
                engine = router.engines.get(hazard)
                if engine is None:
                    raise RuntimeError(router.engine_errors.get(hazard, "Model unavailable"))
                result = getattr(engine, method)(features)
                if result.get("error"):
                    raise RuntimeError(result["error"])
                risk = result.get("risk_score_pct")
                if risk is None:
                    prob = next((result[k] for k in ("risk_probability", "fire_probability", "heat_risk_probability", "leak_risk_probability", "water_quality_risk_probability") if k in result), None)
                    if prob is None:
                        raise RuntimeError("Model omitted risk probability")
                    risk = prob * 100
                confidence = result.get("confidence_pct")
                if confidence is None:
                    confidence = result.get("confidence", 0) * (1 if hazard == "Air Quality" else 100)
                results[hazard] = HazardPredictionResult(
                    hazard=hazard, risk_pct=risk, confidence_pct=confidence,
                    severity=result["severity"].upper(), model_status="success",
                    top_features=result.get("top_features", []),
                    details={**result, "confidence_basis": "Legacy model input-health heuristic; not calibrated accuracy",
                             "input_provenance": "Measured sensors and training-matched feature formulas",
                             "field_validation": "Required: training datasets include proxies and synthetic context"})
            except ValueError as error:
                results[hazard] = HazardPredictionResult(hazard=hazard, risk_pct=0, confidence_pct=0,
                    severity="UNKNOWN", model_status="skipped", skip_reason=str(error))
            except Exception as error:
                results[hazard] = HazardPredictionResult(hazard=hazard, risk_pct=0, confidence_pct=0,
                    severity="UNKNOWN", model_status="error", error=str(error))
        return results

    @staticmethod
    def require(row, fields):
        missing = [k for k in fields if row.get(k) is None]
        if missing:
            raise ValueError("Missing calibrated sensors/measurements: " + ", ".join(missing))

    @staticmethod
    def lag(current, history, seconds):
        candidates = [r for r in history if seconds <= current["_time"] - r["_time"] <= seconds + 60]
        if not candidates:
            raise ValueError(f"Waiting for continuous {seconds // 60}-minute sensor history (60 s tolerance)")
        return candidates[-1]

    def build(self, hazard, row, recent, history):
        if hazard == "Flood":
            fields = ["water_level_m", "streamflow_cumec", "soil_moisture_pct", "temperature_c", "humidity_pct"]
            rain = {f"rain_{h}h": f"rainfall_{h}h_mm" for h in (1, 3, 6, 24, 72)}
            self.require(row, fields + list(rain.values()))
            return {**{f: row[f] for f in fields}, **{k: row[v] for k, v in rain.items()}}, "predict_flood"
        if hazard == "Wildfire":
            raise ValueError("Trained model requires measured TVOC and raw_ethanol from its original sensor domain; BME680 kΩ and MQ-135 ADC cannot substitute. Add matched sensors or retrain with labelled hardware data. Direct flame alerts remain active.")
        if hazard == "Toxic Flame":
            raise ValueError("Training mixes MQ-135, MQ-2 and UCI response domains. MQ135 × 0.85 is not a smoke measurement. Validate response scaling and retrain on the installed sensors before ML deployment.")
        if hazard == "Landslide":
            self.require(row, ["soil_moisture_pct", "tilt_magnitude", "vibration_rate", "temperature_c", "humidity_pct", "rainfall_24h_mm"])
            prev = self.lag(row, history["quarter"], 900)
            self.require(prev, ["soil_moisture_pct", "tilt_magnitude"])
            return {"soil_moisture_vwc": row["soil_moisture_pct"] / 100,
                    "soil_moisture_rate": (row["soil_moisture_pct"] - prev["soil_moisture_pct"]) / 100,
                    "tilt_magnitude": row["tilt_magnitude"], "tilt_rate": row["tilt_magnitude"] - prev["tilt_magnitude"],
                    "vibration_rate": row["vibration_rate"], "temperature": row["temperature_c"],
                    "humidity": row["humidity_pct"], "rainfall_24h": row["rainfall_24h_mm"]}, "predict_landslide"
        if hazard == "Air Quality":
            fields = {"pm25": "pm25_ug_m3", "pm10": "pm10_ug_m3", "temperature": "temperature_c", "relative_humidity": "humidity_pct", "pressure": "pressure_hpa"}
            self.require(row, list(fields.values()) + ["co_mg_m3", "no2_ug_m3"])
            lag15 = self.lag(row, history["quarter"], 900)
            lag30 = self.lag(row, history["quarter"], 1800)
            self.require(lag15, ["pm25_ug_m3"])
            self.require(lag30, ["pm25_ug_m3"])
            delta = row["pm25_ug_m3"] - lag30["pm25_ug_m3"]
            # India station training timestamps use local hour, not UTC receive hour.
            hour = datetime.fromtimestamp(row["_time"] + 19800, tz=timezone.utc).hour
            return {**{k: row[v] for k, v in fields.items()},
                    "gas_proxy": min(200, max(1, row["co_mg_m3"] * 20 + row["no2_ug_m3"] * .5)),
                    "pm25_lag_15": lag15["pm25_ug_m3"], "pm25_lag_30": lag30["pm25_ug_m3"],
                    "pm25_delta_30": delta, "pm25_slope_30": delta / 30,
                    "hour_sin": math.sin(2*math.pi*hour/24), "hour_cos": math.cos(2*math.pi*hour/24)}, "predict_air_pollution"
        if hazard == "Extreme Heat":
            self.require(row, ["temperature_c", "humidity_pct", "solar_radiation_w_m2", "wind_speed_kmh", "rainfall_1h_mm"])
            hours = list(history["hour"])
            if len(hours) < 72 or any(not h["_complete"] for h in hours) or any(
                    b["_slot"] - a["_slot"] != 1 for a, b in zip(hours, hours[1:])):
                raise ValueError("Waiting for 72 complete hourly windows with measured solar/wind/rain; gaps over 30 seconds invalidate an hour")
            curr, prev = hours[-1], hours[-2]
            window = hours[-24:]
            day = curr["_slot"] // 24
            nights = [h for h in hours if h["_slot"] // 24 == day and
                      (h["_slot"] % 24 >= 22 or h["_slot"] % 24 <= 6)]
            if not nights:
                raise ValueError("Waiting for observed nighttime temperature")
            f = {"temperature_c": curr["temperature_c"], "humidity": curr["humidity_pct"],
                 "solar_radiation": curr["solar_radiation_w_m2"], "wind_speed_kmh": curr["wind_speed_kmh"],
                 "rainfall_mm": curr["rainfall_1h_mm"],
                 "temperature_rate": curr["temperature_c"] - prev["temperature_c"],
                 "humidity_rate": curr["humidity_pct"] - prev["humidity_pct"],
                 "solar_radiation_rate": curr["solar_radiation_w_m2"] - prev["solar_radiation_w_m2"],
                 "cumulative_hot_hours": sum(h["temperature_c"] > 35 for h in hours),
                 "nighttime_cooling_deficit": max(0, min(h["temperature_c"] for h in nights) - 28)}
            for name, source in (("temperature", "temperature_c"), ("humidity", "humidity_pct")):
                values = [h[source] for h in window]
                f["rolling_mean_" + name] = statistics.mean(values)
                f["rolling_std_" + name] = statistics.stdev(values)
            return pd.DataFrame([f]), "predict_heat_risk"
        if hazard == "Water Quality":
            mapping = {"pH": "ph", "turbidity": "turbidity", "EC": "electrical_conductivity", "TDS": "tds_ppm", "dissolved_oxygen": "dissolved_oxygen", "temperature_c": "water_temperature_c"}
            self.require(row, list(mapping.values()))
            window = (recent + [row])[-12:]
            # Training uses 12 sample windows. Missing probe samples break the window.
            for sample in window:
                self.require(sample, list(mapping.values()))
            f = {k: row[v] for k, v in mapping.items()}
            prev = window[-2] if len(window) > 1 else row
            for target, source in (("pH", "ph"), ("turbidity", "turbidity"), ("EC", "electrical_conductivity"), ("TDS", "tds_ppm"), ("DO", "dissolved_oxygen")):
                values = [s[source] for s in window]
                f[target + "_rate"] = row[source] - prev[source]
                f["rolling_mean_" + target] = statistics.mean(values)
                f["rolling_std_" + target] = statistics.stdev(values) if len(values) > 1 else 0
            f.update(acidity_shift_score=abs(row["ph"] - 7),
                     degradation_spike_score=min(15, row["turbidity"] / (f["rolling_mean_turbidity"] + 1e-5)),
                     conductivity_shift_score=min(15, row["electrical_conductivity"] / (f["rolling_mean_EC"] + 1e-5)),
                     oxygen_drop_score=max(0, 8 - row["dissolved_oxygen"]),
                     persistence_score=sum(s["ph"] < 6.5 or s["ph"] > 8.5 or s["turbidity"] > 10 or s["tds_ppm"] > 500 for s in window))
            return pd.DataFrame([f]), "predict_water_quality_risk"
        raise ValueError("Unknown hazard")

    @staticmethod
    def accumulate_hour(row, history):
        """Bounded hourly means; partial or interrupted hours cannot train a prediction."""
        fields = ("temperature_c", "humidity_pct", "solar_radiation_w_m2", "wind_speed_kmh", "rainfall_1h_mm")
        now = row["_time"]
        slot = int((now + 19800) // 3600)  # source data local hours, India
        pending = history.get("pending_hour")
        if pending is None or pending["_slot"] != slot:
            if pending:
                end = (pending["_slot"] + 1) * 3600 - 19800
                complete = pending["valid"] and end - pending["last"] <= 30 and slot == pending["_slot"] + 1
                hourly = {k: pending["sums"][k] / pending["count"] for k in fields}
                # Rainfall_1h is already a trailing total, not a 5-second increment.
                hourly["rainfall_1h_mm"] = pending["rain"]
                hourly.update(_slot=pending["_slot"], _complete=complete)
                history["hour"].append(hourly)
            pending = {"_slot": slot, "last": now, "valid": now - (slot*3600 - 19800) <= 30,
                       "count": 0, "sums": {k: 0 for k in fields}, "rain": 0}
            history["pending_hour"] = pending
        pending["valid"] &= now - pending["last"] <= 30 and all(row.get(k) is not None for k in fields)
        pending["last"] = now
        pending["count"] += 1
        for field in fields:
            pending["sums"][field] += row.get(field) or 0
        pending["rain"] = row.get("rainfall_1h_mm") or 0


live_models = LiveModels()
