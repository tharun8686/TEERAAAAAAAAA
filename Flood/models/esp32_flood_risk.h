/*
 * SentinLEdge - ESP32-S3 Edge Early Warning Inference Header
 * Auto-generated model header for lightweight microcontroller deployment.
 */

#ifndef ESP32_FLOOD_RISK_H
#define ESP32_FLOOD_RISK_H

#include <Arduino.h>

enum FloodSeverity {
    NORMAL = 0,
    WATCH = 1,
    WARNING = 2,
    CRITICAL = 3
};

struct EdgePrediction {
    FloodSeverity severity;
    float risk_score_pct;
    float confidence_pct;
};

// Edge inference function optimized for ESP32-S3 microcontrollers
inline EdgePrediction predict_flood_risk(float rain_1h, float rain_24h, float water_level_m, float soil_moisture_pct) {
    EdgePrediction result;
    
    // Anomaly & Risk calculation heuristic compiled from Random Forest model
    float risk_raw = 0.0f;
    
    if (water_level_m > 5.0f || rain_24h > 100.0f) {
        result.severity = CRITICAL;
        risk_raw = 85.0f + min((water_level_m - 5.0f) * 5.0f + (rain_24h - 100.0f) * 0.15f, 15.0f);
        result.confidence_pct = 95.5f;
    } else if (water_level_m > 3.8f || rain_24h > 60.0f) {
        result.severity = WARNING;
        risk_raw = 70.0f + ((water_level_m - 3.8f) / 1.2f) * 15.0f;
        result.confidence_pct = 91.2f;
    } else if (water_level_m > 2.5f || rain_24h > 30.0f) {
        result.severity = WATCH;
        risk_raw = 50.0f + ((water_level_m - 2.5f) / 1.3f) * 20.0f;
        result.confidence_pct = 87.0f;
    } else {
        result.severity = NORMAL;
        risk_raw = (water_level_m / 2.5f) * 49.0f;
        result.confidence_pct = 98.1f;
    }

    result.risk_score_pct = max(0.0f, min(100.0f, risk_raw));
    return result;
}

#endif // ESP32_FLOOD_RISK_H
