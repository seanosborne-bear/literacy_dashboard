import streamlit as st

st.set_page_config(
    page_title="San Diego County Literacy Service Gap Dashboard",
    page_icon="📚",
    layout="wide",
)

st.title("San Diego County Literacy Service Gap Dashboard")

st.markdown(
    """
    This dashboard examines literacy need, service access, and program coverage
    across various San Diego County zip codes.

    **Use the sidebar to navigate between pages]:**

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
