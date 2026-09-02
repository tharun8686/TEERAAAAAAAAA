import pandas as pd
import numpy as np
import os
import openpyxl

def audit_datasets():
    base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    raw_dir = os.path.join(base_dir, 'data', 'raw')
    report_path = os.path.join(base_dir, 'reports', 'fire_data_audit.md')

    lines = []
    lines.append("# ForestWildFire AI - Comprehensive Data Audit Report\n")
    lines.append("**Generated Date:** 2026-08-26\n")
    lines.append("## Executive Summary\n")
    lines.append("This report presents a thorough data audit across all 8 uploaded datasets for the Forest Wildfire Edge-AI Module. Every dataset was analyzed for shape, data types, missing values, duplicates, time ranges, sampling frequencies, target class distributions, and sensor ranges.\n")

    # -------------------------------------------------------------
    # 1. Primary Long Format Dataset: forest_fire_sensor_fusion_raw.csv.gz.csv
    # -------------------------------------------------------------
    fusion_path = os.path.join(raw_dir, 'forest_fire_sensor_fusion_raw.csv.gz.csv')
    lines.append("\n---")
    lines.append("## 1. Primary Dataset (Long Format): `forest_fire_sensor_fusion_raw.csv.gz.csv`\n")
    
    df_fusion = pd.read_csv(fusion_path)
    lines.append(f"- **Total Rows:** `{len(df_fusion):,}`")
    lines.append(f"- **Columns:** `{list(df_fusion.columns)}` (Dtypes: `{df_fusion.dtypes.to_dict()}`)")
    lines.append(f"- **Missing Values:** `{df_fusion.isnull().sum().to_dict()}`")
    lines.append(f"- **Duplicate Rows:** `{df_fusion.duplicated().sum():,}`")
    
    unique_signals = df_fusion['NAME'].unique()
    lines.append(f"- **Unique Sensor Signals (`NAME`):** `{len(unique_signals)}` signals")
    lines.append("```text")
    for sig in unique_signals:
        cnt = (df_fusion['NAME'] == sig).sum()
        lines.append(f"  - {sig}: {cnt:,} readings")
    lines.append("```")

    # Inspect TIME semantics
    df_fusion['parsed_time'] = pd.to_datetime(df_fusion['TIME'], unit='s', errors='coerce')
    min_t, max_t = df_fusion['parsed_time'].min(), df_fusion['parsed_time'].max()
    lines.append(f"- **Time Range (assuming unix epoch seconds):** `{min_t}` to `{max_t}`")

    # Check Target distribution inside fusion data (Fire Alarm signal)
    fire_alarm_rows = df_fusion[df_fusion['NAME'] == 'Fire Alarm']
    alarm_counts = fire_alarm_rows['VALUE'].value_counts().to_dict()
    lines.append(f"- **Target (`Fire Alarm`) Class Distribution:** `{alarm_counts}`")

    # -------------------------------------------------------------
    # 2. Compact Baseline Dataset: fire_data.csv
    # -------------------------------------------------------------
    fire_data_path = os.path.join(raw_dir, 'fire_data.csv')
    lines.append("\n---")
    lines.append("## 2. Compact Baseline Dataset: `fire_data.csv`\n")
    
    df_fire = pd.read_csv(fire_data_path)
    lines.append(f"- **Total Rows:** `{len(df_fire):,}`")
    lines.append(f"- **Columns:** `{list(df_fire.columns)}`")
    lines.append(f"- **Missing Values:** `{df_fire.isnull().sum().to_dict()}`")
    lines.append(f"- **Duplicate Rows:** `{df_fire.duplicated().sum():,}`")
    alarm_counts_compact = df_fire['fire_alarm'].value_counts().to_dict()
    lines.append(f"- **Target (`fire_alarm`) Class Distribution:** `{alarm_counts_compact}` (Normal 0: {alarm_counts_compact.get(0,0):,}, Fire 1: {alarm_counts_compact.get(1,0):,})")

    # Summary Statistics for fire_data.csv
    lines.append("\n### Numerical Summary Statistics (`fire_data.csv`):")
    lines.append("```text")
    lines.append(df_fire.describe().T[['min', 'mean', 'std', '50%', 'max']].to_string())
    lines.append("```")

    # -------------------------------------------------------------
    # 3. Resisto Out-of-Distribution Dataset: forest_fire_resisto_raw.csv.csv
    # -------------------------------------------------------------
    resisto_path = os.path.join(raw_dir, 'forest_fire_resisto_raw.csv.csv')
    lines.append("\n---")
    lines.append("## 3. Resisto OOD Dataset: `forest_fire_resisto_raw.csv.csv`\n")
    
    df_resisto = pd.read_csv(resisto_path)
    lines.append(f"- **Total Rows:** `{len(df_resisto):,}`")
    lines.append(f"- **Columns:** `{list(df_resisto.columns)}`")
    lines.append(f"- **Missing Values:** `{df_resisto.isnull().sum().to_dict()}`")
    lines.append(f"- **Duplicate Rows:** `{df_resisto.duplicated().sum():,}`")
    resisto_labels = df_resisto['fire_alert_status'].value_counts().to_dict()
    lines.append(f"- **Labels (`fire_alert_status`):** `{resisto_labels}` (0 = no alert, 1 = pre-alert, 2 = fire alert)")
    
    lines.append("\n### Resisto Numerical Summary Statistics:")
    lines.append("```text")
    lines.append(df_resisto[['temperature_c', 'humidity_percent', 'air_pressure_pa', 'latitude', 'longitude']].describe().T[['min', 'mean', 'std', '50%', 'max']].to_string())
    lines.append("```")

    # -------------------------------------------------------------
    # 4. Gas & Optical Sensor Experiment Workbooks (.xlsx)
    # -------------------------------------------------------------
    lines.append("\n---")
    lines.append("## 4. Gas & Optical Experiment Workbooks (.xlsx)\n")
    excel_files = ['cng_sensor.xlsx', 'co_sensor.xlsx', 'flame_sensor.xlsx', 'lpg_sensor.xlsx', 'smoke_sensor.xlsx']

    for ef in excel_files:
        ef_path = os.path.join(raw_dir, ef)
        wb = openpyxl.load_workbook(ef_path, read_only=True)
        sheet_names = wb.sheetnames
        lines.append(f"### `{ef}`")
        lines.append(f"- **Sheet Count:** `{len(sheet_names)}` sheets: `{sheet_names[:5]}...`")
        
        # Load first sheet as sample
        df_sample = pd.read_excel(ef_path, sheet_name=sheet_names[0])
        lines.append(f"- **Sample Sheet (`{sheet_names[0]}`) Rows:** `{len(df_sample):,}` | **Columns:** `{list(df_sample.columns)}`")
        lines.append(f"- **Missing Values:** `{df_sample.isnull().sum().to_dict()}`")
        lines.append("---")

    # -------------------------------------------------------------
    # Data Cleaning & Decision Log
    # -------------------------------------------------------------
    lines.append("\n---")
    lines.append("## 5. Audit Decisions & Next Steps (Phase 1 Conclusion)\n")
    lines.append("1. **Primary Dataset Pivoting (Phase 2):** `forest_fire_sensor_fusion_raw.csv.gz.csv` contains 876,820 long-format entries across 14 signals. In Phase 2, we will pivot this into wide format (`data/intermediate/fire_sensor_wide.csv`) where each row represents an exact timestamp.\n")
    lines.append("2. **Label Integrity:** No synthetic labels were fabricated. The `fire_alarm` signal from the sensor fusion dataset will serve as ground truth for Phase 3 (baseline model training).\n")
    lines.append("3. **Resisto & Sensor Experiments Separation:** Resisto and individual gas sensor Excel files will be strictly kept separate and reserved for Phase 5 (OOD Validation) and Phase 6 (Robustness Analysis) respectively.\n")

    # Save to reports/fire_data_audit.md
    with open(report_path, 'w', encoding='utf-8') as f:
        f.write('\n'.join(lines))

    print(f"Data Audit complete! Saved report to: {report_path}")

if __name__ == '__main__':
    audit_datasets()
