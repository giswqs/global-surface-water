import ee
import folium
import geemap.colormaps as cm
import pandas as pd
import streamlit as st
import geemap.foliumap as geemap
import folium.plugins as plugins
from .data_dict import DEMS, LANDCOVERS, LANDFORMS


def app():

    st.title("Split-panel Map")
    # df = pd.read_csv("data/scotland_xyz.tsv", sep="\t")
    basemaps = geemap.basemaps
    names = (
        list(DEMS.keys())
        + list(LANDCOVERS.keys())
        + list(LANDFORMS.keys())
        + list(basemaps.keys())
    )
    palettes = ["Default"] + cm.list_colormaps()

    col1, col1a, col2, col2a, col3, col4, col5, col6 = st.columns(
        [2, 2, 2, 2, 1, 1, 1, 1.5]
    )
    with col1:
        left_name = st.selectbox(
            "Select the left layer",
            names,
            index=names.index("TERRAIN"),
        )

    with col1a:
        left_palette = st.selectbox(
            "Select the left colormap",
            palettes,
            index=palettes.index("terrain"),
        )

    with col2:
        right_name = st.selectbox(
            "Select the right layer",
            names,
            index=names.index("HYBRID"),
        )
    with col2a:
        right_palette = st.selectbox(
            "Select the right colormap",
            palettes,
            index=palettes.index("gist_earth"),
        )

    with col3:
        # lat = st.slider('Latitude', -90.0, 90.0, 55.68, step=0.01)
        lat = st.text_input("Latitude", "40")

    with col4:
        # lon = st.slider('Longitude', -180.0, 180.0, -2.98, step=0.01)
        lon = st.text_input("Longitude", "-100")

    with col5:
        # zoom = st.slider('Zoom', 1, 24, 6, step=1)
        zoom = st.text_input("Zoom", "4")

    with col6:
        clip = st.checkbox("Clip to ROI")

    Map = geemap.Map(
        center=[float(lat), float(lon)],
        zoom=int(zoom),
        locate_control=True,
        draw_control=False,
        measure_control=False,
        google_map=False,
    )
    Map.add_basemap("HYBRID")
    Map.add_basemap("TERRAIN")
    measure = plugins.MeasureControl(position="bottomleft", active_color="orange")
    measure.add_to(Map)

    st.session_state["ROI"] = ee.FeatureCollection(
        "users/giswqs/MRB/NWI_HU8_Boundary_Simplify"
    )

    if left_name in basemaps:
        left_layer = basemaps[left_name]
    else:
        if left_name in DEMS:
            data = DEMS[left_name]
        elif left_name in LANDCOVERS:
            data = LANDCOVERS[left_name]
        elif left_name in LANDFORMS:
            data = LANDFORMS[left_name]

        if clip:
            data["id"] = data["id"].clip(st.session_state["ROI"])
        if left_palette != "Default":
            if left_name in DEMS:
                data["vis"]["palette"] = cm.get_palette(left_palette, 15)
        left_layer = geemap.ee_tile_layer(data["id"], data["vis"], left_name)

    if right_name in basemaps:
        right_layer = basemaps[right_name]
    else:
        if right_name in DEMS:
            data = DEMS[right_name]
        elif right_name in LANDCOVERS:
            data = LANDCOVERS[right_name]
        elif right_name in LANDFORMS:
            data = LANDFORMS[right_name]

        if clip:
            data["id"] = data["id"].clip(st.session_state["ROI"])

        if right_palette != "Default":
            if right_name in DEMS:
                data["vis"]["palette"] = cm.get_palette(right_palette, 15)
        right_layer = geemap.ee_tile_layer(data["id"], data["vis"], right_name)

    if left_name == right_name:
        st.error("Please select different layers")
    Map.split_map(left_layer, right_layer)

    sinks_30m = ee.FeatureCollection("users/giswqs/MRB/NED_30m_sinks")

    Map.addLayer(sinks_30m, {}, "Depressions (30m)", False)

    sinks_10m = ee.FeatureCollection("users/giswqs/MRB/NED_10m_sinks")
    sinks_10m_style = sinks_10m.style(
        **{"color": "0000ff", "width": 2, "fillColor": "0000ff44"}
    )
    Map.addLayer(sinks_10m_style, {}, "Depressions (10m)", False)

    huc8 = ee.FeatureCollection("USGS/WBD/2017/HUC10").filter(
        ee.Filter.Or(
            ee.Filter.stringStartsWith(**{"leftField": "huc10", "rightValue": "05"}),
            ee.Filter.stringStartsWith(**{"leftField": "huc10", "rightValue": "07"}),
            ee.Filter.stringStartsWith(**{"leftField": "huc10", "rightValue": "10"}),
        )
    )
    Map.addLayer(
        huc8.style(**{"fillColor": "00000000", "width": 1}), {}, "NHD-HUC10", False
    )

    ROI_style = st.session_state["ROI"].style(
        **{"color": "ff0000", "width": 2, "fillColor": "00000000"}
    )
    Map.addLayer(ROI_style, {}, "Study Area")

    if left_name in LANDFORMS or right_name in LANDFORMS:
        Map.add_legend(title="ALOS Landforms", builtin_legend="ALOS_landforms")

    if left_name == "ESA WorldCover" or right_name == "ESA WorldCover":
        Map.add_legend(title="ESA Landcover", builtin_legend="ESA_WorldCover")

    if left_name == "ESRI Global Land Cover" or right_name == "ESRI Global Land Cover":
        Map.add_legend(title="ESRI Landcover", builtin_legend="ESRI_LandCover")

    if left_name == "NLCD 2019" or right_name == "NLCD 2019":
        Map.add_legend(title="NLCD Landcover", builtin_legend="NLCD")

    Map.to_streamlit(height=600)
