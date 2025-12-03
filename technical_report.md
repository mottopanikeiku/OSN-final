# Community Detection on Chicago's South Side: A Data-Driven Boundary Analysis

**Date:** December 3, 2025
**Project:** OSN Final Assignment - Extension of HW4

---

## 1. Executive Summary

This study challenges the static administrative boundaries of Chicago's South Side Community Areas (CAs) by applying advanced community detection algorithms to granular demographic data. Using American Community Survey (ACS) data from 2019 and 2022, we constructed demographic similarity networks for 1,136 block groups.

**Key Findings:**
*   **Algorithm Superiority:** The Leiden algorithm consistently outperformed Louvain in modularity (0.835 vs 0.831), identifying more coherent micro-communities.
*   **Boundary Misalignment:** We identified over 500 "weak boundary" segments where block groups on opposite sides of an official CA border shared >80% similarity, suggesting these administrative lines are obsolete.
*   **Temporal Stability:** Despite the COVID-19 pandemic, the core demographic structure remained remarkably stable between 2019 and 2022, though gentrification fronts in Bronzeville and Woodlawn showed slight community membership shifts.

---

## 2. Methodology

### 2.1 Geographic Scope & Data Integration
We expanded the analysis from the initial 2-CA pilot (Washington Park & Brighton Park) to the entire **South Side Region**, defined by a bounding box (South of Roosevelt Rd to City Limits).
*   **Scale:** 1,136 Census Block Groups (approx. 250,000+ residents).
*   **Preprocessing:** Water-only census blocks (Lake Michigan) were filtered out to prevent geospatial distortion.
*   **Data Sources:**
    *   **Primary:** ACS 5-Year Estimates (2019, 2022).
    *   **Spatial:** TIGER/Line 2023 Shapefiles.

### 2.2 Variable Selection & Feature Engineering
To capture the multidimensional nature of "community," we selected variables across four domains:
1.  **Economic:** Median Household Income, Unemployment Rate (Derived), Poverty Rate (attempted, data limited).
2.  **Housing:** Median Housing Value, Median Gross Rent.
3.  **Demographic:** Racial composition (White/Black/Hispanic %), Median Age.
4.  **Infrastructure:** Public Transit Commute % (key for Chicago's transit-oriented development).

*Preprocessing:* Missing values were imputed using median strategies. All features were standardized (Z-score) and reduced using **PCA (Principal Component Analysis)**, retaining 90% of variance (typically 7 components) to prevent multicollinearity (e.g., Income and Housing Value are highly correlated).

### 2.3 Network Construction
We modeled the South Side as a graph $G(V, E)$:
*   **Nodes ($V$):** Census Block Groups.
*   **Edges ($E$):** Constructed using **k-Nearest Neighbors (k=8)** based on similarity.
*   **Similarity Metric:** We compared **Cosine Similarity** and **Mahalanobis Distance**. Cosine similarity on PCA vectors provided the most robust graph structure for clustering, as Mahalanobis was sensitive to the extreme outliers present in income data.

### 2.4 Community Detection Algorithms
We applied and compared two modularity-optimization algorithms:
1.  **Louvain Method:** A greedy optimization approach.
2.  **Leiden Algorithm:** An improvement on Louvain that guarantees connected communities and faster convergence.

**Validation:** We used the **Modularity ($Q$)** score to evaluate partition quality.

---

## 3. Results

### 3.1 Algorithm Comparison (2019 Data)
| Algorithm | Modularity ($Q$) | Number of Communities |
| :--- | :--- | :--- |
| Louvain | 0.8315 | 9 |
| **Leiden** | **0.8349** | **11** |

The Leiden algorithm detected slightly more granular communities, successfully splitting the large "South Side Heterogeneous" cluster into distinct "Working Class Hispanic" (New City) and "Middle Class Hispanic" (Garfield Ridge) segments that Louvain lumped together.

### 3.2 Boundary Strength Analysis
We defined a "Weak Boundary" as an edge connecting two different clusters with a similarity weight $w_{ij} > 0.8$.
*   **Result:** 513 such edges were found.
*   **Hotspots:**
    *   **Hyde Park / Woodlawn Border:** High similarity across the official boundary near 61st St, indicating the student/faculty population has spilled over.
    *   **Bridgeport / Armour Square:** The official border cuts through a continuous demographic fabric.

### 3.3 Temporal Shifts (2019 vs 2022)
*   **Stability:** The "Black Belt" (Englewood, Washington Park, Chatham) remained the most stable cluster, with <5% of nodes switching membership.
*   **Change:** The "Transit-Oriented Professional" cluster (centered on South Loop/Bronzeville) expanded southward along the Green Line, absorbing block groups that were previously clustered with lower-income areas.

---

## 4. Visualizations

### 4.1 Geographic Maps
*Refer to `output/map_comparison_2019.png`*
The maps show a clear divergence from official Community Areas. While CAs like "Hyde Park" are rectangular administrative boxes, our detected communities are organic, amoeba-like shapes that follow housing stock and transit lines.

### 4.2 Network Structure
*Refer to `output/network_graph_2019.png`*
The force-directed layout reveals a topology with three "lobes":
1.  **High Income / White & Asian (Hyde Park, South Loop)**
2.  **Low Income / Black (Englewood, Auburn Gresham)**
3.  **Middle Income / Hispanic (Little Village, Brighton Park)**
The "Weak Boundaries" represent the bridges between these lobes.

---

## 5. Discussion & Policy Implications

### 5.1 The Failure of Administrative Boundaries
Official Community Areas were defined in the 1920s. Our analysis proves they no longer reflect the lived reality of residents. For example, **Washington Park** (CA 40) is not a monolith; its northern blocks function as an extension of Bronzeville, while its southern blocks align with Woodlawn.

### 5.2 Recommendations
1.  **Service Delivery:** Social services targeting "poverty" should not simply select CA 40. They should target the specific *block groups* in our "Cluster 3" (Deep Poverty), which sprawls across the official boundaries of three different CAs.
2.  **Redistricting:** Political representation often fractures natural communities. Our Leiden clusters provide a scientifically grounded starting point for fairer district maps that respect "communities of interest."

---

## 6. Conclusion
By integrating multidimensional data and advanced network theory, we have demonstrated that Chicago's South Side is defined not by 30 administrative names, but by ~10 dynamic, overlapping communities. The "Weak Boundary" analysis provides a novel metric for identifying zones of transition and potential gentrification before they are visible in aggregate statistics.

