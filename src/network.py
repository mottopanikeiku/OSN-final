import numpy as np
import pandas as pd
import networkx as nx
import leidenalg
import igraph as ig
from sklearn.metrics.pairwise import cosine_similarity
from scipy.spatial.distance import cdist
from typing import Tuple, Dict, List
from .config import KNN_K, WEAK_BOUNDARY_THRESHOLD

class NetworkAnalyzer:
    """
    Handles graph construction, similarity computation, and community detection.
    """
    
    @staticmethod
    def compute_mahalanobis_similarity(X: np.ndarray) -> np.ndarray:
        """Computes similarity based on inverse Mahalanobis distance."""
        try:
            cov = np.cov(X.T)
            inv_cov = np.linalg.pinv(cov)
            dist = cdist(X, X, metric='mahalanobis', VI=inv_cov)
            # Convert distance to similarity (0 to 1 range approx)
            return 1 / (1 + dist)
        except Exception as e:
            print(f"Warning: Mahalanobis calculation failed ({e}). Defaulting to Cosine.")
            return cosine_similarity(X)

    @staticmethod
    def build_graph(X_pca: np.ndarray, df_indices: pd.Index) -> Tuple[nx.Graph, np.ndarray]:
        """
        Constructs a k-NN graph based on Cosine Similarity of PCA features.
        Returns the Graph object and the similarity matrix.
        """
        sim_matrix = cosine_similarity(X_pca)
        
        G = nx.Graph()
        # Add nodes
        for i in range(len(X_pca)):
            G.add_node(i, dataframe_index=df_indices[i])
            
        # Add Edges (k-NN)
        # For each node, find top k neighbors
        for i in range(len(X_pca)):
            # Argsort gives ascending, take last k+1 (excluding self)
            neighbors = np.argsort(sim_matrix[i])[-KNN_K-1:-1]
            for j in neighbors:
                weight = sim_matrix[i][j]
                if weight > 0:
                    G.add_edge(i, j, weight=weight)
                    
        return G, sim_matrix

    @staticmethod
    def detect_communities(G: nx.Graph) -> Tuple[Dict[int, int], Dict[int, int], float, float]:
        """
        Runs Louvain and Leiden algorithms.
        Returns dictionaries mapping node_id -> community_id for both, and their modularity scores.
        """
        # 1. Louvain
        louvain_coms = nx.community.louvain_communities(G, seed=42)
        louvain_map = {node: cid for cid, nodes in enumerate(louvain_coms) for node in nodes}
        mod_louvain = nx.community.modularity(G, louvain_coms)
        
        # 2. Leiden (requires igraph conversion)
        h = ig.Graph.from_networkx(G)
        leiden_part = leidenalg.find_partition(h, leidenalg.ModularityVertexPartition)
        leiden_map = {node: leiden_part.membership[i] for i, node in enumerate(G.nodes())}
        mod_leiden = leiden_part.modularity
        
        return louvain_map, leiden_map, mod_louvain, mod_leiden

    @staticmethod
    def find_weak_boundaries(G: nx.Graph, community_map: Dict[int, int]) -> List[Tuple[int, int, float]]:
        """
        Identifies edges that cross community boundaries but have high similarity weight.
        """
        weak_boundaries = []
        for u, v, data in G.edges(data=True):
            if community_map[u] != community_map[v]:
                if data.get('weight', 0) > WEAK_BOUNDARY_THRESHOLD:
                    weak_boundaries.append((u, v, data['weight']))
        return weak_boundaries
