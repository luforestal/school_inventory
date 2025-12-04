import pandas as pd
import folium
import numpy as np
from itertools import cycle
from pathlib import Path
import geopandas as gpd


# =====================================================
# MAIN FUNCTION — GENERIC
def build_tree_map():

    """
    Build an interactive tree inventory map for ANY school dataset.

    Expected folder structure (same directory as this script):

    ├── <School Name> Tree Data.xlsx
    ├── Boundaries/
    │     └── Boundaries.shp
    └── Photos/ (optional)

    Returns
    -------
    folium.Map
    """

    base_dir = Path(__file__).parent.resolve()

    # =====================================================
    # AUTO-DETECT INPUT FILES
    # =====================================================

    # Find Excel
    excel_files = list(base_dir.glob("*.xlsx"))
    if not excel_files:
        raise FileNotFoundError("❌ No Excel file found in folder.")
    excel_path = excel_files[0]

    # Detect school name
    school_name = (
        excel_path.stem
        .replace("Tree Data","")
        .replace("tree data","")
        .strip()
    )

    output_html = f"{school_name.replace(' ','_')}_tree_map.html"

    # Boundary
    boundary_path = base_dir / "Boundaries" / "Boundaries.shp"
    if not boundary_path.exists():
        raise FileNotFoundError("❌ Missing Boundaries/Boundaries.shp")

    # =====================================================
    # LOAD INVENTORY
    # =====================================================

    df = pd.read_excel(excel_path)
    df = df.dropna(subset=["lat","lon"])

    center = [df.lat.mean(), df.lon.mean()]

    # =====================================================
    # BASE MAP
    # =====================================================

    m = folium.Map(center,
                   zoom_start=18,
                   tiles="OpenStreetMap",
                   name="OSM")

    folium.TileLayer("CartoDB positron").add_to(m)

    folium.TileLayer(
        "https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{x}/{y}",
        attr="Esri World Imagery",
        name="Satellite",
        overlay=False,
        control=True
    ).add_to(m)

    # =====================================================
    # SCHOOL BOUNDARY
    # =====================================================

    gdf = gpd.read_file(boundary_path)

    if gdf.crs is None:
        gdf = gdf.set_crs(epsg=3310)

    gdf = gdf.to_crs(epsg=4326)

    folium.GeoJson(
        gdf,
        name="School boundary",
        style_function=lambda x:{
            "color":"black",
            "weight":1,
            "fillColor":"none",
            "fillOpacity":0
        }
    ).add_to(m)

    # =====================================================
    # GENUS STYLES
    # =====================================================

    genera = sorted(df["Genus"].dropna().unique())

    shape_specs = [
        {"sides":3,"rotation":0},
        {"sides":4,"rotation":45},
        {"sides":5,"rotation":0},
        {"sides":6,"rotation":0},
        {"sides":8,"rotation":0},
        {"sides":3,"rotation":180},
        {"sides":4,"rotation":0},
    ]

    colors = [
        "red","blue","green","purple","orange",
        "darkred","darkblue","darkgreen","cadetblue",
        "pink","black","gray"
    ]

    shapes = cycle(shape_specs)
    cols = cycle(colors)

    genus_styles = {
        g:{"shape":next(shapes),"color":next(cols)}
        for g in genera
    }

    # =====================================================
    # PLOT TREES
    # =====================================================

    for _, r in df.iterrows():

        style = genus_styles.get(
            r.Genus,
            {"shape":{"sides":4,"rotation":0},"color":"gray"}
        )

        # ----- CANOPY -----
        radius = None
        if pd.notna(r.CrownNSm) and pd.notna(r.CrownEWm):
            radius = (r.CrownNSm + r.CrownEWm) / 4

        if radius:
            folium.Circle(
                [r.lat,r.lon],
                radius=radius,
                fill=True,
                fill_opacity=0.3,
                color=None,
                stroke=False
            ).add_to(m)

        popup = f"""
        <b>Tree code:</b> {r.TreeCode}<br>
        <b>Genus:</b> {r.Genus}<br>
        <b>Species:</b> {r.Species}<br>
        <b>DBH (cm):</b> {r.DBH1cm}<br>
        <b>Height (m):</b> {r.Heightm}
        """

        folium.RegularPolygonMarker(
            [r.lat,r.lon],
            number_of_sides=style["shape"]["sides"],
            rotation=style["shape"]["rotation"],
            radius=7,
            color=style["color"],
            popup=popup,
            fill=True,
            fill_opacity=0.9
        ).add_to(m)

    folium.LayerControl().add_to(m)

    # =====================================================
    # SAVE MAP
    # =====================================================

    m.save(base_dir / output_html)

    print(f"✅ Map created for: {school_name}")
    print(f"📄 Output: {output_html}")

    return m
