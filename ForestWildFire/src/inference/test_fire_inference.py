import sys
import os
import json
from fire_inference import FireInferenceEngine

def run_synthetic_tests():
    engine = FireInferenceEngine()

    print("=" * 60)
    print("      FOREST WILDFIRE INFERENCE TEST SUITE")
    print("=" * 60)

    # Test Case A: Normal Baseline
    test_a = {
        'temperature': 25.0, 'humidity': 55.0, 'pressure': 1013.0,
        'pm25': 12.0, 'tvoc': 150.0, 'raw_ethanol': 2900.0,
        'temperature_rate': 0.0, 'humidity_rate': 0.0, 'pm25_rate': 0.0, 'tvoc_rate': 0.0,
        'temperature_delta_5': 0.0, 'humidity_delta_5': 0.0
    }
    res_a = engine.predict_fire(test_a)
    print("\n[TEST A] Normal Baseline Environment:")
    print(json.dumps(res_a, indent=2))
    assert res_a['severity'] == 'NORMAL', f"Expected NORMAL but got {res_a['severity']}"

    # Test Case B: Developing Smoke / Early Warning
    test_b = {
        'temperature': 35.0, 'humidity': 40.0, 'pressure': 1009.0,
        'pm25': 85.0, 'tvoc': 450.0, 'raw_ethanol': 3050.0,
        'temperature_rate': 0.08, 'humidity_rate': -0.05, 'pm25_rate': 0.35, 'tvoc_rate': 0.25,
        'temperature_delta_5': 2.0, 'humidity_delta_5': -3.5
    }
    res_b = engine.predict_fire(test_b)
    print("\n[TEST B] Developing Smoke / Elevated Indicators:")
    print(json.dumps(res_b, indent=2))
    assert res_b['severity'] in ['WATCH', 'WARNING', 'CRITICAL'], f"Expected Elevated status but got {res_b['severity']}"

    # Test Case C: Strong Fire Signature
    test_c = {
        'temperature': 55.0, 'humidity': 18.0, 'pressure': 1004.0,
        'pm25': 450.0, 'tvoc': 2200.0, 'raw_ethanol': 3500.0,
        'temperature_rate': 0.25, 'humidity_rate': -0.30, 'pm25_rate': 1.20, 'tvoc_rate': 0.90,
        'temperature_delta_5': 8.5, 'humidity_delta_5': -14.0
    }
    res_c = engine.predict_fire(test_c)
    print("\n[TEST C] Strong Fire Signature:")
    print(json.dumps(res_c, indent=2))
    assert res_c['severity'] in ['WARNING', 'CRITICAL'], f"Expected High Severity but got {res_c['severity']}"

    # Test Case D: Sensor Failure (Missing PM2.5 and Gas proxies)
    test_d = {
        'temperature': 26.0, 'humidity': 52.0, 'pressure': 1012.0,
        'pm25': None, 'tvoc': None, 'raw_ethanol': None, # Missing hardware sensors
        'temperature_rate': 0.0, 'humidity_rate': 0.0, 'pm25_rate': None, 'tvoc_rate': None,
        'temperature_delta_5': 0.0, 'humidity_delta_5': 0.0
    }
    res_d = engine.predict_fire(test_d)
    print("\n[TEST D] Sensor Failure Handling (Missing PM & Gas):")
    print(json.dumps(res_d, indent=2))
    assert res_d['confidence'] < 0.90, "Expected degraded confidence when sensors fail"
    assert res_d['severity'] != 'CRITICAL', "Sensor failure should not trigger false critical"

    print("\n" + "=" * 60)
    print("ALL 4 SYNTHETIC TEST CASES PASSED SUCCESSFULLY!")
    print("=" * 60)

if __name__ == '__main__':
    run_synthetic_tests()
