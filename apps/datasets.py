import ee
import geemap.foliumap as geemap
import geemap.colormaps as cm
import geopandas as gpd
import streamlit as st


@st.cache
def uploaded_file_to_gdf(data):
    import tempfile
    import os
    import uuid

    _, file_extension = os.path.splitext(data.name)
    file_id = str(uuid.uuid4())
    file_path = os.path.join(tempfile.gettempdir(), f"{file_id}{file_extension}")

    with open(file_path, "wb") as file:
        file.write(data.getbuffer())

    if file_path.lower().endswith(".kml"):
        gpd.io.file.fiona.drvsupport.supported_drivers["KML"] = "rw"
        gdf = gpd.read_file(file_path, driver="KML")
    else:
        gdf = gpd.read_file(file_path)

    return gdf


def app():

    st.title("Global Surface Water Datasets")

    col1, col2 = st.columns([3, 1])

    Map = geemap.Map(Draw_export=True, locate_control=True)

    roi = ee.FeatureCollection("users/giswqs/public/countries")
    countries = roi.aggregate_array("name").getInfo()
    countries.sort()

    basemaps = list(geemap.basemaps.keys())
    with col2:
        basemap = st.selectbox(
            "Select a basemap",
            basemaps,
            index=basemaps.index("HYBRID"),
        )
        Map.add_basemap(basemap)

        select = st.checkbox("Select a country")
        if select:
            country = st.selectbox(
                "Select a country from dropdown list",
                countries,
                index=countries.index("United States of America"),
            )
            st.session_state["ROI"] = roi.filter(ee.Filter.eq("name", country))
        else:

            with st.expander("Click here to upload an ROI", False):
                upload = st.file_uploader(
                    "Upload a GeoJSON, KML or Shapefile (as a zif file) to use as an ROI. 😇👇",
                    type=["geojson", "kml", "zip"],
                )

                if upload:
                    gdf = uploaded_file_to_gdf(upload)
                    st.session_state["ROI"] = geemap.gdf_to_ee(gdf, geodesic=False)
                    # Map.add_gdf(gdf, "ROI")
                else:
                    st.session_state["ROI"] = roi

    # roi = ee.FeatureCollection("users/giswqs/MRB/NWI_HU8_Boundary_Simplify")
    style = {
        "color": "000000ff",
        "width": 1,
        "lineType": "solid",
        "fillColor": "00000000",
    }

    # select_holder = col2.empty()
    with col2:
        datasets = st.multiselect(
            "Select datasets",
            [
                "USDA NASS Cropland",
                "JRC Surface Water",
                "NLCD",
                "Esri Land Cover",
                "ESA Land Cover",
                "OpenStreetMap",
                "Global River Width Dataset",
                "NHD-HUC2",
                "NHD-HUC4",
                "NHD-HUC6",
                "NHD-HUC8",
                "NHD-HUC10",
            ],
        )

    # form = st.form(key="submit_form")
    # submit = form.form_submit_button(label="Submit")

    if "USDA NASS Cropland" in datasets:
        cropland = (
            ee.ImageCollection("USDA/NASS/CDL")
            .select("cropland")
            .filterDate("2010-01-01", "2020-01-01")
        )

        def extract_nass_water(img):
            mask = img.remap([83, 87, 111, 190, 195], ee.List.sequence(991, 995)).gt(
                990
            )
            result = img.updateMask(mask)
            return result

        nass_waters = cropland.map(extract_nass_water)
        nass_water_2019 = nass_waters.filterDate("2019-01-01", "2019-12-31").first()
        nass_water_max = nass_waters.map(lambda img: img.gt(0)).sum().selfMask()
        Map.addLayer(
            nass_water_max.randomVisualizer().clip(roi), {}, "NASS Max Water Extent"
        )
        Map.addLayer(nass_water_2019.clip(roi), {}, "NASS Water 2019")

    if "JRC Surface Water" in datasets:
        dataset = (
            ee.ImageCollection("JRC/GSW1_3/MonthlyHistory")
            .filter(ee.Filter.calendarRange(7, 8, "month"))
            .map(lambda img: img.eq(2).selfMask())
        )

        visualization = {
            "bands": ["water"],
            "min": 0.0,
            "max": 2.0,
            "palette": ["ffffff", "fffcb8", "0905ff"],
        }

        Map.addLayer(
            dataset.mosaic().clip(roi), {"palette": ["blue"]}, "JRC Monthly Water"
        )

    if "NLCD" in datasets:
        dataset = ee.ImageCollection("USGS/NLCD_RELEASES/2016_REL")
        nlcd = dataset.filter(
            ee.Filter.inList("system:index", ["2001", "2006", "2011", "2016"])
        ).select("landcover")

        def extract_nlcd_water(img):
            mask = img.remap([11, 90, 95], ee.List.sequence(991, 993)).gt(990)
            result = img.updateMask(mask)
            return result

        nlcd_waters = nlcd.map(extract_nlcd_water)
        nlcd_water_2016 = nlcd_waters.filterDate("2016-01-01", "2016-12-31").first()
        Map.addLayer(nlcd_water_2016.clip(roi), {}, "NLCD Water 2016")

    if "Esri Land Cover" in datasets:

        esri_lulc10 = ee.ImageCollection(
            "projects/sat-io/open-datasets/landcover/ESRI_Global-LULC_10m"
        ).mosaic()
        legend_dict = {
            "names": [
                "Water",
                "Trees",
                "Grass",
                "Flooded Vegetation",
                "Crops",
                "Scrub/Shrub",
                "Built Area",
                "Bare Ground",
                "Snow/Ice",
                "Clouds",
            ],
            "colors": [
                "#1A5BAB",
                "#358221",
                "#A7D282",
                "#87D19E",
                "#FFDB5C",
                "#EECFA8",
                "#ED022A",
                "#EDE9E4",
                "#F2FAFF",
                "#C8C8C8",
            ],
        }

        vis_params = {"min": 1, "max": 10, "palette": legend_dict["colors"]}
        Map.addLayer(esri_lulc10.clip(roi), vis_params, "ESRI LULC 10m", False)
        Map.addLayer(
            esri_lulc10.eq(1).clip(roi).selfMask(),
            {"palette": "blue"},
            "ESRI Water",
            False,
        )

    if "ESA Land Cover" in datasets:
        dataset = ee.ImageCollection("ESA/WorldCover/v100").first().clip(roi).selfMask()
        Map.addLayer(dataset, {}, "Landcover")

    if "OpenStreetMap" in datasets:
        osm_water = (
            ee.ImageCollection("projects/sat-io/open-datasets/OSM_waterLayer")
            .median()
            .toInt()
            .clip(roi.geometry())
        )
        vis = {
            "min": 1,
            "max": 5,
            "palette": ["08306b", "08519c", "2171b5", "4292c6", "6baed6"],
        }
        Map.addLayer(osm_water, vis, "OSM Water")

    if "Global River Width Dataset" in datasets:
        water_mask = (
            ee.ImageCollection("projects/sat-io/open-datasets/GRWL/water_mask_v01_01")
            .median()
            .toInt()
            .clip(roi.geometry())
        )

        grwl_summary = ee.FeatureCollection(
            "projects/sat-io/open-datasets/GRWL/grwl_SummaryStats_v01_01"
        ).filterBounds(roi)
        grwl_water_vector = ee.FeatureCollection(
            "projects/sat-io/open-datasets/GRWL/water_vector_v01_01"
        ).filterBounds(roi)

        Map.addLayer(water_mask, {"palette": "blue"}, "GRWL RIver Mask")
        Map.addLayer(
            grwl_water_vector.style(**{"fillColor": "00000000", "color": "FF5500"}),
            {},
            "GRWL Centerline",
            False,
        )
        Map.addLayer(
            grwl_summary.style(**{"fillColor": "00000000", "color": "EE5500"}),
            {},
            "GRWL Centerline Simplified",
        )

    if "NHD-HUC2" in datasets:
        huc2 = ee.FeatureCollection("USGS/WBD/2017/HUC02")
        Map.addLayer(huc2.style(**{"fillColor": "00000000"}), {}, "NHD-HUC2")

    if "NHD-HUC4" in datasets:
        huc4 = ee.FeatureCollection("USGS/WBD/2017/HUC04")
        Map.addLayer(huc4.style(**{"fillColor": "00000000"}), {}, "NHD-HUC4")

    if "NHD-HUC6" in datasets:
        huc6 = ee.FeatureCollection("USGS/WBD/2017/HUC06")
        Map.addLayer(huc6.style(**{"fillColor": "00000000"}), {}, "NHD-HUC6")

    if "NHD-HUC8" in datasets:
        huc8 = ee.FeatureCollection("USGS/WBD/2017/HUC08")
        Map.addLayer(huc8.style(**{"fillColor": "00000000"}), {}, "NHD-HUC8")

    if "NHD-HUC10" in datasets:
        huc10 = ee.FeatureCollection("USGS/WBD/2017/HUC10")
        Map.addLayer(huc10.style(**{"fillColor": "00000000"}), {}, "NHD-HUC10")

    if select and country is not None:
        name = country
        style["color"] = "#FFFF00"
        style["width"] = 2
    elif upload:
        name = "ROI"
        style["color"] = "#FFFF00"
        style["width"] = 2
    else:
        name = "World"

    Map.addLayer(st.session_state["ROI"].style(**style), {}, name)
    Map.centerObject(st.session_state["ROI"])

    with col1:
        Map.to_streamlit(height=750)
