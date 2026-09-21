"""
TerraEdge — Common Telemetry and Hazard Response Schemas.
Defines strongly typed Pydantic models for incoming Type A telemetry packets
and normalized multi-hazard outputs.
"""

from __future__ import annotations
import datetime
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field, field_validator


def _utc_now_iso() -> str:
    return datetime.datetime.now(datetime.timezone.utc).isoformat()


# ============================================================================
# 1. Type A Ingestion Telemetry Schema
# ============================================================================

class TypeATelemetryPayload(BaseModel):
    """
    Standardized payload format representing data from any ESP32-S3 Type A node.
    Fields are optional to accommodate nodes with differing sensor configurations.
    """
    node_id: str = Field(..., description="Unique field node identifier, e.g. 'TYPE-A-101' or 'TE-001'")
    source: str = "http"
    boot_id: Optional[str] = None
    uptime_ms: Optional[int] = Field(None, ge=0)
    sensor_diagnostics: Dict[str, Any] = Field(default_factory=dict)
    streamflow_cumec: Optional[float] = Field(None, ge=0)
    co_mg_m3: Optional[float] = Field(None, ge=0)
    no2_ug_m3: Optional[float] = Field(None, ge=0)
    water_temperature_c: Optional[float] = Field(None, ge=-5, le=100)
    solar_radiation_w_m2: Optional[float] = Field(None, ge=0)
    wind_speed_kmh: Optional[float] = Field(None, ge=0)
    node_type: str = Field("Type-A", description="Hardware classification: 'Type-A', 'Type-B', or 'Virtual'")
    timestamp: str = Field(default_factory=_utc_now_iso, description="ISO8601 UTC timestamp")
    zone: Optional[str] = Field(None, description="Geographic zone/basin/district name")
    state: Optional[str] = Field("Tamil Nadu", description="State name for regional grouping")
    district: Optional[str] = Field(None, description="District name for administrative risk aggregation")
    gateway_id: Optional[str] = Field("GW-01", description="Associated edge gateway identifier")
    is_simulated: Optional[bool] = Field(False, description="Flag indicating simulated vs physical deployment")
    sequence: Optional[int] = Field(None, description="Packet sequence number")
    firmware_version: Optional[str] = Field("1.0.0", description="Node firmware version")
    snr_db: Optional[float] = Field(None, description="LoRa signal-to-noise ratio in dB")
    
    # Coordinates & Node Health
    latitude: Optional[float] = Field(None, ge=-90.0, le=90.0, description="WGS84 Latitude")
    longitude: Optional[float] = Field(None, ge=-180.0, le=180.0, description="WGS84 Longitude")
    battery_pct: Optional[float] = Field(None, ge=0.0, le=100.0, description="Battery state of charge (0-100%)")
    rssi_dbm: Optional[float] = Field(None, description="LoRa / RF signal strength")

    # Phase 9 Autonomous Power Management & Telemetry Extensions
    power_mode: Optional[str] = Field("NORMAL", description="Autonomous power state: NORMAL, WATCH, WARNING, CRITICAL")
    battery_voltage_v: Optional[float] = Field(None, ge=0.0, le=10.0, description="Battery bus voltage in Volts")
    battery_soc_pct: Optional[float] = Field(None, ge=0.0, le=100.0, description="Battery State of Charge %")
    battery_state: Optional[str] = Field("DISCHARGING", description="Battery state: FULL, CHARGING, DISCHARGING, LOW, CRITICAL, UNKNOWN")
    battery_current_a: Optional[float] = Field(None, description="Net battery current in Amperes (+ into battery, - out)")
    battery_power_w: Optional[float] = Field(None, ge=0.0, description="Battery instantaneous power in Watts")
    charging: Optional[bool] = Field(False, description="True if charging from solar MPPT")
    solar_available: Optional[bool] = Field(False, description="True if solar irradiance available")
    solar_input_voltage_v: Optional[float] = Field(None, ge=0.0, description="Solar panel voltage in Volts")
    solar_input_power_w: Optional[float] = Field(None, ge=0.0, description="Solar panel generation in Watts")
    estimated_power_w: Optional[float] = Field(None, ge=0.0, description="Node estimated total power consumption in Watts")
    estimated_autonomy_hours: Optional[float] = Field(None, ge=0.0, description="Estimated battery autonomy in hours")
    telemetry_interval_s: Optional[int] = Field(300, ge=1, description="Reporting interval in seconds")
    gps_enabled: Optional[bool] = Field(True, description="Whether GPS fix was acquired in this cycle")
    sensor_profile: Optional[str] = Field(None, description="Active sensor duty-cycle profile")
    emergency_state: Optional[bool] = Field(False, description="True if local emergency condition is active")
    telemetry_priority: Optional[str] = Field("NORMAL", description="Transmission priority: NORMAL, ELEVATED, HIGH, EMERGENCY")

    # Environmental Core (BME680 / DHT22 / Barometer)
    temperature_c: Optional[float] = Field(None, ge=-40.0, le=85.0, description="Ambient temperature in °C")
    humidity_pct: Optional[float] = Field(None, ge=0.0, le=100.0, description="Relative humidity in %")
    pressure_hpa: Optional[float] = Field(None, ge=300.0, le=1200.0, description="Atmospheric pressure in hPa")
    gas_resistance_kohm: Optional[float] = Field(None, ge=0.0, description="BME680 MOX gas sensor resistance in kOhm")

    # Hydrological & Precipitation (Rain Gauge / Ultrasonic JSN-SR04T / Soil V2)
    rainfall_mm: Optional[float] = Field(None, ge=0.0, description="Current point rain measurement in mm")
    rainfall_1h_mm: Optional[float] = Field(None, ge=0.0, description="Accumulated rainfall past 1h in mm")
    rainfall_3h_mm: Optional[float] = Field(None, ge=0.0, description="Accumulated rainfall past 3h in mm")
    rainfall_6h_mm: Optional[float] = Field(None, ge=0.0, description="Accumulated rainfall past 6h in mm")
    rainfall_24h_mm: Optional[float] = Field(None, ge=0.0, description="Accumulated rainfall past 24h in mm")
    rainfall_72h_mm: Optional[float] = Field(None, ge=0.0, description="Accumulated rainfall past 72h in mm")
    
    water_level_m: Optional[float] = Field(None, ge=0.0, description="River stage or canal water level in meters")
    water_level_pct: Optional[float] = Field(None, ge=0.0, le=100.0, description="Water level percentage of bankfull stage")
    soil_moisture_pct: Optional[float] = Field(None, ge=0.0, le=100.0, description="Volumetric soil moisture percentage (0-100%)")
    ultrasonic_distance_cm: Optional[float] = Field(None, ge=0.0, description="JSN-SR04T ultrasonic distance measurement in cm")

    # Particulate & Air Quality (SDS011 / PMS5003 / MQ-135)
    pm25_ug_m3: Optional[float] = Field(None, ge=0.0, description="Fine particulate matter PM2.5 in µg/m³")
    pm10_ug_m3: Optional[float] = Field(None, ge=0.0, description="Coarse particulate matter PM10 in µg/m³")
    mq135_raw: Optional[float] = Field(None, ge=0.0, description="MQ-135 air quality gas ADC reading or ppm proxy")

    # Geotechnical & Fire Event (MPU6050 / SW-420 / IR Flame)
    flame: Optional[int] = Field(None, ge=0, le=1, description="Optical flame sensor state (1 = Flame Detected, 0 = Safe)")
    flame_detected: Optional[bool] = Field(None, description="Boolean flame sensor state (True = Flame Detected, False = Safe)")
    tilt_magnitude: Optional[float] = Field(None, ge=0.0, le=180.0, description="Slope inclination from vertical in degrees")
    tilt_rate: Optional[float] = Field(None, description="Rate of tilt change in degrees/min or degrees/step")
    vibration_rate: Optional[float] = Field(None, ge=0.0, description="SW-420 seismic pulse count per minute")

    # Water Quality Physicochemical Probes (pH / TDS / Turbidity / DO / EC)
    ph: Optional[float] = Field(None, ge=0.0, le=14.0, description="Water pH value")
    tds_ppm: Optional[float] = Field(None, ge=0.0, description="Total Dissolved Solids in ppm")
    turbidity: Optional[float] = Field(None, ge=0.0, description="Water turbidity in NTU")
    dissolved_oxygen: Optional[float] = Field(None, ge=0.0, description="[LEGACY] Dissolved Oxygen (DO) in mg/L")
    electrical_conductivity: Optional[float] = Field(None, ge=0.0, description="[LEGACY] Electrical Conductivity (EC) in µS/cm")

    @field_validator("timestamp", mode="before")
    @classmethod
    def validate_timestamp(cls, v: Any) -> str:
        if not v:
            return _utc_now_iso()
        return str(v)

    model_config = {
        "extra": "ignore",
        "json_schema_extra": {
            "example": {
                "node_id": "TYPE-A-101",
                "node_type": "Type-A",
                "zone": "Kaveri Basin - Zone 1",
                "latitude": 10.7905,
                "longitude": 78.7047,
                "battery_pct": 94.5,
                "temperature_c": 28.4,
                "humidity_pct": 74.0,
                "pressure_hpa": 1008.5,
                "rainfall_1h_mm": 15.0,
                "rainfall_24h_mm": 65.0,
                "water_level_m": 2.45,
                "ultrasonic_distance_cm": 245.0,
                "soil_moisture_pct": 68.0,
                "pm25_ug_m3": 35.0,
                "pm10_ug_m3": 65.0,
                "mq135_raw": 180.0,
                "flame": 0,
                "flame_detected": False,
                "tilt_magnitude": 2.4,
                "vibration_rate": 0.0
            }
        }
    }


# ============================================================================
# 2. Normalized Hazard Result Schemas
# ============================================================================

class HazardPredictionResult(BaseModel):
    """Normalized response schema for an individual hazard inference."""
    hazard: str = Field(..., description="Canonical name: Flood, Wildfire, Landslide, Air Quality, Extreme Heat, Toxic Flame, Water Quality")
    risk_pct: float = Field(..., ge=0.0, le=100.0, description="Normalized risk percentage (0.0 to 100.0)")
    confidence_pct: float = Field(..., ge=0.0, le=100.0, description="Model confidence score (0.0 to 100.0)")
    severity: str = Field(..., description="Severity category: 'NORMAL', 'WATCH', 'WARNING', 'CRITICAL'")
    anomaly_score: Optional[float] = Field(None, description="Anomaly detector score (0.0 normal -> 1.0 extreme)")
    top_features: List[str] = Field(default_factory=list, description="Dominant drivers contributing to risk prediction")
    model_status: str = Field("success", description="Execution status: 'success', 'skipped', or 'error'")
    skip_reason: Optional[str] = Field(None, description="Explanation if model was skipped (e.g. missing required sensors)")
    error: Optional[str] = Field(None, description="Error message if inference execution failed")
    timestamp: str = Field(default_factory=_utc_now_iso, description="Inference timestamp")
    details: Dict[str, Any] = Field(default_factory=dict, description="Raw hazard-specific prediction details")
    # Phase 2: input quality flag for degraded-sensor models
    input_quality: str = Field("full", description="'full' = all sensors present, 'degraded' = some sensors missing/injected")


class HazardRanking(BaseModel):
    """Summary item in the multi-hazard priority rank list."""
    hazard: str
    rank: int = Field(..., ge=1, description="1-based priority position (1 = Highest threat)")
    risk_pct: float
    confidence_pct: float
    severity: str
    priority_score: float = Field(..., description="Calculated priority score used for ranking")


# ============================================================================
# 3. Unified Gateway API Response Schema
# ============================================================================

class UnifiedGatewayResponse(BaseModel):
    """Comprehensive composite response returned by POST /api/telemetry."""
    node_id: str
    node_type: str
    zone: Optional[str] = None
    timestamp: str
    location: Dict[str, Optional[float]]
    battery_pct: Optional[float] = None

    # Phase 2: node capability profile
    node_profile: str = Field("UNKNOWN_NODE", description="Detected hardware profile (FLOOD_NODE, AIR_WILDFIRE_NODE, etc.)")
    capabilities: List[str] = Field(default_factory=list, description="Active sensor capability groups detected")

    # Phase 5: Regional & multi-node metadata
    state: Optional[str] = Field("Tamil Nadu", description="State name for regional grouping")
    district: Optional[str] = Field(None, description="District name for administrative risk aggregation")
    gateway_id: Optional[str] = Field("GW-01", description="Edge gateway identifier")
    is_simulated: bool = Field(False, description="True if generated from simulator, False if physical LoRa/hardware")
    node_status: str = Field("ONLINE", description="Health status: ONLINE, STALE, OFFLINE")

    # Aggregated Summary
    composite_risk_pct: float = Field(..., ge=0.0, le=100.0, description="Max or fused multi-hazard risk percentage")
    primary_hazard: Optional[str] = Field(None, description="Dominant top-ranked hazard")
    primary_severity: str = Field("NORMAL", description="Highest severity level across all active hazards")
    priority_score: float = Field(0.0, description="Top priority ranking score")
    
    # Ranked Lists & Full Hazard Map
    ranked_hazards: List[HazardRanking] = Field(default_factory=list, description="Active hazards sorted by urgency")
    hazard_results: Dict[str, HazardPredictionResult] = Field(default_factory=dict, description="Detailed predictions per hazard")
    
    # Alerts & Meta
    alerts_triggered: List[Dict[str, Any]] = Field(default_factory=list, description="Alert entries persisted for this telemetry frame")
    processing_time_ms: float = Field(..., description="Gateway end-to-end processing latency in ms")
    db_status: str = Field("unknown", description="Database persistence mode ('supabase' or 'in-memory')")
    # Phase 3: LoRa transport metadata (None when received over HTTP)
    transport: "Optional[LoRaTransportMetadata]" = None
    
    # Phase 4: Pass through the raw telemetry for frontend rendering
    raw_telemetry: Optional[Dict[str, Any]] = Field(None, description="Raw Type A telemetry payload received from node")

    # Phase 9: Power Management Summary
    power_mode: Optional[str] = Field("NORMAL", description="Autonomous power state: NORMAL, WATCH, WARNING, CRITICAL")
    battery_voltage_v: Optional[float] = None
    battery_soc_pct: Optional[float] = None
    battery_state: Optional[str] = None
    charging: Optional[bool] = None
    solar_available: Optional[bool] = None
    solar_input_power_w: Optional[float] = None
    estimated_power_w: Optional[float] = None
    estimated_autonomy_hours: Optional[float] = None
    telemetry_interval_s: Optional[int] = None
    telemetry_priority: Optional[str] = "NORMAL"
    power_budget: Optional[Dict[str, Any]] = None


# ============================================================================
# 4. Phase 3 — LoRa Transport Metadata
# ============================================================================

class LoRaTransportMetadata(BaseModel):
    """
    Radio transport metadata attached to telemetry received over LoRa.
    None for HTTP simulator path.  Not environmental data.
    """
    transport_type: str = "LoRa"
    rssi_dbm: float | None = None
    snr_db: float | None = None
    frequency_mhz: float = 433.0
    bandwidth_khz: int = 125
    spreading_factor: int = 7
    packet_sequence: int = 0
    retries_used: int = 0
    ack_sent: bool = False


# ============================================================================
# 5. Phase 5 — Node Registry & Detail Schemas
# ============================================================================

class NodeRegistrationRequest(BaseModel):
    """Dynamic node registration payload."""
    node_id: str = Field(..., description="Unique node ID, e.g. 'TE-001'")
    node_type: str = Field("Type-A", description="Classification: 'Type-A', 'Type-B', or 'Virtual'")
    state: str = Field("Tamil Nadu", description="State name")
    district: Optional[str] = Field(None, description="District name, e.g. 'Chennai'")
    zone: Optional[str] = Field(None, description="Local catchment/basin/zone description")
    latitude: Optional[float] = Field(None, ge=-90.0, le=90.0, description="WGS84 Latitude")
    longitude: Optional[float] = Field(None, ge=-180.0, le=180.0, description="WGS84 Longitude")
    capabilities: List[str] = Field(default_factory=list, description="Declared or detected sensor capabilities")
    firmware_version: str = Field("1.0.0", description="Firmware version string")
    is_simulated: bool = Field(False, description="Simulation indicator")
    gateway_id: Optional[str] = Field("GW-01", description="Associated gateway ID")


class NodeUpdateRequest(BaseModel):
    """Partial update payload for node attributes."""
    node_type: Optional[str] = None
    state: Optional[str] = None
    district: Optional[str] = None
    zone: Optional[str] = None
    latitude: Optional[float] = Field(None, ge=-90.0, le=90.0)
    longitude: Optional[float] = Field(None, ge=-180.0, le=180.0)
    battery_pct: Optional[float] = Field(None, ge=0.0, le=100.0)
    status: Optional[str] = None  # ONLINE, STALE, OFFLINE
    capabilities: Optional[List[str]] = None
    firmware_version: Optional[str] = None
    is_simulated: Optional[bool] = None
    gateway_id: Optional[str] = None


class NodeDetailResponse(BaseModel):
    """Comprehensive node status and health record."""
    node_id: str
    node_type: str
    state: str
    district: Optional[str] = None
    zone: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    status: str = Field("ONLINE", description="Health status: ONLINE, STALE, or OFFLINE")
    battery_pct: Optional[float] = None
    last_seen: Optional[str] = None
    capabilities: List[str] = Field(default_factory=list)
    node_profile: str = Field("UNKNOWN_NODE")
    firmware_version: str = Field("1.0.0")
    is_simulated: bool = Field(False)
    gateway_id: Optional[str] = Field("GW-01")
    rssi_dbm: Optional[float] = None
    snr_db: Optional[float] = None
    last_sequence: Optional[int] = None
    packets_received: int = 0
    packets_lost: int = 0
    latest_primary_hazard: Optional[str] = None
    latest_risk_pct: Optional[float] = None
    latest_severity: Optional[str] = None
    latest_confidence_pct: Optional[float] = None

    # Phase 9 Power extensions
    power_mode: Optional[str] = Field("NORMAL", description="Node power state: NORMAL, WATCH, WARNING, CRITICAL")
    battery_voltage_v: Optional[float] = None
    battery_soc_pct: Optional[float] = None
    battery_state: Optional[str] = None
    charging: Optional[bool] = None
    solar_available: Optional[bool] = None
    solar_input_power_w: Optional[float] = None
    telemetry_interval_s: Optional[int] = None
    estimated_autonomy_hours: Optional[float] = None
    desired_power_profile: Optional[Dict[str, Any]] = None


# ============================================================================
# 6. Phase 5 — District Risk Aggregation & GIS Schemas
# ============================================================================

class DistrictHazardSummary(BaseModel):
    """District-level aggregated risk summary for a single hazard."""
    hazard: str
    rank: int = Field(..., ge=1, description="1-based hazard priority in the district")
    risk_pct: float = Field(..., ge=0.0, le=100.0, description="Weighted district risk score")
    confidence_pct: float = Field(..., ge=0.0, le=100.0, description="Aggregated district confidence")
    severity: str = Field(..., description="NORMAL, WATCH, WARNING, CRITICAL")
    affected_nodes: int = Field(..., ge=0, description="Number of active nodes detecting threat")
    total_reporting_nodes: int = Field(..., ge=0, description="Total active nodes with model coverage")
    priority_score: float = Field(..., description="Ranking score based on risk, severity and spread")
    alert_candidate: bool = Field(False, description="Flags whether this hazard crosses district alert criteria")
    top_contributing_nodes: List[str] = Field(default_factory=list, description="Nodes driving the aggregated score")


class HotspotCluster(BaseModel):
    """Spatial risk concentration cluster."""
    hotspot_id: str
    hazard: str
    center_lat: float
    center_lon: float
    radius_km: float = Field(5.0, description="Approximate cluster radius")
    risk_pct: float = Field(..., ge=0.0, le=100.0)
    confidence_pct: float = Field(..., ge=0.0, le=100.0)
    severity: str
    affected_nodes: List[str] = Field(default_factory=list)
    timestamp: str = Field(default_factory=_utc_now_iso)


class DistrictRiskResponse(BaseModel):
    """Comprehensive district-level environmental risk intelligence response."""
    state: str
    district: str
    node_count: int = Field(0, description="Total registered nodes in district")
    active_nodes_count: int = Field(0, description="Online nodes within freshness window")
    stale_nodes_count: int = Field(0, description="Nodes with delayed telemetry")
    offline_nodes_count: int = Field(0, description="Nodes timed out")
    composite_risk_pct: float = Field(0.0, ge=0.0, le=100.0, description="District peak composite risk")
    primary_hazard: Optional[str] = Field(None, description="Leading threat in district")
    primary_severity: str = Field("NORMAL", description="Synthesized district severity")
    hazards: List[DistrictHazardSummary] = Field(default_factory=list, description="Ranked district hazards")
    hotspots: List[HotspotCluster] = Field(default_factory=list, description="Detected local risk hotspots")
    nodes: List[Dict[str, Any]] = Field(default_factory=list, description="Individual node statuses in this district")
    timestamp: str = Field(default_factory=_utc_now_iso)


class RiskMapResponse(BaseModel):
    """Comprehensive multi-node GIS payload for map visualization."""
    state: Optional[str] = None
    district: Optional[str] = None
    total_nodes: int
    active_nodes: int
    stale_nodes: int
    offline_nodes: int
    districts: List[DistrictRiskResponse] = Field(default_factory=list)
    nodes: List[Dict[str, Any]] = Field(default_factory=list)
    hotspots: List[HotspotCluster] = Field(default_factory=list)
    timestamp: str = Field(default_factory=_utc_now_iso)


# ============================================================================
# 7. Phase 9 — Power Profile & Autonomous Management Schemas
# ============================================================================

class PowerProfileUpdateRequest(BaseModel):
    """Payload for configuring or overriding field node power profile via Gateway API."""
    mode: Optional[str] = Field(None, description="Force specific power mode: NORMAL, WATCH, WARNING, CRITICAL, or AUTO")
    telemetry_interval_s: Optional[int] = Field(None, ge=5, le=3600, description="Telemetry interval in seconds")
    gps_interval_s: Optional[int] = Field(None, ge=10, le=86400, description="GPS fix acquisition interval in seconds")
    sensor_profile: Optional[str] = Field(None, description="Sensor duty-cycle profile preset name")
    emergency_wakeup_enabled: Optional[bool] = Field(None, description="Enable/disable local emergency wake-up")
    sampling_profile: Optional[List[str]] = Field(None, description="Explicit list of enabled sensor IDs")


class NodePowerDetailResponse(BaseModel):
    """Detailed power telemetry and autonomy status for a field node."""
    node_id: str
    power_state: str
    battery_soc_pct: Optional[float] = None
    battery_voltage_v: Optional[float] = None
    battery_state: str = "DISCHARGING"
    battery_current_a: Optional[float] = None
    battery_power_w: Optional[float] = None
    charging: bool = False
    solar_available: bool = False
    solar_input_voltage_v: Optional[float] = None
    solar_input_power_w: Optional[float] = None
    telemetry_interval_s: int = 300
    gps_interval_s: int = 3600
    estimated_average_current_ma: Optional[float] = None
    estimated_power_w: Optional[float] = None
    estimated_autonomy_hours: Optional[float] = None
    estimated_autonomy_days: Optional[float] = None
    estimated_daily_energy_use_wh: Optional[float] = None
    estimated_daily_solar_input_wh: Optional[float] = None
    desired_power_profile: Optional[Dict[str, Any]] = None
    measurement_status: str = "SIMULATED / ESTIMATED"
    last_updated: str = Field(default_factory=_utc_now_iso)


UnifiedGatewayResponse.model_rebuild()
