"""
TerraEdge — Gateway Feature Builders.
Adapts the unified Type A telemetry representation to the exact feature schemas
required by each of the 7 existing machine learning hazard models.

Phase 2: All adapters updated for final hardware canonical field names.
Cross-sensor substitutions and injected fallbacks are explicitly documented.

KEY SUBSTITUTIONS (final hardware vs trained features):
  Wildfire: raw_ethanol <- mq135_raw  [CROSS-SENSOR: MQ-2 removed, MQ-135 substituted]
  Wildfire: tvoc       <- BME680 gas_resistance proxy  [NOT calibrated TVOC]
  Industrial: smoke_or_proxy_response <- mq135_raw * 0.85  [CROSS-SENSOR: MQ-2 removed]
  Extreme Heat: solar_radiation  <- INJECTED ESTIMATE (no pyranometer in final hardware)
  Extreme Heat: wind_speed_kmh   <- INJECTED DEFAULT 5.0 km/h (no anemometer)
  Water Quality: EC  <- TDS * 1.56 ESTIMATED (no EC probe in final hardware)
  Water Quality: DO  <- 7.5 INJECTED DEFAULT (no DO probe in final hardware)
"""

from __future__ import annotations
from typing import Any, Dict, List, Optional, Tuple
import pandas as pd

from .telemetry import ProcessedTelemetry


class FeatureBuildResult:
    """Encapsulates the output of a hazard feature adapter."""

    def __init__(self, ready: bool, features: Any = None, missing: Optional[List[str]] = None, reason: Optional[str] = None):
        self.ready = ready
        self.features = features
        self.missing = missing or []
        self.reason = reason
        # Phase 2: input_quality flag — 'full' when all sensors present, 'degraded' when
        # one or more features are injected (e.g., solar_radiation, wind_speed, DO).
        self.input_quality: str = "full"


    def to_dict(self) -> Dict[str, Any]:
        return {
            "ready": self.ready,
            "missing": self.missing,
            "reason": self.reason
        }


# ============================================================================
# 1. Flood Feature Adapter (Expects Dict)
# ============================================================================

def build_flood_features(proc: ProcessedTelemetry) -> FeatureBuildResult:
    """
    Builds feature dictionary for FloodInferenceEngine (11 features).

    FINAL SENSORS: Rain gauge, water level sensor, JSN-SR04T (ultrasonic), capacitive soil v2.0, BME680.

    Water level resolution order:
      1. water_level_m (direct from water level sensor)
      2. Derived from ultrasonic_distance_cm via telemetry engine (reference_height=300cm)
      3. Default fallback 0.5m

    Rainfall accumulation: Direct if node provides rainfall_24h_mm, else estimated
    from rainfall_mm via gateway history (multi-horizon accumulation is approximate).
    """
    # water_level_m may be direct or already derived from ultrasonic by telemetry engine
    water_level = proc.get("water_level_m")
    soil = proc.get("soil_moisture_pct")
    rain_1h = proc.get("rain_1h", 0.0)
    rain_24h = proc.get("rain_24h", 0.0)

    if water_level is None and rain_24h == 0.0 and rain_1h == 0.0 and soil is None:
        return FeatureBuildResult(
            ready=False,
            missing=["water_level_m", "rainfall_24h_mm", "soil_moisture_pct"],
            reason="No hydrological sensors active (missing water level, rain gauge, and soil moisture)"
        )

    wl_actual   = water_level if water_level is not None else 0.5
    soil_actual = soil if soil is not None else 45.0
    temp_c      = proc.get("temperature_c", 27.5)
    hum         = proc.get("humidity_pct", 70.0)
    # streamflow derived via empirical rating curve f(water_level)
    streamflow  = max(1.0, wl_actual * 12.0)

    features = {
        "rain_1h":          float(rain_1h),
        "rain_3h":          float(proc.get("rain_3h", rain_1h * 1.8)),
        "rain_6h":          float(proc.get("rain_6h", rain_1h * 2.5)),
        "rain_24h":         float(rain_24h),
        "rain_72h":         float(proc.get("rain_72h", rain_24h * 1.5)),
        "water_level_m":    float(wl_actual),
        "streamflow_cumec": float(streamflow),
        "soil_moisture_pct": float(soil_actual),
        "temperature_c":    float(temp_c),
        "humidity_pct":     float(hum),
        "anomaly_score":    0.20
    }

    return FeatureBuildResult(ready=True, features=features)


# ============================================================================
# 2. Forest Wildfire Feature Adapter (Expects Dict)
# ============================================================================

def build_wildfire_features(proc: ProcessedTelemetry) -> FeatureBuildResult:
    """
    Builds feature dictionary for FireInferenceEngine (12 compact features).

    FINAL SENSORS: BME680, SDS011, MQ-135, IR flame sensor.

    CROSS-SENSOR SUBSTITUTIONS (documented):
      - raw_ethanol: Model was trained on MQ-2 ADC. MQ-2 is removed from final hardware.
        Substituting mq135_raw ADC as fallback.
        LIMITATION: MQ-135 has different gas sensitivity curve than MQ-2.
        RETRAINING RECOMMENDED in Phase 3 for this feature.

      - tvoc: BME680 gas_resistance_kohm is NOT a TVOC meter.
        Using inverse-resistance proxy: tvoc ≈ 5000 / gas_resistance_kohm.
        This is a relative gas-quality trend indicator, not a calibrated VOC reading.
        LIMITATION: Non-linear, temperature-dependent. Treat as approximate.
    """
    temp = proc.get("temperature_c")
    hum  = proc.get("humidity_pct")
    # Support both flame_detected (bool) and flame (int)
    flame = proc.get("flame_detected") or proc.get("flame")
    # MQ-135 or BME680 gas resistance (no MQ-2 or MQ-7 in final hardware)
    gas   = proc.get("gas_resistance_kohm") or proc.get("mq135_raw")
    # SDS011 PM2.5 (canonical name)
    pm25  = proc.get("pm25_ug_m3")

    if temp is None and hum is None and flame is None and gas is None and pm25 is None:
        return FeatureBuildResult(
            ready=False,
            missing=["temperature_c", "humidity_pct", "flame_detected", "pm25_ug_m3"],
            reason="No fire/thermal or combustion sensors detected (need BME680 or SDS011 or IR flame)"
        )

    temp_val  = float(temp  if temp  is not None else 35.0)
    hum_val   = float(hum   if hum   is not None else 50.0)
    press_val = float(proc.get("pressure_hpa", 1008.0))
    pm25_val  = float(pm25  if pm25  is not None else 30.0)

    # TVOC proxy from BME680 gas resistance (lower resistance = higher VOC load)
    # [PROXY — NOT CALIBRATED TVOC — See docstring above]
    if proc.get("gas_resistance_kohm") is not None:
        tvoc_val = float(max(50.0, 5000.0 / max(0.5, proc.get("gas_resistance_kohm"))))
    elif proc.get("mq135_raw") is not None:
        tvoc_val = float(proc.get("mq135_raw") * 5.0)
    else:
        tvoc_val = 800.0

    # raw_ethanol substitute: MQ-135 raw ADC used instead of MQ-2
    # [CROSS-SENSOR SUBSTITUTE: MQ-135 for MQ-2 — RETRAINING RECOMMENDED]
    mq135_adc = proc.get("mq135_raw")
    raw_eth = float(mq135_adc if mq135_adc is not None else 3034.45)

    features = {
        "temperature":        temp_val,
        "humidity":           hum_val,
        "pressure":           press_val,
        "pm25":               pm25_val,
        "tvoc":               tvoc_val,
        "raw_ethanol":        raw_eth,
        "temperature_rate":   float(proc.get("temperature_rate",  0.0)),
        "humidity_rate":      float(proc.get("humidity_rate",     0.0)),
        "pm25_rate":          float(proc.get("pm25_rate",         0.0)),
        "tvoc_rate":          float(proc.get("tvoc_rate",         0.0)),
        "temperature_delta_5": float(proc.get("temperature_delta_5", 0.0)),
        "humidity_delta_5":   float(proc.get("humidity_delta_5",  0.0)),
    }

    return FeatureBuildResult(ready=True, features=features)


# ============================================================================
# 3. Landslide Precursor Feature Adapter (Expects Dict)
# ============================================================================

def build_landslide_features(proc: ProcessedTelemetry) -> FeatureBuildResult:
    """
    Builds feature dictionary for LandslideInferenceEngine (8 geotechnical features).
    Requires slope tilt (MPU6050), vibration (SW-420), soil moisture, or heavy rain.
    """
    tilt = proc.get("tilt_magnitude")
    vib = proc.get("vibration_rate")
    soil = proc.get("soil_moisture_pct")
    rain = proc.get("rainfall_24h_mm") or proc.get("rainfall_mm")

    if tilt is None and vib is None and soil is None:
        return FeatureBuildResult(
            ready=False,
            missing=["tilt_magnitude", "soil_moisture_pct", "vibration_rate"],
            reason="No geotechnical sensors detected (missing MPU6050 inclinometer and soil moisture probe)"
        )

    # Convert soil % (0-100) to Volumetric Water Content (VWC: 0.05 to 0.50)
    if soil is not None:
        vwc = 0.05 + (soil / 100.0) * 0.45
    else:
        vwc = 0.2426  # Dataset mean

    soil_rate = proc.get("soil_moisture_rate", 0.0)
    vwc_rate = (soil_rate / 100.0) * 0.45

    tilt_val = float(tilt if tilt is not None else 2.6066)
    tilt_rate = float(proc.get("tilt_rate", 0.0))
    vib_rate = float(vib if vib is not None else 0.0)
    temp_val = float(proc.get("temperature_c", 22.5))
    hum_val = float(proc.get("humidity_pct", 64.35))
    r24 = float(rain if rain is not None else proc.get("rain_24h", 3.25))

    features = {
        "soil_moisture_vwc": float(vwc),
        "soil_moisture_rate": float(vwc_rate),
        "tilt_magnitude": float(tilt_val),
        "tilt_rate": float(tilt_rate),
        "vibration_rate": float(vib_rate),
        "temperature": float(temp_val),
        "humidity": float(hum_val),
        "rainfall_24h": float(r24),
    }

    return FeatureBuildResult(ready=True, features=features)


# ============================================================================
# 4. Air Pollution Feature Adapter (Expects Dict)
# ============================================================================

def build_air_pollution_features(proc: ProcessedTelemetry) -> FeatureBuildResult:
    """
    Builds feature dictionary for AirPollutionInferenceEngine (12 edge features).

    FINAL SENSORS: SDS011 (pm25_ug_m3, pm10_ug_m3), MQ-135 (mq135_raw as gas_proxy), BME680.

    gas_proxy = mq135_raw / 10.0
      MQ-135 is a broad-spectrum gas sensor. The /10 normalization converts its ADC
      to a dimensionless gas-trend index. This is semantically valid for trend detection.
      It is NOT a calibrated concentration of any specific pollutant.

    SDS011 replaces PMS5003: Same PM2.5/PM10 measurement unit (ug/m3). Compatible.
    """
    # Use canonical names from final hardware schema
    pm25  = proc.get("pm25_ug_m3")
    pm10  = proc.get("pm10_ug_m3")
    mq135 = proc.get("mq135_raw") or proc.get("gas_resistance_kohm")

    if pm25 is None and pm10 is None and mq135 is None:
        return FeatureBuildResult(
            ready=False,
            missing=["pm25_ug_m3", "pm10_ug_m3", "mq135_raw"],
            reason="No particulate or air quality sensors detected (missing SDS011 or MQ-135)"
        )

    pm25_val = float(pm25 if pm25 is not None else 45.0)
    pm10_val = float(pm10 if pm10 is not None else (pm25_val * 1.8))

    # gas_proxy from MQ-135 (preferred) or BME680 gas_resistance (fallback)
    if proc.get("mq135_raw") is not None:
        gas_proxy = float(proc.get("mq135_raw") / 10.0)
    elif proc.get("gas_resistance_kohm") is not None:
        gas_proxy = float(max(5.0, 100.0 / max(1.0, proc.get("gas_resistance_kohm"))))
    else:
        gas_proxy = 25.0

    temp_val  = float(proc.get("temperature_c", 28.0))
    hum_val   = float(proc.get("humidity_pct", 60.0))
    press_val = float(proc.get("pressure_hpa", 1010.0))

    pm25_delta = float(proc.get("pm25_delta_30", 0.0))
    if pm25_delta == 0.0 and pm25_val > 150.0:
        pm25_delta = min(60.0, pm25_val * 0.25)
    pm25_slope = float(proc.get("pm25_slope_30", pm25_delta / 30.0))

    features = {
        "pm25":             pm25_val,
        "pm10":             pm10_val,
        "gas_proxy":        gas_proxy,
        "temperature":      temp_val,
        "relative_humidity": hum_val,
        "pressure":         press_val,
        "pm25_lag_15":      float(proc.get("pm25_lag_15", max(10.0, pm25_val - pm25_delta * 0.5))),
        "pm25_lag_30":      float(proc.get("pm25_lag_30", max(10.0, pm25_val - pm25_delta))),
        "pm25_delta_30":    pm25_delta,
        "pm25_slope_30":    pm25_slope,
        "hour_sin":         float(proc.get("hour_sin", 0.0)),
        "hour_cos":         float(proc.get("hour_cos", 1.0)),
    }

    return FeatureBuildResult(ready=True, features=features)


# ============================================================================
# 5. Extreme Heat Feature Adapter (Expects 1-Row DataFrame)
# ============================================================================

def build_heat_features(proc: ProcessedTelemetry) -> FeatureBuildResult:
    """
    Builds single-row DataFrame for HeatRiskPredictor (14 features).

    FINAL SENSORS: BME680 (temperature, humidity, pressure), rain gauge.

    INJECTED FALLBACKS (no sensor in final hardware):
      - solar_radiation: ESTIMATED from temperature (no pyranometer).
        Rule: temp > 30C → 600 W/m2, else 250 W/m2. Inaccurate for cloudy conditions.
        RETRAINING RECOMMENDED in Phase 3 to remove solar_radiation dependency.

      - wind_speed_kmh: ASSUMED 5.0 km/h (no anemometer in final hardware).
        Calm wind assumption increases heat index estimates.
        RETRAINING RECOMMENDED in Phase 3 to remove wind_speed dependency.

      - solar_radiation_rate: INJECTED 0.0 (cannot derive without pyranometer).

    These injections reduce model confidence. input_quality = 'degraded'.
    """
    temp = proc.get("temperature_c")
    hum  = proc.get("humidity_pct")

    if temp is None:
        return FeatureBuildResult(
            ready=False,
            missing=["temperature_c"],
            reason="Missing BME680 ambient temperature sensor"
        )

    temp_val  = float(temp)
    hum_val   = float(hum if hum is not None else 50.0)
    rain_val  = float(proc.get("rainfall_mm", 0.0))

    # INJECTED — no pyranometer in final hardware
    solar_val = float(600.0 if temp_val > 30.0 else 250.0)

    # INJECTED — no anemometer in final hardware
    wind_val  = 5.0

    row = {
        "temperature_c":            temp_val,
        "humidity":                  hum_val,
        "solar_radiation":           solar_val,  # INJECTED — no pyranometer
        "rainfall_mm":               rain_val,
        "wind_speed_kmh":            wind_val,   # INJECTED — no anemometer
        "temperature_rate":          float(proc.get("temperature_rate", 0.0)),
        "humidity_rate":             float(proc.get("humidity_rate", 0.0)),
        "solar_radiation_rate":      0.0,        # INJECTED — cannot derive
        "rolling_mean_temperature":  float(proc.get("rolling_mean_temperature", temp_val)),
        "rolling_mean_humidity":     float(proc.get("rolling_mean_humidity",    hum_val)),
        "rolling_std_temperature":   float(proc.get("rolling_std_temperature",  0.5)),
        "rolling_std_humidity":      float(proc.get("rolling_std_humidity",     1.0)),
        "cumulative_hot_hours":      int(proc.get("cumulative_hot_hours", 4 if temp_val >= 38.0 else 0)),
        "nighttime_cooling_deficit": float(proc.get("nighttime_cooling_deficit", 3.0 if temp_val >= 36.0 else 0.0)),
    }

    df = pd.DataFrame([row])
    # input_quality flag signals degraded confidence to caller
    result = FeatureBuildResult(ready=True, features=df)
    result.input_quality = "degraded"  # solar_radiation and wind_speed_kmh are injected
    return result


# ============================================================================
# 6. Industrial Emissions Feature Adapter (Expects 1-Row DataFrame)
# ============================================================================

def build_industrial_features(proc: ProcessedTelemetry) -> FeatureBuildResult:
    """
    Builds single-row DataFrame for IndustrialEmissionsPredictor (17 features).

    FINAL SENSORS: MQ-135 (gas_response), SDS011 (PM2.5, PM10), BME680.

    CROSS-SENSOR SUBSTITUTION (documented):
      - smoke_or_proxy_response: Model was trained on MQ-2 ADC readings.
        MQ-2 is removed from final hardware.
        Substituting: mq135_raw * 0.85 as smoke proxy.
        LIMITATION: MQ-2 and MQ-135 have different sensitivity profiles.
        The 0.85 scaling is an approximation to maintain feature magnitude.
        RETRAINING RECOMMENDED in Phase 3 on MQ-135-only data.
    """
    mq135   = proc.get("mq135_raw")
    gas_res = proc.get("gas_resistance_kohm")
    pm25    = proc.get("pm25_ug_m3")   # canonical SDS011 field

    if mq135 is None and gas_res is None and pm25 is None:
        return FeatureBuildResult(
            ready=False,
            missing=["mq135_raw", "gas_resistance_kohm", "pm25_ug_m3"],
            reason="No industrial gas or particulate sensors detected (need MQ-135 or SDS011)"
        )

    # MQ-135 as primary gas_response (wideband MOS sensor)
    if mq135 is not None:
        gas_resp = float(mq135)
    elif gas_res is not None:
        gas_resp = float(max(10.0, 5000.0 / max(0.5, gas_res)))
    else:
        gas_resp = 120.0

    # smoke_or_proxy_response: MQ-135 * 0.85 substituting for MQ-2
    # [CROSS-SENSOR SUBSTITUTE: MQ-135 for MQ-2 — RETRAINING RECOMMENDED]
    smoke_resp = float(gas_resp * 0.85)

    pm25_val  = float(pm25 if pm25 is not None else 35.0)
    pm10_val  = float(proc.get("pm10_ug_m3") or (pm25_val * 1.6))
    temp_val  = float(proc.get("temperature_c", 28.0))
    hum_val   = float(proc.get("humidity_pct", 55.0))
    press_val = float(proc.get("pressure_hpa", 1010.0))

    gas_rate = float(proc.get("gas_rate", 0.0))
    if gas_rate == 0.0 and gas_resp > 400.0:
        gas_rate = 20.0

    pm_rate = float(proc.get("pm25_rate", 0.0))
    if pm_rate == 0.0 and pm25_val > 80.0:
        pm_rate = 15.0

    gas_spike = float(proc.get("gas_spike_score", 0.0))
    if gas_spike == 0.0 and gas_resp > 400.0:
        gas_spike = 1.2

    pm_spike = float(proc.get("particulate_spike_score", 0.0))
    if pm_spike == 0.0 and pm25_val > 80.0:
        pm_spike = 1.1

    persistence = float(proc.get("persistence_score", 1.0))
    if persistence <= 1.0 and gas_resp > 400.0:
        persistence = 5.0

    row = {
        "gas_response":           gas_resp,
        "smoke_or_proxy_response": smoke_resp,  # [CROSS-SENSOR: MQ-135×0.85 for MQ-2]
        "PM2.5":                  pm25_val,
        "PM10":                   pm10_val,
        "temperature_c":          temp_val,
        "humidity":               hum_val,
        "pressure":               press_val,
        "gas_rate":               gas_rate,
        "PM2.5_rate":             pm_rate,
        "PM10_rate":              float(proc.get("pm10_rate", pm_rate * 1.4)),
        "rolling_mean_gas":       float(proc.get("rolling_mean_gas",  gas_resp)),
        "rolling_mean_PM2.5":     float(proc.get("rolling_mean_pm25", pm25_val)),
        "rolling_std_gas":        float(proc.get("rolling_std_gas",   5.0 if gas_resp > 400.0 else 2.0)),
        "rolling_std_PM2.5":      float(proc.get("rolling_std_pm25",  5.0 if pm25_val > 80.0 else 1.5)),
        "gas_spike_score":        gas_spike,
        "particulate_spike_score": pm_spike,
        "persistence_score":      persistence,
    }

    df = pd.DataFrame([row])
    return FeatureBuildResult(ready=True, features=df)


# ============================================================================
# 7. Water Quality Feature Adapter (Expects 1-Row DataFrame)
# ============================================================================

def build_water_quality_features(proc: ProcessedTelemetry) -> FeatureBuildResult:
    """
    Builds single-row DataFrame for WaterQualityPredictor (26 physicochemical features).

    FINAL SENSORS: pH probe, TDS sensor, Turbidity sensor, BME680 (temperature).

    SENSORS NOT IN FINAL HARDWARE (documented):
      - dissolved_oxygen (DO): No DO probe in final hardware.
        INJECTED: 7.5 mg/L (standard normoxic default).
        LIMITATION: oxygen_drop_score is unreliable without real DO.
        Confidence penalty applied when DO is absent.
        Adding a DO probe is recommended for full water quality accuracy.

      - electrical_conductivity (EC): No EC probe in final hardware.
        DERIVED: EC = TDS * 1.56 uS/cm (published linear approximation).
        Valid approximation for most natural water bodies.
        Confidence is minimally affected.

    input_quality = 'degraded' when DO is absent.
    """
    ph   = proc.get("ph")
    tds  = proc.get("tds_ppm")   # canonical name
    turb = proc.get("turbidity")
    do   = proc.get("dissolved_oxygen")  # LEGACY field, may be None in field deployments

    # Require at least pH, TDS, or turbidity from final hardware sensors
    if ph is None and tds is None and turb is None:
        return FeatureBuildResult(
            ready=False,
            missing=["ph", "tds_ppm", "turbidity"],
            reason="No water quality sensors detected (need pH, TDS sensor, or turbidity sensor)"
        )

    ph_val   = float(ph   if ph   is not None else 7.2)
    turb_val = float(turb if turb is not None else 2.5)
    tds_val  = float(tds  if tds  is not None else 180.0)
    temp_val = float(proc.get("temperature_c", 24.0))

    # EC derived from TDS (no EC probe in final hardware)
    ec_val = float(proc.get("electrical_conductivity") or (tds_val * 1.56))

    # DO injected default when no DO probe present
    do_absent = (do is None)
    do_val = float(do if do is not None else 7.5)  # INJECTED — no DO probe

    row = {
        "pH":               ph_val,
        "turbidity":        turb_val,
        "EC":               ec_val,        # DERIVED from TDS
        "TDS":              tds_val,
        "dissolved_oxygen": do_val,         # INJECTED if no DO probe
        "temperature_c":    temp_val,
        "pH_rate":          float(proc.get("ph_rate",        0.0)),
        "turbidity_rate":   float(proc.get("turbidity_rate", 0.0)),
        "EC_rate":          0.0,            # Cannot derive without EC sensor
        "TDS_rate":         float(proc.get("tds_rate",       0.0)),
        "DO_rate":          0.0,            # Cannot derive without DO sensor
        "rolling_mean_pH":         float(proc.get("rolling_mean_pH",        ph_val)),
        "rolling_mean_turbidity":  float(proc.get("rolling_mean_turbidity", turb_val)),
        "rolling_mean_EC":         float(proc.get("rolling_mean_EC",        ec_val)),
        "rolling_mean_TDS":        float(proc.get("rolling_mean_TDS",       tds_val)),
        "rolling_mean_DO":         float(proc.get("rolling_mean_DO",        7.5)),
        "rolling_std_pH":          float(proc.get("rolling_std_pH",         0.05)),
        "rolling_std_turbidity":   float(proc.get("rolling_std_turbidity",  0.2)),
        "rolling_std_EC":          float(proc.get("rolling_std_EC",         5.0)),
        "rolling_std_TDS":         float(proc.get("rolling_std_TDS",        5.0)),
        "rolling_std_DO":          float(proc.get("rolling_std_DO",         0.1)),
        "acidity_shift_score":     float(proc.get("acidity_shift_score",    abs(ph_val - 7.0))),
        "degradation_spike_score": float(proc.get("degradation_spike_score", 0.0)),
        "conductivity_shift_score": float(max(0.0, (ec_val - 500.0) / 100.0)),
        # oxygen_drop_score is unreliable when DO is injected (7.5 = no drop detected)
        "oxygen_drop_score":       float(max(0.0, 6.0 - do_val)),
        "persistence_score":       float(proc.get("persistence_score", 1.0)),
    }

    df = pd.DataFrame([row])
    result = FeatureBuildResult(ready=True, features=df)
    if do_absent:
        result.input_quality = "degraded"  # oxygen_drop_score unreliable without DO probe
    return result
