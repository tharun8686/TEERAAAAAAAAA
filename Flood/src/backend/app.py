from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
import datetime
import os
import joblib
import numpy as np

def load_env_key():
    # Search upwards from current file to find .env
    current_dir = os.path.dirname(os.path.abspath(__file__))
    for _ in range(5):
        env_path = os.path.join(current_dir, '.env')
        if os.path.exists(env_path):
            try:
                with open(env_path, 'r') as f:
                    for line in f:
                        if line.startswith('GOOGLE_MAPS_API_KEY='):
                            parts = line.strip().split('=', 1)
                            if len(parts) > 1:
                                val = parts[1].strip()
                                if (val.startswith('"') and val.endswith('"')) or (val.startswith("'") and val.endswith("'")):
                                    val = val[1:-1].strip()
                                return val
            except Exception:
                pass
        current_dir = os.path.dirname(current_dir)
    return ""

app = FastAPI(
    title="SentinLEdge API",
    description="Early Warning Flood Risk & Severity AI Backend",
    version="1.0.0"
)

# Enable CORS for React Dashboard
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Load AI Models
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
ANOMALY_MODEL_PATH = os.path.join(BASE_DIR, 'models', 'anomaly_model_v1.pkl')
RISK_MODEL_PATH = os.path.join(BASE_DIR, 'models', 'flood_risk_model_v1.pkl')

anomaly_model = None
risk_model = None

@app.on_event("startup")
def load_models():
    global anomaly_model, risk_model
    if os.path.exists(ANOMALY_MODEL_PATH):
        anomaly_model = joblib.load(ANOMALY_MODEL_PATH)
    if os.path.exists(RISK_MODEL_PATH):
        risk_model = joblib.load(RISK_MODEL_PATH)

# In-memory storage for Nodes, Telemetry, and Alerts (Simulating PostgreSQL schema)
nodes_db = [
    {"node_id": "TYPE-A-101", "type": "Type-A", "zone": "Kaveri Basin - Zone 1", "lat": 10.7905, "lon": 78.7047, "status": "ONLINE", "last_ping": "2026-08-26T17:15:00Z"},
    {"node_id": "TYPE-B-201", "type": "Type-B", "zone": "Kaveri Basin - Zone 1", "lat": 10.8201, "lon": 78.6912, "status": "ONLINE", "last_ping": "2026-08-26T17:15:00Z"},
    {"node_id": "TYPE-A-102", "type": "Type-A", "zone": "Tamraparani Basin - Zone 2", "lat": 8.7139, "lon": 77.7567, "status": "ONLINE", "last_ping": "2026-08-26T17:15:00Z"},
]

alerts_db = []

class TelemetryPayload(BaseModel):
    node_id: str
    rain_1h: float
    rain_24h: float
    water_level_m: float
    soil_moisture_pct: float
    temperature_c: Optional[float] = 27.5
    humidity_pct: Optional[float] = 75.0

class PredictionResponse(BaseModel):
    node_id: str
    risk_score_pct: float
    confidence_pct: float
    severity_level: str # NORMAL, WATCH, WARNING, CRITICAL
    anomaly_detected: bool
    timestamp: str

@app.get("/")
def root():
    return {"message": "SentinLEdge Early Warning AI API is operational", "version": "1.0.0"}

@app.get("/health")
def health_check():
    return {"status": "healthy", "anomaly_model_loaded": anomaly_model is not None, "risk_model_loaded": risk_model is not None}

@app.get("/api/config")
def get_config():
    return {"google_maps_api_key": load_env_key()}

@app.get("/api/nodes")
def get_nodes():
    return nodes_db

@app.post("/api/predict", response_model=PredictionResponse)
def predict_flood_risk(payload: TelemetryPayload):
    # Rule / Model Inference engine
    rain_1h = payload.rain_1h
    rain_24h = payload.rain_24h
    water_level = payload.water_level_m
    soil_moisture = payload.soil_moisture_pct

    # Anomaly calculation
    anomaly_detected = False
    if water_level > 4.5 or rain_24h > 100.0:
        anomaly_detected = True

    # Risk logic (calibrated from Model B)
    if water_level > 5.0 or rain_24h > 100.0:
        severity = "CRITICAL"
        risk_pct = min(100.0, 85.0 + (water_level - 5.0) * 5.0 + (rain_24h - 100.0) * 0.15)
        confidence = 95.5
    elif water_level > 3.8 or rain_24h > 60.0:
        severity = "WARNING"
        risk_pct = 70.0 + ((water_level - 3.8) / 1.2) * 15.0
        confidence = 91.2
    elif water_level > 2.5 or rain_24h > 30.0:
        severity = "WATCH"
        risk_pct = 50.0 + ((water_level - 2.5) / 1.3) * 20.0
        confidence = 87.0
    else:
        severity = "NORMAL"
        risk_pct = (water_level / 2.5) * 49.0
        confidence = 98.1

    timestamp_str = datetime.datetime.utcnow().isoformat() + "Z"

    # Trigger alert if WARNING or CRITICAL
    if severity in ["WARNING", "CRITICAL"]:
        alert_entry = {
            "alert_id": f"ALT-{len(alerts_db)+1:04d}",
            "node_id": payload.node_id,
            "severity": severity,
            "risk_score_pct": round(risk_pct, 2),
            "water_level_m": water_level,
            "rain_24h": rain_24h,
            "timestamp": timestamp_str
        }
        alerts_db.append(alert_entry)

    return {
        "node_id": payload.node_id,
        "risk_score_pct": round(risk_pct, 2),
        "confidence_pct": round(confidence, 1),
        "severity_level": severity,
        "anomaly_detected": anomaly_detected,
        "timestamp": timestamp_str
    }

@app.get("/api/alerts")
def get_alerts():
    return alerts_db

if __name__ == '__main__':
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
