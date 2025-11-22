import os
import pandas as pd
import geopandas as gpd
import censusdata
import requests
import zipfile
from utils import SOUTH_SIDE_CAS, ACS_VARIABLES, ACS_VARS_LIST

# --------------------
# Setup
# --------------------
DATA_DIR = "data"
os.makedirs(DATA_DIR, exist_ok=True)

# --------------------
# 1. Download ACS Data
# --------------------
def download_acs(year, savepath):
    print(f"Downloading ACS {year} data...")
    try:
        # Note: censusdata.censusgeo args might need adjustment depending on exact census hierarchy
        # For block groups, we usually need state > county > block group
        geo = censusdata.censusgeo([('state', '17'), ('county', '031'), ('block group', '*')])
        
        # Only download variables we know exist (some might change between years, but these are standard)
        # We might need to handle potential missing vars gracefully in a real robust script
        df = censusdata.download(
            src='acs5',
            year=year,
            geo=geo,
            var=ACS_VARS_LIST
        )
        
        # Reset index to get geo columns
        df = df.reset_index()
        
        # Parse censusdata index to FIPS codes if needed, or just keep it raw for now
        # censusdata index is complex. Let's try to construct a FIPS GEOID.
        # Example index: censusgeo([('state', '17'), ('county', '031'), ('tract', '010100'), ('block group', '1')])
        # We need 17 + 031 + tract + bg
        
        def create_geoid(row):
            geo_obj = row['index']
            # censusdata objects have params() method returning list of tuples
            params = dict(geo_obj.params())
            state = params['state']
            county = params['county']
            tract = params['tract']
            bg = params['block group']
            return f"{state}{county}{tract}{bg}"

        df['GEOID'] = df.apply(create_geoid, axis=1)
        
        # Rename columns
        df = df.rename(columns=ACS_VARIABLES)
        
        # Save
        df.to_csv(savepath, index=False)
        print(f"ACS {year} data saved to {savepath}")
        return df
    except Exception as e:
        print(f"Error downloading ACS {year}: {e}")
        return None

# Download for 2019 and 2023 (checking availability, 2023 might be out, if not use 2022)
# 2023 ACS 5-year might not be fully available via API in all packages yet, but let's try.
# If 2023 fails, we might fall back to 2022, but user requested 2023.
acs_2019 = download_acs(2019, os.path.join(DATA_DIR, "acs_2019_cook_blockgroups.csv"))
# Note: censusdata library might not support 2023 yet if it hasn't been updated. 
# If it fails, we should warn.
acs_2023 = download_acs(2022, os.path.join(DATA_DIR, "acs_2022_cook_blockgroups.csv")) # Using 2022 as proxy if 2023 fails or for stability
if acs_2023 is None:
    print("Trying 2023...")
    acs_2023 = download_acs(2023, os.path.join(DATA_DIR, "acs_2023_cook_blockgroups.csv"))


# --------------------
# 2. Download/Load Chicago Community Areas
# --------------------
cca_path = os.path.join(DATA_DIR, "chicago_community_areas.geojson")
cca_url = "https://data.cityofchicago.org/api/geospatial/cauq-8yn6?method=export&format=GeoJSON"

if not os.path.exists(cca_path):
    print("Downloading Chicago Community Areas...")
    try:
        r = requests.get(cca_url)
        r.raise_for_status()
        with open(cca_path, "wb") as f:
            f.write(r.content)
        print("Downloaded CCA GeoJSON.")
    except Exception as e:
        print(f"Failed to download CCA: {e}")

if os.path.exists(cca_path):
    cca = gpd.read_file(cca_path)
    # Filter for South Side
    # 'area_numbe' is usually the column, string format
    cca['area_numbe'] = cca['area_numbe'].astype(int)
    cca_south = cca[cca['area_numbe'].isin(SOUTH_SIDE_CAS)]
    
    cca_south_path = os.path.join(DATA_DIR, "south_side_community_areas.geojson")
    cca_south.to_file(cca_south_path, driver="GeoJSON")
    print(f"Filtered South Side CAs saved to {cca_south_path}")
else:
    print("Skipping CCA filtering due to missing file.")
    cca_south = None

# --------------------
# 3. Download TIGER Block Groups & Spatial Join
# --------------------
tiger_url = "https://www2.census.gov/geo/tiger/TIGER2023/BG/tl_2023_17_bg.zip"
tiger_zip_path = os.path.join(DATA_DIR, "tl_2023_17_bg.zip")
tiger_extract_dir = os.path.join(DATA_DIR, "tl_2023_17_bg")

if not os.path.exists(tiger_extract_dir):
    print("Downloading TIGER Block Groups...")
    try:
        if not os.path.exists(tiger_zip_path):
            r = requests.get(tiger_url)
            r.raise_for_status()
            with open(tiger_zip_path, "wb") as f:
                f.write(r.content)
        
        with zipfile.ZipFile(tiger_zip_path, 'r') as z:
            z.extractall(tiger_extract_dir)
        print("TIGER data extracted.")
    except Exception as e:
        print(f"Error handling TIGER data: {e}")

# Load and Join
shapefile_path = os.path.join(tiger_extract_dir, "tl_2023_17_bg.shp")
if os.path.exists(shapefile_path) and cca_south is not None:
    print("Processing Block Groups...")
    bg = gpd.read_file(shapefile_path)
    
    # Filter Cook County (031)
    bg = bg[bg['COUNTYFP'] == '031']
    
    # Reproject to match CCA (likely EPSG:4326 or 3435)
    bg = bg.to_crs(cca_south.crs)
    
    # Spatial Join: Keep block groups that intersect with South Side CAs
    # using inner join
    bg_south = gpd.sjoin(bg, cca_south, how="inner", predicate="intersects")
    
    # Save
    bg_south_path = os.path.join(DATA_DIR, "south_side_block_groups.geojson") # Prefer GeoJSON for easy reading
    bg_south.to_file(bg_south_path, driver="GeoJSON")
    print(f"South Side Block Groups saved to {bg_south_path}")
    
    # Also save a simple CSV mapping GEOID -> CA
    bg_south[['GEOID', 'area_numbe', 'community']].to_csv(os.path.join(DATA_DIR, "bg_to_ca_mapping.csv"), index=False)

print("Data acquisition complete.")

