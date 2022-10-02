import streamlit as st
from streamlit_option_menu import option_menu
from apps import home, datasets, split  # import your app modules here

st.set_page_config(
    page_title="Global Surface Water Information System (GSWIS)", layout="wide"
)

# A dictionary of apps in the format of {"App title": "App icon"}
# More icons can be found here: https://icons.getbootstrap.com

apps = [
    {"func": home.app, "title": "Home", "icon": "house"},
    {"func": datasets.app, "title": "Datasets", "icon": "map"},
    {"func": split.app, "title": "Split-panel Map", "icon": "layout-split"},
]

titles = [app["title"] for app in apps]
titles_lower = [title.lower() for title in titles]
icons = [app["icon"] for app in apps]

params = st.experimental_get_query_params()

if "page" in params:
    default_index = int(titles_lower.index(params["page"][0].lower()))
else:
    default_index = 0

with st.sidebar:
    selected = option_menu(
        "Main Menu",
        options=titles,
        icons=icons,
        menu_icon="cast",
        default_index=default_index,
    )

    st.sidebar.title("Suggested Citations")

    markdown = """
    
    - Khare, A., Rajib, A., Zheng, Q., Golden, H., Wu. Q., Lane, C., Christensen, J., Dahl., T., Ryder, J., McFall, B., 2022. **Global Surface Water Estimates: Critical Need for Data Consistency and Integration** (under peer-review).
    - Khare, A., Wu. Q., Rajib, A., Golden, H., Lane, C., Christensen, J., Dahl., T., Ryder, J., McFall, B., 2022. [**Global Surface Water Information System (GSWIS)**](https://gswis.gishub.org). Latest update: October 1, 2022.
    - Rajib, A. Khare, A., 2022. [**Surface Water Extent Estimates of the United States (version 1)**](https://www.hydroshare.org/resource/a6906817453741c8b8fea4011d224cd2). HydroShare resource. Latest update: October 1, 2022.
    
    """
    st.sidebar.info(markdown)

for app in apps:
    if app["title"] == selected:
        app["func"]()
        break
