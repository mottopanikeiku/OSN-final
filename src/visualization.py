import os
import matplotlib.pyplot as plt
import networkx as nx
import geopandas as gpd
import pandas as pd
from typing import Dict
from .config import OUTPUT_DIR

class Visualizer:
    """
    Handles generation of static maps and network graphs.
    """
    
    @staticmethod
    def plot_community_maps(gdf: gpd.GeoDataFrame, year: int, mod_louvain: float, mod_leiden: float):
        """Generates side-by-side choropleth maps for Louvain vs Leiden."""
        
        # Filter out unassigned (-1) for cleaner plot
        plot_df = gdf[gdf['community_louvain'] != -1]
        
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(20, 12))
        
        # Louvain
        plot_df.plot(column='community_louvain', cmap='tab20', ax=ax1, legend=False)
        ax1.set_title(f"Louvain (Mod: {mod_louvain:.3f})")
        ax1.axis('off')
        ax1.set_aspect('equal')
        
        # Leiden
        plot_df.plot(column='community_leiden', cmap='tab20', ax=ax2, legend=False)
        ax2.set_title(f"Leiden (Mod: {mod_leiden:.3f})")
        ax2.axis('off')
        ax2.set_aspect('equal')
        
        plt.suptitle(f"Community Detection Results - {year}", fontsize=16)
        plt.tight_layout()
        
        save_path = os.path.join(OUTPUT_DIR, f"map_comparison_{year}.png")
        plt.savefig(save_path, dpi=300)
        plt.close()
        print(f"Saved map comparison to {save_path}")

    @staticmethod
    def plot_network_graph(G: nx.Graph, community_map: Dict[int, int], year: int, algorithm: str = "Leiden"):
        """Generates a force-directed network graph visualization."""
        plt.figure(figsize=(12, 12))
        
        # Layout
        pos = nx.spring_layout(G, k=0.15, iterations=20, seed=42)
        
        # Colors
        cmap = plt.get_cmap('tab20')
        node_colors = [cmap(community_map.get(n, 0) % 20) for n in G.nodes()]
        
        # Draw
        nx.draw_networkx_edges(G, pos, alpha=0.1, edge_color='gray')
        nx.draw_networkx_nodes(G, pos, node_size=20, node_color=node_colors)
        
        plt.title(f"Network Structure {year} ({algorithm})")
        plt.axis('off')
        
        save_path = os.path.join(OUTPUT_DIR, f"network_graph_{year}.png")
        plt.savefig(save_path, dpi=300)
        plt.close()
        print(f"Saved network graph to {save_path}")

