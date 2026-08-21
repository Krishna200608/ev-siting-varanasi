"""Live MCDM computation wrapper for What-If scenario exploration.

Imports pure mathematical ranking and weighting routines from src/mcdm
(zero GIS/rasterio dependencies) to enable sub-second interactive re-ranking.
"""

import sys
from pathlib import Path
from typing import Optional
import numpy as np
import pandas as pd

# Ensure repository root is on sys.path for importing pure src/mcdm modules
REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from src.mcdm.weighting import compute_critic_weights, compute_entropy_weights
from src.mcdm.ranking import compute_topsis_ranking

# Explicit Criteria Orientation Mapping (Fix 3: C5_Competitor_EVCS is strictly COST)
CRITERIA_ORIENTATION: dict[str, str] = {
    "C1_Major_Roads": "benefit",
    "C5_Competitor_EVCS": "cost",
    "C6_POI_Schools": "benefit",
    "C6_POI_Shopping_Malls": "benefit",
    "C6_POI_Restaurants": "benefit",
    "C6_POI_Hospitals": "benefit",
    "C6_POI_Theatres": "benefit",
    "C6_POI_Bus_Stops": "benefit",
    "C6_POI_Petrol_Bunks": "benefit",
}


def get_default_critic_weights(decision_matrix_df: pd.DataFrame) -> dict[str, float]:
    """Compute exact empirical CRITIC weights for the 9 criteria from the decision matrix.

    Returns:
        Dictionary mapping criterion name to its normalized CRITIC weight.
    """
    criteria_cols = [c for c in decision_matrix_df.columns if c not in ["site_id", "latitude", "longitude"]]
    criteria_types = [CRITERIA_ORIENTATION.get(c, "benefit") for c in criteria_cols]
    
    critic_weights = compute_critic_weights(
        decision_matrix_df[criteria_cols],
        criteria_types=criteria_types,
    )
    return {col: float(w) for col, w in zip(criteria_cols, critic_weights)}


def compute_live_whatif_ranking(
    custom_weights: dict[str, float],
    decision_matrix_df: pd.DataFrame,
    baseline_rankings_df: Optional[pd.DataFrame] = None,
) -> pd.DataFrame:
    """Recompute TOPSIS suitability ranking live with user-specified criteria weights.

    Args:
        custom_weights: Dictionary of criterion name -> raw slider weight.
        decision_matrix_df: Processed decision matrix DataFrame (308 sites x criteria).
        baseline_rankings_df: Optional baseline rankings DataFrame for rank delta tracking.

    Returns:
        DataFrame sorted by custom TOPSIS score with rank, score, and rank shift columns.
    """
    criteria_cols = [c for c in decision_matrix_df.columns if c not in ["site_id", "latitude", "longitude"]]
    criteria_types = [CRITERIA_ORIENTATION.get(c, "benefit") for c in criteria_cols]

    # Extract and normalize weights
    raw_weights_arr = np.array([custom_weights.get(c, 0.0) for c in criteria_cols], dtype=float)
    total_w = raw_weights_arr.sum()
    if total_w > 0:
        norm_weights_arr = raw_weights_arr / total_w
    else:
        norm_weights_arr = np.ones(len(criteria_cols)) / len(criteria_cols)

    # Execute pure TOPSIS ranking
    topsis_res = compute_topsis_ranking(
        decision_matrix=decision_matrix_df[criteria_cols],
        weights=norm_weights_arr,
        criteria_types=criteria_types,
    )

    scores = topsis_res["closeness_coefficient"].values
    ranks = topsis_res["rank"].values

    result_df = pd.DataFrame({
        "site_id": decision_matrix_df["site_id"].values,
        "latitude": decision_matrix_df["latitude"].values,
        "longitude": decision_matrix_df["longitude"].values,
        "custom_topsis_score": np.round(scores, 4),
        "custom_topsis_rank": ranks.astype(int),
    })

    # Merge criteria scores for inspection
    for c in criteria_cols:
        result_df[c] = np.round(decision_matrix_df[c].values, 2)

    # If baseline rankings provided, compute rank shift
    if baseline_rankings_df is not None and "topsis_critic_rank" in baseline_rankings_df.columns:
        base_map = dict(zip(baseline_rankings_df["site_id"], baseline_rankings_df["topsis_critic_rank"]))
        result_df["baseline_rank"] = result_df["site_id"].map(base_map).astype(int)
        # Shift: positive means improved rank (e.g. 19 -> 10 is +9)
        result_df["rank_shift"] = result_df["baseline_rank"] - result_df["custom_topsis_rank"]

    return result_df.sort_values("custom_topsis_rank").reset_index(drop=True)
