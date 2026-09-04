# Toxic Flame & Chemical Plume Feature Engineering Report

## 1. Physical Mechanics & Differentiation from Wildfire
Industrial fires and chemical leaks exhibit distinct signatures compared to wildland forest fires:
- Wildfires produce predominantly biogenic smoldering smoke with slow thermal ramp rates ($VPD$ and foliage drought dependence).
- Toxic industrial flames produce rapid exothermic bursts, halogenated / solvent VOC spikes ($MQ$ resistance drops $>50\Omega/s$), and sudden co-occurring particulate plumes without vegetation drying precursors.

## 2. Engineered Telemetry Vectors
1. **Chemical Response Channels**:
   - `gas_response`: Analog voltage/resistance response from wideband metal-oxide sensor array ($\Omega \text{ or PPM}$).
   - `smoke_or_proxy_response`: Dual-channel reducing gas proxy.
   - `gas_rate`: Rapid rate of gas concentration rise ($\Delta Gas / \Delta t$).
2. **Aerosol & Atmospheric Indicators**:
   - `PM2.5` & `PM10`: Dense combustion soot loading.
   - `PM2.5_rate` & `PM10_rate`: Plume expansion speed.
   - `temperature_c`, `humidity`, `pressure`: Ambient dispersal atmospheric conditions.
3. **Plume Spikes & Persistence**:
   - `gas_spike_score` & `particulate_spike_score`: Ratio of short-term concentration to 1-hour rolling baseline.
   - `persistence_score`: Number of continuous observation intervals above trigger threshold.

## 3. Explicit Feature Order for Inference (17 Features)
```json
[
  "gas_response", "smoke_or_proxy_response", "PM2.5", "PM10",
  "temperature_c", "humidity", "pressure",
  "gas_rate", "PM2.5_rate", "PM10_rate",
  "rolling_mean_gas", "rolling_mean_PM2.5",
  "rolling_std_gas", "rolling_std_PM2.5",
  "gas_spike_score", "particulate_spike_score", "persistence_score"
]
```
