# Extreme Heat Data Audit Report

This report summarizes the data quality, missing values, outliers, and time resolution of the raw weather datasets.

## 3b01bcb8-0b14-4abf-b6f2-c1bfd384ba69.csv

- **Shape:** 3493 rows, 11 columns
- **Duplicate Rows:** 0

### Missing Values
- `pollutant_min`: 320 (9.16%)
- `pollutant_max`: 320 (9.16%)
- `pollutant_avg`: 320 (9.16%)

### Time Analysis
- **Time Column:** `last_update`
- **Start Time:** 2026-08-29 23:00:00
- **End Time:** 2026-08-29 23:00:00
- **Most Common Resolution:** 0 days 00:00:00
- **Duplicate Timestamps:** 2994

### Numeric Summary (Potential Outliers/Sentinels)
- **latitude**: min=8.5149093, max=34.147096, mean=23.36
- **longitude**: min=70.776774, max=94.636574, mean=78.48
- **pollutant_min**: min=0.0, max=255.0, mean=19.80
- **pollutant_max**: min=0.0, max=500.0, mean=46.64
- **pollutant_avg**: min=0.0, max=429.0, mean=29.84

---

## humid_tel_hr_cwprs_mh_2021_2025.csv

- **Shape:** 87990 rows, 20 columns
- **Duplicate Rows:** 0

### Missing Values
No missing values detected in any column.

### Time Analysis
- **Time Column:** `Data Acquisition Time`
- **Start Time:** 2024-05-11 00:00:00
- **End Time:** 2024-05-11 00:00:00
- **Most Common Resolution:** 0 days 00:05:00
- **Duplicate Timestamps:** 0

### Numeric Summary (Potential Outliers/Sentinels)
- **Telemetry Hourly Relative Humidity (%)**: min=0.0, max=101.0, mean=72.86

---

## rainfall_manual_hr_maharashtra_sw_mh_2021_2025.csv

- **Shape:** 170517 rows, 20 columns
- **Duplicate Rows:** 0

### Missing Values
No missing values detected in any column.

### Time Analysis
- **Time Column:** `Data Acquisition Time`
- **Start Time:** 2021-01-05 00:30:00
- **End Time:** 2021-01-05 00:30:00
- **Most Common Resolution:** 0 days 00:00:00
- **Duplicate Timestamps:** 0

### Numeric Summary (Potential Outliers/Sentinels)
- **Manual Hourly Rainfall (mm)**: min=-1000.0, max=90.0, mean=3.43

---

## solar_rediation_tel_hr_cwprs_mh_2021_2025.csv

- **Shape:** 87990 rows, 20 columns
- **Duplicate Rows:** 0

### Missing Values
No missing values detected in any column.

### Time Analysis
- **Time Column:** `Data Acquisition Time`
- **Start Time:** 2024-05-11 00:00:00
- **End Time:** 2024-05-11 00:00:00
- **Most Common Resolution:** 0 days 00:05:00
- **Duplicate Timestamps:** 0

### Numeric Summary (Potential Outliers/Sentinels)
- **Solar Radiation (Watt/m2)**: min=-11.0, max=1467.0, mean=191.95

---

## temprature_tel_hr_cwprs_mh_2021_2025.csv

- **Shape:** 87990 rows, 20 columns
- **Duplicate Rows:** 0

### Missing Values
No missing values detected in any column.

### Time Analysis
- **Time Column:** `Data Acquisition Time`
- **Start Time:** 2024-05-11 00:00:00
- **End Time:** 2024-05-11 00:00:00
- **Most Common Resolution:** 0 days 00:05:00
- **Duplicate Timestamps:** 0

### Numeric Summary (Potential Outliers/Sentinels)
- **Air Temperature Telemetry Hourly (ºC)**: min=-40.0, max=42.8, mean=25.22

---

## wind_speed_manual_twicedaily_maharashtra_sw_mh_1970_2025.csv

- **Shape:** 533384 rows, 20 columns
- **Duplicate Rows:** 0

### Missing Values
No missing values detected in any column.

### Time Analysis
- **Time Column:** `Data Acquisition Time`
- **Start Time:** 1998-01-01 08:30:00
- **End Time:** 1998-01-01 08:30:00
- **Most Common Resolution:** 0 days 00:00:00
- **Duplicate Timestamps:** 237400

### Numeric Summary (Potential Outliers/Sentinels)
- **Manual TwiceDaily Wind Speed (Km/Hr)**: min=0.0, max=167.0, mean=2.39

---

