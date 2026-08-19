"""Pipeline A: MCDM Decision Analysis — Objective Criteria Weighting.

Synopsis Stage: Stage 2 — Criteria Importance Computation (CRITIC & Entropy).
Theoretical Foundation: Rashmitha, Sushma & Roy (2024, Environment, Development and Sustainability).

This module computes objective criteria weights directly from the empirical decision matrix:
1. CRITIC (Criteria Importance Through Intercriteria Correlation): Measures contrast intensity
   via standard deviation and conflict via intercriteria correlation.
2. Shannon Entropy Weighting: Measures information entropy and degree of diversification across alternatives.

Both methods eliminate subjective evaluator bias in criteria weighting.
"""

from typing import Union
import numpy as np
import pandas as pd


def _extract_numeric_matrix(
    decision_matrix: Union[pd.DataFrame, np.ndarray],
) -> tuple[np.ndarray, list[str]]:
    """Helper to isolate numeric criteria columns from metadata columns if present."""
    if isinstance(decision_matrix, pd.DataFrame):
        # Exclude non-criteria metadata columns dynamically
        cols = [c for c in decision_matrix.columns if c not in ["site_id", "latitude", "longitude"]]
        return decision_matrix[cols].to_numpy(dtype=float), cols
    return np.asarray(decision_matrix, dtype=float), [f"C{i+1}" for i in range(decision_matrix.shape[1])]


def compute_critic_weights(
    decision_matrix: Union[pd.DataFrame, np.ndarray],
    criteria_types: list[str],
) -> np.ndarray:
    """Compute objective criteria weights using the CRITIC method.

    Formulation per Rashmitha et al. (2024):
    1. Normalize decision matrix X to r_ij in [0, 1]:
       - Benefit: r_ij = (x_ij - min(x_j)) / (max(x_j) - min(x_j))
       - Cost:    r_ij = (max(x_j) - x_ij) / (max(x_j) - min(x_j))
    2. Compute standard deviation sigma_j for each criterion (contrast intensity).
    3. Compute linear correlation matrix R = [r_jk] across criteria.
    4. Compute information content: C_j = sigma_j * sum_{k=1}^n (1 - r_jk).
    5. Compute normalized weights: w_j = C_j / sum_{k=1}^n C_k.

    Args:
        decision_matrix: DataFrame or 2D array of candidate alternatives x criteria.
        criteria_types: List of criteria types ("benefit" or "cost") corresponding to each criterion.

    Returns:
        1D NumPy array of criterion weights summing to 1.0.
    """
    X, col_names = _extract_numeric_matrix(decision_matrix)
    m, n = X.shape

    if m == 0 or n == 0:
        return np.array([], dtype=float)

    if len(criteria_types) != n:
        raise ValueError(f"Length of criteria_types ({len(criteria_types)}) must match number of criteria ({n}).")

    # 1. Normalization
    R = np.zeros((m, n), dtype=float)
    for j in range(n):
        col = X[:, j]
        c_min, c_max = np.min(col), np.max(col)
        c_type = criteria_types[j].lower()

        if np.isclose(c_max, c_min):
            R[:, j] = 0.0  # Zero variance criterion
        else:
            if c_type == "cost":
                R[:, j] = (c_max - col) / (c_max - c_min)
            else:  # benefit
                R[:, j] = (col - c_min) / (c_max - c_min)

    # 2. Standard deviation (contrast intensity)
    sigma = np.std(R, axis=0, ddof=0)

    # 3. Correlation matrix (conflict measure)
    corr_matrix = np.eye(n, dtype=float)
    for j in range(n):
        for k in range(n):
            if j != k:
                if sigma[j] > 0 and sigma[k] > 0:
                    r_jk = np.corrcoef(R[:, j], R[:, k])[0, 1]
                    corr_matrix[j, k] = 0.0 if np.isnan(r_jk) else r_jk
                else:
                    corr_matrix[j, k] = 0.0  # Zero correlation if constant

    # 4. Information content C_j
    conflict = np.sum(1.0 - corr_matrix, axis=1)
    C = sigma * conflict

    # 5. Normalized weights
    c_sum = np.sum(C)
    if c_sum > 0:
        weights = C / c_sum
    else:
        # Fallback to uniform weights if all criteria have zero variance
        weights = np.ones(n, dtype=float) / n

    return weights


def compute_entropy_weights(
    decision_matrix: Union[pd.DataFrame, np.ndarray],
    criteria_types: list[str],
) -> np.ndarray:
    """Compute objective criteria weights using Shannon's Entropy Weighting method.

    Formulation per Rashmitha et al. (2024):
    1. Normalize decision matrix X to r_ij in [0, 1] (inverting cost criteria).
    2. Compute probability proportion: p_ij = r_ij / sum_{k=1}^m r_kj.
    3. Compute information entropy: e_j = - (1 / ln(m)) * sum_{i=1}^m p_ij * ln(p_ij) (with 0*ln(0) = 0).
    4. Compute degree of divergence: d_j = 1 - e_j.
    5. Compute normalized weights: w_j = d_j / sum_{k=1}^n d_k.

    Args:
        decision_matrix: DataFrame or 2D array of candidate alternatives x criteria.
        criteria_types: List of criteria types ("benefit" or "cost") corresponding to each criterion.

    Returns:
        1D NumPy array of criterion weights summing to 1.0.
    """
    X, col_names = _extract_numeric_matrix(decision_matrix)
    m, n = X.shape

    if m == 0 or n == 0:
        return np.array([], dtype=float)

    if len(criteria_types) != n:
        raise ValueError(f"Length of criteria_types ({len(criteria_types)}) must match number of criteria ({n}).")

    if m == 1:
        return np.ones(n, dtype=float) / n

    # 1. Normalization to [0, 1]
    R = np.zeros((m, n), dtype=float)
    for j in range(n):
        col = X[:, j]
        c_min, c_max = np.min(col), np.max(col)
        c_type = criteria_types[j].lower()

        if np.isclose(c_max, c_min):
            R[:, j] = 1.0  # Equal values
        else:
            if c_type == "cost":
                R[:, j] = (c_max - col) / (c_max - c_min)
            else:
                R[:, j] = (col - c_min) / (c_max - c_min)

    # 2. Probability distribution p_ij
    col_sums = np.sum(R, axis=0)
    P = np.zeros((m, n), dtype=float)
    for j in range(n):
        if col_sums[j] > 0:
            P[:, j] = R[:, j] / col_sums[j]
        else:
            P[:, j] = 1.0 / m

    # 3. Entropy e_j
    k_const = 1.0 / np.log(m)
    e = np.zeros(n, dtype=float)
    for j in range(n):
        p_col = P[:, j]
        # p * ln(p) with convention 0 * ln(0) = 0
        nonzero_mask = p_col > 0
        entropy_terms = p_col[nonzero_mask] * np.log(p_col[nonzero_mask])
        e[j] = -k_const * np.sum(entropy_terms)
        e[j] = np.clip(e[j], 0.0, 1.0)

    # 4. Degree of divergence d_j
    d = 1.0 - e

    # 5. Normalized weights
    d_sum = np.sum(d)
    if d_sum > 0:
        weights = d / d_sum
    else:
        weights = np.ones(n, dtype=float) / n

    return weights
