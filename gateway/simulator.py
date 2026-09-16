"""
TerraEdge — Type A Field Sensor Node Simulator (Phase 5).
Generates and transmits physically coherent multi-sensor telemetry packets to the Type B Gateway.
Supports single-node hazard scenarios and multi-node concurrent network demonstrations.
"""

from __future__ import annotations
import argparse
import datetime
import json
import math
import random
import sys
import time
from typing import Any, Dict, Generator, List, Optional
import urllib.request
import urllib.error

# Ensure UTF-8 output across Windows consoles
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")


def _utc_now_iso() -> str:
    return datetime.datetime.now(datetime.timezone.utc).isoformat()


# ============================================================================
# Coherent Scenario Telemetry Generators
# ============================================================================

def generate_normal_packet(
    node_id: str,
    step: int = 0,
    state: str = "Tamil Nadu",
    district: str = "Coimbatore",
    zone: str = "Western Ghats Foothill Station",
    lat: float = 11.0168,
    lon: float = 76.9558,
    is_simulated: bool = True
) -> Dict[str, Any]:
    """Nominal baseline."""
    j = math.sin(step * 0.5) * 1.5
    return {
        "node_id": node_id, "node_type": "Type-A",
        "state": state, "district": district, "zone": zone,
        "timestamp": _utc_now_iso(), "latitude": lat, "longitude": lon,
        "is_simulated": is_simulated, "sequence": step,
        "battery_pct": round(96.0 - step * 0.05, 1),
        "temperature_c": round(28.0 + j, 1), "humidity_pct": round(65.0 - j, 1),
        "pressure_hpa": 1010.5, "gas_resistance_kohm": round(45.0 + j, 1),
        "rainfall_mm": 0.0, "rainfall_1h_mm": 0.0, "rainfall_24h_mm": 2.0,
        "water_level_m": 0.45, "ultrasonic_distance_cm": 255.0,
        "soil_moisture_pct": round(32.0 + j, 1),
        "pm25_ug_m3": round(22.0 + abs(j), 1), "pm10_ug_m3": round(45.0 + abs(j), 1),
        "mq135_raw": 110.0, "flame_detected": False,
        "tilt_magnitude": 1.8, "tilt_rate": 0.0, "vibration_rate": 0.0,
        "ph": 7.35, "tds_ppm": 185.0, "turbidity": 2.1
    }


def generate_flood_packet(
    node_id: str,
    step: int = 0,
    state: str = "Tamil Nadu",
    district: str = "Tiruchirappalli",
    zone: str = "Kaveri River Floodplain",
    lat: float = 10.7905,
    lon: float = 78.7047,
    is_simulated: bool = True
) -> Dict[str, Any]:
    """Severe monsoon deluge."""
    r1 = min(65.0, 25.0 + step * 8.0)
    r24 = min(220.0, 80.0 + step * 25.0)
    wl = min(4.8, 2.2 + step * 0.45)
    return {
        "node_id": node_id, "node_type": "Type-A",
        "state": state, "district": district, "zone": zone,
        "timestamp": _utc_now_iso(), "latitude": lat, "longitude": lon,
        "is_simulated": is_simulated, "sequence": step,
        "battery_pct": 89.0, "temperature_c": 24.5, "humidity_pct": 96.0, "pressure_hpa": 996.5,
        "rainfall_mm": round(r1 / 4.0, 1), "rainfall_1h_mm": round(r1, 1),
        "rainfall_24h_mm": round(r24, 1), "water_level_m": round(wl, 2),
        "ultrasonic_distance_cm": round(max(0.0, 300.0 - wl * 100.0), 1),
        "soil_moisture_pct": round(min(98.0, 75.0 + step * 5.0), 1),
        "pm25_ug_m3": 12.0, "pm10_ug_m3": 22.0, "mq135_raw": 115.0,
        "flame_detected": False, "tilt_magnitude": 2.5
    }


def generate_landslide_packet(
    node_id: str,
    step: int = 0,
    state: str = "Tamil Nadu",
    district: str = "Nilgiris",
    zone: str = "Nilgiris Mountain Pass",
    lat: float = 11.4102,
    lon: float = 76.6950,
    is_simulated: bool = True
) -> Dict[str, Any]:
    """Slope failure precursor."""
    tilt = min(35.0, 12.0 + step * 4.5)
    vib = min(85.0, 25.0 + step * 15.0)
    return {
        "node_id": node_id, "node_type": "Type-A",
        "state": state, "district": district, "zone": zone,
        "timestamp": _utc_now_iso(), "latitude": lat, "longitude": lon,
        "is_simulated": is_simulated, "sequence": step,
        "battery_pct": 82.5, "temperature_c": 19.5, "humidity_pct": 88.0,
        "rainfall_mm": 12.0, "rainfall_24h_mm": 110.0,
        "soil_moisture_pct": round(min(95.0, 80.0 + step * 3.0), 1),
        "tilt_magnitude": round(tilt, 2), "tilt_rate": round(3.5 + step * 1.2, 2),
        "vibration_rate": round(vib, 1), "flame_detected": False
    }


def generate_wildfire_packet(
    node_id: str,
    step: int = 0,
    state: str = "Tamil Nadu",
    district: str = "Erode",
    zone: str = "Sathyamangalam Forest Reserve",
    lat: float = 11.5034,
    lon: float = 77.2412,
    is_simulated: bool = True
) -> Dict[str, Any]:
    """Wildfire scenario."""
    temp = min(48.0, 39.0 + step * 1.8)
    hum = max(12.0, 24.0 - step * 2.0)
    pm = min(350.0, 85.0 + step * 50.0)
    mq135 = min(800.0, 200.0 + step * 100.0)
    return {
        "node_id": node_id, "node_type": "Type-A",
        "state": state, "district": district, "zone": zone,
        "timestamp": _utc_now_iso(), "latitude": lat, "longitude": lon,
        "is_simulated": is_simulated, "sequence": step,
        "battery_pct": 78.0, "temperature_c": round(temp, 1), "humidity_pct": round(hum, 1),
        "pressure_hpa": 1004.0, "gas_resistance_kohm": round(max(0.4, 6.5 - step * 1.2), 2),
        "pm25_ug_m3": round(pm, 1), "pm10_ug_m3": round(pm * 1.6, 1),
        "mq135_raw": round(mq135, 1), "flame_detected": step >= 1
    }


def generate_air_pollution_packet(
    node_id: str,
    step: int = 0,
    state: str = "Tamil Nadu",
    district: str = "Chennai",
    zone: str = "Adyar Urban Industrial Belt",
    lat: float = 13.0325,
    lon: float = 80.1808,
    is_simulated: bool = True
) -> Dict[str, Any]:
    """Air pollution smog."""
    pm25 = min(450.0, 260.0 + step * 40.0)
    return {
        "node_id": node_id, "node_type": "Type-A",
        "state": state, "district": district, "zone": zone,
        "timestamp": _utc_now_iso(), "latitude": lat, "longitude": lon,
        "is_simulated": is_simulated, "sequence": step,
        "battery_pct": 91.0, "temperature_c": 16.0, "humidity_pct": 82.0, "pressure_hpa": 1016.0,
        "pm25_ug_m3": round(pm25, 1), "pm10_ug_m3": round(pm25 * 1.8, 1),
        "mq135_raw": round(min(650.0, 320.0 + step * 60.0), 1),
        "gas_resistance_kohm": 25.0, "flame_detected": False
    }


def generate_extreme_heat_packet(
    node_id: str,
    step: int = 0,
    state: str = "Maharashtra",
    district: str = "Pune",
    zone: str = "Pune CWPRS Micro-met Station",
    lat: float = 18.4350,
    lon: float = 73.7915,
    is_simulated: bool = True
) -> Dict[str, Any]:
    """Heatwave scenario."""
    temp = min(49.5, 43.5 + step * 1.5)
    return {
        "node_id": node_id, "node_type": "Type-A",
        "state": state, "district": district, "zone": zone,
        "timestamp": _utc_now_iso(), "latitude": lat, "longitude": lon,
        "is_simulated": is_simulated, "sequence": step,
        "battery_pct": 84.0, "temperature_c": round(temp, 1), "humidity_pct": 58.0,
        "pressure_hpa": 1008.0, "gas_resistance_kohm": 40.0, "mq135_raw": 125.0, "flame_detected": False
    }


def generate_industrial_packet(
    node_id: str,
    step: int = 0,
    state: str = "Andhra Pradesh",
    district: str = "Visakhapatnam",
    zone: str = "Visakhapatnam Petrochemical Zone",
    lat: float = 17.6868,
    lon: float = 83.2185,
    is_simulated: bool = True
) -> Dict[str, Any]:
    """Industrial plume."""
    mq135 = min(850.0, 580.0 + step * 80.0)
    pm25 = min(220.0, 95.0 + step * 35.0)
    return {
        "node_id": node_id, "node_type": "Type-A",
        "state": state, "district": district, "zone": zone,
        "timestamp": _utc_now_iso(), "latitude": lat, "longitude": lon,
        "is_simulated": is_simulated, "sequence": step,
        "battery_pct": 88.0, "temperature_c": 32.0, "humidity_pct": 72.0, "pressure_hpa": 1008.0,
        "mq135_raw": round(mq135, 1), "gas_resistance_kohm": 0.8,
        "pm25_ug_m3": round(pm25, 1), "pm10_ug_m3": round(pm25 * 1.6, 1), "flame_detected": False
    }


def generate_water_quality_packet(
    node_id: str,
    step: int = 0,
    state: str = "Andhra Pradesh",
    district: str = "Visakhapatnam",
    zone: str = "Godavari River Industrial Outfall",
    lat: float = 17.7285,
    lon: float = 83.3015,
    is_simulated: bool = True
) -> Dict[str, Any]:
    """Water quality degradation."""
    ph = max(3.2, 5.2 - step * 0.6)
    turb = min(140.0, 45.0 + step * 25.0)
    tds = min(1600.0, 650.0 + step * 250.0)
    return {
        "node_id": node_id, "node_type": "Type-A",
        "state": state, "district": district, "zone": zone,
        "timestamp": _utc_now_iso(), "latitude": lat, "longitude": lon,
        "is_simulated": is_simulated, "sequence": step,
        "battery_pct": 92.0, "temperature_c": 26.5, "humidity_pct": 78.0,
        "ph": round(ph, 2), "tds_ppm": round(tds, 1), "turbidity": round(turb, 1)
    }


SCENARIO_MAP = {
    "normal": generate_normal_packet,
    "flood": generate_flood_packet,
    "landslide": generate_landslide_packet,
    "wildfire": generate_wildfire_packet,
    "air_pollution": generate_air_pollution_packet,
    "extreme_heat": generate_extreme_heat_packet,
    "industrial_emissions": generate_industrial_packet,
    "water_quality": generate_water_quality_packet,
}


def send_telemetry_http(url: str, packet: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """Transmits JSON telemetry packet via HTTP POST to the Type B Gateway."""
    data = json.dumps(packet).encode("utf-8")
    req = urllib.request.Request(
        url,
        data=data,
        headers={"Content-Type": "application/json", "User-Agent": "TerraEdge-Simulator/5.0"}
    )
    try:
        with urllib.request.urlopen(req, timeout=5.0) as resp:
            body = resp.read().decode("utf-8")
            return json.loads(body)
    except urllib.error.HTTPError as e:
        err_body = e.read().decode("utf-8", errors="ignore")
        print(f"❌ [SIMULATOR] HTTP {e.code} Error: {err_body}", flush=True)
    except Exception as e:
        print(f"❌ [SIMULATOR] Connection Failed ({e})", flush=True)
    return None


def run_multi_node_demo(url: str, interval: float, count: int) -> None:
    """
    Executes a concurrent 4-node environmental network simulation:
    - TE-001 (Tiruchirappalli - Kaveri River Floodplain): Elevated Flood (Risk ~82%)
    - TE-002 (Tiruchirappalli - Grand Anicut Canal): Elevated Flood (Risk ~76%)
    - TE-003 (Chennai - Adyar Urban Industrial Belt): Elevated Air Pollution (Risk ~71%)
    - TE-004 (Coimbatore - Western Ghats Foot Station): Normal Baseline (Risk ~12%)
    Demonstrates district aggregation, spatial hotspot formation, and isolated histories.
    """
    print("=" * 70)
    print("  🌐 TerraEdge Phase 5 — Multi-Node Environmental Network Demo")
    print("  Node 1: TE-001 | Tiruchirappalli | Kaveri Floodplain   | FLOOD ELEVATED")
    print("  Node 2: TE-002 | Tiruchirappalli | Grand Anicut Canal  | FLOOD ELEVATED")
    print("  Node 3: TE-003 | Chennai         | Adyar Industrial    | AIR POLLUTION")
    print("  Node 4: TE-004 | Coimbatore      | Western Ghats Foot  | NORMAL BASELINE")
    print(f"  Target : {url}")
    print(f"  Interval: {interval}s  |  Count: {'Infinite' if count == 0 else count}")
    print("=" * 70)

    step = 0
    while True:
        step += 1
        print(f"\n[{datetime.datetime.now().strftime('%H:%M:%S')}] 🚀 MULTI-NODE CYCLE #{step}")

        # Node 1: TE-001 (Flood)
        p1 = generate_flood_packet(
            node_id="TE-001", step=step,
            state="Tamil Nadu", district="Tiruchirappalli",
            zone="Kaveri River Floodplain", lat=10.7905, lon=78.7047
        )
        res1 = send_telemetry_http(url, p1)
        if res1:
            print(f"  📍 [TE-001 | Tiruchirappalli] Flood: {res1.get('composite_risk_pct')}% ({res1.get('primary_severity')}) | Proc: {res1.get('processing_time_ms')}ms")

        # Node 2: TE-002 (Flood hotspot partner)
        p2 = generate_flood_packet(
            node_id="TE-002", step=max(0, step - 1),
            state="Tamil Nadu", district="Tiruchirappalli",
            zone="Grand Anicut Canal Corridor", lat=10.8201, lon=78.6912
        )
        res2 = send_telemetry_http(url, p2)
        if res2:
            print(f"  📍 [TE-002 | Tiruchirappalli] Flood: {res2.get('composite_risk_pct')}% ({res2.get('primary_severity')}) | Proc: {res2.get('processing_time_ms')}ms")

        # Node 3: TE-003 (Air Pollution)
        p3 = generate_air_pollution_packet(
            node_id="TE-003", step=step,
            state="Tamil Nadu", district="Chennai",
            zone="Adyar Urban Industrial Belt", lat=13.0325, lon=80.1808
        )
        res3 = send_telemetry_http(url, p3)
        if res3:
            print(f"  📍 [TE-003 | Chennai] Air Pollution: {res3.get('composite_risk_pct')}% ({res3.get('primary_severity')}) | Proc: {res3.get('processing_time_ms')}ms")

        # Node 4: TE-004 (Normal)
        p4 = generate_normal_packet(
            node_id="TE-004", step=step,
            state="Tamil Nadu", district="Coimbatore",
            zone="Western Ghats Foothill Station", lat=11.0168, lon=76.9558
        )
        res4 = send_telemetry_http(url, p4)
        if res4:
            print(f"  📍 [TE-004 | Coimbatore] Normal: {res4.get('composite_risk_pct')}% ({res4.get('primary_severity')}) | Proc: {res4.get('processing_time_ms')}ms")

        if count > 0 and step >= count:
            print("\n🏁 Multi-node demo target cycles reached. Simulator stopped.")
            break

        time.sleep(interval)


def run_simulator(
    scenario: str,
    node_id: str,
    url: str,
    interval: float,
    count: int,
    state: Optional[str] = None,
    district: Optional[str] = None,
    zone: Optional[str] = None,
    lat: Optional[float] = None,
    lon: Optional[float] = None,
    is_simulated: bool = True
) -> None:
    """Runs single-node simulator loop generating and streaming packets."""
    print("=" * 65)
    print(f"  📡 TerraEdge Type-A Sensor Node Simulator")
    print(f"  Node ID  : {node_id}")
    print(f"  Target   : {url}")
    print(f"  Scenario : {scenario.upper()}")
    print(f"  Interval : {interval}s  |  Count: {'Infinite' if count == 0 else count}")
    print("=" * 65)

    step = 0
    scenario_keys = list(SCENARIO_MAP.keys())

    while True:
        step += 1
        if scenario == "all":
            current_scenario = scenario_keys[(step - 1) % len(scenario_keys)]
            generator = SCENARIO_MAP[current_scenario]
            scenario_label = current_scenario.upper()
        else:
            generator = SCENARIO_MAP.get(scenario, generate_normal_packet)
            scenario_label = scenario.upper()

        kwargs: Dict[str, Any] = {"node_id": node_id, "step": step, "is_simulated": is_simulated}
        if state: kwargs["state"] = state
        if district: kwargs["district"] = district
        if zone: kwargs["zone"] = zone
        if lat is not None: kwargs["lat"] = lat
        if lon is not None: kwargs["lon"] = lon

        packet = generator(**kwargs)

        print(f"\n[{datetime.datetime.now().strftime('%H:%M:%S')}] 🚀 Frame #{step} ({scenario_label}) -> Transmitting {node_id}...")
        res = send_telemetry_http(url, packet)

        if res:
            print(f"  ✅ Status: 200 OK | Processing Time: {res.get('processing_time_ms', 0)}ms")
            print(f"  🚨 Composite Risk: {res.get('composite_risk_pct')}% | Severity: {res.get('primary_severity')} | Dominant: {res.get('primary_hazard')}")
            
            rankings = res.get("ranked_hazards", [])
            if rankings:
                top_3 = ", ".join([f"#{r['rank']} {r['hazard']} ({r['risk_pct']}%)" for r in rankings[:3]])
                print(f"  📊 Priority Ranking: {top_3}")
            
            alerts = res.get("alerts_triggered", [])
            if alerts:
                for a in alerts:
                    print(f"  ⚠️  [ALERT DISPATCHED] {a.get('hazard')} ({a.get('severity')}) - {a.get('risk_score_pct')}%")

        if count > 0 and step >= count:
            print("\n🏁 Target packet count reached. Simulator stopped.")
            break

        time.sleep(interval)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="TerraEdge Type-A Telemetry Simulator (Phase 5)")
    parser.add_argument("--scenario", type=str, default="flood",
                        choices=["normal", "flood", "landslide", "wildfire", "air_pollution", "extreme_heat", "industrial_emissions", "water_quality", "all"],
                        help="Hazard scenario to simulate (default: flood)")
    parser.add_argument("--node-id", type=str, default="TE-SIM-001", help="Field node ID (default: TE-SIM-001)")
    parser.add_argument("--state", type=str, default=None, help="State name (e.g. 'Tamil Nadu')")
    parser.add_argument("--district", type=str, default=None, help="District name (e.g. 'Chennai')")
    parser.add_argument("--zone", type=str, default=None, help="Geographic zone description")
    parser.add_argument("--lat", type=float, default=None, help="Latitude")
    parser.add_argument("--lon", type=float, default=None, help="Longitude")
    parser.add_argument("--url", type=str, default="http://127.0.0.1:8000/api/telemetry", help="Gateway endpoint URL")
    parser.add_argument("--interval", type=float, default=2.0, help="Interval between frames in seconds")
    parser.add_argument("--count", type=int, default=1, help="Number of packets to send (0 for infinite)")
    parser.add_argument("--multi-node-demo", action="store_true", help="Launch concurrent 4-node multi-hazard network demonstration")

    args = parser.parse_args()

    if args.multi-node-demo if hasattr(args, "multi-node-demo") else getattr(args, "multi_node_demo", False):
        run_multi_node_demo(args.url, args.interval, args.count)
    else:
        run_simulator(
            scenario=args.scenario,
            node_id=args.node_id,
            url=args.url,
            interval=args.interval,
            count=args.count,
            state=args.state,
            district=args.district,
            zone=args.zone,
            lat=args.lat,
            lon=args.lon
        )
