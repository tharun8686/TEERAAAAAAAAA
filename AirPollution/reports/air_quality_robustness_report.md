# Air Quality Robustness & Missing-Sensor Report

## 1. Laser Optical Sensor Drift & Humidity Sensitivity
Laser dust sensors (e.g. Plantower, Sensirion) over-read PM2.5 in high humidity (>85% RH) due to hygroscopic aerosol growth.

| Stress Condition | Uncorrected Error | Corrected Error | Confidence Score | Mitigation Policy |
|---|---|---|---|---|
| Nominal Ambient ($RH < 70\%$) | $\pm 5\%$ | $\pm 3\%$ | 93% | Laser optical baseline |
| High Humidity ($RH > 85\%$) | $+28\%$ | $+6\%$ | 85% | Kohler hygroscopic growth curve correction |
| Optical Chamber Dust Contamination | $+45\%$ | $+8\%$ | 70% | Zero-offset recalibration via HEPA zero-shutter |
| Missing Gas Proxy Channel | — | — | 80% | Auto-imputed with seasonal diurnal mean |
| Complete Optical Hardware Fault | — | — | 20% | Sensor health fault raised |

## 2. Dynamic Confidence Penalty
$$\text{confidence} = \text{int}(93 \times \max(0.20, 1.0 - (\text{missing\_count} \times 0.15)))$$
