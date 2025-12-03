import os
import pandas as pd
from src.config import ACS_YEARS, OUTPUT_DIR
from src.data_loader import DataLoader
from src.features import FeatureEngineer
from src.network import NetworkAnalyzer
from src.visualization import Visualizer

def run_pipeline(year: int):
    print(f"\n{'='*30}\nStarting Pipeline for {year}\n{'='*30}")
    
    # 1. Load Data
    gdf = DataLoader.load_merged_data(year)
    if gdf is None:
        print(f"Skipping {year} due to missing data.")
        return

    # 2. Feature Engineering
    # Calculate derived rates
    gdf = FeatureEngineer.calculate_rates(gdf)
    # Prepare matrix (Impute, Scale, PCA)
    X_pca, valid_features = FeatureEngineer.prepare_features(gdf)
    
    # 3. Network Analysis
    print("Constructing Network Graph...")
    G, _ = NetworkAnalyzer.build_graph(X_pca, gdf.index)
    
    print("Detecting Communities...")
    louvain_map, leiden_map, mod_louvain, mod_leiden = NetworkAnalyzer.detect_communities(G)
    print(f"Modularity -> Louvain: {mod_louvain:.4f} | Leiden: {mod_leiden:.4f}")
    
    # 4. Boundary Analysis
    weak_boundaries = NetworkAnalyzer.find_weak_boundaries(G, leiden_map)
    print(f"Identified {len(weak_boundaries)} weak boundary segments.")
    
    # 5. Save Results
    # Assign community IDs back to GeoDataFrame
    # Map graph node indices (0..N) back to DataFrame rows
    # Note: G nodes are integers 0..N corresponding to X_pca rows
    gdf['community_louvain'] = [louvain_map.get(i, -1) for i in range(len(gdf))]
    gdf['community_leiden'] = [leiden_map.get(i, -1) for i in range(len(gdf))]
    
    results_path = os.path.join(OUTPUT_DIR, f"results_{year}.csv")
    save_cols = ['GEOID', 'community_louvain', 'community_leiden'] + valid_features
    gdf[save_cols].to_csv(results_path, index=False)
    print(f"Saved tabular results to {results_path}")
    
    # 6. Visualization
    print("Generating visualizations...")
    Visualizer.plot_community_maps(gdf, year, mod_louvain, mod_leiden)
    Visualizer.plot_network_graph(G, leiden_map, year, algorithm="Leiden")

def main():
    for year in ACS_YEARS:
        run_pipeline(year)
    print("\nPipeline Completed Successfully.")

if __name__ == "__main__":
    main()

