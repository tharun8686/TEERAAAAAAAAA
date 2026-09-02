import os
import pandas as pd
import json

def generate_reports():
    print("Generating AirPollution Quality, Model Comparison & Edge Reports...")

    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    reports_dir = os.path.join(base_dir, 'reports')
    os.makedirs(reports_dir, exist_ok=True)

    # 1. Data Quality HTML Report
    qual_csv = os.path.join(reports_dir, 'data_quality_report.csv')
    df_qual = pd.read_csv(qual_csv) if os.path.exists(qual_csv) else pd.DataFrame()

    html_qual = f"""<!DOCTYPE html>
<html>
<head>
    <title>AirPollution Data Quality Report</title>
    <style>
        body {{ font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background: #0f1410; color: #f8f9fa; padding: 20px; }}
        h1 {{ color: #e67e22; }}
        table {{ border-collapse: collapse; width: 100%; margin-top: 20px; background: rgba(255,255,255,0.05); }}
        th, td {{ border: 1px solid rgba(255,255,255,0.1); padding: 12px; text-align: left; }}
        th {{ background: #d35400; color: white; }}
    </style>
</head>
<body>
    <h1>CPCB Air Quality Data Quality Report</h1>
    <p>Total Stations Analyzed: {len(df_qual)}</p>
    {df_qual.to_html(index=False)}
</body>
</html>
"""
    with open(os.path.join(reports_dir, 'data_quality_report.html'), 'w') as f:
        f.write(html_qual)

    # 2. Model Comparison HTML Report
    comp_csv = os.path.join(reports_dir, 'model_comparison.csv')
    df_comp = pd.read_csv(comp_csv) if os.path.exists(comp_csv) else pd.DataFrame()

    html_comp = f"""<!DOCTYPE html>
<html>
<head>
    <title>AirPollution Model Comparison Report</title>
    <style>
        body {{ font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background: #0f1410; color: #f8f9fa; padding: 20px; }}
        h1 {{ color: #e67e22; }}
        table {{ border-collapse: collapse; width: 100%; margin-top: 20px; background: rgba(255,255,255,0.05); }}
        th, td {{ border: 1px solid rgba(255,255,255,0.1); padding: 12px; text-align: left; }}
        th {{ background: #d35400; color: white; }}
    </style>
</head>
<body>
    <h1>Air Quality Deterioration Early Warning Model Comparison</h1>
    <p>Track A (Reference) vs Track B (Edge) Evaluation</p>
    {df_comp.to_html(index=False)}
</body>
</html>
"""
    with open(os.path.join(reports_dir, 'model_comparison.html'), 'w') as f:
        f.write(html_comp)

    print(f"Generated HTML Reports in: {reports_dir}")

if __name__ == '__main__':
    generate_reports()
