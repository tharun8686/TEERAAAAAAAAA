import pandas as pd
import numpy as np
import os
import glob

def audit_cleveland_dataset():
    base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    raw_dir = os.path.join(base_dir, 'data', 'raw')
    reports_dir = os.path.join(base_dir, 'reports')
    os.makedirs(reports_dir, exist_ok=True)

    desc_path = os.path.join(raw_dir, 'Cleveland_Corral_Sensor_Descriptions.csv')
    print(f"Reading Sensor Description Metadata: {desc_path}")
    df_desc = pd.read_csv(desc_path, skiprows=5)

    # Save Sensor Inventory CSV
    inventory_path = os.path.join(reports_dir, 'cleveland_sensor_inventory.csv')
    df_desc.to_csv(inventory_path, index=False)

    csv_files = glob.glob(os.path.join(raw_dir, '**', '*.csv'), recursive=True)
    file_records = []

    for fpath in csv_files:
        fname = os.path.basename(fpath)
        if fname.startswith('Cleveland_Corral_Sensor_Descriptions') or fname.startswith('wsn_'):
            continue

        # Extract station zone & water year
        zone = "middle" if "middle" in fpath else ("toe" if "toe" in fpath else "upper")
        
        try:
            # Metadata comments on first 3 lines
            df_curr = pd.read_csv(fpath, skiprows=3)
            row_cnt = len(df_curr)
            time_col = [c for c in df_curr.columns if 'date' in c.lower() or 'time' in c.lower()]
            start_t, end_t = "N/A", "N/A"
            if time_col:
                start_t = str(df_curr[time_col[0]].iloc[0])
                end_t = str(df_curr[time_col[0]].iloc[-1])

            cols = [c for c in df_curr.columns if c not in time_col]
            missing_pct = round(df_curr[cols].isnull().mean().mean() * 100, 2)

            file_records.append({
                'filename': fname,
                'zone': zone,
                'rows': row_cnt,
                'start_time': start_t,
                'end_time': end_t,
                'missing_pct': missing_pct,
                'sensors_count': len(cols)
            })
        except Exception as e:
            file_records.append({
                'filename': fname,
                'zone': zone,
                'rows': 0,
                'start_time': 'ERR',
                'end_time': 'ERR',
                'missing_pct': 100.0,
                'sensors_count': 0
            })

    df_files = pd.DataFrame(file_records)
    
    # Write Cleveland Audit Markdown Report
    report_path = os.path.join(reports_dir, 'cleveland_data_audit.md')
    lines = []
    lines.append("# Phase 1: USGS Cleveland Corral Landslide Dataset Audit Report\n")
    lines.append("## Executive Summary")
    lines.append(f"- **Total Monitoring Files:** `{len(df_files)}` CSV workbooks across 3 physical landslide zones.")
    lines.append("- **Landslide Monitoring Zones**:")
    lines.append(f"  - **Middle Station**: {len(df_files[df_files['zone']=='middle'])} files (WY1997 – WY2018)")
    lines.append(f"  - **Toe Station**: {len(df_files[df_files['zone']=='toe'])} files (WY1997 – WY2017)")
    lines.append(f"  - **Upper Station**: {len(df_files[df_files['zone']=='upper'])} files (WY1998 – WY1999)\n")

    lines.append("## Physical Sensor Parameters Available")
    lines.append("1. **Downslope Ground Displacement (cm)**: Extensometers (`mid_E1`, `mid_E2_A`, `mid_E2_B`, `toe_E3`, `toe_E4_A`, `toe_E5_A`, `toe_E5_B`, `toe_E5_C`).")
    lines.append("2. **Groundwater Pore Pressure / Head (cm)**: Piezometers (`mid_P1`, `mid_P2`, `mid_P3`, `toe_P7_A`, `toe_P8_A`, `toe_P9_A`).")
    lines.append("3. **Rainfall Accumulation (mm)**: Rain Gauge (`mid_R`, 15-minute intensity & cumulative).")
    lines.append("4. **Soil Water Content**: Volumetric soil moisture (`toe_M1_A`, `toe_M1_B`).\n")

    lines.append("## Sensor Quality & Continuity Audit (Metadata Notes)")
    lines.append("- **Sensor Replacements & Cable Breakages**: Metadata documents instrument destruction during major ground movement (e.g. `mid_E2_A` destroyed in 2002, replaced by `mid_E2_B`; `toe_E5_C` post toppled in 2017).")
    lines.append("- **Rule Uheld**: Sensor periods with suffixes `_A`, `_B`, `_C` must NOT be concatenated as fake continuous sensors. They will be processed as distinct operational deployments.\n")

    lines.append("## Hardware Mapping to Type-A Node")
    lines.append("| Physical Parameter | Cleveland USGS Sensor | Type-A Hardware Equivalent | Edge Deployment Status |")
    lines.append("| --- | --- | --- | --- |")
    lines.append("| Soil Water Content | `toe_M1_A/B` | Capacitive Soil Moisture | **Local Primary Input** |")
    lines.append("| Slope Displacement | Extensometers (`mid_E2_A`) | MPU6050 (Roll/Pitch/Tilt Rate) | **Local Deformation Proxy** |")
    lines.append("| Microseismic / Vibration | Geophone / Strain | SW-420 Vibration Sensor | **Local Anomaly Support** |")
    lines.append("| Ambient Weather | Weather station | DHT22 (Temp & Humidity) | **Local Weather Context** |")
    lines.append("| Atmospheric Pressure | Barometer | BMP280 Pressure | **Local Weather Context** |")
    lines.append("| Rainfall Accumulation | `mid_R` | External Rain Gauge / Weather API | **Optional External Context** |")
    lines.append("| Pore-Water Pressure | `mid_P1..P5` | *None* | **Research Precursor Only** |\n")

    with open(report_path, 'w', encoding='utf-8') as f:
        f.write('\n'.join(lines))

    print(f"Cleveland Audit Complete! Saved report to: {report_path}")

if __name__ == '__main__':
    audit_cleveland_dataset()
