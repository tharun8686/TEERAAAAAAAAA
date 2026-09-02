// ============================================================
// LandslideEdge.ino  --  Main Arduino Sketch
// Landslide Early Warning Node | ESP32-S3 N16R8
//
// Hardware Connections:
//   MPU6050  SDA -> GPIO8   SCL -> GPIO9
//   Soil V2  AO  -> GPIO1
//   LM393    AO  -> GPIO2
//   DHT11    DATA -> GPIO7
//   SW-420   DO   -> GPIO4
//
// Required Libraries (install via Arduino Library Manager):
//   - DHT sensor library by Adafruit (v1.4.4+)
//   - Adafruit Unified Sensor (v1.1.9+)
//   - Wire (built-in ESP32 core)
//
// Board: ESP32S3 Dev Module
//   Flash Mode      : QIO 80MHz
//   Flash Size      : 16MB (128Mb)
//   PSRAM           : OPI PSRAM
//   Upload Speed    : 921600
//   CPU Freq        : 240MHz
//   Core Debug Level: None
//
// Model: CalibratedRandomForestClassifier
//   150 decision trees (50 per CV fold, 3 folds)
//   8 input features, 2 output classes
//   Exact StandardScaler + Sigmoid Platt calibration
//   Compiled from: Landslide/models/final_landslide_model.pkl
// ============================================================

#include "config.h"
#include "sensors.h"
#include "inference.h"

static FeatureVector prev_feat = {};  // Previous feature vector for derivatives
static FeatureVector curr_feat = {};
static RawSensorData raw       = {};
static InferenceResult result  = {};

static uint32_t last_inference_ms = 0;
static uint32_t sample_count      = 0;

// ---- Separator helper ----
static void print_separator(char c = '-', int n = 60) {
    for (int i = 0; i < n; i++) Serial.print(c);
    Serial.println();
}

void setup() {
    Serial.begin(SERIAL_BAUD);
    delay(1500);

    print_separator('=');
    Serial.printf("  LandslideEdge Firmware v%s\n", FIRMWARE_VERSION);
    Serial.printf("  Node ID: %s\n", NODE_ID);
    Serial.printf("  Board  : %s @ 240 MHz\n", BOARD_NAME);
    print_separator('=');

    sensors_init();
    inference_init();

    // Initialise prev_feat to training means (avoids spike on first rate computation)
    prev_feat.soil_moisture_vwc  = 0.2426f;
    prev_feat.tilt_magnitude     = 2.6066f;

    last_inference_ms = millis();
    Serial.println("[main] System ready. Inference every 1 second.\n");
}

void loop() {
    uint32_t now = millis();
    if (now - last_inference_ms < INFERENCE_INTERVAL_MS) return;
    last_inference_ms = now;
    sample_count++;

    print_separator('=');
    Serial.printf("SAMPLE #%lu  |  uptime: %lus\n", sample_count, now / 1000);
    print_separator('-');

    // 1. Read all sensors
    bool all_ok = sensors_read(raw);
    sensors_print_raw(raw);

    // 2. Compute feature vector
    features_compute(raw, curr_feat, prev_feat);
    features_print(curr_feat);

    // 3. Run ML inference
    inference_run(curr_feat, raw, result);
    inference_print_result(result);

    // 4. Alert banner for elevated conditions
    if (result.severity >= SEVERITY_WARNING) {
        print_separator('!');
        Serial.printf("  *** ALERT: %s ***\n", result.severity_str);
        Serial.printf("  Risk Probability: %.1f %%\n", result.prob_instability * 100.0f);
        print_separator('!');
    }

    Serial.println();

    // 5. Save current features as previous for next derivative computation
    prev_feat = curr_feat;
}
