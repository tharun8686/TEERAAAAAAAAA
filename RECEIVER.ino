// TerraEdge receiver: CRC-checked LoRa bytes -> one USB JSON envelope.
// Standard ESP32 wiring: NSS5 MOSI23 MISO19 SCK18 RST14 DIO0=2.
// ESP32-S3 wiring: NSS10 MOSI11 MISO12 SCK13 RST14 DIO0=47.
// ML inference runs in the Python gateway; no invented receiver scores.
#include <Arduino.h>
#include <SPI.h>
#include <LoRa.h>
#include <ArduinoJson.h>
#if CONFIG_IDF_TARGET_ESP32S3
#define BOARD_ESP32_S3
#elif CONFIG_IDF_TARGET_ESP32
#define BOARD_ESP32_DEV
#else
#error "Supported targets are ESP32 and ESP32-S3; configure other pin maps explicitly."
#endif
#if defined(BOARD_ESP32_S3)
  #define LORA_SCK            13
  #define LORA_MISO           12
  #define LORA_MOSI           11
  #define LORA_SS             10
  #define LORA_RST            14
  #define LORA_DIO0           47
#elif defined(BOARD_ESP32_DEV)
  #define LORA_SCK            18
  #define LORA_MISO           19
  #define LORA_MOSI           23
  #define LORA_SS             5
  #define LORA_RST            14
  #define LORA_DIO0           2
#endif


void setup() {
  Serial.begin(115200);
  delay(500);
  // Never drive DIO0 as an LED output: on ESP32 DEV both used GPIO2 before.
  SPI.begin(LORA_SCK, LORA_MISO, LORA_MOSI, LORA_SS);
  LoRa.setPins(LORA_SS, LORA_RST, LORA_DIO0);
  if (!LoRa.begin(433E6)) {
    Serial.println("{\"type\":\"ERROR\",\"msg\":\"LoRa init failed: check board pins and power\"}");
    while (true) delay(1000);
  }
  LoRa.setSignalBandwidth(125E3);
  LoRa.setSpreadingFactor(7);
  LoRa.setCodingRate4(5);
  LoRa.setSyncWord(0x34);
  LoRa.enableCrc();
  Serial.println("{\"type\":\"READY\",\"protocol\":4}");
}

void loop() {
  int size = LoRa.parsePacket();
  if (size <= 0) return;
  char hex[511];
  const char digits[] = "0123456789abcdef";
  int len = 0;
  while (LoRa.available() && len < 255) {
    uint8_t b = LoRa.read();
    hex[len*2] = digits[b >> 4];
    hex[len*2+1] = digits[b & 15];
    len++;
  }
  if (len != size) return;
  hex[len*2] = 0;
  StaticJsonDocument<1024> doc;
  doc["type"] = "RX";
  doc["rssi"] = LoRa.packetRssi();
  doc["snr"] = LoRa.packetSnr();
  doc["size"] = len;
  doc["data"] = hex;
  if (!doc.overflowed()) { serializeJson(doc, Serial); Serial.println(); }
}
