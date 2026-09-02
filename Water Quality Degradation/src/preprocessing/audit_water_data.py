import pandas as pd
import os
import glob

def audit_datasets(raw_dir, reports_dir):
    os.makedirs(reports_dir, exist_ok=True)
    inventory = []
    audit_md = "# Water Quality Degradation Data Audit Report\n\n"
    
    # Files
    files_map = {
        "a8b02547-0b97-4775-a0ce-3bc7f2c86fd6.csv": "Surface Water Physical Parameters",
        "swq_manual_chemical_parameters_cwc_ap_1961_2020.csv": "Surface Water Chemical Parameters",
        "gwq_physical_parameter_manual_cgwb_ap_1961_2025.csv": "Groundwater Physical Parameters",
        "gwq_chemical_parameter_manual_cgwb_ap_1961_2025.csv": "Groundwater Chemical Parameters"
    }
    
    for filename, label in files_map.items():
        filepath = os.path.join(raw_dir, filename)
        if os.path.exists(filepath):
            print(f"Auditing {label}...")
            # Use encoding='utf-8' to handle micro sign in groundwater chemistry
            df = pd.read_csv(filepath, encoding='utf-8', nrows=5000) # read sample for audit details
            num_rows = sum(1 for _ in open(filepath, encoding='utf-8')) - 1
            
            inventory.append({
                "Dataset": label,
                "Filename": filename,
                "Rows": num_rows,
                "Cols": len(df.columns),
                "Format": "CSV"
            })
            
            audit_md += f"## {label} ({filename})\n"
            audit_md += f"- **Rows:** {num_rows}\n"
            audit_md += f"- **Cols:** {len(df.columns)}\n"
            audit_md += f"- **Columns:** {df.columns.tolist()[:15]}... (truncated)\n"
            
            # Detect missing value counts
            missing = df.isnull().sum()
            high_missing = missing[missing > 0].sort_values(ascending=False)
            if not high_missing.empty:
                audit_md += "- **Top Missing Fields (Sample of 5000):**\n"
                for col, val in high_missing.items():
                    audit_md += f"  - `{col}`: {val} missing\n"
            audit_md += "\n"
            
    pd.DataFrame(inventory).to_csv(os.path.join(reports_dir, "water_dataset_inventory.csv"), index=False)
    
    with open(os.path.join(reports_dir, "water_data_audit.md"), "w", encoding='utf-8') as f:
        f.write(audit_md)
        
    print("Water Quality Data Audit complete.")

if __name__ == "__main__":
    raw_dir = r"C:\Users\TEJESHWAR\OneDrive\Desktop\Terra Edge\Water Quality Degradation\data\raw"
    reports_dir = r"C:\Users\TEJESHWAR\OneDrive\Desktop\Terra Edge\Water Quality Degradation\reports"
    audit_datasets(raw_dir, reports_dir)
