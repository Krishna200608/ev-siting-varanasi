"""Pipeline A: MCDM Decision Analysis — Objective Criteria Weighting.

Synopsis Stage: Stage 2 — Criteria Importance Computation (CRITIC & Entropy).
Theoretical Foundation: Rashmitha, Sushma & Roy (2024, Environment, Development and Sustainability).

This module computes objective criteria weights from the standardized decision matrix:
1. CRITIC (Criteria Importance Through Intercriteria Correlation): Measures contrast intensity
   via standard deviation and conflict via correlation coefficients.
2. Entropy Weighting: Computes information entropy to measure disorder and dispersion in criteria values.
Both methods eliminate subjective evaluator bias in criteria weighting.
"""

import numpy as np
import pandas as pd


def compute_critic_weights(
    decision_matrix: pd.DataFrame,
    criteria_types: list[str],
) -> np.ndarray:
    """Compute objective criteria weights using the CRITIC method.

    CRITIC calculates weights based on the standard deviation of normalized criteria (contrast intensity)
    and linear correlation with other criteria (conflict / redundancy).

    Args:
        decision_matrix: DataFrame containing candidate sites as rows and criteria as columns.
        criteria_types: List of criteria types ("benefit" or "cost") corresponding to each column.

    Returns:
        1D NumPy array of normalized criterion weights summing to 1.0.

    Raises:
        NotImplementedError: Scheduled for Milestone 3 implementation.
    """
    raise NotImplementedError("Milestone 3 — see docs/ROADMAP.md")


def compute_entropy_weights(
    decision_matrix: pd.DataFrame,
    criteria_types: list[str],
) -> np.ndarray:
    """Compute objective criteria weights using Shannon's Entropy Weighting method.

    Entropy weighting derives weights by quantifying information entropy and degree of diversification.

    Args:
        decision_matrix: DataFrame containing candidate sites as rows and criteria as columns.
        criteria_types: List of criteria types ("benefit" or "cost") corresponding to each column.

    Returns:
        1D NumPy array of normalized criterion weights summing to 1.0.

    Raises:
        NotImplementedError: Scheduled for Milestone 3 implementation.
    """
    raise NotImplementedError("Milestone 3 — see docs/ROADMAP.md")
