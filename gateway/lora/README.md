# TerraEdge Phase 3 — LoRa Transport Layer

## Overview

This directory contains the Type B gateway LoRa transport layer.
It provides the bridge between physical SX1278/RA-02 radio communication
and the existing unified telemetry pipeline.

**Key architectural principle:**
LoRa is TRANSPORT only. Both the HTTP simulator and the LoRa receiver
call the SAME `process_type_a_telemetry()` function in `gateway/app.py`.

```
[Simulator]──HTTP──┐
                   ▼
          process_type_a_telemetry()
                   ▲
[LoRa Receiver]────┘
```

---

## Files

| File | Purpose |
|---|---|
| `config.py` | Single source of truth for radio parameters (must match firmware) |
| `packet.py` | Compact JSON packet encoder/decoder |
| `radio.py` | LoRaRadioBase interface, MockLoRaRadio, SerialLoRaRadio |
| `receiver.py` | Async background receiver loop |
| `README.md` | This file |

---

## Radio Configuration

| Parameter | Value | Notes |
|---|---|---|
| Frequency | 433 MHz | SX1278/RA-02; India ISM band |
| Bandwidth | 125 kHz | Standard outdoor balance |
| Spreading Factor | SF7 | Fast, ~1-2 km outdoor LoS |
| Coding Rate | 4/5 | Minimal overhead |
| Sync Word | `0x34` | TerraEdge private network |
| TX Power | 17 dBm | Safe for RA-02 prototype |
| CRC | Enabled | Hardware packet integrity |
| Max payload | 222 bytes | SX1278 hardware limit |

**CRITICAL:** These values MUST match `hardware/terraedge_node/lora_config.h`.

---

## Packet Format

Compact JSON with short keys (null fields omitted):

```json
{
  "v": 3,
  "id": "TE-001",
  "seq": 1042,
  "ts": "2026-09-16T07:30:00Z",
  "lat": 13.0827, "lon": 80.2707,
  "bat": 87,
  "t": 39.2, "h": 31.5, "p": 1004.2, "gr": 8.3,
  "p25": 94, "p10": 161,
  "mq": 1840,
  "rm": 18.4, "r1": 18.4, "r24": 62.0,
  "wl": 2.3, "ud": 57.0,
  "sm": 68,
  "tm": 2.4, "tr": 0.6, "vr": 3,
  "fd": 0,
  "ph": 7.1, "td": 480, "tb": 14,
  "sf": 32767
}
```

`sf` = sensor presence bitmask (bit 0 = BME680, bit 1 = SDS011, …).
Sensors with bit NOT set → gateway sets field to null (not zero).

Typical full-sensor packet: **~185–200 bytes** (within 222-byte limit).

---

## Type A → Type B Flow

```
ESP32-S3 sensors
    ↓
terraedge_node.ino reads sensors
    ↓
Compact JSON built (short keys)
    ↓
LoRa.beginPacket() / LoRa.endPacket()
    ↓ 433 MHz
SX1278 bridge ESP32 receives
    ↓ USB Serial
{"type":"RX","rssi":-81,"snr":7.5,"data":"<hex>"}
    ↓
SerialLoRaRadio.receive() → bytes
    ↓
decode_packet() → TypeATelemetryPayload + sequence
    ↓
Duplicate check (node_id:sequence)
    ↓
Sequence gap detection
    ↓
process_type_a_telemetry(payload, transport_meta)
    ↓
[Same as HTTP path → 7 models → risk engine → Supabase]
```

---

## Hardware Required

### Type A (Field Node)
- ESP32-S3
- SX1278 / RA-02 (433 MHz)
- All sensors per Phase 2 spec

### Type B (Gateway Side)
- Gateway PC/server
- Second ESP32 (any variant) + SX1278 → USB cable → PC
- Runs `hardware/terraedge_bridge/terraedge_bridge.ino`

---

## SX1278 Wiring (Both ESP32 Nodes)

| SX1278 Pin | ESP32-S3 GPIO |
|---|---|
| NSS (CS) | 10 |
| RST | 14 |
| DIO0 | 47 |
| SCK | 13 |
| MISO | 12 |
| MOSI | 11 |
| VCC | 3.3V |
| GND | GND |

---

## Running the Gateway

### Standard HTTP mode (no LoRa):
```bash
python -m uvicorn gateway.app:app --host 127.0.0.1 --port 8000
```

### LoRa mock mode (testing, no hardware):
```bash
LORA_ENABLED=true LORA_MOCK_MODE=true python -m uvicorn gateway.app:app --host 127.0.0.1 --port 8000
```
Windows PowerShell:
```powershell
$env:LORA_ENABLED="true"; $env:LORA_MOCK_MODE="true"
python -m uvicorn gateway.app:app --host 127.0.0.1 --port 8000
```

### LoRa real hardware mode:
```bash
LORA_ENABLED=true LORA_SERIAL_PORT=COM4 python -m uvicorn gateway.app:app --host 127.0.0.1 --port 8000
```

### USB bridge forwarder (development utility):
```bash
python hardware/usb_serial_bridge.py --port COM4 --gateway http://127.0.0.1:8000
```

---

## Running Tests

### Phase 1 existing tests (must still pass):
```bash
python -m pytest tests/test_gateway.py -v
```

### Phase 3 LoRa tests (no hardware needed):
```bash
python -m pytest tests/test_lora.py -v
```

### All tests:
```bash
python -m pytest tests/ -v
```

### Phase 2 unit validation:
```bash
python "C:\Users\TEJESHWAR\.gemini\antigravity-ide\brain\9793f532-1723-4116-8913-9fe187be00aa\scratch\validate_phase2.py"
```

---

## ACK Design

```
Type A                    Type B Bridge
  ├── TX DATA (seq=N) ──────────────────→
  │   wait LORA_ACK_TIMEOUT_MS (2000ms)
  │                 ←───── ACK {"ack":"TE-001","seq":N}
  ├── ACK received → next packet
  │   (no ACK) → retry (up to LORA_RETRIES=2)
  └── All retries exhausted → log FAILED, continue
```

ACK is disabled by default (`LORA_ACK_ENABLED=false`).
Enable: `LORA_ACK_ENABLED=true` in `.env`.

---

## Sequence Number Design

- Type A increments `seq` every transmission
- Gateway tracks `_last_sequence[node_id]`
- If `current - last > 1` → log `SEQUENCE GAP`
- Duplicate: same `node_id:seq` → `DUPLICATE PACKET IGNORED`
- Cache size: last 1000 packets per `LORA_DEDUP_CACHE_SIZE`

---

## RSSI / SNR

- RSSI: received signal strength in dBm (e.g. -81 dBm)
  - Better than -100 dBm = usable link
  - Better than -70 dBm = strong link
- SNR: signal-to-noise ratio in dB (e.g. 7.5 dB)
  - Positive SNR = signal above noise floor
  - SF7 minimum SNR ≈ -7.5 dB

Stored in node registry under `radio_rssi` and `radio_snr`.
Returned in `transport.rssi_dbm` and `transport.snr_db` in API response.

---

## Current Limitations

1. Type A node_id is hardcoded in firmware (`"TE-001"`). Should be stored in EEPROM.
2. No RTC in prototype — timestamp left empty in firmware packet; gateway fills with receive time.
3. MPU6050 tilt/accelerometer not wired in current firmware (placeholder).
4. Battery percentage derived from ADC voltage — calibration accuracy ~5%.
5. Rain gauge raw % sent; gateway/feature builder handles conversion.
6. ACK is optional and disabled by default for prototype stability.
7. SerialLoRaRadio requires pyserial (`pip install pyserial`).
8. Real hardware test (Type A → LoRa → Type B) not yet performed — documented as pending.
