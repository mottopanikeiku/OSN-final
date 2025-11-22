import pandas as pd
import numpy as np
import os
from sklearn.preprocessing import StandardScaler
from sklearn.metrics.pairwise import cosine_similarity
import networkx as nx
from utils import ACS_VARIABLES

# --------------------
# Setup
# --------------------
DATA_DIR = "data"
OUTPUT_DIR = "output"
os.makedirs(OUTPUT_DIR, exist_ok=True)

def process_year(year):
    print(f"Processing data for {year}...")
    
    # Load ACS Data
    acs_path = os.path.join(DATA_DIR, f"acs_{year}_cook_blockgroups.csv")
    if not os.path.exists(acs_path):
        # Fallback to 2022 if 2023 requested but not found (handled in download script)
        if year == 2023:
             acs_path = os.path.join(DATA_DIR, "acs_2022_cook_blockgroups.csv")
        if not os.path.exists(acs_path):
            print(f"File not found: {acs_path}")
            return

    df = pd.read_csv(acs_path)
    
    # Load Mapping
    mapping_path = os.path.join(DATA_DIR, "bg_to_ca_mapping.csv")
    if not os.path.exists(mapping_path):
        print("Mapping file not found. Run 01_download_data.py first.")
        return
    
    mapping = pd.read_csv(mapping_path)
    
    # Filter ACS data to South Side BGs
    # Ensure GEOID types match (string)
    df['GEOID'] = df['GEOID'].astype(str)
    mapping['GEOID'] = mapping['GEOID'].astype(str)
    
    merged = pd.merge(mapping, df, on='GEOID', how='inner')
    
    print(f"Matched {len(merged)} block groups for {year}.")
    
    # Feature Engineering & Cleaning
    # 1. Calculate Percentages where appropriate
    # Poverty Rate = poverty_count / total_population
    if 'poverty_count' in merged.columns and 'total_population' in merged.columns:
        merged['poverty_rate'] = merged['poverty_count'] / merged['total_population']
        merged['poverty_rate'] = merged['poverty_rate'].fillna(0) # Handle div by zero

    # Education Rates
    if 'edu_hs_diploma' in merged.columns and 'total_population' in merged.columns: # simplified denom
         merged['hs_rate'] = merged['edu_hs_diploma'] / merged['total_population'] # Roughly
    
    # Select features for clustering
    # Using the ones defined in utils, plus derived ones
    # We need to handle raw counts vs rates. Usually rates are better for similarity.
    # For this template, I'll just select the raw columns mapped in utils, but a real analysis should normalize by population.
    
    feature_cols = list(ACS_VARIABLES.values())
    
    # Drop rows with missing values in critical columns
    data_clean = merged.dropna(subset=feature_cols)
    
    # Normalization
    scaler = StandardScaler()
    X = scaler.fit_transform(data_clean[feature_cols])
    
    # Compute Similarity (Cosine)
    sim_matrix = cosine_similarity(X)
    
    # Save processed data and similarity matrix
    data_clean.to_csv(os.path.join(OUTPUT_DIR, f"processed_data_{year}.csv"), index=False)
    np.save(os.path.join(OUTPUT_DIR, f"similarity_matrix_{year}.npy"), sim_matrix)
    
    print(f"Saved processed data and similarity matrix for {year}.")

if __name__ == "__main__":
    process_year(2019)
    process_year(2023) # Or 2022

