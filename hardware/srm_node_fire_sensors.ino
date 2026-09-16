#include <Wire.h>
#include <SPI.h>
#include <LoRa.h>

#include <Adafruit_Sensor.h>
#include <Adafruit_BME680.h>

// =====================================================
// TERRAEDGE TYPE-A TEST FIRMWARE (REAL-TIME NON-BLOCKING)
// ESP32-S3 + BME680 + LoRa + MQ-2 + Flame + Rain + Water + Soil
// =====================================================

// ---------------- I2C ----------------
#define SDA_PIN 8
#define SCL_PIN 9

// ---------------- LoRa ----------------
#define LORA_SS   10
#define LORA_RST  14
#define LORA_DIO0 47
#define LORA_SCK  13
#define LORA_MISO 12
#define LORA_MOSI 11
#define LORA_FREQ 433E6

// ---------------- Sensors --------------
#define RAIN_PIN   1
#define WATER_PIN  2
#define SOIL_PIN   3
#define MQ2_PIN    7   // MQ-2 for now, MQ-135 later
#define FLAME_PIN  15

// ---------------- Objects & Status Flags ---------------
Adafruit_BME680 bme;
bool bme_ready = false;
bool lora_ready = false;

// ---------------- Timers & State ---------------
unsigned long lastUpdate = 0;          
const long updateInterval = 10000;     // 10 seconds between LoRa packets
bool fireAlertActive = false;          

// ---------------- Calibration points ----------------
const int RAIN_DRY_ADC   = 3800;
const int RAIN_WET_ADC   = 1200;
const int WATER_EMPTY_ADC = 300;
const int WATER_FULL_ADC  = 3500;
const int SOIL_DRY_ADC   = 3600;
const int SOIL_WET_ADC   = 1800;

int toPercent(int raw, int lowRaw, int highRaw) {
  long pct = map(raw, lowRaw, highRaw, 0, 100);
  return constrain(pct, 0, 100);
}

void setup() {
  Serial.begin(115200);
  delay(1000);

  Serial.println();
  Serial.println("========================================");
  Serial.println("     TerraEdge Type-A Sensor Test       ");
  Serial.println("========================================");

  // 1. I2C init (Restored your exact sequence and delay)
  Wire.begin(SDA_PIN, SCL_PIN);
  Wire.setClock(100000);
  delay(100);

  // 2. BME680 init
  Serial.println("Initializing BME680...");
  if (bme.begin(0x76, &Wire)) {
    bme_ready = true;
    Serial.println("BME680 OK (0x76)");
  } else if (bme.begin(0x77, &Wire)) {
    bme_ready = true;
    Serial.println("BME680 OK (0x77)");
  } else {
    Serial.println("BME680 NOT FOUND!");
  }

  if (bme_ready) {
    bme.setTemperatureOversampling(BME680_OS_8X);
    bme.setHumidityOversampling(BME680_OS_2X);
    bme.setPressureOversampling(BME680_OS_4X);
    bme.setIIRFilterSize(BME680_FILTER_SIZE_3);
    bme.setGasHeater(320, 150);
  }

  // 3. LoRa init (Restored your exact sequence)
  Serial.println("Initializing LoRa...");
  SPI.begin(LORA_SCK, LORA_MISO, LORA_MOSI, LORA_SS);

  pinMode(LORA_RST, OUTPUT);
  digitalWrite(LORA_RST, HIGH); delay(10);
  digitalWrite(LORA_RST, LOW);  delay(20);
  digitalWrite(LORA_RST, HIGH); delay(20);

  LoRa.setPins(LORA_SS, LORA_RST, LORA_DIO0);

  if (!LoRa.begin(LORA_FREQ)) {
    Serial.println("LoRa FAILED!");
  } else {
    lora_ready = true;
    Serial.println("LoRa OK");
  }

  // 4. Sensor pin modes
  pinMode(FLAME_PIN, INPUT);
  pinMode(RAIN_PIN, INPUT);
  pinMode(WATER_PIN, INPUT);
  pinMode(SOIL_PIN, INPUT);
  pinMode(MQ2_PIN, INPUT);

  // 5. ADC settings
  analogReadResolution(12);

  Serial.println("System Ready\n");
}

void loop() {
  // --- INSTANT FLAME CHECK (No Delays) ---
  int flameRaw = digitalRead(FLAME_PIN);
  
  if (flameRaw == LOW && !fireAlertActive) {
    Serial.println("\n=========================================");
    Serial.println("   ⚠️ EMERGENCY: FIRE DETECTED! ⚠️   ");
    Serial.println("=========================================\n");
    fireAlertActive = true; 
  } else if (flameRaw == HIGH && fireAlertActive) {
    Serial.println("Fire hazard cleared.");
    fireAlertActive = false;
  }

  // --- 10 SECOND LORA & SENSOR DATA UPDATE ---
  if (millis() - lastUpdate >= updateInterval) {
    lastUpdate = millis();

    float temp = 0.0, hum = 0.0, press = 0.0, gas = 0.0;

    if (bme_ready && bme.performReading()) {
        temp  = bme.temperature;
        hum   = bme.humidity;
        press = bme.pressure / 100.0;
        gas   = bme.gas_resistance / 1000.0;   
    }

    int mqRaw    = analogRead(MQ2_PIN);
    int rainRaw  = analogRead(RAIN_PIN);
    int waterRaw = analogRead(WATER_PIN);
    int soilRaw  = analogRead(SOIL_PIN);

    int rainPercent  = toPercent(rainRaw,   RAIN_DRY_ADC,   RAIN_WET_ADC);
    int waterPercent = toPercent(waterRaw,  WATER_EMPTY_ADC, WATER_FULL_ADC);
    int soilPercent  = toPercent(soilRaw,   SOIL_DRY_ADC,   SOIL_WET_ADC);

    // Print Data safely to Serial
    Serial.println("\n========== SENSOR DATA ==========");
    if (bme_ready) {
      Serial.print("Temperature : "); Serial.print(temp, 2);  Serial.println(" C");
      Serial.print("Humidity    : "); Serial.print(hum, 2);   Serial.println(" %");
      Serial.print("Pressure    : "); Serial.print(press, 2); Serial.println(" hPa");
      Serial.print("Gas Resist. : "); Serial.print(gas, 2);   Serial.println(" KOhm");
    }
    Serial.println();
    
    Serial.print("MQ2 Raw     : "); Serial.println(mqRaw);
    Serial.print("Rain Raw    : "); Serial.print(rainRaw);
    Serial.print("  |  Rain %: "); Serial.print(rainPercent); Serial.println("%");
    Serial.print("Water Raw   : "); Serial.print(waterRaw);
    Serial.print("  |  Water %: "); Serial.print(waterPercent); Serial.println("%");
    Serial.print("Soil Raw    : "); Serial.print(soilRaw);
    Serial.print("  |  Soil %: "); Serial.print(soilPercent); Serial.println("%");
    Serial.print("Flame       : "); Serial.println(flameRaw == LOW ? "FIRE DETECTED!" : "Safe (No Fire)");
    Serial.println("--------------------------------");

    // Send LoRa packet
    if (lora_ready) {
      LoRa.beginPacket();
      LoRa.print(temp, 2);        LoRa.print(",");
      LoRa.print(hum, 2);         LoRa.print(",");
      LoRa.print(press, 2);       LoRa.print(",");
      LoRa.print(gas, 2);         LoRa.print(",");
      LoRa.print(mqRaw);          LoRa.print(",");
      LoRa.print(rainRaw);        LoRa.print(",");
      LoRa.print(rainPercent);    LoRa.print(",");
      LoRa.print(waterRaw);       LoRa.print(",");
      LoRa.print(waterPercent);   LoRa.print(",");
      LoRa.print(soilRaw);        LoRa.print(",");
      LoRa.print(soilPercent);    LoRa.print(",");
      LoRa.print(flameRaw == LOW ? 1 : 0);
      LoRa.endPacket();
      Serial.println("LoRa Packet Sent");
    }
  }
}
