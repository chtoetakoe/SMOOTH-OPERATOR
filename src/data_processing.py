"""
this module contains all  data cleaning and feature engineering functions 
that we reuse across notebooks

"""
from __future__ import annotations

import numpy as np
import pandas as pd


def clean_grid(df: pd.DataFrame) -> pd.DataFrame:
    """
    create grid_clean: qualifying position with grid=0 treated as missing.
    Ergast often uses 0 when the grid is unknown or pit-lane start.
    We replace 0 with NaN and keep a numeric column.
    """
    out = df.copy()
    out["grid"] = pd.to_numeric(out["grid"], errors="coerce")
    out["grid_clean"] = out["grid"].replace(0, np.nan)
    return out


def add_race_features(df: pd.DataFrame) -> pd.DataFrame:
    #add simple per-race features
    out = df.copy()

    out["positionOrder"] = pd.to_numeric(out["positionOrder"], errors="coerce")
    out["points"] = pd.to_numeric(out["points"], errors="coerce")

    #positive means gained positions(started worse than finished)
    if "grid_clean" not in out.columns:
        out = clean_grid(out)
    out["position_gain"] = out["grid_clean"] - out["positionOrder"]

    #podium indicator(1,2,3)
    out["is_podium"] = (out["positionOrder"] <= 3).astype(int)
    return out


def attach_status_text(df: pd.DataFrame, status_df: pd.DataFrame) -> pd.DataFrame:
    """
    this function merges the status lookup  table so we 
    know WHY a driver didn't finish  was it engine failure,collision...
 """
    if "statusId" not in df.columns:
        return df.copy()
    out = df.copy()
    status_df = status_df.rename(columns={"status": "status_text"})
    out = out.merge(status_df[["statusId", "status_text"]], on="statusId", how="left")
    return out


def add_dnf_dns_flags(df: pd.DataFrame) -> pd.DataFrame:
    """
     simple finished/DNF/DNS flags using status text when available
     if status_text is missing this function returns safe defaults.
    """
    out = df.copy()

    #defaults
    out["is_finished"] = 0
    out["is_dnf"] = 0
    out["is_dns"] = 0

    #if we have status_text use it
    if "status_text" in out.columns:
        s = out["status_text"].astype(str).str.lower()

        finished = s.isin(["finished", "classified"])
        dns = s.str.contains("did not start", na=False)
        dnf = (~finished) & (~dns)

        out["is_finished"] = finished.astype(int)
        out["is_dns"] = dns.astype(int)
        out["is_dnf"] = dnf.astype(int)
    else:
        #fallback if points/positionOrder exist treat non null as finishedish
        if "positionOrder" in out.columns:
            out["is_finished"] = out["positionOrder"].notna().astype(int)

    return out


def _time_sort(df: pd.DataFrame) -> pd.DataFrame:
    """
    this helper ensures our data is in chronological order 
    which is critical for calculating historical features without data leakage
    
    sorts data chronologically by date then by raceId for races on same date
    """
    
    out = df.copy()
    out["date"] = pd.to_datetime(out["date"], errors="coerce")
    #stable ordering:date then raceId for ties
    return out.sort_values(["date", "raceId"], kind="mergesort")


def add_time_aware_aggregates(df: pd.DataFrame) -> pd.DataFrame:
    """
    this is most important function. 
    calculate historical features using ONLY PAST DATA. 
    The shift(1) is critical - 
    it prevents data leakage by ensuring we never use the current race's result to predict itself
    """
    out = _time_sort(df)

    #ensure numeric
    out["points"] = pd.to_numeric(out["points"], errors="coerce").fillna(0.0)
    out["positionOrder"] = pd.to_numeric(out["positionOrder"], errors="coerce")

    #driver aggregates
    g_d = out.groupby("driverId", sort=False)

    #past race count(before current row)
    out["driver_races_past"] = g_d.cumcount()

    #past avg points
    out["driver_avg_points_past"] = (
        g_d["points"].expanding().mean().shift(1).reset_index(level=0, drop=True)
    )

    #past consistency:std of past finish position(lower=more consistent)
    out["driver_consistency_past"] = (
        g_d["positionOrder"].expanding().std(ddof=0).shift(1).reset_index(level=0, drop=True)
    )

    #Constructor aggregates
    g_c = out.groupby("constructorId", sort=False)

    out["constructor_races_past"] = g_c.cumcount()

    out["constructor_strength_past"] = (
        g_c["points"].expanding().mean().shift(1).reset_index(level=0, drop=True)
    )

    out["constructor_avg_finish_past"] = (
        g_c["positionOrder"].expanding().mean().shift(1).reset_index(level=0, drop=True)
    )

    return out


def final_clean(df: pd.DataFrame) -> pd.DataFrame:
    """
      final cleaning handles edge cases - 
    like a driver's first race where they have no history.
      fill those with sensible defaults"""
    out = df.copy()

    #fill historical features where not enough past data exists
    fill_zero = [
        "driver_avg_points_past",
        "constructor_strength_past",
    ]
    for c in fill_zero:
        if c in out.columns:
            out[c] = pd.to_numeric(out[c], errors="coerce").fillna(0.0)

    #consistency/avg finish:if no past races, set to NaN then fill with dataset medians
    for c in ["driver_consistency_past", "constructor_avg_finish_past"]:
        if c in out.columns:
            out[c] = pd.to_numeric(out[c], errors="coerce")
            out[c] = out[c].fillna(out[c].median())

    #make sure that grid_clean exists
    if "grid_clean" not in out.columns:
        out = clean_grid(out)

    #ensure ints for flags if they exist
    for c in ["is_finished", "is_dnf", "is_dns", "is_podium"]:
        if c in out.columns:
            out[c] = pd.to_numeric(out[c], errors="coerce").fillna(0).astype(int)

    return out
