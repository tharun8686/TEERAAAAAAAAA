from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional
import datetime
import os
import sys
import pandas as pd

# Add src to sys.path
base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(base_dir)

from inference.industrial_inference import IndustrialEmissionsPredictor

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
    title="Industrial Emissions / Chemical Leak API",
    description="Early Warning AI system for toxic gas emissions and chemical plumes",
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
    predictor = IndustrialEmissionsPredictor(models_dir)
    print("Industrial Emissions Inference Engine Loaded Successfully!")

stations_db = [
    {"station_id": "IND-PLUME-1", "name": "Vizag Industrial Zone", "city": "Visakhapatnam", "lat": 17.6868, "lon": 83.2185, "status": "ONLINE"}
]

alerts_db = []

class IndustrialTelemetryPayload(BaseModel):
    station_id: Optional[str] = "IND-PLUME-1"
    gas_response: float
    smoke_or_proxy_response: Optional[float] = None
    pm25: float
    pm10: float
    temperature_c: Optional[float] = 30.0
    humidity: Optional[float] = 60.0
    pressure: Optional[float] = 1010.0
    gas_rate: Optional[float] = 0.0
    pm25_rate: Optional[float] = 0.0
    pm10_rate: Optional[float] = 0.0
    rolling_mean_gas: Optional[float] = None
    rolling_mean_pm25: Optional[float] = None
    rolling_std_gas: Optional[float] = 2.0
    rolling_std_pm25: Optional[float] = 1.0
    gas_spike_score: Optional[float] = 1.0
    particulate_spike_score: Optional[float] = 1.0
    persistence_score: Optional[int] = 0

@app.get("/")
def root():
    return {"message": "Industrial Emissions API Operational", "version": "1.0.0"}

@app.get("/health")
def health_check():
    return {"status": "healthy", "model_loaded": predictor is not None}

@app.get("/api/config")
def get_config():
    return {"google_maps_api_key": load_env_key()}

@app.get("/api/stations")
def get_stations():
    return stations_db

@app.post("/api/predict")
def predict_leak(payload: IndustrialTelemetryPayload):
    data_dict = payload.model_dump()
    
    # Map back to model expected feature names with dots
    data_dict["PM2.5"] = data_dict.pop("pm25")
    data_dict["PM10"] = data_dict.pop("pm10")
    data_dict["PM2.5_rate"] = data_dict.pop("pm25_rate")
    data_dict["PM10_rate"] = data_dict.pop("pm10_rate")
    data_dict["rolling_mean_PM2.5"] = data_dict.pop("rolling_mean_pm25")
    data_dict["rolling_std_PM2.5"] = data_dict.pop("rolling_std_pm25")
    
    # Fill defaults
    if data_dict["smoke_or_proxy_response"] is None:
        data_dict["smoke_or_proxy_response"] = data_dict["gas_response"] * 0.8
    if data_dict["rolling_mean_gas"] is None:
        data_dict["rolling_mean_gas"] = data_dict["gas_response"]
    if data_dict["rolling_mean_PM2.5"] is None:
        data_dict["rolling_mean_PM2.5"] = data_dict["PM2.5"]
        
    df_input = pd.DataFrame([data_dict])
    result = predictor.predict_industrial_risk(df_input)
    
    result["station_id"] = payload.station_id
    timestamp_str = datetime.datetime.utcnow().isoformat() + "Z"
    result["timestamp"] = timestamp_str

    if result.get("severity") in ["WARNING", "CRITICAL"]:
        alert_entry = {
            "alert_id": f"IND-ALT-{len(alerts_db)+1:04d}",
            "station_id": payload.station_id,
            "severity": result["severity"],
            "leak_risk_probability": result["leak_risk_probability"],
            "confidence": result["confidence"],
            "timestamp": timestamp_str
        }
        alerts_db.append(alert_entry)

    return result

@app.get("/api/alerts")
def get_alerts():
    return alerts_db

if __name__ == '__main__':
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8005)
