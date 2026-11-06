import streamlit as st
import pandas as pd
import plotly.express as px

from utils import load_service_gap_rankings

st.set_page_config(page_title="Service Gap Rankings", page_icon="📋", layout="wide")
st.title("Service Gap Rankings")

st.markdown(
    """
    Zip codes ranked by service gap severity. This can be filtered by literacy level,
    program type, and affiliation. The higher the severity ratio, the greater the need for assistance that isn't being met.
    """
)

df = load_service_gap_rankings()

PROGRAM_TYPES = ["Adult_Literacy", "ESL", "Early_Childhood", "Family_Literacy", "Multiple", "Does_Not_Fit"]

st.sidebar.header("Filters")

level_rank_choice = st.sidebar.selectbox(
    "Rank by literacy level", ["Level 1", "Level 2", "Level 3", "Overall severity"]
)
rank_col_map = {
    "Level 1": "rank_by_level1",
    "Level 2": "rank_by_level2",
    "Level 3": "rank_by_level3",
    "Overall severity": "severity_rank",
}
rank_col = rank_col_map[level_rank_choice]

program_type_choice = st.sidebar.selectbox(
    "Program type gap ratio to display", ["All programs (overall)"] + PROGRAM_TYPES
)
affiliation_choice = st.sidebar.radio(
    "Gap ratio basis", ["All programs", "Affiliated only"]
)
gap_col = "gap_ratio_all" if affiliation_choice == "All programs" else "gap_ratio_affiliated"

zero_program_only = st.sidebar.checkbox("Show only zips with zero programs (`has_zero_programs`)", value=False)

view = df.copy()
if zero_program_only:
    view = view[view["has_zero_programs"] == True]  # noqa: E712

view = view.sort_values(rank_col)

# ---- Top gap bar chart ----
st.subheader(f"Top 20 zip codes by {level_rank_choice} rank")
top20 = view.head(20)
fig = px.bar(
    top20.sort_values(rank_col, ascending=False),
    x="severity_score" if level_rank_choice == "Overall severity" else gap_col,
    y="zip_code",
    orientation="h",
    color="program_count_total",
    color_continuous_scale="Reds_r",
    labels={
        "severity_score": "Severity score",
        gap_col: "Gap ratio",
        "zip_code": "Zip code",
        "program_count_total": "Total programs in zip",
    },
    height=600,
)
fig.update_layout(bargap=0.1)
fig.update_yaxes(type="category")
st.plotly_chart(fig, use_container_width=True)

# ---- Program-type specific gap view ----
if program_type_choice != "All programs (overall)":
    st.subheader(f"Gap ratio for {program_type_choice.replace('_', ' ')} programs")
    pt_gap_col = f"gap_ratio_{program_type_choice}"
    pt_rank_col = f"gap_rank_{program_type_choice}"
    if pt_gap_col in view.columns:
        pt_view = view.sort_values(pt_rank_col).head(20)
        fig2 = px.bar(
            pt_view.sort_values(pt_rank_col, ascending=False),
            x=pt_gap_col, y="zip_code", orientation="h",
            labels={pt_gap_col: "Gap ratio", "zip_code": "Zip code"},
            height=550,
        )
        st.plotly_chart(fig2, use_container_width=True)
    else:
        st.info("No gap ratio column found for this program type.")

# ---- Table + download ----
st.subheader("Full Table")
table_cols = [
    "zip_code", "severity_rank", "severity_score", "rank_by_level1", "rank_by_level2", "rank_by_level3",
    "demand_supply_ratio", "program_count_total", "program_count_affiliated", "program_count_independent",
    "has_zero_programs", gap_col,
]
st.dataframe(view[table_cols], use_container_width=True)

csv = view.to_csv(index=False).encode("utf-8")
st.download_button(
    "Download full service gap rankings as CSV",
    data=csv,
    file_name="service_gap_rankings_filtered.csv",
    mime="text/csv",
)

st.caption(f"Showing {len(view)} of {len(df)} zip codes.")
