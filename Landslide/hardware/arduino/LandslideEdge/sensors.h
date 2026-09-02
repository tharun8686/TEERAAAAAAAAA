// ============================================================
// sensors.h  --  Sensor driver declarations
// LandslideEdge | ESP32-S3 N16R8
// Sensors: MPU6050, Capacitive Soil V2.0, LM393 Rain, DHT11, SW-420
// ============================================================
#pragma once
#include <Arduino.h>

// --- Raw sensor readings container ---
struct RawSensorData {
    float soil_adc;          // Capacitive Soil Moisture ADC (0-4095)
    float rain_adc;          // Rain Sensor ADC (0-4095)
    float accel_x, accel_y, accel_z;  // MPU6050 acceleration (m/s^2)
    float gyro_x,  gyro_y,  gyro_z;   // MPU6050 gyroscope (deg/s)
    float temperature_c;     // DHT11 temperature (deg C)
    float humidity_pct;      // DHT11 humidity (%)
    float vibration_count;   // SW-420 events per minute
    bool  soil_ok;
    bool  mpu_ok;
    bool  dht_ok;
    bool  vibration_ok;
    bool  rain_ok;
};

// --- Processed 8-feature vector (matches training exactly) ---
struct FeatureVector {
    float soil_moisture_vwc;    // [0] Volumetric Water Content 0.05-0.50
    float soil_moisture_rate;   // [1] VWC derivative per step
    float tilt_magnitude;       // [2] Tilt angle in degrees (0-45)
    float tilt_rate;            // [3] Tilt change per step (deg/step)
    float vibration_rate;       // [4] Vibration events per minute
    float temperature;          // [5] Ambient temperature (deg C)
    float humidity;             // [6] Relative humidity (%)
    float rainfall_24h;         // [7] 24h rainfall proxy from rain sensor (mm)
    float raw_array[8];         // Flat array fed directly to the model
};

// --- Public API ---
void sensors_init();
bool sensors_read(RawSensorData& raw);
void features_compute(const RawSensorData& raw,
                       FeatureVector& feat,
                       const FeatureVector& prev);
void sensors_print_raw(const RawSensorData& raw);
void features_print(const FeatureVector& feat);
