const fs = require('fs');
const path = require('path');

const target = path.join(__dirname, 'index.html');
let html = fs.readFileSync(target, 'utf-8');

// 1. Add Dropdowns
const dropdownsHtml = `
                        <!-- Region Selectors -->
                        <div class="map-filter-bar" style="border-bottom:1px solid var(--panel-border); padding-bottom:12px; margin-bottom:12px;">
                            <select id="countrySelect" class="map-filter-pill" style="appearance:auto; background:white; cursor:pointer;"><option value="IN">India</option></select>
                            <select id="stateSelect" class="map-filter-pill" style="appearance:auto; background:white; cursor:pointer;" onchange="updateDistricts()">
                                <option value="">Select State</option>
                                <option value="Delhi">Delhi</option>
                                <option value="Maharashtra">Maharashtra</option>
                                <option value="Tamil Nadu">Tamil Nadu</option>
                                <option value="Uttar Pradesh">Uttar Pradesh</option>
                                <option value="Andhra Pradesh">Andhra Pradesh</option>
                            </select>
                            <select id="districtSelect" class="map-filter-pill" style="appearance:auto; background:white; cursor:pointer;" onchange="onDistrictChange()">
                                <option value="">Select District</option>
                            </select>
                        </div>
`;
html = html.replace('<!-- Map Filters -->', dropdownsHtml + '\n                        <!-- Map Filters -->');

// 2. Wrap map-shared and add ranking panel
const rankingPanelHtml = `
                            <!-- Hazard Ranking Panel -->
                            <div id="hazardRankingPanel" style="width: 320px; background: white; border-radius: var(--radius-lg); border: 1px solid var(--panel-border); padding: 16px; overflow-y: auto; display: flex; flex-direction: column; gap: 12px; flex-shrink: 0;">
                                <div style="font-weight: 600; color: var(--text-primary); border-bottom: 1px solid var(--panel-border); padding-bottom: 8px;">
                                    ⚠️ Active Hazard Rankings
                                </div>
                                <div id="rankingCards" style="display:flex; flex-direction:column; gap:8px;">
                                    <div style="color:var(--text-secondary); font-size: 0.9rem;">Select a district to view hazard priorities.</div>
                                </div>
                            </div>
`;
html = html.replace('<!-- Bottom-Right Station Telemetry Panel -->', '<!-- Bottom-Right Station Telemetry Panel -->'); // No-op to test location
html = html.replace('<div class="shared-map-frame">', '<div class="shared-map-frame" style="display: flex; gap: 16px; padding: 16px; background: var(--bg-deep);">');
html = html.replace('<div id="map-shared" class="main-shared-map-canvas"></div>', '<div id="map-shared" class="main-shared-map-canvas" style="flex: 1; border-radius: var(--radius-lg); min-height: 500px; border: 1px solid var(--panel-border);"></div>' + rankingPanelHtml);


// 3. Add script block for Google Maps Key loading at the very end before </body>
const mapsInjectionJS = `
<script>
    // Fetch Google Maps API Key
    fetch('http://localhost:8007/api/maps-key')
        .then(res => res.json())
        .then(data => {
            if (data.key) {
                const script = document.createElement('script');
                script.src = 'https://maps.googleapis.com/maps/api/js?key=' + data.key + '&libraries=places';
                script.async = true;
                script.defer = true;
                script.onload = () => {
                    console.log('Google Maps loaded');
                    setTimeout(() => initSharedMap('all'), 500); // Re-initialize shared map after load
                };
                document.head.appendChild(script);
            }
        }).catch(err => console.error('Failed to fetch Maps Key', err));
</script>
</body>
`;
html = html.replace('</body>', mapsInjectionJS);

// 4. Extended Pins Array (find and replace the old allPins)
const oldPinsRegex = /const allPins = \[([\s\S]*?)\];/;
const newPins = `const allPins = [
        { lat: 28.6139, lon: 77.2090, name: 'Delhi Yamuna Hydro Node (FLD-101)', color: '#00d2ff', desc: '💧 Flood Hydro-Sensor', state: 'Delhi', district: 'New Delhi', hazard: 'flood', severity: 85, confidence: 92, trend: 'rising', node_count: 4 },
        { lat: 25.3176, lon: 82.9739, name: 'Varanasi Ganga Station (FLD-102)', color: '#00d2ff', desc: '💧 Flood Hydro-Sensor', state: 'Uttar Pradesh', district: 'Varanasi', hazard: 'flood', severity: 65, confidence: 88, trend: 'stable', node_count: 2 },
        { lat: 18.5204, lon: 73.8567, name: 'Pune Forest Station (FWF-01)', color: '#ff5722', desc: '🔥 Wildfire Node', state: 'Maharashtra', district: 'Pune', hazard: 'fire', severity: 92, confidence: 95, trend: 'rising', node_count: 5 },
        { lat: 11.1085, lon: 77.3411, name: 'Nilgiris Forest Reserve (FWF-02)', color: '#ff5722', desc: '🔥 Wildfire Node', state: 'Tamil Nadu', district: 'Nilgiris', hazard: 'fire', severity: 45, confidence: 80, trend: 'falling', node_count: 1 },
        { lat: 18.4350, lon: 73.7915, name: 'Pune CWPRS Station (HT-01)', color: '#fbbf24', desc: '☀️ Extreme Heat Node', state: 'Maharashtra', district: 'Pune', hazard: 'heat', severity: 88, confidence: 90, trend: 'rising', node_count: 3 },
        { lat: 17.6868, lon: 83.2185, name: 'Vizag Industrial Belt (IND-01)', color: '#a855f7', desc: '⚠️ Toxic Plume Node', state: 'Andhra Pradesh', district: 'Visakhapatnam', hazard: 'ind', severity: 75, confidence: 85, trend: 'stable', node_count: 2 },
        { lat: 17.7285, lon: 83.3015, name: 'Godavari Reservoir (WTR-01)', color: '#0ea5e9', desc: '🌊 Water Quality Node', state: 'Andhra Pradesh', district: 'Visakhapatnam', hazard: 'water', severity: 55, confidence: 75, trend: 'stable', node_count: 1 },
        { lat: 28.6289, lon: 77.2408, name: 'Delhi ITO CPCB Station (AIR-01)', color: '#2dd4bf', desc: '💨 Air Quality Node', state: 'Delhi', district: 'New Delhi', hazard: 'air', severity: 95, confidence: 98, trend: 'rising', node_count: 6 }
    ];`;
html = html.replace(oldPinsRegex, newPins);

// 5. Update filter code that used array indices (p[4]) to use object properties
html = html.replace(/pinsToRender = allPins\.filter\(p => p\[4\]\.includes\(icon\)\);/g, "pinsToRender = allPins.filter(p => p.desc.includes(icon));");

// Update mkGoogleMap call to use objects
html = html.replace(/\[p\[0\], p\[1\], p\[2\], p\[3\], p\[4\]\]/g, "[p.lat, p.lon, p.name, p.color, p.desc]"); // if mapped somewhere else
// Actually, let's inject a rewritten initSharedMap entirely because it needs Geocoder logic.
const newInitSharedMap = `
// ================== HAZARD RANKING & GEOCODING LOGIC ==================
const districtsByState = {
    'Delhi': ['New Delhi', 'North Delhi', 'South Delhi'],
    'Maharashtra': ['Pune', 'Mumbai', 'Nagpur', 'Thane'],
    'Tamil Nadu': ['Chennai', 'Coimbatore', 'Nilgiris', 'Madurai'],
    'Uttar Pradesh': ['Lucknow', 'Varanasi', 'Kanpur'],
    'Andhra Pradesh': ['Visakhapatnam', 'Vijayawada', 'Guntur']
};

function updateDistricts() {
    const state = document.getElementById('stateSelect').value;
    const districtSelect = document.getElementById('districtSelect');
    districtSelect.innerHTML = '<option value="">Select District</option>';
    if (districtsByState[state]) {
        districtsByState[state].forEach(d => {
            districtSelect.innerHTML += \`<option value="\${d}">\${d}</option>\`;
        });
    }
}

let sharedGoogleMap = null;
let districtPolygon = null;

function onDistrictChange() {
    const state = document.getElementById('stateSelect').value;
    const district = document.getElementById('districtSelect').value;
    if (!state || !district) return;

    rankHazards(district);

    if (window.google && window.google.maps && sharedGoogleMap) {
        const geocoder = new google.maps.Geocoder();
        const address = \`\${district}, \${state}, India\`;
        
        geocoder.geocode({ address: address }, (results, status) => {
            if (status === 'OK' && results[0]) {
                sharedGoogleMap.fitBounds(results[0].geometry.viewport);
                
                // Draw mock polygon for district boundary using viewport corners
                if (districtPolygon) districtPolygon.setMap(null);
                
                const bounds = results[0].geometry.viewport;
                const ne = bounds.getNorthEast();
                const sw = bounds.getSouthWest();
                const coords = [
                    { lat: ne.lat(), lng: sw.lng() },
                    { lat: ne.lat(), lng: ne.lng() },
                    { lat: sw.lat(), lng: ne.lng() },
                    { lat: sw.lat(), lng: sw.lng() }
                ];

                districtPolygon = new google.maps.Polygon({
                    paths: coords,
                    strokeColor: "#1b6343",
                    strokeOpacity: 0.8,
                    strokeWeight: 2,
                    fillColor: "#1b6343",
                    fillOpacity: 0.1,
                    map: sharedGoogleMap
                });
            } else {
                console.warn('Geocode was not successful: ' + status);
            }
        });
    }
}

function rankHazards(district) {
    const districtPins = allPins.filter(p => p.district === district);
    
    // Calculate priority rank: Severity (0-100) + Confidence (0-100) + TrendBonus (Rising=20, Stable=0, Falling=-10) + NodeCount(x5)
    districtPins.forEach(p => {
        let trendBonus = p.trend === 'rising' ? 20 : (p.trend === 'falling' ? -10 : 0);
        p.priority_rank = p.severity + p.confidence + trendBonus + (p.node_count * 5);
    });

    // Sort by priority rank descending
    districtPins.sort((a, b) => b.priority_rank - a.priority_rank);

    // Update UI
    const container = document.getElementById('rankingCards');
    container.innerHTML = '';
    
    if (districtPins.length === 0) {
        container.innerHTML = '<div style="color:var(--text-secondary); font-size: 0.9rem;">No active hazard nodes in this district.</div>';
    } else {
        districtPins.forEach((p, idx) => {
            const isTop = idx === 0;
            const card = document.createElement('div');
            card.style.cssText = \`border: 1px solid \${p.color}; border-left: 4px solid \${p.color}; border-radius: 6px; padding: 12px; background: \${isTop ? p.color+'10' : '#f9fafb'};\`;
            card.innerHTML = \`
                <div style="font-weight: 600; color: var(--text-primary); margin-bottom: 4px;">#\${idx+1} \${p.desc.split('·')[0]}</div>
                <div style="font-size: 0.85rem; color: var(--text-secondary); display: grid; grid-template-columns: 1fr 1fr; gap: 4px;">
                    <div>Severity: <strong style="color:\${p.severity > 80 ? 'red' : 'inherit'}">\${p.severity}</strong></div>
                    <div>Confidence: <strong>\${p.confidence}%</strong></div>
                    <div>Trend: <strong style="text-transform: capitalize;">\${p.trend}</strong></div>
                    <div>Rank Score: <strong>\${p.priority_rank}</strong></div>
                </div>
            \`;
            container.appendChild(card);
        });
    }
    
    // Notify chatbot widget of context update
    const chatbot = document.querySelector('terra-edge-chat');
    if (chatbot && chatbot.updateContext) {
        chatbot.updateContext({
            selectedState: document.getElementById('stateSelect').value,
            selectedDistrict: district,
            hazardRanking: districtPins.map(p => ({ hazard: p.hazard, rank: p.priority_rank, severity: p.severity }))
        });
    }

    // Re-render map with only district pins
    if (window.google && window.google.maps) {
        // Redraw shared map
        maps.shared = mkGoogleMap('map-shared', 20.5937, 78.9629, 5, 'Regional Control Center Map', districtPins.map(p => [p.lat, p.lon, p.name, p.color, p.desc]));
        sharedGoogleMap = maps.shared;
    }
}

function initSharedMap(hazardFilter = 'all') {
    const el = document.getElementById('map-shared');
    if (!el) return;
    
    let pinsToRender = allPins;
    if (hazardFilter !== 'all') {
        const keywordMap = {
            'flood': '💧', 'fire': '🔥', 'land': '⛰️', 'air': '💨',
            'heat': '☀️', 'ind': '⚠️', 'water': '🌊'
        };
        const icon = keywordMap[hazardFilter];
        pinsToRender = allPins.filter(p => p.desc.includes(icon));
    }

    // Convert object to array format for mkGoogleMap
    const pinArrays = pinsToRender.map(p => [p.lat, p.lon, p.name, p.color, p.desc]);

    if (window.google && window.google.maps) {
        maps.shared = mkGoogleMap('map-shared', 20.5937, 78.9629, 5, 'Regional Control Center Map', pinArrays);
        sharedGoogleMap = maps.shared;
    } else {
        renderFallbackSharedMap('map-shared', pinArrays);
    }
}
// ======================================================================
`;
// Replace the old initSharedMap with the new block (removing up to line 4306)
const initMapRegex = /function initSharedMap\([\s\S]*?\}\s*\n\}\s*/;
html = html.replace(initMapRegex, newInitSharedMap);

fs.writeFileSync(target, html);
console.log('Successfully updated index.html');
