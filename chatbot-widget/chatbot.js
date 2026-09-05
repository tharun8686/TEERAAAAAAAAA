class TerraEdgeChat extends HTMLElement {
    constructor() {
        super();
        this.attachShadow({ mode: 'open' });
        this.isOpen = false;
        this.context = {
            district: 'Chennai',
            coordinates: '13.03247850707785, 80.18077042149193',
            floodNode: {
                name: 'Chennai Coastal Flood Node',
                hazard: 'Flood / Inundation',
                severity: 'Warning',
                severityScore: 64,
                confidenceScore: 92,
                lat: 13.0324785,
                lon: 80.1807704,
                zone: 'Adyar Catchment Corridor',
                rainfall: '42.6 mm/h',
                waterLevel: '3.18 m',
                soilMoisture: '78%',
                pressure: '1004.8 hPa',
                status: 'High runoff accumulation in Adyar river basin; ground absorption saturated.'
            },
            fireNode: {
                name: 'Chennai North Fire Node',
                hazard: 'Forest / Scrub Wildfire',
                severity: 'Moderate',
                severityScore: 36,
                confidenceScore: 91,
                lat: 13.0354785,
                lon: 80.1837704,
                zone: 'Northern Industrial & Scrub Belt',
                temperature: '37.8 °C',
                humidity: '42%',
                smoke: '126 ppm',
                co: '8.4 ppm',
                flameIndex: '0.18',
                status: 'Thermal dry conditions; elevated smoke, but flame index remains below 0.25 ignition threshold.'
            }
        };
        this.history = [];
    }

    connectedCallback() {
        this.render();
        this.setupEventListeners();
    }

    getAutomatedAnswer(question) {
        const q = (question || '').toLowerCase().trim();
        const flood = this.context.floodNode;
        const fire = this.context.fireNode;

        // 1. Flood Situation
        if (q.includes('flood') || q.includes('rain') || q.includes('water') || q.includes('inundation') || q.includes('coastal') || q.includes('adyar')) {
            return `🌊 **Chennai Coastal Flood Node — Live Telemetry & Situation**\n\n` +
                `📍 **Location**: \`${flood.lat.toFixed(6)}° N, ${flood.lon.toFixed(6)}° E\` (${flood.zone})\n` +
                `⚠️ **Hazard Level**: **${flood.severity.toUpperCase()} (${flood.severityScore} / 100)**\n` +
                `🎯 **Edge-AI Confidence**: **${flood.confidenceScore}%**\n\n` +
                `📊 **Live Sensor Readings:**\n` +
                `• **Precipitation Rate**: \`${flood.rainfall}\` *(Heavy Convective Downpour)*\n` +
                `• **Water Stage**: \`${flood.waterLevel}\` *(Danger Threshold: 3.50 m)*\n` +
                `• **Soil Moisture**: \`${flood.soilMoisture}\` *(Critical Saturation - No Infiltration)*\n` +
                `• **Surface Pressure**: \`${flood.pressure}\`\n\n` +
                `📌 **Operational Outlook**: Rapid surface pooling is occurring in Adyar basin lowlands. Drainage pumps and storm barriers should remain engaged.`;
        }

        // 2. Fire Situation
        if (q.includes('fire') || q.includes('smoke') || q.includes('flame') || q.includes('thermal') || q.includes('heat') || q.includes('temperature')) {
            return `🔥 **Chennai North Fire Node — Live Telemetry & Situation**\n\n` +
                `📍 **Location**: \`${fire.lat.toFixed(6)}° N, ${fire.lon.toFixed(6)}° E\` (${fire.zone})\n` +
                `🟡 **Hazard Level**: **${fire.severity.toUpperCase()} (${fire.severityScore} / 100)**\n` +
                `🎯 **Edge-AI Confidence**: **${fire.confidenceScore}%**\n\n` +
                `📊 **Live Sensor Readings:**\n` +
                `• **Ambient Temperature**: \`${fire.temperature}\`\n` +
                `• **Relative Humidity**: \`${fire.humidity}\`\n` +
                `• **Smoke Concentration**: \`${fire.smoke}\`\n` +
                `• **Carbon Monoxide (CO)**: \`${fire.co}\`\n` +
                `• **Optical Flame Index**: \`${fire.flameIndex}\` *(Ignition Threshold > 0.25)*\n\n` +
                `📌 **Operational Outlook**: Elevated ambient heat and scrub smoke detected, but sub-critical flame index confirms no spreading wildfire front. Buffer patrols active.`;
        }

        // 3. Top Risk & Priority Assessment
        if (q.includes('top risk') || q.includes('priority') || q.includes('ranking') || q.includes('situation') || q.includes('summary') || q.includes('alert') || q.includes('overall') || q.includes('status')) {
            return `🚨 **Chennai Multi-Hazard Operations Summary**\n\n` +
                `Active edge telemetry from coordinate **\`${this.context.coordinates}\`**:\n\n` +
                `🥇 **#1 HIGHEST PRIORITY — Flood Node (Warning Level 64)**\n` +
                `• **Zone**: ${flood.zone}\n` +
                `• **Threat**: Rainfall at \`${flood.rainfall}\` with soil saturation at \`${flood.soilMoisture}\` is causing rapid accumulation towards the 3.50m danger line.\n\n` +
                `🥈 **#2 SECONDARY — Fire Node (Moderate Level 36)**\n` +
                `• **Zone**: ${fire.zone}\n` +
                `• **Threat**: Thermal reading at \`${fire.temperature}\` with smoke at \`${fire.smoke}\`. Stable flame index (\`${fire.flameIndex}\`).\n\n` +
                `🛡️ **Primary Directive**: Focus immediate civil defense resources on flood gate regulation along the Adyar corridor.`;
        }

        // 4. Live Sensor Telemetry Readings
        if (q.includes('sensor') || q.includes('readings') || q.includes('telemetry') || q.includes('data') || q.includes('values') || q.includes('metrics')) {
            return `📡 **Real-Time Edge Sensor Telemetry [Chennai Nodes]**\n\n` +
                `🌊 **Node 1: Flood Node (${flood.lat}, ${flood.lon})**\n` +
                `  ├── Rainfall: \`${flood.rainfall}\`\n` +
                `  ├── Water Level: \`${flood.waterLevel}\`\n` +
                `  ├── Soil Moisture: \`${flood.soilMoisture}\`\n` +
                `  └── Pressure: \`${flood.pressure}\`\n\n` +
                `🔥 **Node 2: Fire Node (${fire.lat}, ${fire.lon})**\n` +
                `  ├── Temperature: \`${fire.temperature}\`\n` +
                `  ├── Humidity: \`${fire.humidity}\`\n` +
                `  ├── Smoke (MQ-2): \`${fire.smoke}\`\n` +
                `  ├── Carbon Monoxide: \`${fire.co}\`\n` +
                `  └── Flame Index: \`${fire.flameIndex}\``;
        }

        // 5. Evacuation & Emergency Guidelines
        if (q.includes('evacuat') || q.includes('emergency') || q.includes('action') || q.includes('guidelines') || q.includes('safety') || q.includes('protocol')) {
            return `🛡️ **Chennai Emergency Response & Action Guidelines**\n\n` +
                `**1. Flood Warning Actions (Severity 64):**\n` +
                `• Activate auxiliary stormwater sluice gates along the Adyar river basin.\n` +
                `• Stage rescue boats and NDRF personnel at Saidapet, Jafferkhanpet, and Kotturpuram.\n` +
                `• Issue ground-floor advisory warnings for residents near low-lying canals.\n\n` +
                `**2. Fire Advisory Actions (Severity 36):**\n` +
                `• Maintain a 150-meter clear perimeter from northern dry brush corridors.\n` +
                `• Pre-check industrial fire hydrant pressure in North Chennai.\n\n` +
                `📞 **Emergency Desk**: Monitored 24/7 via TerraEdge Edge-AI Network.`;
        }

        // 6. Severity & Score Breakdown
        if (q.includes('score') || q.includes('confidence') || q.includes('severity') || q.includes('how') || q.includes('breakdown') || q.includes('explain')) {
            return `📊 **Severity Score & Model Confidence Breakdown**\n\n` +
                `• **Chennai Coastal Flood Node**: **64 / 100 Severity (Warning)**\n` +
                `  - *Calculation*: \`78% Soil Moisture (Runoff Risk) + 3.18m Water Stage + 42.6 mm/h Rain\`\n` +
                `  - *Confidence*: **92%** (Cross-sensor validation between ultrasonic stage meter and tipping bucket rain gauge).\n\n` +
                `• **Chennai North Fire Node**: **36 / 100 Severity (Moderate)**\n` +
                `  - *Calculation*: \`37.8°C Thermal Level + 126 ppm Smoke\` offset by safe \`0.18 Flame Index\`.\n` +
                `  - *Confidence*: **91%** (Optical IR flame array fused with electrochemical gas sensors).`;
        }

        // Generic fallback for any other query
        return `🤖 **TerraEdge Chennai Operations Assistant**\n\n` +
            `Monitoring active edge nodes at **\`${this.context.coordinates}\`**:\n\n` +
            `• 🌊 **Flood Node**: Warning (\`64/100\`) · Rain: \`${flood.rainfall}\` · Water: \`${flood.waterLevel}\`\n` +
            `• 🔥 **Fire Node**: Moderate (\`36/100\`) · Temp: \`${fire.temperature}\` · Smoke: \`${fire.smoke}\`\n\n` +
            `Choose one of the built-in situation queries below or type your question regarding flood levels, fire hazards, or emergency protocols!`;
    }

    render() {
        this.shadowRoot.innerHTML = `
            <style>
                :host {
                    font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
                    --primary-color: #579477;
                    --primary-highlight: #38bdf8;
                    --bg-color: rgba(12, 17, 28, 0.92);
                    --text-color: #f1f5f9;
                    --border-color: rgba(255, 255, 255, 0.1);
                    --chat-bg: rgba(8, 12, 20, 0.8);
                    --shadow: 0 16px 40px rgba(0, 0, 0, 0.6), inset 0 1px 0 rgba(255, 255, 255, 0.1);
                }

                .chatbot-container {
                    position: fixed;
                    bottom: 24px;
                    right: 24px;
                    z-index: 9999;
                    display: flex;
                    flex-direction: column;
                    align-items: flex-end;
                }

                /* Tactical Floating Action Button */
                .chat-button {
                    position: relative;
                    background: linear-gradient(135deg, #0284c7, #0369a1);
                    color: white;
                    border: 1px solid rgba(255, 255, 255, 0.25);
                    border-radius: 50%;
                    width: 56px;
                    height: 56px;
                    cursor: pointer;
                    box-shadow: 0 8px 24px rgba(0, 0, 0, 0.45), 0 0 16px rgba(2, 132, 199, 0.35);
                    display: flex;
                    align-items: center;
                    justify-content: center;
                    backdrop-filter: blur(12px);
                    transition: all 0.2s cubic-bezier(0.2, 0.8, 0.2, 1);
                }

                .chat-button:hover {
                    transform: scale(1.06) translateY(-2px);
                    box-shadow: 0 12px 28px rgba(0, 0, 0, 0.55), 0 0 24px rgba(14, 165, 233, 0.45);
                }

                .chat-button:active {
                    transform: translateY(1px);
                    box-shadow: inset 0 2px 4px rgba(0, 0, 0, 0.4);
                }

                .chat-button svg {
                    width: 24px;
                    height: 24px;
                    fill: currentColor;
                }

                /* Tactical Frosted Glass Panel */
                .chat-panel {
                    display: none;
                    width: 400px;
                    height: 620px;
                    max-height: calc(100vh - 90px);
                    background: var(--bg-color);
                    backdrop-filter: blur(24px) saturate(160%);
                    -webkit-backdrop-filter: blur(24px) saturate(160%);
                    border-radius: 16px;
                    box-shadow: var(--shadow);
                    overflow: hidden;
                    flex-direction: column;
                    margin-bottom: 14px;
                    border: 1px solid var(--border-color);
                    animation: slideUp 0.25s cubic-bezier(0.16, 1, 0.3, 1) forwards;
                }

                @keyframes slideUp {
                    from { opacity: 0; transform: translateY(16px); }
                    to { opacity: 1; transform: translateY(0); }
                }

                .chat-panel.open {
                    display: flex;
                }

                .chat-header {
                    background: #0f172a;
                    border-bottom: 1px solid var(--border-color);
                    color: #f8fafc;
                    padding: 13px 18px;
                    font-weight: 700;
                    font-size: 0.92rem;
                    letter-spacing: 0.4px;
                    display: flex;
                    justify-content: space-between;
                    align-items: center;
                }

                .close-btn {
                    background: rgba(255, 255, 255, 0.08);
                    border: 1px solid rgba(255, 255, 255, 0.12);
                    color: #94a3b8;
                    width: 26px;
                    height: 26px;
                    border-radius: 50%;
                    font-size: 0.85rem;
                    cursor: pointer;
                    display: flex;
                    align-items: center;
                    justify-content: center;
                    transition: all 0.18s ease;
                }

                .close-btn:hover {
                    background: rgba(255, 255, 255, 0.2);
                    color: #f8fafc;
                }

                .demo-badge-bar {
                    background: rgba(14, 165, 233, 0.08);
                    padding: 7px 16px;
                    font-size: 0.72rem;
                    color: #38bdf8;
                    font-family: 'JetBrains Mono', Consolas, monospace;
                    display: flex;
                    align-items: center;
                    justify-content: space-between;
                    border-bottom: 1px solid var(--border-color);
                    font-weight: 600;
                }

                .chat-messages {
                    flex: 1;
                    padding: 16px;
                    overflow-y: auto;
                    display: flex;
                    flex-direction: column;
                    gap: 12px;
                    background: var(--chat-bg);
                }

                .message {
                    max-width: 90%;
                    padding: 11px 15px;
                    border-radius: 12px;
                    font-size: 0.86rem;
                    line-height: 1.55;
                    word-wrap: break-word;
                    white-space: pre-wrap;
                }

                .message.user {
                    background: #0284c7;
                    color: #ffffff;
                    align-self: flex-end;
                    border-bottom-right-radius: 2px;
                    border: 1px solid rgba(255, 255, 255, 0.18);
                    font-weight: 500;
                }

                .message.assistant {
                    background: rgba(18, 26, 42, 0.85);
                    backdrop-filter: blur(12px);
                    color: #f1f5f9;
                    align-self: flex-start;
                    border-bottom-left-radius: 2px;
                    border: 1px solid var(--border-color);
                    box-shadow: 0 4px 14px rgba(0, 0, 0, 0.3);
                }

                .quick-prompts-title {
                    font-size: 0.68rem;
                    color: #94a3b8;
                    font-weight: 700;
                    text-transform: uppercase;
                    letter-spacing: 0.8px;
                    margin-bottom: 4px;
                    width: 100%;
                }

                .quick-prompts {
                    padding: 10px 14px;
                    display: flex;
                    flex-wrap: wrap;
                    gap: 6px;
                    background: var(--bg-color);
                    border-top: 1px solid var(--border-color);
                    max-height: 140px;
                    overflow-y: auto;
                }

                .prompt-chip {
                    background: rgba(30, 41, 59, 0.6);
                    color: #cbd5e1;
                    border: 1px solid rgba(255, 255, 255, 0.1);
                    border-radius: 12px;
                    padding: 5px 11px;
                    font-size: 0.74rem;
                    cursor: pointer;
                    font-weight: 600;
                    transition: all 0.18s ease;
                }

                .prompt-chip:hover {
                    background: #0ea5e9;
                    color: #ffffff;
                    border-color: #0ea5e9;
                    transform: translateY(-1px);
                }

                .chat-input-area {
                    display: flex;
                    padding: 12px 14px;
                    background: #0b0f19;
                    border-top: 1px solid var(--border-color);
                }

                .chat-input {
                    flex: 1;
                    border: 1px solid var(--border-color);
                    border-radius: 18px;
                    padding: 9px 15px;
                    outline: none;
                    font-family: inherit;
                    font-size: 0.88rem;
                    background: rgba(18, 26, 42, 0.7);
                    color: #ffffff;
                    transition: border 0.18s;
                }

                .chat-input::placeholder {
                    color: #64748b;
                }

                .chat-input:focus {
                    border-color: #0ea5e9;
                    background: rgba(22, 32, 52, 0.85);
                }

                .send-btn {
                    background: #0284c7;
                    color: white;
                    border: 1px solid rgba(255, 255, 255, 0.2);
                    border-radius: 50%;
                    width: 38px;
                    height: 38px;
                    margin-left: 8px;
                    cursor: pointer;
                    display: flex;
                    align-items: center;
                    justify-content: center;
                    transition: all 0.18s ease;
                }

                .send-btn:hover {
                    background: #0ea5e9;
                    transform: scale(1.05);
                }
                
                .send-btn:disabled {
                    background: #475569;
                    box-shadow: none;
                    cursor: not-allowed;
                }

                .typing-indicator {
                    display: none;
                    align-self: flex-start;
                    padding: 10px 14px;
                    background: var(--bg-color);
                    border: 1px solid var(--border-color);
                    border-radius: 10px;
                    border-bottom-left-radius: 2px;
                }

                .dot {
                    display: inline-block;
                    width: 5px;
                    height: 5px;
                    border-radius: 50%;
                    background: var(--primary-color);
                    margin: 0 2px;
                    animation: bounce 1.4s infinite ease-in-out both;
                }
                .dot:nth-child(1) { animation-delay: -0.32s; }
                .dot:nth-child(2) { animation-delay: -0.16s; }
                
                @keyframes bounce {
                    0%, 80%, 100% { transform: scale(0); }
                    40% { transform: scale(1); }
                }
            </style>

            <div class="chatbot-container">
                <div class="chat-panel" id="chatPanel">
                    <div class="chat-header">
                        <span>⚡ TerraEdge Chennai Ops Assistant</span>
                        <button class="close-btn" id="closeBtn" aria-label="Close chat">✕</button>
                    </div>
                    <div class="demo-badge-bar">
                        <span>📍 CHENNAI (13.0325, 80.1808)</span>
                        <span>FIRE & FLOOD LIVE</span>
                    </div>
                    <div class="chat-messages" id="chatMessages">
                        <div class="message assistant">👋 <strong>Welcome to TerraEdge Emergency Operations!</strong><br><br>Live situational telemetry is active for <strong>Chennai</strong>:<br>• 🌊 <strong>Coastal Flood Node</strong> — ⚠️ Warning (64/100) · 3.18m Stage<br>• 🔥 <strong>North Fire Node</strong> — 🟡 Moderate (36/100) · 37.8°C Heat<br><br>Tap any scenario question below or ask about live sensor readings and emergency plans!</div>
                    </div>
                    <div class="typing-indicator" id="typingIndicator">
                        <div class="dot"></div>
                        <div class="dot"></div>
                        <div class="dot"></div>
                    </div>
                    <div class="quick-prompts">
                        <div class="quick-prompts-title">In-Built Node Situation Queries:</div>
                        <button class="prompt-chip">🌊 Flood Situation (13.0325° N)</button>
                        <button class="prompt-chip">🔥 Fire Situation (13.0355° N)</button>
                        <button class="prompt-chip">🚨 Top Risk & Priority Assessment</button>
                        <button class="prompt-chip">📊 Live Sensor Telemetry Readings</button>
                        <button class="prompt-chip">🛡️ Evacuation & Emergency Guidelines</button>
                        <button class="prompt-chip">📈 Severity & Model Confidence (64 vs 36)</button>
                    </div>
                    <form class="chat-input-area" id="chatForm">
                        <input type="text" class="chat-input" id="chatInput" placeholder="Ask about Chennai Flood or Fire situation..." autocomplete="off">
                        <button type="submit" class="send-btn" id="sendBtn" title="Send message">
                            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M22 2L11 13M22 2l-7 20-4-9-9-4 20-7z"/></svg>
                        </button>
                    </form>
                </div>
                
                <button class="chat-button" id="toggleBtn" title="Open TerraEdge Operations Assistant">
                    <svg viewBox="0 0 24 24"><path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"></path></svg>
                </button>
            </div>
        `;
    }

    setupEventListeners() {
        const toggleBtn = this.shadowRoot.getElementById('toggleBtn');
        const closeBtn = this.shadowRoot.getElementById('closeBtn');
        const chatForm = this.shadowRoot.getElementById('chatForm');
        const chatInput = this.shadowRoot.getElementById('chatInput');
        const prompts = this.shadowRoot.querySelectorAll('.prompt-chip');

        toggleBtn.addEventListener('click', () => this.toggleChat());
        closeBtn.addEventListener('click', () => this.toggleChat());
        
        chatForm.addEventListener('submit', (e) => {
            e.preventDefault();
            this.sendMessage(chatInput.value);
        });

        prompts.forEach(prompt => {
            prompt.addEventListener('click', () => {
                this.sendMessage(prompt.innerText);
            });
        });
    }

    toggleChat() {
        this.isOpen = !this.isOpen;
        const panel = this.shadowRoot.getElementById('chatPanel');
        if (this.isOpen) {
            panel.classList.add('open');
            this.shadowRoot.getElementById('chatInput').focus();
        } else {
            panel.classList.remove('open');
        }
    }

    addMessage(text, sender) {
        const messagesDiv = this.shadowRoot.getElementById('chatMessages');
        const msgDiv = document.createElement('div');
        msgDiv.className = `message ${sender}`;
        
        // Basic markdown formatting
        let formattedText = text
            .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
            .replace(/\*(.*?)\*/g, '<em>$1</em>')
            .replace(/`([^`]+)`/g, '<code style="background:rgba(0,0,0,0.06);padding:2px 4px;border-radius:4px;font-family:monospace;font-size:0.85em;">$1</code>');
        
        msgDiv.innerHTML = formattedText;
        messagesDiv.appendChild(msgDiv);
        messagesDiv.scrollTop = messagesDiv.scrollHeight;
    }

    setTyping(isTyping) {
        const indicator = this.shadowRoot.getElementById('typingIndicator');
        const sendBtn = this.shadowRoot.getElementById('sendBtn');
        if (indicator) indicator.style.display = isTyping ? 'flex' : 'none';
        if (sendBtn) sendBtn.disabled = isTyping;
    }

    sendMessage(text) {
        if (!text || !text.trim()) return;

        const chatInput = this.shadowRoot.getElementById('chatInput');
        chatInput.value = '';

        this.addMessage(text, 'user');
        this.history.push({ role: 'user', content: text });

        this.setTyping(true);

        // Instantly generate automated situational answer for Chennai Fire & Flood nodes
        setTimeout(() => {
            const reply = this.getAutomatedAnswer(text);
            this.addMessage(reply, 'assistant');
            this.history.push({ role: 'assistant', content: reply });
            this.setTyping(false);
        }, 300);
    }
}

customElements.define('terra-edge-chat', TerraEdgeChat);
