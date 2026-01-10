"""
Data Processing Module for F1 Race Analysis

This module contains all data cleaning and feature engineering functions 
that we reuse across notebooks.

IMPORTANT: All historical features use ONLY PAST DATA to prevent data leakage.
- Driver features: use expanding().shift(1) within each driver
- Constructor features: aggregate at RACE level first, then expand over races
  (to avoid same-race teammate leakage)
"""
from __future__ import annotations

import numpy as np
import pandas as pd


def clean_grid(df: pd.DataFrame) -> pd.DataFrame:
    """
    Create grid_clean: qualifying position with grid=0 treated as missing.
    
    Ergast uses 0 when the grid is unknown or pit-lane start.
    We replace 0 with NaN and keep a numeric column.
    """
    out = df.copy()
    out["grid"] = pd.to_numeric(out["grid"], errors="coerce")
    out["grid_clean"] = out["grid"].replace(0, np.nan)
    return out


def add_race_features(df: pd.DataFrame) -> pd.DataFrame:
    """
    Add simple per-race features.
    
    Note: position_gain and is_podium are POST-RACE features.
    They should NOT be used as ML features for predicting points.
    They are useful for EDA only.
    """
    out = df.copy()

    out["positionOrder"] = pd.to_numeric(out["positionOrder"], errors="coerce")
    out["points"] = pd.to_numeric(out["points"], errors="coerce")

    # Ensure grid_clean exists
    if "grid_clean" not in out.columns:
        out = clean_grid(out)
    
    # Position gain: positive means gained positions (started worse than finished)
    # WARNING: This is a POST-RACE feature - do not use for prediction!
    out["position_gain"] = out["grid_clean"] - out["positionOrder"]

    # Podium indicator (1, 2, 3)
    # WARNING: This is a POST-RACE feature - do not use for prediction!
    out["is_podium"] = (out["positionOrder"] <= 3).astype(int)
    
    return out


def attach_status_text(df: pd.DataFrame, status_df: pd.DataFrame) -> pd.DataFrame:
    """
    Merge the status lookup table so we know WHY a driver didn't finish
    (engine failure, collision, etc.)
    """
    if "statusId" not in df.columns:
        return df.copy()
    out = df.copy()
    status_df = status_df.rename(columns={"status": "status_text"})
    out = out.merge(status_df[["statusId", "status_text"]], on="statusId", how="left")
    return out


def add_dnf_dns_flags(df: pd.DataFrame) -> pd.DataFrame:
    """
    Add simple finished/DNF/DNS flags using status text when available.
    If status_text is missing, returns safe defaults.
    """
    out = df.copy()

    # Defaults
    out["is_finished"] = 0
    out["is_dnf"] = 0
    out["is_dns"] = 0

    # If we have status_text, use it
    if "status_text" in out.columns:
        s = out["status_text"].astype(str).str.lower()

        finished = s.isin(["finished", "classified"])
        dns = s.str.contains("did not start", na=False)
        dnf = (~finished) & (~dns)

        out["is_finished"] = finished.astype(int)
        out["is_dns"] = dns.astype(int)
        out["is_dnf"] = dnf.astype(int)
    else:
        # Fallback: if points/positionOrder exist, treat non-null as finished
        if "positionOrder" in out.columns:
            out["is_finished"] = out["positionOrder"].notna().astype(int)

    return out


def _time_sort(df: pd.DataFrame) -> pd.DataFrame:
    """
    Helper: ensures data is in chronological order.
    
    This is CRITICAL for calculating historical features without data leakage.
    Sorts by date, then by raceId for races on same date.
    """
    out = df.copy()
    out["date"] = pd.to_datetime(out["date"], errors="coerce")
    # Stable sort: date first, then raceId for ties
    return out.sort_values(["date", "raceId"], kind="mergesort").reset_index(drop=True)


def add_time_aware_aggregates(df: pd.DataFrame) -> pd.DataFrame:
    """
    Calculate historical features using ONLY PAST DATA.
    
    This is the most important function for preventing data leakage.
    
    Key techniques:
    1. expanding() - uses all data up to current row
    2. shift(1) - excludes current row (only past data)
    3. transform() - ensures shift happens WITHIN each group
    4. Constructor features aggregated at RACE level first
       (to avoid same-race teammate leakage)
    
    Example for driver_avg_points_past:
    - Race 1: Driver scores 25 pts → avg_past = NaN (no history)
    - Race 2: Driver scores 18 pts → avg_past = 25 (only Race 1)
    - Race 3: Driver scores 15 pts → avg_past = 21.5 (Race 1+2)
    """
    out = _time_sort(df)

    # Ensure numeric
    out["points"] = pd.to_numeric(out["points"], errors="coerce").fillna(0.0)
    out["positionOrder"] = pd.to_numeric(out["positionOrder"], errors="coerce")

    # =========================================================================
    # DRIVER AGGREGATES (safe: one row per driver per race)
    # Using transform() ensures shift happens within each driver group
    # =========================================================================
    g_d = out.groupby("driverId", sort=False)

    # Past race count (before current row)
    out["driver_races_past"] = g_d.cumcount()

    # Past average points - using transform for safe within-group shift
    out["driver_avg_points_past"] = g_d["points"].transform(
        lambda s: s.expanding().mean().shift(1)
    )

    # Past consistency: std of past finish positions (lower = more consistent)
    out["driver_consistency_past"] = g_d["positionOrder"].transform(
        lambda s: s.expanding().std(ddof=0).shift(1)
    )

    # =========================================================================
    # CONSTRUCTOR AGGREGATES (must be race-level to avoid same-race leakage)
    # 
    # Problem: Each constructor has 2 drivers per race. If we compute
    # expanding stats row-by-row, the first driver's result from the SAME
    # race could leak into the second driver's features. That's wrong!
    #
    # Solution: First aggregate constructor performance at the RACE level,
    # then compute expanding stats over races (not over driver-rows).
    # =========================================================================
    
    # Step 1: Aggregate constructor stats per race
    cons_race = (
        out.groupby(["constructorId", "raceId", "date"], as_index=False)
        .agg(
            constructor_points=("points", "sum"),           # Total team points in race
            constructor_mean_finish=("positionOrder", "mean")  # Avg finish position
        )
        .sort_values(["date", "raceId"], kind="mergesort")
        .reset_index(drop=True)
    )

    # Step 2: Compute expanding stats at race level (within each constructor)
    g_c = cons_race.groupby("constructorId", sort=False)
    
    # Past race count for constructor
    cons_race["constructor_races_past"] = g_c.cumcount()
    
    # Past average points per race (team total)
    cons_race["constructor_strength_past"] = g_c["constructor_points"].transform(
        lambda s: s.expanding().mean().shift(1)
    )
    
    # Past average finish position
    cons_race["constructor_avg_finish_past"] = g_c["constructor_mean_finish"].transform(
        lambda s: s.expanding().mean().shift(1)
    )

    # Step 3: Merge back to driver-level data
    out = out.merge(
        cons_race[[
            "constructorId", 
            "raceId",
            "constructor_races_past",
            "constructor_strength_past",
            "constructor_avg_finish_past"
        ]],
        on=["constructorId", "raceId"],
        how="left"
    )

    return out


def final_clean(df: pd.DataFrame, train_medians: dict = None) -> pd.DataFrame:
    """
    Final cleaning: handle edge cases like a driver's first race
    where they have no history.
    
    Args:
        df: DataFrame to clean
        train_medians: Optional dict of medians computed from training data.
                      If None, uses current data medians (slight leakage for test set).
                      Format: {"column_name": median_value}
    
    Fill strategies:
    - driver_avg_points_past: 0 (new driver has no history)
    - constructor_strength_past: 0 (new team has no history)
    - consistency/avg_finish: median (sensible default)
    """
    out = df.copy()

    # Fill historical features where not enough past data exists
    fill_zero = [
        "driver_avg_points_past",
        "constructor_strength_past",
    ]
    for c in fill_zero:
        if c in out.columns:
            out[c] = pd.to_numeric(out[c], errors="coerce").fillna(0.0)

    # Consistency/avg finish: fill with median
    fill_median = ["driver_consistency_past", "constructor_avg_finish_past"]
    for c in fill_median:
        if c in out.columns:
            out[c] = pd.to_numeric(out[c], errors="coerce")
            if train_medians and c in train_medians:
                # Use provided training median (no leakage)
                out[c] = out[c].fillna(train_medians[c])
            else:
                # Use current data median (slight leakage, but acceptable for school project)
                out[c] = out[c].fillna(out[c].median())

    # Make sure grid_clean exists
    if "grid_clean" not in out.columns:
        out = clean_grid(out)

    # Ensure ints for flags if they exist
    for c in ["is_finished", "is_dnf", "is_dns", "is_podium"]:
        if c in out.columns:
            out[c] = pd.to_numeric(out[c], errors="coerce").fillna(0).astype(int)

    return out


def get_train_medians(df: pd.DataFrame, train_years: tuple = (2018, 2022)) -> dict:
    """
    Compute medians from training data only (to avoid leakage when filling test set).
    
    Args:
        df: Full DataFrame
        train_years: Tuple of (start_year, end_year) for training data
    
    Returns:
        Dictionary of {column_name: median_value}
    """
    train_df = df[(df["year"] >= train_years[0]) & (df["year"] <= train_years[1])]
    
    medians = {}
    for c in ["driver_consistency_past", "constructor_avg_finish_past"]:
        if c in train_df.columns:
            medians[c] = train_df[c].median()
    
    return medians
