"""
TerraEdge Phase 3 — LoRa Radio Configuration (Single Source of Truth).

These values MUST match the Type A firmware lora_config.h exactly.
Do not change one side without changing the other.
"""

FREQ_HZ: int   = 433_000_000   # 433 MHz
FREQ_MHZ: float = 433.0
BW_KHZ: int    = 125            # 125 kHz bandwidth
SF: int        = 7              # Spreading Factor 7  (fast / short range)
CR: str        = "4/5"          # Coding Rate 4/5
TX_POWER_DBM: int = 17          # Transmit power (safe for RA-02 prototype)
SYNC_WORD: int = 0x34           # TerraEdge private network sync byte
CRC_ENABLED: bool = True        # Hardware CRC enabled
PREAMBLE_LEN: int = 8           # Preamble symbols (default)

# SX1278 hardware payload limit in bytes
MAX_PAYLOAD_BYTES: int = 250

# Packet version identifier  (increment when packet format changes)
PACKET_VERSION: int = 3

# ACK packet marker
ACK_PREFIX: bytes = b"ACK:"
