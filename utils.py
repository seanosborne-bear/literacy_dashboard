"""Shared data loading helpers for the Literacy Service Gap dashboard."""

import os
import pandas as pd
import zipcodes

DATA_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data")


def _path(name):
    return os.path.join(DATA_DIR, name)


def zip_centroids(zip_list):
    """Return a DataFrame of zip_code, lat, lon for the given zip codes using
    the offline `zipcodes` package (no network calls -- safe for deployment)."""
    rows = []
    for z in sorted(set(str(z).zfill(5) for z in zip_list)):
        matches = zipcodes.matching(z)
        if matches:
            m = matches[0]
            rows.append(
                {
                    "zip_code": z,
                    "lat": float(m["lat"]),
                    "lon": float(m["long"]),
                    "city": m.get("city", ""),
                }
            )
        else:
            rows.append({"zip_code": z, "lat": None, "lon": None, "city": ""})
    return pd.DataFrame(rows)


def load_hotspots():
    df = pd.read_csv(_path("Literacy_Hotspot_Analysis.csv"), dtype={"zip_code": str})
    df["zip_code"] = df["zip_code"].str.zfill(5)
    centroids = zip_centroids(df["zip_code"])
    df = df.merge(centroids, on="zip_code", how="left")
    return df


def load_micro_area_scores():
    df = pd.read_csv(_path("Literacy_MicroArea_Scores.csv"), dtype={"zip_code": str})
    df["zip_code"] = df["zip_code"].str.zfill(5)
    centroids = zip_centroids(df["zip_code"])
    df = df.merge(centroids, on="zip_code", how="left")
    return df


def load_service_gap_rankings():
    df = pd.read_csv(_path("Literacy_ServiceGap_Rankings.csv"), dtype={"zip_code": str})
    df["zip_code"] = df["zip_code"].str.zfill(5)
    return df


def load_service_gap_scores():
    df = pd.read_csv(_path("Literacy_ServiceGap_Scores.csv"), dtype={"zip_code": str})
    df["zip_code"] = df["zip_code"].str.zfill(5)
    return df


def load_zip_estimates():
    df = pd.read_csv(_path("SD_ZipCode_LiteracyEstimates_AllLevels.csv"), dtype={"zip_code": str})
    df["zip_code"] = df["zip_code"].str.zfill(5)
    return df


def load_transit_accessibility():
    df = pd.read_csv(_path("Literacy_Transit_Accessibility_Scores.csv"), dtype={"zip_code": str})
    df["zip_code"] = df["zip_code"].str.zfill(5)
    return df


def load_level1_trend():
    df = pd.read_csv(_path("Level1_Validated_2017_2023.csv"), dtype={"zip_code": str})
    df["zip_code"] = df["zip_code"].str.zfill(5)
    return df


def load_travel_time_matrix(affiliated=True):
    name = "Literacy_TravelTimeMatrix_Affiliated.csv" if affiliated else "Literacy_TravelTimeMatrix_All.csv"
    df = pd.read_csv(_path(name))
    return df


def load_programs():
    """Return the combined program directory (42 rows) tagged with an
    `affiliation` column: 'Affiliated' or 'Independent', derived by matching
    Name against Programs_affiliated.csv / Programs_independent.csv."""
    all_geo = pd.read_csv(_path("Programs_all_geocoded.csv"))
    aff = pd.read_csv(_path("Programs_affiliated.csv"))
    ind = pd.read_csv(_path("Programs_independent.csv"))

    aff_names = set(aff["Name"])
    ind_names = set(ind["Name"])

    def tag(name):
        if name in aff_names:
            return "Affiliated"
        if name in ind_names:
            return "Independent"
        return "Unknown"

    all_geo["affiliation"] = all_geo["Name"].apply(tag)

    # bring in the affiliated-only enrichment columns (primary_type, flags review, etc.)
    aff_extra = aff[["Name", "primary_type", "type_note", "incomplete_flag", "missing_fields"]]
    all_geo = all_geo.merge(aff_extra, on="Name", how="left")

    return all_geo


def load_programs_affiliated():
    return pd.read_csv(_path("Programs_affiliated.csv"))


def load_programs_independent():
    return pd.read_csv(_path("Programs_independent.csv"))


def load_gtfs_stops():
    """Transit stops with lat/lon, from the GTFS stops.txt feed (small, clean,
    no need for the full 261MB flattened GTFS export)."""
    df = pd.read_csv(_path("gtfs_stops.csv"))
    df = df.dropna(subset=["stop_lat", "stop_lon"])
    return df


def load_level1_panel():
    """Long panel: one row per zip_code x year, 2017-2023. The source file also
    contains city-level aggregate rows (geography_type == 'city') with no
    zip_code -- those are dropped here since this view is zip-level only."""
    df = pd.read_csv(_path("Level1_Validated_2017_2023.csv"))
    df = df[df["geography_type"] == "zip"].copy()
    df["zip_code"] = df["zip_code"].astype(float).astype(int).astype(str).str.zfill(5)
    return df
