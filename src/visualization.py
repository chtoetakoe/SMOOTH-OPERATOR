# visualization_helpers for notebook 3(EDA).
from __future__ import annotations

from pathlib import Path
from typing import Iterable, Optional, Sequence, Tuple

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors

#Official F1 color palette
F1_RED = "#FF1801"
F1_DARK = "#15151e"
F1_GREY = "#38383f"
F1_WHITE = "#FFFFFF"

#apply a global clean style
plt.rcParams['axes.facecolor'] = 'white'
plt.rcParams['grid.color'] = '#f0f0f0'
plt.rcParams['font.family'] = 'sans-serif'

def ensure_fig_dir(project_root: Path) -> Path:
    #ensure reports and figures exists and return the directory path
    fig_dir = project_root / "reports" / "figures"
    fig_dir.mkdir(parents=True, exist_ok=True)
    return fig_dir

def save_fig(fig: plt.Figure, fig_dir: Path, filename: str, dpi: int = 150) -> Path:
    #save figure and return saved path
    out_path = fig_dir / filename
    fig.tight_layout()
    fig.savefig(out_path, dpi=dpi, bbox_inches="tight")
    return out_path

def plot_points_distribution(
        #this function plots the distribution of points. 
        #most drivers score 0 points(right-skewed distribution), 
        #only top 10 finishers get points in F1
    df: pd.DataFrame,
    fig_dir: Path,
    filename: str = "eda_points_hist.png",
) -> Path:
    fig, ax = plt.subplots(figsize=(10, 4))
    
    ax.hist(df["points"].dropna(), bins=30, color=F1_RED, edgecolor='white', linewidth=0.5)
    ax.set_title("Distribution of Race Points", fontweight='bold', loc='left')
    ax.set_xlabel("Points")
    ax.set_ylabel("Count")
    ax.grid(axis='y', alpha=0.3)
    return save_fig(fig, fig_dir, filename)

def plot_avg_points_by_year(
    df: pd.DataFrame,
    fig_dir: Path,
    filename: str = "eda_avg_points_by_year_line.png",
) -> Path:
    tmp = df.groupby("year", as_index=False)["points"].mean()
    fig, ax = plt.subplots(figsize=(10, 4))
    
    ax.plot(tmp["year"], tmp["points"], marker="o", color=F1_RED, linewidth=3, markersize=8, markerfacecolor=F1_DARK)
    ax.set_title("Average Points per Driver-Race by Year (2018–2024)", fontweight='bold', loc='left')
    ax.set_xlabel("Year")
    ax.set_ylabel("Average Points")
    ax.set_xticks(sorted(tmp["year"].unique()))
    ax.grid(True, alpha=0.3, linestyle='--')
    return save_fig(fig, fig_dir, filename)

def plot_qualifying_vs_points_scatter(
    df: pd.DataFrame,
    fig_dir: Path,
    filename: str = "eda_grid_vs_points_scatter.png",
) -> Path:
    fig, ax = plt.subplots(figsize=(10, 5))
    x = df["grid_clean"].astype(float)
    y = df["points"].astype(float)
    
    ax.scatter(x, y, alpha=0.3, s=40, color=F1_RED, edgecolors='white', linewidth=0.5)
    ax.set_title("Qualifying Position vs Race Points", fontweight='bold', loc='left')
    ax.set_xlabel("Qualifying Position (grid_clean)")
    ax.set_ylabel("Points")
    ax.set_xlim(0.5, max(20.5, float(np.nanmax(x)) + 0.5))
    ax.grid(True, alpha=0.2)
    return save_fig(fig, fig_dir, filename)

def plot_points_by_grid_bucket_boxplot(
        #this boxplot shows that frontrow starters(P1-3) have median ~18 points, while 
        #back-of-grid starters(P11-20) have median 0 points. 
        #the outliers in P11-20 are rare comeback drives
    df: pd.DataFrame,
    fig_dir: Path,
    filename: str = "eda_points_by_grid_bucket_boxplot.png",
) -> Path:
    def bucket(g: float) -> str:
        if pd.isna(g):
            return "Unknown"
        g = int(g)
        if 1 <= g <= 3:
            return "P1-3"
        if 4 <= g <= 10:
            return "P4-10"
        return "P11-20"

    tmp = df.copy()
    tmp["grid_bucket"] = tmp["grid_clean"].apply(bucket)
    order = ["P1-3", "P4-10", "P11-20"]
    groups = [tmp.loc[tmp["grid_bucket"] == o, "points"].dropna().values for o in order]

    fig, ax = plt.subplots(figsize=(8, 5))
    
    bplot = ax.boxplot(groups, labels=order, showfliers=True, patch_artist=True)
    
    for box in bplot['boxes']:
        box.set(facecolor=F1_RED, color=F1_DARK, linewidth=1.5)
    for median in bplot['medians']:
        median.set(color=F1_DARK, linewidth=2)
        
    ax.set_title("Points by Qualifying Bucket", fontweight='bold', loc='left')
    ax.set_xlabel("Grid Bucket")
    ax.set_ylabel("Points")
    ax.grid(axis='y', alpha=0.3)
    return save_fig(fig, fig_dir, filename)

def plot_constructor_strength_vs_points(
         #This function creates a scatter plot to test a hypothesis: 
        #"Do teams that have been strong in the past (X-axis) actually score 
        # more points today (Y-axis)?"
        #If this feature (constructor_strength_past) is good,
        # we should see a trend moving up and to the right.
        #If the dots are just a random cloud, the feature is useless for your machine learning model.
    df: pd.DataFrame,
    fig_dir: Path,
    filename: str = "eda_constructor_strength_vs_points.png",
) -> Path:
    fig, ax = plt.subplots(figsize=(10, 5))
    x = df["constructor_strength_past"].astype(float)
    y = df["points"].astype(float)
    ax.scatter(x, y, alpha=0.3, s=40, color=F1_RED, edgecolors='white', linewidth=0.5)
    ax.set_title("Constructor Strength (Past) vs Race Points", fontweight='bold', loc='left')
    ax.set_xlabel("Constructor Strength (past avg points)")
    ax.set_ylabel("Points")
    ax.grid(True, alpha=0.2)
    return save_fig(fig, fig_dir, filename)

def plot_driver_consistency_vs_points(
         #driver consistency is measured as standard deviation of past finishes. 
        #Lower std=more consistent 
        #this plot helps us understand if consistent drivers score more
        #though the relationship is weaker than grid position
    df: pd.DataFrame,
    fig_dir: Path,
    filename: str = "eda_driver_consistency_vs_points.png",
) -> Path:
    fig, ax = plt.subplots(figsize=(10, 5))
    x = df["driver_consistency_past"].astype(float)
    y = df["points"].astype(float)
    ax.scatter(x, y, alpha=0.3, s=40, color=F1_RED, edgecolors='white', linewidth=0.5)
    ax.set_title("Driver Consistency (Past) vs Race Points", fontweight='bold', loc='left')
    ax.set_xlabel("Driver Consistency (past std of finish position)")
    ax.set_ylabel("Points")
    ax.grid(True, alpha=0.2)
    return save_fig(fig, fig_dir, filename)

def plot_top_constructors_avg_points(df: pd.DataFrame, fig_dir: Path, top_n: int = 10,
                                     filename: str = "eda_top10_constructors_avg_points.png") -> Path:
    if "constructorName" in df.columns:
        col = "constructorName"
    elif "constructor" in df.columns:
        col = "constructor"
    elif "constructorId" in df.columns:
        col = "constructorId"
    else:
        raise KeyError("No constructor column found.")

    tmp = (
        df.groupby(col, as_index=False)["points"]
          .mean()
          .sort_values("points", ascending=False)
          .head(top_n)
    )

    fig, ax = plt.subplots(figsize=(11, 5))
    ax.bar(tmp[col].astype(str), tmp["points"], color=F1_RED, edgecolor=F1_DARK)
    ax.set_title(f"Top {top_n} Constructors by Average Points (2018–2024)", fontweight='bold', loc='left')
    ax.set_xlabel("Constructor")
    ax.set_ylabel("Average Points")
    plt.setp(ax.get_xticklabels(), rotation=45, ha="right")
    ax.grid(axis='y', alpha=0.3)
    return save_fig(fig, fig_dir, filename)

def plot_top_drivers_avg_points(df: pd.DataFrame, fig_dir: Path, top_n: int = 15,
                                filename: str = "eda_top15_drivers_avg_points.png") -> Path:
    if "driverName" in df.columns:
        label_col = "driverName"
        tmp = df.copy()
    elif "givenName" in df.columns and "familyName" in df.columns:
        tmp = df.copy()
        tmp["driverName"] = tmp["givenName"].astype(str) + " " + tmp["familyName"].astype(str)
        label_col = "driverName"
    elif "driverRef" in df.columns:
        label_col = "driverRef"
        tmp = df.copy()
    else:
        label_col = "driverId"
        tmp = df.copy()

    stats = (
        tmp.groupby(label_col, as_index=False)["points"]
           .mean()
           .sort_values("points", ascending=False)
           .head(top_n)
    )

    fig, ax = plt.subplots(figsize=(12, 5))
    ax.bar(stats[label_col].astype(str), stats["points"], color=F1_RED, edgecolor=F1_DARK)
    ax.set_title(f"Top {top_n} Drivers by Average Points (2018–2024)", fontweight='bold', loc='left')
    ax.set_xlabel("Driver")
    ax.set_ylabel("Average Points")
    plt.setp(ax.get_xticklabels(), rotation=45, ha="right")
    ax.grid(axis='y', alpha=0.3)
    return save_fig(fig, fig_dir, filename)

def plot_corr_heatmap_top_features(
    df: pd.DataFrame,
    fig_dir: Path,
    target: str = "points",
    top_k: int = 10,
    filename: str = "eda_corr_heatmap_top_features.png",
) -> Path:
    num = df.select_dtypes(include=["number"]).copy()
    if target not in num.columns:
        raise ValueError(f"Target column '{target}' not found.")

    corrs = num.corr(numeric_only=True)[target].drop(index=target).abs().sort_values(ascending=False)
    top_features = [target] + corrs.head(top_k).index.tolist()
    corr_mat = num[top_features].corr(numeric_only=True).values
    labels = top_features

    fig, ax = plt.subplots(figsize=(10, 7))
    
    cmap_f1 = mcolors.LinearSegmentedColormap.from_list("f1_heatmap", [F1_DARK, F1_WHITE, F1_RED])
    im = ax.imshow(corr_mat, vmin=-1, vmax=1, cmap=cmap_f1)

    ax.set_xticks(range(len(labels)))
    ax.set_yticks(range(len(labels)))
    ax.set_xticklabels(labels, rotation=45, ha="right")
    ax.set_yticklabels(labels)

    for i in range(len(labels)):
        for j in range(len(labels)):
            
            text_color = "white" if abs(corr_mat[i, j]) > 0.6 else "black"
            ax.text(j, i, f"{corr_mat[i, j]:.2f}", ha="center", va="center", fontsize=9, color=text_color)

    ax.set_title("Correlation Heatmap (Top Features vs Points)", fontweight='bold', loc='left')
    fig.colorbar(im, ax=ax, shrink=0.8, label="Correlation")
    return save_fig(fig, fig_dir, filename)

def plot_corr_with_points_bar(
    df: pd.DataFrame,
    fig_dir: Path,
    target: str = "points",
    filename: str = "eda_corr_with_points_bar.png",
) -> Path:
    num = df.select_dtypes(include=["number"]).copy()
    corr = num.corr(numeric_only=True)[target].drop(index=target).sort_values()

    fig, ax = plt.subplots(figsize=(10, 6))
    ax.barh(corr.index.astype(str), corr.values, color=F1_RED, edgecolor=F1_DARK)
    ax.set_title("Correlation of Features with Race Points", fontweight='bold', loc='left')
    ax.set_xlabel("Correlation with Points")
    ax.set_ylabel("Feature")
    ax.axvline(0, color=F1_DARK, linewidth=1.5)
    ax.grid(axis='x', alpha=0.3)
    return save_fig(fig, fig_dir, filename)

def plot_pole_win_rate_selected_gps(
    df: pd.DataFrame,
    fig_dir: Path,
    gps: Sequence[str] = ("Monaco Grand Prix", "Italian Grand Prix", "Belgian Grand Prix"),
    filename: str = "eda_pole_win_rate_monaco_monza_spa.png",
) -> Path:
    race_col = "name" if "name" in df.columns else ("raceName" if "raceName" in df.columns else None)
    if race_col is None:
        raise KeyError("No race name column found.")

    tmp = df[df[race_col].isin(gps)].copy()
    tmp["from_pole"] = tmp["grid_clean"] == 1
    tmp["won"] = tmp["positionOrder"] == 1

    rates = []
    labels = []
    for gp in gps:
        sub = tmp[tmp[race_col] == gp]
        pole = sub[sub["from_pole"]]
        poles = len(pole)
        wins = int(pole["won"].sum()) if poles else 0
        rate = (wins / poles) if poles else np.nan
        rates.append(rate)
        labels.append(gp)

    fig, ax = plt.subplots(figsize=(10, 5))
    ax.bar(labels, rates, color=F1_RED, edgecolor=F1_DARK)
    ax.set_title("Win Rate from Pole (2018–2024): Monaco vs Monza vs Spa", fontweight='bold', loc='left')
    ax.set_xlabel("Grand Prix")
    ax.set_ylabel("Win Rate from Pole (P1→P1)")
    ax.set_ylim(0, 1.1)

    for i, r in enumerate(rates):
        if not np.isnan(r):
            gp = labels[i]
            sub = tmp[tmp[race_col] == gp]
            pole = sub[sub["from_pole"]]
            poles = len(pole)
            wins = int(pole["won"].sum())
            ax.text(i, r + 0.02, f"{wins}/{poles} ({r*100:.1f}%)", 
                    ha="center", va="bottom", fontsize=10, fontweight='bold', color=F1_DARK)

    plt.setp(ax.get_xticklabels(), rotation=20, ha="right")
    ax.grid(axis='y', alpha=0.3)
    return save_fig(fig, fig_dir, filename)