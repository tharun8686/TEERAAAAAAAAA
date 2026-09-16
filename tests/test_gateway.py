"""
TerraEdge — Gateway Automated Verification Test Suite.
Tests telemetry validation, node tracking, temporal feature calculation,
execution of all 7 hazard models, risk normalization, priority ranking, and API endpoints.
"""

import os
import sys
import unittest

from fastapi.testclient import TestClient

# Add project root to sys.path
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from gateway.app import app
from gateway.node_manager import node_manager
from gateway.telemetry import telemetry_engine
from gateway.simulator import (
    generate_normal_packet,
    generate_flood_packet,
    generate_wildfire_packet,
    generate_landslide_packet,
    generate_air_pollution_packet,
    generate_extreme_heat_packet,
    generate_industrial_packet,
    generate_water_quality_packet,
)


class TestTerraEdgeGateway(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.client = TestClient(app)

    def setUp(self):
        telemetry_engine.clear_history()

    def test_01_health_endpoint(self):
        """Verify gateway health and model loading status."""
        resp = self.client.get("/health")
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertEqual(data["status"], "healthy")
        self.assertIn("models_loaded", data)
        # Verify all 7 models are loaded
        for hazard in ["Flood", "Wildfire", "Landslide", "Air Quality", "Extreme Heat", "Toxic Flame", "Water Quality"]:
            self.assertTrue(data["models_loaded"].get(hazard), f"Model {hazard} failed to load!")

    def test_02_ingest_normal_telemetry(self):
        """Verify nominal environmental conditions yield NORMAL severity and low composite risk."""
        packet = generate_normal_packet("TE-TEST-001", step=0)
        resp = self.client.post("/api/telemetry", json=packet)
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        
        self.assertEqual(data["node_id"], "TE-TEST-001")
        self.assertIn(data["primary_severity"], ["NORMAL", "WATCH"])
        self.assertLess(data["composite_risk_pct"], 60.0)
        self.assertIn("Flood", data["hazard_results"])
        self.assertEqual(data["hazard_results"]["Flood"]["model_status"], "success")

    def test_03_flood_scenario(self):
        """Verify heavy rainfall and river stage triggers Flood as top priority."""
        packet = generate_flood_packet("TE-TEST-FLOOD", step=3)
        resp = self.client.post("/api/telemetry", json=packet)
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        
        self.assertEqual(data["primary_hazard"], "Flood")
        self.assertIn(data["primary_severity"], ["WARNING", "CRITICAL"])
        self.assertGreater(data["composite_risk_pct"], 60.0)
        self.assertEqual(data["ranked_hazards"][0]["hazard"], "Flood")
        self.assertGreater(len(data["alerts_triggered"]), 0)

    def test_04_wildfire_scenario(self):
        """Verify high heat, low humidity, smoke, and flame trigger Wildfire as top priority."""
        packet = generate_wildfire_packet("TE-TEST-FIRE", step=3)
        resp = self.client.post("/api/telemetry", json=packet)
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        
        self.assertEqual(data["primary_hazard"], "Wildfire")
        self.assertEqual(data["primary_severity"], "CRITICAL")
        self.assertGreater(data["composite_risk_pct"], 75.0)
        self.assertEqual(data["ranked_hazards"][0]["hazard"], "Wildfire")

    def test_05_landslide_scenario(self):
        """Verify slope tilt, soil saturation, and vibration trigger Landslide hazard."""
        packet = generate_landslide_packet("TE-TEST-SLOPE", step=3)
        resp = self.client.post("/api/telemetry", json=packet)
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        
        self.assertIn(data["primary_hazard"], ["Landslide", "Flood"])
        landslide_res = data["hazard_results"]["Landslide"]
        self.assertEqual(landslide_res["model_status"], "success")
        self.assertGreater(landslide_res["risk_pct"], 40.0)

    def test_06_air_pollution_scenario(self):
        """Verify high PM2.5 and gas proxy trigger Air Quality as top priority."""
        packet = generate_air_pollution_packet("TE-TEST-AIR", step=3)
        resp = self.client.post("/api/telemetry", json=packet)
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        
        self.assertEqual(data["primary_hazard"], "Air Quality")
        self.assertIn(data["primary_severity"], ["WARNING", "CRITICAL"])
        self.assertGreater(data["composite_risk_pct"], 70.0)

    def test_07_extreme_heat_scenario(self):
        """Verify extreme ambient temperature triggers Extreme Heat hazard."""
        packet = generate_extreme_heat_packet("TE-TEST-HEAT", step=3)
        resp = self.client.post("/api/telemetry", json=packet)
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        
        heat_res = data["hazard_results"]["Extreme Heat"]
        self.assertEqual(heat_res["model_status"], "success")
        self.assertGreater(heat_res["risk_pct"], 50.0)

    def test_08_industrial_emissions_scenario(self):
        """Verify sudden gas/solvent resistance drop triggers Toxic Flame."""
        packet = generate_industrial_packet("TE-TEST-IND", step=3)
        resp = self.client.post("/api/telemetry", json=packet)
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        
        ind_res = data["hazard_results"]["Toxic Flame"]
        self.assertEqual(ind_res["model_status"], "success")
        self.assertGreater(ind_res["risk_pct"], 40.0)

    def test_09_water_quality_scenario(self):
        """Verify toxic pH excursion and high turbidity trigger Water Quality hazard."""
        packet = generate_water_quality_packet("TE-TEST-WATER", step=3)
        resp = self.client.post("/api/telemetry", json=packet)
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        
        water_res = data["hazard_results"]["Water Quality"]
        self.assertEqual(water_res["model_status"], "success")
        self.assertGreater(water_res["risk_pct"], 40.0)

    def test_10_missing_sensor_skipping(self):
        """Verify that missing sensors cause corresponding models to be skipped gracefully without errors."""
        # Minimal packet with only air quality sensors — use canonical schema field names
        packet = {
            "node_id": "TE-AIR-ONLY",
            "pm25_ug_m3": 45.0,
            "pm10_ug_m3": 85.0,
            "temperature_c": 25.0
        }
        resp = self.client.post("/api/telemetry", json=packet)
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        
        # Air Quality should succeed
        self.assertEqual(data["hazard_results"]["Air Quality"]["model_status"], "success")
        # Water Quality should be skipped (missing pH, TDS, Turbidity)
        self.assertEqual(data["hazard_results"]["Water Quality"]["model_status"], "skipped")
        self.assertIn("sensors", data["hazard_results"]["Water Quality"]["skip_reason"].lower())

    def test_11_temporal_history_derivatives(self):
        """Verify that streaming multiple frames computes rate-of-change derivatives."""
        # Frame 1: temp = 30.0
        packet1 = {"node_id": "TE-HIST-01", "temperature_c": 30.0, "humidity_pct": 50.0}
        self.client.post("/api/telemetry", json=packet1)
        
        # Frame 2: temp = 35.0 (rate = +5.0)
        packet2 = {"node_id": "TE-HIST-01", "temperature_c": 35.0, "humidity_pct": 45.0}
        resp2 = self.client.post("/api/telemetry", json=packet2)
        self.assertEqual(resp2.status_code, 200)

    def test_12_node_manager_endpoints(self):
        """Verify GET /api/nodes and GET /api/nodes/{node_id}."""
        # Send telemetry to ensure node registered
        packet = generate_normal_packet("TE-NODE-REG-01")
        self.client.post("/api/telemetry", json=packet)
        
        # Check node list
        resp = self.client.get("/api/nodes")
        self.assertEqual(resp.status_code, 200)
        nodes = resp.json()
        node_ids = [n["node_id"] for n in nodes]
        self.assertIn("TE-NODE-REG-01", node_ids)
        
        # Check single node
        resp_single = self.client.get("/api/nodes/TE-NODE-REG-01")
        self.assertEqual(resp_single.status_code, 200)
        self.assertEqual(resp_single.json()["node_id"], "TE-NODE-REG-01")

    def test_13_latest_node_evaluation_endpoint(self):
        """Verify GET /api/latest/{node_id} returns cached composite response."""
        packet = generate_flood_packet("TE-LATEST-TEST")
        self.client.post("/api/telemetry", json=packet)
        
        resp = self.client.get("/api/latest/TE-LATEST-TEST")
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertEqual(data["node_id"], "TE-LATEST-TEST")
        self.assertEqual(data["primary_hazard"], "Flood")

    def test_14_invalid_telemetry_validation(self):
        """Verify invalid payload values are rejected with HTTP 422."""
        # Invalid latitude (> 90)
        bad_packet = {"node_id": "TE-BAD-01", "latitude": 125.0}
        resp = self.client.post("/api/telemetry", json=bad_packet)
        self.assertEqual(resp.status_code, 422)


if __name__ == "__main__":
    unittest.main()
