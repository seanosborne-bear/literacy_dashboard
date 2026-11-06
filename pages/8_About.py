import streamlit as st

st.set_page_config(page_title="Methodology / About", page_icon="ℹ️", layout="wide")
st.title("About This Dashboard")

st.markdown(
    """
    This dashboard supports the **DSA Literacy Service Gap** volunteer analytics
    project for San Diego County, with the goal of mapping literacy need against program
    accessibility to identify under-served micro-areas (zip codes).

    ## Data Sources

    - **ACS / Census-derived zip code estimates** — population, income, housing,
      employment, and SNAP indicators used to model literacy need and demographic risk
    - **Predicted literacy levels (Lit_P1 / Lit_P2_pred / Lit_P3_pred)** — modeled
      shares of adults at each literacy level by zip code
    - **Program directories** — affiliated (council-affiliated) and independent
      literacy, ESL, family literacy, and early-childhood programs, geocoded to
      lat/lon
    - **San Diego County Library locations** — used for library-based access scoring
    - **MTS GTFS transit feed** — stop locations and route coverage, used for the
      accessibility and transit layer
    - **2017–2023 panel data** — year-by-year adult low-literacy rate estimates, used
      for the temporal trend view

    ## Scoring Methodology

    The **Micro-Area Literacy Score** (0–100) is built per the project's
    specifications:

    1. Every component is normalized with min-max scaling to \\[0, 1\\], inverted
       where needed so that **higher always means better for the community**.
    2. Three sub-scores are built, each an equal-weighted average of their inputs:
       - **Need Severity** = 0.5 × literacy need + 0.5 × demographic risk
       - **Service Access** = 0.5 × library access + 0.5 × program accessibility
       - **Trend Direction** = mapped from the 2017→2023 trend category
         (persistent high-need / emerging problem = 0.0, insufficient data = 0.5,
         improving = 0.67, consistently low-need = 1.0)
    3. The composite score is the equal-weighted average of all three sub-scores,
       scaled to 0–100.

    There are three zip codes with no adult population in the database, and thus didn't receive scoring: 
    Cal State San Marcos (92096), Naval Base San Diego (92132),
    and San Diego State University (92182). Their inclusion would distort the
    min-max normalization for every other zip, so despite the exclusion, they will still appear on the map.

    A **sensitivity analysis** tested the equal-weighting baseline against four
    alternative weighting schemes (need-weighted, access-weighted,
    trend-weighted, and a need+trend emphasis). Rank correlations against the
    baseline ranged from 0.98–1.00 (Spearman), and the composite score correlated
    at **-0.76** with the observed adult low-literacy rate (expected negative
    direction, moderately strong) — indicating the scoring approach is reasonably
    robust to the specific weighting choice.

    ## Known Limitations

    - Zip-code boundaries are shown as centroid points rather than filled
      polygons; the TIGER/Line ZCTA shapefile needed for true choropleth maps
      was too large to bring into this environment. Centroid-based bubble maps
      are used throughout as the deployed fallback.
    - Level 2 and Level 3 literacy rates are model predictions
      (Lit_P2_pred and Lit_P3_pred) instead of being directly observed.
    - The outcome correlation check uses a variable called adult_low_literacy_rate, which is not
      fully independent of the Level 1 input used to build the Need Severity
      sub-score, so that correlation should be read as a consistency check
      rather than a fully external validation.
    - The dataset containing all council affiliated programs (Programs_affiliated.csv) lists 35 programs while the original project brief
      referenced 34. This is likely a minor discrepancy in the original count rather
      than a data error, but it's worth a final check against the source list.

    ## Navigation

    Use the sidebar to move between the hotspot map, literacy rate breakdowns,
    temporal trends, accessibility/transit, service gap rankings, the composite
    score map, and the program directory.
    """
)
