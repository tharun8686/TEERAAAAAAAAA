# TerraEdge — Deployment Architecture & Guide

## 1. Deployment Topology

TerraEdge can be deployed as a bare-metal Python service, a systemd daemon, or a Docker container on an industrial edge computer (Raspberry Pi 4/5, NVIDIA Jetson, or Intel NUC).

```
                      [ Field Nodes: ESP32-S3 ]
                                  │
                                  │ SX1278 LoRa 433 MHz
                                  ▼
           ┌──────────────────────────────────────────────┐
           │      Type B Edge Gateway (Docker / Host)     │
           │                                              │
           │  • FastAPI Server (Port 8000)                │
           │  • 7 Hazard ML Inference Engines             │
           │  • SQLite WAL Store-and-Forward Queue        │
           │  • Multi-Tier Failover Manager               │
           └──────────────────────┬───────────────────────┘
                                  │
             ┌────────────────────┼────────────────────┐
             ▼                    ▼                    ▼
     [ Wi-Fi / LAN ]       [ 4G LTE Modem ]    [ Iridium Satellite ]
             │                    │                    │
             └────────────────────┼────────────────────┘
                                  ▼
                    [ Cloud Database (Supabase) ]
                                  │
                                  ▼
                    [ Central Operations Dashboard ]
```

---

## 2. Docker Deployment

### Prerequisites
- Docker Engine 24+ & Docker Compose v2+

### Quickstart
```bash
# 1. Clone repository & configure environment
cp .env.example .env

# 2. Build and launch container
docker compose up -d --build

# 3. Verify health
curl http://localhost:8000/health/live
```

---

## 3. Host / Systemd Deployment (Linux)

```ini
[Unit]
Description=TerraEdge Type B Edge Gateway
After=network.target

[Service]
Type=simple
User=terraedge
WorkingDirectory=/opt/terraedge
ExecStart=/opt/terraedge/venv/bin/python -m gateway.app
Restart=always
RestartSec=5
EnvironmentFile=/opt/terraedge/.env

[Install]
WantedBy=multi-user.target
```
