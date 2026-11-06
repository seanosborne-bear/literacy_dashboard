import streamlit as st
import pandas as pd
import plotly.express as px

from utils import load_zip_estimates

st.set_page_config(page_title="Literacy Rates by Zip", page_icon="📊", layout="wide")
st.title("Literacy Rates by Zip Code Across All Levels")

st.markdown(
    """
    Each zip code's population is spread across three levels of literacy:

    - **Level 1**: Predicted to have below basic literacy
    - **Level 2**: Predicted to have literacy between basic and moderate
    - **Level 3**: Preedicted to have moderate to proficient fluency
    """
)

df = load_zip_estimates()

# exclude institutional/non-residential zips (adult_population == 0) from ranked views,
# consistent with the Micro-Area Score methodology, but keep them visible with a flag
df["is_institutional"] = df["adult_population"] == 0

st.sidebar.header("Filters")
level_choice = st.sidebar.multiselect(
    "Literacy level(s) to display",
    ["Level 1", "Level 2", "Level 3"],
    default=["Level 1", "Level 2", "Level 3"],
)
show_institutional = st.sidebar.checkbox(
    "Include institutional/non-residential zips (e.g. universities, military base)",
    value=False,
)
sort_by = st.sidebar.selectbox("Sort zip table by", ["Level 1", "Level 2", "Level 3", "Zip code"])

view = df if show_institutional else df[~df["is_institutional"]]

level_map = {"Level 1": "Lit_P1", "Level 2": "Lit_P2_pred", "Level 3": "Lit_P3_pred"}
cols_to_plot = [level_map[l] for l in level_choice]

# ---- Bar comparison across zips ----
st.subheader("Literacy level rates by zip code")

melted = view.melt(
    id_vars=["zip_code", "name"],
    value_vars=cols_to_plot,
    var_name="level_col",
    value_name="rate",
)
inv_map = {v: k for k, v in level_map.items()}
melted["Level"] = melted["level_col"].map(inv_map)

sort_col = level_map.get(sort_by, "zip_code")
zip_order = (
    view.sort_values(sort_col, ascending=False)["zip_code"].tolist()
    if sort_by != "Zip code"
    else sorted(view["zip_code"].tolist())
)

fig = px.bar(
    melted,
    x="zip_code",
    y="rate",
    color="Level",
    barmode="group",
    category_orders={"zip_code": zip_order},
    labels={"rate": "Share of adult population", "zip_code": "Zip code"},
    height=550,
)
fig.update_layout(xaxis_tickangle=-60, bargap=0.05, bargroupgap=0.02)
fig.update_xaxes(type="category")
st.plotly_chart(fig, use_container_width=True)

# ---- Scatter: level 1 vs level 3 as a quick "need vs strength" view ----
st.subheader("Level 1 Need vs. Level 3 Proficiency by Zip Code")
fig2 = px.scatter(
    view,
    x="Lit_P1",
    y="Lit_P3_pred",
    size="adult_population",
    color="median_household_income",
    hover_name="zip_code",
    labels={
        "Lit_P1": "Level 1 (low literacy) rate",
        "Lit_P3_pred": "Level 3 (proficient) rate",
        "median_household_income": "Median household income",
    },
    color_continuous_scale="Viridis",
    height=500,
)
st.plotly_chart(fig2, use_container_width=True)

# ---- Table + download ----
st.subheader("Data")
table_cols = ["zip_code", "name", "adult_population", "Lit_P1", "Lit_P2_pred", "Lit_P3_pred", "is_institutional"]
st.dataframe(view[table_cols].sort_values(sort_col, ascending=False), use_container_width=True)

csv = view[table_cols].to_csv(index=False).encode("utf-8")
st.download_button(
    "Download literacy rates as CSV",
    data=csv,
    file_name="literacy_rates_by_zip.csv",
    mime="text/csv",
)

st.caption(f"Showing {len(view)} of {len(df)} zip codes" + (" (institutional zips excluded)" if not show_institutional else ""))
