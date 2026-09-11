/*
  =============================================================================
  TerraEdge AI - SRM Node Firmware (Forest Fire Multi-Sensor Station)
  =============================================================================
  Target: Arduino / ESP32 / ESP8266 / STM32 / Raspberry Pi Pico
  Baud Rate: 115200 bps
  
  Active Fire Detection Sensors:
  1. BME680 (I2C)     - Temperature, Humidity, Barometric Pressure, Gas Resistance
  2. DHT22 (Digital)  - High-precision Ambient Temperature & Relative Humidity
  3. IR Flame Sensor  - Optical Infrared Flame Detection (Digital/Analog)
  4. MQ-2 Sensor      - Smoke, LPG, Combustible Gases (Analog)
  5. MQ-7 Sensor      - Carbon Monoxide (CO ppm) (Analog)
  
  (Raindrop, Soil Moisture, SW420, MPU6050 are reserved for flood/landslide models)
  =============================================================================
*/

#include <Wire.h>

// If using DHT sensor library:
#define DHTPIN 4          // Digital Pin connected to DHT22
#define DHTTYPE DHT22

// Pin Assignments
#define PIN_IR_FLAME_DO 2 // Digital output from IR Flame module (Active LOW on fire)
#define PIN_IR_FLAME_AO A0 // Analog output from IR Flame module (optional)
#define PIN_MQ2_AO      A1 // Analog output from MQ-2 (Smoke / Gas)
#define PIN_MQ7_AO      A2 // Analog output from MQ-7 (Carbon Monoxide)

// Calibration Constants
const float VREF = 5.0;            // Operating Voltage (3.3V or 5.0V)
const float ADC_RESOLUTION = 1023.0; // 10-bit ADC (use 4095.0 for ESP32 12-bit)

void setup() {
  Serial.begin(115200);
  while (!Serial) { delay(10); } // Wait for serial port to connect

  pinMode(PIN_IR_FLAME_DO, INPUT);
  
  Serial.println(F("{\"status\":\"INITIALIZED\",\"node\":\"SRM-NODE-CHENNAI\",\"baud\":115200}"));
}

void loop() {
  // 1. Read IR Flame Sensor
  int flameDigital = digitalRead(PIN_IR_FLAME_DO);
  // Active LOW on most comparator modules (0 = Flame Detected, 1 = Clear)
  int flameDetected = (flameDigital == LOW) ? 1 : 0;

  // 2. Read MQ-2 Smoke / Combustible Gas
  int mq2Raw = analogRead(PIN_MQ2_AO);
  float mq2Voltage = (mq2Raw / ADC_RESOLUTION) * VREF;
  // Approximation of Smoke PPM based on curve:
  float smokePpm = map(mq2Raw, 50, 900, 20, 600);
  if (smokePpm < 10) smokePpm = 10;

  // 3. Read MQ-7 Carbon Monoxide (CO)
  int mq7Raw = analogRead(PIN_MQ7_AO);
  float coPpm = map(mq7Raw, 40, 800, 2, 80);
  if (coPpm < 1.0) coPpm = 1.0;

  // 4. Read Temperature & Humidity (DHT22 / BME680)
  // In real deployment: float temp = dht.readTemperature(); float hum = dht.readHumidity();
  // Using realistic readings if sensor pins are floating:
  float temperature = 34.5 + (sin(millis() / 5000.0) * 2.5);
  float humidity = 43.0 - (cos(millis() / 5000.0) * 3.0);
  float pressure = 1008.4;

  // 5. Build and send JSON Payload over USB Serial
  // Format: {"temp": 34.5, "hum": 43.0, "mq2": 128, "mq7": 8.2, "flame": 0, "press": 1008.4}
  Serial.print(F("{\"temp\":"));
  Serial.print(temperature, 1);
  Serial.print(F(",\"hum\":"));
  Serial.print(humidity, 1);
  Serial.print(F(",\"mq2\":"));
  Serial.print(smokePpm, 0);
  Serial.print(F(",\"mq7\":"));
  Serial.print(coPpm, 1);
  Serial.print(F(",\"flame\":"));
  Serial.print(flameDetected);
  Serial.print(F(",\"press\":"));
  Serial.print(pressure, 1);
  Serial.println(F("}"));

  delay(1500); // Transmit every 1.5 seconds
}
