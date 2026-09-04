# Water Quality Edge Feasibility & Hardware Tier Report

## 1. Physical Hardware vs Full Chemistry Duality
There is an intentional duality in the Water Quality module:
- **Current Prototype Hardware Shell**: Minimalist sensing unit utilizing a Water Level Float Sensor + DHT22 ambient probe.
- **Full Data-Driven ML Model**: 26-feature physicochemical water quality prediction engine trained on CWC & WHO chemistry records (pH, Turbidity, EC, TDS, Dissolved Oxygen).

## 2. Confidence Graceful Degradation Protocol
When the physical hardware shell is deployed without glass pH electrodes or optical nephelometric turbidity probes:
1. Missing chemistry parameters are imputed with baseline environmental equilibrium values ($pH = 7.0, Turbidity = 5.0, TDS = 350.0$).
2. Confidence score is automatically penalized:
   - Missing pH: $-0.35$
   - Missing Turbidity: $-0.35$
   - Missing Dissolved Oxygen: $-0.15$
   - Minimum bound: $0.30$
3. The system warns operators that physical chemistry probes are unavailable while safely continuing telemetry operations without application crashes.
