# Air Quality CAAQM Data Audit Report

## 1. Data Sources & Geographic Grid
- **Primary Data Provider**: Central Pollution Control Board (CPCB) India Continuous Ambient Air Quality Monitoring (CAAQM) stations.
- **Monitoring Stations**: Delhi ITO, Delhi IHBAS Dilshad Garden, Delhi PUSA DPCC, Mumbai Deonar IITM, Pune Bhosari, and Pune Shivajinagar.
- **Temporal Window**: Continuous 15-minute and 1-hour intervals spanning seasonal winter inversion, post-monsoon crop residue burning, and summer dust storm regimes.

## 2. Monitored Pollutants & Feature Distribution

| Feature Name | Sensor Principle | Physical Units | Nominal Range | Missing Rate (%) | Quality / Imputation |
|---|---|---|---|---|---|
| `pm25` | Dual-laser optical particle counter | $\mu g/m^3$ | 5.0 to 480.0 | 0.85% | Forward lag interpolation |
| `pm10` | Beta-attenuation / Laser optical | $\mu g/m^3$ | 10.0 to 750.0 | 1.10% | Spline imputation |
| `gas_proxy` | MQ-135 / Electrochemical cell ($NO_x$) | Proxy index | 5.0 to 180.0 | 0.45% | Median baseline imputation |
| `temperature` | RTD / SHT40 | °C | 12.0°C to 45.0°C | 0.15% | Linear interpolation |
| `relative_humidity` | Capacitive polymer probe | % RH | 18.0% to 98.0% | 0.15% | Physical bounds clip |
| `pressure` | Piezo-resistive barometer | hPa | 995.0 to 1025.0 | 0.10% | Standard lapse interpolation |

## 3. Data Cleaning & Sentinel Checks
- Sentinel negative values (CPCB sensor zero-calibration error flags: -99.0) removed and imputed.
- Unphysical ratios ($PM_{2.5} > PM_{10}$) corrected using physical particle conservation constraints.
