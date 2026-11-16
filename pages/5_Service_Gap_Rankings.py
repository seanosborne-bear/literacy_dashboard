import streamlit as st
import pandas as pd
import plotly.express as px

from utils import load_service_gap_rankings

st.set_page_config(page_title="Service Gap Rankings", page_icon="📋", layout="wide")
st.title("Service Gap Rankings")

st.markdown(
    """
    Zip codes ranked by service gap severity. This can be filtered by literacy level,
    program type, and affiliation. Higher gap ratio / severity = greater need that isn't being met.

    **Note:** most San Diego County zip codes (87 of 114) have zero literacy programs located
    in them at all. For those zip codes, "gap ratio" (demand ÷ programs) is mathematically
    undefined rather than zero, so they're labeled **"No programs"** instead of showing a blank bar.
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

metric_col_map = {
    "Level 1": "demand_level1",
    "Level 2": "demand_level2",
    "Level 3": "demand_level3",
    "Overall severity": "severity_score",
}
metric_label_map = {
    "Level 1": "Level 1 demand (unmet need)",
    "Level 2": "Level 2 demand (unmet need)",
    "Level 3": "Level 3 demand (unmet need)",
    "Overall severity": "Severity score",
}
rank_col = rank_col_map[level_rank_choice]
metric_col = metric_col_map[level_rank_choice]
metric_label = metric_label_map[level_rank_choice]

program_type_choice = st.sidebar.selectbox(
    "Program type gap ratio to display", ["All programs (overall)"] + PROGRAM_TYPES
)
affiliation_choice = st.sidebar.radio(
    "Gap ratio basis", ["All programs", "Affiliated only"]
)
gap_col = "gap_ratio_all" if affiliation_choice == "All programs" else "gap_ratio_affiliated"

zero_program_only = st.sidebar.checkbox("Show only zips with zero programs", value=False)

view = df.copy()
if zero_program_only:
    view = view[view["has_zero_programs"] == True]  # noqa: E712

view = view.sort_values(rank_col)

st.subheader(f"Top 20 zip codes by {level_rank_choice} rank")
top20 = view.head(20).sort_values(metric_col, ascending=True)
fig = px.bar(
    top20,
    x=metric_col,
    y="zip_code",
    orientation="h",
    color="program_count_total",
    color_continuous_scale="Reds_r",
    labels={
        metric_col: metric_label,
        "zip_code": "Zip code",
        "program_count_total": "Total programs in zip",
    },
    height=600,
)
fig.update_layout(bargap=0.1, xaxis_title=f"{metric_label} (higher = greater unmet need)")
fig.update_yaxes(type="category")
st.plotly_chart(fig, use_container_width=True)

if program_type_choice != "All programs (overall)":
    st.subheader(f"Gap ratio for {program_type_choice.replace('_', ' ')} programs")
    pt_gap_col = f"gap_ratio_{program_type_choice}"
    pt_rank_col = f"gap_rank_{program_type_choice}"
    if pt_gap_col in view.columns:
        pt_view = view.sort_values(pt_rank_col).head(20).copy()
        n_undefined = pt_view[pt_gap_col].isna().sum()
        pt_view["gap_display"] = pt_view[pt_gap_col]
        pt_view["gap_label"] = pt_view.apply(
            lambda r: "No programs" if pd.isna(r[pt_gap_col]) else f"{r[pt_gap_col]:.2f}",
            axis=1,
        )
        # plot defined values; zero-program zips are called out separately below
        plot_view = pt_view[pt_view[pt_gap_col].notna()].sort_values(pt_gap_col, ascending=True)
        if not plot_view.empty:
            fig2 = px.bar(
                plot_view,
                x=pt_gap_col, y="zip_code", orientation="h",
                labels={pt_gap_col: "Gap ratio (higher = more unmet need)", "zip_code": "Zip code"},
                height=550,
            )
            fig2.update_yaxes(type="category")
            st.plotly_chart(fig2, use_container_width=True)
        if n_undefined:
            no_program_zips = pt_view[pt_view[pt_gap_col].isna()]["zip_code"].tolist()
            st.caption(
                f"{n_undefined} of these top 20 zip codes have zero programs of this type, "
                f"so their gap ratio is undefined rather than zero: {', '.join(no_program_zips)}."
            )
    else:
        st.info("No gap ratio column found for this program type.")

# ---- Table + download ----
st.subheader("Full Table")
table_cols = [
    "zip_code", "severity_rank", "severity_score", "rank_by_level1", "rank_by_level2", "rank_by_level3",
    "demand_supply_ratio", "program_count_total", "program_count_affiliated", "program_count_independent",
    "has_zero_programs", gap_col,
]
display_table = view[table_cols].rename(columns={
    "severity_rank": "Severity rank",
    "severity_score": "Severity score",
    "rank_by_level1": "Rank (Level 1)",
    "rank_by_level2": "Rank (Level 2)",
    "rank_by_level3": "Rank (Level 3)",
    "demand_supply_ratio": "Demand ÷ supply ratio",
    "program_count_total": "Total programs",
    "program_count_affiliated": "Affiliated programs",
    "program_count_independent": "Independent programs",
    "has_zero_programs": "Zero programs?",
    gap_col: "Gap ratio",
})
st.dataframe(display_table, use_container_width=True)

csv = view.to_csv(index=False).encode("utf-8")
st.download_button(
    "Download full service gap rankings as CSV",
    data=csv,
    file_name="service_gap_rankings_filtered.csv",
    mime="text/csv",
)

st.caption(f"Showing {len(view)} of {len(df)} zip codes.")
