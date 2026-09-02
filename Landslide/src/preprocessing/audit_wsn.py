import pandas as pd
import numpy as np
import os

def audit_wsn_dataset():
    base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    raw_path = os.path.join(base_dir, 'data', 'raw', 'wsn_landslide_data.csv')
    reports_dir = os.path.join(base_dir, 'reports')
    os.makedirs(reports_dir, exist_ok=True)

    print(f"Loading WSN Landslide Dataset from: {raw_path}")
    df = pd.read_csv(raw_path)

    n_rows, n_cols = df.shape
    missing_sum = df.isnull().sum().sum()
    duplicate_rows = df.duplicated().sum()
    label_counts = df['Label'].value_counts().to_dict()

    # Feature Summary Statistics
    summary_rows = []
    for col in df.columns:
        dtype = str(df[col].dtype)
        null_cnt = df[col].isnull().sum()
        unique_cnt = df[col].nunique()
        c_min = df[col].min()
        c_max = df[col].max()
        c_mean = df[col].mean()
        c_std = df[col].std()

        summary_rows.append({
            'feature': col,
            'dtype': dtype,
            'null_count': null_cnt,
            'unique_values': unique_cnt,
            'min': round(float(c_min), 4),
            'max': round(float(c_max), 4),
            'mean': round(float(c_mean), 4),
            'std': round(float(c_std), 4)
        })

    df_summary = pd.DataFrame(summary_rows)
    summary_csv_path = os.path.join(reports_dir, 'wsn_feature_summary.csv')
    df_summary.to_csv(summary_csv_path, index=False)

    # Generate Markdown Report
    report_path = os.path.join(reports_dir, 'wsn_data_audit.md')
    lines = []
    lines.append("# Phase 1: WSN Landslide Dataset Audit Report\n")
    lines.append("## Dataset Overview")
    lines.append(f"- **Total Rows:** `{n_rows:,}`")
    lines.append(f"- **Total Columns:** `{n_cols}`")
    lines.append(f"- **Total Missing Values:** `{missing_sum}`")
    lines.append(f"- **Duplicate Rows:** `{duplicate_rows}`")
    lines.append(f"- **Target Column:** `Label`")
    lines.append(f"- **Label Balance:** Class 0 (`{label_counts.get(0, 0):,}`) | Class 1 (`{label_counts.get(1, 0):,}`)\n")

    lines.append("## Critical Audit Findings & Scope Restrictions")
    lines.append("1. **No Temporal / Event Identity**: `wsn_landslide_data.csv` lacks timestamps, node IDs, or event IDs. It represents a synthetic/i.i.d. feature distribution.")
    lines.append("2. **Supervised Baseline Role Only**: Suitable for Random Forest / XGBoost baseline feature importance and physical correlation analysis. **Cannot** be used to claim chronological lead-time or temporal early warning.")
    lines.append("3. **Post-Event & Static Feature Warning**: Contains static GIS features (`Elevation_m`, `Aspect`, `NDVI_Index`, `Land_Use_*`) and historical indicators (`Historical_Landslide_Count`) that are NOT available on a local Type-A sensor node.\n")

    lines.append("## Feature Group Classification")
    lines.append("- **Hydrological**: `Rainfall_mm`, `Rainfall_3Day`, `Rainfall_7Day`, `Soil_Saturation`, `Pore_Water_Pressure_kPa`, `Soil_Moisture_Content`")
    lines.append("- **Mechanical**: `Slope_Angle`, `Microseismic_Activity`, `Acoustic_Emission_dB`, `Soil_Strain`, `TDR_Reflection_Index`")
    lines.append("- **Weather**: `Temperature_C`, `Humidity_percent`, `Soil_Temperature_C`")
    lines.append("- **Terrain / Static**: `Elevation_m`, `Aspect`, `Vegetation_Cover`, `NDVI_Index`, `Proximity_to_Water`, `Distance_to_Road_m`")
    lines.append("- **Soil Physics**: `Soil_pH`, `Clay_Content`, `Sand_Content`, `Silt_Content`, `Soil_Type_*`")
    lines.append("- **Land Use & History**: `Land_Use_*`, `Earthquake_Activity`, `Historical_Landslide_Count`, `Soil_Erosion_Rate`\n")

    lines.append("## Summary Statistics Preview")
    lines.append("| Feature | Min | Max | Mean | Std | Nulls | Unique |")
    lines.append("| --- | --- | --- | --- | --- | --- | --- |")
    for r in summary_rows[:10]:
        lines.append(f"| `{r['feature']}` | `{r['min']}` | `{r['max']}` | `{r['mean']}` | `{r['std']}` | `{r['null_count']}` | `{r['unique_values']}` |")
    lines.append(f"\n*(Full 35-feature statistics saved to [`reports/wsn_feature_summary.csv`](file:///{summary_csv_path.replace(os.sep, '/')}))*")

    with open(report_path, 'w', encoding='utf-8') as f:
        f.write('\n'.join(lines))

    print(f"WSN Audit Complete! Saved report to: {report_path}")

if __name__ == '__main__':
    audit_wsn_dataset()
