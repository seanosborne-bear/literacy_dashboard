import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

from utils import load_level1_panel, zip_centroids

st.set_page_config(page_title="Temporal Trends", page_icon="📈", layout="wide")
st.title("Literacy Rate Changes Over Time")

panel = load_level1_panel()
years = sorted(panel["year"].unique())

st.sidebar.header("Filters")
selected_year = st.sidebar.slider(
    "Year", min_value=int(min(years)), max_value=int(max(years)), value=int(max(years)), step=1
)
zip_search = st.sidebar.text_input("Highlight a specific zip code (optional)")

st.markdown(
    f"For each zip code, this visual the low-literacy rate for adults. "
    "Drag the slider in the sidebar to see how rates evolved from 2017 to 2023."
)

year_df = panel[panel["year"] == selected_year].copy()
centroids = zip_centroids(year_df["zip_code"]).drop(columns=["city"])
year_df = year_df.merge(centroids, on="zip_code", how="left")

fig_map = go.Figure(
    go.Scattermap(
        lat=year_df["lat"],
        lon=year_df["lon"],
        mode="markers",
        marker=dict(
            size=12,
            color=year_df["adult_low_literacy_rate"],
            colorscale="OrRd",
            cmin=panel["adult_low_literacy_rate"].min(),
            cmax=panel["adult_low_literacy_rate"].max(),
            colorbar=dict(title="Low-literacy rate"),
        ),
        text=year_df.apply(
            lambda r: f"Zip {r['zip_code']} ({r['city']})<br>Year {r['year']}<br>Rate: {r['adult_low_literacy_rate']:.3f}",
            axis=1,
        ),
        hoverinfo="text",
    )
)
fig_map.update_layout(
    map=dict(style="open-street-map", center=dict(lat=32.85, lon=-116.9), zoom=8.3),
    height=550,
    margin=dict(l=0, r=0, t=0, b=0),
)
st.plotly_chart(fig_map, use_container_width=True)

# ---- County-wide trend line ----
st.subheader("Average Low-Literacy Rate from 2017 to 2023")
county_trend = panel.groupby("year")["adult_low_literacy_rate"].mean().reset_index()
fig_trend = px.line(
    county_trend, x="year", y="adult_low_literacy_rate", markers=True,
    labels={"adult_low_literacy_rate": "Avg. low-literacy rate", "year": "Year"},
)
fig_trend.add_vline(x=selected_year, line_dash="dash", line_color="gray")
st.plotly_chart(fig_trend, use_container_width=True)

# ---- Per-zip trend, chosen zips only ----
st.subheader("Compare Zip Codes Over Time")

all_zips = sorted(panel["zip_code"].unique())
default_zips = (
    panel.groupby("zip_code")["adult_low_literacy_rate"].mean()
    .sort_values(ascending=False)
    .head(5)
    .index.tolist()
)

compare_zips = st.multiselect(
    "Select zip codes to compare rates. This defaults to the 5 highest-need zip codes.",
    all_zips,
    default=default_zips,
)

if zip_search:
    z = zip_search.strip().zfill(5)
    if z in all_zips and z not in compare_zips:
        compare_zips.append(z)
    elif z not in all_zips:
        st.warning(f"Zip code {z} not found in this dataset.")

fig_lines = go.Figure()

# faint shaded band showing the county-wide min-max range, for context
band = panel.groupby("year")["adult_low_literacy_rate"].agg(["min", "max"]).reset_index()
fig_lines.add_trace(go.Scatter(
    x=list(band["year"]) + list(band["year"][::-1]),
    y=list(band["max"]) + list(band["min"][::-1]),
    fill="toself", fillcolor="rgba(150,150,150,0.15)",
    line=dict(color="rgba(255,255,255,0)"),
    hoverinfo="skip", showlegend=True, name="County range (min-max)",
))

for z in compare_zips:
    sub = panel[panel["zip_code"] == z]
    fig_lines.add_trace(go.Scatter(
        x=sub["year"], y=sub["adult_low_literacy_rate"],
        mode="lines+markers", name=f"Zip {z}",
    ))

fig_lines.update_layout(height=450, xaxis_title="Year", yaxis_title="Low-literacy rate")
st.plotly_chart(fig_lines, use_container_width=True)

# ---- Table + download ----
st.subheader(f"Data for {selected_year}")
table_cols = ["zip_code", "city", "year", "adult_low_literacy_rate", "total_population", "median_income"]
st.dataframe(year_df[table_cols].sort_values("adult_low_literacy_rate", ascending=False), use_container_width=True)

csv = panel[table_cols].to_csv(index=False).encode("utf-8")
st.download_button(
    "Download full 2017–2023 panel as CSV",
    data=csv,
    file_name="literacy_rate_panel_2017_2023.csv",
    mime="text/csv",
)
