import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px

from utils import load_micro_area_scores

st.set_page_config(page_title="Micro-Area Literacy Score", page_icon="🧮", layout="wide")
st.title("Micro-Area Literacy Score Map")

st.markdown(
    """
    Each zip code can be scored based on how badly help is needed, how accessible help is, and whether this help can improve.
    Three zip codes (university/military, non-residential) are excluded from
    scoring and shown separately with a data-quality flag.
    """
)

df = load_micro_area_scores()
scored = df[df["literacy_score"].notna()].copy()
excluded = df[df["literacy_score"].isna()].copy()

st.sidebar.header("Filters")
score_range = st.sidebar.slider(
    "Literacy score range",
    float(scored["literacy_score"].min()), float(scored["literacy_score"].max()),
    (float(scored["literacy_score"].min()), float(scored["literacy_score"].max())),
)
trend_filter = st.sidebar.multiselect(
    "Trend category", sorted(scored["trend_category"].dropna().unique()),
    default=sorted(scored["trend_category"].dropna().unique()),
)

view = scored[
    scored["literacy_score"].between(*score_range)
    & scored["trend_category"].isin(trend_filter)
]

# ---- Map ----
st.subheader("Composite score map")
fig = go.Figure(
    go.Scattermap(
        lat=view["lat"], lon=view["lon"],
        mode="markers",
        marker=dict(
            size=16,
            color=view["literacy_score"],
            colorscale="RdYlGn",
            cmin=scored["literacy_score"].min(),
            cmax=scored["literacy_score"].max(),
            colorbar=dict(title="Literacy score (0-100)"),
        ),
        text=view.apply(
            lambda r: f"Zip {r['zip_code']}<br>Score: {r['literacy_score']:.1f}"
            f"<br>Need severity: {r['need_severity_score']:.2f}"
            f"<br>Service access: {r['service_access_score']:.2f}"
            f"<br>Trend: {r['trend_category']} ({r['trend_direction_score']:.2f})",
            axis=1,
        ),
        hoverinfo="text",
    )
)
fig.update_layout(
    map=dict(style="open-street-map", center=dict(lat=32.85, lon=-116.9), zoom=8.3),
    height=600, margin=dict(l=0, r=0, t=0, b=0),
)
st.plotly_chart(fig, use_container_width=True)

# ---- Sub-score breakdown for a selected zip ----
st.subheader("Sub-score Breakdown For a Selected Zip")
zip_choice = st.selectbox("Zip code", sorted(view["zip_code"].tolist()))
row = view[view["zip_code"] == zip_choice].iloc[0]

col1, col2, col3 = st.columns(3)
col1.metric("Need Severity", f"{row['need_severity_score']:.2f}")
col2.metric("Service Access", f"{row['service_access_score']:.2f}")
col3.metric("Trend Direction", f"{row['trend_direction_score']:.2f}")

breakdown = pd.DataFrame({
    "Component": [
        "Literacy need", "Demographic risk",
        "Library proximity", "Library density", "Library access", "Program accessibility",
        "Trend direction",
    ],
    "Sub-score group": [
        "Need Severity", "Need Severity",
        "Service Access", "Service Access", "Service Access", "Service Access",
        "Trend Direction",
    ],
    "Value": [
        row["literacy_need_score"], row["demographic_risk_score"],
        row["library_proximity_score"], row["library_density_score"],
        row["library_access_score"], row["accessibility_score_all_programs"],
        row["trend_direction_score"],
    ],
})
fig_bar = px.bar(
    breakdown, x="Component", y="Value", color="Sub-score group",
    height=400,
)
fig_bar.update_layout(xaxis_tickangle=-30)
st.plotly_chart(fig_bar, use_container_width=True)
st.metric(f"Composite Literacy Score — Zip {zip_choice}", f"{row['literacy_score']:.1f} / 100")

# ---- Excluded zips note ----
if not excluded.empty:
    with st.expander(f"{len(excluded)} zip codes excluded from scoring (institutional/non-residential)"):
        st.dataframe(excluded[["zip_code", "data_quality_flag"]], use_container_width=True)

# ---- Table + download ----
st.subheader("Full Scored Data")
table_cols = [
    "zip_code", "literacy_score", "need_severity_score", "service_access_score",
    "trend_direction_score", "trend_category",
]
st.dataframe(view[table_cols].sort_values("literacy_score", ascending=False), use_container_width=True)

csv = df.to_csv(index=False).encode("utf-8")
st.download_button(
    "Download full Micro-Area Score data (incl. excluded zips) as CSV",
    data=csv,
    file_name="Literacy_MicroArea_Scores_export.csv",
    mime="text/csv",
)

st.caption(f"Showing {len(view)} of {len(scored)} scored zip codes.")
