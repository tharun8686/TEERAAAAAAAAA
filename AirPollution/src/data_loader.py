import pandas as pd
import numpy as np
import os
import glob
import re
from schema import COLUMN_MAPPING, STANDARDIZED_COLUMNS

def clean_col_name(c):
    c_clean = str(c).strip().lower()
    c_clean = re.sub(r'[^\w\s\(\)/.-]', '', c_clean)
    return c_clean

def map_column(c):
    c_clean = str(c).encode('ascii', 'ignore').decode('ascii').lower().strip()
    if c_clean in ['station id', 'station_id', '_id']: return 'station_id'
    if c_clean in ['state']: return 'state'
    if c_clean in ['city']: return 'city'
    if c_clean in ['station name', 'station_name', 'station']: return 'station_name'
    if c_clean in ['timestamp', 'last_update', 'date']: return 'timestamp'

    if 'pm2.5' in c_clean or 'pm25' in c_clean: return 'pm25'
    if 'pm10' in c_clean: return 'pm10'
    if 'no2' in c_clean: return 'no2'
    if 'nox' in c_clean: return 'nox'
    if 'nh3' in c_clean: return 'nh3'
    if 'so2' in c_clean: return 'so2'
    if 'co' in c_clean: return 'co'
    if 'ozone' in c_clean or 'o3' in c_clean: return 'o3'
    if 'no' in c_clean and 'nox' not in c_clean and 'no2' not in c_clean: return 'no'
    if 'benzene' in c_clean and 'eth' not in c_clean: return 'benzene'
    if 'toluene' in c_clean: return 'toluene'
    if 'xylene' in c_clean and 'o x' not in c_clean and 'mp' not in c_clean: return 'xylene'
    if 'o xylene' in c_clean: return 'o_xylene'
    if 'eth' in c_clean and 'benzene' in c_clean: return 'eth_benzene'
    if 'mp' in c_clean and 'xylene' in c_clean: return 'mp_xylene'
    if re.search(r'\bat\b', c_clean) or 'temp' in c_clean: return 'temperature'
    if 'rh' in c_clean or 'humid' in c_clean: return 'relative_humidity'
    if 'vws' in c_clean: return 'vertical_wind_speed'
    if 'ws' in c_clean and 'vws' not in c_clean: return 'wind_speed'
    if 'wd' in c_clean: return 'wind_direction'
    if 'tot-rf' in c_clean: return 'total_rainfall'
    if 'rf' in c_clean: return 'rainfall'
    if 'sr' in c_clean or 'solar' in c_clean: return 'solar_radiation'
    if 'bp' in c_clean or 'press' in c_clean: return 'pressure'
    return c_clean

def load_and_standardize_csv(file_path):
    print(f"Loading CSV: {os.path.basename(file_path)}")
    df = pd.read_csv(file_path, low_memory=False)
    
    # Standardize column headers
    df.columns = [map_column(c) for c in df.columns]

    # Clean up station_id and station_name
    fname = os.path.basename(file_path).lower()
    if 'station_name' not in df.columns or df['station_name'].isnull().all():
        if 'ihbas' in fname:
            df['station_name'] = 'Delhi IHBAS'
        elif 'pusa' in fname:
            df['station_name'] = 'Delhi Pusa'
        elif 'deonar' in fname:
            df['station_name'] = 'Mumbai Deonar'
        elif 'bhosari' in fname:
            df['station_name'] = 'Pune Bhosari'
        elif 'shivajinagar' in fname or 'revenue' in fname:
            df['station_name'] = 'Pune Shivajinagar'
        else:
            df['station_name'] = 'Delhi ITO'

    df['station_name'] = df['station_name'].fillna('Delhi ITO').astype(str)
    df['station_id'] = df['station_name'].apply(lambda s: s.replace(' ', '_').replace(',', '').lower())

    # Ensure all standardized columns exist
    for c in STANDARDIZED_COLUMNS:
        if c not in df.columns:
            df[c] = np.nan

    df = df.loc[:, ~df.columns.duplicated()]
    return df[STANDARDIZED_COLUMNS]

def load_all_stations():
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    raw_dir = os.path.join(base_dir, 'data', 'raw')
    csv_files = glob.glob(os.path.join(raw_dir, '*.csv'))

    dfs = []
    for f in sorted(csv_files):
        df_std = load_and_standardize_csv(f)
        dfs.append(df_std)

    master_df = pd.concat(dfs, ignore_index=True)
    print(f"Master Ingested Dataset: {master_df.shape[0]:,} rows across {master_df['station_name'].nunique()} CPCB stations.")
    return master_df

if __name__ == '__main__':
    load_all_stations()
