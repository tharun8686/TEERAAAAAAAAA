// ============================================================
// TerraEdge Phase 3 — LoRa Radio Configuration (Single Source of Truth)
// MUST match gateway/lora/config.py exactly.
// ============================================================
#pragma once

// Frequency
#define LORA_FREQ         433E6         // 433 MHz

// Radio parameters
#define LORA_BW           125E3         // 125 kHz bandwidth
#define LORA_SF           7             // Spreading Factor 7 (fast / short-range)
#define LORA_CR           5             // Coding Rate 4/5
#define LORA_TX_POWER     17            // dBm (safe for RA-02)
#define LORA_SYNC_WORD    0x34          // TerraEdge private network byte
#define LORA_CRC_ENABLED  true          // Hardware CRC

// Packet version
#define PACKET_VERSION    3

// Transmission interval (milliseconds)
#define LORA_TX_INTERVAL_MS  10000      // 10 seconds

// ACK configuration
#define LORA_ACK_ENABLED     false      // Set true to enable ACK wait
#define LORA_ACK_TIMEOUT_MS  2000       // Wait 2 seconds for ACK
#define LORA_RETRIES         2          // Retry up to 2 times on no-ACK

// SX1278 / RA-02 GPIO (ESP32-S3 — confirmed from repository)
#define LORA_SS    10
#define LORA_RST   14
#define LORA_DIO0  47
#define LORA_SCK   13
#define LORA_MISO  12
#define LORA_MOSI  11
