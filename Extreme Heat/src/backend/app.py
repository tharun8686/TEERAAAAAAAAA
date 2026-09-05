from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional
import datetime
import os
import sys
import pandas as pd
import joblib

# Add src to sys.path
base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(base_dir)

from inference.heat_inference import HeatRiskPredictor

# Shared Supabase data layer (repo-root /common). Falls back to in-memory
# storage automatically when SUPABASE_URL / SUPABASE_SERVICE_KEY are unset.
REPO_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
sys.path.append(os.path.join(REPO_ROOT, 'common'))
import terra_supabase as db

HAZARD = "heat"

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
    title="Extreme Heat Edge-AI API",
    description="India Weather-Node Calibrated Extreme Heat Risk Engine",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

predictor = None

@app.on_event("startup")
def load_engine():
    global predictor
    models_dir = os.path.join(os.path.dirname(base_dir), "models")
    predictor = HeatRiskPredictor(models_dir)
    print("Extreme Heat Inference Engine Loaded Successfully!")

    # Publish the built-in station inventory to Supabase (no-op when unconfigured)
    db.seed_nodes(HAZARD, stations_db)

stations_db = [
    {"station_id": "MH-CWPRS", "name": "Pune CWPRS Campus", "city": "Pune", "lat": 18.4350, "lon": 73.7915, "status": "ONLINE"}
]


class HeatTelemetryPayload(BaseModel):
    station_id: Optional[str] = "MH-CWPRS"
    temperature_c: float
    humidity: float
    solar_radiation: float
    wind_speed_kmh: float
    rainfall_mm: Optional[float] = 0.0
    temperature_rate: Optional[float] = 0.0
    humidity_rate: Optional[float] = 0.0
    solar_radiation_rate: Optional[float] = 0.0
    rolling_mean_temperature: Optional[float] = None
    rolling_mean_humidity: Optional[float] = None
    rolling_std_temperature: Optional[float] = 1.5
    rolling_std_humidity: Optional[float] = 5.0
    cumulative_hot_hours: Optional[int] = 0
    nighttime_cooling_deficit: Optional[float] = 0.0

@app.get("/")
def root():
    return {"message": "Extreme Heat AI API Operational", "version": "1.0.0"}

@app.get("/health")
def health_check():
    return {"status": "healthy", "model_loaded": predictor is not None, "database": db.status()}

@app.get("/api/config")
def get_config():
    return {"google_maps_api_key": load_env_key()}

@app.get("/api/stations")
def get_stations():
    return db.fetch_nodes(HAZARD, stations_db)

@app.post("/api/predict")
def predict_heat(payload: HeatTelemetryPayload):
    # Prepare payload with fallbacks
    data_dict = payload.model_dump()
    if data_dict["rolling_mean_temperature"] is None:
        data_dict["rolling_mean_temperature"] = data_dict["temperature_c"]
    if data_dict["rolling_mean_humidity"] is None:
        data_dict["rolling_mean_humidity"] = data_dict["humidity"]
        
    df_input = pd.DataFrame([data_dict])
    result = predictor.predict_heat_risk(df_input)
    
    result["station_id"] = payload.station_id
    timestamp_str = datetime.datetime.utcnow().isoformat() + "Z"
    result["timestamp"] = timestamp_str

    # Record every inference in Supabase (skipped when SUPABASE_LOG_PREDICTIONS=false)
    db.log_prediction(HAZARD, payload.station_id, data_dict, result)

    if result.get("severity") in ["WARNING", "CRITICAL"]:
        alert_entry = {
            "alert_id": db.next_alert_id(HAZARD, "HEAT-ALT-"),
            "station_id": payload.station_id,
            "severity": result["severity"],
            "heat_risk_probability": result["heat_risk_probability"],
            "confidence": result["confidence"],
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
    uvicorn.run(app, host="127.0.0.1", port=8004)
