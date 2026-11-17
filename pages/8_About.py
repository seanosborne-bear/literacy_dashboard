import streamlit as st

st.set_page_config(page_title="Methodology / About", page_icon="ℹ️", layout="wide")
st.title("About This Dashboard")

st.markdown(
    """
    This dashboard supports the **DSA Literacy Service Gap** volunteer analytics
    project for San Diego County, with the goal of mapping literacy need against program
    accessibility to identify under-served micro-areas (zip codes).
    """
)

# ---- Data Sources ----
st.subheader("Data Sources")

data_sources = [
    ("📊 ACS / Census Estimates", "Population, income, housing, employment, and SNAP indicators used to model literacy need and demographic risk"),
    ("📖 Predicted Literacy Levels", "Modeled shares of adults at each literacy level (Level 1, 2, 3) by zip code"),
    ("🏢 Program Directories", "Affiliated and independent literacy, ESL, family literacy, and early-childhood programs, geocoded to lat/lon"),
    ("📚 Library Locations", "San Diego County Library branches, used for library-based access scoring"),
    ("🚌 MTS Transit Feed (GTFS)", "Stop locations and route coverage, used for the accessibility and transit layer"),
    ("📈 2017–2023 Panel Data", "Year-by-year adult low-literacy rate estimates, used for the temporal trend view"),
]

cols = st.columns(3)
for i, (name, desc) in enumerate(data_sources):
    with cols[i % 3]:
        with st.container(border=True):
            st.markdown(f"**{name}**")
            st.caption(desc)

# ---- Scoring Methodology ----
st.subheader("Scoring Methodology")

with st.container(border=True):
    st.markdown(
        """
        The **Micro-Area Literacy Score** (0–100) is built per the project's specifications:

        1. Every component is normalized with min-max scaling to [0, 1], inverted
           where needed so that **higher always means better for the community**.
        2. Three sub-scores are built, each an equal-weighted average of their inputs:
           - **Need Severity** = 0.5 × literacy need + 0.5 × demographic risk
           - **Service Access** = 0.5 × library access + 0.5 × program accessibility
           - **Trend Direction** = mapped from the 2017→2023 trend category
             (persistent high-need / emerging problem = 0.0, insufficient data = 0.5,
             improving = 0.67, consistently low-need = 1.0)
        3. The composite score is the equal-weighted average of all three sub-scores,
           scaled to 0–100.
        """
    )

col1, col2 = st.columns(2)
with col1:
    with st.container(border=True):
        st.markdown("**Excluded Zip Codes**")
        st.caption(
            "Three zip codes have no adult population in the database and don't receive a "
            "score: Cal State San Marcos (92096), Naval Base San Diego (92132), and San Diego "
            "State University (92182). Including them would distort the min-max normalization "
            "for every other zip, but they still appear on the map."
        )
with col2:
    with st.container(border=True):
        st.markdown("**Sensitivity Analysis**")
        st.caption(
            "Tested the equal-weighting baseline against 4 alternative weighting schemes. "
            "Rank correlations against the baseline ranged 0.98–1.00 (Spearman); the composite "
            "score correlated at -0.76 with observed low-literacy rate (expected direction, "
            "moderately strong) — the scoring approach is reasonably robust to weighting choice."
        )

# ---- Known Limitations ----
st.subheader("Known Limitations")

limitations = [
    ("🗺️ No Filled Zip Boundaries", "Maps use zip-code centroid points, not filled polygons — the TIGER/Line ZCTA shapefile needed for true choropleth maps was too large to bring into this environment."),
    ("🔮 Modeled, Not Observed", "Level 2 and Level 3 literacy rates (Lit_P2_pred, Lit_P3_pred) are model predictions, not directly observed."),
    ("🔁 Partial Circularity", "The outcome correlation check uses adult_low_literacy_rate, which isn't fully independent of the Level 1 input in Need Severity — read it as a consistency check, not full external validation."),
    ("🔢 Minor Count Discrepancy", "Programs_affiliated.csv lists 35 programs; the original project brief referenced 34 — likely a minor discrepancy, worth a final check against the source list."),
]

cols = st.columns(2)
for i, (name, desc) in enumerate(limitations):
    with cols[i % 2]:
        with st.container(border=True):
            st.markdown(f"**{name}**")
            st.caption(desc)

# ---- Navigation ----
st.subheader("Navigation")
st.markdown(
    "Use the sidebar to move between the hotspot map, literacy rate breakdowns, "
    "temporal trends, accessibility/transit, service gap rankings, the composite "
    "score map, and the program directory."
)
