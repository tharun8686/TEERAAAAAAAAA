// ============================================================================
// TerraEdge — Multi-Hazard Environmental Sensor Node Firmware (SENDER.ino)
// Compatible with ESP32 / ESP32-S3 + SX1278 LoRa (433MHz / Ra-02)
// 
// Sensors Supported:
//   - BME680 (Temp, Humidity, Barometric Pressure, Gas Resistance) [I2C]
//   - MQ-135 / MQ-2 (Smoke, VOCs, Hazardous Gases, CO) [Analog ADC]
//   - Rain Sensor (Rainfall Intensity / Surface Wetness) [Analog ADC]
//   - JSN-SR04T Ultrasonic / Analog Water Depth (Water Level) [Pulse / ADC]
//   - Capacitive Soil Moisture Sensor [Analog ADC]
//   - MPU-6050 (3-Axis Accelerometer & Tilt Magnitude) [I2C]
//   - SW-420 (Vibration / Seismic Motion Pulse Counter) [Digital ISR]
//   - IR Optical Flame Sensor (Instant Fire Detection) [Digital Interrupt]
//   - Water Quality Probes (pH, TDS ppm, Turbidity NTU) [Analog ADC]
//   - NEO-6M GPS Module (Latitude, Longitude, Altitude) [Hardware UART]
//   - Battery Monitoring (Voltage Divider) [Analog ADC]
// ============================================================================

#include <Arduino.h>
#include <Wire.h>
#include <SPI.h>
#include <LoRa.h>
#include <ArduinoJson.h>
#include <Adafruit_Sensor.h>
#include <Adafruit_BME680.h>
#include <Adafruit_MPU6050.h>

// ============================================================================
// 1. HARDWARE PINOUT CONFIGURATION
// ============================================================================
// Uncomment ONE of the following board profiles:
#define BOARD_ESP32_S3
// #define BOARD_ESP32_DEV

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
  #define PIN_MQ135           7     // MQ-135 / MQ-2 Air/Smoke
  #define PIN_RAIN            1     // Rain sensor plate
  #define PIN_WATER           2     // Analog water level probe
  #define PIN_SOIL            3     // Capacitive soil moisture
  #define PIN_PH              4     // Water pH probe
  #define PIN_TDS             5     // Water TDS probe
  #define PIN_TURBIDITY       6     // Water Turbidity probe
  #define PIN_BATTERY         0     // Battery voltage divider (GPIO 0)

  // --- Digital Sensor Pins ---
  #define PIN_FLAME           15    // IR Flame sensor (Active LOW)
  #define PIN_SW420           21    // SW-420 Vibration sensor

  // --- Ultrasonic Sensor Pins (JSN-SR04T) ---
  #define PIN_US_TRIG         17
  #define PIN_US_ECHO         16

  // --- Hardware UARTs ---
  #define GPS_RX_PIN          18
  #define GPS_TX_PIN          19

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

  #define PIN_MQ135           34
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
#define PACKET_VERSION        3           // Protocol Schema Version

// Reference height for ultrasonic sensor (sensor to channel floor in cm)
#define ULTRASONIC_REF_CM     300.0f

// Calibration ADC Values
#define ADC_MAX_VAL           4095.0f
#define VREF                  3.3f
#define RAIN_DRY_ADC          3800
#define RAIN_WET_ADC          1200
#define SOIL_DRY_ADC          3600
#define SOIL_WET_ADC          1800
#define WATER_EMPTY_ADC       300
#define WATER_FULL_ADC        3500

#define BATTERY_DIVIDER_RATIO 2.0f        // 100k + 100k divider
#define BATTERY_V_MAX         4.2f
#define BATTERY_V_MIN         3.2f

// ============================================================================
// 3. GLOBAL OBJECTS & STATE
// ============================================================================
Adafruit_BME680   bme;
Adafruit_MPU6050  mpu;
HardwareSerial    GPS_Serial(1);

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
float             vibrationRate    = 0.0f;  // Pulses per minute

unsigned long     lastTxTime       = 0;
uint32_t          seqNumber        = 0;

// GPS Coordinates
float             latitude         = 13.0827f;  // Default fallback (Chennai / SRM)
float             longitude        = 80.2707f;
bool              gpsFixed         = false;

// ============================================================================
// 4. INTERRUPT SERVICE ROUTINES (ISRs)
// ============================================================================
void IRAM_ATTR isrVibration() {
  vibrationCounter++;
}

void IRAM_ATTR isrFlame() {
  emergencyFire = (digitalRead(PIN_FLAME) == LOW);
}

// ============================================================================
// 5. HELPER FUNCTIONS
// ============================================================================
inline float round2(float v) {
  return (float)((int)(v * 100.0f + (v >= 0 ? 0.5f : -0.5f))) / 100.0f;
}

int mapConstrain(int val, int lowRaw, int highRaw) {
  long pct = map(val, lowRaw, highRaw, 0, 100);
  return (int)constrain(pct, 0L, 100L);
}

float readBatteryVoltage() {
  int raw = analogRead(PIN_BATTERY);
  float measured = (raw / ADC_MAX_VAL) * VREF;
  return measured * BATTERY_DIVIDER_RATIO;
}

float readBatteryPct(float voltage) {
  float pct = ((voltage - BATTERY_V_MIN) / (BATTERY_V_MAX - BATTERY_V_MIN)) * 100.0f;
  return constrain(pct, 0.0f, 100.0f);
}

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
  while (GPS_Serial.available()) {
    char c = GPS_Serial.read();
    static char nmea[120];
    static int idx = 0;

    if (c == '\n' || idx >= 118) {
      nmea[idx] = '\0';
      idx = 0;

      // Extract coordinates from $GPRMC
      if (strncmp(nmea, "$GPRMC", 6) == 0) {
        char buf[120];
        strncpy(buf, nmea, 119);
        char* token = strtok(buf, ",");
        int field = 0;
        char status = 'V';
        char latStr[16] = "", latDir = 'N';
        char lonStr[16] = "", lonDir = 'E';

        while (token != nullptr) {
          switch (field) {
            case 2: status = token[0]; break;
            case 3: strncpy(latStr, token, 15); break;
            case 4: latDir = token[0]; break;
            case 5: strncpy(lonStr, token, 15); break;
            case 6: lonDir = token[0]; break;
          }
          token = strtok(nullptr, ",");
          field++;
        }

        if (status == 'A' && strlen(latStr) > 0) {
          float rawLat = atof(latStr);
          int latDeg = (int)(rawLat / 100);
          float latMin = rawLat - latDeg * 100;
          latitude = latDeg + latMin / 60.0f;
          if (latDir == 'S') latitude = -latitude;

          float rawLon = atof(lonStr);
          int lonDeg = (int)(rawLon / 100);
          float lonMin = rawLon - lonDeg * 100;
          longitude = lonDeg + lonMin / 60.0f;
          if (lonDir == 'W') longitude = -longitude;

          gpsFixed = true;
          health.gps = true;
        }
      }
    } else if (c != '\r') {
      nmea[idx++] = c;
    }
  }
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

  // Pin modes for digital/analog sensors
  pinMode(PIN_FLAME, INPUT_PULLUP);
  pinMode(PIN_SW420, INPUT);
  pinMode(PIN_US_TRIG, OUTPUT);
  pinMode(PIN_US_ECHO, INPUT);

  // Attach interrupts for instant response
  attachInterrupt(digitalPinToInterrupt(PIN_SW420), isrVibration, RISING);
  attachInterrupt(digitalPinToInterrupt(PIN_FLAME), isrFlame, CHANGE);
  emergencyFire = (digitalRead(PIN_FLAME) == LOW);

  // Initialize I2C Bus
  Wire.begin(SDA_PIN, SCL_PIN);
  Wire.setClock(100000);
  delay(50);

  // 1. Initialize BME680
  Serial.print(F("[INIT] Probing BME680... "));
  if (bme.begin(0x76, &Wire) || bme.begin(0x77, &Wire)) {
    health.bme680 = true;
    bme.setTemperatureOversampling(BME680_OS_8X);
    bme.setHumidityOversampling(BME680_OS_2X);
    bme.setPressureOversampling(BME680_OS_4X);
    bme.setIIRFilterSize(BME680_FILTER_SIZE_3);
    bme.setGasHeater(320, 150); // 320°C for 150ms
    Serial.println(F("SUCCESS (I2C 0x76/0x77)"));
  } else {
    Serial.println(F("NOT FOUND (Using fallback models)"));
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
    Serial.println(F("NOT FOUND (Tilt calculated via ADC/sim)"));
  }

  // 3. Initialize GPS UART
  GPS_Serial.begin(9600, SERIAL_8N1, GPS_RX_PIN, GPS_TX_PIN);
  Serial.println(F("[INIT] GPS UART initialized on 9600 baud."));

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
void transmitSensorTelemetry() {
  seqNumber++;
  unsigned long now = millis();

  // 1. Read BME680
  float temperature = 32.5f;
  float humidity    = 52.0f;
  float pressure    = 1011.2f;
  float gasResKohm  = 120.0f;

  if (health.bme680 && bme.performReading()) {
    temperature = bme.temperature;
    humidity    = bme.humidity;
    pressure    = bme.pressure / 100.0f;           // Convert Pa -> hPa
    gasResKohm  = bme.gas_resistance / 1000.0f;     // Convert Ohm -> kOhm
  }

  // 2. Read Analog Environmental Sensors
  int rawMq135     = analogRead(PIN_MQ135);
  int rawRain      = analogRead(PIN_RAIN);
  int rawWater     = analogRead(PIN_WATER);
  int rawSoil      = analogRead(PIN_SOIL);
  int rawPh        = analogRead(PIN_PH);
  int rawTds       = analogRead(PIN_TDS);
  int rawTurbidity = analogRead(PIN_TURBIDITY);

  // Scaled percentages / metric conversions
  float rainPct    = mapConstrain(rawRain, RAIN_DRY_ADC, RAIN_WET_ADC);
  float soilPct    = mapConstrain(rawSoil, SOIL_DRY_ADC, SOIL_WET_ADC);
  float waterPct   = mapConstrain(rawWater, WATER_EMPTY_ADC, WATER_FULL_ADC);

  // Ultrasonic distance & derived water depth
  float usDistCm   = readUltrasonicDistanceCm();
  float waterLevelM = (usDistCm > 0 && usDistCm <= ULTRASONIC_REF_CM) 
                     ? (ULTRASONIC_REF_CM - usDistCm) / 100.0f 
                     : (waterPct / 100.0f * 2.5f); // Fallback to float probe

  // pH (0 - 14)
  float phVoltage  = (rawPh / ADC_MAX_VAL) * VREF;
  float phValue    = constrain(7.0f - ((phVoltage - 2.5f) / 0.18f), 0.0f, 14.0f);

  // TDS (ppm)
  float tdsVoltage = (rawTds / ADC_MAX_VAL) * VREF;
  float tdsPpm     = max(0.0f, (tdsVoltage * tdsVoltage / 3.3f / 3.3f) * 1000.0f);

  // Turbidity (NTU)
  float turbVoltage = (rawTurbidity / ADC_MAX_VAL) * VREF;
  float turbNTU    = max(0.0f, (3300.0f - turbVoltage * 1000.0f) / 10.0f);

  // 3. Tilt & Motion from MPU6050
  float tiltAngleDeg = 0.0f;
  if (health.mpu6050) {
    sensors_event_t a, g, temp;
    mpu.getEvent(&a, &g, &temp);
    float norm = sqrt(a.acceleration.x * a.acceleration.x + 
                      a.acceleration.y * a.acceleration.y + 
                      a.acceleration.z * a.acceleration.z);
    if (norm > 0.001f) {
      tiltAngleDeg = acos(constrain(a.acceleration.z / norm, -1.0f, 1.0f)) * 180.0f / PI;
    }
  }

  // 4. Vibration Rate
  if (now - lastVibResetTime >= 60000) {
    vibrationRate = (float)vibrationCounter;
    vibrationCounter = 0;
    lastVibResetTime = now;
  }

  // 5. Battery Monitoring
  float battVoltage = readBatteryVoltage();
  float battPct     = readBatteryPct(battVoltage);

  // 6. IR Optical Flame Status
  bool isFlameActive = (digitalRead(PIN_FLAME) == LOW) || emergencyFire;

  // 7. Sensor Flag Bitmask (matches gateway codec SENSOR_FLAGS)
  uint16_t sf = 0;
  if (health.bme680) sf |= (1 << 0);
  sf |= (1 << 2); // MQ-135 always active
  sf |= (1 << 3); // Rain
  sf |= (1 << 4); // Water
  if (usDistCm > 0) sf |= (1 << 5); // Ultrasonic
  sf |= (1 << 6); // Soil
  if (health.mpu6050) sf |= (1 << 7); // MPU6050
  sf |= (1 << 8); // SW420
  sf |= (1 << 9); // Flame
  sf |= (1 << 10); // pH
  sf |= (1 << 11); // TDS
  sf |= (1 << 12); // Turbidity
  if (gpsFixed) sf |= (1 << 13);
  sf |= (1 << 14); // Battery

  // 8. Build Compact JSON Payload (Standard TerraEdge Short-Key Schema)
  StaticJsonDocument<384> doc;
  doc["v"]   = PACKET_VERSION;
  doc["id"]  = NODE_ID;
  doc["seq"] = seqNumber;
  doc["ts"]  = (uint32_t)(now / 1000); // Relative epoch timestamp
  doc["sf"]  = sf;
  doc["lat"] = round2(latitude);
  doc["lon"] = round2(longitude);
  doc["bat"] = (int)battPct;
  doc["bv"]  = round2(battVoltage);

  // Environmental readings
  doc["t"]   = round2(temperature);
  doc["h"]   = round2(humidity);
  doc["p"]   = round2(pressure);
  doc["gr"]  = round2(gasResKohm);
  doc["mq"]  = rawMq135;

  // Hazards & Water
  doc["rm"]  = round2(rainPct);
  doc["wl"]  = round2(waterLevelM);
  if (usDistCm > 0) doc["ud"] = round2(usDistCm);
  doc["sm"]  = round2(soilPct);
  doc["tm"]  = round2(tiltAngleDeg);
  doc["vr"]  = round2(vibrationRate);
  doc["fd"]  = isFlameActive ? 1 : 0;

  // Water Quality
  doc["ph"]  = round2(phValue);
  doc["td"]  = round2(tdsPpm);
  doc["tb"]  = round2(turbNTU);

  // Serialize to string buffer
  char jsonBuffer[384];
  size_t len = serializeJson(doc, jsonBuffer, sizeof(jsonBuffer));

  // --- Display Diagnostic Serial Log ---
  Serial.printf("\n[TX #%u] %u Bytes | Batt: %.1fV (%d%%) | Flame: %s\n", 
                seqNumber, len, battVoltage, (int)battPct, isFlameActive ? "ALERT (FIRE!)" : "Clear");
  Serial.printf("  Env: T=%.1f°C | H=%.1f%% | P=%.1fhPa | Gas=%.1fkΩ | MQ=%d\n", 
                temperature, humidity, pressure, gasResKohm, rawMq135);
  Serial.printf("  Hydro/Geo: Rain=%.0f%% | Water=%.2fm | Soil=%.0f%% | Tilt=%.1f° | Vib=%.0f/min\n", 
                rainPct, waterLevelM, soilPct, tiltAngleDeg, vibrationRate);
  Serial.printf("  Payload: %s\n", jsonBuffer);

  // --- Transmit via LoRa ---
  if (health.lora) {
    LoRa.beginPacket();
    LoRa.write((const uint8_t*)jsonBuffer, len);
    LoRa.endPacket();
    Serial.println(F("  -> LoRa SX1278 Packet Dispatched Successfully"));
  } else {
    Serial.println(F("  [WARN] LoRa offline. Retrying next cycle."));
  }
}

// ============================================================================
// 8. MAIN LOOP
// ============================================================================
void loop() {
  unsigned long now = millis();

  // Continuously parse incoming GPS NMEA sentences
  parseGPSStream();

  // Instant Fire Hazard Detection
  bool currentFlame = (digitalRead(PIN_FLAME) == LOW);
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
