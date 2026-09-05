class TerraEdgeChat extends HTMLElement {
    constructor() {
        super();
        this.attachShadow({ mode: 'open' });
        this.isOpen = false;
        this.context = {};
        this.history = [];
        this.backendUrl = 'http://localhost:8007/api/chat';
        this.configUrl = 'http://localhost:8007/api/config';
        this.providers = [];
        this.selectedProvider = 'nvidia';
        this.selectedModel = 'meta/llama-3.1-405b-instruct';
    }

    async connectedCallback() {
        this.render();
        this.setupEventListeners();
        await this.loadConfig();
    }

    async loadConfig() {
        try {
            const res = await fetch(this.configUrl);
            const data = await res.json();
            this.providers = data.providers || [];
            if (this.providers.length > 0) {
                // Select first available provider and its first model
                this.selectedProvider = this.providers[0].id;
                this.selectedModel = this.providers[0].models[0].id;
                this.updateSelectors();
            }
        } catch (err) {
            console.error('Failed to load API config:', err);
        }
    }

    updateSelectors() {
        const providerSelect = this.shadowRoot.getElementById('providerSelect');
        const modelSelect = this.shadowRoot.getElementById('modelSelect');
        
        providerSelect.innerHTML = '';
        this.providers.forEach(p => {
            const opt = document.createElement('option');
            opt.value = p.id;
            opt.textContent = p.name;
            if (p.id === this.selectedProvider) opt.selected = true;
            providerSelect.appendChild(opt);
        });

        this.updateModelDropdown();
    }

    updateModelDropdown() {
        const modelSelect = this.shadowRoot.getElementById('modelSelect');
        modelSelect.innerHTML = '';
        
        const providerData = this.providers.find(p => p.id === this.selectedProvider);
        if (providerData) {
            providerData.models.forEach(m => {
                const opt = document.createElement('option');
                opt.value = m.id;
                opt.textContent = m.name;
                if (m.id === this.selectedModel) opt.selected = true;
                modelSelect.appendChild(opt);
            });
            // Ensure selectedModel is valid for this provider
            if (!providerData.models.find(m => m.id === this.selectedModel)) {
                this.selectedModel = providerData.models[0].id;
                modelSelect.value = this.selectedModel;
            }
        }
    }

    // Method to allow the dashboard to update the chatbot's context
    updateContext(newContext) {
        this.context = { ...this.context, ...newContext };
    }

    render() {
        this.shadowRoot.innerHTML = `
            <style>
                :host {
                    font-family: 'Inter', sans-serif;
                    --primary-color: #579477;
                    --primary-highlight: #68a588;
                    /* Custom properties pierce the shadow boundary, so these inherit the host page's
                       light/dark theme tokens automatically; the literal is only a fallback. */
                    --bg-color: var(--panel-bg, #ffffff);
                    --text-color: var(--text-primary, #1f2937);
                    --border-color: var(--panel-border, #e5e7eb);
                    --chat-bg: var(--bg-deep, #f3f4f6);
                    --shadow: 0 12px 30px rgba(0, 0, 0, 0.24);
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

                .chat-button {
                    background: linear-gradient(135deg, var(--primary-highlight), var(--primary-color));
                    color: white;
                    border: none;
                    border-radius: 50%;
                    width: 60px;
                    height: 60px;
                    cursor: pointer;
                    box-shadow: var(--shadow);
                    display: flex;
                    align-items: center;
                    justify-content: center;
                    transition: transform 0.2s ease;
                }

                .chat-button:hover {
                    transform: scale(1.05);
                }

                .chat-button svg {
                    width: 28px;
                    height: 28px;
                    fill: none;
                    stroke: currentColor;
                    stroke-width: 2;
                }

                .chat-panel {
                    display: none;
                    width: 380px;
                    height: 600px;
                    max-height: calc(100vh - 100px);
                    background: var(--bg-color);
                    border-radius: 10px;
                    box-shadow: var(--shadow);
                    overflow: hidden;
                    flex-direction: column;
                    margin-bottom: 16px;
                    border: 1px solid var(--border-color);
                    opacity: 0;
                    transform: translateY(20px);
                    transition: opacity 0.3s ease, transform 0.3s ease;
                }

                .chat-panel.open {
                    display: flex;
                    opacity: 1;
                    transform: translateY(0);
                }

                .chat-header {
                    background: linear-gradient(135deg, var(--primary-highlight), var(--primary-color));
                    color: white;
                    padding: 16px;
                    font-weight: 600;
                    display: flex;
                    justify-content: space-between;
                    align-items: center;
                }

                .close-btn {
                    background: none;
                    border: none;
                    color: white;
                    cursor: pointer;
                    font-size: 1.2rem;
                }
                
                .config-bar {
                    background: var(--chat-bg);
                    padding: 8px 12px;
                    display: flex;
                    gap: 8px;
                    border-bottom: 1px solid var(--border-color);
                    font-size: 0.8rem;
                }
                
                .config-bar select {
                    flex: 1;
                    padding: 4px;
                    border: 1px solid var(--border-color);
                    border-radius: 4px;
                    background: var(--bg-color);
                    color: var(--text-color);
                    font-family: inherit;
                    font-size: 0.8rem;
                    outline: none;
                }

                .chat-messages {
                    flex: 1;
                    padding: 16px;
                    overflow-y: auto;
                    display: flex;
                    flex-direction: column;
                    gap: 12px;
                    background-color: var(--chat-bg);
                }

                .message {
                    max-width: 80%;
                    padding: 12px 16px;
                    border-radius: 12px;
                    font-size: 0.95rem;
                    line-height: 1.4;
                    word-wrap: break-word;
                }

                .message.user {
                    background-color: var(--primary-color);
                    color: white;
                    align-self: flex-end;
                    border-bottom-right-radius: 4px;
                }

                .message.assistant {
                    background-color: var(--bg-color);
                    color: var(--text-color);
                    align-self: flex-start;
                    border-bottom-left-radius: 4px;
                    border: 1px solid var(--border-color);
                }

                .quick-prompts {
                    padding: 8px 16px;
                    display: flex;
                    flex-wrap: wrap;
                    gap: 8px;
                    background: var(--bg-color);
                    border-top: 1px solid var(--border-color);
                }

                .prompt-chip {
                    background-color: var(--chat-bg);
                    border: 1px solid var(--border-color);
                    border-radius: 16px;
                    padding: 6px 12px;
                    font-size: 0.8rem;
                    cursor: pointer;
                    transition: background-color 0.2s;
                }

                .prompt-chip:hover {
                    background-color: var(--border-color);
                }

                .chat-input-area {
                    display: flex;
                    padding: 16px;
                    background: var(--bg-color);
                    border-top: 1px solid var(--border-color);
                }

                .chat-input {
                    flex: 1;
                    border: 1px solid var(--border-color);
                    border-radius: 20px;
                    padding: 10px 16px;
                    outline: none;
                    font-family: inherit;
                    font-size: 0.95rem;
                    background: var(--bg-color);
                    color: var(--text-color);
                }

                .chat-input:focus {
                    border-color: var(--primary-color);
                }

                .send-btn {
                    background: var(--primary-color);
                    color: white;
                    border: none;
                    border-radius: 50%;
                    width: 40px;
                    height: 40px;
                    margin-left: 8px;
                    cursor: pointer;
                    display: flex;
                    align-items: center;
                    justify-content: center;
                }
                
                .send-btn:disabled {
                    background: #9ca3af;
                    cursor: not-allowed;
                }

                .typing-indicator {
                    display: none;
                    align-self: flex-start;
                    padding: 12px 16px;
                    background: var(--bg-color);
                    border: 1px solid var(--border-color);
                    border-radius: 12px;
                    border-bottom-left-radius: 4px;
                }

                .dot {
                    display: inline-block;
                    width: 6px;
                    height: 6px;
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
                        TerraEdge Ops Assistant
                        <button class="close-btn" id="closeBtn">✖</button>
                    </div>
                    <div class="config-bar">
                        <select id="providerSelect" title="Select Provider"><option>Loading...</option></select>
                        <select id="modelSelect" title="Select Model"><option>Loading...</option></select>
                    </div>
                    <div class="chat-messages" id="chatMessages">
                        <div class="message assistant">Hello! I am your TerraEdge Operations Assistant. I can help you interpret hazard data, node statuses, and alerts. How can I assist you today?</div>
                    </div>
                    <div class="typing-indicator" id="typingIndicator">
                        <div class="dot"></div>
                        <div class="dot"></div>
                        <div class="dot"></div>
                    </div>
                    <div class="quick-prompts">
                        <button class="prompt-chip">What is the top risk here?</button>
                        <button class="prompt-chip">Explain severity score</button>
                        <button class="prompt-chip">Summarize current alerts</button>
                    </div>
                    <form class="chat-input-area" id="chatForm">
                        <input type="text" class="chat-input" id="chatInput" placeholder="Ask about this region..." autocomplete="off">
                        <button type="submit" class="send-btn" id="sendBtn">
                            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M22 2L11 13M22 2l-7 20-4-9-9-4 20-7z"/></svg>
                        </button>
                    </form>
                </div>
                
                <button class="chat-button" id="toggleBtn">
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
        const providerSelect = this.shadowRoot.getElementById('providerSelect');
        const modelSelect = this.shadowRoot.getElementById('modelSelect');

        providerSelect.addEventListener('change', (e) => {
            this.selectedProvider = e.target.value;
            this.updateModelDropdown();
        });

        modelSelect.addEventListener('change', (e) => {
            this.selectedModel = e.target.value;
        });

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
        
        // Basic markdown-like formatting (bold)
        const formattedText = text.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>');
        msgDiv.innerHTML = formattedText;
        
        messagesDiv.appendChild(msgDiv);
        messagesDiv.scrollTop = messagesDiv.scrollHeight;
    }

    setTyping(isTyping) {
        const indicator = this.shadowRoot.getElementById('typingIndicator');
        const sendBtn = this.shadowRoot.getElementById('sendBtn');
        indicator.style.display = isTyping ? 'flex' : 'none';
        sendBtn.disabled = isTyping;
    }

    async sendMessage(text) {
        if (!text.trim()) return;

        const chatInput = this.shadowRoot.getElementById('chatInput');
        chatInput.value = '';

        this.addMessage(text, 'user');
        
        // Save to history
        this.history.push({ role: 'user', content: text });

        this.setTyping(true);

        try {
            const response = await fetch(this.backendUrl, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    message: text,
                    context: this.context,
                    history: this.history.slice(-10), // Send last 10 messages for context
                    provider: this.selectedProvider,
                    model: this.selectedModel
                })
            });

            if (!response.ok) {
                const errData = await response.json().catch(() => ({}));
                throw new Error(errData.error || 'API Error');
            }

            const data = await response.json();
            const reply = data.reply || "I'm sorry, I couldn't process that request.";
            
            this.addMessage(reply, 'assistant');
            this.history.push({ role: 'assistant', content: reply });

        } catch (error) {
            console.error('Chatbot error:', error);
            this.addMessage(error.message || "Connection error. Please ensure the TerraEdge backend is running.", 'assistant');
        } finally {
            this.setTyping(false);
        }
    }
}

customElements.define('terra-edge-chat', TerraEdgeChat);
