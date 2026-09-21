/* Hardware-only summary. Scenario/map data never enters these assessments. */
(() => {
  const el = id => document.getElementById(id);
  const api = `${location.protocol}//${location.hostname}:8000`;
  const modelNames = ['Flood','Wildfire','Landslide','Air Quality','Extreme Heat','Industrial Emissions','Water Quality'];
  let snapshot = {nodes: []}, online = false;
  const text = (id, value) => { el(id).textContent = value; };
  function render() {
    const node = snapshot.nodes.find(n => n.node_id === el('ops-node').value);
    text('ops-nodes', online ? snapshot.nodes.length : '—');
    text('ops-node-note', online ? 'Gateway connected' : 'Gateway unavailable');
    el('ops-empty').hidden = Boolean(node);
    el('ops-results').replaceChildren(); el('ops-alerts').replaceChildren();
    if (!node) {
      ['ops-age','ops-models','ops-alert-count'].forEach(id => text(id,'—'));
      text('ops-source','No hardware reading');
      text('ops-status', online ? 'Waiting for a complete packet from the receiver.' : 'Start the project gateway to receive hardware data.');
      return;
    }
    const age = Math.max(0, Math.floor((Date.now() - Date.parse(node.timestamp)) / 1000));
    const stale = !Number.isFinite(age) || age > 30 || !online;
    text('ops-age', Number.isFinite(age) ? (age < 60 ? `${age}s ago` : `${Math.floor(age/60)}m ago`) : 'Unknown');
    text('ops-source', `${node.node_id}${stale ? ' · Stale' : ' · Current'}`);
    const results = node.hazard_results || {}, alerts = node.alerts_triggered || [];
    const entries = Object.entries(results);
    text('ops-models', `${entries.filter(([,r])=>r.model_status === 'success').length} / ${entries.length || 7}`);
    text('ops-alert-count', alerts.length);
    text('ops-status', `${online ? 'Gateway connected' : 'Gateway unavailable'} · ${stale ? 'Last known reading; waiting for fresh data' : 'Current reading'} · ${new Date(node.timestamp).toLocaleString()}`);
    for (const alert of alerts) {
      const item = document.createElement('div'); item.className = 'alert';
      item.textContent = `${stale ? 'Last reading · ' : ''}${alert.severity}: ${alert.details?.message || alert.top_features?.join(', ') || 'Model threshold crossed'}`;
      el('ops-alerts').append(item);
    }
    for (const [name, result] of entries.length ? entries : modelNames.map(n=>[n,{}])) {
      const card = document.createElement('article'); card.className = 'model-result';
      const title = document.createElement('h3'); title.textContent = name;
      const value = document.createElement('strong');
      const valid = result.model_status === 'success' && Number.isFinite(result.risk_pct);
      value.textContent = valid ? `${result.risk_pct}% risk` : 'Unavailable';
      const detail = document.createElement('p');
      detail.textContent = valid ? `${result.severity || 'Unclassified'} · ${stale ? 'Last known result' : 'Current result'}` : result.skip_reason || result.error || 'Waiting for compatible inputs';
      const confidence = document.createElement('small');
      confidence.textContent = valid && Number.isFinite(result.confidence_pct) ? `Input confidence ${result.confidence_pct}%` : 'Input confidence unavailable';
      card.append(title,value,detail,confidence); el('ops-results').append(card);
    }
  }
  async function refresh() {
    try {
      const response = await fetch(`${api}/api/hardware/latest`, {signal:AbortSignal.timeout(5000)});
      if (!response.ok) throw Error(response.status);
      const next = await response.json();
      if (!Array.isArray(next.nodes)) throw Error('Invalid node response');
      snapshot = next; online = true;
      const previous = el('ops-node').value;
      const ids = snapshot.nodes.map(n=>n.node_id);
      if (JSON.stringify(ids) !== JSON.stringify(Array.from(el('ops-node').options).map(o=>o.value))) {
        el('ops-node').replaceChildren();
        for (const node of snapshot.nodes) { const option=document.createElement('option'); option.value=node.node_id; option.textContent=node.node_id; el('ops-node').append(option); }
        if (!snapshot.nodes.length) { const option=document.createElement('option'); option.value=''; option.textContent='No hardware nodes'; el('ops-node').append(option); }
        if(ids.includes(previous))el('ops-node').value=previous;
      }
    } catch { online = false; }
    render(); setTimeout(refresh,3000);
  }
  el('ops-node').addEventListener('change',render);
  refresh();
})();
