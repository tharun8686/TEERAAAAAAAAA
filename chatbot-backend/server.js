require('dotenv').config({ path: '../.env' }); // Load from the root project folder
const express = require('express');
const cors = require('cors');
const { getSystemPrompt } = require('./prompt');

const app = express();
const PORT = process.env.CHATBOT_API_PORT || 8007;

app.use(cors());
app.use(express.json());

// API Endpoints
const NVIDIA_API_URL = "https://integrate.api.nvidia.com/v1/chat/completions";
const OPENROUTER_API_URL = "https://openrouter.ai/api/v1/chat/completions";

// Model Registry
const MODEL_REGISTRY = {
    nvidia: [
        { id: 'meta/llama2-70b', name: 'Llama 2 70B' },
        { id: 'meta/llama-3.1-405b-instruct', name: 'Llama 3.1 405B Instruct' },
        { id: 'nvidia/llama-3.1-nemotron-70b-instruct', name: 'Nemotron 70B Instruct' }
    ],
    openrouter: [
        { id: 'openai/gpt-4o-mini', name: 'GPT-4o Mini' },
        { id: 'anthropic/claude-3.5-sonnet', name: 'Claude 3.5 Sonnet' },
        { id: 'google/gemini-pro-1.5', name: 'Gemini 1.5 Pro' },
        { id: 'meta-llama/llama-3.1-8b-instruct', name: 'Llama 3.1 8B Instruct' }
    ]
};

// Route to get available providers and models
app.get('/api/config', (req, res) => {
    const providers = [];
    
    if (process.env.NV_API_KEY) {
        providers.push({
            id: 'nvidia',
            name: 'NVIDIA',
            models: MODEL_REGISTRY.nvidia
        });
    }
    
    if (process.env.OPENROUTER_API_KEY) {
        providers.push({
            id: 'openrouter',
            name: 'OpenRouter',
            models: MODEL_REGISTRY.openrouter
        });
    }
    
    res.json({ providers });
});

// Route to securely provide the Google Maps API key to the frontend
app.get('/api/maps-key', (req, res) => {
    if (process.env.GOOGLE_MAPS_API_KEY) {
        res.json({ key: process.env.GOOGLE_MAPS_API_KEY });
    } else {
        res.status(404).json({ error: 'Google Maps API key not configured in .env' });
    }
});

app.post('/api/chat', async (req, res) => {
    try {
        const { message, context, history = [], provider = 'nvidia', model = 'meta/llama-3.1-405b-instruct' } = req.body;

        if (!message) {
            return res.status(400).json({ error: 'Message is required' });
        }

        // Determine routing configuration
        let apiUrl = '';
        let apiKey = '';
        let headers = {
            'Content-Type': 'application/json'
        };

        if (provider === 'nvidia') {
            if (!process.env.NV_API_KEY) {
                return res.status(500).json({ error: 'NVIDIA provider authentication failed: NV_API_KEY not configured.' });
            }
            apiUrl = NVIDIA_API_URL;
            apiKey = process.env.NV_API_KEY;
        } else if (provider === 'openrouter') {
            if (!process.env.OPENROUTER_API_KEY) {
                return res.status(500).json({ error: 'OpenRouter provider authentication failed: OPENROUTER_API_KEY not configured.' });
            }
            apiUrl = OPENROUTER_API_URL;
            apiKey = process.env.OPENROUTER_API_KEY;
            // OpenRouter required headers
            headers['HTTP-Referer'] = 'http://localhost'; // Default to localhost for dashboard
            headers['X-Title'] = 'TerraEdge Operations Assistant';
        } else {
            return res.status(400).json({ error: 'Invalid provider specified.' });
        }
        
        headers['Authorization'] = `Bearer ${apiKey}`;

        const systemPrompt = getSystemPrompt(context);

        const messages = [
            { role: "system", content: systemPrompt },
            ...history,
            { role: "user", content: message }
        ];

        const response = await fetch(apiUrl, {
            method: 'POST',
            headers: headers,
            body: JSON.stringify({
                model: model,
                messages: messages,
                max_tokens: 500,
                temperature: 0.2
            })
        });

        if (!response.ok) {
            const errData = await response.text();
            console.error(`[${provider.toUpperCase()}] API Error:`, errData);
            
            let errorMessage = `${provider === 'nvidia' ? 'NVIDIA' : 'OpenRouter'} provider failed to process the request.`;
            
            if (response.status === 401) {
                errorMessage = `${provider === 'nvidia' ? 'NVIDIA' : 'OpenRouter'} provider authentication failed.`;
            } else if (response.status === 404 && errData.includes('Not found for account')) {
                errorMessage = 'NVIDIA API Error: Your API key does not have access to this model. Please check your model selection or API key on build.nvidia.com.';
            } else if (response.status === 429) {
                errorMessage = `${provider === 'nvidia' ? 'NVIDIA' : 'OpenRouter'} rate limit exceeded. Please try again later.`;
            }
            
            return res.status(500).json({ error: errorMessage });
        }

        const data = await response.json();
        const reply = data.choices[0].message.content;

        res.json({ reply });

    } catch (error) {
        console.error('Chat endpoint error:', error);
        res.status(500).json({ error: 'Internal server error' });
    }
});

app.listen(PORT, () => {
    console.log(`TerraEdge Chatbot API running on port ${PORT}`);
});
