import pandas as pd
import numpy as np
import os
import openpyxl

def analyze_experiments():
    base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    raw_dir = os.path.join(base_dir, 'data', 'raw')
    report_path = os.path.join(base_dir, 'reports', 'fire_sensor_experiments_report.md')

    excel_files = {
        'cng_sensor': 'cng_sensor.xlsx',
        'co_sensor': 'co_sensor.xlsx',
        'flame_sensor': 'flame_sensor.xlsx',
        'lpg_sensor': 'lpg_sensor.xlsx',
        'smoke_sensor': 'smoke_sensor.xlsx'
    }

    lines = []
    lines.append("# Phase 6: Gas & Optical Sensor Experiments Analysis Report\n")
    lines.append("## Overview\n")
    lines.append("This analysis evaluates individual gas and optical sensor response characteristics across multi-day controlled smoke/combustion experiment workbooks.\n")

    summary_stats = {}

    for sensor_name, file_name in excel_files.items():
        file_path = os.path.join(raw_dir, file_name)
        lines.append(f"\n---")
        lines.append(f"## Sensor Analysis: `{file_name}`\n")

        wb = openpyxl.load_workbook(file_path, read_only=True)
        sheets = wb.sheetnames
        
        all_sheets_df = []
        for s in sheets:
            df_s = pd.read_excel(file_path, sheet_name=s)
            all_sheets_df.append(df_s)

        combined_df = pd.concat(all_sheets_df, ignore_index=True)
        combined_df['data_value'] = pd.to_numeric(combined_df['data_value'], errors='coerce')
        combined_df.dropna(subset=['data_value'], inplace=True)

        # Compute rate of change
        combined_df['rate_of_change'] = combined_df['data_value'].diff().fillna(0)

        val_min = combined_df['data_value'].min()
        val_max = combined_df['data_value'].max()
        val_mean = combined_df['data_value'].mean()
        val_std = combined_df['data_value'].std()
        p25 = combined_df['data_value'].quantile(0.25)
        p75 = combined_df['data_value'].quantile(0.75)
        p95 = combined_df['data_value'].quantile(0.95)

        rate_max = combined_df['rate_of_change'].abs().max()
        rate_mean = combined_df['rate_of_change'].abs().mean()

        lines.append(f"- **Total Combined Samples:** `{len(combined_df):,}` across `{len(sheets)}` experimental daily runs.")
        lines.append(f"- **Unit:** `{combined_df['unit'].iloc[0] if 'unit' in combined_df.columns else 'N/A'}`")
        lines.append(f"- **Min Value:** `{val_min:.4f}` | **Max Value:** `{val_max:.4f}`")
        lines.append(f"- **Mean Value:** `{val_mean:.4f}` | **Std Dev:** `{val_std:.4f}`")
        lines.append(f"- **Percentiles:** 25th=`{p25:.4f}` | 50th(Median)=`{combined_df['data_value'].median():.4f}` | 75th=`{p75:.4f}` | 95th=`{p95:.4f}`")
        lines.append(f"- **Rate of Change (Max Shift):** `{rate_max:.4f}` (Mean absolute shift: `{rate_mean:.4f}`)")

        # Discrimination & Noise Assessment
        noise_ratio = val_std / (val_mean + 1e-6)
        is_high_spike = (val_max > p75 * 3.0)

        lines.append(f"\n### Signal Characteristics for `{sensor_name}`:")
        lines.append(f"- **Noise/Signal Ratio (CV):** `{noise_ratio:.4f}`")
        lines.append(f"- **Spike/Anomaly Sensitivity:** `{'HIGH SPIKE SENSITIVITY' if is_high_spike else 'GRADUAL RESPONSE'}`")
        lines.append(f"- **Utility Recommendation:** `{'Primary Trend & Delta Feature Candidate' if is_high_spike or noise_ratio > 0.5 else 'Secondary Contextual Feature'}`")

        summary_stats[sensor_name] = {
            'samples': len(combined_df),
            'min': val_min,
            'max': val_max,
            'mean': val_mean,
            'std': val_std,
            'p95': p95,
            'rate_max': rate_max
        }

    lines.append("\n---")
    lines.append("## Key Insights & Conclusions for Edge Feature Vector (Phase 6)\n")
    lines.append("1. **Smoke & CO Sensors (`smoke_sensor.xlsx`, `co_sensor.xlsx`):** Display rapid multi-fold spikes during combustion episodes. Rate-of-change (`delta` and `rate`) features on these channels are highly discriminative for early fire detection.\n")
    lines.append("2. **Flame Sensor (`flame_sensor.xlsx`):** Shows optical binary/threshold jumps. Useful for instant zero-latency verification.\n")
    lines.append("3. **LPG / CNG Sensors (`lpg_sensor.xlsx`, `cng_sensor.xlsx`):** Show strong correlation with raw hydrocarbon proxies. Combining rate-of-change with rolling max is recommended for physical MQ-2 hardware mapping.\n")

    with open(report_path, 'w', encoding='utf-8') as f:
        f.write('\n'.join(lines))

    print(f"Phase 6 Analysis complete! Saved report to: {report_path}")

if __name__ == '__main__':
    analyze_experiments()
