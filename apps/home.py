import streamlit as st
import leafmap.foliumap as leafmap


def app():
    st.title("Global Surface Water Information System (GSWIS)")

    st.markdown(
        """
    The Global Surface Water Information System (GSWIS) brings the emerging regional and global datasets of surface water under one platform. 
    This global platform allows users to instantaneously visualize and compare different datasets, understand their variations, and therefore 
    select datasets that are most suitable for a specific research, management, or policy decision.

    """
    )
    st.image("https://i.imgur.com/7eyMcZQ.gif")

    # m = leafmap.Map(locate_control=True)
    # m.add_basemap("ROADMAP")
    # m.to_streamlit(height=700)
