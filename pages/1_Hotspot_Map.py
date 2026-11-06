import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

from utils import load_hotspots, load_programs

st.set_page_config(page_title="Hotspot Map", page_icon="🗺️", layout="wide")
st.title("Hotspot Map with Service Location Overlay")

st.markdown(
    """
    For every zip code in San Diego County, this visual displays a bubble to showcase how necessary literacy help should be provided. The bigger the bubble, the more necessary help should be provided.

    *Note: a true zip-boundary choropleth needs the TIGER/Line zip boundary
    shapefile, which hasn't been provided yet (too large to upload). This view
    uses zip-code centroid points instead — switch to a filled-boundary map once
    that shapefile is available.*
    """
)

hotspots = load_hotspots()
programs = load_programs()

# ---- Sidebar filters ----
st.sidebar.header("Filters")

tier_options = sorted(hotspots["hotspot_tier"].dropna().unique())
selected_tiers = st.sidebar.multiselect(
    "Hotspot tier", tier_options, default=tier_options
)

affiliation_toggle = st.sidebar.radio(
    "Show programs",
    ["All programs", "Affiliated only", "Independent only", "None"],
    index=0,
)

min_programs, max_programs = int(hotspots["program_count"].min()), int(hotspots["program_count"].max())
program_count_range = st.sidebar.slider(
    "Zip-level program count range", min_programs, max_programs, (min_programs, max_programs)
)

filtered = hotspots[
    hotspots["hotspot_tier"].isin(selected_tiers)
    & hotspots["program_count"].between(*program_count_range)
].copy()

# ---- Map ----
tier_colors = {
    "High need (clustered hotspot)": "#d62728",
    "Medium need (isolated high-need)": "#ff7f0e",
    "Low need": "#2ca02c",
}

fig = go.Figure()

for tier in tier_options:
    sub = filtered[filtered["hotspot_tier"] == tier]
    if sub.empty:
        continue
    fig.add_trace(
        go.Scattermap(
            lat=sub["lat"],
            lon=sub["lon"],
            mode="markers",
            marker=dict(
                size=(sub["Lit_P1"].fillna(0) * 40 + 10),
                color=tier_colors.get(tier, "#888"),
                opacity=0.65,
            ),
            name=tier,
            text=sub.apply(
                lambda r: f"Zip {r['zip_code']}<br>Tier: {r['hotspot_tier']}"
                f"<br>Lit P1 need rate: {r['Lit_P1']:.2f}"
                f"<br>Programs in zip: {int(r['program_count'])}"
                f"<br>Trend: {r['trend_category']}",
                axis=1,
            ),
            hoverinfo="text",
        )
    )

if affiliation_toggle != "None":
    if affiliation_toggle == "All programs":
        prog_sub = programs
    elif affiliation_toggle == "Affiliated only":
        prog_sub = programs[programs["affiliation"] == "Affiliated"]
    else:
        prog_sub = programs[programs["affiliation"] == "Independent"]

    fig.add_trace(
        go.Scattermap(
            lat=prog_sub["Latitude"],
            lon=prog_sub["Longitude"],
            mode="markers",
            marker=dict(size=10, color="#1f77b4", symbol="circle"),
            name=f"Programs ({affiliation_toggle})",
            text=prog_sub.apply(
                lambda r: f"{r['Name']}<br>{r.get('Program Type', '')}"
                f"<br>Affiliation: {r['affiliation']}"
                f"<br>{r.get('Address', '')}",
                axis=1,
            ),
            hoverinfo="text",
            marker_symbol="circle",
        )
    )

fig.update_layout(
    map=dict(
        style="open-street-map",
        center=dict(lat=32.85, lon=-116.9),
        zoom=8.3,
    ),
    height=650,
    margin=dict(l=0, r=0, t=0, b=0),
    legend=dict(orientation="h", y=-0.05),
)

st.plotly_chart(fig, use_container_width=True)

# ---- Summary table + download ----
st.subheader("Filtered Data")
display_cols = [
    "zip_code", "hotspot_tier", "Lit_P1", "Lit_P2_pred", "Lit_P3_pred",
    "trend_category", "program_count", "programs_per_10k_adults",
]
st.dataframe(filtered[display_cols].sort_values("Lit_P1", ascending=False), use_container_width=True)

csv = filtered[display_cols].to_csv(index=False).encode("utf-8")
st.download_button(
    "Download filtered hotspot data as CSV",
    data=csv,
    file_name="hotspot_map_filtered.csv",
    mime="text/csv",
)

st.caption(f"Showing {len(filtered)} of {len(hotspots)} zip codes.")
