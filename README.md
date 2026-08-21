# EV Siting Varanasi (`ev-siting-varanasi`)

A data-driven, two-stage decision-support framework for Electric Vehicle (EV) charging station site selection and demand forecasting in Varanasi, India. Developed as a semester research project for **Managing Corporate Entrepreneurship**, this framework integrates spatial Multi-Criteria Decision-Making (MCDM) for physical site suitability with explainable Machine Learning (ML) for relative demand estimation, supporting entrepreneurial capital allocation and de-risking infrastructure deployment in under-studied Tier-2 Indian cities.

---

## 1. Pipeline Overview

The project combines two independent methodological pipelines that merge in the final evaluation phase:

```
[ Pipeline A: Spatial GIS & MCDM ]                 [ Pipeline B: ML Demand Forecasting ]
1. Candidate Fishnet Grid (500m UTM 44N)           1. Public EV Charging Dataset (Hourly)
2. Road Network Proximity (OSM Overpass)           2. Feature Cleaning & Encoding
3. Competitor EV Density (OpenChargeMap)           3. XGBoost Training (5-fold CV)
4. POI Density Surfaces (Google Places New API)    4. SHAP Feature Attribution
5. Candidate Overlay -> Decision Matrix            5. Relative Demand Inference
6. CRITIC / Entropy Weighting (Completed)
7. TOPSIS / WASPAS Site Ranking (Completed)
                       │                                         │
                       └───────────────────┬─────────────────────┘
                                           ▼
                       [ Stage 4: Integration & Robustness ]
                       1. Composite Feasibility Scoring
                       2. Shortlist Overlap & Divergence Analysis
                       3. 12-Scenario Sensitivity Analysis (±10–20%)
                       4. Final Decision-Grade Ranked Shortlist
```

---

## 2. Directory Structure & Synopsis Mapping

| Directory / File | Synopsis Stage / Pipeline | Purpose & Theoretical Basis |
|---|---|---|
| `config/criteria.yaml` | Configuration | Defines MCDM criteria, orientation types (`benefit` vs `cost`), execution mode (`sample` vs `full`), and parameters. |
| `data/raw/gis/` | Pipeline A: Data Ingestion | Raw spatial data: OSM shapefiles/GeoJSON, Census population, Bhuvan land cover. |
| `data/raw/demand/` | Pipeline B: Data Ingestion | External public hourly EV charging session dataset (e.g., California / Kaggle). |
| `data/processed/gis/` | Pipeline A: GIS Preprocessing | Generated decision matrix (`decision_matrix.csv`). |
| `data/processed/demand/` | Pipeline B: ML Preprocessing | Cleaned feature matrices and target demand vectors. |
| `src/gis/` | Pipeline A: Stage 1 | GIS candidate grid generation, KDE/distance rasterization, spatial overlay. *(Rashmitha et al., 2024)* |
| `src/mcdm/` | Pipeline A: Stage 2 | Objective weighting (CRITIC / Entropy) and multi-criteria ranking (TOPSIS / WASPAS). *(Rashmitha et al., 2024; Guo & Zhao, 2015)* |
| `src/ml/` | Pipeline B: Stage 3 | XGBoost regression training, cross-validation, and SHAP explainability. *(Zhang et al., 2025)* |
| `src/integration/` | Stage 4: Synthesis | Composite feasibility scoring and 12-scenario weight-perturbation sensitivity testing. |
| `notebooks/` | Exploration | Step-by-step interactive Jupyter notebooks for GIS, MCDM, and ML phases. |
| `outputs/` | Deliverables | Consolidated ranking tables (`outputs/tables/mcdm_rankings.csv`), SHAP plots, suitability maps. |
| `tests/` | Quality Assurance | Pytest test suites verifying mathematical properties and data integrity. |
| `docs/ROADMAP.md` | Governance | Multi-week implementation roadmap across Milestones 1 to 5. |
| `docs/PENDING_DECISIONS.md` | Governance | Authoritative list of confirmed vs. pending data sources and architectural decisions. |
| `AGENTS.md` | Standing Rules | Coding standards, type-hinting rules, and zero-assumption data policies for AI agents. |

---

## 3. Environment Setup & Installation

### Prerequisites
- **Python:** 3.11 or higher recommended.
- **Package Manager:** `pip` (or `conda` / `mamba` for precompiled GIS binaries).

### Setup via `pip`
```bash
# 1. Navigate to the project root
cd ev-siting-varanasi

# 2. Create and activate a virtual environment
python -m venv .venv
# On Windows (PowerShell):
.\.venv\Scripts\Activate.ps1
# On Linux/macOS:
source .venv/bin/activate

# 3. Upgrade pip and install dependencies
pip install --upgrade pip
pip install -r requirements.txt
```

### Configuration & API Keys
Copy the environment template and populate your API keys in `.env`:
```bash
cp .env.example .env
```
Key requirements:
- `GOOGLE_PLACES_API_KEY`: Required for fetching POI layers via Google Places API (New).
- `OPENCHARGEMAP_API_KEY`: Required for fetching existing EV charging stations via OpenChargeMap.

---

## 4. Running the Pipelines

### Pipeline A — Stage 1: GIS Decision Matrix Builder
```bash
python src/gis/build_decision_matrix.py
```
Output: `data/processed/gis/decision_matrix.csv` (dynamically extracted spatial criteria scores).

### Pipeline A — Stage 2: MCDM Weighting & Ranking
```bash
python -c "from src.mcdm.pipeline import run_mcdm_pipeline; run_mcdm_pipeline()"
```
Output: `outputs/tables/mcdm_rankings.csv` containing candidate coordinates, suitability scores, and ranks across all 4 combinations:
- `topsis_critic_score`, `topsis_critic_rank` (Primary academic benchmark)
- `topsis_entropy_score`, `topsis_entropy_rank`
- `waspas_critic_score`, `waspas_critic_rank`
- `waspas_entropy_score`, `waspas_entropy_rank`

### Pipeline B — Stage 3: ML Demand Forecasting & SHAP Explainability

#### 1. Full-Feature Descriptive Model (General Demand Drivers — RQ2)
```bash
python -c "from src.ml.train_demand_model import train_and_save_pipeline; from src.ml.explain import generate_shap_artifacts; model, X, metrics = train_and_save_pipeline(); generate_shap_artifacts(model, X)"
```
- **Trained Model:** `outputs/models/demand_xgboost.pkl` ($R^2 \approx 0.4832$, $\text{RMSE} \approx 7.93\text{ kWh}$)
- **Evaluation Report:** `outputs/reports/ml_training_metrics.md`
- **SHAP Summary Plot:** `outputs/figures/shap_summary.png`
- **Feature Importance Table:** `outputs/tables/shap_feature_importance.csv`

#### 2. Ex-Ante Transferable Model (Operational Siting Model — Milestone 5)
```bash
python -c "from src.ml.train_demand_model import train_and_save_transferable_pipeline; from src.ml.explain import generate_shap_artifacts; model, X, metrics = train_and_save_transferable_pipeline(); generate_shap_artifacts(model, X, 'outputs/figures/shap_summary_transferable.png', 'outputs/tables/shap_feature_importance_transferable.csv')"
```
- **Trained Model:** `outputs/models/demand_xgboost_transferable.pkl` ($R^2 \approx 0.0213$, $\text{RMSE} \approx 10.91\text{ kWh}$)
- **Evaluation Report:** `outputs/reports/ml_training_metrics_transferable.md`
- **SHAP Summary Plot:** `outputs/figures/shap_summary_transferable.png`
- **Feature Importance Table:** `outputs/tables/shap_feature_importance_transferable.csv`

### Stage 4: Two-Stage Integration, Temporal Profiling & Robustness (Sample Mode)
```bash
python src/integration/pipeline.py
```
Generated Deliverables:
- **Formal Synthesis Report (RQ3):** `outputs/reports/rq3_ranking_comparison.md` (Direct RQ3 evaluation and MCDM spatial primacy documentation)
- **Diurnal Demand Curve:** `outputs/tables/temporal_demand_curve.csv` & `outputs/figures/temporal_demand_curve.png` (24-hour weekday vs weekend load profile)
- **12-Scenario Sensitivity Analysis:** `outputs/tables/mcdm_sensitivity_results.csv` & `outputs/figures/mcdm_sensitivity_analysis.png` (TOPSIS-CRITIC stability across criteria perturbations)

### Milestone 6: Full-Mode Citywide Pipeline Execution (308 Sites, 76.99 km²)
To run the full-mode citywide pipeline across Varanasi's complete municipal extent:
```bash
# 1. Build full decision matrix (308 sites x 12 columns)
python -c "from src.gis.build_decision_matrix import build_decision_matrix; build_decision_matrix(mode='full')"

# 2. Run full MCDM ranking (all 4 combinations on 308 sites)
python -c "from src.mcdm.pipeline import run_mcdm_pipeline; run_mcdm_pipeline(decision_matrix_path='data/processed/gis/decision_matrix_full.csv', output_table_path='outputs/tables/mcdm_rankings_full.csv')"

# 3. Run full-scale 12-scenario sensitivity analysis
python -c "import pandas as pd; from src.integration.sensitivity_analysis import run_mcdm_criteria_sensitivity, generate_mcdm_sensitivity_figure; df = pd.read_csv('data/processed/gis/decision_matrix_full.csv'); cols = [c for c in df.columns if c not in ['site_id', 'latitude', 'longitude']]; types = ['benefit', 'cost', 'benefit', 'benefit', 'benefit', 'benefit', 'benefit', 'benefit', 'benefit']; s = run_mcdm_criteria_sensitivity(df[cols], types, output_table_path='outputs/tables/mcdm_sensitivity_results_full.csv'); generate_mcdm_sensitivity_figure(s, 'outputs/figures/mcdm_sensitivity_analysis_full.png')"
```
Full-Mode Deliverables:
- **Full Decision Matrix:** `data/processed/gis/decision_matrix_full.csv` (308 sites $\times 12$ columns)
- **Full MCDM Rankings:** `outputs/tables/mcdm_rankings_full.csv` (Top-5: `SITE_195`, `SITE_217`, `SITE_196`, `SITE_218`, `SITE_194`)
- **Full Sensitivity Analysis:** `outputs/tables/mcdm_sensitivity_results_full.csv` & `outputs/figures/mcdm_sensitivity_analysis_full.png`
- **Sample vs. Full Comparative Report:** `outputs/reports/sample_vs_full_comparison.md`

### Milestone 7: Equal-Scrutiny Multi-Zone Validation (Sigra, Lanka, Cantt)
To run the equal-scrutiny pipeline with 5 nested tiles ($r=800\text{m}$) across all 4 major commercial nodes:
```bash
# 1. Build equal-scrutiny decision matrix (v2)
python -c "from src.gis.build_decision_matrix import build_decision_matrix; build_decision_matrix(mode='full_v2')"

# 2. Run equal-scrutiny MCDM ranking (v2)
python -c "from src.mcdm.pipeline import run_mcdm_pipeline; run_mcdm_pipeline(decision_matrix_path='data/processed/gis/decision_matrix_full_v2.csv', output_table_path='outputs/tables/mcdm_rankings_full_v2.csv')"

# 3. Run equal-scrutiny 12-scenario sensitivity analysis (v2)
python -c "import pandas as pd; from src.integration.sensitivity_analysis import run_mcdm_criteria_sensitivity, generate_mcdm_sensitivity_figure; df = pd.read_csv('data/processed/gis/decision_matrix_full_v2.csv'); cols = [c for c in df.columns if c not in ['site_id', 'latitude', 'longitude']]; types = ['benefit', 'cost', 'benefit', 'benefit', 'benefit', 'benefit', 'benefit', 'benefit', 'benefit']; s = run_mcdm_criteria_sensitivity(df[cols], types, output_table_path='outputs/tables/mcdm_sensitivity_results_full_v2.csv'); generate_mcdm_sensitivity_figure(s, 'outputs/figures/mcdm_sensitivity_analysis_full_v2.png')"
```
Equal-Scrutiny Deliverables:
- **Decision Matrix (v2):** `data/processed/gis/decision_matrix_full_v2.csv`
- **MCDM Rankings (v2):** `outputs/tables/mcdm_rankings_full_v2.csv` (Top-5: `SITE_195`, `SITE_217`, `SITE_218`, `SITE_196`, `SITE_194`)
- **Sensitivity Analysis (v2):** `outputs/tables/mcdm_sensitivity_results_full_v2.csv` & `outputs/figures/mcdm_sensitivity_analysis_full_v2.png`
- **Validation Report:** `outputs/reports/equal_scrutiny_validation.md` (Definitive confirmation that Godowlia primacy is a genuine urban concentration)

### Milestone 8: Interactive Streamlit Showcase & What-If Dashboard
An interactive, dependency-light web dashboard designed for viva presentations, stakeholder demonstrations, and cloud deployment:

```bash
# Launch the dashboard locally from repository root
streamlit run dashboard/app.py
```

#### Dashboard Architecture & Page Guide:
- **`app.py` (Home & Overview):** Executive summary, two-stage framework structure, and headline urban metrics (308 candidate alternatives, 0 existing public EV fast-chargers, Top site score).
- **`1_Site_Map.py` (Interactive Site Map):** Full-screen Folium map with dynamic suitability color coding, Top-5 distinctive markers, click-to-view criteria popups, and a v1 vs. v2 spatial scrutiny toggle.
- **`2_MCDM_Rankings.py` (MCDM Rankings Table):** Sortable and filterable table across all 4 MCDM combinations (TOPSIS/WASPAS $\times$ CRITIC/Entropy) with urban zone filters and CSV export.
- **`3_Whatif_Weight_Explorer.py` (Live What-If Explorer):** Interactive sensitivity tool with 9 criteria sliders (defaulted to empirical CRITIC weights) performing sub-second live TOPSIS re-ranking and rank-shift scatter analytics.
- **`4_Demand_and_SHAP.py` (Demand & SHAP):** 24-hour diurnal energy demand curves (weekday vs. weekend), SHAP feature attribution plots, and methodological synthesis on operational timing (RQ3).
- **`5_Sensitivity_Analysis.py` (Sensitivity Analysis):** 12-scenario criteria weight perturbation analysis, radar/line plots, and scale-dependent road proximity dynamics ($S_{11}$).
- **`6_Data_Quality_Audit.py` (Data Quality Audit):** Systematic 9-criteria $\times$ 2-version audit table, root-cause diagnostics on $C_5$ and $C_6$, and automated pipeline safeguard documentation.
- **`7_Project_Journey.py` (Project Journey):** Grounded chronological chronicle of key architectural decisions (AD-1 through AD-11) documenting problems tried, empirical findings, and verified solutions.

---

## 5. Running Tests

To run the complete automated test suite (32 unit and integration tests covering GIS, MCDM, ML, Sensitivity, Data Quality Safeguards, and Dashboard components with zero live network calls):
```bash
pytest tests/ -v
```

---

## 6. Documentation & Key Links

- **Implementation Roadmap:** See [docs/ROADMAP.md](docs/ROADMAP.md) for milestone status.
- **Data Sourcing & Pending Decisions:** Consult [docs/PENDING_DECISIONS.md](docs/PENDING_DECISIONS.md) for authoritative data source statuses and architectural decisions (AD-1 through AD-11).
- **Standing Agent Rules:** Review [AGENTS.md](AGENTS.md) for coding conventions and policies.
- **Public GitHub Repository:** [https://github.com/Krishna200608/ev-siting-varanasi](https://github.com/Krishna200608/ev-siting-varanasi)

