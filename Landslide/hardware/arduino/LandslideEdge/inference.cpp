// ============================================================
// inference.cpp  --  ML Inference engine
// LandslideEdge | ESP32-S3 N16R8
// Model: CalibratedClassifierCV(RandomForest, n=50, depth=10, folds=3)
// Exact replica of sklearn predict_proba() pipeline
// ============================================================
#include "inference.h"
#include "config.h"
#include "model_rf.h"   // auto-generated 150 tree functions

// Severity labels
static const char* SEV_LABELS[] = {"NORMAL", "WATCH", "WARNING", "CRITICAL"};

void inference_init() {
    Serial.println("[inference] CalibratedRF model loaded (150 trees, 8 features).");
    Serial.printf("[inference] Sigmoid params: A=[%.4f, %.4f, %.4f]  B=[%.4f, %.4f, %.4f]\n",
                  RF_SIGMOID_A[0], RF_SIGMOID_A[1], RF_SIGMOID_A[2],
                  RF_SIGMOID_B[0], RF_SIGMOID_B[1], RF_SIGMOID_B[2]);
}

void inference_run(const FeatureVector& feat,
                   const RawSensorData& raw,
                   InferenceResult& result) {
    uint32_t t0 = micros();

    // Run full CalibratedClassifierCV inference (see model_rf.h)
    float prob1 = rf_predict_proba(feat.raw_array);
    float prob0 = 1.0f - prob1;

    result.prob_instability = prob1;
    result.prob_normal      = prob0;
    result.predicted_class  = (prob1 >= 0.50f) ? 1 : 0;

    // Sensor health & confidence (mirrors Python inference engine)
    float missing = 0.0f;
    if (!raw.soil_ok)  missing += 1.0f;
    if (!raw.mpu_ok)   missing += 1.0f;
    if (!raw.dht_ok)   missing += 1.0f;
    result.sensor_health = max(SENSOR_HEALTH_MIN, 1.0f - missing * SENSOR_HEALTH_PENALTY);

    bool has_rain     = raw.rain_ok;
    float base_conf   = has_rain ? 0.96f : 0.82f;
    result.confidence = base_conf * result.sensor_health;

    // Severity decision policy (mirrors landslide_inference.py exactly)
    float sm   = feat.soil_moisture_vwc;
    float tilt = feat.tilt_rate;
    float vib  = feat.vibration_rate;

    if (prob1 >= SEV_CRITICAL_PROB ||
        (sm > 0.40f && tilt > 1.5f) ||
        (tilt > 3.0f && vib > 30.0f)) {
        result.severity = SEVERITY_CRITICAL;
    } else if (prob1 >= SEV_WARNING_PROB || (sm > 0.35f && tilt > 0.5f)) {
        result.severity = SEVERITY_WARNING;
    } else if (prob1 >= SEV_WATCH_PROB || sm > 0.30f || tilt > 0.2f) {
        result.severity = SEVERITY_WATCH;
    } else {
        result.severity = SEVERITY_NORMAL;
    }

    result.severity_str     = SEV_LABELS[result.severity];
    result.inference_time_us = micros() - t0;
}

void inference_print_result(const InferenceResult& result) {
    Serial.println("=== INFERENCE RESULT ===");
    Serial.printf("  Class Probabilities:\n");
    Serial.printf("    P(NORMAL)      : %.4f  (%.1f %%)\n",
                  result.prob_normal,      result.prob_normal      * 100.0f);
    Serial.printf("    P(INSTABILITY) : %.4f  (%.1f %%)\n",
                  result.prob_instability, result.prob_instability * 100.0f);
    Serial.printf("  Predicted Class  : %d (%s)\n",
                  result.predicted_class,
                  result.predicted_class == 0 ? "NORMAL" : "INSTABILITY");
    Serial.printf("  Severity Level   : %s\n", result.severity_str);
    Serial.printf("  Confidence       : %.2f  (%.0f %%)\n",
                  result.confidence, result.confidence * 100.0f);
    Serial.printf("  Sensor Health    : %.2f\n", result.sensor_health);
    Serial.printf("  Inference Time   : %lu us\n", result.inference_time_us);
}
