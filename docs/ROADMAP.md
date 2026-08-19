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

## Milestone 3 — MCDM Pipeline: Criteria Weighting & Site Ranking (Next)
- Implementation of CRITIC (primary) and Entropy (secondary) objective criteria weighting methods.
- Implementation of TOPSIS (primary) and WASPAS (cross-check) multi-criteria ranking algorithms.
- Ingestion and processing of `data/processed/gis/decision_matrix.csv`.
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
