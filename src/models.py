"""
- Preprocessor (numeric + categorical)
- Models: Linear Regression, Decision Tree Regressor
- Metrics: MSE, RMSE, MAE, R^2
- Splits:
  * random split (train_test_split)
  * time-based split (2018–2022 train, 2023–2024 test)
"""

from __future__ import annotations

from typing import Dict, List, Tuple

import numpy as np
import pandas as pd

from sklearn.compose import ColumnTransformer
from sklearn.impute import SimpleImputer
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder
from sklearn.linear_model import LinearRegression
from sklearn.tree import DecisionTreeRegressor


def build_preprocessor(numeric_features: List[str], categorical_features: List[str]) -> ColumnTransformer:
    """Create a preprocessing transformer for numeric + categorical features."""
    numeric_pipe = Pipeline(steps=[
        ("imputer", SimpleImputer(strategy="median")),
    ])

    categorical_pipe = Pipeline(steps=[
        ("imputer", SimpleImputer(strategy="most_frequent")),
        ("onehot", OneHotEncoder(handle_unknown="ignore")),
    ])

    preprocessor = ColumnTransformer(
        transformers=[
            ("num", numeric_pipe, numeric_features),
            ("cat", categorical_pipe, categorical_features),
        ],
        remainder="drop",
    )
    return preprocessor


def make_models(preprocessor: ColumnTransformer, random_state: int = 42) -> Dict[str, Pipeline]:
    """Create regression models as sklearn Pipelines."""
    models = {
        "LinearRegression": Pipeline(steps=[
            ("preprocess", preprocessor),
            ("model", LinearRegression()),
        ]),
        "DecisionTree": Pipeline(steps=[
            ("preprocess", preprocessor),
            ("model", DecisionTreeRegressor(random_state=random_state, max_depth=8)),
        ]),
    }
    return models


def evaluate_regression(y_true: np.ndarray, y_pred: np.ndarray) -> Dict[str, float]:
    mse = mean_squared_error(y_true, y_pred)
    rmse = np.sqrt(mse)  # ✅ works on all sklearn versions
    mae = mean_absolute_error(y_true, y_pred)
    r2 = r2_score(y_true, y_pred)
    return {"MSE": float(mse), "RMSE": float(rmse), "MAE": float(mae), "R2": float(r2)}



def train_and_evaluate_models(
    models: Dict[str, Pipeline],
    X_train: pd.DataFrame,
    y_train: pd.Series,
    X_test: pd.DataFrame,
    y_test: pd.Series,
) -> Tuple[pd.DataFrame, Dict[str, np.ndarray]]:
    """Fit all models, evaluate, return results table and predictions."""
    rows = []
    preds: Dict[str, np.ndarray] = {}

    y_test_arr = y_test.to_numpy()

    for name, pipe in models.items():
        pipe.fit(X_train, y_train)
        y_pred = pipe.predict(X_test)
        preds[name] = y_pred

        metrics = evaluate_regression(y_test_arr, y_pred)
        rows.append({"model": name, **metrics})

    results = pd.DataFrame(rows).sort_values("MSE", ascending=True).reset_index(drop=True)
    return results, preds


def default_train_test_split(
    df: pd.DataFrame,
    feature_cols: List[str],
    target_col: str,
    test_size: float = 0.2,
    random_state: int = 42,
) -> Tuple[pd.DataFrame, pd.DataFrame, pd.Series, pd.Series]:
    """Simple random train/test split."""
    X = df[feature_cols].copy()
    y = df[target_col].copy()
    return train_test_split(X, y, test_size=test_size, random_state=random_state)


def time_based_split(
    df: pd.DataFrame,
    feature_cols: List[str],
    target_col: str,
    year_col: str = "year",
    train_years: Tuple[int, int] = (2018, 2022),
    test_years: Tuple[int, int] = (2023, 2024),
) -> Tuple[pd.DataFrame, pd.DataFrame, pd.Series, pd.Series]:
    """
    Time-based split:
      Train: train_years (inclusive)
      Test : test_years (inclusive)

    This avoids leakage and matches your requirement (2018–2022 vs 2023–2024).
    """
    if year_col not in df.columns:
        raise KeyError(f"'{year_col}' column not found in df. Available: {list(df.columns)}")

    tmp = df.copy()
    tmp[year_col] = pd.to_numeric(tmp[year_col], errors="coerce").astype("Int64")

    # keep only rows where year is valid + required columns exist
    needed = feature_cols + [target_col, year_col]
    tmp = tmp.dropna(subset=needed)

    train_mask = tmp[year_col].between(train_years[0], train_years[1])
    test_mask = tmp[year_col].between(test_years[0], test_years[1])

    train_df = tmp.loc[train_mask]
    test_df = tmp.loc[test_mask]

    if train_df.empty or test_df.empty:
        raise ValueError(
            f"Time split produced empty set. "
            f"Train rows: {len(train_df)}, Test rows: {len(test_df)}. "
            f"Check your year range or year column values."
        )

    X_train = train_df[feature_cols].copy()
    y_train = train_df[target_col].copy()
    X_test = test_df[feature_cols].copy()
    y_test = test_df[target_col].copy()

    return X_train, X_test, y_train, y_test
