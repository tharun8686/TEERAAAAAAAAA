import sys
import os
import json
from landslide_inference import LandslideInferenceEngine

def run_synthetic_tests():
    engine = LandslideInferenceEngine()

    print("=" * 60)
    print("      LANDSLIDE / SLOPE INSTABILITY INFERENCE TEST SUITE")
    print("=" * 60)

    # Test A: Normal Stable Slope
    test_a = {
        'soil_moisture_vwc': 0.18, 'soil_moisture_rate': 0.0,
        'tilt_magnitude': 2.5, 'tilt_rate': 0.0, 'vibration_rate': 2.0,
        'temperature': 22.0, 'humidity': 55.0, 'rainfall_24h': 0.0
    }
    res_a = engine.predict_landslide(test_a)
    print("\n[TEST A] Normal Stable Slope:")
    print(json.dumps(res_a, indent=2))
    assert res_a['severity'] == 'NORMAL', f"Expected NORMAL but got {res_a['severity']}"

    # Test B: Developing Moisture Saturation
    test_b = {
        'soil_moisture_vwc': 0.32, 'soil_moisture_rate': 0.03,
        'tilt_magnitude': 3.0, 'tilt_rate': 0.1, 'vibration_rate': 5.0,
        'temperature': 21.0, 'humidity': 80.0, 'rainfall_24h': 25.0
    }
    res_b = engine.predict_landslide(test_b)
    print("\n[TEST B] Developing Soil Moisture Saturation:")
    print(json.dumps(res_b, indent=2))
    assert res_b['severity'] in ['WATCH', 'WARNING'], f"Expected WATCH/WARNING but got {res_b['severity']}"

    # Test C: Accelerated Slope Instability & Movement
    test_c = {
        'soil_moisture_vwc': 0.45, 'soil_moisture_rate': 0.08,
        'tilt_magnitude': 14.0, 'tilt_rate': 2.2, 'vibration_rate': 55.0,
        'temperature': 20.0, 'humidity': 90.0, 'rainfall_24h': 85.0
    }
    res_c = engine.predict_landslide(test_c)
    print("\n[TEST C] Accelerated Slope Instability & Movement:")
    print(json.dumps(res_c, indent=2))
    assert res_c['severity'] in ['WARNING', 'CRITICAL'], f"Expected High Severity but got {res_c['severity']}"

    # Test D: Sensor Failure (Soil Moisture Missing)
    test_d = {
        'soil_moisture_vwc': None, 'soil_moisture_rate': None,
        'tilt_magnitude': 2.5, 'tilt_rate': 0.0, 'vibration_rate': 2.0,
        'temperature': 22.0, 'humidity': 55.0, 'rainfall_24h': 0.0
    }
    res_d = engine.predict_landslide(test_d)
    print("\n[TEST D] Sensor Failure Handling (Soil Moisture Missing):")
    print(json.dumps(res_d, indent=2))
    assert res_d['sensor_health'] < 1.0, "Expected degraded sensor health"
    assert res_d['severity'] != 'CRITICAL', "Sensor failure should not trigger false critical"

    # Test E: Missing External Rainfall Context
    test_e = {
        'soil_moisture_vwc': 0.20, 'soil_moisture_rate': 0.0,
        'tilt_magnitude': 2.5, 'tilt_rate': 0.0, 'vibration_rate': 2.0,
        'temperature': 22.0, 'humidity': 55.0, 'rainfall_24h': None
    }
    res_e = engine.predict_landslide(test_e)
    print("\n[TEST E] Missing External Rainfall Context:")
    print(json.dumps(res_e, indent=2))
    assert res_e['external_context_available'] == False, "Expected external context false"

    print("\n" + "=" * 60)
    print("ALL SYNTHETIC TEST CASES PASSED SUCCESSFULLY!")
    print("=" * 60)

if __name__ == '__main__':
    run_synthetic_tests()
