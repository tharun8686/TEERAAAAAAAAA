from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
import datetime
import os
import sys

# Add src/inference to path
base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(os.path.join(base_dir, 'inference'))
from fire_inference import FireInferenceEngine

# Shared Supabase data layer (repo-root /common). Falls back to in-memory
# storage automatically when SUPABASE_URL / SUPABASE_SERVICE_KEY are unset.
REPO_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
sys.path.append(os.path.join(REPO_ROOT, 'common'))
import terra_supabase as db

HAZARD = "fire"

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
    title="ForestWildFire AI API",
    description="Wildfire Early Warning & Smoke Anomaly Detection API",
    version="1.0.0"
)

# Enable CORS for HTML Dashboard
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
    engine = FireInferenceEngine()
    print("ForestWildFire Inference Engine Loaded!")

    # Publish the built-in sensor inventory to Supabase (no-op when unconfigured)
    db.seed_nodes(HAZARD, nodes_db)

nodes_db = [
    {"node_id": "NODE-FWF-01", "type": "Type-A", "location": "Nilgiris Forest Reserve", "lat": 11.4916, "lon": 76.7337, "status": "ONLINE"},
    {"node_id": "NODE-FWF-02", "type": "Type-B (ESP32-S3)", "location": "Anamalai Tiger Reserve", "lat": 10.5050, "lon": 76.9650, "status": "ONLINE"},
    {"node_id": "NODE-FWF-03", "type": "Type-A", "location": "Mudumalai Forest Zone", "lat": 11.5623, "lon": 76.5345, "status": "ONLINE"},
]


class WildfireTelemetryPayload(BaseModel):
    node_id: Optional[str] = "NODE-FWF-01"
    temperature: float
    humidity: float
    pressure: Optional[float] = 1008.0
    pm25: float
    tvoc: float
    raw_ethanol: Optional[float] = 3000.0
    temperature_rate: Optional[float] = 0.05
    humidity_rate: Optional[float] = -0.05
    pm25_rate: Optional[float] = 0.15
    tvoc_rate: Optional[float] = 0.10
    temperature_delta_5: Optional[float] = 1.2
    humidity_delta_5: Optional[float] = -2.5

@app.get("/")
def root():
    return {"message": "ForestWildFire AI API operational", "version": "1.0.0"}

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
def predict_wildfire(payload: WildfireTelemetryPayload):
    sensor_dict = payload.model_dump()
    result = engine.predict_fire(sensor_dict)
    
    result["node_id"] = payload.node_id
    timestamp_str = datetime.datetime.utcnow().isoformat() + "Z"
    result["timestamp"] = timestamp_str

    # Record every inference in Supabase (skipped when SUPABASE_LOG_PREDICTIONS=false)
    db.log_prediction(HAZARD, payload.node_id, sensor_dict, result)

    if result["severity"] in ["WARNING", "CRITICAL"]:
        alert_entry = {
            "alert_id": db.next_alert_id(HAZARD, "FIRE-ALT-"),
            "node_id": payload.node_id,
            "severity": result["severity"],
            "fire_probability": result["fire_probability"],
            "anomaly_score": result["anomaly_score"],
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
    uvicorn.run(app, host="127.0.0.1", port=8001)
