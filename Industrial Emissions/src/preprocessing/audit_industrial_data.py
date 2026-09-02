import pandas as pd
import os
import glob
import json

def audit_datasets(raw_dir, reports_dir):
    os.makedirs(reports_dir, exist_ok=True)
    inventory = []
    audit_md = "# Industrial Emissions Data Audit Report\n\n"
    
    # 1. India AQI
    aqi_path = os.path.join(raw_dir, "3b01bcb8-0b14-4abf-b6f2-c1bfd384ba69.csv")
    if os.path.exists(aqi_path):
        df_aqi = pd.read_csv(aqi_path)
        inventory.append({"Dataset": "India AQI baseline", "Rows": len(df_aqi), "Cols": len(df_aqi.columns), "Format": "CSV"})
        audit_md += f"## India AQI Baseline\n- **Rows:** {len(df_aqi)}\n- **Cols:** {len(df_aqi.columns)}\n- **Columns:** {df_aqi.columns.tolist()}\n- **Missing Values:**\n"
        missing = df_aqi.isnull().sum()
        for k, v in missing[missing > 0].items():
            audit_md += f"  - `{k}`: {v}\n"
        audit_md += "\n"
        
    # 2. MQ Gas Sensors Measurements
    mq_path = os.path.join(raw_dir, "Gas-Sensors-Measurements-Dataset-v1.0.0", "TakMashhido-Gas-Sensors-Measurements-Dataset-a4f36db", "Gas_Sensors_Measurements.csv")
    if os.path.exists(mq_path):
        df_mq = pd.read_csv(mq_path)
        inventory.append({"Dataset": "MQ Gas Sensor Measurements", "Rows": len(df_mq), "Cols": len(df_mq.columns), "Format": "CSV"})
        audit_md += f"## MQ-Series Gas Sensor Measurements\n- **Rows:** {len(df_mq)}\n- **Cols:** {len(df_mq.columns)}\n- **Columns:** {df_mq.columns.tolist()}\n- **Gas Distribution:**\n"
        gas_dist = df_mq['Gas'].value_counts()
        for k, v in gas_dist.items():
            audit_md += f"  - `{k}`: {v}\n"
        audit_md += "\n"
        
    # 3. Flow Modulation
    flow_path = os.path.join(raw_dir, "gas+sensor+array+under+flow+modulation", "features.csv")
    if os.path.exists(flow_path):
        df_flow = pd.read_csv(flow_path)
        inventory.append({"Dataset": "Flow Modulation Features", "Rows": len(df_flow), "Cols": len(df_flow.columns), "Format": "CSV"})
        audit_md += f"## Flow Modulation Features\n- **Rows:** {len(df_flow)}\n- **Cols:** {len(df_flow.columns)}\n- **Ethylene Conc Range:** {df_flow['eth_conc'].min()} to {df_flow['eth_conc'].max()}\n\n"

    # 4. UCI Gas Sensor Array Drift
    drift_dir = os.path.join(raw_dir, "gas+sensor+array+drift+dataset", "Dataset")
    if os.path.exists(drift_dir):
        dat_files = glob.glob(os.path.join(drift_dir, "*.dat"))
        inventory.append({"Dataset": "UCI Gas Sensor Array Drift", "Rows": len(dat_files), "Cols": 0, "Format": "LIBSVM (dat)"})
        audit_md += f"## UCI Gas Sensor Array Drift\n- Found {len(dat_files)} batch files (.dat in LIBSVM format).\n- Represents long-term drift robustness over 36 months.\n\n"

    # 5. Dynamic Mixtures
    dyn_dir = os.path.join(raw_dir, "gas+sensor+array+under+dynamic+gas+mixtures")
    if os.path.exists(dyn_dir):
        txt_files = glob.glob(os.path.join(dyn_dir, "*.txt"))
        inventory.append({"Dataset": "UCI Dynamic Gas Mixtures", "Rows": len(txt_files), "Cols": 0, "Format": "TXT"})
        audit_md += f"## UCI Dynamic Gas Mixtures\n- Found {len(txt_files)} massive time-series files (Ethylene/CO and Ethylene/Methane mixes).\n\n"
        
    # Save files
    pd.DataFrame(inventory).to_csv(os.path.join(reports_dir, "industrial_dataset_inventory.csv"), index=False)
    with open(os.path.join(reports_dir, "industrial_data_audit.md"), "w", encoding='utf-8') as f:
        f.write(audit_md)
    print("Audit completed successfully.")

if __name__ == "__main__":
    raw_dir = r"C:\Users\TEJESHWAR\OneDrive\Desktop\Terra Edge\Industrial Emissions\data\raw"
    reports_dir = r"C:\Users\TEJESHWAR\OneDrive\Desktop\Terra Edge\Industrial Emissions\reports"
    audit_datasets(raw_dir, reports_dir)
