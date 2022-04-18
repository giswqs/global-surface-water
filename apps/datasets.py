import ee
import geemap.foliumap as geemap
import geemap.colormaps as cm
import streamlit as st


def app():

    st.title("Surface Water Datasets for Missouri River Basins")

    Map = geemap.Map(Draw_export=True, basemap="HYBRID")

    roi = ee.FeatureCollection("users/giswqs/MRB/NWI_HU8_Boundary_Simplify")
    style = {
        "color": "000000ff",
        "width": 2,
        "lineType": "solid",
        "fillColor": "00000000",
    }

    col1, col2 = st.columns([1.5, 4])

    basemap = col1.selectbox("Select a basemap", geemap.basemaps.keys())
    Map.add_basemap(basemap)

    select_holder = col2.empty()
    selected = select_holder.multiselect(
        "Select a dataset",
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

    form = st.form(key="submit_form")
    submit = form.form_submit_button(label="Submit")

    if submit:

        if "USDA NASS Cropland" in selected:
            cropland = (
                ee.ImageCollection("USDA/NASS/CDL")
                .select("cropland")
                .filterDate("2010-01-01", "2020-01-01")
            )

            def extract_nass_water(img):
                mask = img.remap(
                    [83, 87, 111, 190, 195], ee.List.sequence(991, 995)
                ).gt(990)
                result = img.updateMask(mask)
                return result

            nass_waters = cropland.map(extract_nass_water)
            nass_water_2019 = nass_waters.filterDate("2019-01-01", "2019-12-31").first()
            nass_water_max = nass_waters.map(lambda img: img.gt(0)).sum().selfMask()
            Map.addLayer(
                nass_water_max.randomVisualizer().clip(roi), {}, "NASS Max Water Extent"
            )
            Map.addLayer(nass_water_2019.clip(roi), {}, "NASS Water 2019")

        if "JRC Surface Water" in selected:
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

        if "NLCD" in selected:
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

        if "Esri Land Cover" in selected:

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

        if "ESA Land Cover" in selected:
            dataset = (
                ee.ImageCollection("ESA/WorldCover/v100").first().clip(roi).selfMask()
            )
            Map.addLayer(dataset, {}, "Landcover")

        if "OpenStreetMap" in selected:
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

        if "Global River Width Dataset" in selected:
            water_mask = (
                ee.ImageCollection(
                    "projects/sat-io/open-datasets/GRWL/water_mask_v01_01"
                )
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

        if "NHD-HUC2" in selected:
            huc2 = ee.FeatureCollection("USGS/WBD/2017/HUC02").filter(
                ee.Filter.inList(
                    "name",
                    ["Upper Mississippi Region", "Missouri Region", "Ohio Region"],
                )
            )
            Map.addLayer(huc2.style(**{"fillColor": "00000000"}), {}, "NHD-HUC2")

        if "NHD-HUC4" in selected:
            huc4 = ee.FeatureCollection("USGS/WBD/2017/HUC04").filter(
                ee.Filter.Or(
                    ee.Filter.stringStartsWith(
                        **{"leftField": "huc4", "rightValue": "05"}
                    ),
                    ee.Filter.stringStartsWith(
                        **{"leftField": "huc4", "rightValue": "07"}
                    ),
                    ee.Filter.stringStartsWith(
                        **{"leftField": "huc4", "rightValue": "10"}
                    ),
                )
            )
            Map.addLayer(huc4.style(**{"fillColor": "00000000"}), {}, "NHD-HUC4")

        if "NHD-HUC6" in selected:
            huc6 = ee.FeatureCollection("USGS/WBD/2017/HUC06").filter(
                ee.Filter.Or(
                    ee.Filter.stringStartsWith(
                        **{"leftField": "huc6", "rightValue": "05"}
                    ),
                    ee.Filter.stringStartsWith(
                        **{"leftField": "huc6", "rightValue": "07"}
                    ),
                    ee.Filter.stringStartsWith(
                        **{"leftField": "huc6", "rightValue": "10"}
                    ),
                )
            )
            Map.addLayer(huc6.style(**{"fillColor": "00000000"}), {}, "NHD-HUC6")

        if "NHD-HUC8" in selected:
            huc8 = ee.FeatureCollection("USGS/WBD/2017/HUC08").filter(
                ee.Filter.Or(
                    ee.Filter.stringStartsWith(
                        **{"leftField": "huc8", "rightValue": "05"}
                    ),
                    ee.Filter.stringStartsWith(
                        **{"leftField": "huc8", "rightValue": "07"}
                    ),
                    ee.Filter.stringStartsWith(
                        **{"leftField": "huc8", "rightValue": "10"}
                    ),
                )
            )
            Map.addLayer(huc8.style(**{"fillColor": "00000000"}), {}, "NHD-HUC8")

        if "NHD-HUC10" in selected:
            huc10 = ee.FeatureCollection("USGS/WBD/2017/HUC10").filter(
                ee.Filter.Or(
                    ee.Filter.stringStartsWith(
                        **{"leftField": "huc10", "rightValue": "05"}
                    ),
                    ee.Filter.stringStartsWith(
                        **{"leftField": "huc10", "rightValue": "07"}
                    ),
                    ee.Filter.stringStartsWith(
                        **{"leftField": "huc10", "rightValue": "10"}
                    ),
                )
            )
            Map.addLayer(huc10.style(**{"fillColor": "00000000"}), {}, "NHD-HUC10")

    Map.addLayer(roi.style(**style), {}, "MRB")
    Map.to_streamlit(width=1400, height=650)
