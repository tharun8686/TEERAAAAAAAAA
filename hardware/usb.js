/* One USB owner per browser tab. Gateway owns inference, receiver owns radio. */
(() => {
  const el = id => document.getElementById(id);
  const api = location.protocol === 'file:' ? 'http://127.0.0.1:8000' : `${location.protocol}//${location.hostname}:8000`;
  // Local files have an opaque origin. Use the gateway-served dashboard so USB
  // packets and polling share a valid HTTP origin instead of weakening CORS.
  if (location.protocol === 'file:') {
    location.replace(api + '/live');
    return;
  }
  let port = null, reader = null, busy = false, stop = false, identified = false;
  const status = message => { el('usb-status').textContent = message; };
  const log = message => {
    const target = el('log');
    if (target) target.textContent = (target.textContent + '\n' + message).split('\n').slice(-30).join('\n');
  };
  async function forward(line) {
    let message;
    try { message = JSON.parse(line); } catch { return; }
    if (message.type === 'READY' && message.role === 'receiver' && message.protocol === 4) {
      identified = true;
      status(message.radio_ready ? 'Receiver detected · LoRa ready · waiting for sensor packets' : 'Receiver detected · LoRa unavailable: check receiver wiring and power');
      return;
    }
    if (message.type === 'ERROR') { el('error').textContent = message.msg || 'Receiver error'; return; }
    if (message.type !== 'RX') return;
    identified = true;
    status('Receiver detected · receiving sensor packets');
    // Complete frames are assembled by the gateway. Retry the same envelope;
    // gateway sequence deduplication prevents duplicate model evaluations.
    for (let attempt = 0; attempt < 2; attempt++) {
      if (stop) return;
      try {
        const response = await fetch(api + '/api/hardware', {
          method: 'POST', headers: {'Content-Type': 'application/json'},
          body: JSON.stringify(message), signal: AbortSignal.timeout(5000)
        });
        if (!response.ok) {
          const error = new Error(`Gateway rejected packet (HTTP ${response.status})`);
          error.permanent = response.status < 500;
          throw error;
        }
        const result = await response.json();
        log(`Packet ${message.size} B · ${result.status}`);
        el('error').textContent = '';
        return;
      } catch (error) { if (attempt || error.permanent) throw error; }
    }
  }
  el('connect').onclick = async () => {
    if (busy) return;
    if (!navigator.serial) {
      el('error').textContent = 'USB access needs Chrome or Edge on localhost. Open this page there, or use the Python serial bridge.';
      return;
    }
    busy = true; stop = false; identified = false;
    el('connect').disabled = true; el('error').textContent = '';
    let identityTimer;
    try {
      const selected = await navigator.serial.requestPort();
      await selected.open({baudRate:115200});
      port = selected;
      el('disconnect').disabled = false;
      status('USB open · identifying receiver…');
      identityTimer = setTimeout(() => {
        if (!identified && port) status('USB open, receiver not identified. Select the receiver port and flash RECEIVER.ino.');
      }, 7000);
      reader = port.readable.getReader();
      const decoder = new TextDecoder();
      let buffer = '';
      while (!stop) {
        const {value, done} = await reader.read();
        if (done) break;
        buffer += decoder.decode(value, {stream:true});
        const lines = buffer.split('\n'); buffer = lines.pop();
        for (const line of lines) {
          if (stop) break;
          if (line.length > 4096) { log('Oversized serial line discarded'); continue; }
          try { await forward(line.trim()); }
          catch (error) { el('error').textContent = 'Reading delivery failed: ' + error.message; }
        }
        if (buffer.length > 4096) { buffer = ''; log('Oversized serial line discarded'); }
      }
    } catch (error) {
      if (!stop && error.name !== 'NotFoundError') el('error').textContent = error.message + '. Close Arduino Serial Monitor or any other USB bridge, then reconnect.';
    } finally {
      clearTimeout(identityTimer);
      if (reader) { reader.releaseLock(); reader = null; }
      if (port) { try { await port.close(); } catch {} port = null; }
      busy = false;
      el('connect').disabled = false; el('disconnect').disabled = true;
      status('USB disconnected · stored readings remain visible with their timestamps');
    }
  };
  el('disconnect').onclick = async () => {
    stop = true; el('disconnect').disabled = true;
    status('Disconnecting USB…');
    if (reader) { try { await reader.cancel(); } catch {} }
  };
  if (navigator.serial) {
    navigator.serial.addEventListener('disconnect', event => {
      if (event.target === port || event.port === port) el('disconnect').onclick();
    });
    navigator.serial.addEventListener('connect', () => {
      if (!busy) status('USB device attached · click Connect receiver USB and select its port');
    });
    navigator.serial.getPorts().then(ports => {
      if (!busy && ports.length) status('Previously authorized USB device available · click Connect receiver USB');
    }).catch(() => {});
  }
})();
