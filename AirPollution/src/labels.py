import pandas as pd
import numpy as np

def generate_future_labels(df):
    print("Generating Future Targets (30m & 60m) & Deterioration Labels...")

    station_dfs = []

    for station_id, group in df.groupby('station_id'):
        group = group.copy()
        group.sort_values(by='timestamp', inplace=True)

        # Future PM2.5 30m average (shift -2 to -3 steps: t+30m to t+45m)
        pm25_30m = group['pm25'].shift(-2)
        pm25_45m = group['pm25'].shift(-3)
        group['future_pm25_30m'] = (pm25_30m + pm25_45m) / 2.0

        # Future PM2.5 60m average (shift -4 to -5 steps: t+60m to t+75m)
        pm25_60m = group['pm25'].shift(-4)
        pm25_75m = group['pm25'].shift(-5)
        group['future_pm25_60m'] = (pm25_60m + pm25_75m) / 2.0

        # Future PM10 30m average
        pm10_30m = group['pm10'].shift(-2)
        pm10_45m = group['pm10'].shift(-3)
        group['future_pm10_30m'] = (pm10_30m + pm10_45m) / 2.0

        # Deterioration Binary Label (ratio >= 1.15 AND min absolute increase >= 15 ug/m3)
        current_pm25 = group['pm25']
        
        det_30m = (group['future_pm25_30m'] >= current_pm25 * 1.15) & (group['future_pm25_30m'] - current_pm25 >= 15.0)
        group['pollution_deterioration_30m'] = det_30m.astype(int)

        det_60m = (group['future_pm25_60m'] >= current_pm25 * 1.15) & (group['future_pm25_60m'] - current_pm25 >= 15.0)
        group['pollution_deterioration_60m'] = det_60m.astype(int)

        # Future Severity Category based on future_pm25_60m
        def assign_severity(val):
            if pd.isnull(val):
                return 'NORMAL'
            if val <= 60.0:
                return 'NORMAL'
            elif val <= 120.0:
                return 'WATCH'
            elif val <= 250.0:
                return 'WARNING'
            else:
                return 'CRITICAL'

        group['severity_60m'] = group['future_pm25_60m'].apply(assign_severity)

        station_dfs.append(group)

    master_labeled = pd.concat(station_dfs, ignore_index=True)
    
    # Drop rows where future labels are missing (end of time series)
    valid_labeled = master_labeled.dropna(subset=['future_pm25_30m', 'future_pm25_60m']).reset_index(drop=True)
    
    det_cnt = valid_labeled['pollution_deterioration_60m'].sum()
    print(f"Label Generation Complete! Valid samples: {len(valid_labeled):,} | Deterioration 60m Events: {det_cnt:,} ({det_cnt/len(valid_labeled)*100:.2f}%)")
    return valid_labeled
