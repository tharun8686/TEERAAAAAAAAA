import pandas as pd
import os

def main():
    # Define paths based on script location
    base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    raw_dir = os.path.join(base_dir, 'data', 'raw')
    intermediate_dir = os.path.join(base_dir, 'data', 'intermediate')

    floodevents_path = os.path.join(raw_dir, 'floodevents_indofloods.csv')
    precip_path = os.path.join(raw_dir, 'precipitation_variables_indofloods.csv')
    catchment_path = os.path.join(raw_dir, 'catchment_characteristics_indofloods.csv')
    output_path = os.path.join(intermediate_dir, 'indofloods_master.csv')

    # Load data
    print("Loading datasets...")
    floodevents_df = pd.read_csv(floodevents_path)
    precip_df = pd.read_csv(precip_path)
    catchment_df = pd.read_csv(catchment_path)

    print(f"Floodevents shape: {floodevents_df.shape}")
    print(f"Precipitation shape: {precip_df.shape}")
    print(f"Catchment characteristics shape: {catchment_df.shape}")

    # Merge precipitation
    print("Merging precipitation variables...")
    master_df = pd.merge(floodevents_df, precip_df, on='EventID', how='inner')
    print(f"After precipitation merge shape: {master_df.shape}")

    # Extract GaugeID from EventID
    # e.g., 'INDOFLOODS-gauge-1013-4' -> 'INDOFLOODS-gauge-1013'
    print("Extracting GaugeID...")
    master_df['GaugeID'] = master_df['EventID'].apply(lambda x: x.rsplit('-', 1)[0])

    # Merge catchment characteristics
    print("Merging catchment characteristics...")
    master_df = pd.merge(master_df, catchment_df, on='GaugeID', how='inner')
    print(f"Final master shape: {master_df.shape}")

    # Save to intermediate
    print(f"Saving to {output_path}...")
    master_df.to_csv(output_path, index=False)
    print("Done!")

if __name__ == "__main__":
    main()
