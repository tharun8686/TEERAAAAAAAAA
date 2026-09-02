/*
 * SentinLEdge - ESP32-S3 Dummy Hardware Firmware Test
 * Upload this sketch to your ESP32-S3 microcontroller to test live sensor reading,
 * local edge AI prediction using esp32_flood_risk.h, and FastAPI backend sync.
 */

#include <WiFi.h>
#include <HTTPClient.h>
#include "esp32_flood_risk.h"  // Include generated Edge AI header

// --- NETWORK CONFIGURATION ---
const char* WIFI_SSID = "YOUR_WIFI_NAME";
const char* WIFI_PASS = "YOUR_WIFI_PASSWORD";
// Replace with the local IP address of the laptop running FastAPI app.py
const char* BACKEND_URL = "http://192.168.1.100:8000/api/predict";

// --- HARDWARE PIN DEFINITIONS ---
#define LED_BUZZER_PIN 2   // Onboard LED or Alarm Transistor Pin
#define TRIG_PIN       12  // Ultrasonic Sensor Trigger Pin
#define ECHO_PIN       14  // Ultrasonic Sensor Echo Pin

void setup() {
    Serial.begin(115200);
    pinMode(LED_BUZZER_PIN, OUTPUT);
    pinMode(TRIG_PIN, OUTPUT);
    pinMode(ECHO_PIN, INPUT);

    Serial.println("\n==============================================");
    Serial.println("  SentinLEdge ESP32-S3 Edge AI Firmware Initialized");
    Serial.println("==============================================");

    // Connect to Wi-Fi network
    WiFi.begin(WIFI_SSID, WIFI_PASS);
    Serial.print("Connecting to Wi-Fi");
    while (WiFi.status() != WL_CONNECTED) {
        delay(500);
        Serial.print(".");
    }
    Serial.println("\n[SUCCESS] Connected to Wi-Fi!");
    Serial.print("ESP32 IP Address: ");
    Serial.println(WiFi.localIP());
}

// Helper function to simulate/read ultrasonic water level
float readWaterLevel() {
    digitalWrite(TRIG_PIN, LOW);
    delayMicroseconds(2);
    digitalWrite(TRIG_PIN, HIGH);
    delayMicroseconds(10);
    digitalWrite(TRIG_PIN, LOW);

    long duration = pulseIn(ECHO_PIN, HIGH, 30000); // 30ms timeout
    if (duration == 0) {
        // Fallback to simulated reading if sensor not connected yet
        return 1.8f; 
    }
    float distance_cm = duration * 0.0343 / 2.0;
    // Assuming sensor is mounted 6.0m above riverbed
    float water_level_m = 6.0f - (distance_cm / 100.0f);
    return max(0.2f, water_level_m);
}

void loop() {
    // 1. Read Sensor Values (Replace with physical pin reads when connected)
    float water_level_m = readWaterLevel();
    float rain_1h = 12.5f;       // mm
    float rain_24h = 75.0f;      // mm
    float soil_moisture = 82.0f; // %

    // 2. Execute Offline Edge AI Prediction (Zero Cloud Latency)
    EdgePrediction pred = predict_flood_risk(rain_1h, rain_24h, water_level_m, soil_moisture);

    Serial.println("----------------------------------------------");
    Serial.printf("Sensor Inputs -> WL: %.2fm | Rain24h: %.1fmm | Soil: %.1f%%\n", water_level_m, rain_24h, soil_moisture);
    Serial.printf("Edge AI Output -> Risk Score: %.1f%% | Severity Level: %d\n", pred.risk_score_pct, pred.severity);

    // 3. Autonomous Alarm Control
    if (pred.severity >= WARNING) {
        digitalWrite(LED_BUZZER_PIN, HIGH);
        Serial.println("[ALERT] HIGH FLOOD RISK! Local Alarm Triggered!");
    } else {
        digitalWrite(LED_BUZZER_PIN, LOW);
    }

    // 4. Send Telemetry to FastAPI Backend & Live GIS Dashboard
    if (WiFi.status() == WL_CONNECTED) {
        HTTPClient http;
        http.begin(BACKEND_URL);
        http.addHeader("Content-Type", "application/json");

        String jsonPayload = "{\"node_id\":\"TYPE-B-ESP32-HARDWARE\","
                             "\"rain_1h\":" + String(rain_1h, 1) + ","
                             "\"rain_24h\":" + String(rain_24h, 1) + ","
                             "\"water_level_m\":" + String(water_level_m, 2) + ","
                             "\"soil_moisture_pct\":" + String(soil_moisture, 1) + "}";

        int httpResponseCode = http.POST(jsonPayload);
        if (httpResponseCode > 0) {
            Serial.printf("[HTTP] Backend Sync Success: Code %d\n", httpResponseCode);
        } else {
            Serial.printf("[HTTP] Error syncing with backend: %s\n", http.errorToString(httpResponseCode).c_str());
        }
        http.end();
    }

    delay(10000); // Repeat every 10 seconds
}
