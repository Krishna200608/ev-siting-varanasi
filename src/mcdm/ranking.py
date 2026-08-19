"""Pipeline A: MCDM Decision Analysis — Site Suitability Ranking.

Synopsis Stage: Stage 2 — Alternative Ranking Algorithms (TOPSIS & WASPAS).
Theoretical Foundation: Guo & Zhao (2015, Applied Energy); Rashmitha, Sushma & Roy (2024).

This module implements multi-criteria ranking of candidate charging station alternatives:
1. TOPSIS (Technique for Order Preference by Similarity to Ideal Solution): Primary ranking method
   measuring Euclidean distance to positive-ideal and negative-ideal solutions.
2. WASPAS (Weighted Aggregated Sum Product Assessment): Cross-validation ranking combining
   Weighted Sum Model (WSM) and Weighted Product Model (WPM).
"""

from typing import Union, Optional
import numpy as np
import pandas as pd


def _extract_numeric_matrix_and_index(
    decision_matrix: Union[pd.DataFrame, np.ndarray],
) -> tuple[np.ndarray, list[str], pd.Index]:
    """Helper to isolate numeric criteria matrix, column names, and site index."""
    if isinstance(decision_matrix, pd.DataFrame):
        cols = [c for c in decision_matrix.columns if c not in ["site_id", "latitude", "longitude"]]
        site_idx = decision_matrix.index
        if "site_id" in decision_matrix.columns:
            site_idx = pd.Index(decision_matrix["site_id"].values)
        return decision_matrix[cols].to_numpy(dtype=float), cols, site_idx
    X = np.asarray(decision_matrix, dtype=float)
    return X, [f"C{i+1}" for i in range(X.shape[1])], pd.RangeIndex(len(X))


def compute_topsis_ranking(
    decision_matrix: Union[pd.DataFrame, np.ndarray],
    weights: np.ndarray,
    criteria_types: list[str],
) -> pd.DataFrame:
    """Rank candidate sites using the TOPSIS algorithm.

    Formulation per Rashmitha et al. (2024) and Guo & Zhao (2015):
    1. Vector normalize decision matrix: n_ij = x_ij / sqrt(sum_{k=1}^m x_kj^2).
    2. Weight normalized matrix: v_ij = w_j * n_ij.
    3. Determine Positive-Ideal (A+) and Negative-Ideal (A-) solutions:
       - Benefit: A+_j = max(v_j), A-_j = min(v_j)
       - Cost:    A+_j = min(v_j), A-_j = max(v_j)
    4. Compute Euclidean separation distances:
       S+_i = sqrt(sum_{j=1}^n (v_ij - A+_j)^2)
       S-_i = sqrt(sum_{j=1}^n (v_ij - A-_j)^2)
    5. Compute Relative Closeness: CC_i = S-_i / (S+_i + S-_i).
    6. Rank alternatives in descending order of CC_i.

    Args:
        decision_matrix: DataFrame or 2D array of candidate alternatives x criteria.
        weights: 1D array of criteria weights summing to 1.0.
        criteria_types: List of "benefit" or "cost" flags.

    Returns:
        DataFrame containing site indices, closeness_coefficient scores, and integer ranks (1 = best).
    """
    X, col_names, site_idx = _extract_numeric_matrix_and_index(decision_matrix)
    m, n = X.shape

    if m == 0 or n == 0:
        return pd.DataFrame(columns=["closeness_coefficient", "rank"])

    if len(weights) != n or len(criteria_types) != n:
        raise ValueError(f"Dimensions of weights ({len(weights)}) and criteria_types ({len(criteria_types)}) must match criteria ({n}).")

    w = np.asarray(weights, dtype=float) / np.sum(weights)

    # 1. Vector Normalization
    col_norm = np.sqrt(np.sum(X ** 2, axis=0))
    # Avoid zero division if column is all zeros
    col_norm[col_norm == 0.0] = 1.0
    N = X / col_norm

    # 2. Weighted Normalized Matrix
    V = N * w

    # 3. Ideal (A+) and Anti-Ideal (A-) Solutions
    A_plus = np.zeros(n, dtype=float)
    A_minus = np.zeros(n, dtype=float)

    for j in range(n):
        c_type = criteria_types[j].lower()
        if c_type == "cost":
            A_plus[j] = np.min(V[:, j])
            A_minus[j] = np.max(V[:, j])
        else:  # benefit
            A_plus[j] = np.max(V[:, j])
            A_minus[j] = np.min(V[:, j])

    # 4. Separation Measures
    S_plus = np.sqrt(np.sum((V - A_plus) ** 2, axis=1))
    S_minus = np.sqrt(np.sum((V - A_minus) ** 2, axis=1))

    # 5. Closeness Coefficient (CC)
    total_dist = S_plus + S_minus
    CC = np.where(total_dist > 0, S_minus / total_dist, 0.5)
    CC = np.clip(CC, 0.0, 1.0)

    # 6. Rank calculation (1 = highest CC score)
    # argsort of -CC gives ranking order
    ranks = np.zeros(m, dtype=int)
    ranks[np.argsort(-CC)] = np.arange(1, m + 1)

    results_df = pd.DataFrame(
        {
            "closeness_coefficient": CC,
            "rank": ranks,
        },
        index=site_idx,
    )

    return results_df


def compute_waspas_ranking(
    decision_matrix: Union[pd.DataFrame, np.ndarray],
    weights: np.ndarray,
    criteria_types: list[str],
    lambda_param: float = 0.5,
) -> pd.DataFrame:
    """Rank candidate sites using the WASPAS algorithm.

    Formulation per Rashmitha et al. (2024):
    1. Linear normalization:
       - Benefit: x_bar_ij = x_ij / max(x_j)
       - Cost:    x_bar_ij = min(x_j) / x_ij
    2. Weighted Sum Model (WSM): Q1_i = sum_{j=1}^n x_bar_ij * w_j.
    3. Weighted Product Model (WPM): Q2_i = prod_{j=1}^n (x_bar_ij)^w_j.
    4. Joint WASPAS Score: Q_i = lambda * Q1_i + (1 - lambda) * Q2_i.
    5. Rank alternatives in descending order of Q_i.

    Args:
        decision_matrix: DataFrame or 2D array of candidate alternatives x criteria.
        weights: 1D array of criteria weights summing to 1.0.
        criteria_types: List of "benefit" or "cost" flags.
        lambda_param: Trade-off parameter balancing WSM and WPM (default: 0.5).

    Returns:
        DataFrame containing site indices, waspas_score values, and integer ranks (1 = best).
    """
    X, col_names, site_idx = _extract_numeric_matrix_and_index(decision_matrix)
    m, n = X.shape

    if m == 0 or n == 0:
        return pd.DataFrame(columns=["waspas_score", "rank"])

    if len(weights) != n or len(criteria_types) != n:
        raise ValueError(f"Dimensions of weights ({len(weights)}) and criteria_types ({len(criteria_types)}) must match criteria ({n}).")

    w = np.asarray(weights, dtype=float) / np.sum(weights)

    # 1. Linear Normalization
    X_bar = np.zeros((m, n), dtype=float)
    for j in range(n):
        col = X[:, j]
        c_min, c_max = np.min(col), np.max(col)
        c_type = criteria_types[j].lower()

        if c_type == "cost":
            # For cost: min / val (avoid division by zero with small epsilon)
            safe_col = np.where(col > 0, col, 1e-6)
            X_bar[:, j] = np.where(col > 0, c_min / safe_col, 1.0)
        else:  # benefit
            # For benefit: val / max
            if c_max > 0:
                X_bar[:, j] = col / c_max
            else:
                X_bar[:, j] = 1.0

    X_bar = np.clip(X_bar, 1e-12, 1.0)

    # 2. Weighted Sum Model (WSM)
    Q1 = np.dot(X_bar, w)

    # 3. Weighted Product Model (WPM)
    # prod(x_bar_ij ^ w_j) = exp(sum(w_j * ln(x_bar_ij)))
    log_x_bar = np.log(X_bar)
    Q2 = np.exp(np.dot(log_x_bar, w))

    # 4. Joint WASPAS Score
    Q = lambda_param * Q1 + (1.0 - lambda_param) * Q2

    # 5. Rank calculation (1 = highest Q score)
    ranks = np.zeros(m, dtype=int)
    ranks[np.argsort(-Q)] = np.arange(1, m + 1)

    results_df = pd.DataFrame(
        {
            "waspas_score": Q,
            "rank": ranks,
        },
        index=site_idx,
    )

    return results_df
