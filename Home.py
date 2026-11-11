import streamlit as st

st.set_page_config(
    page_title="San Diego County Literacy Service Gap Dashboard",
    page_icon="📚",
    layout="wide",
)

st.title("San Diego County Literacy Service Gap Dashboard")

st.markdown(
    """
    This dashboard different zip codes across San Diego County to examine their need for literacy assistance, 
    access to said assistance, and how programs for it cover these codes.

    **The related pages can be found below:**

    - **Hotspot Map**: Where in San Diego is literacy help needed most?
    - **Literacy Rates by Zip**: How do literacy levels compare across each zip code?
    - **Temporal Trends**: How have literacy rates changed from 2017 to 2023?
    - **Accessibility & Transit**: How difficult is it to reach a literacy center? Includes transit routes.
    - **Service Gap Rankings**: What zip codes most need help but lack sufficient programs to help them?
    - **Micro-Area Literacy Score**: How would we generally compare how well catered each zip code is?
    - **Program Directory**: What programs are available?
    - **About**: About this dasboard

    Use the page list in the left sidebar to explore.
    """
)

st.info("Component 1 (Hotspot Map) is live — open it from the sidebar. More components are being added incrementally.")
