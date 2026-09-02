// ============================================================
// sensors.cpp  --  Sensor driver implementation
// LandslideEdge | ESP32-S3 N16R8
// ============================================================
#include "sensors.h"
#include "config.h"
#include <Wire.h>
#include <DHT.h>
#include <math.h>

// ---- MPU6050 register map ----
#define MPU_PWR_MGMT_1   0x6B
#define MPU_ACCEL_CONFIG 0x1C
#define MPU_GYRO_CONFIG  0x1B
#define MPU_ACCEL_XOUT_H 0x3B
#define MPU_GYRO_XOUT_H  0x43

// Scale factors for +/-2g, +/-250 deg/s
static const float ACCEL_SCALE_G = 16384.0f;  // LSB per g
static const float GYRO_SCALE    = 131.0f;    // LSB per deg/s
static const float GRAVITY_MS2   = 9.80665f;

// DHT instance
static DHT dht_sensor(PIN_DHT11, DHT_TYPE);

// Interrupt-driven vibration counter
static volatile uint32_t g_vib_count    = 0;
static uint32_t           g_vib_ts_ms   = 0;

static void IRAM_ATTR vib_isr_handler() {
    g_vib_count++;
}

// ---- MPU6050 helpers ----
static bool mpu_write(uint8_t reg, uint8_t val) {
    Wire.beginTransmission(MPU6050_I2C_ADDR);
    Wire.write(reg);
    Wire.write(val);
    return (Wire.endTransmission() == 0);
}

static bool mpu_read_6axis(float& ax, float& ay, float& az,
                             float& gx, float& gy, float& gz) {
    Wire.beginTransmission(MPU6050_I2C_ADDR);
    Wire.write(MPU_ACCEL_XOUT_H);
    if (Wire.endTransmission(false) != 0) return false;
    if (Wire.requestFrom((uint8_t)MPU6050_I2C_ADDR, (uint8_t)14) != 14) return false;
    int16_t raw_ax = (Wire.read() << 8) | Wire.read();
    int16_t raw_ay = (Wire.read() << 8) | Wire.read();
    int16_t raw_az = (Wire.read() << 8) | Wire.read();
    Wire.read(); Wire.read();  // temperature bytes (ignored)
    int16_t raw_gx = (Wire.read() << 8) | Wire.read();
    int16_t raw_gy = (Wire.read() << 8) | Wire.read();
    int16_t raw_gz = (Wire.read() << 8) | Wire.read();
    ax = (raw_ax / ACCEL_SCALE_G) * GRAVITY_MS2;
    ay = (raw_ay / ACCEL_SCALE_G) * GRAVITY_MS2;
    az = (raw_az / ACCEL_SCALE_G) * GRAVITY_MS2;
    gx = raw_gx / GYRO_SCALE;
    gy = raw_gy / GYRO_SCALE;
    gz = raw_gz / GYRO_SCALE;
    return true;
}

// ---- Public API ----
void sensors_init() {
    analogReadResolution(ADC_RESOLUTION_BITS);

    // I2C
    Wire.begin(PIN_I2C_SDA, PIN_I2C_SCL);
    Wire.setClock(400000UL);

    // MPU6050: wake up, set +/-2g, +/-250deg/s
    delay(200);
    mpu_write(MPU_PWR_MGMT_1,   0x00);
    delay(100);
    mpu_write(MPU_ACCEL_CONFIG, 0x00);
    mpu_write(MPU_GYRO_CONFIG,  0x00);

    // DHT11
    dht_sensor.begin();

    // SW-420 vibration (interrupt on rising edge)
    pinMode(PIN_VIBRATION, INPUT);
    attachInterrupt(digitalPinToInterrupt(PIN_VIBRATION), vib_isr_handler, RISING);
    g_vib_ts_ms = millis();

    delay(SENSOR_WARMUP_MS);
    Serial.println("[sensors] All sensors initialised.");
}

bool sensors_read(RawSensorData& raw) {
    bool all_ok = true;

    // --- Soil Moisture ADC ---
    raw.soil_adc = (float)analogRead(PIN_SOIL_MOISTURE);
    raw.soil_ok  = (raw.soil_adc > 100 && raw.soil_adc < 4090);
    if (!raw.soil_ok) all_ok = false;

    // --- Rain Sensor ADC ---
    raw.rain_adc = (float)analogRead(PIN_RAIN_SENSOR);
    raw.rain_ok  = (raw.rain_adc > 50 && raw.rain_adc < 4090);
    if (!raw.rain_ok) all_ok = false;

    // --- MPU6050 ---
    raw.mpu_ok = mpu_read_6axis(raw.accel_x, raw.accel_y, raw.accel_z,
                                  raw.gyro_x,  raw.gyro_y,  raw.gyro_z);
    if (!raw.mpu_ok) {
        raw.accel_x = raw.accel_y = raw.gyro_x = raw.gyro_y = raw.gyro_z = 0.0f;
        raw.accel_z = GRAVITY_MS2;  // assume upright
        all_ok = false;
    }

    // --- DHT11 ---
    float h = dht_sensor.readHumidity();
    float t = dht_sensor.readTemperature();
    if (!isnan(h) && !isnan(t) && h >= 0.0f && h <= 100.0f && t >= -40.0f && t <= 80.0f) {
        raw.humidity_pct  = h;
        raw.temperature_c = t;
        raw.dht_ok        = true;
    } else {
        // Use training-set mean as fallback (prevents false CRITICAL)
        raw.humidity_pct  = 64.349f;
        raw.temperature_c = 22.508f;
        raw.dht_ok        = false;
        all_ok            = false;
    }

    // --- SW-420 Vibration (interrupt-counted) ---
    noInterrupts();
    uint32_t cnt   = g_vib_count;
    g_vib_count    = 0;
    interrupts();
    uint32_t elapsed_ms = millis() - g_vib_ts_ms;
    g_vib_ts_ms         = millis();
    raw.vibration_count = (elapsed_ms > 0)
        ? (cnt * 60000.0f / (float)elapsed_ms)
        : 0.0f;
    raw.vibration_ok = true;

    return all_ok;
}

// ---- Feature engineering (mirrors training pipeline exactly) ----
// Reference: Landslide/src/training/train_final_landslide_model.py
//
// Training synthesized physical proxy variables from Cleveland dataset:
//   tilt_magnitude = (displacement_rate.abs() * 12.0 + 2.5).clip(1.0, 45.0)
//   tilt_rate      = tilt_magnitude.diff()
//   vibration_rate = (displacement_acceleration.abs() * 50.0 + 1.0).clip(0, 100)
//
// On real ESP32-S3 hardware we derive these from physical sensors:
//   tilt_magnitude = arccos(az/|a|) in degrees  (MPU6050 tilt from vertical)
//   tilt_rate      = current - previous tilt_magnitude
//   vibration_rate = SW-420 interrupt count/min
//
// StandardScaler is applied inside model_rf.h (rf_scale_features)
// No additional preprocessing is needed here.

void features_compute(const RawSensorData& raw,
                       FeatureVector& feat,
                       const FeatureVector& prev) {
    // [0] Soil Moisture VWC
    // Capacitive sensor: HIGH ADC = dry, LOW ADC = wet (inverted)
    float sm_frac = constrain(
        (float)(SOIL_ADC_DRY - raw.soil_adc) / (float)(SOIL_ADC_DRY - SOIL_ADC_WET),
        0.0f, 1.0f);
    feat.soil_moisture_vwc = SOIL_VWC_MIN + sm_frac * (SOIL_VWC_MAX - SOIL_VWC_MIN);
    if (!raw.soil_ok) feat.soil_moisture_vwc = 0.2426f;  // training mean

    // [1] Soil Moisture Rate (per-step VWC derivative)
    feat.soil_moisture_rate = feat.soil_moisture_vwc - prev.soil_moisture_vwc;

    // [2] Tilt Magnitude from MPU6050 (degrees, 0-45)
    if (raw.mpu_ok) {
        float ax = raw.accel_x, ay = raw.accel_y, az = raw.accel_z;
        float mag = sqrtf(ax*ax + ay*ay + az*az);
        if (mag > 0.05f) {
            float cosine  = constrain(az / mag, -1.0f, 1.0f);
            float tilt_r  = acosf(cosine);
            feat.tilt_magnitude = constrain(tilt_r * 57.29578f, 1.0f, 45.0f);
        } else {
            feat.tilt_magnitude = 2.6066f;  // training mean
        }
    } else {
        feat.tilt_magnitude = 2.6066f;
    }

    // [3] Tilt Rate (deg/step)
    feat.tilt_rate = feat.tilt_magnitude - prev.tilt_magnitude;

    // [4] Vibration Rate (events per minute)
    feat.vibration_rate = constrain(raw.vibration_count, 0.0f, 100.0f);

    // [5] Temperature
    feat.temperature = raw.dht_ok ? raw.temperature_c : 22.508f;

    // [6] Humidity
    feat.humidity = raw.dht_ok ? raw.humidity_pct : 64.349f;

    // [7] Rainfall 24h proxy (linear map from rain sensor ADC)
    float rain_frac = constrain(
        (float)(RAIN_ADC_DRY - raw.rain_adc) / (float)(RAIN_ADC_DRY - RAIN_ADC_WET),
        0.0f, 1.0f);
    feat.rainfall_24h = rain_frac * RAIN_MAX_PROXY_MM;
    if (!raw.rain_ok) feat.rainfall_24h = 3.2525f;  // training mean

    // Pack flat array for model input
    feat.raw_array[0] = feat.soil_moisture_vwc;
    feat.raw_array[1] = feat.soil_moisture_rate;
    feat.raw_array[2] = feat.tilt_magnitude;
    feat.raw_array[3] = feat.tilt_rate;
    feat.raw_array[4] = feat.vibration_rate;
    feat.raw_array[5] = feat.temperature;
    feat.raw_array[6] = feat.humidity;
    feat.raw_array[7] = feat.rainfall_24h;
}

void sensors_print_raw(const RawSensorData& raw) {
    Serial.println("=== RAW SENSOR READINGS ===");
    Serial.printf("  Soil Moisture ADC : %.0f  [%s]\n",
                  raw.soil_adc, raw.soil_ok ? "OK" : "FAIL");
    Serial.printf("  Rain Sensor ADC   : %.0f  [%s]\n",
                  raw.rain_adc, raw.rain_ok ? "OK" : "FAIL");
    Serial.printf("  MPU6050 Accel     : X=%.3f Y=%.3f Z=%.3f m/s2  [%s]\n",
                  raw.accel_x, raw.accel_y, raw.accel_z,
                  raw.mpu_ok ? "OK" : "FAIL");
    Serial.printf("  MPU6050 Gyro      : X=%.2f Y=%.2f Z=%.2f deg/s\n",
                  raw.gyro_x, raw.gyro_y, raw.gyro_z);
    Serial.printf("  DHT11             : T=%.1f C  H=%.1f %%  [%s]\n",
                  raw.temperature_c, raw.humidity_pct,
                  raw.dht_ok ? "OK" : "FAIL");
    Serial.printf("  SW-420 Vibration  : %.1f events/min\n",
                  raw.vibration_count);
}

void features_print(const FeatureVector& feat) {
    Serial.println("=== PROCESSED FEATURE VECTOR ===");
    Serial.printf("  [0] soil_moisture_vwc  : %.5f\n",  feat.soil_moisture_vwc);
    Serial.printf("  [1] soil_moisture_rate : %.6f\n",  feat.soil_moisture_rate);
    Serial.printf("  [2] tilt_magnitude     : %.4f deg\n", feat.tilt_magnitude);
    Serial.printf("  [3] tilt_rate          : %.4f deg/step\n", feat.tilt_rate);
    Serial.printf("  [4] vibration_rate     : %.2f events/min\n", feat.vibration_rate);
    Serial.printf("  [5] temperature        : %.2f C\n",  feat.temperature);
    Serial.printf("  [6] humidity           : %.2f %%\n", feat.humidity);
    Serial.printf("  [7] rainfall_24h       : %.2f mm (proxy)\n", feat.rainfall_24h);
}
