# Project Implementation Roadmap (`ev-siting-varanasi`)

This repository is built incrementally milestone-by-milestone across a multi-week engineering cadence. Each milestone addresses one focused phase of the two-stage EV charging station siting framework for Varanasi, India.

---

## Milestone 1 — Repository Scaffolding & Setup (Active / Current)
- Repository directory structure, standing agent rules (`AGENTS.md`), and environment templates.
- Python 3.11+ dependencies in `requirements.txt`.
- Fully typed Python stub modules across GIS, MCDM, ML, and Integration packages.
- Pytest testing harness and starter exploration notebooks.
- Authoritative documentation of confirmed vs. pending decisions (`docs/PENDING_DECISIONS.md`).

---

## Milestone 2 — GIS Pipeline: Spatial Data Processing & Decision Matrix
- Ingestion and preprocessing of Varanasi spatial layers (OSM roads/POIs, Census population data, Bhuvan land cover, power grid points, OpenChargeMap EV stations).
- Kernel Density Estimation (KDE) and Inverse Distance Weighting (IDW) raster surface generation.
- Candidate site buffer delineation (300m buffers around power substations).
- Spatial overlay and zonal statistics extraction to generate the standardized decision matrix ($m$ sites $\times$ $n$ criteria).

---

## Milestone 3 — MCDM Pipeline: Criteria Weighting & Site Ranking
- Implementation of CRITIC (primary) and Entropy (secondary) objective criteria weighting methods.
- Implementation of TOPSIS (primary) and WASPAS (cross-check) multi-criteria ranking algorithms.
- Validation of ranking stability against Indian case study benchmarks (Rashmitha et al., 2024).

---

## Milestone 4 — ML Demand Pipeline: XGBoost Training & SHAP Interpretability
- Verification, ingestion, and preprocessing of the public hourly EV charging session dataset.
- Training, hyperparameter tuning, and 5-fold cross-validation of XGBoost regression models (benchmarked against $R^2$ baselines from Zhang et al., 2025).
- Computation of SHAP global feature importances and local candidate site attributions.
- Generation of relative demand potential scores for Varanasi candidate site profiles.

---

## Milestone 5 — Two-Stage Integration & Sensitivity Analysis
- Normalization and synthesis of MCDM suitability scores and ML relative demand estimates into a single composite feasibility score.
- Evaluation of shortlist overlap and ranking divergence between the MCDM baseline and the composite framework.
- Implementation of the 12-scenario weight-perturbation sensitivity analysis ($\pm 10–20\%$).
- Generation of final ranked shortlists, summary tables, maps, and executive report deliverables.
