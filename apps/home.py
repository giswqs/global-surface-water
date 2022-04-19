import streamlit as st
import leafmap.foliumap as leafmap


def app():
    st.title("Home")

    st.markdown(
        """
    Select **Datasets** from the Main Menu to explore global surface water datasets interatively.

    """
    )
    st.image("https://i.imgur.com/KVRvlwM.png")

    # m = leafmap.Map(locate_control=True)
    # m.add_basemap("ROADMAP")
    # m.to_streamlit(height=700)
