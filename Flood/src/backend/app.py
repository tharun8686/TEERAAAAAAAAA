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

import sys
SRC_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(SRC_DIR)
from inference.flood_inference import FloodInferenceEngine

# Shared Supabase data layer (repo-root /common). Falls back to in-memory
# storage automatically when SUPABASE_URL / SUPABASE_SERVICE_KEY are unset.
REPO_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
sys.path.append(os.path.join(REPO_ROOT, 'common'))
import terra_supabase as db

HAZARD = "flood"

# Load AI Models
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
MODELS_DIR = os.path.join(BASE_DIR, 'models')

engine = None

@app.on_event("startup")
def load_models():
    global engine
    try:
        engine = FloodInferenceEngine(MODELS_DIR)
        print("Flood Inference Engine Loaded Successfully!")
    except Exception as e:
        print(f"Error loading Flood Inference Engine: {e}")

    # Publish the built-in sensor inventory to Supabase (no-op when unconfigured)
    db.seed_nodes(HAZARD, nodes_db)

# Built-in sensor inventory. Seeded into the Supabase `nodes` table on startup
# and used as the fallback whenever the database is unavailable.
nodes_db = [
    {"node_id": "TYPE-A-101", "type": "Type-A", "zone": "Kaveri Basin - Zone 1", "lat": 10.7905, "lon": 78.7047, "status": "ONLINE", "last_ping": "2026-08-26T17:15:00Z"},
    {"node_id": "TYPE-B-201", "type": "Type-B", "zone": "Kaveri Basin - Zone 1", "lat": 10.8201, "lon": 78.6912, "status": "ONLINE", "last_ping": "2026-08-26T17:15:00Z"},
    {"node_id": "TYPE-A-102", "type": "Type-A", "zone": "Tamraparani Basin - Zone 2", "lat": 8.7139, "lon": 77.7567, "status": "ONLINE", "last_ping": "2026-08-26T17:15:00Z"},
]

class TelemetryPayload(BaseModel):
    node_id: Optional[str] = "TYPE-A-101"
    rain_1h: float
    rain_24h: float
    water_level_m: float
    soil_moisture_pct: float
    temperature_c: Optional[float] = 27.5
    humidity_pct: Optional[float] = 75.0

@app.get("/")
def root():
    return {"message": "SentinLEdge Early Warning AI API is operational", "version": "1.2.0"}

@app.get("/health")
def health_check():
    return {"status": "healthy", "engine_loaded": engine is not None, "database": db.status()}

@app.get("/api/config")
def get_config():
    return {"google_maps_api_key": load_env_key()}

@app.get("/api/nodes")
def get_nodes():
    return db.fetch_nodes(HAZARD, nodes_db)

@app.post("/api/predict")
def predict_flood_risk(payload: TelemetryPayload):
    data_dict = payload.model_dump()
    if engine is not None:
        result = engine.predict_flood(data_dict)
    else:
        # Fallback if engine failed to load
        water_level = payload.water_level_m
        rain_24h = payload.rain_24h
        risk_pct = min(100.0, max(2.0, (water_level / 3.0) * 45 + (rain_24h / 100.0) * 35))
        severity = "CRITICAL" if risk_pct > 75 else "WARNING" if risk_pct > 50 else "WATCH" if risk_pct > 30 else "NORMAL"
        result = {
            "hazard": "Flood",
            "risk_probability": round(risk_pct / 100.0, 4),
            "confidence": 0.90,
            "severity": severity,
            "anomaly_score": 0.2,
            "sensor_health": 1.0,
            "top_features": ["water_level_m", "rain_24h"],
            "model_version": "v1.2.0-fallback",
            "timestamp": datetime.datetime.now(datetime.timezone.utc).isoformat(),
            "risk_score_pct": round(risk_pct, 1),
            "confidence_pct": 90.0,
            "severity_level": severity,
            "anomaly_detected": severity in ["WARNING", "CRITICAL"]
        }

    result["node_id"] = payload.node_id

    # Record every inference in Supabase (skipped when SUPABASE_LOG_PREDICTIONS=false)
    db.log_prediction(HAZARD, payload.node_id, data_dict, result)

    # Trigger alert if WARNING or CRITICAL
    if result.get("severity") in ["WARNING", "CRITICAL"]:
        alert_entry = {
            "alert_id": db.next_alert_id(HAZARD, "ALT-"),
            "node_id": payload.node_id,
            "severity": result["severity"],
            "risk_score_pct": result["risk_score_pct"],
            "water_level_m": payload.water_level_m,
            "rain_24h": payload.rain_24h,
            "timestamp": result["timestamp"]
        }
        db.insert_alert(HAZARD, alert_entry)

    return result

@app.get("/api/alerts")
def get_alerts(limit: int = 200):
    return db.fetch_alerts(HAZARD, limit=limit)

@app.get("/api/history")
def get_history(hours: int = 24):
    """Recent prediction history for this hazard, used by the Analytics dashboard."""
    return db.fetch_predictions(HAZARD, hours=hours)

@app.get("/api/db-status")
def get_db_status():
    """Reports whether this service is persisting to Supabase or running in-memory."""
    return db.status()

if __name__ == '__main__':
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

