# Project Implementation Roadmap (`ev-siting-varanasi`)

This repository is built incrementally milestone-by-milestone across a multi-week engineering cadence. Each milestone addresses one focused phase of the two-stage EV charging station siting framework for Varanasi, India.

---

## Milestone 1 — Repository Scaffolding & Setup (Completed)
- Repository directory structure, standing agent rules (`AGENTS.md`), and environment templates.
- Python 3.11+ dependencies in `requirements.txt`.
- Fully typed Python stub modules across GIS, MCDM, ML, and Integration packages.
- Pytest testing harness and starter exploration notebooks.
- Authoritative documentation of confirmed vs. pending decisions (`docs/PENDING_DECISIONS.md`).

---

## Milestone 2 — GIS Pipeline: Spatial Data Processing & Decision Matrix (Completed — Confirmed Criteria)
- Implemented regular 500m fishnet candidate grid generation projected in metric UTM Zone 44N (`EPSG:32644`).
- Implemented automated OSM Overpass road network query and Euclidean distance-to-road proximity rasterization (1–9 scale).
- Implemented OpenChargeMap API integration for competitor charging station coverage scoring (1–9 KDE raster).
- Implemented generic, reusable Google Places API (New) fetcher for 7 confirmed POI categories (Schools, Shopping Malls, Restaurants, Hospitals, Theatres, Bus Stops, Petrol Bunks) with Gaussian Kernel Density Estimation (1–9 scale).
- Implemented spatial candidate overlay generating `data/processed/gis/decision_matrix.csv`.
- Maintained unconfirmed criteria (Population Density, Land Use/Cover, Land Cost, Substation Grid Proximity) as explicit stubs raising `NotImplementedError` per `docs/PENDING_DECISIONS.md`.
- Implemented mock-based unit test suite (`tests/test_gis.py`) passing with zero live network calls.

---

## Milestone 3 — MCDM Pipeline: Weighting & Ranking (Completed)
- Implemented objective criteria weighting algorithms in `src/mcdm/weighting.py`:
  - **CRITIC**: Standard deviation contrast intensity + Pearson intercriteria correlation conflict measure with robust zero-variance handling.
  - **Shannon Entropy**: Probability proportion transformation + information entropy divergence.
- Implemented multi-criteria alternative ranking algorithms in `src/mcdm/ranking.py`:
  - **TOPSIS**: Vector normalization + Euclidean distance to Positive-Ideal ($A^+$) and Negative-Ideal ($A^-$) solutions.
  - **WASPAS**: Linear normalization + joint Weighted Sum Model (WSM) and Weighted Product Model (WPM) scoring ($\lambda = 0.5$).
- Dynamic criteria column detection (filtering out metadata `site_id`, `latitude`, `longitude`).
- Implemented end-to-end pipeline orchestrator `run_mcdm_pipeline()` in `src/mcdm/pipeline.py` generating consolidated 4-combination ranking table at `outputs/tables/mcdm_rankings.csv`.
- Activated and expanded unit tests in `tests/test_mcdm.py` (16 total tests passing across GIS and MCDM).

---

## Milestone 4 & 4b — ML Demand Pipeline & Transferability-Constrained Siting Model (Completed)
- Ingested and preprocessed authentic EV charging sessions from the peer-reviewed **ACN-Data** dataset (Caltech + JPL sites; Lee, Li & Low, 2019).
- **Full-Feature Model (RQ2):** 5-fold CV on full feature set ($R^2 \approx 0.4832$, $\text{RMSE} \approx 7.93\text{ kWh}$); isolated charging duration as dominant demand driver (~75.8% SHAP weight). Artifacts: `outputs/models/demand_xgboost.pkl`, `outputs/reports/ml_training_metrics.md`.
- **Ex-Ante Transferable Model (Milestone 5 Siting):** 5-fold CV on strictly observable ex-ante features (`connection_hour`, `day_of_week`, `is_weekend`, `month`), yielding $R^2 \approx 0.0213$, $\text{RMSE} \approx 10.91\text{ kWh}$. Explicitly rejected heuristic dwell-time proxies per zero-fabrication rules (AD-6). Artifacts: `outputs/models/demand_xgboost_transferable.pkl`, `outputs/reports/ml_training_metrics_transferable.md`.
- Computed global SHAP attributions for both models (`outputs/figures/shap_summary*.png` and `outputs/tables/shap_feature_importance*.csv`).
- Activated unit tests in `tests/test_ml.py` (20 total unit tests passing with zero live network dependencies).

---

## Milestone 5 — Two-Stage Integration, Temporal Profiling & Sensitivity Analysis (Completed)
- **Spatial Primacy (*Where* to Site):** Established the Stage 2 GIS-MCDM TOPSIS-CRITIC ranking (`outputs/tables/mcdm_rankings.csv`) as the primary spatial site selection benchmark.
- **Operational Demand Profiling (*When* Demand Occurs):** Generated 24-hour diurnal load curves (weekday vs. weekend) from the transferable XGBoost model, saved to `outputs/tables/temporal_demand_curve.csv` and `outputs/figures/temporal_demand_curve.png`.
- **12-Scenario MCDM Sensitivity Analysis:** Evaluated weight perturbation robustness matching Rashmitha et al. (2024), demonstrating high shortlist stability ($\rho \ge 0.9613$ across S01–S11; 80–100% Top-5 candidate retention), saved to `outputs/tables/mcdm_sensitivity_results.csv` and `outputs/figures/mcdm_sensitivity_analysis.png`.
- **Formal RQ3 Resolution (AD-8):** Published comprehensive synthesis report at `outputs/reports/rq3_ranking_comparison.md`.
- **Unit Testing:** Implemented offline integration tests in `tests/test_integration.py` (23 total test cases passing).

---

## Milestone 6 — Full-Mode Citywide Run & Multi-Scale Validation (Completed)
- **Municipal Boundary Resolution:** Thoroughly explored administrative hierarchy; confirmed lack of OSM `admin_level=8` polygon and established an approximated 90-ward VMC municipal polygon ($76.99\text{ km}^2$, 308 clipped candidate sites @ 500m spacing; `data/raw/gis/varanasi_vmc_boundary.geojson`).
- **Resilient POI Fetching:** Deployed a 30-tile mesh (25 primary tiles $r=1,800\text{m}$ + 5 nested dense-core tiles $r=800\text{m}$) with `place_id` deduplication and incremental checkpoint disk caching (`data/raw/gis/full_run_cache/`), capturing 230–450+ unique POIs per category with 100% geometric candidate coverage.
- **Full-Mode Pipeline Execution:**
  - Full GIS Decision Matrix: `data/processed/gis/decision_matrix_full.csv` (308 sites $\times 12$ columns).
  - Full MCDM Rankings: `outputs/tables/mcdm_rankings_full.csv` (Top-5: `SITE_195` Godowlia/Girijaghar, `SITE_217` Dashashwamedh, `SITE_196` Godowlia North, `SITE_218` Vishwanath Corridor, `SITE_194` Sonarpura).
  - Full 12-Scenario Sensitivity Analysis: `outputs/tables/mcdm_sensitivity_results_full.csv` & `outputs/figures/mcdm_sensitivity_analysis_full.png` (100% Top-5 stability across S01–S10; revealed scale-dependent road proximity sensitivity in S11 with $\rho = 0.7763$).
- **Comparative Evaluation Report:** Synthesized sample-vs-full spatial transferability in `outputs/reports/sample_vs_full_comparison.md`, demonstrating core cluster persistence and score dynamic range expansion (0.2468 to 0.7782).


