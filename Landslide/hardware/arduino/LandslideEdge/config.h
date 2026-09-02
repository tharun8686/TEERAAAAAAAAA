// ============================================================
// config.h  --  LandslideEdge Hardware & Timing Configuration
// ESP32-S3 N16R8 | Landslide Early Warning Node (Type-A)
// ============================================================
#pragma once

// --- Board ---
#define BOARD_NAME          "ESP32-S3 N16R8"
#define FIRMWARE_VERSION    "1.0.0"
#define NODE_ID             "NODE-LND-TYPE-A"

// --- Serial ---
#define SERIAL_BAUD         115200

// --- I2C Bus (MPU6050) ---
#define PIN_I2C_SDA         8
#define PIN_I2C_SCL         9
#define MPU6050_I2C_ADDR    0x68   // AD0 = GND

// --- Analog Sensors ---
#define PIN_SOIL_MOISTURE   1      // Capacitive Soil Moisture V2.0  AO -> GPIO1
#define PIN_RAIN_SENSOR     2      // LM393 Rain Sensor              AO -> GPIO2

// --- Digital Sensors ---
#define PIN_DHT11           7      // DHT11 DATA -> GPIO7
#define PIN_VIBRATION       4      // SW-420 DO  -> GPIO4

// --- ADC ---
#define ADC_RESOLUTION_BITS 12
#define ADC_MAX_RAW         4095

// --- Soil Moisture Calibration (ADC raw -> VWC) ---
#define SOIL_ADC_DRY        3200
#define SOIL_ADC_WET        1400
#define SOIL_VWC_MIN        0.05f
#define SOIL_VWC_MAX        0.50f

// --- Rain Sensor Calibration (ADC raw -> mm proxy) ---
#define RAIN_ADC_DRY        3200
#define RAIN_ADC_WET         300
#define RAIN_MAX_PROXY_MM   80.0f

// --- DHT11 ---
#define DHT_TYPE            11

// --- MPU6050 ---
#define MPU_ACCEL_RANGE     2      // +/-2g
#define MPU_GYRO_RANGE      250    // +/-250 deg/s

// --- Timing ---
#define INFERENCE_INTERVAL_MS   1000
#define SENSOR_WARMUP_MS        2000

// --- Severity Thresholds ---
#define SEV_CRITICAL_PROB   0.80f
#define SEV_WARNING_PROB    0.55f
#define SEV_WATCH_PROB      0.30f
#define SENSOR_HEALTH_MIN   0.20f
#define SENSOR_HEALTH_PENALTY 0.20f
