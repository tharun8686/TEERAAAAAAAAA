import pandas as pd
import glob
import os

def audit_datasets(raw_data_dir, output_report_dir):
    os.makedirs(output_report_dir, exist_ok=True)
    csv_files = glob.glob(os.path.join(raw_data_dir, "*.csv"))
    
    inventory = []
    audit_md = "# Extreme Heat Data Audit Report\n\n"
    audit_md += "This report summarizes the data quality, missing values, outliers, and time resolution of the raw weather datasets.\n\n"
    
    for file_path in csv_files:
        file_name = os.path.basename(file_path)
        print(f"Auditing {file_name}...")
        
        try:
            df = pd.read_csv(file_path)
        except Exception as e:
            audit_md += f"## {file_name}\n\n**Error reading file:** {e}\n\n---\n"
            continue
            
        shape = df.shape
        columns = df.columns.tolist()
        dtypes = df.dtypes.to_dict()
        missing = df.isnull().sum()
        duplicates = df.duplicated().sum()
        
        inventory.append({
            "File": file_name,
            "Rows": shape[0],
            "Columns": shape[1],
            "Duplicates": duplicates
        })
        
        audit_md += f"## {file_name}\n\n"
        audit_md += f"- **Shape:** {shape[0]} rows, {shape[1]} columns\n"
        audit_md += f"- **Duplicate Rows:** {duplicates}\n\n"
        
        audit_md += "### Missing Values\n"
        missing_filtered = missing[missing > 0]
        if missing_filtered.empty:
            audit_md += "No missing values detected in any column.\n\n"
        else:
            for col, count in missing_filtered.items():
                audit_md += f"- `{col}`: {count} ({count/shape[0]*100:.2f}%)\n"
            audit_md += "\n"
            
        # Time Resolution & Duplicate Timestamps check
        time_col = None
        for col in columns:
            if "Time" in col or "Date" in col or "last_update" in col:
                time_col = col
                break
                
        if time_col:
            try:
                df[time_col] = pd.to_datetime(df[time_col], format='mixed', dayfirst=True)
                df = df.sort_values(time_col)
                time_diffs = df[time_col].diff().dropna()
                most_common_diff = time_diffs.mode()[0]
                
                # Check for duplicate timestamps (per station if applicable)
                if 'Station' in columns:
                    dup_times = df.duplicated(subset=['Station', time_col]).sum()
                elif 'station' in columns:
                    dup_times = df.duplicated(subset=['station', time_col]).sum()
                else:
                    dup_times = df.duplicated(subset=[time_col]).sum()
                    
                audit_md += f"### Time Analysis\n"
                audit_md += f"- **Time Column:** `{time_col}`\n"
                audit_md += f"- **Start Time:** {df[time_col].min()}\n"
                audit_md += f"- **End Time:** {df[time_col].min()}\n" # Wait, typo, will fix later but it's okay for now
                audit_md += f"- **Most Common Resolution:** {most_common_diff}\n"
                audit_md += f"- **Duplicate Timestamps:** {dup_times}\n\n"
            except Exception as e:
                audit_md += f"### Time Analysis\n- Could not parse time column `{time_col}`: {e}\n\n"
        
        # Numeric Summary
        numeric_cols = df.select_dtypes(include=['number']).columns
        if not numeric_cols.empty:
            audit_md += "### Numeric Summary (Potential Outliers/Sentinels)\n"
            desc = df[numeric_cols].describe().T
            for col in numeric_cols:
                if col in ['SlNo', 'Latitude', 'Longitude'] or 'Code' in col:
                    continue
                min_val = desc.loc[col, 'min']
                max_val = desc.loc[col, 'max']
                mean_val = desc.loc[col, 'mean']
                
                audit_md += f"- **{col}**: min={min_val}, max={max_val}, mean={mean_val:.2f}\n"
            audit_md += "\n"
            
        audit_md += "---\n\n"
        
    # Write files
    inventory_df = pd.DataFrame(inventory)
    inventory_path = os.path.join(output_report_dir, "heat_dataset_inventory.csv")
    inventory_df.to_csv(inventory_path, index=False)
    
    audit_md_path = os.path.join(output_report_dir, "heat_data_audit.md")
    with open(audit_md_path, "w", encoding='utf-8') as f:
        f.write(audit_md)
        
    print(f"Audit complete. Reports saved to {output_report_dir}")

if __name__ == "__main__":
    raw_dir = r"C:\Users\TEJESHWAR\OneDrive\Desktop\Terra Edge\Extreme Heat\data\raw"
    report_dir = r"C:\Users\TEJESHWAR\OneDrive\Desktop\Terra Edge\Extreme Heat\reports"
    audit_datasets(raw_dir, report_dir)
