from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional
import datetime
import os
import sys

# Add src to sys.path
base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(base_dir)
from inference import AirPollutionInferenceEngine

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
    title="AirPollution Edge-AI API",
    description="India CPCB Air Pollution Early Warning Engine",
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
    engine = AirPollutionInferenceEngine()
    print("AirPollution Inference Engine Loaded Successfully!")

stations_db = [
    {"station_id": "DEL-ITO", "name": "Delhi ITO Station", "city": "Delhi", "lat": 28.6289, "lon": 77.2408, "status": "ONLINE"},
    {"station_id": "DEL-IHBAS", "name": "Delhi IHBAS Dilshad Garden", "city": "Delhi", "lat": 28.6812, "lon": 77.3195, "status": "ONLINE"},
    {"station_id": "DEL-PUSA", "name": "Delhi PUSA DPCC Node", "city": "Delhi", "lat": 28.6360, "lon": 77.1585, "status": "ONLINE"},
    {"station_id": "MUM-DEONAR", "name": "Mumbai Deonar IITM Station", "city": "Mumbai", "lat": 19.0565, "lon": 72.9150, "status": "ONLINE"},
    {"station_id": "PUN-BHOSARI", "name": "Pune Bhosari IITM Station", "city": "Pune", "lat": 18.6265, "lon": 73.8445, "status": "ONLINE"},
    {"station_id": "PUN-SHIVAJINAGAR", "name": "Pune Shivajinagar Station", "city": "Pune", "lat": 18.5308, "lon": 73.8475, "status": "ONLINE"}
]

alerts_db = []

class AirTelemetryPayload(BaseModel):
    station_id: Optional[str] = "DEL-ITO"
    pm25: float
    pm10: float
    gas_proxy: Optional[float] = 25.0
    temperature: Optional[float] = 28.0
    relative_humidity: Optional[float] = 65.0
    pressure: Optional[float] = 1012.0
    pm25_lag_15: Optional[float] = 40.0
    pm25_lag_30: Optional[float] = 35.0
    pm25_delta_30: Optional[float] = 10.0
    pm25_slope_30: Optional[float] = 0.33
    hour_sin: Optional[float] = 0.5
    hour_cos: Optional[float] = -0.86

@app.get("/")
def root():
    return {"message": "AirPollution AI API Operational", "version": "1.0.0"}

@app.get("/health")
def health_check():
    return {"status": "healthy", "model_loaded": engine is not None}

@app.get("/api/config")
def get_config():
    return {"google_maps_api_key": load_env_key()}

@app.get("/api/stations")
def get_stations():
    return stations_db

@app.post("/api/predict")
def predict_air(payload: AirTelemetryPayload):
    sensor_dict = payload.model_dump()
    result = engine.predict_air_pollution(sensor_dict)
    
    result["station_id"] = payload.station_id
    timestamp_str = datetime.datetime.utcnow().isoformat() + "Z"
    result["timestamp"] = timestamp_str

    if result["severity"] in ["WARNING", "CRITICAL"]:
        alert_entry = {
            "alert_id": f"AIR-ALT-{len(alerts_db)+1:04d}",
            "station_id": payload.station_id,
            "severity": result["severity"],
            "risk_score": result["risk_score"],
            "confidence": result["confidence"],
            "predicted_pm25_60m": result["predicted_pm25_60m"],
            "timestamp": timestamp_str
        }
        alerts_db.append(alert_entry)

    return result

@app.get("/api/alerts")
def get_alerts():
    return alerts_db

if __name__ == '__main__':
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8003)
