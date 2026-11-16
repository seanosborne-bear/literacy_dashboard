import streamlit as st

from utils import load_hotspots, load_service_gap_rankings, load_programs

st.set_page_config(
    page_title="San Diego County Literacy Service Gap Dashboard",
    page_icon="📚",
    layout="wide",
)

st.title("San Diego County Literacy Service Gap Dashboard")

st.markdown(
    """
    This dashboard looks at every zip code across San Diego County to examine their need for literacy assistance,
    access to said assistance, and how well existing programs cover that need.
    """
)

# ---- Headline stats ----
hotspots = load_hotspots()
rankings = load_service_gap_rankings()
programs = load_programs()

total_zips = len(hotspots)
high_need_zips = (hotspots["hotspot_tier"] == "High need (clustered hotspot)").sum()
zero_program_zips = int(rankings["has_zero_programs"].sum())
total_programs = len(programs)

c1, c2, c3, c4 = st.columns(4)
c1.metric("Zip codes covered", total_zips)
c2.metric("High-need zip codes", high_need_zips)
c3.metric("Zip codes with zero programs", zero_program_zips)
c4.metric("Programs in directory", total_programs)

st.markdown(
    """
    **Start here:** the Service Gap Rankings page shows which zip codes have the
    biggest mismatch between literacy need and available programs — that's the
    fastest way to see where help is most urgently needed.

    **The rest of the pages can be found in the sidebar:**

    - **Hotspot Map**: Where in San Diego is literacy help needed most?
    - **Literacy Rates by Zip**: How do literacy levels compare across each zip code?
    - **Temporal Trends**: How have literacy rates changed from 2017 to 2023?
    - **Accessibility & Transit**: How difficult is it to reach a literacy center? Includes transit routes.
    - **Service Gap Rankings**: What zip codes most need help but lack sufficient programs to help them?
    - **Micro-Area Literacy Score**: How would we generally compare how well catered each zip code is?
    - **Program Directory**: What programs are available?
    - **About**: About this dashboard, including methodology and data sources
    """
)
