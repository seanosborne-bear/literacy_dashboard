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

st.subheader("**Where Should I Start?**")

st.markdown(
    """
    The Service Gap Rankings page shows which zip codes have the
    biggest mismatch between literacy need and available programs — that's the
    fastest way to see where help is most urgently needed."""
)

st.subheader("Pages")

page_info = [
    ("🗺️ Hotspot Map", "Where in San Diego is literacy help needed most?"),
    ("📊 Literacy Rates by Zip", "How do literacy levels compare across each zip code?"),
    ("📈 Temporal Trends", "How have literacy rates changed from 2017 to 2023?"),
    ("🚌 Accessibility & Transit", "How difficult is it to reach a literacy center?"),
    ("📋 Service Gap Rankings", "What zip codes most need help but lack programs?"),
    ("🧮 Micro-Area Score", "How well catered is each zip code, overall?"),
    ("🔎 Program Directory", "What programs are available?"),
    ("ℹ️ About", "Methodology, data sources, and limitations."),
]

cols = st.columns(4)
for i, (name, desc) in enumerate(page_info):
    with cols[i % 4]:
        with st.container(border=True):
            st.markdown(f"**{name}**")
            st.caption(desc)
