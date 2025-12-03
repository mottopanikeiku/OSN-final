import os
import pandas as pd
import geopandas as gpd
from typing import Optional, Tuple
from .config import DATA_DIR, SOUTH_SIDE_BBOX

class DataLoader:
    """
    Handles loading of ACS data and TIGER shapefiles, including spatial filtering.
    """
    
    @staticmethod
    def load_acs_data(year: int) -> Optional[pd.DataFrame]:
        """Loads raw ACS CSV data for a specific year."""
        path = os.path.join(DATA_DIR, f"acs_{year}_cook_blockgroups.csv")
        if not os.path.exists(path):
            print(f"Error: ACS data file not found at {path}")
            return None
        
        df = pd.read_csv(path)
        # Ensure GEOID is string for merging
        if 'GEOID' in df.columns:
            df['GEOID'] = df['GEOID'].astype(str)
        return df

    @staticmethod
    def load_shapefile() -> Optional[gpd.GeoDataFrame]:
        """Loads the TIGER block group shapefile."""
        path = os.path.join(DATA_DIR, "tl_2023_17_bg", "tl_2023_17_bg.shp")
        if not os.path.exists(path):
            # Fallback to parent directory check
            path = os.path.join(DATA_DIR, "tl_2023_17_bg.shp")
            if not os.path.exists(path):
                print(f"Error: Shapefile not found at {path}")
                return None
        
        gdf = gpd.read_file(path)
        # Filter Cook County (031)
        gdf = gdf[gdf['COUNTYFP'] == '031']
        return gdf

    @classmethod
    def load_merged_data(cls, year: int) -> Optional[gpd.GeoDataFrame]:
        """
        Loads and merges spatial and demographic data, filtering for the South Side.
        Removes water-only blocks.
        """
        df = cls.load_acs_data(year)
        gdf = cls.load_shapefile()
        
        if df is None or gdf is None:
            return None
            
        # Ensure GEOID consistency
        gdf['GEOID'] = gdf['GEOID'].astype(str)
        
        # Spatial Filter (South Side BBox)
        south_gdf = gdf[gdf.intersects(SOUTH_SIDE_BBOX)].copy()
        
        # Filter Water Blocks (ALAND > 0)
        if 'ALAND' in south_gdf.columns:
            south_gdf = south_gdf[south_gdf['ALAND'] > 0]
            
        # Merge
        merged = pd.merge(south_gdf, df, on='GEOID', how='inner')
        print(f"[{year}] Loaded {len(merged)} block groups after filtering.")
        
        return merged

