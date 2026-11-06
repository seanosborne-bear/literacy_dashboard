import streamlit as st
import pandas as pd
import plotly.graph_objects as go

from utils import load_transit_accessibility, load_hotspots, load_gtfs_stops

st.set_page_config(page_title="Accessibility & Transit", page_icon="🚌", layout="wide")
st.title("Accessibility Analysis with Transit Layer")

st.markdown(
    """
    For each zip code, how easy is it for people in it to reach a literacy program? The San Diego MTS transit routes are overlayed for reference. 
    The higher the score, the better catered the zip code.
    """
)

access = load_transit_accessibility()
hotspots = load_hotspots()[["zip_code", "lat", "lon", "hotspot_tier"]]
access = access.merge(hotspots, on="zip_code", how="left")
stops = load_gtfs_stops()

st.sidebar.header("Filters")
score_type = st.sidebar.radio(
    "Accessibility score to map",
    ["All programs", "Affiliated programs only"],
)
score_col = "accessibility_score_all_programs" if score_type == "All programs" else "accessibility_score_affiliated"

min_score, max_score = float(access[score_col].min()), float(access[score_col].max())
threshold = st.sidebar.slider(
    "Minimum accessibility score (filter out zips below this)",
    min_value=0.0, max_value=round(max_score, 3), value=0.0, step=0.001,
)
show_transit = st.sidebar.checkbox("Show transit stops layer", value=True)

filtered = access[access[score_col] >= threshold]

fig = go.Figure()

fig.add_trace(
    go.Scattermap(
        lat=filtered["lat"],
        lon=filtered["lon"],
        mode="markers",
        marker=dict(
            size=14,
            color=filtered[score_col],
            colorscale="RdYlGn",
            cmin=min_score,
            cmax=max_score,
            colorbar=dict(title="Accessibility score"),
        ),
        name="Zip accessibility",
        text=filtered.apply(
            lambda r: f"Zip {r['zip_code']}<br>Hotspot tier: {r['hotspot_tier']}"
            f"<br>Accessibility ({score_type}): {r[score_col]:.4f}"
            f"<br>Walk to nearest stop: {r['walk_to_stop_minutes']:.1f} min"
            f"<br>Travel time to programs: {r['travel_min_affiliated' if score_type=='Affiliated programs only' else 'travel_min_all_programs']:.1f} min",
            axis=1,
        ),
        hoverinfo="text",
    )
)

if show_transit:
    fig.add_trace(
        go.Scattermap(
            lat=stops["stop_lat"],
            lon=stops["stop_lon"],
            mode="markers",
            marker=dict(size=2, color="#888888", opacity=0.25),
            name="Transit stops (MTS)",
            text=stops["stop_name"],
            hoverinfo="text",
        )
    )

fig.update_layout(
    map=dict(style="open-street-map", center=dict(lat=32.85, lon=-116.9), zoom=8.3),
    height=650,
    margin=dict(l=0, r=0, t=0, b=0),
    legend=dict(orientation="h", y=-0.05),
)
st.plotly_chart(fig, use_container_width=True)

# ---- Table + download ----
st.subheader("Accessibility Data")
table_cols = [
    "zip_code", "hotspot_tier", "walk_to_stop_minutes", "nearest_stop_headway_min",
    "coverage_stop_count", "travel_min_affiliated", "travel_min_all_programs",
    "accessibility_score_affiliated", "accessibility_score_all_programs",
]
st.dataframe(filtered[table_cols].sort_values(score_col, ascending=False), use_container_width=True)

csv = filtered[table_cols].to_csv(index=False).encode("utf-8")
st.download_button(
    "Download accessibility data as CSV",
    data=csv,
    file_name="accessibility_transit_filtered.csv",
    mime="text/csv",
)

st.caption(
    f"Showing {len(filtered)} of {len(access)} zip codes. Transit layer: {len(stops)} MTS stops "
    "(bus, trolley, ferry) from GTFS stops.txt."
)
