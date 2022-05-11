import ee
import geemap.colormaps as cm
import geemap.foliumap as geemap

geemap.ee_initialize()


dem_vis = {"min": 0, "max": 4000, "palette": cm.get_palette("terrain", 15)}
landform_vis = {
    "min": 11,
    "max": 42,
    "palette": [
        "141414",
        "383838",
        "808080",
        "EBEB8F",
        "F7D311",
        "AA0000",
        "D89382",
        "DDC9C9",
        "DCCDCE",
        "1C6330",
        "68AA63",
        "B5C98E",
        "E1F0E5",
        "a975ba",
        "6f198c",
    ],
}
esri_vis = {
    "min": 1,
    "max": 10,
    "palette": list(geemap.builtin_legends["ESRI_LandCover"].values()),
}

DEMS = {
    "STRM": {"id": ee.Image("CGIAR/SRTM90_V4"), "vis": dem_vis},
    "NASA SRTM": {
        "id": ee.Image("USGS/SRTMGL1_003").select("elevation"),
        "vis": dem_vis,
    },
    "NASA DEM": {
        "id": ee.Image("NASA/NASADEM_HGT/001").select("elevation"),
        "vis": dem_vis,
    },
    "ASTER GDEM": {
        "id": ee.Image("projects/sat-io/open-datasets/ASTER/GDEM"),
        "vis": dem_vis,
    },
    "ALOS DEM": {
        "id": ee.ImageCollection("JAXA/ALOS/AW3D30/V3_2")
        .mosaic()
        .select("DSM")
        .rename("elevation"),
        "vis": dem_vis,
    },
    "GLO-30": {
        "id": ee.ImageCollection("projects/sat-io/open-datasets/GLO-30")
        .mosaic()
        .rename("elevation"),
        "vis": dem_vis,
    },
    "FABDEM": {
        "id": ee.ImageCollection("projects/sat-io/open-datasets/FABDEM")
        .mosaic()
        .rename("elevation"),
        "vis": dem_vis,
    },
    "NED": {
        "id": ee.Image("USGS/3DEP/10m"),
        "vis": dem_vis,
    },
}

LANDCOVERS = {
    "ESA WorldCover": {
        "id": ee.ImageCollection("ESA/WorldCover/v100").first(),
        "vis": {},
    },
    "ESRI Global Land Cover": {
        "id": ee.ImageCollection(
            "projects/sat-io/open-datasets/landcover/ESRI_Global-LULC_10m"
        ).mosaic(),
        "vis": esri_vis,
    },
    "NLCD 2019": {
        "id": ee.Image("USGS/NLCD_RELEASES/2019_REL/NLCD/2019").select("landcover"),
        "vis": {},
    },
}

LANDFORMS = {
    "Global ALOS Landforms": {
        "id": ee.Image("CSP/ERGo/1_0/Global/ALOS_landforms").select("constant"),
        "vis": landform_vis,
    },
    "Global SRTM Landforms": {
        "id": ee.Image("CSP/ERGo/1_0/Global/SRTM_landforms").select("constant"),
        "vis": landform_vis,
    },
    "NED Landforms": {
        "id": ee.Image("CSP/ERGo/1_0/US/landforms").select("constant"),
        "vis": landform_vis,
    },
}
