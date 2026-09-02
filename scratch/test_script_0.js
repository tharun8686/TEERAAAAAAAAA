

// ─── DYNAMIC PROCEDURAL BACKGROUND ENGINE ────────────────────
const canvas = document.getElementById('bg-canvas');
const ctx = canvas.getContext('2d');
let cw, ch;
let currentBgTheme = 'all';

function resizeCanvas() {
    cw = canvas.width = window.innerWidth;
    ch = canvas.height = window.innerHeight;
}
window.addEventListener('resize', resizeCanvas);
resizeCanvas();

// Particle & Vector Pools
const meshNodes = Array.from({length: 42}, () => ({
    x: Math.random() * window.innerWidth,
    y: Math.random() * window.innerHeight,
    vx: (Math.random() - 0.5) * 0.6,
    vy: (Math.random() - 0.5) * 0.6,
    radius: Math.random() * 2 + 1.5,
    pulse: Math.random() * Math.PI * 2
}));

const embers = Array.from({length: 55}, () => ({
    x: Math.random() * window.innerWidth,
    y: Math.random() * window.innerHeight,
    vx: (Math.random() - 0.5) * 0.8,
    vy: -(Math.random() * 1.5 + 0.6),
    size: Math.random() * 3 + 1,
    opacity: Math.random() * 0.8 + 0.2,
    color: ['#ff5722', '#dc2626', '#f59e0b', '#fb923c'][Math.floor(Math.random()*4)]
}));

const waterBubbles = Array.from({length: 45}, () => ({
    x: Math.random() * window.innerWidth,
    y: Math.random() * window.innerHeight,
    vy: -(Math.random() * 0.8 + 0.3),
    vx: Math.sin(Math.random()*Math.PI) * 0.4,
    size: Math.random() * 2.5 + 1,
    alpha: Math.random() * 0.6 + 0.2
}));

const windStreams = Array.from({length: 50}, () => ({
    x: Math.random() * window.innerWidth,
    y: Math.random() * window.innerHeight,
    vx: Math.random() * 2.5 + 1.2,
    len: Math.random() * 40 + 20,
    alpha: Math.random() * 0.5 + 0.15,
    color: ['#2dd4bf', '#0d9488', '#38bdf8', '#06b6d4'][Math.floor(Math.random()*4)]
}));

let waveOffset = 0;

function renderBgAnimation() {
    ctx.clearRect(0, 0, cw, ch);

    if (currentBgTheme === 'all') {
        // ─── LoRa Mesh Network Animation ───
        meshNodes.forEach(node => {
            node.x += node.vx;
            node.y += node.vy;
            node.pulse += 0.03;
            if (node.x < 0 || node.x > cw) node.vx *= -1;
            if (node.y < 0 || node.y > ch) node.vy *= -1;

            // Draw Node
            const pSize = node.radius + Math.sin(node.pulse) * 0.8;
            ctx.beginPath();
            ctx.arc(node.x, node.y, Math.max(1, pSize), 0, Math.PI * 2);
            ctx.fillStyle = 'rgba(0, 210, 255, 0.65)';
            ctx.shadowBlur = 8;
            ctx.shadowColor = '#00d2ff';
            ctx.fill();
            ctx.shadowBlur = 0;
        });

        // Draw connections
        for (let i = 0; i < meshNodes.length; i++) {
            for (let j = i + 1; j < meshNodes.length; j++) {
                const dx = meshNodes[i].x - meshNodes[j].x;
                const dy = meshNodes[i].y - meshNodes[j].y;
                const dist = Math.sqrt(dx * dx + dy * dy);
                if (dist < 140) {
                    ctx.beginPath();
                    ctx.moveTo(meshNodes[i].x, meshNodes[i].y);
                    ctx.lineTo(meshNodes[j].x, meshNodes[j].y);
                    const alpha = (1 - dist / 140) * 0.22;
                    ctx.strokeStyle = `rgba(0, 210, 255, ${alpha})`;
                    ctx.lineWidth = 1;
                    ctx.stroke();
                }
            }
        }
    } 
    else if (currentBgTheme === 'flood') {
        // ─── 02: PROFESSIONAL BATHYMETRIC DOPPLER HYDROLOGY & SONAR MATRIX ───
        waveOffset += 0.015;

        // Faint Coordinate Grid & River Axis Crosshairs
        ctx.strokeStyle = 'rgba(0, 210, 255, 0.035)';
        ctx.lineWidth = 0.6;
        for (let x = 0; x < cw; x += 140) {
            ctx.beginPath(); ctx.moveTo(x, 0); ctx.lineTo(x, ch); ctx.stroke();
        }
        for (let y = 0; y < ch; y += 100) {
            ctx.beginPath(); ctx.moveTo(0, y); ctx.lineTo(cw, y); ctx.stroke();
        }

        // 8 Precision Bathymetric Depth Isolines
        for (let i = 0; i < 8; i++) {
            const yBase = ch * (0.25 + i * 0.08);
            const alpha = 0.08 + (i % 3) * 0.05;
            ctx.strokeStyle = `rgba(0, 210, 255, ${alpha})`;
            ctx.lineWidth = 0.8;
            ctx.beginPath();
            
            for (let x = 0; x <= cw; x += 18) {
                const y = yBase 
                    + Math.sin(x * 0.003 + waveOffset * 0.7 + i * 0.8) * 24 
                    + Math.cos(x * 0.007 - waveOffset * 0.5 + i) * 12;
                if (x === 0) ctx.moveTo(x, y);
                else ctx.lineTo(x, y);
            }
            ctx.stroke();
        }

        // Hydrometric Velocity Streamline Arrows along River Profile
        ctx.fillStyle = 'rgba(0, 210, 255, 0.3)';
        for (let i = 0; i < 6; i++) {
            const ax = ((waveOffset * 90 + i * (cw / 6)) % cw);
            const ay = ch * 0.38 + Math.sin(ax * 0.003 + waveOffset) * 25 + (i % 3) * 65;
            ctx.beginPath();
            ctx.moveTo(ax, ay);
            ctx.lineTo(ax - 9, ay - 3.5);
            ctx.lineTo(ax - 9, ay + 3.5);
            ctx.closePath();
            ctx.fill();
        }

        // Technical HUD Telemetry Overlay
        ctx.font = '10px "JetBrains Mono", monospace';
        ctx.fillStyle = 'rgba(0, 210, 255, 0.28)';
        ctx.fillText('INDO-GANGETIC BASIN HYDRO-SURGE PROFILE · VELOCITY: 0.84 m/s · STAGE: +1.2m', 40, ch - 30);
    }
    else if (currentBgTheme === 'fire') {
        // ─── 03: DYNAMIC MODIS THERMAL INFRARED & CONVECTIVE HEAT DYNAMICS ───
        waveOffset += 0.022;

        // Faint Coordinate Grid
        ctx.strokeStyle = 'rgba(255, 87, 34, 0.04)';
        ctx.lineWidth = 0.6;
        for (let x = 0; x < cw; x += 120) {
            ctx.beginPath(); ctx.moveTo(x, 0); ctx.lineTo(x, ch); ctx.stroke();
        }
        for (let y = 0; y < ch; y += 100) {
            ctx.beginPath(); ctx.moveTo(0, y); ctx.lineTo(cw, y); ctx.stroke();
        }

        // Active Pulsing Thermal Infrared Isotherm Hotspots
        const hotspots = [
            { x: cw * 0.28, y: ch * 0.62, label: 'ZONE-A1 (Goa)' },
            { x: cw * 0.58, y: ch * 0.48, label: 'ZONE-B2 (MP)' },
            { x: cw * 0.76, y: ch * 0.68, label: 'ZONE-C3 (Nilgiris)' }
        ];

        hotspots.forEach((hs, idx) => {
            for (let r = 1; r <= 4; r++) {
                const rad = (waveOffset * 35 + r * 55 + idx * 30) % 220;
                const alpha = Math.max(0, (1 - rad / 220) * 0.32);
                ctx.strokeStyle = `rgba(255, 87, 34, ${alpha})`;
                ctx.lineWidth = 0.9;
                ctx.beginPath();
                ctx.arc(hs.x, hs.y, rad, 0, Math.PI * 2);
                ctx.stroke();
            }

            // Core Hotspot Marker
            ctx.fillStyle = '#ff5722';
            ctx.beginPath();
            ctx.arc(hs.x, hs.y, 4 + Math.sin(waveOffset * 3 + idx) * 1.5, 0, Math.PI * 2);
            ctx.shadowBlur = 12;
            ctx.shadowColor = '#ff5722';
            ctx.fill();
            ctx.shadowBlur = 0;

            ctx.font = '9px "JetBrains Mono", monospace';
            ctx.fillStyle = 'rgba(255, 87, 34, 0.6)';
            ctx.fillText(hs.label, hs.x + 8, hs.y + 3);
        });

        // 18 Weaving Convective Heat & Thermal Updraft Streamlines
        ctx.lineWidth = 0.85;
        for (let i = 0; i < 18; i++) {
            const hx = (i * (cw / 18)) + Math.sin(waveOffset * 1.2 + i * 2) * 22;
            const y1 = ch;
            const y2 = ch * 0.12;
            const grad = ctx.createLinearGradient(hx, y1, hx, y2);
            grad.addColorStop(0, 'rgba(255, 87, 34, 0.35)');
            grad.addColorStop(0.5, 'rgba(245, 158, 11, 0.18)');
            grad.addColorStop(1, 'rgba(220, 38, 38, 0.0)');
            ctx.strokeStyle = grad;
            ctx.beginPath();
            ctx.moveTo(hx, y1);
            const cx1 = hx + Math.sin(waveOffset * 2.0 + i) * 45;
            const cx2 = hx - Math.cos(waveOffset * 1.8 + i) * 35;
            ctx.bezierCurveTo(cx1, ch * 0.65, cx2, ch * 0.35, hx, y2);
            ctx.stroke();
        }

        // Rising Luminous Thermal Ember Sparks
        for (let k = 0; k < 30; k++) {
            const ex = (k * 67 + Math.sin(waveOffset * 1.5 + k) * 30) % cw;
            const ey = ((ch - (waveOffset * 110 + k * 45) % ch));
            const sz = 1.2 + (k % 3) * 0.8;
            const alpha = 0.25 + Math.sin(waveOffset * 3 + k) * 0.2;
            ctx.fillStyle = k % 2 === 0 ? `rgba(255, 87, 34, ${alpha})` : `rgba(245, 158, 11, ${alpha})`;
            ctx.beginPath();
            ctx.arc(ex, ey, sz, 0, Math.PI * 2);
            ctx.fill();
        }

        // Technical HUD Telemetry Overlay
        ctx.font = '10px "JetBrains Mono", monospace';
        ctx.fillStyle = 'rgba(255, 87, 34, 0.32)';
        ctx.fillText('DYNAMIC CANOPY THERMAL FLUX · CONVECTIVE RADIATIVE SPREAD · MQ-135 / SHT40', 40, ch - 30);
    }
    else if (currentBgTheme === 'land') {
        // ─── 04: DYNAMIC 3D TOPOGRAPHIC DEM TERRAIN & SEISMIC PULSE MATRIX ───
        waveOffset += 0.02;

        // Faint Coordinate Elevation Grid
        ctx.strokeStyle = 'rgba(245, 158, 11, 0.035)';
        ctx.lineWidth = 0.6;
        for (let x = 0; x < cw; x += 120) {
            ctx.beginPath(); ctx.moveTo(x, 0); ctx.lineTo(x, ch); ctx.stroke();
        }

        // Multi-Layer Dynamic Undulating 3D Topographic DEM Mesh
        ctx.lineWidth = 0.85;
        const cols = 16, rows = 11;
        const gridW = cw * 0.94, gridH = ch * 0.72;
        const startX = cw * 0.03, startY = ch * 0.15;

        for (let r = 0; r < rows; r++) {
            const rowAlpha = 0.08 + (r / rows) * 0.16;
            ctx.strokeStyle = `rgba(245, 158, 11, ${rowAlpha})`;
            ctx.beginPath();
            for (let c = 0; c <= cols; c++) {
                const px = startX + (c / cols) * gridW;
                // Double harmonic spatial undulation to simulate live slope strain
                const elev = Math.sin(c * 0.5 + waveOffset * 0.8 + r * 0.6) * 26
                           + Math.cos(r * 0.7 - waveOffset * 0.6 + c * 0.3) * 18;
                const py = startY + (r / rows) * gridH + elev;
                if (c === 0) ctx.moveTo(px, py);
                else ctx.lineTo(px, py);
            }
            ctx.stroke();
        }

        // Vertical connecting slope triangulation ribs
        ctx.lineWidth = 0.5;
        ctx.strokeStyle = 'rgba(245, 158, 11, 0.06)';
        for (let c = 0; c <= cols; c += 2) {
            ctx.beginPath();
            for (let r = 0; r < rows; r++) {
                const px = startX + (c / cols) * gridW;
                const elev = Math.sin(c * 0.5 + waveOffset * 0.8 + r * 0.6) * 26
                           + Math.cos(r * 0.7 - waveOffset * 0.6 + c * 0.3) * 18;
                const py = startY + (r / rows) * gridH + elev;
                if (r === 0) ctx.moveTo(px, py);
                else ctx.lineTo(px, py);
            }
            ctx.stroke();
        }

        // Active Seismic Wavefront Centers (Epicenters along fault lines)
        const epicenters = [
            { x: cw * 0.35, y: ch * 0.58, label: 'FAULT-WGH-01' },
            { x: cw * 0.72, y: ch * 0.46, label: 'FAULT-VALP-02' }
        ];

        epicenters.forEach((ep, eIdx) => {
            for (let k = 0; k < 4; k++) {
                const rad = ((waveOffset * 40 + k * 70 + eIdx * 45) % 280);
                const alpha = Math.max(0, (1 - rad / 280) * 0.3);
                ctx.strokeStyle = `rgba(245, 158, 11, ${alpha})`;
                ctx.lineWidth = 1.0;
                ctx.beginPath();
                ctx.arc(ep.x, ep.y, rad, 0, Math.PI * 2);
                ctx.stroke();
            }

            // Epicenter Node Point
            ctx.fillStyle = '#f59e0b';
            ctx.beginPath();
            ctx.arc(ep.x, ep.y, 4 + Math.sin(waveOffset * 3 + eIdx) * 1.5, 0, Math.PI * 2);
            ctx.shadowBlur = 10;
            ctx.shadowColor = '#f59e0b';
            ctx.fill();
            ctx.shadowBlur = 0;

            ctx.font = '9px "JetBrains Mono", monospace';
            ctx.fillStyle = 'rgba(245, 158, 11, 0.6)';
            ctx.fillText(ep.label, ep.x + 8, ep.y + 3);
        });

        // Directional Shear Strain Vectors along the slope
        ctx.fillStyle = 'rgba(245, 158, 11, 0.35)';
        for (let i = 0; i < 5; i++) {
            const sx = ((waveOffset * 75 + i * (cw / 5)) % cw);
            const sy = ch * 0.42 + Math.sin(sx * 0.003 + waveOffset) * 30 + (i % 2) * 80;
            ctx.beginPath();
            ctx.moveTo(sx, sy);
            ctx.lineTo(sx - 8, sy - 4);
            ctx.lineTo(sx - 8, sy + 4);
            ctx.closePath();
            ctx.fill();
        }

        // Technical HUD Telemetry Overlay
        ctx.font = '10px "JetBrains Mono", monospace';
        ctx.fillStyle = 'rgba(245, 158, 11, 0.32)';
        ctx.fillText('DYNAMIC 3D DEM TOPOGRAPHY · SEISMIC SHEAR DISPLACEMENT · MPU-6050 6-DoF INCLINE', 40, ch - 30);
    }
    else if (currentBgTheme === 'air') {
        // ─── 05: CAAQM AERODYNAMIC DISPERSION VECTORS & AIRFLOW ISOPLETHS ───
        waveOffset += 0.015;

        // Aerodynamic Velocity Streamlines
        ctx.lineWidth = 0.85;
        for (let i = 0; i < 16; i++) {
            const yBase = ch * (0.12 + i * 0.052);
            const speed = 1.0 + (i % 3) * 0.35;
            const alpha = 0.06 + (i % 2) * 0.06;
            ctx.strokeStyle = `rgba(45, 212, 191, ${alpha})`;
            ctx.beginPath();
            
            for (let x = 0; x <= cw; x += 22) {
                const y = yBase + Math.sin(x * 0.0035 + waveOffset * speed + i) * 16;
                if (x === 0) ctx.moveTo(x, y);
                else ctx.lineTo(x, y);
            }
            ctx.stroke();
        }

        // CAAQM Laser Optical Dispersion Pointers
        ctx.fillStyle = 'rgba(45, 212, 191, 0.32)';
        for (let k = 0; k < 8; k++) {
            const px = ((waveOffset * 105 + k * (cw / 8)) % cw);
            const py = ch * 0.18 + (k * 48) + Math.sin(px * 0.0035 + waveOffset) * 16;
            ctx.beginPath();
            ctx.arc(px, py, 2, 0, Math.PI * 2);
            ctx.fill();
        }

        // Technical HUD Telemetry Overlay
        ctx.font = '10px "JetBrains Mono", monospace';
        ctx.fillStyle = 'rgba(45, 212, 191, 0.28)';
        ctx.fillText('CAAQM AEROSOL DISPERSION FIELD · 30m/60m FORWARD VECTOR PROJECTION · CPCB ITO', 40, ch - 30);
    }

    requestAnimationFrame(renderBgAnimation);
}
renderBgAnimation();

function setBgTheme(themeName) {
    currentBgTheme = themeName;
    const aura = document.getElementById('ambient-aura');
    if (aura) {
        aura.className = `ambient-aura theme-${themeName}`;
    }
}

// ─── VIEW CONTROLLER ─────────────────────────────────────────
let maps = {};
const ALL_MODELS = ['flood', 'fire', 'land', 'air', 'heat', 'ind', 'water'];

function openOverview(targetSectionId) {
    document.getElementById('view-consoles').style.display = 'none';
    document.getElementById('view-overview').style.display = 'flex';
    setBgTheme('all');
    if(targetSectionId) {
        const el = document.getElementById(targetSectionId);
        if(el) el.scrollIntoView({behavior: 'smooth'});
    } else {
        window.scrollTo({top: 0, behavior: 'smooth'});
    }
}

function scrollToSection(targetSectionId) {
    openOverview(targetSectionId);
}

// Case A: Open ONLY that particular model when clicking its card
function openSingleModel(modKey) {
    document.getElementById('view-overview').style.display = 'none';
    document.getElementById('view-consoles').style.display = 'flex';
    setBgTheme(modKey);
    try { window.location.hash = modKey; } catch(e) {}

    // Display exclusively the selected model console
    ALL_MODELS.forEach(m => {
        const c = document.getElementById(`console-${m}`);
        if(c) c.style.display = (m === modKey) ? 'flex' : 'none';
        const p = document.getElementById(`pill-${m}`);
        if(p) p.classList.toggle('active-pill', m === modKey);
    });
    const allPill = document.getElementById('pill-all');
    if(allPill) allPill.classList.remove('active-pill');

    window.scrollTo({top: 0, behavior: 'smooth'});
    setTimeout(() => {
        if(maps[modKey]) {
            if (maps[modKey].invalidateSize) {
                maps[modKey].invalidateSize();
            } else if (window.google && window.google.maps) {
                google.maps.event.trigger(maps[modKey], 'resize');
            }
        }
    }, 120);
}

// Case B: Open ALL models when clicking the Live Consoles button (all 4 scrollable)
function openAllConsoles() {
    document.getElementById('view-overview').style.display = 'none';
    document.getElementById('view-consoles').style.display = 'flex';
    setBgTheme('all');

    // Make all 4 models visible in continuous feed
    ALL_MODELS.forEach(m => {
        const c = document.getElementById(`console-${m}`);
        if(c) c.style.display = 'flex';
        const p = document.getElementById(`pill-${m}`);
        if(p) p.classList.remove('active-pill');
    });
    const allPill = document.getElementById('pill-all');
    if(allPill) allPill.classList.add('active-pill');

    window.scrollTo({top: 0, behavior: 'smooth'});
    setTimeout(() => {
        ALL_MODELS.forEach(k => {
            if(maps[k]) {
                if (maps[k].invalidateSize) {
                    maps[k].invalidateSize();
                } else if (window.google && window.google.maps) {
                    google.maps.event.trigger(maps[k], 'resize');
                }
            }
        });
    }, 100);
}

// ─── RDR2 RADIAL SELECTION WHEEL CONTROLLER ─────────────────
const RDR_MODEL_DATA = {
    flood: {
        icon: '💧',
        title: 'SentinLEdge Flood AI',
        category: '01 / FLOOD & INUNDATION',
        desc: 'River surge detection, rapid soil moisture infiltration, and basin inundation risk.',
        action: 'EXPLORE FLOOD CONSOLE ➔'
    },
    fire: {
        icon: '🔥',
        title: 'ForestWildFire AI',
        category: '02 / WILDFIRE COMBUSTION',
        desc: 'Smoldering combustion gas signatures, vapor pressure deficits, and canopy drought stress.',
        action: 'EXPLORE WILDFIRE CONSOLE ➔'
    },
    land: {
        icon: '⛰️',
        title: 'Landslide Edge AI',
        category: '03 / SLIP & SLOPE INSTABILITY',
        desc: 'Micro-angular slope displacement, pore-water pressure spikes, and seismic shear pulses.',
        action: 'EXPLORE LANDSLIDE CONSOLE ➔'
    },
    air: {
        icon: '💨',
        title: 'AirPollution AI',
        category: '04 / AIR QUALITY & PARTICULATES',
        desc: 'CPCB CAAQM-calibrated 30/60-minute forward particulate projections and toxic air trends.',
        action: 'EXPLORE AIR CONSOLE ➔'
    },
    heat: {
        icon: '☀️',
        title: 'Extreme Heat AI',
        category: '05 / HEATWAVE STRESS',
        desc: 'Apparent temperature projections, cumulative heat stress, and nighttime cooling failures.',
        action: 'EXPLORE HEAT CONSOLE ➔'
    },
    ind: {
        icon: '⚠️',
        title: 'Toxic Emissions AI',
        category: '06 / INDUSTRIAL TOXIC PLUME',
        desc: 'Gas discriminative array drift compensation, dynamic chemical leaks, and toxic dispersion.',
        action: 'EXPLORE PLUME CONSOLE ➔'
    },
    water: {
        icon: '🌊',
        title: 'Water Quality AI',
        category: '07 / AQUATIC ECOSYSTEM HEALTH',
        desc: 'Early warning systems for municipal reservoirs, pH shift, turbidity spikes, and chemical run-offs.',
        action: 'EXPLORE WATER CONSOLE ➔'
    }
};

function hoverRdrSlice(modKey) {
    const data = RDR_MODEL_DATA[modKey];
    if (!data) return;

    // Highlight slice wedge button
    document.querySelectorAll('.rdr-slice').forEach(el => el.classList.remove('active'));
    const activeSlice = document.querySelector(`.rdr-slice[onclick*="${modKey}"]`);
    if(activeSlice) activeSlice.classList.add('active');

    document.getElementById('rdr-hud-icon').innerText = data.icon;
    document.getElementById('rdr-hud-title').innerText = data.title;
    document.getElementById('rdr-hud-category').innerText = data.category;
    document.getElementById('rdr-hud-desc').innerText = data.desc;
    
    const btn = document.getElementById('rdr-hud-btn');
    btn.innerText = data.action;
    btn.onclick = function() { openSingleModel(modKey); };
}

// ─── GOOGLE MAPS INTEGRATION & INTERACTIVE TELEMETRY NODES ───
// Define global key variable for hardcoding (optional override)
window.GOOGLE_MAPS_API_KEY = "";

// Sleek dark theme configuration for Google Maps vector view
const GOOGLE_MAPS_DARK_STYLE = [
    { elementType: "geometry", stylers: [{ color: "#06070e" }] },
    { elementType: "labels.text.stroke", stylers: [{ color: "#06070e" }] },
    { elementType: "labels.text.fill", stylers: [{ color: "#8a9ba8" }] },
    { featureType: "administrative", elementType: "geometry", stylers: [{ color: "#1c2035" }] },
    { featureType: "water", elementType: "geometry", stylers: [{ color: "#0d111d" }] },
    { featureType: "water", elementType: "labels.text.fill", stylers: [{ color: "#4e5d6c" }] },
    { featureType: "road", elementType: "geometry", stylers: [{ color: "#141829" }] },
    { featureType: "road", elementType: "geometry.stroke", stylers: [{ color: "#1c2035" }] },
    { featureType: "road", elementType: "labels.text.fill", stylers: [{ color: "#6e7e8c" }] },
    { featureType: "poi", elementType: "geometry", stylers: [{ color: "#090c15" }] },
    { featureType: "poi", elementType: "labels.text.fill", stylers: [{ color: "#6e7e8c" }] },
    { featureType: "transit", elementType: "geometry", stylers: [{ color: "#141829" }] }
];

// Custom HTML Marker implementation in Google Maps
let CustomPulseMarker;
function setupCustomMarkerClass() {
    if (typeof google === 'undefined' || typeof google.maps === 'undefined') return;
    
    CustomPulseMarker = class extends google.maps.OverlayView {
        constructor(latlng, map, html, title, popupHtml) {
            super();
            this.latlng = latlng;
            this.html = html;
            this.title = title;
            this.popupHtml = popupHtml;
            this.div = null;
            this.setMap(map);
        }
        
        onAdd() {
            const div = this.div = document.createElement('div');
            div.style.position = 'absolute';
            div.style.cursor = 'pointer';
            div.title = this.title;
            div.innerHTML = this.html;
            
            // Setup InfoWindow popup on click
            const infoWindow = new google.maps.InfoWindow({
                content: this.popupHtml
            });
            
            div.addEventListener('click', () => {
                infoWindow.setPosition(this.latlng);
                infoWindow.open({
                    map: this.getMap(),
                    anchor: this,
                    shouldFocus: false
                });
            });
            
            const panes = this.getPanes();
            panes.overlayMouseTarget.appendChild(div);
        }
        
        draw() {
            const overlayProjection = this.getProjection();
            const position = overlayProjection.fromLatLngToDivPixel(this.latlng);
            if (position && this.div) {
                this.div.style.left = (position.x - 16) + 'px';
                this.div.style.top = (position.y - 16) + 'px';
            }
        }
        
        onRemove() {
            if (this.div) {
                this.div.parentNode.removeChild(this.div);
                this.div = null;
            }
        }
    };
}

function mkGoogleMap(divId, lat, lng, zoom, modelType, pins) {
    const el = document.getElementById(divId);
    if (!el) return null;
    
    // Clear any previous instances or innerHTML
    el.innerHTML = '';
    
    // Check if Google Maps script loaded successfully
    if (typeof google === 'undefined' || typeof google.maps === 'undefined') {
        // Render styled placeholder
        el.innerHTML = `
            <div class="map-placeholder">
                <h3>📍 Google Maps API Required</h3>
                <p>Please configure your <code>GOOGLE_MAPS_API_KEY</code> in the <code>.env</code> file or hardcode it in <code>index.html</code>, and start a backend microservice to enable mapping.</p>
            </div>
        `;
        return null;
    }
    
    // Ensure Custom Marker class is defined
    if (!CustomPulseMarker) {
        setupCustomMarkerClass();
    }
    
    const mapOptions = {
        center: { lat: lat, lng: lng },
        zoom: zoom,
        styles: GOOGLE_MAPS_DARK_STYLE,
        mapTypeId: google.maps.MapTypeId.ROADMAP,
        mapTypeControl: true,
        mapTypeControlOptions: {
            style: google.maps.MapTypeControlStyle.DEFAULT,
            mapTypeIds: [
                google.maps.MapTypeId.ROADMAP,
                google.maps.MapTypeId.SATELLITE,
                google.maps.MapTypeId.HYBRID,
                google.maps.MapTypeId.TERRAIN
            ]
        },
        renderingType: google.maps.RenderingType.VECTOR,
        disableDefaultUI: false,
        zoomControl: true,
        scaleControl: true,
        streetViewControl: false,
        rotateControl: false,
        fullscreenControl: true
    };
    
    let map = null;
    try {
        map = new google.maps.Map(el, mapOptions);
        // Adjust styling when switching to Terrain view to ensure terrain features are visible
        map.addListener('maptypeid_changed', function() {
            if (map.getMapTypeId() === google.maps.MapTypeId.TERRAIN) {
                // Remove dark style for Terrain to display natural shading
                map.setOptions({styles: null});
            } else {
                // Reapply dark style for other map types
                map.setOptions({styles: GOOGLE_MAPS_DARK_STYLE});
            }
        });
        console.log(`Google Maps instance created for ${divId}`);
    } catch (e) {
        console.error(`Failed to create Google Maps for ${divId}:`, e);
        el.innerHTML = `<div style="color:#ff6b6b; padding:10px;">Error loading map. See console for details.</div>`;
        return null;
    }
    
    // Create Custom HUD Watermark & Controls
    const hudDiv = document.createElement('div');
    hudDiv.style.cssText = 'background:rgba(10,16,28,0.92);backdrop-filter:blur(8px);border:1px solid rgba(255,255,255,0.12);padding:6px 12px;border-radius:16px;font-family:var(--font-mono);color:#cbd5e1;box-shadow:0 4px 12px rgba(0,0,0,0.5);margin:10px;pointer-events:auto;';
    
    hudDiv.innerHTML = `
        <div style="font-size:10px;"><span style="color:#00d2ff;">● LIVE</span> ${modelType.toUpperCase()} · ${lat.toFixed(1)}°N, ${lng.toFixed(1)}°E</div>
        <div class="map-hud-modes">
            <span class="map-hud-mode-btn active" data-mode="roadmap">Vector</span>
            <span class="map-hud-mode-btn" data-mode="satellite">Satellite</span>
            <span class="map-hud-mode-btn" data-mode="terrain">Terrain</span>
            <span class="map-hud-mode-btn" data-mode="hybrid">Hybrid</span>
        </div>
    `;
    
    // Add mode buttons click handlers
    const btns = hudDiv.querySelectorAll('.map-hud-mode-btn');
    btns.forEach(btn => {
        btn.addEventListener('click', (e) => {
            e.stopPropagation();
            const mode = btn.getAttribute('data-mode');
            
            // Toggle active class
            btns.forEach(b => b.classList.remove('active'));
            btn.classList.add('active');
            
            // Set Map Type and style with safety checks
            try {
                if (!map) throw new Error('Map instance not available');
                if (mode === 'roadmap') {
                    map.setMapTypeId(google.maps.MapTypeId.ROADMAP);
                    map.setOptions({ styles: GOOGLE_MAPS_DARK_STYLE });
                } else if (mode === 'satellite') {
                    map.setMapTypeId(google.maps.MapTypeId.SATELLITE);
                    map.setOptions({ styles: [] });
                } else if (mode === 'terrain') {
                    map.setMapTypeId(google.maps.MapTypeId.TERRAIN);
                    map.setOptions({ styles: GOOGLE_MAPS_DARK_STYLE });
                } else if (mode === 'hybrid') {
                    map.setMapTypeId(google.maps.MapTypeId.HYBRID);
                    map.setOptions({ styles: [] });
                }
            } catch (err) {
                console.error('Map mode switch error:', err);
            }
        });
    });
    
    map.controls[google.maps.ControlPosition.TOP_RIGHT].push(hudDiv);
    
    // Add custom pulsing pins
    if (pins && CustomPulseMarker && map) {
        pins.forEach(([plt, pln, nm, col, desc]) => {
            const html = `
                <div class="telemetry-pulse-pin" style="color:${col};">
                    <div class="t-pin-ring"></div>
                    <div class="t-pin-core" style="background:${col};"></div>
                </div>
            `;
            
            const popupHtml = `
                <div style="font-family:var(--font-sans);font-size:12.5px;line-height:1.5;min-width:180px;">
                    <div style="font-weight:700;color:#ffffff;display:flex;align-items:center;gap:6px;margin-bottom:4px;">
                        <span style="width:8px;height:8px;border-radius:50%;background:${col};box-shadow:0 0 6px ${col};display:inline-block;"></span>
                        ${nm}
                    </div>
                    <div style="font-family:var(--font-mono);font-size:10.5px;color:#94a3b8;margin-bottom:6px;">
                        Lat: ${plt.toFixed(4)}°, Lon: ${pln.toFixed(4)}°
                    </div>
                    <div style="font-size:11px;color:#cbd5e1;border-top:1px solid rgba(255,255,255,0.1);padding-top:4px;">
                        ${desc || 'Active LoRa Edge Sensing Node'}
                    </div>
                </div>
            `;
            
            new CustomPulseMarker(
                new google.maps.LatLng(plt, pln),
                map,
                html,
                nm,
                popupHtml
            );
        });
    }
    
    return map;
}

function initGoogleMaps() {
    maps.flood = mkGoogleMap('map-flood', 25.5, 82.0, 5, 'Flood Hydrometry', [
        [28.6139, 77.2090, 'Delhi Yamuna Node', '#00d2ff', 'Stage Level: 1.2m · Ultrasonic Hydro-Sensor'],
        [25.3176, 82.9739, 'Varanasi Ganga Node', '#00d2ff', 'Flow Velocity: 0.84 m/s · Indo-Gangetic Basin'],
        [22.5726, 88.3639, 'Kolkata Hooghly Node', '#00d2ff', 'Tidal Surge Sensor · Delta Outflow']
    ]);

    maps.fire = mkGoogleMap('map-fire', 20.5, 80.0, 5, 'WildFire Canopy Mesh', [
        [15.2993, 74.1240, 'Goa Forest Zone', '#ff5722', 'Ambient Temp: 32°C · MQ-135 Combustion Sensor'],
        [11.1085, 77.3411, 'Nilgiris Forest Node', '#ff5722', 'Canopy VPD: 3.4 kPa · SHT40 Micro-climate'],
        [22.9734, 78.6569, 'Madhya Pradesh Reserve', '#ff5722', 'Thermal Radiative Flux: 12% Risk']
    ]);

    maps.land = mkGoogleMap('map-land', 20.0, 77.0, 5, 'Slope Inertial Radar', [
        [11.4100, 76.6900, 'Western Ghats Slope Station', '#f59e0b', 'MPU-6050 Tilt: 0.05°/step · Soil VWC: 18%'],
        [10.3270, 76.9550, 'Valparai Hill Pass Node', '#f59e0b', 'SW-420 Seismic Vibration: 2.0 RMS'],
        [32.0845, 77.1734, 'Manali Himalayan Node', '#f59e0b', 'Pore Pressure: Normal · Fault Strain Inactive']
    ]);

    maps.air = mkGoogleMap('map-air', 22.0, 79.0, 5, 'CAAQM Aerosol Grid', [
        [28.6289, 77.2408, 'Delhi ITO - CPCB', '#2dd4bf', 'PM2.5: 45 µg/m³ · Dual-Laser Optical'],
        [28.6812, 77.3195, 'Delhi IHBAS - CPCB', '#2dd4bf', 'PM10: 85 µg/m³ · 60m Forward Forecast: 55 µg/m³'],
        [19.0565, 72.9150, 'Mumbai Deonar - IITM', '#2dd4bf', 'Aerosol Dispersion: Coastal Wind Field'],
        [18.5308, 73.8475, 'Pune Shivajinagar - IITM', '#2dd4bf', 'O3/NO2 Electrochemical Sensor']
    ]);

    maps.heat = mkGoogleMap('map-heat', 18.5, 73.8, 6, 'Thermal Radiative Mesh', [
        [18.4350, 73.7915, 'Pune CWPRS Campus Node', '#fbbf24', 'Temperature: 38°C · Solar: 850 W/m2 · Heat Index: 42°C']
    ]);

    maps.ind = mkGoogleMap('map-ind', 17.68, 83.21, 6, 'Plume Toxic Dispersion', [
        [17.6868, 83.2185, 'Vizag Industrial Complex Node', '#a855f7', 'MQ Gas: 150 · PM2.5: 25 µg/m3 · Leak Risk: Inactive']
    ]);

    maps.water = mkGoogleMap('map-water', 17.7285, 83.3015, 6, 'Reservoir Water Health Mesh', [
        [17.7285, 83.3015, 'Vizag Municipal Reservoir Node', '#0ea5e9', 'pH: 7.2 · Turbidity: 2.0 NTU · TDS: 150 mg/L']
    ]);
}

function loadScript(src) {
    return new Promise((resolve, reject) => {
        const script = document.createElement('script');
        script.src = src;
        script.onload = () => resolve();
        script.onerror = (e) => reject(e);
        document.head.appendChild(script);
    });
}

function loadGoogleMaps(apiKey) {
    return new Promise((resolve, reject) => {
        window.googleMapsCallback = function() {
            resolve();
        };
        const script = document.createElement('script');
        script.src = `https://maps.googleapis.com/maps/api/js?key=${apiKey}&callback=googleMapsCallback`;
        script.async = true;
        script.defer = true;
        script.onerror = (e) => reject(e);
        document.head.appendChild(script);
    });
}

async function prepareAndInitMaps() {
    let apiKey = window.GOOGLE_MAPS_API_KEY || "";
    
    // If running locally, check if backend contains API config
    if (!apiKey && (window.location.hostname === '127.0.0.1' || window.location.hostname === 'localhost')) {
        const ports = [8000, 8001, 8002, 8003, 8004, 8005, 8006];
        for (const port of ports) {
            try {
                const controller = new AbortController();
                const timeoutId = setTimeout(() => controller.abort(), 400);
                const res = await fetch(`http://127.0.0.1:${port}/api/config`, { signal: controller.signal });
                clearTimeout(timeoutId);
                if (res.ok) {
                    const data = await res.json();
                    if (data.google_maps_api_key) {
                        apiKey = data.google_maps_api_key;
                        console.log(`Fetched Google Maps API Key from port ${port}: ${apiKey.substring(0, 5)}...`);
                        break;
                    }
                }
            } catch (e) {}
        }
    }

    if (apiKey) {
        console.log(`Using Google Maps API Key: ${apiKey.substring(0,5)}...`);
        try {
            await loadGoogleMaps(apiKey);
            console.log("Google Maps JS API loaded successfully.");
        } catch (err) {
            console.error("Failed to load Google Maps script.", err);
        }
    } else {
        console.log("No Google Maps API Key found.");
    }
    
    initGoogleMaps();
}

// Automatically load map when DOM is ready
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', prepareAndInitMaps);
} else {
    prepareAndInitMaps();
}


// ─── FLOOD TELEMETRY ────────────────────────────────────────
function fSync() {
    document.getElementById('fl-rl').innerText  = document.getElementById('f-i-rl').value;
    document.getElementById('fl-sm').innerText  = document.getElementById('f-i-sm').value;
    document.getElementById('fl-rf').innerText  = document.getElementById('f-i-rf').value;
}

async function floodPredict() {
    const rl = parseFloat(document.getElementById('f-i-rl').value);
    const sm = parseFloat(document.getElementById('f-i-sm').value);
    const rf = parseFloat(document.getElementById('f-i-rf').value);

    const payload = {
        node_id: "TYPE-A-101",
        rain_1h: rf / 8,
        rain_24h: rf,
        water_level_m: rl,
        soil_moisture_pct: sm,
        temperature_c: 28.0,
        humidity_pct: 70.0
    };
    let d = null;
    if (window.location.hostname === '127.0.0.1' || window.location.hostname === 'localhost') {
        try {
            const controller = new AbortController();
            const tid = setTimeout(() => controller.abort(), 800);
            const r = await fetch('http://127.0.0.1:8000/api/predict', { method:'POST',
                headers:{'Content-Type':'application/json'}, body: JSON.stringify(payload), signal: controller.signal });
            clearTimeout(tid);
            if (r.ok) d = await r.json();
        } catch(e) {}
    }

    if (!d) {
        const risk_pct = Math.min(99.9, Math.max(2.0, (rl / 3.0) * 45 + (rf / 100.0) * 35 + (sm / 100.0) * 20));
        const anomaly_detected = (rl > 2.2 || rf > 65 || sm > 85);
        const severity_level = risk_pct > 75 ? 'CRITICAL' : risk_pct > 50 ? 'WARNING' : risk_pct > 30 ? 'WATCH' : 'NORMAL';
        d = { risk_score_pct: risk_pct, anomaly_detected, severity_level };
        addLocalAlert('flood', severity_level, `Water Level: ${rl}m | Rainfall: ${rf}mm`);
    }

    document.getElementById('f-level').innerText = `${rl}m / ${sm}%`;
    document.getElementById('f-prob').innerText  = `${Math.round(d.risk_score_pct || 0)}%`;
    document.getElementById('f-anom').innerText  = d.anomaly_detected ? '1.00' : '0.00';
    const sev = d.severity_level || 'NORMAL';
    const sevEl = document.getElementById('f-sev');
    sevEl.innerText = sev;
    sevEl.style.color = sev === 'CRITICAL' ? '#ef4444' : sev === 'WARNING' ? '#f59e0b' : sev === 'WATCH' ? '#f59e0b' : '#10b981';
    refreshAlerts('flood');
}

// ─── FIRE TELEMETRY ─────────────────────────────────────────
function fiSync() {
    document.getElementById('fil-t').innerText = document.getElementById('fi-i-t').value;
    document.getElementById('fil-h').innerText = document.getElementById('fi-i-h').value;
    document.getElementById('fil-w').innerText = document.getElementById('fi-i-w').value;
}

async function firePredict() {
    const t = parseFloat(document.getElementById('fi-i-t').value);
    const h = parseFloat(document.getElementById('fi-i-h').value);
    const w = parseFloat(document.getElementById('fi-i-w').value);

    const pm25_est  = Math.max(10, (55 - h * 0.4) + (t - 25) * 2.5);
    const tvoc_est  = Math.max(50, (t - 20) * 30 + (100 - h) * 8);
    const tempRate  = t > 40 ? 0.18 : t > 35 ? 0.12 : 0.03;
    const humRate   = h < 25 ? -0.18 : h < 40 ? -0.10 : -0.02;
    const pm25Rate  = t > 42 && h < 25 ? 1.2 : t > 38 && h < 35 ? 0.6 : 0.1;
    const tvocRate  = t > 42 ? 0.5 : t > 38 ? 0.2 : 0.05;
    const payload = {
        node_id: "NODE-FWF-01",
        temperature: t, humidity: h, pressure: 1008.0,
        pm25: pm25_est, tvoc: tvoc_est, raw_ethanol: 3000 + (t - 25) * 20,
        temperature_rate: tempRate, humidity_rate: humRate,
        pm25_rate: pm25Rate, tvoc_rate: tvocRate,
        temperature_delta_5: t > 40 ? 4.5 : t > 35 ? 2.5 : 0.8,
        humidity_delta_5: h < 25 ? -8.0 : h < 40 ? -4.0 : -1.5
    };
    let d = null;
    if (window.location.hostname === '127.0.0.1' || window.location.hostname === 'localhost') {
        try {
            const controller = new AbortController();
            const tid = setTimeout(() => controller.abort(), 800);
            const r = await fetch('http://127.0.0.1:8001/api/predict', { method:'POST',
                headers:{'Content-Type':'application/json'}, body: JSON.stringify(payload), signal: controller.signal });
            clearTimeout(tid);
            if (r.ok) d = await r.json();
        } catch(e) {}
    }

    if (!d) {
        const fire_prob = Math.min(0.99, Math.max(0.01, (t / 50.0) * 0.45 + ((100 - h) / 100.0) * 0.35 + (w / 40.0) * 0.20));
        const top_features = [t > 38 ? 'Temperature Rate' : h < 25 ? 'Low Humidity' : 'Wind Velocity'];
        const severity = fire_prob > 0.75 ? 'CRITICAL' : fire_prob > 0.50 ? 'WARNING' : fire_prob > 0.30 ? 'WATCH' : 'NORMAL';
        d = { fire_probability: fire_prob, top_features, severity };
        addLocalAlert('fire', severity, `Temp: ${t}°C | Humidity: ${h}%`);
    }

    document.getElementById('fi-th').innerText    = `${t}°C / ${h}%`;
    document.getElementById('fi-risk').innerText  = `${Math.round((d.fire_probability || 0) * 100)}%`;
    document.getElementById('fi-drought').innerText = (d.top_features && d.top_features[0]) || 'N/A';
    const sev = d.severity || 'NORMAL';
    const sevEl = document.getElementById('fi-sev');
    sevEl.innerText = sev;
    sevEl.style.color = sev === 'CRITICAL' ? '#ef4444' : sev === 'WARNING' ? '#f59e0b' : sev === 'WATCH' ? '#f59e0b' : '#10b981';
    refreshAlerts('fire');
}

// ─── LANDSLIDE TELEMETRY ────────────────────────────────────
function laSync() {
    document.getElementById('lal-sm').innerText  = document.getElementById('la-i-sm').value;
    document.getElementById('lal-tr').innerText  = document.getElementById('la-i-tr').value;
    document.getElementById('lal-vib').innerText = document.getElementById('la-i-vib').value;
}

async function landPredict() {
    const sm  = parseFloat(document.getElementById('la-i-sm').value);
    const tr  = parseFloat(document.getElementById('la-i-tr').value);
    const vib = parseFloat(document.getElementById('la-i-vib').value);

    const payload = { node_id: "NODE-LND-02",
        soil_moisture_vwc: sm, soil_moisture_rate: sm>0.30?0.04:0.0,
        tilt_magnitude: 5.0 + tr*4.0, tilt_rate: tr, vibration_rate: vib,
        temperature: 21.5, humidity: 75.0, rainfall_24h: 10.0 };
    let d = null;
    if (window.location.hostname === '127.0.0.1' || window.location.hostname === 'localhost') {
        try {
            const controller = new AbortController();
            const tid = setTimeout(() => controller.abort(), 800);
            const r = await fetch('http://127.0.0.1:8002/api/predict', { method:'POST',
                headers:{'Content-Type':'application/json'}, body: JSON.stringify(payload), signal: controller.signal });
            clearTimeout(tid);
            if (r.ok) d = await r.json();
        } catch(e) {}
    }

    if (!d) {
        const risk_prob = Math.min(0.99, Math.max(0.01, sm * 0.40 + (tr / 2.0) * 0.35 + (vib / 2.0) * 0.25));
        const anomaly_score = tr > 0.8 || sm > 0.75 ? 0.92 : 0.12;
        const severity = risk_prob > 0.70 ? 'CRITICAL' : risk_prob > 0.45 ? 'WARNING' : risk_prob > 0.25 ? 'WATCH' : 'NORMAL';
        d = { risk_probability: risk_prob, anomaly_score, severity };
        addLocalAlert('land', severity, `Moisture: ${Math.round(sm*100)}% | Tilt: ${tr}°`);
    }

    document.getElementById('la-sm').innerText   = `${Math.round(sm*100)}% / ${tr}°`;
    document.getElementById('la-risk').innerText = `${Math.round((d.risk_probability||0)*100)}%`;
    document.getElementById('la-anom').innerText = (d.anomaly_score||0).toFixed(2);
    const sev = d.severity || 'NORMAL';
    const sevEl = document.getElementById('la-sev');
    sevEl.innerText = sev;
    sevEl.style.color = sev === 'CRITICAL' ? '#ef4444' : sev === 'WARNING' ? '#f59e0b' : '#10b981';
    refreshAlerts('land');
}

// ─── AIR POLLUTION TELEMETRY ────────────────────────────────
function aiSync() {
    document.getElementById('ail-p25').innerText   = document.getElementById('ai-i-p25').value;
    document.getElementById('ail-p10').innerText   = document.getElementById('ai-i-p10').value;
    document.getElementById('ail-delta').innerText = document.getElementById('ai-i-delta').value;
}

async function airPredict() {
    const pm25  = parseFloat(document.getElementById('ai-i-p25').value);
    const pm10  = parseFloat(document.getElementById('ai-i-p10').value);
    const delta = parseFloat(document.getElementById('ai-i-delta').value);

    const payload = { station_id:"DEL-ITO", pm25, pm10, gas_proxy: 25.0,
        temperature: 28.5, relative_humidity: 72.0, pressure: 1012.0,
        pm25_lag_15: pm25-5, pm25_lag_30: pm25-delta,
        pm25_delta_30: delta, pm25_slope_30: delta/30.0,
        hour_sin: 0.5, hour_cos: -0.86 };
    let d = null;
    if (window.location.hostname === '127.0.0.1' || window.location.hostname === 'localhost') {
        try {
            const controller = new AbortController();
            const tid = setTimeout(() => controller.abort(), 800);
            const r = await fetch('http://127.0.0.1:8003/api/predict', { method:'POST',
                headers:{'Content-Type':'application/json'}, body: JSON.stringify(payload), signal: controller.signal });
            clearTimeout(tid);
            if (r.ok) d = await r.json();
        } catch(e) {}
    }

    if (!d) {
        const predicted_pm25 = Math.max(10, Math.round(pm25 + delta * 1.2));
        const risk_score = Math.min(100, Math.round((pm25 / 250.0) * 60 + (pm10 / 350.0) * 40));
        const confidence = 94.5;
        const severity = pm25 > 250 ? 'CRITICAL' : pm25 > 120 ? 'WARNING' : pm25 > 60 ? 'WATCH' : 'NORMAL';
        d = { predicted_pm25_60m: predicted_pm25, risk_score, confidence, severity };
        addLocalAlert('air', severity, `PM2.5: ${pm25} µg/m³ | Forecast: ${predicted_pm25}`);
    }

    document.getElementById('ai-pm').innerText   = `${pm25} / ${pm10} µg/m³`;
    document.getElementById('ai-fc').innerText   = `${d.predicted_pm25_60m} µg/m³`;
    document.getElementById('ai-risk').innerText = `${d.risk_score} / ${d.confidence}%`;
    const sev = d.severity || 'NORMAL';
    const sevEl = document.getElementById('ai-sev');
    sevEl.innerText = sev;
    sevEl.style.color = sev === 'CRITICAL' ? '#ef4444' : sev === 'WARNING' ? '#f59e0b' : '#10b981';
    refreshAlerts('air');
}

// ─── HEAT TELEMETRY ─────────────────────────────────────────
function heSync() {
    document.getElementById('hel-temp').innerText  = document.getElementById('he-i-temp').value + " °C";
    document.getElementById('hel-humid').innerText = document.getElementById('he-i-humid').value + " %";
    document.getElementById('hel-solar').innerText = document.getElementById('he-i-solar').value + " W/m²";
    document.getElementById('hel-wind').innerText  = document.getElementById('he-i-wind').value + " Km/Hr";
}

async function heatPredict() {
    const temp  = parseFloat(document.getElementById('he-i-temp').value);
    const humid = parseFloat(document.getElementById('he-i-humid').value);
    const solar = parseFloat(document.getElementById('he-i-solar').value);
    const wind  = parseFloat(document.getElementById('he-i-wind').value);

    const payload = {
        station_id: "MH-CWPRS", temperature_c: temp, humidity: humid,
        solar_radiation: solar, wind_speed_kmh: wind, rainfall_mm: 0.0,
        temperature_rate: 0.5, humidity_rate: -1.0, solar_radiation_rate: 50.0,
        cumulative_hot_hours: temp > 35 ? 4 : 0, nighttime_cooling_deficit: temp > 30 ? 2.0 : 0.0
    };
    let d = null;
    if (window.location.hostname === '127.0.0.1' || window.location.hostname === 'localhost') {
        try {
            const controller = new AbortController();
            const tid = setTimeout(() => controller.abort(), 800);
            const r = await fetch('http://127.0.0.1:8004/api/predict', { method:'POST',
                headers:{'Content-Type':'application/json'}, body: JSON.stringify(payload), signal: controller.signal });
            clearTimeout(tid);
            if (r.ok) d = await r.json();
        } catch(e) {}
    }

    if (!d) {
        const heat_risk_prob = Math.min(0.99, Math.max(0.01, (temp / 50.0) * 0.60 + (humid / 100.0) * 0.25 + (solar / 1000.0) * 0.15));
        const anomaly_score = temp > 42 ? 0.88 : 0.08;
        const confidence = 0.95;
        const severity = heat_risk_prob > 0.75 ? 'CRITICAL' : heat_risk_prob > 0.55 ? 'WARNING' : heat_risk_prob > 0.35 ? 'WATCH' : 'NORMAL';
        d = { heat_risk_probability: heat_risk_prob, anomaly_score, confidence, severity };
        addLocalAlert('heat', severity, `Temp: ${temp}°C | Humidity: ${humid}%`);
    }

    document.getElementById('he-temphum').innerText  = `${temp}°C / ${humid}%`;
    document.getElementById('he-prob').innerText     = `${(d.heat_risk_probability * 100).toFixed(1)}%`;
    document.getElementById('he-anomaly').innerText  = `${d.anomaly_score} / ${(d.confidence * 100).toFixed(0)}%`;
    
    const sev = d.severity || 'NORMAL';
    const sevEl = document.getElementById('he-sev');
    sevEl.innerText = sev;
    
    if (sev === 'CRITICAL') {
        sevEl.style.color = '#ef4444';
        document.getElementById('he-prob').style.color = '#ef4444';
    } else if (sev === 'WARNING') {
        sevEl.style.color = '#f59e0b';
        document.getElementById('he-prob').style.color = '#f59e0b';
    } else if (sev === 'WATCH') {
        sevEl.style.color = '#fbbf24';
        document.getElementById('he-prob').style.color = '#fbbf24';
    } else {
        sevEl.style.color = '#10b981';
        document.getElementById('he-prob').style.color = '#10b981';
    }
    refreshAlerts('heat');
}

// ─── INDUSTRIAL TELEMETRY ────────────────────────────────────
function inSync() {
    document.getElementById('inl-gas').innerText  = document.getElementById('in-i-gas').value;
    document.getElementById('inl-pm25').innerText = document.getElementById('in-i-pm25').value + " µg/m³";
    document.getElementById('inl-pm10').innerText = document.getElementById('in-i-pm10').value + " µg/m³";
}

async function indPredict() {
    const gas  = parseFloat(document.getElementById('in-i-gas').value);
    const pm25 = parseFloat(document.getElementById('in-i-pm25').value);
    const pm10 = parseFloat(document.getElementById('in-i-pm10').value);

    const payload = {
        station_id: "IND-PLUME-1", gas_response: gas, pm25: pm25, pm10: pm10,
        temperature_c: 30.0, humidity: 60.0, pressure: 1010.0, gas_rate: 10.0,
        pm25_rate: 5.0, pm10_rate: 10.0, cumulative_hot_hours: 0
    };
    let d = null;
    if (window.location.hostname === '127.0.0.1' || window.location.hostname === 'localhost') {
        try {
            const controller = new AbortController();
            const tid = setTimeout(() => controller.abort(), 800);
            const r = await fetch('http://127.0.0.1:8005/api/predict', { method:'POST',
                headers:{'Content-Type':'application/json'}, body: JSON.stringify(payload), signal: controller.signal });
            clearTimeout(tid);
            if (r.ok) d = await r.json();
        } catch(e) {}
    }

    if (!d) {
        const leak_risk_prob = Math.min(0.99, Math.max(0.01, (gas / 2500.0) * 0.50 + (pm25 / 300.0) * 0.30 + (pm10 / 500.0) * 0.20));
        const anomaly_score = gas > 1800 ? 0.94 : 0.10;
        const confidence = 0.96;
        const severity = leak_risk_prob > 0.70 ? 'CRITICAL' : leak_risk_prob > 0.45 ? 'WARNING' : leak_risk_prob > 0.25 ? 'WATCH' : 'NORMAL';
        d = { leak_risk_probability: leak_risk_prob, anomaly_score, confidence, severity };
        addLocalAlert('ind', severity, `Gas: ${gas} | PM2.5: ${pm25}`);
    }

    document.getElementById('in-gaspm').innerText   = `${gas} / ${pm25} µg/m³`;
    document.getElementById('in-prob').innerText    = `${(d.leak_risk_probability * 100).toFixed(1)}%`;
    document.getElementById('in-anomaly').innerText = `${d.anomaly_score} / ${(d.confidence * 100).toFixed(0)}%`;
    
    const sev = d.severity || 'NORMAL';
    const sevEl = document.getElementById('in-sev');
    sevEl.innerText = sev;
    
    if (sev === 'CRITICAL') {
        sevEl.style.color = '#ef4444';
        document.getElementById('in-prob').style.color = '#ef4444';
    } else if (sev === 'WARNING') {
        sevEl.style.color = '#f59e0b';
        document.getElementById('in-prob').style.color = '#f59e0b';
    } else if (sev === 'WATCH') {
        sevEl.style.color = '#fbbf24';
        document.getElementById('in-prob').style.color = '#fbbf24';
    } else {
        sevEl.style.color = '#10b981';
        document.getElementById('in-prob').style.color = '#10b981';
    }
    refreshAlerts('ind');
}

// ─── WATER QUALITY TELEMETRY ─────────────────────────────────
function wtSync() {
    document.getElementById('wtl-ph').innerText   = document.getElementById('wt-i-ph').value;
    document.getElementById('wtl-tur').innerText  = document.getElementById('wt-i-tur').value + " NTU";
    document.getElementById('wtl-tds').innerText  = document.getElementById('wt-i-tds').value + " mg/L";
    document.getElementById('wtl-temp').innerText = document.getElementById('wt-i-temp').value + "°C";
}

async function waterPredict() {
    const ph   = parseFloat(document.getElementById('wt-i-ph').value);
    const tur  = parseFloat(document.getElementById('wt-i-tur').value);
    const tds  = parseFloat(document.getElementById('wt-i-tds').value);
    const temp = parseFloat(document.getElementById('wt-i-temp').value);

    const payload = {
        station_id: "AP-WATER-CWC-1", pH: ph, turbidity: tur, EC: tds * 1.5, TDS: tds,
        dissolved_oxygen: 7.5, temperature_c: temp, pH_rate: 0.0, turbidity_rate: 0.0,
        EC_rate: 0.0, TDS_rate: 0.0, DO_rate: 0.0, rolling_std_pH: 0.05,
        rolling_std_turbidity: 0.2, rolling_std_EC: 10.0, rolling_std_TDS: 5.0,
        rolling_std_DO: 0.1, persistence_score: 0
    };
    let d = null;
    if (window.location.hostname === '127.0.0.1' || window.location.hostname === 'localhost') {
        try {
            const controller = new AbortController();
            const tid = setTimeout(() => controller.abort(), 800);
            const r = await fetch('http://127.0.0.1:8006/api/predict', { method:'POST',
                headers:{'Content-Type':'application/json'}, body: JSON.stringify(payload), signal: controller.signal });
            clearTimeout(tid);
            if (r.ok) d = await r.json();
        } catch(e) {}
    }

    if (!d) {
        const ph_dev = Math.abs(ph - 7.0);
        const risk_prob = Math.min(0.99, Math.max(0.01, (ph_dev / 4.0) * 0.35 + (tur / 50.0) * 0.40 + (tds / 1000.0) * 0.25));
        const anomaly_score = tur > 25 || ph_dev > 1.8 ? 0.91 : 0.09;
        const confidence = 0.93;
        const severity = risk_prob > 0.70 ? 'CRITICAL' : risk_prob > 0.45 ? 'WARNING' : risk_prob > 0.25 ? 'WATCH' : 'NORMAL';
        d = { water_quality_risk_probability: risk_prob, anomaly_score, confidence, severity };
        addLocalAlert('water', severity, `pH: ${ph} | Turbidity: ${tur} NTU`);
    }

    document.getElementById('wt-phtub').innerText   = `${ph} / ${tur} NTU`;
    document.getElementById('wt-prob').innerText    = `${(d.water_quality_risk_probability * 100).toFixed(1)}%`;
    document.getElementById('wt-anomaly').innerText = `${d.anomaly_score} / ${(d.confidence * 100).toFixed(0)}%`;
    
    const sev = d.severity || 'NORMAL';
    const sevEl = document.getElementById('wt-sev');
    sevEl.innerText = sev;
    
    if (sev === 'CRITICAL') {
        sevEl.style.color = '#ef4444';
        document.getElementById('wt-prob').style.color = '#ef4444';
    } else if (sev === 'WARNING') {
        sevEl.style.color = '#f59e0b';
        document.getElementById('wt-prob').style.color = '#f59e0b';
    } else if (sev === 'WATCH') {
        sevEl.style.color = '#fbbf24';
        document.getElementById('wt-prob').style.color = '#fbbf24';
    } else {
        sevEl.style.color = '#10b981';
        document.getElementById('wt-prob').style.color = '#10b981';
    }
    refreshAlerts('water');
}

// ─── ALERTS ─────────────────────────────────────────────────
const ALERT_PORTS = { flood:8000, fire:8001, land:8002, air:8003, heat:8004, ind:8005, water:8006 };
const ALERT_DIV   = { flood:'f-alerts', fire:'fi-alerts', land:'la-alerts', air:'ai-alerts', heat:'he-alerts', ind:'in-alerts', water:'wt-alerts' };
const ALERT_CNT   = { flood:'f-alert-cnt', fire:'fi-alert-cnt', land:'la-alert-cnt', air:'ai-alert-cnt', heat:'he-alert-cnt', ind:'in-alert-cnt', water:'wt-alert-cnt' };

const localAlertsStore = {
    flood: [
        { alert_id: "ALT-FLD-01", severity: "WARNING", timestamp: new Date(Date.now() - 3600000).toISOString() }
    ],
    fire: [
        { alert_id: "ALT-FWF-01", severity: "WATCH", timestamp: new Date(Date.now() - 7200000).toISOString() }
    ],
    land: [
        { alert_id: "ALT-LND-01", severity: "NORMAL", timestamp: new Date(Date.now() - 10800000).toISOString() }
    ],
    air: [
        { alert_id: "ALT-AIR-01", severity: "WARNING", timestamp: new Date(Date.now() - 1800000).toISOString() }
    ],
    heat: [
        { alert_id: "ALT-HT-01", severity: "WATCH", timestamp: new Date(Date.now() - 5400000).toISOString() }
    ],
    ind: [
        { alert_id: "ALT-IND-01", severity: "NORMAL", timestamp: new Date(Date.now() - 14400000).toISOString() }
    ],
    water: [
        { alert_id: "ALT-WTR-01", severity: "NORMAL", timestamp: new Date(Date.now() - 9000000).toISOString() }
    ]
};

function addLocalAlert(mod, severity, details) {
    if (severity === 'NORMAL') return;
    const prefixMap = { flood:'FLD', fire:'FWF', land:'LND', air:'AIR', heat:'HT', ind:'IND', water:'WTR' };
    const pfx = prefixMap[mod] || 'ALT';
    const newAlert = {
        alert_id: `ALT-${pfx}-${Math.floor(100 + Math.random() * 900)}`,
        severity: severity,
        timestamp: new Date().toISOString()
    };
    if (localAlertsStore[mod]) {
        localAlertsStore[mod].push(newAlert);
    }
}

async function refreshAlerts(mod) {
    let alerts = null;
    if (window.location.hostname === '127.0.0.1' || window.location.hostname === 'localhost') {
        try {
            const controller = new AbortController();
            const tid = setTimeout(() => controller.abort(), 600);
            const endpoint = 'alerts';
            const r = await fetch(`http://127.0.0.1:${ALERT_PORTS[mod]}/api/${endpoint}`, { signal: controller.signal });
            clearTimeout(tid);
            if (r.ok) alerts = await r.json();
        } catch(e) {}
    }
    
    if (!alerts) {
        alerts = localAlertsStore[mod] || [];
    }

    const cntEl = document.getElementById(ALERT_CNT[mod]);
    if (cntEl) cntEl.innerText = alerts.length;
    const el = document.getElementById(ALERT_DIV[mod]);
    if (!el) return;

    if (!alerts.length) {
        el.innerHTML = `<p class="no-alerts">No active warnings.</p>`;
        return;
    }
    el.innerHTML = alerts.slice(-3).reverse().map(a => {
        const cls = a.severity === 'CRITICAL' ? 'al-crit' : a.severity === 'WARNING' ? 'al-warning' : 'al-watch';
        const id  = a.alert_id || '—';
        const ts  = (a.timestamp||'').substring(0,19).replace('T',' ');
        return `<div class="alert-item ${cls}"><b>🚨 ${a.severity} (${id})</b><br>${ts}</div>`;
    }).join('');
}

// Periodic alert polling
setInterval(() => {
    ['flood', 'fire', 'land', 'air', 'heat', 'ind', 'water'].forEach(refreshAlerts);
}, 15000);

// ─── PRODUCT CONTROL CENTER INTEGRATION ───
function scrollToSection(id) {
    openOverview();
    setTimeout(() => {
        const el = document.getElementById(id);
        if (el) el.scrollIntoView({ behavior: 'smooth' });
    }, 40);
}

function initSharedMap() {
    const el = document.getElementById('map-shared');
    if (!el) return;
    
    const allPins = [
        [28.6139, 77.2090, 'Delhi Yamuna Hydro Node (FLD-101)', '#00d2ff', '💧 Flood Hydro-Sensor · Water Stage Level: 1.2m'],
        [25.3176, 82.9739, 'Varanasi Ganga Station (FLD-102)', '#00d2ff', '💧 Flood Hydro-Sensor · Flow Velocity: 0.84 m/s'],
        [15.2993, 74.1240, 'Goa Forest Station (FWF-01)', '#ff5722', '🔥 Wildfire Node · Temp: 32°C · Combustion Sensor'],
        [11.1085, 77.3411, 'Nilgiris Forest Reserve (FWF-02)', '#ff5722', '🔥 Wildfire Node · VPD: 3.4 kPa · SHT40 Micro-Climate'],
        [11.4100, 76.6900, 'Western Ghats Slope (LND-01)', '#f59e0b', '⛰️ Landslide Node · MPU6050 Tilt: 0.05° · VWC: 18%'],
        [10.3270, 76.9550, 'Valparai Hill Pass (LND-02)', '#f59e0b', '⛰️ Landslide Node · SW-420 Seismic Vibration: 2.0 RMS'],
        [28.6289, 77.2408, 'Delhi ITO CPCB Station (AIR-01)', '#2dd4bf', '💨 Air Quality Node · PM2.5: 45 µg/m³ · CPCB CAAQM'],
        [28.6812, 77.3195, 'Delhi IHBAS Station (AIR-02)', '#2dd4bf', '💨 Air Quality Node · PM10: 85 µg/m³ · 60m Forecast: 55'],
        [18.4350, 73.7915, 'Pune CWPRS Station (HT-01)', '#fbbf24', '☀️ Extreme Heat Node · Temp: 38°C · Solar: 850 W/m²'],
        [17.6868, 83.2185, 'Vizag Industrial Belt (IND-01)', '#a855f7', '⚠️ Toxic Plume Node · MQ Gas: 150 · PM2.5: 25 µg/m³'],
        [17.7285, 83.3015, 'Godavari Reservoir (WTR-01)', '#0ea5e9', '🌊 Water Quality Node · pH: 7.2 · Turbidity: 2.0 NTU']
    ];

    if (window.google && window.google.maps) {
        maps.shared = mkGoogleMap('map-shared', 20.5937, 78.9629, 5, 'Regional Control Center Map', allPins);
    } else {
        renderFallbackSharedMap('map-shared', allPins);
    }
}

function renderFallbackSharedMap(divId, pins) {
    const el = document.getElementById(divId);
    if (!el) return;
    
    // SVG Canvas Map of India
    let pinsSvg = '';
    pins.forEach(([lat, lon, nm, col, desc]) => {
        const x = ((lon - 68.0) / (96.0 - 68.0)) * 760 + 20;
        const y = 460 - (((lat - 8.0) / (35.5 - 8.0)) * 420 + 20);
        pinsSvg += `
            <g class="svg-map-pin-group" data-name="${nm}" data-desc="${desc}" transform="translate(${x}, ${y})">
                <circle r="16" fill="${col}" opacity="0.2">
                    <animate attributeName="r" values="8;22;8" dur="3s" repeatCount="indefinite"/>
                    <animate attributeName="opacity" values="0.4;0.05;0.4" dur="3s" repeatCount="indefinite"/>
                </circle>
                <circle r="5" fill="${col}" stroke="#ffffff" stroke-width="1.5"/>
                <text x="10" y="4" fill="#f1f5f9" font-size="10" font-family="Outfit, sans-serif" font-weight="600">${nm.split(' ')[0]}</text>
            </g>
        `;
    });

    el.innerHTML = `
        <div style="position:relative;width:100%;height:100%;background:#080b14;overflow:hidden;border-radius:16px;">
            <svg viewBox="0 0 800 480" style="width:100%;height:100%;">
                <defs>
                    <pattern id="gridPattern" width="40" height="40" patternUnits="userSpaceOnUse">
                        <path d="M 40 0 L 0 0 0 40" fill="none" stroke="rgba(255,255,255,0.03)" stroke-width="1"/>
                    </pattern>
                </defs>
                <rect width="800" height="480" fill="url(#gridPattern)"/>
                <circle cx="270" cy="180" r="75" fill="rgba(0, 210, 255, 0.05)" stroke="rgba(0, 210, 255, 0.15)" stroke-dasharray="4,4"/>
                <circle cx="260" cy="380" r="90" fill="rgba(255, 87, 34, 0.05)" stroke="rgba(255, 87, 34, 0.15)" stroke-dasharray="4,4"/>
                ${pinsSvg}
            </svg>
            <div style="position:absolute;top:16px;left:20px;font-family:var(--font-mono);font-size:11px;color:#94a3b8;background:rgba(10,16,28,0.85);padding:6px 14px;border-radius:9999px;border:1px solid rgba(255,255,255,0.1);">
                <span style="color:#10b981;">● SPATIAL CONTROL CANVAS</span> · India Regional Monitoring Network
            </div>
        </div>
    `;
}

function filterSharedMap(hazard, btn) {
    const pills = document.querySelectorAll('.map-filter-pill');
    pills.forEach(p => p.classList.remove('active'));
    if (btn) btn.classList.add('active');
    initSharedMap();
}

function populateUnifiedAlertCenter() {
    const el = document.getElementById('unified-alert-list');
    if (!el) return;

    const hazardTitles = {
        flood: { icon: '💧', name: 'Flood Inundation Warning' },
        fire:  { icon: '🔥', name: 'Wildfire VPD Spike' },
        land:  { icon: '⛰️', name: 'Slope Instability Alert' },
        air:   { icon: '💨', name: 'CPCB AQI Particulate Surge' },
        heat:  { icon: '☀️', name: 'Extreme Thermal Risk' },
        ind:   { icon: '⚠️', name: 'Toxic Gas Plume Leak' },
        water: { icon: '🌊', name: 'Reservoir Water Health' }
    };

    const hazardNodes = {
        flood: 'NODE-FLD-101 (Indo-Gangetic Basin)',
        fire:  'NODE-FWF-01 (Nilgiris Forest)',
        land:  'NODE-LND-02 (Valparai Hill Pass)',
        air:   'DEL-ITO-01 (Delhi CAAQM Station)',
        heat:  'MH-CWPRS-01 (Pune Station)',
        ind:   'IND-PLUME-1 (Vizag Industrial Belt)',
        water: 'AP-WATER-1 (Godavari River)'
    };

    let allAlerts = [];
    Object.keys(localAlertsStore).forEach(mod => {
        const items = localAlertsStore[mod] || [];
        items.forEach(item => {
            allAlerts.push({
                ...item,
                mod,
                hazardInfo: hazardTitles[mod] || { icon: '🚨', name: 'Environmental Warning' },
                nodeInfo: hazardNodes[mod] || 'NODE-FIELD-AI'
            });
        });
    });

    if (!allAlerts.length) {
        el.innerHTML = `<p class="no-alerts">No active warnings in stream.</p>`;
        return;
    }

    allAlerts.sort((a, b) => new Date(b.timestamp) - new Date(a.timestamp));

    el.innerHTML = allAlerts.map(a => {
        const cls = a.severity === 'CRITICAL' ? 'al-crit' : a.severity === 'WARNING' ? 'al-warning' : 'al-watch';
        const id  = a.alert_id || 'ALT-DISPATCH';
        const ts  = (a.timestamp || '').substring(0, 19).replace('T', ' ');
        return `
            <div class="alert-item ${cls}">
                <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:4px;">
                    <span style="font-weight:700;color:#ffffff;font-size:12.5px;">${a.hazardInfo.icon} ${a.hazardInfo.name}</span>
                    <span class="pill" style="color:${a.severity==='CRITICAL'?'#ef4444':a.severity==='WARNING'?'#f59e0b':'#fbbf24'};">${a.severity}</span>
                </div>
                <div style="font-family:var(--font-mono);font-size:10.5px;color:#94a3b8;">
                    ID: <b>${id}</b> · ${a.nodeInfo}
                </div>
                <div style="font-size:10.5px;color:#64748b;margin-top:4px;display:flex;justify-content:space-between;">
                    <span>Dispatched: ${ts}</span>
                    <span style="color:#34d399;">✔ NDMA ROUTED</span>
                </div>
            </div>
        `;
    }).join('');
}

function filterAlertStream(filter, btn) {
    const pills = document.querySelectorAll('.sf-pill');
    pills.forEach(p => p.classList.remove('active'));
    if (btn) btn.classList.add('active');
    populateUnifiedAlertCenter();
}

function simulateSystemBroadcast() {
    addLocalAlert('flood', 'WARNING', 'Simulated Basin Surge Advisory');
    populateUnifiedAlertCenter();
    alert("📡 Test Broadcast Protocol Sent!\n\nAutomated emergency advisory dispatched to NDMA API Gateway and local public SMS channels.");
}

// Auto-initialize Control Center components on load
document.addEventListener('DOMContentLoaded', () => {
    initSharedMap();
    populateUnifiedAlertCenter();
});

