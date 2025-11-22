# Chicago South Side Community Detection

This project aims to identify natural neighborhood boundaries within Chicago's South Side by analyzing demographic similarity patterns across multiple Community Areas (CAs) and comparing them to official administrative boundaries.

## Project Structure

The codebase is modularized to separate data acquisition, processing, and visualization, allowing for parallel development.

### Files & Modules

*   **`utils.py`**:
    *   **Purpose:** Defines shared constants and configuration.
    *   **Content:**
        *   `SOUTH_SIDE_CAS`: List of IDs for the relevant Community Areas.
        *   `ACS_VARIABLES`: Dictionary mapping ACS variable codes (e.g., `B19013_001E`) to human-readable names (e.g., `median_household_income`).
    *   **Status:** *Drafted.* Needs confirmation that variables match research goals.

*   **`01_download_data.py`**:
    *   **Purpose:** Fetches raw data from external sources.
    *   **Actions:**
        1.  Downloads ACS 5-year estimates (aiming for 2019 & 2023) via `censusdata`.
        2.  Downloads Chicago Community Area boundaries (GeoJSON).
        3.  Downloads TIGER/Line Block Group shapefiles.
        4.  Performs a spatial join to filter block groups to the South Side CAs.
    *   **Status:** *Drafted.* Ready for initial test run.

*   **`02_process_data.py`**:
    *   **Purpose:** Cleans and prepares data for analysis.
    *   **Actions:**
        1.  Merges ACS data with spatial data.
        2.  Calculates derived metrics (e.g., poverty rate from counts).
        3.  Normalizes features using `StandardScaler`.
        4.  Computes a similarity matrix (Cosine Similarity) for clustering.
    *   **Status:** *Drafted.* Basic feature engineering implemented; needs refinement on handling missing data and weighting.

*   **`03_visualize_boundaries.py`**:
    *   **Purpose:** Visualization pipeline.
    *   **Actions:**
        1.  Generates a static base map of official boundaries.
        2.  Creates an interactive Folium map.
    *   **Status:** *Drafted.* Placeholder for visualizing results once clustering is implemented.

## Current Status

*   [x] Project structure established.
*   [x] Core dependencies defined (`requirements.txt`).
*   [ ] **Step 1 (Data):** Run `01_download_data.py` to verify data access and variables.
*   [ ] **Step 2 (Analysis):** Verify data quality (missing values) in `02_process_data.py`.

## Immediate Next Goals

1.  **Verify Data Download:** Run `01_download_data.py` to ensure API access works and the correct variables are retrieved.
2.  **Refine Variables:** Confirm if the chosen 12 ACS variables accurately reflect the "community" definition (Employment, Transportation, Housing, etc.).
3.  **Test Processing:** Run `02_process_data.py` to check for `NaN` issues or data gaps in the South Side region.

## How to Run (Proposed Workflow)

1.  `pip install -r requirements.txt`
2.  `python 01_download_data.py` (Run once to cache data)
3.  `python 02_process_data.py` (Iterate here for modeling)
4.  `python 03_visualize_boundaries.py` (Run to view results)

