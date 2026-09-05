from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
import datetime
import os
import sys

# Add src/inference to sys.path
base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(os.path.join(base_dir, 'inference'))
from landslide_inference import LandslideInferenceEngine

# Shared Supabase data layer (repo-root /common). Falls back to in-memory
# storage automatically when SUPABASE_URL / SUPABASE_SERVICE_KEY are unset.
REPO_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
sys.path.append(os.path.join(REPO_ROOT, 'common'))
import terra_supabase as db

HAZARD = "land"

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
    title="Landslide Edge-AI API",
    description="Slope Instability & Early Warning AI Engine",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

engine = None

@app.on_event("startup")
def load_engine():
    global engine
    engine = LandslideInferenceEngine()
    print("Landslide Inference Engine Loaded Successfully!")

    # Publish the built-in sensor inventory to Supabase (no-op when unconfigured)
    db.seed_nodes(HAZARD, nodes_db)

nodes_db = [
    {"node_id": "NODE-LND-01", "type": "Type-A", "location": "Western Ghats Slope Station", "lat": 11.4100, "lon": 76.6900, "status": "ONLINE"},
    {"node_id": "NODE-LND-02", "type": "Type-B (ESP32-S3)", "location": "Valparai Hill Pass Node", "lat": 10.3270, "lon": 76.9550, "status": "ONLINE"},
    {"node_id": "NODE-LND-03", "type": "Type-A", "location": "Munnar Slope Reserve", "lat": 10.0889, "lon": 77.0595, "status": "ONLINE"}
]


class LandslideTelemetryPayload(BaseModel):
    node_id: str
    soil_moisture_vwc: float
    soil_moisture_rate: Optional[float] = 0.01
    tilt_magnitude: float
    tilt_rate: Optional[float] = 0.05
    vibration_rate: Optional[float] = 2.0
    temperature: Optional[float] = 22.0
    humidity: Optional[float] = 65.0
    rainfall_24h: Optional[float] = 10.0

@app.get("/")
def root():
    return {"message": "Landslide AI API Operational", "version": "1.0.0"}

@app.get("/health")
def health_check():
    return {"status": "healthy", "model_loaded": engine is not None, "database": db.status()}

@app.get("/api/config")
def get_config():
    return {"google_maps_api_key": load_env_key()}

@app.get("/api/nodes")
def get_nodes():
    return db.fetch_nodes(HAZARD, nodes_db)

@app.post("/api/predict")
def predict_landslide(payload: LandslideTelemetryPayload):
    sensor_dict = payload.model_dump()
    result = engine.predict_landslide(sensor_dict)
    
    result["node_id"] = payload.node_id
    timestamp_str = datetime.datetime.utcnow().isoformat() + "Z"
    result["timestamp"] = timestamp_str

    # Record every inference in Supabase (skipped when SUPABASE_LOG_PREDICTIONS=false)
    db.log_prediction(HAZARD, payload.node_id, sensor_dict, result)

    if result["severity"] in ["WARNING", "CRITICAL"]:
        alert_entry = {
            "alert_id": db.next_alert_id(HAZARD, "LND-ALT-"),
            "node_id": payload.node_id,
            "severity": result["severity"],
            "risk_probability": result["risk_probability"],
            "anomaly_score": result["anomaly_score"],
            "sensor_health": result["sensor_health"],
            "top_features": result["top_features"],
            "timestamp": timestamp_str
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
    uvicorn.run(app, host="127.0.0.1", port=8002)
