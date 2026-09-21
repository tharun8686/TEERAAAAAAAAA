// ============================================================================
// TerraEdge — Multi-Hazard Environmental Sensor Node Firmware (SENDER.ino)
// Compatible with ESP32 / ESP32-S3 + SX1278 LoRa (433MHz / Ra-02)
// 
// Sensors Supported:
//   - BME680 (Temp, Humidity, Barometric Pressure, Gas Resistance) [I2C]
//   - MQ-7 (raw ADC response; NOT ppm, CO, or TVOC) [Analog ADC]
//   - Rain plate (raw wetness response; NOT rainfall in mm) [Analog ADC]
//   - JSN-SR04T Ultrasonic / Analog Water Depth (Water Level) [Pulse / ADC]
//   - Capacitive Soil Moisture Sensor [Analog ADC]
//   - MPU-6050 (3-Axis Accelerometer & Tilt Magnitude) [I2C]
//   - SW-420 (Vibration / Seismic Motion Pulse Counter) [Digital ISR]
//   - IR Optical Flame Sensor (active-low digital input)
//   - Water Quality Probes (pH, TDS ppm, Turbidity NTU) [Analog ADC]
//   - NEO-6M GPS Module (Latitude, Longitude, Altitude) [Hardware UART]
//   - Battery Monitoring (Voltage Divider) [Analog ADC]
// ============================================================================

#include <Arduino.h>
#include <esp_system.h>  // Explicit declaration of esp_random().
#include "hardware_config.h"
#if ENABLE_GPS
#include <TinyGPSPlus.h>
#endif
#include <Wire.h>
#include <SPI.h>
#include <LoRa.h>
#include <ArduinoJson.h>
#include <Adafruit_Sensor.h>
#include <Adafruit_BME680.h>
#include <Adafruit_MPU6050.h>

// Explicit declarations also support tools that compile the sketch as C++.
void parseGPSStream();
void transmitSensorTelemetry();
bool sendPart(JsonDocument &part);

// ============================================================================
// 1. HARDWARE PINOUT CONFIGURATION
// ============================================================================
// Board selection follows the ESP32 target selected in Arduino IDE.
#if CONFIG_IDF_TARGET_ESP32S3
#define BOARD_ESP32_S3
#elif CONFIG_IDF_TARGET_ESP32
#define BOARD_ESP32_DEV
#else
#error "Supported targets are ESP32 and ESP32-S3. Supply a verified pin map for other boards."
#endif

#if defined(BOARD_ESP32_S3)
  // --- I2C Pins ---
  #define SDA_PIN             8
  #define SCL_PIN             9

  // --- SX1278 LoRa SPI & Control Pins ---
  #define LORA_SCK            13
  #define LORA_MISO           12
  #define LORA_MOSI           11
  #define LORA_SS             10
  #define LORA_RST            14
  #define LORA_DIO0           47

  // --- Analog Sensor ADC Pins ---
  #define PIN_MQ7           7     // MQ-7 AO through voltage divider
  #define PIN_RAIN            1     // Rain sensor plate
  #define PIN_WATER           2     // Analog water level probe
  #define PIN_SOIL            3     // Capacitive soil moisture
  #define PIN_PH              4     // Water pH probe
  #define PIN_TDS             5     // Water TDS probe
  #define PIN_TURBIDITY       6     // Water Turbidity probe
  #define PIN_BATTERY         S3_BATTERY_PIN     // Disabled until a free ADC pin is configured

  // --- Digital Sensor Pins ---
  #define PIN_FLAME           15    // IR Flame sensor (Active LOW)
  #define PIN_SW420           16    // SW-420 Vibration sensor

  // --- Ultrasonic Sensor Pins (JSN-SR04T) ---
  #define PIN_US_TRIG         17
  #define PIN_US_ECHO         18

  // --- Hardware UARTs ---
  #define GPS_RX_PIN          S3_GPS_RX_PIN
  #define GPS_TX_PIN          -1    // Receive-only GPS; preserve native USB GPIO19/20

#elif defined(BOARD_ESP32_DEV)
  // Standard ESP32 DevKit V1 (WROOM-32)
  #define SDA_PIN             21
  #define SCL_PIN             22

  #define LORA_SCK            18
  #define LORA_MISO           19
  #define LORA_MOSI           23
  #define LORA_SS             5
  #define LORA_RST            14
  #define LORA_DIO0           2

  #define PIN_MQ7           34
  #define PIN_RAIN            35
  #define PIN_WATER           32
  #define PIN_SOIL            33
  #define PIN_PH              36    // VP
  #define PIN_TDS             39    // VN
  #define PIN_TURBIDITY       25
  #define PIN_BATTERY         26

  #define PIN_FLAME           27
  #define PIN_SW420           13

  #define PIN_US_TRIG         12
  #define PIN_US_ECHO         4

  #define GPS_RX_PIN          16
  #define GPS_TX_PIN          17
#endif

// ============================================================================
// 2. RADIO CONFIGURATION (Single Source of Truth)
// ============================================================================
#define LORA_FREQ             433E6       // 433.0 MHz (SX1278 Ra-02)
#define LORA_BW               125E3       // 125 kHz Bandwidth
#define LORA_SF               7           // Spreading Factor 7
#define LORA_CR               5           // Coding Rate 4/5
#define LORA_TX_POWER         17          // 17 dBm (50 mW)
#define LORA_SYNC_WORD        0x34        // TerraEdge Private Sync Word
#define LORA_CRC_ENABLED      true        // Hardware CRC
#define LORA_TX_INTERVAL_MS   5000        // Normal transmission interval (5 sec)
#define LORA_EMERGENCY_COOLDOWN_MS 2000   // Min interval on active emergency (2 sec)

#define NODE_ID               "TE-001"    // Canonical Node Identifier
#define PACKET_VERSION        4           // Protocol Schema Version

#define BATTERY_DIVIDER_RATIO 2.0f        // 100k + 100k divider
static_assert(!ENABLE_BATTERY || PIN_BATTERY >= 0, "Configure a free battery ADC pin before enabling it");

// ============================================================================
// 3. GLOBAL OBJECTS & STATE
// ============================================================================
Adafruit_BME680   bme;
Adafruit_MPU6050  mpu;
#if ENABLE_GPS
HardwareSerial    GPS_Serial(1);
TinyGPSPlus gps;
static_assert(GPS_RX_PIN >= 0 && GPS_RX_PIN != PIN_US_ECHO, "Assign a free GPS RX pin before enabling GPS");
#endif
uint32_t bootId;
portMUX_TYPE vibrationMux = portMUX_INITIALIZER_UNLOCKED;
volatile uint32_t lastVibrationUs = 0;

struct SensorHealth {
  bool bme680   = false;
  bool mpu6050  = false;
  bool lora     = false;
  bool gps      = false;
} health;

// Interrupt Counters & State
volatile uint32_t vibrationCounter = 0;
volatile bool     emergencyFire    = false;
unsigned long     lastVibResetTime = 0;

unsigned long     lastTxTime       = 0;
uint32_t          seqNumber        = 0;

bool              gpsFixed         = false;

// ============================================================================
// 4. INTERRUPT SERVICE ROUTINES (ISRs)
// ============================================================================
void IRAM_ATTR isrVibration() {
  uint32_t now = micros();
  portENTER_CRITICAL_ISR(&vibrationMux);
  if (now - lastVibrationUs >= VIBRATION_DEBOUNCE_US) {
    vibrationCounter++;
    lastVibrationUs = now;
  }
  portEXIT_CRITICAL_ISR(&vibrationMux);
}

// ============================================================================
// 5. HELPER FUNCTIONS
// ============================================================================
float readUltrasonicDistanceCm() {
  digitalWrite(PIN_US_TRIG, LOW);
  delayMicroseconds(2);
  digitalWrite(PIN_US_TRIG, HIGH);
  delayMicroseconds(10);
  digitalWrite(PIN_US_TRIG, LOW);

  long duration = pulseIn(PIN_US_ECHO, HIGH, 30000); // 30ms timeout (approx 5m range)
  if (duration <= 0) return -1.0f;
  return (duration * 0.0343f) / 2.0f; // Speed of sound = 343 m/s
}

void parseGPSStream() {
  #if ENABLE_GPS
  while (GPS_Serial.available()) gps.encode(GPS_Serial.read());
  gpsFixed = gps.location.isValid() && gps.location.age() < 15000;
  health.gps = gpsFixed;
  #endif
}

// ============================================================================
// 6. SETUP
// ============================================================================
void setup() {
  Serial.begin(115200);
  delay(1000);

  Serial.println(F("\n========================================================"));
  Serial.println(F("    TERRA EDGE — MULTI-HAZARD SENSOR NODE (SENDER)      "));
  Serial.printf ("    Node ID: %s | Packet Version: %d\n", NODE_ID, PACKET_VERSION);
  Serial.println(F("========================================================"));

  // Configure ADC resolution
  analogReadResolution(12);
  analogSetAttenuation(ADC_11db);
  bootId = esp_random();

  // Pin modes for digital/analog sensors
  pinMode(PIN_FLAME, INPUT_PULLUP);
  pinMode(PIN_SW420, INPUT);
  pinMode(PIN_US_TRIG, OUTPUT);
  pinMode(PIN_US_ECHO, INPUT);

  // Attach interrupts for instant response
  if (ENABLE_VIBRATION) attachInterrupt(digitalPinToInterrupt(PIN_SW420), isrVibration, RISING);
  // Flame is sampled each loop; no ISR race with emergency transition detection.
  emergencyFire = ENABLE_FLAME && (digitalRead(PIN_FLAME) == LOW);

  // Initialize I2C Bus
  Wire.begin(SDA_PIN, SCL_PIN);
  Wire.setClock(100000);
  delay(50);

  // 1. Initialize BME680
  Serial.print(F("[INIT] Probing BME680... "));
  if (bme.begin(0x76) || bme.begin(0x77)) {
    health.bme680 = true;
    bme.setTemperatureOversampling(BME680_OS_8X);
    bme.setHumidityOversampling(BME680_OS_2X);
    bme.setPressureOversampling(BME680_OS_4X);
    bme.setIIRFilterSize(BME680_FILTER_SIZE_3);
    bme.setGasHeater(320, 150); // 320°C for 150ms
    Serial.println(F("SUCCESS (I2C 0x76/0x77)"));
  } else {
    Serial.println(F("NOT FOUND: check power, SDA/SCL and address; readings omitted"));
  }

  // 2. Initialize MPU6050
  Serial.print(F("[INIT] Probing MPU6050... "));
  if (mpu.begin(0x68, &Wire) || mpu.begin(0x69, &Wire)) {
    health.mpu6050 = true;
    mpu.setAccelerometerRange(MPU6050_RANGE_8_G);
    mpu.setGyroRange(MPU6050_RANGE_500_DEG);
    mpu.setFilterBandwidth(MPU6050_BAND_21_HZ);
    Serial.println(F("SUCCESS (I2C 0x68/0x69)"));
  } else {
    Serial.println(F("NOT FOUND: tilt omitted"));
  }

  // 3. Initialize GPS UART
  #if ENABLE_GPS
  GPS_Serial.begin(9600, SERIAL_8N1, GPS_RX_PIN, GPS_TX_PIN);
  Serial.println(F("[INIT] GPS UART initialized on 9600 baud."));
  #endif

  // 4. Initialize LoRa SX1278
  Serial.print(F("[INIT] Initializing SX1278 LoRa @ 433MHz... "));
  SPI.begin(LORA_SCK, LORA_MISO, LORA_MOSI, LORA_SS);
  pinMode(LORA_RST, OUTPUT);
  digitalWrite(LORA_RST, HIGH); delay(10);
  digitalWrite(LORA_RST, LOW);  delay(20);
  digitalWrite(LORA_RST, HIGH); delay(20);

  LoRa.setPins(LORA_SS, LORA_RST, LORA_DIO0);

  if (LoRa.begin(LORA_FREQ)) {
    LoRa.setSignalBandwidth(LORA_BW);
    LoRa.setSpreadingFactor(LORA_SF);
    LoRa.setCodingRate4(LORA_CR);
    LoRa.setTxPower(LORA_TX_POWER);
    LoRa.setSyncWord(LORA_SYNC_WORD);
    if (LORA_CRC_ENABLED) LoRa.enableCrc();
    health.lora = true;
    Serial.println(F("SUCCESS"));
    Serial.printf ("       SF=%d | BW=%.0fkHz | CR=4/%d | Sync=0x%02X\n", LORA_SF, LORA_BW/1000.0, LORA_CR, LORA_SYNC_WORD);
  } else {
    Serial.println(F("FAILED! Check SPI wiring & power rails."));
  }

  lastVibResetTime = millis();
  lastTxTime = millis();
  Serial.println(F("=== Sensor Node Active & Ready to Transmit ===\n"));
}

// ============================================================================
// 7. SENSOR ACQUISITION & TRANSMISSION
// ============================================================================
// Each frame is split at field boundaries. A receiver forwards each part unchanged.
// The gateway evaluates ONLY complete frames, never a partial sensor snapshot.
bool sendPart(JsonDocument &part) {
  char buffer[251];
  size_t expected = measureJson(part);
  if (part.overflowed() || expected > 250) {
    Serial.println("[ERROR] Packet capacity exceeded; nothing transmitted");
    return false;
  }
  size_t len = serializeJson(part, buffer, sizeof(buffer));
  Serial.println(buffer);
  if (!health.lora || !LoRa.beginPacket()) return false;
  if (LoRa.write((const uint8_t*)buffer, len) != len) return false;
  return LoRa.endPacket() == 1;
}

float linearCalibration(float value, float x1, float y1, float x2, float y2) {
  if (x1 == x2) return NAN;
  return y1 + (value - x1) * (y2 - y1) / (x2 - x1);
}

void transmitSensorTelemetry() {
  uint32_t now = millis();
  seqNumber++;
  StaticJsonDocument<2048> readings;
  // Failed reads are absent. No synthetic temperature, humidity, location or battery.
  bool bmeOk = health.bme680 && bme.performReading();
  readings["bme_ok"] = bmeOk;
  if (bmeOk && isfinite(bme.temperature) && isfinite(bme.humidity)) {
    readings["t"] = bme.temperature;
    readings["h"] = bme.humidity;
    readings["p"] = bme.pressure / 100.0f;
    readings["gr"] = bme.gas_resistance / 1000.0f;
  }
  if (ENABLE_MQ7) {
    // Fixed 5V module power does not provide a calibrated CO concentration.
    readings["m7"] = analogRead(PIN_MQ7);
    readings["m7_mv"] = analogReadMilliVolts(PIN_MQ7);
  }
  if (ENABLE_RAIN_PLATE) readings["rain_adc"] = analogRead(PIN_RAIN);
  if (ENABLE_WATER_ADC) readings["water_adc"] = analogRead(PIN_WATER);
  if (ENABLE_SOIL) {
    int raw = analogRead(PIN_SOIL);
    readings["soil_adc"] = raw;
    if (SOIL_CALIBRATED) {
      float v = linearCalibration(raw, SOIL_ADC_1, SOIL_VWC_1_PCT, SOIL_ADC_2, SOIL_VWC_2_PCT);
      if (isfinite(v) && v >= 0 && v <= 100) readings["sm"] = v;
    }
  }
  if (ENABLE_PH) {
    float mv = analogReadMilliVolts(PIN_PH);
    readings["ph_mv"] = mv;
    if (PH_CALIBRATED && mv < ADC_USABLE_MAX_MV) {
      float v = linearCalibration(mv, PH_MV_1, PH_VALUE_1, PH_MV_2, PH_VALUE_2);
      if (isfinite(v) && v >= 0 && v <= 14) readings["ph"] = v;
    }
  }
  if (ENABLE_TDS) {
    float mv = analogReadMilliVolts(PIN_TDS);
    readings["tds_mv"] = mv;
    if (TDS_CALIBRATED && mv < ADC_USABLE_MAX_MV) {
      float v = mv * TDS_PPM_PER_MV + TDS_OFFSET_PPM;
      if (isfinite(v) && v >= 0) readings["td"] = v;
    }
  }
  if (ENABLE_TURBIDITY) {
    float mv = analogReadMilliVolts(PIN_TURBIDITY);
    readings["turb_mv"] = mv;
    if (TURBIDITY_CALIBRATED && mv < ADC_USABLE_MAX_MV) {
      float v = mv * TURBIDITY_NTU_PER_MV + TURBIDITY_OFFSET_NTU;
      if (isfinite(v) && v >= 0) readings["tb"] = v;
    }
  }
  if (ENABLE_ULTRASONIC) {
    float distance = readUltrasonicDistanceCm();
    if (distance > 0) {
      readings["ud"] = distance;
      if (WATER_HEIGHT_CALIBRATED && distance <= WATER_REFERENCE_CM)
        readings["wl"] = (WATER_REFERENCE_CM - distance) / 100.0f;
    }
  }
  bool mpuOk = false;
  if (health.mpu6050) {
    sensors_event_t a{}, g{}, temp{};
    mpuOk = mpu.getEvent(&a, &g, &temp);
    float norm = sqrt(a.acceleration.x*a.acceleration.x + a.acceleration.y*a.acceleration.y + a.acceleration.z*a.acceleration.z);
    if (mpuOk && isfinite(norm) && norm > 0.001f) {
      readings["tm"] = acos(constrain(a.acceleration.z/norm, -1.0f, 1.0f)) * 180.0f / PI;
    } else mpuOk = false;
  }
  readings["mpu_ok"] = mpuOk;
  if (ENABLE_VIBRATION) {
    portENTER_CRITICAL(&vibrationMux);
    uint32_t vibrationSampleTime = millis();
    uint32_t pulses = vibrationCounter;
    vibrationCounter = 0;
    portEXIT_CRITICAL(&vibrationMux);
    uint32_t elapsed = vibrationSampleTime - lastVibResetTime;
    if (elapsed) readings["vr"] = pulses * 60000.0f / elapsed;
    lastVibResetTime = vibrationSampleTime;
  }
  if (ENABLE_FLAME) readings["fd"] = digitalRead(PIN_FLAME) == LOW ? 1 : 0;
  if (ENABLE_BATTERY) readings["bv"] = analogReadMilliVolts(PIN_BATTERY) / 1000.0f * BATTERY_DIVIDER_RATIO;
  #if ENABLE_GPS
  if (gpsFixed) {
    readings["lat"] = gps.location.lat();
    readings["lon"] = gps.location.lng();
  }
  #endif
  if (readings.overflowed()) {
    Serial.println("[ERROR] Readings buffer full; frame dropped");
    return;
  }
  // A small, fixed maximum bounds RAM and LoRa traffic. Metadata repeats per part.
  StaticJsonDocument<1536> part;
  part["v"] = 4;
  part["id"] = NODE_ID;
  part["boot"] = bootId;
  part["seq"] = seqNumber;
  part["up"] = now;
  part["part"] = 0;
  JsonObject data = part.createNestedObject("d");
  unsigned index = 0;
  for (JsonPair kv : readings.as<JsonObject>()) {
    data[kv.key()] = kv.value();
    // Reserve bytes for the final marker and growing part index.
    if (measureJson(part) > 230) {
      data.remove(kv.key());
      part["last"] = false;
      if (!sendPart(part)) { Serial.println("[ERROR] LoRa TX failed"); return; }
      delay(30);
      data.clear();
      part.remove("last");
      part["part"] = ++index;
      data[kv.key()] = kv.value();
    }
  }
  part["last"] = true;
  if (!sendPart(part)) Serial.println("[ERROR] LoRa TX failed");
}

// ============================================================================
// 8. MAIN LOOP
// ============================================================================
void loop() {
  unsigned long now = millis();

  // Continuously parse incoming GPS NMEA sentences
  parseGPSStream();

  // Instant Fire Hazard Detection
  bool currentFlame = ENABLE_FLAME && (digitalRead(PIN_FLAME) == LOW);
  if (currentFlame && !emergencyFire) {
    Serial.println(F("\n🚨 [EMERGENCY INTERRUPT] OPTICAL FLAME SENSOR TRIGGERED! 🚨"));
    emergencyFire = true;
    transmitSensorTelemetry(); // Immediately dispatch emergency packet without waiting for timer
    lastTxTime = now;
  } else if (!currentFlame && emergencyFire) {
    emergencyFire = false;
    Serial.println(F("[INFO] Flame cleared. Returning to normal telemetry cycle."));
  }

  // Periodic Telemetry Transmission
  unsigned long interval = emergencyFire ? LORA_EMERGENCY_COOLDOWN_MS : LORA_TX_INTERVAL_MS;
  if (now - lastTxTime >= interval) {
    lastTxTime = now;
    transmitSensorTelemetry();
  }

  delay(20); // Small loop yield for RTOS scheduler
}
