"""
TerraEdge — Gateway Node Manager (Phase 5).
Tracks multi-node registry, health lifecycle (ONLINE / STALE / OFFLINE),
battery status, radio link metadata, sensor capabilities, and district assignment.
Integrates with the Supabase 'nodes' table.
"""

from __future__ import annotations
import datetime
import os
import sys
import threading
from typing import Any, Dict, List, Optional, Tuple

# Ensure project root / common can be imported
HERE = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(HERE)
COMMON_DIR = os.path.join(PROJECT_ROOT, "common")
if COMMON_DIR not in sys.path:
    sys.path.append(COMMON_DIR)

try:
    import terra_supabase as db
except ImportError:
    db = None

from .schemas import (
    LoRaTransportMetadata,
    NodeRegistrationRequest,
    NodeUpdateRequest,
    TypeATelemetryPayload,
)
from .sensor_profiles import detect_capabilities, detect_node_profile
from .power import (
    DEFAULT_POWER_CONFIG,
    NodePowerStateMachine,
    PowerBudgetEngine,
    PowerState,
    check_emergency_conditions,
    classify_battery_state,
    estimate_soc_from_voltage,
    estimate_voltage_from_soc,
)


def _utc_now_iso() -> str:
    return datetime.datetime.now(datetime.timezone.utc).isoformat()


# Spatial bounding box / zone lookup dictionary for automated district resolution
KNOWN_ZONE_DISTRICT_MAP: Dict[str, Tuple[str, str]] = {
    "adyar catchment corridor": ("Chennai", "Tamil Nadu"),
    "srm edge fire node": ("Chennai", "Tamil Nadu"),
    "srm forest fire station": ("Chennai", "Tamil Nadu"),
    "kaveri basin - zone 1": ("Tiruchirappalli", "Tamil Nadu"),
    "kaveri river floodplain": ("Tiruchirappalli", "Tamil Nadu"),
    "tamraparani basin - zone 2": ("Tirunelveli", "Tamil Nadu"),
    "nilgiris mountain pass": ("Nilgiris", "Tamil Nadu"),
    "nilgiris slope station": ("Nilgiris", "Tamil Nadu"),
    "sathyamangalam forest reserve": ("Erode", "Tamil Nadu"),
    "western ghats scrub reserve": ("Pune", "Maharashtra"),
    "pune cwprs micro-met": ("Pune", "Maharashtra"),
    "pune cwprs micro-met station": ("Pune", "Maharashtra"),
    "delhi ito urban belt": ("New Delhi", "Delhi"),
    "delhi ito urban station": ("New Delhi", "Delhi"),
    "vizag industrial belt": ("Visakhapatnam", "Andhra Pradesh"),
    "visakhapatnam petrochemical zone": ("Visakhapatnam", "Andhra Pradesh"),
    "godavari basin outfall": ("Visakhapatnam", "Andhra Pradesh"),
    "godavari river industrial outfall": ("Visakhapatnam", "Andhra Pradesh"),
}


def infer_district_and_state(
    zone: Optional[str] = None,
    lat: Optional[float] = None,
    lon: Optional[float] = None,
    default_state: str = "Tamil Nadu",
    default_district: str = "Chennai"
) -> Tuple[str, str]:
    """Resolves (district, state) from explicit zone or geographical coordinates."""
    if zone:
        z_norm = zone.strip().lower()
        for pattern, (d, s) in KNOWN_ZONE_DISTRICT_MAP.items():
            if pattern in z_norm or z_norm in pattern:
                return d, s

    if lat is not None and lon is not None:
        # Chennai region (~12.8 - 13.3 N, 80.0 - 80.35 E)
        if 12.7 <= lat <= 13.4 and 79.9 <= lon <= 80.4:
            return "Chennai", "Tamil Nadu"
        # Tiruchirappalli / Kaveri (~10.6 - 11.0 N, 78.5 - 79.0 E)
        if 10.5 <= lat <= 11.1 and 78.4 <= lon <= 79.2:
            return "Tiruchirappalli", "Tamil Nadu"
        # Nilgiris (~11.2 - 11.7 N, 76.4 - 77.0 E)
        if 11.1 <= lat <= 11.8 and 76.3 <= lon <= 77.1:
            return "Nilgiris", "Tamil Nadu"
        # Erode / Sathyamangalam (~11.3 - 11.8 N, 77.0 - 77.6 E)
        if 11.2 <= lat <= 11.9 and 77.0 <= lon <= 77.8:
            return "Erode", "Tamil Nadu"
        # Tirunelveli / Tamraparani (~8.5 - 9.0 N, 77.5 - 78.0 E)
        if 8.3 <= lat <= 9.2 and 77.3 <= lon <= 78.2:
            return "Tirunelveli", "Tamil Nadu"
        # Pune (~18.3 - 18.7 N, 73.6 - 74.0 E)
        if 18.2 <= lat <= 18.8 and 73.5 <= lon <= 74.2:
            return "Pune", "Maharashtra"
        # Delhi (~28.4 - 28.9 N, 77.0 - 77.5 E)
        if 28.3 <= lat <= 29.0 and 76.8 <= lon <= 77.5:
            return "New Delhi", "Delhi"
        # Visakhapatnam (~17.5 - 17.9 N, 83.1 - 83.5 E)
        if 17.4 <= lat <= 18.0 and 83.0 <= lon <= 83.6:
            return "Visakhapatnam", "Andhra Pradesh"

    return default_district, default_state


class NodeManager:
    """
    Manages the in-memory registry, health lifecycle, and Supabase synchronization
    of all field sensor nodes in the multi-node network.
    """

    def __init__(
        self,
        stale_threshold_seconds: int = 120,
        offline_threshold_seconds: int = 300
    ):
        self.stale_threshold_seconds = stale_threshold_seconds
        self.offline_threshold_seconds = offline_threshold_seconds
        self._lock = threading.Lock()
        self._nodes: Dict[str, Dict[str, Any]] = {}
        self._power_state_machines: Dict[str, NodePowerStateMachine] = {}
        self._desired_power_profiles: Dict[str, Dict[str, Any]] = {}
        self._power_budget_engine = PowerBudgetEngine()

        # Pre-seed known baseline nodes
        self._seed_baseline_nodes()

    def _seed_baseline_nodes(self) -> None:
        initial_nodes = [
            {
                "node_id": "TE-001",
                "node_type": "Type-A",
                "state": "Tamil Nadu",
                "district": "Chennai",
                "zone": "Adyar Catchment Corridor",
                "latitude": 13.0325,
                "longitude": 80.1808,
                "battery_pct": 98.0,
                "status": "ONLINE",
                "last_seen": _utc_now_iso(),
                "capabilities": ["bme680", "sds011", "mq135", "flame", "rainfall", "water_level", "ultrasonic", "soil_moisture"],
                "node_profile": "MULTI_HAZARD_FULL",
                "firmware_version": "1.2.0",
                "is_simulated": False,
                "gateway_id": "GW-01",
                "rssi_dbm": -82.0,
                "snr_db": 8.5,
                "last_sequence": 1,
                "packets_received": 1,
                "packets_lost": 0,
            },
            {
                "node_id": "TYPE-A-101",
                "node_type": "Type-A",
                "state": "Tamil Nadu",
                "district": "Tiruchirappalli",
                "zone": "Kaveri Basin - Zone 1",
                "latitude": 10.7905,
                "longitude": 78.7047,
                "battery_pct": 92.0,
                "status": "ONLINE",
                "last_seen": "2026-09-03T17:15:00Z",
                "capabilities": ["bme680", "rainfall", "water_level", "ultrasonic", "soil_moisture"],
                "node_profile": "FLOOD_HYDROLOGICAL",
                "firmware_version": "1.0.0",
                "is_simulated": True,
                "gateway_id": "GW-01",
                "rssi_dbm": -88.0,
                "snr_db": 7.0,
                "last_sequence": 0,
                "packets_received": 0,
                "packets_lost": 0,
            },
            {
                "node_id": "TYPE-B-201",
                "node_type": "Type-B",
                "state": "Tamil Nadu",
                "district": "Tiruchirappalli",
                "zone": "Kaveri Basin - Zone 1",
                "latitude": 10.8201,
                "longitude": 78.6912,
                "battery_pct": 100.0,
                "status": "ONLINE",
                "last_seen": "2026-09-03T17:15:00Z",
                "capabilities": [],
                "node_profile": "GATEWAY_CORE",
                "firmware_version": "2.0.0",
                "is_simulated": False,
                "gateway_id": "GW-01",
                "rssi_dbm": -72.0,
                "snr_db": 11.0,
                "last_sequence": 0,
                "packets_received": 0,
                "packets_lost": 0,
            },
            {
                "node_id": "TYPE-A-102",
                "node_type": "Type-A",
                "state": "Tamil Nadu",
                "district": "Tirunelveli",
                "zone": "Tamraparani Basin - Zone 2",
                "latitude": 8.7139,
                "longitude": 77.7567,
                "battery_pct": 90.0,
                "status": "ONLINE",
                "last_seen": "2026-09-03T17:15:00Z",
                "capabilities": ["bme680", "rainfall", "water_level", "soil_moisture"],
                "node_profile": "FLOOD_HYDROLOGICAL",
                "firmware_version": "1.0.0",
                "is_simulated": True,
                "gateway_id": "GW-01",
                "rssi_dbm": -90.0,
                "snr_db": 6.0,
                "last_sequence": 0,
                "packets_received": 0,
                "packets_lost": 0,
            },
            {
                "node_id": "FWF-01",
                "node_type": "Type-A",
                "state": "Maharashtra",
                "district": "Pune",
                "zone": "Western Ghats Scrub Reserve",
                "latitude": 18.5204,
                "longitude": 73.8567,
                "battery_pct": 85.0,
                "status": "ONLINE",
                "last_seen": "2026-09-03T17:15:00Z",
                "capabilities": ["bme680", "mq135", "flame"],
                "node_profile": "WILDFIRE_THERMAL",
                "firmware_version": "1.0.0",
                "is_simulated": True,
                "gateway_id": "GW-01",
                "rssi_dbm": -85.0,
                "snr_db": 8.0,
                "last_sequence": 0,
                "packets_received": 0,
                "packets_lost": 0,
            },
            {
                "node_id": "LS-01",
                "node_type": "Type-A",
                "state": "Tamil Nadu",
                "district": "Nilgiris",
                "zone": "Nilgiris Slope Station",
                "latitude": 11.4102,
                "longitude": 76.6950,
                "battery_pct": 88.0,
                "status": "ONLINE",
                "last_seen": "2026-09-03T17:15:00Z",
                "capabilities": ["bme680", "mpu6050", "sw420", "rainfall", "soil_moisture"],
                "node_profile": "LANDSLIDE_GEOTECHNICAL",
                "firmware_version": "1.0.0",
                "is_simulated": True,
                "gateway_id": "GW-01",
                "rssi_dbm": -86.0,
                "snr_db": 8.0,
                "last_sequence": 0,
                "packets_received": 0,
                "packets_lost": 0,
            },
            {
                "node_id": "AIR-01",
                "node_type": "Type-A",
                "state": "Delhi",
                "district": "New Delhi",
                "zone": "Delhi ITO Urban Belt",
                "latitude": 28.6289,
                "longitude": 77.2408,
                "battery_pct": 94.0,
                "status": "ONLINE",
                "last_seen": "2026-09-03T17:15:00Z",
                "capabilities": ["bme680", "sds011", "mq135"],
                "node_profile": "AIR_QUALITY_STATION",
                "firmware_version": "1.0.0",
                "is_simulated": True,
                "gateway_id": "GW-01",
                "rssi_dbm": -79.0,
                "snr_db": 9.5,
                "last_sequence": 0,
                "packets_received": 0,
                "packets_lost": 0,
            },
            {
                "node_id": "HT-01",
                "node_type": "Type-A",
                "state": "Maharashtra",
                "district": "Pune",
                "zone": "Pune CWPRS Micro-met",
                "latitude": 18.4350,
                "longitude": 73.7915,
                "battery_pct": 91.0,
                "status": "ONLINE",
                "last_seen": "2026-09-03T17:15:00Z",
                "capabilities": ["bme680"],
                "node_profile": "METEOROLOGICAL_CORE",
                "firmware_version": "1.0.0",
                "is_simulated": True,
                "gateway_id": "GW-01",
                "rssi_dbm": -81.0,
                "snr_db": 9.0,
                "last_sequence": 0,
                "packets_received": 0,
                "packets_lost": 0,
            },
            {
                "node_id": "IND-01",
                "node_type": "Type-A",
                "state": "Andhra Pradesh",
                "district": "Visakhapatnam",
                "zone": "Vizag Industrial Belt",
                "latitude": 17.6868,
                "longitude": 83.2185,
                "battery_pct": 89.0,
                "status": "ONLINE",
                "last_seen": "2026-09-03T17:15:00Z",
                "capabilities": ["bme680", "sds011", "mq135"],
                "node_profile": "AIR_QUALITY_STATION",
                "firmware_version": "1.0.0",
                "is_simulated": True,
                "gateway_id": "GW-01",
                "rssi_dbm": -84.0,
                "snr_db": 8.5,
                "last_sequence": 0,
                "packets_received": 0,
                "packets_lost": 0,
            },
            {
                "node_id": "WTR-01",
                "node_type": "Type-A",
                "state": "Andhra Pradesh",
                "district": "Visakhapatnam",
                "zone": "Godavari Basin Outfall",
                "latitude": 17.7285,
                "longitude": 83.3015,
                "battery_pct": 86.0,
                "status": "ONLINE",
                "last_seen": "2026-09-03T17:15:00Z",
                "capabilities": ["ph", "tds", "turbidity", "temperature"],
                "node_profile": "WATER_QUALITY_STATION",
                "firmware_version": "1.0.0",
                "is_simulated": True,
                "gateway_id": "GW-01",
                "rssi_dbm": -89.0,
                "snr_db": 7.5,
                "last_sequence": 0,
                "packets_received": 0,
                "packets_lost": 0,
            },
        ]
        with self._lock:
            for n in initial_nodes:
                self._nodes[n["node_id"]] = n

    def register_or_update(
        self,
        telemetry: TypeATelemetryPayload,
        transport_meta: Optional[LoRaTransportMetadata] = None
    ) -> Dict[str, Any]:
        """
        Dynamically registers or updates internal node state on telemetry packet arrival.
        Calculates packet loss, updates radio health, and syncs to Supabase.
        """
        now_iso = telemetry.timestamp or _utc_now_iso()
        capabilities = detect_capabilities(telemetry)

        # Infer state & district if missing
        district, state = telemetry.district, telemetry.state
        if not district or not state:
            inferred_dist, inferred_state = infer_district_and_state(
                zone=telemetry.zone,
                lat=telemetry.latitude,
                lon=telemetry.longitude
            )
            district = district or inferred_dist
            state = state or inferred_state

        with self._lock:
            existing = self._nodes.get(telemetry.node_id, {})
            
            # Packet loss tracking
            last_seq = existing.get("last_sequence")
            current_seq = telemetry.sequence or (transport_meta.packet_sequence if transport_meta else None)
            packets_lost = existing.get("packets_lost", 0)
            if last_seq is not None and current_seq is not None and current_seq > (last_seq + 1):
                packets_lost += (current_seq - last_seq - 1)

            packets_received = existing.get("packets_received", 0) + 1

            # Radio metadata resolution
            rssi = telemetry.rssi_dbm
            if rssi is None and transport_meta is not None:
                rssi = transport_meta.rssi_dbm
            if rssi is None:
                rssi = existing.get("rssi_dbm")

            snr = telemetry.snr_db
            if snr is None and transport_meta is not None:
                snr = transport_meta.snr_db
            if snr is None:
                snr = existing.get("snr_db")

            # Determine simulation status
            # If received over LoRa transport or explicitly flagged as live, is_simulated=False
            is_sim = telemetry.is_simulated if telemetry.is_simulated is not None else existing.get("is_simulated", False)
            if transport_meta is not None:
                is_sim = False

            merged_caps = list(set(capabilities + existing.get("capabilities", [])))
            profile = detect_node_profile(merged_caps)

            # Phase 9: Battery and Power State Management
            soc = telemetry.battery_soc_pct if telemetry.battery_soc_pct is not None else (telemetry.battery_pct if telemetry.battery_pct is not None else existing.get("battery_pct"))
            v_bat = telemetry.battery_voltage_v if telemetry.battery_voltage_v is not None else existing.get("battery_voltage_v")
            if v_bat is None and soc is not None:
                v_bat = round(estimate_voltage_from_soc(soc), 2)
            elif soc is None and v_bat is not None:
                soc = round(estimate_soc_from_voltage(v_bat), 1)

            is_emerg, emerg_reasons = check_emergency_conditions(telemetry)
            
            # State machine tracking
            sm = self.get_or_create_power_sm(telemetry.node_id)
            if is_emerg:
                sm.update(risk_pct=100.0, severity="CRITICAL", emergency_trigger=True)
            elif telemetry.power_mode:
                try:
                    sm.current_state = PowerState(telemetry.power_mode.upper())
                except Exception:
                    pass

            telemetry_interval = telemetry.telemetry_interval_s or sm.get_telemetry_interval()
            budget = self._power_budget_engine.calculate_budget(
                telemetry_interval_s=telemetry_interval,
                battery_soc_pct=soc if soc is not None else 85.0,
                battery_voltage_v=v_bat,
                active_sensor_ids=merged_caps,
                solar_peak_power_w=telemetry.solar_input_power_w
            )

            node_record = {
                "node_id": telemetry.node_id,
                "node_type": telemetry.node_type or existing.get("node_type", "Type-A"),
                "state": state or existing.get("state", "Tamil Nadu"),
                "district": district or existing.get("district", "Chennai"),
                "zone": telemetry.zone or existing.get("zone", "Field Station"),
                "latitude": telemetry.latitude if telemetry.latitude is not None else existing.get("latitude"),
                "longitude": telemetry.longitude if telemetry.longitude is not None else existing.get("longitude"),
                "battery_pct": soc,
                "status": "ONLINE",
                "last_seen": now_iso,
                "capabilities": merged_caps,
                "node_profile": profile,
                "firmware_version": telemetry.firmware_version or existing.get("firmware_version", "1.0.0"),
                "is_simulated": is_sim,
                "gateway_id": telemetry.gateway_id or existing.get("gateway_id", "GW-01"),
                "rssi_dbm": rssi,
                "snr_db": snr,
                "last_sequence": current_seq if current_seq is not None else existing.get("last_sequence"),
                "packets_received": packets_received,
                "packets_lost": packets_lost,
                # Phase 9 Power Telemetry
                "power_mode": sm.current_state.value,
                "battery_voltage_v": v_bat,
                "battery_soc_pct": soc,
                "battery_state": telemetry.battery_state or classify_battery_state(soc if soc is not None else 85.0, bool(telemetry.charging)),
                "charging": bool(telemetry.charging),
                "solar_available": bool(telemetry.solar_available or (telemetry.solar_input_power_w and telemetry.solar_input_power_w > 0)),
                "solar_input_power_w": telemetry.solar_input_power_w,
                "telemetry_interval_s": telemetry_interval,
                "estimated_power_w": telemetry.estimated_power_w or budget.estimated_power_w,
                "estimated_autonomy_hours": telemetry.estimated_autonomy_hours or budget.estimated_autonomy_hours,
                "desired_power_profile": self._desired_power_profiles.get(telemetry.node_id),
                # Preserve cached prediction summaries
                "latest_primary_hazard": existing.get("latest_primary_hazard"),
                "latest_risk_pct": existing.get("latest_risk_pct"),
                "latest_severity": existing.get("latest_severity"),
                "latest_confidence_pct": existing.get("latest_confidence_pct"),
            }
            self._nodes[telemetry.node_id] = node_record

        # Synchronize with Supabase if connected
        if db is not None:
            try:
                db_node = {
                    "node_id": node_record["node_id"],
                    "hazard": "all",
                    "type": node_record["node_type"],
                    "state": node_record["state"],
                    "district": node_record["district"],
                    "zone": node_record["zone"],
                    "lat": node_record["latitude"],
                    "lon": node_record["longitude"],
                    "status": node_record["status"],
                    "last_ping": node_record["last_seen"],
                    "battery": node_record["battery_pct"],
                    "capabilities": node_record["capabilities"],
                    "firmware_version": node_record["firmware_version"],
                    "is_simulated": node_record["is_simulated"],
                    "gateway_id": node_record["gateway_id"],
                }
                db.seed_nodes("all", [db_node])
            except Exception as exc:
                print(f"[node-manager] Supabase node sync warning: {exc}", flush=True)

        return node_record

    def register_node(self, req: NodeRegistrationRequest | Dict[str, Any]) -> Dict[str, Any]:
        """Explicitly registers a new node into inventory via API."""
        if hasattr(req, "model_dump"):
            data = req.model_dump()
        else:
            data = dict(req)

        node_id = data["node_id"]
        district, state = data.get("district"), data.get("state")
        if not district or not state:
            inf_dist, inf_state = infer_district_and_state(
                zone=data.get("zone"),
                lat=data.get("latitude"),
                lon=data.get("longitude")
            )
            district = district or inf_dist
            state = state or inf_state

        caps = data.get("capabilities", [])
        profile = detect_node_profile(caps)

        with self._lock:
            record = {
                "node_id": node_id,
                "node_type": data.get("node_type", "Type-A"),
                "state": state,
                "district": district,
                "zone": data.get("zone", "Field Station"),
                "latitude": data.get("latitude"),
                "longitude": data.get("longitude"),
                "battery_pct": 100.0,
                "status": "ONLINE",
                "last_seen": _utc_now_iso(),
                "capabilities": caps,
                "node_profile": profile,
                "firmware_version": data.get("firmware_version", "1.0.0"),
                "is_simulated": bool(data.get("is_simulated", False)),
                "gateway_id": data.get("gateway_id", "GW-01"),
                "rssi_dbm": None,
                "snr_db": None,
                "last_sequence": None,
                "packets_received": 0,
                "packets_lost": 0,
                "latest_primary_hazard": None,
                "latest_risk_pct": None,
                "latest_severity": None,
                "latest_confidence_pct": None,
            }
            self._nodes[node_id] = record

        # Sync to DB
        if db is not None:
            try:
                db.seed_nodes("all", [{
                    "node_id": record["node_id"],
                    "hazard": "all",
                    "type": record["node_type"],
                    "state": record["state"],
                    "district": record["district"],
                    "zone": record["zone"],
                    "lat": record["latitude"],
                    "lon": record["longitude"],
                    "status": record["status"],
                    "last_ping": record["last_seen"],
                    "battery": record["battery_pct"],
                    "capabilities": record["capabilities"],
                    "firmware_version": record["firmware_version"],
                    "is_simulated": record["is_simulated"],
                    "gateway_id": record["gateway_id"],
                }])
            except Exception as exc:
                print(f"[node-manager] Supabase node registration warning: {exc}", flush=True)

        return self._apply_online_status(dict(record))

    def update_node(self, node_id: str, updates: NodeUpdateRequest | Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Applies partial updates to an existing node record."""
        if hasattr(updates, "model_dump"):
            up_dict = {k: v for k, v in updates.model_dump().items() if v is not None}
        else:
            up_dict = {k: v for k, v in updates.items() if v is not None}

        with self._lock:
            if node_id not in self._nodes:
                return None
            
            node = self._nodes[node_id]
            for k, v in up_dict.items():
                node[k] = v
            
            if "capabilities" in up_dict:
                node["node_profile"] = detect_node_profile(node["capabilities"])

            self._nodes[node_id] = node
            return self._apply_online_status(dict(node))

    def update_node_latest_predictions(
        self,
        node_id: str,
        primary_hazard: Optional[str],
        risk_pct: float,
        severity: str,
        confidence_pct: float
    ) -> None:
        """Caches the latest multi-hazard risk assessment on the node record and transitions power state."""
        with self._lock:
            if node_id in self._nodes:
                self._nodes[node_id]["latest_primary_hazard"] = primary_hazard
                self._nodes[node_id]["latest_risk_pct"] = round(risk_pct, 1)
                self._nodes[node_id]["latest_severity"] = severity
                self._nodes[node_id]["latest_confidence_pct"] = round(confidence_pct, 1)

                # Phase 9: Autonomous power state machine update
                sm = self.get_or_create_power_sm(node_id)
                new_state, changed, reason = sm.update(risk_pct=risk_pct, severity=severity)
                self._nodes[node_id]["power_mode"] = new_state.value
                self._nodes[node_id]["telemetry_interval_s"] = sm.get_telemetry_interval()

    def get_or_create_power_sm(self, node_id: str) -> NodePowerStateMachine:
        """Retrieves or creates an in-memory power state machine for the given node."""
        if node_id not in self._power_state_machines:
            self._power_state_machines[node_id] = NodePowerStateMachine(node_id=node_id)
        return self._power_state_machines[node_id]

    def set_desired_power_profile(self, node_id: str, profile_req: Any) -> Dict[str, Any]:
        """Sets or overrides power profile for a field node."""
        with self._lock:
            node = self._nodes.get(node_id)
            if not node:
                raise KeyError(f"Node {node_id} not found")
            req_dict = profile_req.model_dump(exclude_unset=True) if hasattr(profile_req, "model_dump") else dict(profile_req)
            self._desired_power_profiles[node_id] = req_dict
            node["desired_power_profile"] = req_dict

            if req_dict.get("mode") and req_dict["mode"].upper() != "AUTO":
                try:
                    target_mode = PowerState(req_dict["mode"].upper())
                    sm = self.get_or_create_power_sm(node_id)
                    sm.current_state = target_mode
                    node["power_mode"] = target_mode.value
                    if req_dict.get("telemetry_interval_s"):
                        node["telemetry_interval_s"] = req_dict["telemetry_interval_s"]
                    else:
                        node["telemetry_interval_s"] = sm.get_telemetry_interval()
                except Exception:
                    pass
            return req_dict

    def get_power_details(self, node_id: str) -> Optional[Dict[str, Any]]:
        """Returns detailed power status, battery telemetry, and autonomy estimates."""
        with self._lock:
            node = self._nodes.get(node_id)
            if not node:
                return None
            node_copy = self._apply_online_status(dict(node))
            sm = self.get_or_create_power_sm(node_id)
            soc = node_copy.get("battery_soc_pct") or node_copy.get("battery_pct") or 85.0
            v_bat = node_copy.get("battery_voltage_v") or estimate_voltage_from_soc(soc)
            caps = node_copy.get("capabilities", [])
            interval = node_copy.get("telemetry_interval_s") or sm.get_telemetry_interval()
            budget = self._power_budget_engine.calculate_budget(
                telemetry_interval_s=interval,
                battery_soc_pct=soc,
                battery_voltage_v=v_bat,
                active_sensor_ids=caps,
                solar_peak_power_w=node_copy.get("solar_input_power_w")
            )
            return {
                "node_id": node_id,
                "power_state": node_copy.get("power_mode", sm.current_state.value),
                "battery_soc_pct": soc,
                "battery_voltage_v": v_bat,
                "battery_state": node_copy.get("battery_state", classify_battery_state(soc, False)),
                "battery_current_a": round(budget.estimated_average_current_ma / 1000.0, 3),
                "battery_power_w": budget.estimated_power_w,
                "charging": bool(node_copy.get("charging", False)),
                "solar_available": bool(node_copy.get("solar_available", False)),
                "solar_input_voltage_v": 5.8 if node_copy.get("solar_available") else 0.0,
                "solar_input_power_w": node_copy.get("solar_input_power_w", 0.0),
                "telemetry_interval_s": interval,
                "gps_interval_s": sm.get_gps_interval(),
                "estimated_average_current_ma": budget.estimated_average_current_ma,
                "estimated_power_w": budget.estimated_power_w,
                "estimated_autonomy_hours": budget.estimated_autonomy_hours,
                "estimated_autonomy_days": budget.estimated_autonomy_days,
                "estimated_daily_energy_use_wh": budget.estimated_daily_energy_use_wh,
                "estimated_daily_solar_input_wh": budget.estimated_daily_solar_input_wh,
                "desired_power_profile": self._desired_power_profiles.get(node_id),
                "measurement_status": "SIMULATED / ESTIMATED",
                "last_updated": _utc_now_iso(),
            }

    def get_node(self, node_id: str) -> Optional[Dict[str, Any]]:
        """Retrieves a single node by ID with evaluated dynamic status."""
        with self._lock:
            node = self._nodes.get(node_id)
            if not node:
                return None
            return self._apply_online_status(dict(node))

    def get_all_nodes(
        self,
        state: Optional[str] = None,
        district: Optional[str] = None,
        status: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """Retrieves all registered nodes with optional filtering by state, district, or status."""
        with self._lock:
            nodes = [self._apply_online_status(dict(n)) for n in self._nodes.values()]

        if state:
            nodes = [n for n in nodes if (n.get("state") or "").lower() == state.lower()]
        if district:
            nodes = [n for n in nodes if (n.get("district") or "").lower() == district.lower()]
        if status:
            nodes = [n for n in nodes if (n.get("status") or "").upper() == status.upper()]

        return nodes

    def get_nodes_by_district(self, district: str) -> List[Dict[str, Any]]:
        """Returns all nodes assigned to a specific district."""
        return self.get_all_nodes(district=district)

    def get_all_districts(self, state: Optional[str] = None) -> List[str]:
        """Returns list of distinct districts having registered nodes."""
        nodes = self.get_all_nodes(state=state)
        districts = {n["district"] for n in nodes if n.get("district")}
        return sorted(list(districts))

    def _apply_online_status(self, node: Dict[str, Any]) -> Dict[str, Any]:
        """
        Evaluates node health state based on elapsed time since last_seen:
        - delta <= stale_threshold_seconds (120s): ONLINE
        - 120s < delta <= offline_threshold_seconds (300s): STALE
        - delta > offline_threshold_seconds (300s): OFFLINE
        """
        last_seen_str = node.get("last_seen")
        if not last_seen_str:
            node["status"] = "OFFLINE"
            return node

        try:
            cleaned_iso = last_seen_str.replace("Z", "+00:00")
            dt = datetime.datetime.fromisoformat(cleaned_iso)
            now = datetime.datetime.now(datetime.timezone.utc)
            if dt.tzinfo is None:
                dt = dt.replace(tzinfo=datetime.timezone.utc)
            delta = (now - dt).total_seconds()
            
            if delta <= self.stale_threshold_seconds:
                node["status"] = "ONLINE"
            elif delta <= self.offline_threshold_seconds:
                node["status"] = "STALE"
            else:
                node["status"] = "OFFLINE"
        except Exception:
            node["status"] = "OFFLINE"

        return node


# Global instance
node_manager = NodeManager()
