import geopandas as gpd
import matplotlib.pyplot as plt
import folium
import os

# --------------------
# Setup
# --------------------
DATA_DIR = "data"
OUTPUT_DIR = "output"
os.makedirs(OUTPUT_DIR, exist_ok=True)

def create_base_map():
    bg_path = os.path.join(DATA_DIR, "south_side_block_groups.geojson")
    if not os.path.exists(bg_path):
        print("Block group shapefile not found. Run 01_download_data.py first.")
        return

    print("Loading shapefile...")
    bg = gpd.read_file(bg_path)
    
    # 1. Static Map (Matplotlib)
    print("Generating static map...")
    fig, ax = plt.subplots(figsize=(10, 10))
    bg.plot(column='area_numbe', cmap='tab20', ax=ax, edgecolor='white', linewidth=0.2)
    ax.set_title("South Side Block Groups by Community Area (Official)")
    ax.axis('off')
    plt.savefig(os.path.join(OUTPUT_DIR, "south_side_base_map.png"), dpi=300)
    plt.close()
    
    # 2. Interactive Map (Folium)
    print("Generating interactive map...")
    # Reproject to lat/lon for Folium
    bg_wgs84 = bg.to_crs(epsg=4326)
    
    m = folium.Map(location=[41.79, -87.6], zoom_start=12)
    
    folium.Choropleth(
        geo_data=bg_wgs84,
        name="Official Community Areas",
        data=bg_wgs84,
        columns=['GEOID', 'area_numbe'],
        key_on='feature.properties.GEOID',
        fill_color='YlGn',
        fill_opacity=0.7,
        line_opacity=0.2,
        legend_name='Community Area ID'
    ).add_to(m)
    
    folium.LayerControl().add_to(m)
    m.save(os.path.join(OUTPUT_DIR, "south_side_interactive.html"))
    
    print("Maps saved to output/ directory.")

if __name__ == "__main__":
    create_base_map()

