# Phase 6: Gas & Optical Sensor Experiments Analysis Report

## Overview

This analysis evaluates individual gas and optical sensor response characteristics across multi-day controlled smoke/combustion experiment workbooks.


---
## Sensor Analysis: `cng_sensor.xlsx`

- **Total Combined Samples:** `8,905` across `4` experimental daily runs.
- **Unit:** `ppm`
- **Min Value:** `5.1199` | **Max Value:** `2316.7780`
- **Mean Value:** `15.4885` | **Std Dev:** `33.5983`
- **Percentiles:** 25th=`11.6204` | 50th(Median)=`14.1387` | 75th=`17.4091` | 95th=`21.9630`
- **Rate of Change (Max Shift):** `2261.2122` (Mean absolute shift: `1.4517`)

### Signal Characteristics for `cng_sensor`:
- **Noise/Signal Ratio (CV):** `2.1692`
- **Spike/Anomaly Sensitivity:** `HIGH SPIKE SENSITIVITY`
- **Utility Recommendation:** `Primary Trend & Delta Feature Candidate`

---
## Sensor Analysis: `co_sensor.xlsx`

- **Total Combined Samples:** `8,891` across `4` experimental daily runs.
- **Unit:** `ppm`
- **Min Value:** `0.5448` | **Max Value:** `112.6995`
- **Mean Value:** `0.7982` | **Std Dev:** `1.2365`
- **Percentiles:** 25th=`0.6952` | 50th(Median)=`0.7811` | 75th=`0.8579` | 95th=`0.9372`
- **Rate of Change (Max Shift):** `95.4083` (Mean absolute shift: `0.0459`)

### Signal Characteristics for `co_sensor`:
- **Noise/Signal Ratio (CV):** `1.5491`
- **Spike/Anomaly Sensitivity:** `HIGH SPIKE SENSITIVITY`
- **Utility Recommendation:** `Primary Trend & Delta Feature Candidate`

---
## Sensor Analysis: `flame_sensor.xlsx`

- **Total Combined Samples:** `8,918` across `4` experimental daily runs.
- **Unit:** `raw values`
- **Min Value:** `0.2536` | **Max Value:** `4.7803`
- **Mean Value:** `0.5473` | **Std Dev:** `0.2423`
- **Percentiles:** 25th=`0.3864` | 50th(Median)=`0.4821` | 75th=`0.6457` | 95th=`0.9731`
- **Rate of Change (Max Shift):** `3.8438` (Mean absolute shift: `0.2002`)

### Signal Characteristics for `flame_sensor`:
- **Noise/Signal Ratio (CV):** `0.4427`
- **Spike/Anomaly Sensitivity:** `HIGH SPIKE SENSITIVITY`
- **Utility Recommendation:** `Primary Trend & Delta Feature Candidate`

---
## Sensor Analysis: `lpg_sensor.xlsx`

- **Total Combined Samples:** `8,904` across `4` experimental daily runs.
- **Unit:** `ppm`
- **Min Value:** `13.0447` | **Max Value:** `1158225.0000`
- **Mean Value:** `153.5895` | **Std Dev:** `12275.4136`
- **Percentiles:** 25th=`17.9618` | 50th(Median)=`20.5595` | 75th=`23.0225` | 95th=`24.8018`
- **Rate of Change (Max Shift):** `1157795.7217` (Mean absolute shift: `264.3467`)

### Signal Characteristics for `lpg_sensor`:
- **Noise/Signal Ratio (CV):** `79.9235`
- **Spike/Anomaly Sensitivity:** `HIGH SPIKE SENSITIVITY`
- **Utility Recommendation:** `Primary Trend & Delta Feature Candidate`

---
## Sensor Analysis: `smoke_sensor.xlsx`

- **Total Combined Samples:** `8,949` across `4` experimental daily runs.
- **Unit:** `ppm`
- **Min Value:** `9.9167` | **Max Value:** `1179.4200`
- **Mean Value:** `14.8604` | **Std Dev:** `17.3408`
- **Percentiles:** 25th=`12.9058` | 50th(Median)=`14.5357` | 75th=`16.1942` | 95th=`17.2396`
- **Rate of Change (Max Shift):** `1024.3842` (Mean absolute shift: `0.8726`)

### Signal Characteristics for `smoke_sensor`:
- **Noise/Signal Ratio (CV):** `1.1669`
- **Spike/Anomaly Sensitivity:** `HIGH SPIKE SENSITIVITY`
- **Utility Recommendation:** `Primary Trend & Delta Feature Candidate`

---
## Key Insights & Conclusions for Edge Feature Vector (Phase 6)

1. **Smoke & CO Sensors (`smoke_sensor.xlsx`, `co_sensor.xlsx`):** Display rapid multi-fold spikes during combustion episodes. Rate-of-change (`delta` and `rate`) features on these channels are highly discriminative for early fire detection.

2. **Flame Sensor (`flame_sensor.xlsx`):** Shows optical binary/threshold jumps. Useful for instant zero-latency verification.

3. **LPG / CNG Sensors (`lpg_sensor.xlsx`, `cng_sensor.xlsx`):** Show strong correlation with raw hydrocarbon proxies. Combining rate-of-change with rolling max is recommended for physical MQ-2 hardware mapping.
