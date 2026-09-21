"""
TerraEdge Phase 3 — LoRa Background Receiver.

Runs as a FastAPI background task (asyncio-friendly).
Responsibilities:
1. Continuously poll radio.receive()
2. Decode packet via packet.decode_packet()
3. Validate packet integrity and schema
4. Detect and discard duplicates
5. Detect and log sequence gaps
6. Call process_type_a_telemetry() — same function used by HTTP path
7. Update node LoRa health metadata in NodeManager
8. Optionally send ACK

Architecture guarantee:
    LoRa path and HTTP path call the SAME process_type_a_telemetry() function.
    No duplicate hazard-processing logic.
"""
from __future__ import annotations
import asyncio
import collections
import logging
import json
import time
from typing import Any, Callable, Dict, Optional

from .packet import decode_packet
from .radio import LoRaRadioBase
from ..schemas import LoRaTransportMetadata

logger = logging.getLogger("terraedge.lora.receiver")


class LoRaReceiver:
    """
    Background LoRa receiver that decodes packets and feeds them into
    the existing gateway telemetry pipeline.

    Usage:
        receiver = LoRaReceiver(radio=radio, ingest_fn=process_type_a_telemetry)
        await receiver.run()   # called as asyncio background task
    """

    def __init__(
        self,
        radio: LoRaRadioBase,
        ingest_fn: Callable,
        node_manager=None,
        ack_enabled: bool = False,
        ack_timeout_ms: int = 2000,
        dedup_cache_size: int = 1000,
        poll_interval_ms: int = 50,
    ):
        self.radio = radio
        self.ingest_fn = ingest_fn
        self.node_manager = node_manager
        self.ack_enabled = ack_enabled
        self.ack_timeout_ms = ack_timeout_ms
        self.dedup_cache_size = dedup_cache_size
        self.poll_interval_ms = poll_interval_ms

        # Duplicate detection: ordered dict keyed by "node_id:sequence"
        self._seen_packets: collections.OrderedDict = collections.OrderedDict()

        # Sequence tracking per node
        self._last_sequence: Dict[str, int] = {}

        # Communication stats per node
        self._node_stats: Dict[str, Dict[str, Any]] = {}

        self._running = False

    # ------------------------------------------------------------------
    # Main receive loop — must be run as asyncio task
    # ------------------------------------------------------------------
    async def run(self) -> None:
        """Infinite receive loop. Yields control to event loop between polls."""
        if not self.radio.initialize():
            logger.error("[LoRaReceiver] Radio initialization failed — LoRa receiver NOT started")
            return

        self._running = True
        logger.info("[LoRaReceiver] Started — listening for LoRa packets")

        while self._running:
            try:
                await self._poll_once()
            except Exception as e:
                logger.exception(f"[LoRaReceiver] Unexpected error in receive loop: {e}")

            # Yield control to FastAPI event loop
            await asyncio.sleep(self.poll_interval_ms / 1000.0)

    async def _poll_once(self) -> None:
        """One receive cycle — blocking radio.receive() is run in thread executor."""
        loop = asyncio.get_event_loop()

        # Run blocking receive in thread pool to avoid blocking event loop
        raw = await loop.run_in_executor(
            None, lambda: self.radio.receive(timeout_ms=self.poll_interval_ms)
        )

        if raw is None:
            return  # timeout — nothing received

        rssi = self.radio.get_rssi()
        snr = self.radio.get_snr()

        await self._handle_packet(raw, rssi, snr)

    async def _handle_packet(
        self, raw: bytes, rssi: Optional[float], snr: Optional[float]
    ) -> None:
        """Validate, deduplicate, and ingest a received packet."""
        # Root SENDER.ino v4 fragments use the same assembler as browser/HTTP USB.
        try:
            is_v4 = json.loads(raw).get("v") == 4
        except (ValueError, AttributeError, UnicodeError):
            is_v4 = False
        if is_v4:
            from ..hardware_ingest import assembler
            from ..schemas import TypeATelemetryPayload
            try:
                with assembler.lock:
                    state, values, identity = assembler.accept({"type": "RX", "data": raw.hex(),
                        "size": len(raw), "rssi": rssi, "snr": snr})
                    if values is None:
                        return
                    payload = TypeATelemetryPayload(**values)
                    meta = LoRaTransportMetadata(rssi_dbm=rssi, snr_db=snr, packet_sequence=payload.sequence)
                    self.ingest_fn(payload, meta)
                    assembler.commit(identity)
                    self._inc_stat(payload.node_id, "packets_received")
            except Exception as error:
                logger.warning("Rejected v4 frame: %s", error)
            return
        # 1. Decode
        try:
            payload, sequence = decode_packet(raw)
        except ValueError as e:
            logger.warning(f"[LoRaReceiver] Invalid packet ({len(raw)} bytes): {e}")
            return

        node_id = payload.node_id

        # 2. Duplicate detection
        dedup_key = f"{node_id}:{sequence}"
        if dedup_key in self._seen_packets:
            logger.info(f"[LoRaReceiver] DUPLICATE PACKET IGNORED — {dedup_key}")
            self._inc_stat(node_id, "duplicates")
            return

        # Maintain bounded cache
        self._seen_packets[dedup_key] = True
        if len(self._seen_packets) > self.dedup_cache_size:
            self._seen_packets.popitem(last=False)

        # 3. Sequence gap detection
        last_seq = self._last_sequence.get(node_id)
        if last_seq is not None:
            expected = last_seq + 1
            if sequence > expected:
                missed = sequence - expected
                logger.warning(
                    f"[LoRaReceiver] SEQUENCE GAP — {node_id}: "
                    f"expected {expected}, got {sequence} "
                    f"(~{missed} packet(s) missing)"
                )
                self._inc_stat(node_id, "packets_lost", delta=missed)
        self._last_sequence[node_id] = sequence

        # 4. Build transport metadata
        transport_meta = LoRaTransportMetadata(
            rssi_dbm=rssi,
            snr_db=snr,
            packet_sequence=sequence,
        )

        # 5. Update node LoRa health in NodeManager
        if self.node_manager is not None:
            self._update_node_lora_health(node_id, rssi, snr, sequence)

        # 6. Feed into existing telemetry pipeline (same as HTTP path)
        logger.info(
            f"[LoRaReceiver] RX — node={node_id} seq={sequence} "
            f"rssi={rssi} snr={snr} size={len(raw)}B"
        )
        try:
            self.ingest_fn(payload, transport_meta)
        except Exception as e:
            logger.error(f"[LoRaReceiver] ingest_fn error for {node_id}: {e}")
            return

        self._inc_stat(node_id, "packets_received")

        # 7. Send ACK if enabled
        if self.ack_enabled:
            await self._send_ack(node_id, sequence)

    async def _send_ack(self, node_id: str, sequence: int) -> None:
        """Transmit ACK packet back to Type A node."""
        import json
        ack_data = json.dumps({"ack": node_id, "seq": sequence}).encode("utf-8")
        loop = asyncio.get_event_loop()
        ok = await loop.run_in_executor(None, lambda: self.radio.send(ack_data))
        if ok:
            logger.debug(f"[LoRaReceiver] ACK sent to {node_id} seq={sequence}")
        else:
            logger.warning(f"[LoRaReceiver] ACK send failed for {node_id} seq={sequence}")

    def _update_node_lora_health(
        self, node_id: str, rssi: Optional[float], snr: Optional[float], sequence: int
    ) -> None:
        """Push LoRa communication health fields into NodeManager."""
        try:
            with self.node_manager._lock:
                node = self.node_manager._nodes.get(node_id, {})
                node["radio_rssi"] = rssi
                node["radio_snr"] = snr
                node["packet_sequence"] = sequence
                stats = self._node_stats.get(node_id, {})
                node["packets_received"] = stats.get("packets_received", 0)
                node["packets_lost"] = stats.get("packets_lost", 0)
                node["last_packet_status"] = "OK"
                node["transport_type"] = "LoRa"
                self.node_manager._nodes[node_id] = node
        except Exception as e:
            logger.debug(f"[LoRaReceiver] node health update error: {e}")

    def _inc_stat(self, node_id: str, key: str, delta: int = 1) -> None:
        stats = self._node_stats.setdefault(node_id, {})
        stats[key] = stats.get(key, 0) + delta

    def stop(self) -> None:
        self._running = False
        self.radio.close()
        logger.info("[LoRaReceiver] Stopped")
