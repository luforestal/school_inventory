
import pandas as pd
import geopandas as gpd
import folium
import numpy as np
from itertools import cycle
from pathlib import Path
import base64


# =====================================================
# MAIN FUNCTION
# =====================================================

def build_tree_map():

    """
    Build an interactive tree inventory map for ANY school dataset.

    Expected folder structure:

    ├── <School Name> Tree Data.xlsx
    ├── Boundaries/
    │     └── Boundaries.shp
    └── Photos/   (optional)
          └── TreeCode.jpg / png ...

    Returns
    -------
    folium.Map
    """

    # -------------------------------------------------
    # BASE DIR
    # -------------------------------------------------
    base_dir = Path(__file__).parent.resolve()

    # -------------------------------------------------
    # FIND EXCEL
    # -------------------------------------------------
    excel_files = list(base_dir.glob("*.xlsx"))
    if not excel_files:
        raise FileNotFoundError("❌ No Excel file found in folder.")

    excel_path = excel_files[0]

    school_name = (
        excel_path.stem
        .replace("Tree Data", "")
        .replace("tree data", "")
        .strip()
    )

    OUTPUT_HTML = f"{school_name.replace(' ','_')}_tree_map.html"

    # -------------------------------------------------
    # BOUNDARY
    # -------------------------------------------------
    boundary_path = base_dir / "Boundaries" / "Boundaries.shp"
    if not boundary_path.exists():
        raise FileNotFoundError("❌ Missing Boundaries/Boundaries.shp")

    # -------------------------------------------------
    # PHOTOS
    # -------------------------------------------------
    photos_dir = base_dir / "Photos"

    # -------------------------------------------------
    # LOAD INVENTORY
    # -------------------------------------------------
    df_map = pd.read_excel(excel_path, sheet_name="Trees")
    df_map = df_map.dropna(subset=["lat", "lon"])

    center = [df_map["lat"].mean(), df_map["lon"].mean()]

    # -------------------------------------------------
    # BASE MAP
    # -------------------------------------------------
    m = folium.Map(
        location=center,
        zoom_start=18,
        tiles="OpenStreetMap",
        name="OSM"
    )

    folium.TileLayer("CartoDB positron").add_to(m)

    folium.TileLayer(
        "https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{x}/{y}",
        attr="ESRI World Imagery",
        name="Satellite",
        overlay=False,
        control=True,
    ).add_to(m)

    # -------------------------------------------------
    # SCHOOL BOUNDARY
    # -------------------------------------------------
    gdf = gpd.read_file(boundary_path)

    if gdf.crs is None:
        gdf = gdf.set_crs(epsg=3310)

    gdf = gdf.to_crs(epsg=4326)

    folium.GeoJson(
        gdf,
        name="School boundary",
        style_function=lambda x: {
            "color": "black",
            "weight": 1,
            "fillColor": "none",
            "fillOpacity": 0,
        }
    ).add_to(m)

    # -------------------------------------------------
    # GENUS STYLES
    # -------------------------------------------------
    genera = sorted(df_map["Genus"].dropna().unique())

    shape_specs = [
        {"sides": 3, "rotation": 0},
        {"sides": 4, "rotation": 45},
        {"sides": 5, "rotation": 0},
        {"sides": 6, "rotation": 0},
        {"sides": 8, "rotation": 0},
        {"sides": 3, "rotation": 180},
        {"sides": 4, "rotation": 0},
    ]

    colors = [
        "red", "blue", "green", "purple", "orange",
        "darkred", "darkblue", "darkgreen",
        "cadetblue", "pink", "black", "gray",
    ]

    shapes = cycle(shape_specs)
    cols = cycle(colors)

    genus_styles = {
        g: {"shape": next(shapes), "color": next(cols)}
        for g in genera
    }

    # =================================================
    # ADD TREES — ORIGINAL BLOCK RESTORED ✅
    # =================================================

    for _, r in df_map.iterrows():

        lat, lon = float(r["lat"]), float(r["lon"])
        genus = r.get("Genus", "NA")
        tree_code = str(r.get("TreeCode", "")).strip()

        style = genus_styles.get(genus)

        # -------- CANOPY SIZE --------
        ns = r.get("CrownNSm", np.nan)
        ew = r.get("CrownEWm", np.nan)

        crown_radius = None
        if pd.notna(ns) and pd.notna(ew):
            crown_radius = (ns + ew) / 4
        elif pd.notna(ns):
            crown_radius = ns / 2
        elif pd.notna(ew):
            crown_radius = ew / 2

        if crown_radius:
            folium.Circle(
                location=[lat, lon],
                radius=crown_radius,
                fill=True,
                fill_opacity=0.3,
                color=None,
                stroke=False,
            ).add_to(m)

        # -------- PHOTO LOOKUP --------
        photo_html = ""

        if tree_code and photos_dir.exists():

            code = tree_code.lower()

            matches = [
                p for p in photos_dir.iterdir()
                if code in p.stem.lower()
                and p.suffix.lower() in [".jpg", ".jpeg", ".png"]
            ]

            if matches:
                img_path = matches[0]

                with open(img_path, "rb") as f:
                    encoded = base64.b64encode(f.read()).decode("utf-8")

                ext = img_path.suffix.lower().replace(".", "")
                if ext == "jpg":
                    ext = "jpeg"

                photo_html = f"""
                <br>
                <img src="data:image/{ext};base64,{encoded}"
                     width="200"
                     style="border-radius:8px;margin-top:6px;">
                """
            else:
                photo_html = "<br><i>No photo available</i>"

        # -------- POPUP --------
        popup_html = f"""
        <div style="font-size:13px;">
            <b>Tree code:</b> {tree_code}<br>
            <b>Genus:</b> {r.get('Genus','')}<br>
            <b>Species:</b> {r.get('Species','')}<br>
            <b>DBH (cm):</b> {r.get('DBH1cm','')}<br>
            <b>Height (m):</b> {r.get('Heightm','')}
            {photo_html}
        </div>
        """

        popup = folium.Popup(popup_html, max_width=300)

        # -------- MARKERS --------
        if style:
            shape = style["shape"]
            color = style["color"]
        else:
            shape = {"sides": 4, "rotation": 0}
            color = "gray"

        folium.RegularPolygonMarker(
            location=[lat, lon],
            number_of_sides=shape["sides"],
            rotation=shape["rotation"],
            radius=7,
            color=color,
            fill=True,
            fill_opacity=0.9,
            popup=popup,
        ).add_to(m)

    # =================================================
    # FINALIZE
    # =================================================
    folium.LayerControl().add_to(m)

    m.save(base_dir / OUTPUT_HTML)

    print(f"✅ Map created for: {school_name}")
    print(f"📄 Output: {OUTPUT_HTML}")

    return m
