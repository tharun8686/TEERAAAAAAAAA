from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional
import datetime
import os
import sys
import pandas as pd
import uvicorn

# Add src to sys.path
base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(base_dir)

from inference.water_inference import WaterQualityPredictor

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
    title="Water Quality Degradation / Contamination API",
    description="Early Warning AI system for municipal and ground water safety monitoring",
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
    predictor = WaterQualityPredictor(models_dir)
    print("Water Quality Degradation Inference Engine Loaded Successfully!")

stations_db = [
    {"station_id": "AP-WATER-CWC-1", "name": "Vizag Municipal Reservoir", "city": "Visakhapatnam", "lat": 17.7285, "lon": 83.3015, "status": "ONLINE"}
]

alerts_db = []

class WaterTelemetryPayload(BaseModel):
    station_id: Optional[str] = "AP-WATER-CWC-1"
    pH: float
    turbidity: float
    EC: float
    TDS: float
    dissolved_oxygen: Optional[float] = 7.5
    temperature_c: float
    
    # Optional rates/rolling params (with sensible defaults)
    pH_rate: Optional[float] = 0.0
    turbidity_rate: Optional[float] = 0.0
    EC_rate: Optional[float] = 0.0
    TDS_rate: Optional[float] = 0.0
    DO_rate: Optional[float] = 0.0
    
    rolling_mean_pH: Optional[float] = None
    rolling_mean_turbidity: Optional[float] = None
    rolling_mean_EC: Optional[float] = None
    rolling_mean_TDS: Optional[float] = None
    rolling_mean_DO: Optional[float] = None
    
    rolling_std_pH: Optional[float] = 0.05
    rolling_std_turbidity: Optional[float] = 0.2
    rolling_std_EC: Optional[float] = 10.0
    rolling_std_TDS: Optional[float] = 5.0
    rolling_std_DO: Optional[float] = 0.1
    
    acidity_shift_score: Optional[float] = None
    degradation_spike_score: Optional[float] = None
    conductivity_shift_score: Optional[float] = None
    oxygen_drop_score: Optional[float] = None
    persistence_score: Optional[int] = 0

@app.get("/")
def root():
    return {"message": "Water Quality Degradation API Operational", "version": "1.0.0"}

@app.get("/health")
def health_check():
    return {"status": "healthy", "model_loaded": predictor is not None}

@app.get("/api/stations")
def get_stations():
    return stations_db

@app.get("/api/config")
def get_config():
    return {"google_maps_api_key": load_env_key()}

@app.post("/api/predict")
def predict_water(payload: WaterTelemetryPayload):
    data_dict = payload.model_dump()
    
    # Backfill rolling/derived features if None
    if data_dict["rolling_mean_pH"] is None:
        data_dict["rolling_mean_pH"] = data_dict["pH"]
    if data_dict["rolling_mean_turbidity"] is None:
        data_dict["rolling_mean_turbidity"] = data_dict["turbidity"]
    if data_dict["rolling_mean_EC"] is None:
        data_dict["rolling_mean_EC"] = data_dict["EC"]
    if data_dict["rolling_mean_TDS"] is None:
        data_dict["rolling_mean_TDS"] = data_dict["TDS"]
    if data_dict["rolling_mean_DO"] is None:
        data_dict["rolling_mean_DO"] = data_dict["dissolved_oxygen"]
        
    # Derived scores
    if data_dict["acidity_shift_score"] is None:
        data_dict["acidity_shift_score"] = abs(data_dict["pH"] - 7.0)
    if data_dict["degradation_spike_score"] is None:
        data_dict["degradation_spike_score"] = data_dict["turbidity"] / (data_dict["rolling_mean_turbidity"] + 1e-5)
    if data_dict["conductivity_shift_score"] is None:
        data_dict["conductivity_shift_score"] = data_dict["EC"] / (data_dict["rolling_mean_EC"] + 1e-5)
    if data_dict["oxygen_drop_score"] is None:
        data_dict["oxygen_drop_score"] = max(0.0, 8.0 - data_dict["dissolved_oxygen"])
        
    # Combined water quality index proxy for inference
    data_dict["combined_water_quality_score"] = (data_dict["turbidity"] * data_dict["TDS"]) / (data_dict["dissolved_oxygen"] + 1e-5)
    
    df_input = pd.DataFrame([data_dict])
    result = predictor.predict_water_quality_risk(df_input)
    
    result["station_id"] = payload.station_id
    result["timestamp"] = datetime.datetime.now().isoformat()
    
    # Store trigger log if risk elevated
    if result["severity"] in ["WARNING", "CRITICAL"]:
        alerts_db.append({
            "timestamp": result["timestamp"],
            "station_id": payload.station_id,
            "severity": result["severity"],
            "probability": result["water_quality_risk_probability"],
            "trigger_values": {
                "pH": payload.pH,
                "turbidity": payload.turbidity,
                "TDS": payload.TDS
            }
        })
        
    return result

@app.get("/api/alerts")
def get_alerts():
    return alerts_db

if __name__ == "__main__":
    uvicorn.run("app:app", host="127.0.0.1", port=8006, reload=True)
