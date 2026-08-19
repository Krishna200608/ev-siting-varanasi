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

## Milestone 5 — Two-Stage Integration & Sensitivity Analysis (Next)
- Normalization and synthesis of MCDM suitability scores and ML relative demand estimates into a single composite feasibility score.
- Evaluation of shortlist overlap and ranking divergence between the MCDM baseline and the composite framework.
- Implementation of the 12-scenario weight-perturbation sensitivity analysis ($\pm 10–20\%$).
- Generation of final ranked shortlists, summary tables, maps, and executive report deliverables.
