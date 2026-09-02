// ============================================================
// inference.h  --  ML Inference engine declarations
// LandslideEdge | ESP32-S3 N16R8
// Model: CalibratedRandomForestClassifier (150 trees, 8 features)
// ============================================================
#pragma once
#include <Arduino.h>
#include "sensors.h"

// Severity levels matching Python backend exactly
enum LandslideSeverity {
    SEVERITY_NORMAL   = 0,
    SEVERITY_WATCH    = 1,
    SEVERITY_WARNING  = 2,
    SEVERITY_CRITICAL = 3
};

// Complete inference result
struct InferenceResult {
    float             prob_normal;       // P(class=0)
    float             prob_instability;  // P(class=1) -- primary risk score
    int               predicted_class;  // 0 or 1
    LandslideSeverity severity;
    float             confidence;        // 0.2-0.96 based on sensor health
    float             sensor_health;
    const char*       severity_str;
    uint32_t          inference_time_us; // Microseconds
};

void inference_init();
void inference_run(const FeatureVector& feat,
                   const RawSensorData& raw,
                   InferenceResult& result);
void inference_print_result(const InferenceResult& result);
