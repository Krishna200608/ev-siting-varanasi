"""Stage 4: MCDM Robustness & Sensitivity Analysis.

Synopsis Stage: Stage 4 — Multi-Scenario Sensitivity Testing.
Theoretical Foundation: Rashmitha, Sushma & Roy (2024, Environment, Development and Sustainability).

This module implements a 12-scenario criteria weight perturbation analysis to assess the stability
of the primary TOPSIS-CRITIC site suitability ranking under varying decision preferences and weight shifts:
- Scenarios 1–9: Individual +20% weight increases on each confirmed spatial criterion (renormalized).
- Scenario 10: Equal criterion weighting (1/N baseline).
- Scenario 11: Transportation dominance (50% weight on Major Roads).
- Scenario 12: Commercial dominance (50% weight on Shopping Malls).
"""

import sys
from pathlib import Path
from typing import Any, Optional, Union

# Add project root to sys.path if running as standalone script
project_root = Path(__file__).resolve().parents[2]
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from scipy.stats import kendalltau, spearmanr

from src.mcdm.ranking import compute_topsis_ranking
from src.mcdm.weighting import _extract_numeric_matrix, compute_critic_weights


def run_mcdm_criteria_sensitivity(
    decision_matrix: Union[pd.DataFrame, np.ndarray],
    criteria_types: list[str],
    base_weights: Optional[np.ndarray] = None,
    perturbation_pct: float = 0.20,
    top_n: int = 5,
    output_table_path: Optional[Path] = Path("outputs/tables/mcdm_sensitivity_results.csv"),
) -> pd.DataFrame:
    """Execute 12-scenario weight perturbation sensitivity analysis on the decision matrix.

    Args:
        decision_matrix: DataFrame or numeric 2D array of candidates x criteria.
        criteria_types: List of "benefit" or "cost" flags corresponding to criteria.
        base_weights: 1D array of base weights (computed via CRITIC if None).
        perturbation_pct: Fraction by which to increase individual criterion weight (default: 0.20).
        top_n: Number of top-ranked sites to evaluate for shortlist overlap (default: 5).
        output_table_path: Optional path to save CSV results.

    Returns:
        DataFrame summarizing scenario parameters, Spearman rho, Kendall tau, and Top-N overlap %.
    """
    X, col_names = _extract_numeric_matrix(decision_matrix)
    m, n = X.shape

    if m == 0 or n == 0:
        return pd.DataFrame()

    if base_weights is None:
        base_weights = compute_critic_weights(X, criteria_types)

    # Compute base TOPSIS-CRITIC ranking
    base_topsis = compute_topsis_ranking(X, base_weights, criteria_types)
    base_ranks = base_topsis["rank"].to_numpy()

    # Identify base Top-N site indices
    base_top_n_indices = set(np.where(base_ranks <= top_n)[0])

    scenarios: list[dict[str, Any]] = []

    # Scenarios 1 to n: Perturb each individual criterion weight by +perturbation_pct
    for j in range(n):
        col_name = col_names[j] if j < len(col_names) else f"Criterion_{j+1}"
        w_perturbed = base_weights.copy()
        w_perturbed[j] *= (1.0 + perturbation_pct)
        # Renormalize sum to 1.0
        w_perturbed = w_perturbed / np.sum(w_perturbed)

        res = compute_topsis_ranking(X, w_perturbed, criteria_types)
        scen_ranks = res["rank"].to_numpy()

        rho, _ = spearmanr(base_ranks, scen_ranks)
        tau, _ = kendalltau(base_ranks, scen_ranks)

        scen_top_n_indices = set(np.where(scen_ranks <= top_n)[0])
        overlap_count = len(base_top_n_indices.intersection(scen_top_n_indices))
        overlap_pct = (overlap_count / top_n) * 100.0
        max_shift = int(np.max(np.abs(base_ranks - scen_ranks)))

        scenarios.append(
            {
                "scenario_id": f"S{j+1:02d}",
                "description": f"+{int(perturbation_pct*100)}% on {col_name}",
                "perturbed_criterion": col_name,
                "spearman_rho": round(float(rho), 4),
                "kendall_tau": round(float(tau), 4),
                "top5_overlap_pct": round(float(overlap_pct), 1),
                "max_rank_shift": max_shift,
            }
        )

    # Scenario 10: Equal weights across all criteria
    w_equal = np.ones(n, dtype=float) / n
    res_eq = compute_topsis_ranking(X, w_equal, criteria_types)
    eq_ranks = res_eq["rank"].to_numpy()
    rho_eq, _ = spearmanr(base_ranks, eq_ranks)
    tau_eq, _ = kendalltau(base_ranks, eq_ranks)
    eq_top_n = set(np.where(eq_ranks <= top_n)[0])
    eq_overlap = (len(base_top_n_indices.intersection(eq_top_n)) / top_n) * 100.0

    scenarios.append(
        {
            "scenario_id": "S10",
            "description": "Equal weights (1/N baseline)",
            "perturbed_criterion": "ALL_EQUAL",
            "spearman_rho": round(float(rho_eq), 4),
            "kendall_tau": round(float(tau_eq), 4),
            "top5_overlap_pct": round(float(eq_overlap), 1),
            "max_rank_shift": int(np.max(np.abs(base_ranks - eq_ranks))),
        }
    )

    # Scenario 11: Dominant Major Roads (50% to C1_Major_Roads, remainder split equally)
    w_road = np.full(n, 0.5 / (n - 1) if n > 1 else 1.0, dtype=float)
    road_idx = col_names.index("C1_Major_Roads") if "C1_Major_Roads" in col_names else 0
    w_road[road_idx] = 0.50
    w_road = w_road / np.sum(w_road)

    res_road = compute_topsis_ranking(X, w_road, criteria_types)
    road_ranks = res_road["rank"].to_numpy()
    rho_road, _ = spearmanr(base_ranks, road_ranks)
    tau_road, _ = kendalltau(base_ranks, road_ranks)
    road_top_n = set(np.where(road_ranks <= top_n)[0])
    road_overlap = (len(base_top_n_indices.intersection(road_top_n)) / top_n) * 100.0

    scenarios.append(
        {
            "scenario_id": "S11",
            "description": "Dominant Major Roads (50% weight)",
            "perturbed_criterion": "C1_Major_Roads_50PCT",
            "spearman_rho": round(float(rho_road), 4),
            "kendall_tau": round(float(tau_road), 4),
            "top5_overlap_pct": round(float(road_overlap), 1),
            "max_rank_shift": int(np.max(np.abs(base_ranks - road_ranks))),
        }
    )

    # Scenario 12: Dominant Shopping Malls (50% to C6_POI_Shopping_Malls, remainder split equally)
    w_mall = np.full(n, 0.5 / (n - 1) if n > 1 else 1.0, dtype=float)
    mall_idx = col_names.index("C6_POI_Shopping_Malls") if "C6_POI_Shopping_Malls" in col_names else min(3, n - 1)
    w_mall[mall_idx] = 0.50
    w_mall = w_mall / np.sum(w_mall)

    res_mall = compute_topsis_ranking(X, w_mall, criteria_types)
    mall_ranks = res_mall["rank"].to_numpy()
    rho_mall, _ = spearmanr(base_ranks, mall_ranks)
    tau_mall, _ = kendalltau(base_ranks, mall_ranks)
    mall_top_n = set(np.where(mall_ranks <= top_n)[0])
    mall_overlap = (len(base_top_n_indices.intersection(mall_top_n)) / top_n) * 100.0

    scenarios.append(
        {
            "scenario_id": "S12",
            "description": "Dominant Shopping Malls (50% weight)",
            "perturbed_criterion": "C6_POI_Shopping_Malls_50PCT",
            "spearman_rho": round(float(rho_mall), 4),
            "kendall_tau": round(float(tau_mall), 4),
            "top5_overlap_pct": round(float(mall_overlap), 1),
            "max_rank_shift": int(np.max(np.abs(base_ranks - mall_ranks))),
        }
    )

    sensitivity_df = pd.DataFrame(scenarios)

    if output_table_path is not None:
        output_table_path = Path(output_table_path)
        output_table_path.parent.mkdir(parents=True, exist_ok=True)
        sensitivity_df.to_csv(output_table_path, index=False)

    return sensitivity_df


def generate_mcdm_sensitivity_figure(
    sensitivity_df: pd.DataFrame,
    output_figure_path: Path = Path("outputs/figures/mcdm_sensitivity_analysis.png"),
) -> None:
    """Render publication-grade visualization of MCDM sensitivity analysis across 12 scenarios.

    Args:
        sensitivity_df: DataFrame generated by run_mcdm_criteria_sensitivity.
        output_figure_path: Destination path for rendered PNG figure.
    """
    output_figure_path = Path(output_figure_path)
    output_figure_path.parent.mkdir(parents=True, exist_ok=True)

    fig, ax1 = plt.subplots(figsize=(12, 6))

    scenarios = sensitivity_df["scenario_id"]
    x = np.arange(len(scenarios))
    width = 0.42

    # Primary axis: Spearman rho
    color1 = "#1f77b4"
    bars1 = ax1.bar(x - width / 2, sensitivity_df["spearman_rho"], width, label="Spearman Rank Correlation (ρ)", color=color1, alpha=0.85)
    ax1.set_xlabel("Sensitivity Scenario (Rashmitha et al., 2024 Framework)", fontsize=11, labelpad=10)
    ax1.set_ylabel("Spearman Rank Correlation (ρ)", fontsize=11, color=color1)
    ax1.tick_params(axis="y", labelcolor=color1)
    ax1.set_ylim(0.5, 1.05)
    ax1.set_xticks(x)
    ax1.set_xticklabels(scenarios, fontsize=10)
    ax1.grid(axis="y", linestyle="--", alpha=0.4)

    # Secondary axis: Top-5 Overlap %
    ax2 = ax1.twinx()
    color2 = "#2ca02c"
    bars2 = ax2.bar(x + width / 2, sensitivity_df["top5_overlap_pct"], width, label="Top-5 Shortlist Overlap (%)", color=color2, alpha=0.85)
    ax2.set_ylabel("Top-5 Shortlist Overlap (%)", fontsize=11, color=color2)
    ax2.tick_params(axis="y", labelcolor=color2)
    ax2.set_ylim(40, 110)

    # Title & Legends
    plt.title("MCDM Criteria Weight Sensitivity Analysis (TOPSIS-CRITIC Robustness)", fontsize=13, pad=15, fontweight="bold")
    
    # Combined legend
    lines1, labels1 = ax1.get_legend_handles_labels()
    lines2, labels2 = ax2.get_legend_handles_labels()
    ax1.legend(lines1 + lines2, labels1 + labels2, loc="lower left", frameon=True, facecolor="white", edgecolor="none")

    plt.tight_layout()
    plt.savefig(output_figure_path, dpi=300, bbox_inches="tight")
    plt.close()
