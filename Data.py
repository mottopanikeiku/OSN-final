import os
import pandas as pd
import geopandas as gpd
import censusdata
import requests, zipfile, io

# --------------------
# Setup
# --------------------
os.makedirs("data", exist_ok=True)

south_side_cas = [
    35,36,37,38,39,40,41,42,43,44,45,46,47,48,49,50,51,52,53,54,67,68,58
]

acs_vars = [
    'B19013_001E','B15003_017E','B15003_022E','B03002_003E',
    'B03002_004E','B03002_012E','B01001_001E','B23025_004E',
    'B08301_001E','B17001_002E','B25077_001E'
]

# --------------------
# Function to download ACS data
# --------------------
def download_acs(year, savepath):
    df = censusdata.download(
        src='acs5',
        year=year,
        geo=censusdata.censusgeo([('state','17'),('county','031'),('block group','*')]),
        var=acs_vars
    )
    df.to_csv(savepath)
    print(f"ACS {year} data saved to {savepath}")
    return df

# Download ACS data
acs_2019 = download_acs(2019, "data/acs_2019_cook_blockgroups.csv")
acs_2023 = download_acs(2023, "data/acs_2023_cook_blockgroups.csv")

# --------------------
# Load Chicago Community Areas (local file)
# --------------------
local_cca_path = "data/chicago_community_areas.geojson"

if not os.path.exists(local_cca_path):
    raise RuntimeError(f"Please download a valid GeoJSON and save it as {local_cca_path}")

cca = gpd.read_file(local_cca_path)
cca = cca[cca['area_numbe'].astype(int).isin(south_side_cas)]
cca.to_file("data/south_side_community_areas.geojson", driver="GeoJSON")
print("Filtered South Side community areas saved.")

# --------------------
# Download Illinois statewide TIGER block groups robustly
# --------------------
tiger_url = "https://www2.census.gov/geo/tiger/TIGER2023/BG/tl_2023_17_bg.zip"
local_tiger_zip = "data/tl_2023_17_bg.zip"

def download_tiger(url, savepath):
    try:
        r = requests.get(url)
        r.raise_for_status()
        if r.headers.get('Content-Type') != 'application/zip':
            raise RuntimeError("Downloaded file is not a ZIP. Check URL.")
        with open(savepath, "wb") as f:
            f.write(r.content)
        print("TIGER BG ZIP downloaded successfully.")
    except Exception as e:
        print(f"Failed to download TIGER ZIP: {e}")
        if os.path.exists(savepath):
            print("Using existing local TIGER ZIP.")
        else:
            raise RuntimeError("No valid TIGER ZIP available. Please download manually.")

# Download or use existing
download_tiger(tiger_url, local_tiger_zip)

# Extract ZIP
with zipfile.ZipFile(local_tiger_zip, 'r') as z:
    z.extractall("data/tl_2023_17_bg")

# Load shapefile
bg = gpd.read_file("data/tl_2023_17_bg/tl_2023_17_bg.shp")

# Filter Cook County
bg = bg[bg['COUNTYFP'] == '031']

# --------------------
# Spatial join: filter block groups in South Side
# --------------------
bg = bg.to_crs(cca.crs)
bg_south = gpd.sjoin(bg, cca, predicate="intersects")
bg_south.to_file("data/south_side_block_groups.shp")
print("South Side block groups saved.")
