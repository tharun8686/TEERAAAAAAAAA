// ============================================================
// TerraEdge Phase 3 — Type A Sensor Node Firmware
// ESP32-S3 + BME680 + SDS011 + MQ-135 + Rain + Water +
//           JSN-SR04T + Soil + MPU6050 + SW420 + IR Flame +
//           pH + TDS + Turbidity + NEO-6M GPS + SX1278 LoRa
// ============================================================
// Key design principles:
//   - Non-blocking (millis-based, no delay() in main loop)
//   - Per-sensor availability flags
//   - Canonical Phase 2 field names in JSON packet
//   - Compact JSON serialization for LoRa
//   - Sequence number for duplicate / gap detection
//   - Optional ACK with retry
// ============================================================

#include <Arduino.h>
#include <Wire.h>
#include <SPI.h>
#include <LoRa.h>
#include <ArduinoJson.h>
#include <Adafruit_Sensor.h>
#include <Adafruit_BME680.h>
#include <Adafruit_MPU6050.h>

#include "lora_config.h"

// ---- I2C ----------------------------------------------------------------
#define SDA_PIN   8
#define SCL_PIN   9

// ---- SDS011 UART --------------------------------------------------------
// SDS011 uses 9600 baud UART
#define SDS011_RX   18
#define SDS011_TX   17
HardwareSerial SDS011_Serial(2);  // Serial2

// ---- GPS (NEO-6M) UART --------------------------------------------------
#define GPS_RX    4
#define GPS_TX    5
HardwareSerial GPS_Serial(1);     // Serial1

// ---- JSN-SR04T Ultrasonic -----------------------------------------------
#define ULTRASONIC_TRIG  6
#define ULTRASONIC_ECHO  16
#define ULTRASONIC_REF_CM  300.0f  // Reference height: sensor to channel floor in cm

// ---- ADC Sensors --------------------------------------------------------
#define MQ135_PIN   7      // MQ-135 (replaces old MQ2_PIN — same GPIO)
#define RAIN_PIN    1
#define WATER_PIN   2
#define SOIL_PIN    3
#define PH_PIN      34
#define TDS_PIN     35
#define TURBIDITY_PIN 36
#define BATTERY_PIN 0      // Battery ADC (through voltage divider)

// ---- Digital Sensors ----------------------------------------------------
#define FLAME_PIN   15     // IR flame sensor (LOW = fire)
#define SW420_PIN   21     // SW-420 vibration sensor

// ---- Calibration --------------------------------------------------------
const int RAIN_DRY_ADC    = 3800;
const int RAIN_WET_ADC    = 1200;
const int WATER_EMPTY_ADC = 300;
const int WATER_FULL_ADC  = 3500;
const int SOIL_DRY_ADC    = 3600;
const int SOIL_WET_ADC    = 1800;
const float BATTERY_VOLTAGE_FULL  = 4.2f;
const float BATTERY_VOLTAGE_EMPTY = 3.2f;
const float BATTERY_ADC_SCALE     = 3.3f / 4095.0f;
const float BATTERY_DIVIDER_RATIO = 2.0f;   // R1=R2 voltage divider

// ---- Sensor status flags ------------------------------------------------
struct SensorStatus {
  bool bme680    = false;
  bool sds011    = false;
  bool mq135     = true;   // always try (ADC)
  bool rain      = true;
  bool water     = true;
  bool ultrasonic = true;
  bool soil      = true;
  bool mpu6050   = false;  // Phase 3 placeholder — use tilt from ADC for now
  bool sw420     = true;
  bool flame     = true;
  bool ph        = true;
  bool tds       = true;
  bool turbidity = true;
  bool gps       = false;
  bool lora      = false;
} sensors;

// ---- Objects ------------------------------------------------------------
Adafruit_BME680 bme;
Adafruit_MPU6050 mpu;

// ---- State --------------------------------------------------------------
unsigned long lastTxTime   = 0;
uint32_t      seqNumber    = 0;
bool          fireActive   = false;
float         gpsLat       = 0.0f;
float         gpsLon       = 0.0f;
bool          gpsFix       = false;
uint8_t       gpsSats      = 0;

// ---- SDS011 readings (updated via UART parsing) -------------------------
float sds011_pm25 = 0.0f;
float sds011_pm10 = 0.0f;
bool  sds011_valid = false;

// ---- Vibration counter (ISR incremented) --------------------------------
volatile uint32_t vibCount = 0;
unsigned long     lastVibReset = 0;
float             vibRate  = 0.0f;   // pulses per minute

// ============================================================
// SETUP
// ============================================================
void setup() {
  Serial.begin(115200);
  delay(500);
  Serial.println("\n=== TerraEdge Type-A Node v3 ===");

  // ADC
  analogReadResolution(12);

  // I2C
  Wire.begin(SDA_PIN, SCL_PIN);
  Wire.setClock(100000);
  delay(50);

  // MPU6050
  if (mpu.begin()) {
    sensors.mpu6050 = true;
    mpu.setAccelerometerRange(MPU6050_RANGE_8_G);
    mpu.setGyroRange(MPU6050_RANGE_500_DEG);
    mpu.setFilterBandwidth(MPU6050_BAND_21_HZ);
    Serial.println("[OK] MPU6050");
  } else {
    Serial.println("[WARN] MPU6050 not found");
  }

  // BME680
  if (bme.begin(0x76, &Wire) || bme.begin(0x77, &Wire)) {
    sensors.bme680 = true;
    bme.setTemperatureOversampling(BME680_OS_8X);
    bme.setHumidityOversampling(BME680_OS_2X);
    bme.setPressureOversampling(BME680_OS_4X);
    bme.setIIRFilterSize(BME680_FILTER_SIZE_3);
    bme.setGasHeater(320, 150);
    Serial.println("[OK] BME680");
  } else {
    Serial.println("[WARN] BME680 not found");
  }

  // SDS011 (9600 baud UART)
  SDS011_Serial.begin(9600, SERIAL_8N1, SDS011_RX, SDS011_TX);
  sensors.sds011 = true;   // Assume present; validated on first read
  Serial.println("[OK] SDS011 UART on Serial2");

  // GPS (9600 baud UART)
  GPS_Serial.begin(9600, SERIAL_8N1, GPS_RX, GPS_TX);
  sensors.gps = true;
  Serial.println("[OK] GPS UART on Serial1");

  // JSN-SR04T
  pinMode(ULTRASONIC_TRIG, OUTPUT);
  pinMode(ULTRASONIC_ECHO, INPUT);
  Serial.println("[OK] JSN-SR04T ultrasonic");

  // Flame + SW420
  pinMode(FLAME_PIN, INPUT);
  pinMode(SW420_PIN, INPUT);
  // Vibration ISR
  attachInterrupt(digitalPinToInterrupt(SW420_PIN), []{ vibCount++; }, RISING);

  // LoRa SX1278
  SPI.begin(LORA_SCK, LORA_MISO, LORA_MOSI, LORA_SS);
  pinMode(LORA_RST, OUTPUT);
  digitalWrite(LORA_RST, HIGH); delay(10);
  digitalWrite(LORA_RST, LOW);  delay(20);
  digitalWrite(LORA_RST, HIGH); delay(20);
  LoRa.setPins(LORA_SS, LORA_RST, LORA_DIO0);

  if (LoRa.begin(LORA_FREQ)) {
    // Set all radio parameters explicitly — must match gateway config
    LoRa.setSignalBandwidth(LORA_BW);
    LoRa.setSpreadingFactor(LORA_SF);
    LoRa.setCodingRate4(LORA_CR);
    LoRa.setTxPower(LORA_TX_POWER);
    LoRa.setSyncWord(LORA_SYNC_WORD);
    if (LORA_CRC_ENABLED) LoRa.enableCrc();
    sensors.lora = true;
    Serial.println("[OK] SX1278 LoRa @ 433 MHz, SF7, BW125, CR4/5, sync=0x34");
  } else {
    Serial.println("[ERROR] SX1278 LoRa FAILED");
  }

  Serial.println("=== System Ready ===\n");
  lastTxTime    = millis();
  lastVibReset  = millis();
}

// ============================================================
// LOOP
// ============================================================
void loop() {
  unsigned long now = millis();

  // --- Instant flame check (no delay) ---
  bool flameDetected = (digitalRead(FLAME_PIN) == LOW);
  if (flameDetected && !fireActive) {
    Serial.println("[ALERT] FIRE DETECTED");
    fireActive = true;
  } else if (!flameDetected && fireActive) {
    Serial.println("[INFO] Fire hazard cleared");
    fireActive = false;
  }

  // --- Vibration rate (pulses per minute) ---
  if (now - lastVibReset >= 60000) {
    vibRate = (float)vibCount;
    vibCount = 0;
    lastVibReset = now;
  }

  // --- Parse SDS011 UART (async) ---
  parseSDS011();

  // --- Parse GPS UART (async) ---
  parseGPS();

  // --- Periodic LoRa transmission ---
  if (now - lastTxTime >= LORA_TX_INTERVAL_MS) {
    lastTxTime = now;
    transmitTelemetry();
  }
}

// ============================================================
// SENSOR READERS
// ============================================================

float readUltrasonicDistance() {
  // JSN-SR04T: trigger 10µs pulse, measure echo duration
  digitalWrite(ULTRASONIC_TRIG, LOW);  delayMicroseconds(2);
  digitalWrite(ULTRASONIC_TRIG, HIGH); delayMicroseconds(10);
  digitalWrite(ULTRASONIC_TRIG, LOW);
  long duration = pulseIn(ULTRASONIC_ECHO, HIGH, 30000);  // 30ms timeout
  if (duration == 0) return -1.0f;   // no echo = out of range
  return duration * 0.0343f / 2.0f;  // cm
}

float readBatteryPct() {
  int raw = analogRead(BATTERY_PIN);
  float voltage = raw * BATTERY_ADC_SCALE * BATTERY_DIVIDER_RATIO;
  float pct = (voltage - BATTERY_VOLTAGE_EMPTY) /
              (BATTERY_VOLTAGE_FULL - BATTERY_VOLTAGE_EMPTY) * 100.0f;
  return constrain(pct, 0.0f, 100.0f);
}

int toPercent(int raw, int low, int high) {
  long pct = map(raw, low, high, 0, 100);
  return constrain((int)pct, 0, 100);
}

// SDS011 UART parser (binary protocol: 10-byte frames, start 0xAA)
void parseSDS011() {
  static uint8_t buf[10];
  static uint8_t idx = 0;

  while (SDS011_Serial.available()) {
    uint8_t b = SDS011_Serial.read();
    if (idx == 0 && b != 0xAA) continue;  // wait for start byte
    buf[idx++] = b;
    if (idx == 10) {
      idx = 0;
      if (buf[9] == 0xAB) {  // end byte
        uint8_t checksum = 0;
        for (int i = 2; i < 8; i++) checksum += buf[i];
        if (checksum == buf[8]) {
          sds011_pm25 = ((buf[3] << 8) | buf[2]) / 10.0f;
          sds011_pm10 = ((buf[5] << 8) | buf[4]) / 10.0f;
          sds011_valid = true;
        }
      }
    }
  }
}

// GPS NMEA parser (minimal — extracts lat/lon from GPRMC)
void parseGPS() {
  while (GPS_Serial.available()) {
    char c = GPS_Serial.read();
    static char line[100];
    static int lineIdx = 0;
    if (c == '\n' || lineIdx >= 99) {
      line[lineIdx] = '\0';
      lineIdx = 0;
      parseNMEA(line);
    } else {
      line[lineIdx++] = c;
    }
  }
}

void parseNMEA(const char* nmea) {
  // Only handle GPRMC sentences
  if (strncmp(nmea, "$GPRMC", 6) != 0) return;

  char buf[100];
  strncpy(buf, nmea, 99);
  char* token = strtok(buf, ",");
  int field = 0;
  char status = 'V';
  char latStr[15] = "", latDir = 'N';
  char lonStr[15] = "", lonDir = 'E';

  while (token != nullptr) {
    switch (field) {
      case 2: status = token[0]; break;
      case 3: strncpy(latStr, token, 14); break;
      case 4: latDir = token[0]; break;
      case 5: strncpy(lonStr, token, 14); break;
      case 6: lonDir = token[0]; break;
    }
    token = strtok(nullptr, ",");
    field++;
  }

  if (status == 'A' && strlen(latStr) > 0) {
    // NMEA format: DDDMM.MMMM -> decimal degrees
    float rawLat = atof(latStr);
    int latDeg = (int)(rawLat / 100);
    float latMin = rawLat - latDeg * 100;
    gpsLat = latDeg + latMin / 60.0f;
    if (latDir == 'S') gpsLat = -gpsLat;

    float rawLon = atof(lonStr);
    int lonDeg = (int)(rawLon / 100);
    float lonMin = rawLon - lonDeg * 100;
    gpsLon = lonDeg + lonMin / 60.0f;
    if (lonDir == 'W') gpsLon = -gpsLon;

    gpsFix = true;
  }
}

// ============================================================
// TELEMETRY PACKET BUILDER + LORA TX
// ============================================================
void transmitTelemetry() {
  seqNumber++;

  // --- Read all sensors ---
  float temp = -999, hum = -999, press = -999, gasRes = -999;
  if (sensors.bme680 && bme.performReading()) {
    temp   = bme.temperature;
    hum    = bme.humidity;
    press  = bme.pressure / 100.0f;
    gasRes = bme.gas_resistance / 1000.0f;
    
    // Sanity checks
    if (temp < -40.0f || temp > 85.0f) temp = -999;
    if (hum < 0.0f || hum > 100.0f) hum = -999;
    if (press < 300.0f || press > 1200.0f) press = -999;
  }

  int mq135Raw = analogRead(MQ135_PIN);
  int rainRaw  = analogRead(RAIN_PIN);
  int waterRaw = analogRead(WATER_PIN);
  int soilRaw  = analogRead(SOIL_PIN);
  int phRaw    = analogRead(PH_PIN);
  int tdsRaw   = analogRead(TDS_PIN);
  int turbRaw  = analogRead(TURBIDITY_PIN);

  float ultrasonicDist = readUltrasonicDistance();
  float waterLevelM = -1.0f;
  if (ultrasonicDist > 0 && ultrasonicDist <= ULTRASONIC_REF_CM) {
    waterLevelM = (ULTRASONIC_REF_CM - ultrasonicDist) / 100.0f;
  }

  float soilPct  = toPercent(soilRaw, SOIL_DRY_ADC, SOIL_WET_ADC);
  float rainPct  = toPercent(rainRaw, RAIN_DRY_ADC, RAIN_WET_ADC);
  float battPct  = readBatteryPct();

  // pH bounds 0-14
  float phVoltage = (phRaw / 4095.0f) * 3.3f;
  float phValue   = 7.0f - ((phVoltage - 2.5f) / 0.18f);
  if (phValue < 0.0f) phValue = 0.0f;
  if (phValue > 14.0f) phValue = 14.0f;

  float tdsVoltage = (tdsRaw / 4095.0f) * 3.3f;
  float tdsPpm     = (tdsVoltage * tdsVoltage / 3.3f / 3.3f) * 1000.0f;
  if (tdsPpm < 0.0f) tdsPpm = 0.0f;

  float turbVoltage = (turbRaw / 4095.0f) * 3.3f;
  float turbNTU     = max(0.0f, (3300.0f - turbVoltage * 1000.0f) / 10.0f);
  
  float tiltMag = -999;
  if (sensors.mpu6050) {
    sensors_event_t a, g, temp_mpu;
    mpu.getEvent(&a, &g, &temp_mpu);
    // Simple tilt magnitude: sqrt(ax^2 + ay^2 + az^2) in m/s^2.
    // 1G ~ 9.8 m/s^2. Deviation from 9.8 can be mapped to degrees or just sent as magnitude.
    // Let's send the raw magnitude for now, gateway expects degrees, 
    // so let's calculate tilt angle from vertical assuming Z is up:
    // angle = acos(az / sqrt(ax^2 + ay^2 + az^2)) * 180 / PI
    float norm = sqrt(a.acceleration.x * a.acceleration.x + 
                      a.acceleration.y * a.acceleration.y + 
                      a.acceleration.z * a.acceleration.z);
    if (norm > 0) {
      tiltMag = acos(a.acceleration.z / norm) * 180.0 / PI;
    }
  }

  // Build sensor flags bitmask
  uint16_t sf = 0;
  if (sensors.bme680)    sf |= (1 << 0);
  if (sensors.sds011 && sds011_valid) sf |= (1 << 1);
  sf |= (1 << 2);   // MQ-135 always present (ADC)
  sf |= (1 << 3);   // Rain
  sf |= (1 << 4);   // Water level
  if (ultrasonicDist > 0) sf |= (1 << 5);  // Ultrasonic valid
  sf |= (1 << 6);   // Soil
  if (sensors.mpu6050 && tiltMag != -999) sf |= (1 << 7); // MPU6050
  sf |= (1 << 8);   // SW420
  sf |= (1 << 9);   // Flame
  sf |= (1 << 10);  // pH
  sf |= (1 << 11);  // TDS
  sf |= (1 << 12);  // Turbidity
  if (gpsFix) sf |= (1 << 13);
  sf |= (1 << 14);  // Battery

  // Build compact JSON packet (short keys — MUST match gateway/lora/packet.py)
  StaticJsonDocument<512> doc;
  doc["v"]   = PACKET_VERSION;
  doc["id"]  = "TE-001";        // TODO: read from EEPROM / config
  doc["seq"] = seqNumber;
  doc["ts"]  = "";               // Gateway fills if empty (no RTC in prototype)
  doc["sf"]  = sf;

  if (gpsFix)         { doc["lat"] = gpsLat; doc["lon"] = gpsLon; }
  doc["bat"] = (int)battPct;

  if (sensors.bme680 && temp != -999) doc["t"] = round2(temp);
  if (sensors.bme680 && hum != -999) doc["h"] = round2(hum);
  if (sensors.bme680 && press != -999) doc["p"] = round2(press);
  if (sensors.bme680 && gasRes != -999) doc["gr"] = round2(gasRes);

  if (sensors.sds011 && sds011_valid) {
    if (sds011_pm25 >= 0) doc["p25"] = round2(sds011_pm25);
    if (sds011_pm10 >= 0) doc["p10"] = round2(sds011_pm10);
  }

  if (mq135Raw >= 0) doc["mq"] = mq135Raw;
  if (rainPct >= 0) doc["rm"] = round2(rainPct);
  if (waterLevelM >= 0) doc["wl"] = round2(waterLevelM);
  if (ultrasonicDist > 0) doc["ud"] = round2(ultrasonicDist);
  if (soilPct >= 0) doc["sm"] = round2(soilPct);
  if (vibRate >= 0) doc["vr"] = round2(vibRate);
  doc["fd"] = fireActive ? 1 : 0;
  if (phValue >= 0) doc["ph"] = round2(phValue);
  if (tdsPpm >= 0) doc["td"] = round2(tdsPpm);
  if (turbNTU >= 0) doc["tb"] = round2(turbNTU);
  if (sensors.mpu6050 && tiltMag != -999) doc["tm"] = round2(tiltMag);

  char jsonBuf[256];
  size_t jsonLen = serializeJson(doc, jsonBuf, sizeof(jsonBuf));

  // --- Serial debug ---
  Serial.printf("\n[TX] Seq=%u  Size=%u bytes\n", seqNumber, jsonLen);
  Serial.println(jsonBuf);

  // --- Transmit over LoRa ---
  if (!sensors.lora) {
    Serial.println("[WARN] LoRa not ready — skipping TX");
    return;
  }

  int retries = 0;
  bool acked  = false;

  do {
    LoRa.beginPacket();
    LoRa.write((const uint8_t*)jsonBuf, jsonLen);
    LoRa.endPacket();
    Serial.printf("[LoRa] TX seq=%u (attempt %d)\n", seqNumber, retries + 1);

#if LORA_ACK_ENABLED
    // Switch to receive mode and wait for ACK
    LoRa.receive();
    unsigned long ackDeadline = millis() + LORA_ACK_TIMEOUT_MS;
    while (millis() < ackDeadline) {
      int pktSize = LoRa.parsePacket();
      if (pktSize > 0) {
        String ackStr = "";
        while (LoRa.available()) ackStr += (char)LoRa.read();
        if (ackStr.indexOf(String(seqNumber)) >= 0) {
          Serial.printf("[LoRa] ACK received for seq=%u\n", seqNumber);
          acked = true;
          break;
        }
      }
      delay(10);
    }
    if (acked) break;
    Serial.printf("[LoRa] No ACK — retry %d/%d\n", retries + 1, LORA_RETRIES);
    retries++;
#else
    acked = true;  // No ACK mode — treat single TX as success
    break;
#endif
  } while (retries <= LORA_RETRIES);

  if (!acked) {
    Serial.println("[LoRa] All retries exhausted — packet FAILED");
  }
}

inline float round2(float v) {
  return (float)((int)(v * 100 + 0.5f)) / 100.0f;
}
