// ============================================================
// TerraEdge Phase 3 — Type B LoRa USB Bridge Firmware
// ============================================================
// Purpose: Second ESP32 at the gateway PC.
//   - Receives LoRa packets from Type A nodes
//   - Forwards them to PC over USB serial as JSON:
//       {"type":"RX","rssi":-81.0,"snr":7.5,"data":"<hex>"}
//   - Accepts TX commands from PC for ACK:
//       {"type":"TX","data":"<hex>"}
//
// Radio config MUST match terraedge_node lora_config.h exactly.
// ============================================================

#include <Arduino.h>
#include <SPI.h>
#include <LoRa.h>
#include <ArduinoJson.h>

// Same GPIO as Type A (bridge uses same SX1278 wiring)
#define LORA_SS    10
#define LORA_RST   14
#define LORA_DIO0  47
#define LORA_SCK   13
#define LORA_MISO  12
#define LORA_MOSI  11

// Radio parameters — MUST match lora_config.h
#define LORA_FREQ       433E6
#define LORA_BW         125E3
#define LORA_SF         7
#define LORA_CR         5
#define LORA_SYNC_WORD  0x34

void setup() {
  Serial.begin(115200);
  while (!Serial);

  SPI.begin(LORA_SCK, LORA_MISO, LORA_MOSI, LORA_SS);
  pinMode(LORA_RST, OUTPUT);
  digitalWrite(LORA_RST, HIGH); delay(10);
  digitalWrite(LORA_RST, LOW);  delay(20);
  digitalWrite(LORA_RST, HIGH); delay(20);

  LoRa.setPins(LORA_SS, LORA_RST, LORA_DIO0);

  if (!LoRa.begin(LORA_FREQ)) {
    Serial.println("{\"type\":\"ERROR\",\"msg\":\"LoRa init failed\"}");
    while (true);
  }

  LoRa.setSignalBandwidth(LORA_BW);
  LoRa.setSpreadingFactor(LORA_SF);
  LoRa.setCodingRate4(LORA_CR);
  LoRa.setSyncWord(LORA_SYNC_WORD);
  LoRa.enableCrc();

  LoRa.receive();   // Enter continuous receive mode
  Serial.println("{\"type\":\"READY\",\"msg\":\"TerraEdge Bridge v3 listening\"}");
}

void loop() {
  // --- Handle incoming LoRa packet ---
  int pktSize = LoRa.parsePacket();
  if (pktSize > 0) {
    uint8_t buf[256];
    int len = 0;
    while (LoRa.available() && len < 255) {
      buf[len++] = (uint8_t)LoRa.read();
    }

    float rssi = LoRa.packetRssi();
    float snr  = LoRa.packetSnr();

    // Hex-encode the payload
    char hexBuf[512];
    for (int i = 0; i < len; i++) {
      sprintf(hexBuf + i * 2, "%02x", buf[i]);
    }
    hexBuf[len * 2] = '\0';

    // Output JSON line to PC
    StaticJsonDocument<600> doc;
    doc["type"] = "RX";
    doc["rssi"] = rssi;
    doc["snr"]  = snr;
    doc["size"] = len;
    doc["data"] = hexBuf;
    serializeJson(doc, Serial);
    Serial.println();
  }

  // --- Handle TX command from PC (for ACK) ---
  if (Serial.available()) {
    String line = Serial.readStringUntil('\n');
    line.trim();
    if (line.length() > 0) {
      StaticJsonDocument<256> cmd;
      if (!deserializeJson(cmd, line) && cmd["type"] == "TX") {
        String hexData = cmd["data"].as<String>();
        uint8_t txBuf[128];
        int txLen = 0;
        for (int i = 0; i < (int)hexData.length() - 1; i += 2) {
          txBuf[txLen++] = strtol(hexData.substring(i, i + 2).c_str(), nullptr, 16);
        }
        LoRa.beginPacket();
        LoRa.write(txBuf, txLen);
        LoRa.endPacket();
        LoRa.receive();  // Return to RX mode
        Serial.println("{\"type\":\"TX_DONE\"}");
      }
    }
  }
}
