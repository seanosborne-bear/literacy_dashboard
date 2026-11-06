import streamlit as st
import pandas as pd

from utils import load_programs

st.set_page_config(page_title="Program Directory", page_icon="🔎", layout="wide")
st.title("Program Directory")

st.markdown("This contains the full directory of literacy-related programs across San Diego County.")

df = load_programs()

st.sidebar.header("Filters")
search_term = st.sidebar.text_input("Search by name, city, or description")

affiliation_filter = st.sidebar.multiselect(
    "Affiliation", sorted(df["affiliation"].unique()), default=sorted(df["affiliation"].unique())
)
program_type_filter = st.sidebar.multiselect(
    "Program type", sorted(df["Program Type"].dropna().unique()),
    default=sorted(df["Program Type"].dropna().unique()),
)
city_filter = st.sidebar.multiselect(
    "City", sorted(df["City"].dropna().unique()), default=sorted(df["City"].dropna().unique())
)
only_incomplete = st.sidebar.checkbox("Show only programs with incomplete/flagged data", value=False)

view = df[
    df["affiliation"].isin(affiliation_filter)
    & df["Program Type"].isin(program_type_filter)
    & df["City"].isin(city_filter)
]

if search_term:
    s = search_term.lower()
    mask = (
        view["Name"].str.lower().str.contains(s, na=False)
        | view["City"].str.lower().str.contains(s, na=False)
        | view["Description"].str.lower().str.contains(s, na=False)
    )
    view = view[mask]

if only_incomplete:
    view = view[view["incomplete_flag"] == "Yes"]

st.caption(f"Showing {len(view)} of {len(df)} programs")

for _, row in view.sort_values("Name").iterrows():
    with st.container(border=True):
        c1, c2 = st.columns([3, 1])
        with c1:
            st.markdown(f"**{row['Name']}**  \n{row.get('Address', '')}, {row.get('City', '')}, {row.get('State', '')} {row.get('Zip Code', '')}")
            if pd.notna(row.get("Description")):
                st.caption(row["Description"])
        with c2:
            st.markdown(f"**{row['affiliation']}**")
            st.markdown(f"{row.get('Program Type', '')}")
        cols = st.columns(4)
        cols[0].markdown(f"📞 {row.get('Phone', 'N/A')}")
        cols[1].markdown(f"✉️ {row.get('Email', 'N/A')}")
        cols[2].markdown(f"🕐 {row.get('Hours', 'N/A') if pd.notna(row.get('Hours')) else 'Not listed'}")
        cols[3].markdown(f"👥 Capacity: {row.get('Capacity', 'N/A') if pd.notna(row.get('Capacity')) else 'Not listed'}")
        if pd.notna(row.get("Flags")) and str(row.get("Flags")).strip():
            st.warning(f"Flag: {row['Flags']}")

st.subheader("Table view")
table_cols = ["Name", "City", "affiliation", "Program Type", "Hours", "Capacity", "Phone", "Email", "Website"]
st.dataframe(view[table_cols], use_container_width=True)

csv = view.to_csv(index=False).encode("utf-8")
st.download_button(
    "Download filtered program directory as CSV",
    data=csv,
    file_name="program_directory_filtered.csv",
    mime="text/csv",
)
