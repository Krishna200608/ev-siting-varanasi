# Research Question 3 (RQ3) Evaluation & Framework Synthesis Report

**Project Title:** Two-Stage Decision-Support Framework for EV Charging Station Siting in Varanasi  
**Academic Context:** Managing Corporate Entrepreneurship (Semester Project)  
**Primary Theoretical Foundation:** Rashmitha, Sushma & Roy (2024); Zhang, Peng & Zeng (2025); Lee, Li & Low (2019)  

---

## 1. Direct Resolution to Research Question 3 (RQ3)

### The Research Question
> **RQ3:** *Does integrating Machine Learning demand forecasting alter or improve spatial Multi-Criteria Decision-Making (MCDM) site suitability recommendations for EV charging infrastructure in Varanasi?*

### The Empirical & Methodological Finding
**Direct Answer:** Within the boundary of publicly available, non-confidential charging telemetry (ACN-Data), **ML demand estimation cannot be localized to individual candidate sites without either fabricating unsupported heuristic proxies or redundantly double-counting GIS criteria.** 

Consequently, the framework establishes a methodologically rigorous separation of concerns:
1. **Spatial Dimension (*Where* to Site — MCDM Primacy):** The spatial suitability ranking of candidate sites is governed definitively by the **GIS-MCDM Stage 2 pipeline** (TOPSIS-CRITIC). Spatial criteria (road network proximity, competitor deficits, and multimodal POI density) capture the vast majority of actionable, physically observable information available prior to station construction.
2. **Temporal Dimension (*When* Demand Occurs — Operational ML Profiling):** The **transferable XGBoost demand model** provides city-wide operational timing intelligence. It predicts diurnal load curves across 24-hour cycles to inform dynamic tariff scheduling, electrical transformer capacity planning, and operational staffing at whichever candidate sites are selected.

---

## 2. Definitive Spatial Site Prioritization (Top-5 Ranked Candidates)

The operative candidate site shortlist for EV charging station deployment in Varanasi is determined by the **TOPSIS-CRITIC** primary benchmark (validated across Entropy weighting and WASPAS ranking):

| site_id | latitude | longitude | topsis_critic_score | topsis_critic_rank | topsis_entropy_rank | waspas_critic_rank | waspas_entropy_rank |
| --- | --- | --- | --- | --- | --- | --- | --- |
| SITE_012 | 25.3247 | 82.9974 | 0.5392 | 1 | 2 | 2 | 2 |
| SITE_004 | 25.3158 | 82.9923 | 0.5267 | 2 | 5 | 1 | 3 |
| SITE_018 | 25.3247 | 83.0024 | 0.5155 | 3 | 1 | 5 | 1 |
| SITE_015 | 25.3111 | 83.0022 | 0.5131 | 4 | 4 | 4 | 4 |
| SITE_003 | 25.3113 | 82.9923 | 0.4794 | 5 | 7 | 3 | 5 |

### Key Geographic Characteristics of Top Candidates:
- **`SITE_012` (Rank 1):** High accessibility along major arterial corridors with well-balanced multimodal POI support and zero immediate competitor saturation.
- **`SITE_004` (Rank 2):** High commercial agglomeration (shopping malls, entertainment/theatres, and retail dining).
- **`SITE_018` (Rank 3):** Transit-oriented node with strong bus stop and hospital accessibility.
- **`SITE_015` (Rank 4):** Central urban mixed-use cluster with balanced educational and commercial footfall.
- **`SITE_003` (Rank 5):** High fuel station co-location potential along secondary arterial routes.

---

## 3. Operational Demand Profiling (*When* Demand Occurs)

Evaluated across a 24-hour diurnal cycle using the transferability-constrained XGBoost model:
- **Weekday Peak Arrival Hour:** 12:00 (17.77 kWh predicted session demand).
- **Diurnal Dynamic Range:** Energy demand ranges from a low of 5.08 kWh (off-peak night/early morning) to 17.77 kWh (peak daytime commute), providing a clear empirical foundation for **time-of-use (ToU) electricity tariffs**.
- **Deliverables:** Data table saved to [`outputs/tables/temporal_demand_curve.csv`](../tables/temporal_demand_curve.csv) and visualized in [`outputs/figures/temporal_demand_curve.png`](../figures/temporal_demand_curve.png).

---

## 4. Multi-Scenario MCDM Sensitivity Analysis (Robustness Check)

Following Rashmitha et al. (2024), 12 weight-perturbation scenarios ($\pm 20\%$, equal weighting, and single-criterion dominance) were evaluated against the base TOPSIS-CRITIC ranking:

| scenario_id | description | spearman_rho | kendall_tau | top5_overlap_pct | max_rank_shift |
| --- | --- | --- | --- | --- | --- |
| S01 | +20% on C1_Major_Roads | 1.0000 | 1.0000 | 100.0 | 0 |
| S02 | +20% on C5_Competitor_EVCS | 1.0000 | 1.0000 | 100.0 | 0 |
| S03 | +20% on C6_POI_Schools | 0.9973 | 0.9770 | 100.0 | 2 |
| S04 | +20% on C6_POI_Shopping_Malls | 0.9982 | 0.9816 | 100.0 | 1 |
| S05 | +20% on C6_POI_Restaurants | 0.9871 | 0.9310 | 80.0 | 3 |
| S06 | +20% on C6_POI_Hospitals | 0.9929 | 0.9586 | 100.0 | 3 |
| S07 | +20% on C6_POI_Theatres | 0.9924 | 0.9540 | 80.0 | 3 |
| S08 | +20% on C6_POI_Bus_Stops | 0.9996 | 0.9954 | 100.0 | 1 |
| S09 | +20% on C6_POI_Petrol_Bunks | 0.9978 | 0.9816 | 100.0 | 2 |
| S10 | Equal weights (1/N baseline) | 0.9942 | 0.9632 | 100.0 | 3 |
| S11 | Dominant Major Roads (50% weight) | 0.9613 | 0.8759 | 100.0 | 7 |
| S12 | Dominant Shopping Malls (50% weight) | 0.7615 | 0.5816 | 60.0 | 16 |

### Sensitivity Findings:
- **High Rank Stability (Scenarios S01–S11):** Under individual criterion perturbations of $\pm 20\%$, equal weights, and dominant road weighting, Spearman rank correlation remains exceptionally high ($\rho \ge 0.9613$) with **80% to 100% Top-5 candidate retention**.
- **Extreme Commercial Dominance (Scenario S12):** When shopping malls are forced to 50% total weight, $\rho = 0.7615$ with 60% Top-5 retention, correctly reflecting that commercial-heavy sites (`SITE_004`) gain precedence over road-heavy nodes.
- **Visual Deliverable:** Visualization exported to [`outputs/figures/mcdm_sensitivity_analysis.png`](../figures/mcdm_sensitivity_analysis.png).
