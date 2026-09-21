"""
TerraEdge -- Sensor Capability Profiles.
Defines canonical node hardware profiles for the final TerraEdge sensor suite.

FINAL HARDWARE (Phase 2):
  BME680, SDS011, MQ-135, Rain gauge, Water level sensor, JSN-SR04T,
  Capacitive soil moisture v2.0, MPU6050, SW420, IR flame, pH, TDS, Turbidity,
  NEO-6M GPS, SX1278 LoRa 433 MHz

REMOVED -- LEGACY -- NOT IN FINAL HARDWARE:
  MQ-2, MQ-7, DHT22, DHT11, PMS5003, BME280, GP2Y1010
"""

from __future__ import annotations
from typing import Any, Dict, List

CAPABILITY_ENVIRONMENTAL   = "environmental"
CAPABILITY_PARTICULATE     = "particulate"
CAPABILITY_GAS             = "gas"
CAPABILITY_FLAME           = "flame"
CAPABILITY_HYDROLOGICAL    = "hydrological"
CAPABILITY_WATER_LEVEL     = "water_level"
CAPABILITY_ULTRASONIC      = "ultrasonic"
CAPABILITY_SOIL_MOISTURE   = "soil_moisture"
CAPABILITY_GEOTECHNICAL    = "geotechnical"
CAPABILITY_WATER_CHEMISTRY = "water_chemistry"
CAPABILITY_GPS             = "gps"

NODE_PROFILES = {
    "FLOOD_NODE": {
        "description": "Flood and Hydrology monitoring node",
        "required_capabilities": ["hydrological","water_level","soil_moisture","environmental"],
        "optional_capabilities": ["ultrasonic","gps"],
        "supported_hazards": ["Flood","Landslide"],
    },
    "LANDSLIDE_NODE": {
        "description": "Slope stability and landslide precursor node",
        "required_capabilities": ["geotechnical","soil_moisture","environmental"],
        "optional_capabilities": ["hydrological","gps"],
        "supported_hazards": ["Landslide","Flood"],
    },
    "AIR_WILDFIRE_NODE": {
        "description": "Air quality and wildfire detection node",
        "required_capabilities": ["environmental","particulate","gas","flame"],
        "optional_capabilities": ["gps"],
        "supported_hazards": ["Air Quality","Wildfire","Toxic Flame","Extreme Heat"],
    },
    "WATER_NODE": {
        "description": "Water quality monitoring node",
        "required_capabilities": ["water_chemistry","environmental"],
        "optional_capabilities": ["gps"],
        "supported_hazards": ["Water Quality"],
    },
    "UNIVERSAL_NODE": {
        "description": "Full-stack prototype node with all final hardware sensors",
        "required_capabilities": [
            "environmental","particulate","gas","flame",
            "hydrological","water_level","ultrasonic",
            "soil_moisture","geotechnical","water_chemistry"
        ],
        "optional_capabilities": ["gps"],
        "supported_hazards": [
            "Flood","Wildfire","Landslide","Air Quality",
            "Extreme Heat","Toxic Flame","Water Quality"
        ],
    },
}


def detect_capabilities(telemetry: Any) -> List[str]:
    """Detects active sensor capabilities from non-null telemetry fields."""
    caps = []
    if (getattr(telemetry,"temperature_c",None) is not None
            or getattr(telemetry,"humidity_pct",None) is not None
            or getattr(telemetry,"pressure_hpa",None) is not None):
        caps.append(CAPABILITY_ENVIRONMENTAL)
    if (getattr(telemetry,"pm25_ug_m3",None) is not None
            or getattr(telemetry,"pm10_ug_m3",None) is not None):
        caps.append(CAPABILITY_PARTICULATE)
    if (getattr(telemetry,"mq7_raw",None) is not None
            or getattr(telemetry,"mq135_raw",None) is not None
            or getattr(telemetry,"gas_resistance_kohm",None) is not None):
        caps.append(CAPABILITY_GAS)
    if (getattr(telemetry,"flame_detected",None) is not None
            or getattr(telemetry,"flame",None) is not None):
        caps.append(CAPABILITY_FLAME)
    if (getattr(telemetry,"rainfall_mm",None) is not None
            or getattr(telemetry,"rainfall_24h_mm",None) is not None):
        caps.append(CAPABILITY_HYDROLOGICAL)
    if getattr(telemetry,"water_level_m",None) is not None:
        caps.append(CAPABILITY_WATER_LEVEL)
    if getattr(telemetry,"ultrasonic_distance_cm",None) is not None:
        caps.append(CAPABILITY_ULTRASONIC)
    if getattr(telemetry,"soil_moisture_pct",None) is not None:
        caps.append(CAPABILITY_SOIL_MOISTURE)
    if (getattr(telemetry,"tilt_magnitude",None) is not None
            or getattr(telemetry,"vibration_rate",None) is not None):
        caps.append(CAPABILITY_GEOTECHNICAL)
    if (getattr(telemetry,"ph",None) is not None
            or getattr(telemetry,"tds_ppm",None) is not None
            or getattr(telemetry,"turbidity",None) is not None):
        caps.append(CAPABILITY_WATER_CHEMISTRY)
    if (getattr(telemetry,"latitude",None) is not None
            and getattr(telemetry,"longitude",None) is not None):
        caps.append(CAPABILITY_GPS)
    return caps


def detect_node_profile(capabilities: List[str]) -> str:
    """Matches detected capabilities to the best-fit named node profile."""
    cap_set = set(capabilities)
    if (CAPABILITY_ENVIRONMENTAL in cap_set and CAPABILITY_PARTICULATE in cap_set
            and CAPABILITY_GAS in cap_set and CAPABILITY_GEOTECHNICAL in cap_set
            and CAPABILITY_WATER_CHEMISTRY in cap_set):
        return "UNIVERSAL_NODE"
    if (CAPABILITY_PARTICULATE in cap_set and CAPABILITY_GAS in cap_set
            and CAPABILITY_FLAME in cap_set):
        return "AIR_WILDFIRE_NODE"
    if CAPABILITY_WATER_CHEMISTRY in cap_set and CAPABILITY_GEOTECHNICAL not in cap_set:
        return "WATER_NODE"
    if (CAPABILITY_GEOTECHNICAL in cap_set and CAPABILITY_SOIL_MOISTURE in cap_set
            and CAPABILITY_PARTICULATE not in cap_set):
        return "LANDSLIDE_NODE"
    if (CAPABILITY_HYDROLOGICAL in cap_set or CAPABILITY_WATER_LEVEL in cap_set
            or CAPABILITY_ULTRASONIC in cap_set):
        return "FLOOD_NODE"
    return "UNKNOWN_NODE"


def get_profile_metadata(profile_name: str) -> Dict[str, Any]:
    """Returns the full profile metadata dict for a given profile name."""
    return NODE_PROFILES.get(profile_name, {
        "description": "Unknown or unclassified node",
        "required_capabilities": [],
        "optional_capabilities": [],
        "supported_hazards": [],
    })
