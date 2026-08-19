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
6. CRITIC / Entropy Weighting (Milestone 3)
7. TOPSIS / WASPAS Site Ranking (Milestone 3)
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
| `config/criteria.yaml` | Configuration | Defines MCDM criteria, execution mode (`sample` vs `full`), and parameters. |
| `data/raw/gis/` | Pipeline A: Data Ingestion | Raw spatial data: OSM shapefiles/GeoJSON, Census population, Bhuvan land cover. |
| `data/raw/demand/` | Pipeline B: Data Ingestion | External public hourly EV charging session dataset (e.g., California / Kaggle). |
| `data/processed/gis/` | Pipeline A: GIS Preprocessing | Generated decision matrix (`decision_matrix.csv`). |
| `data/processed/demand/` | Pipeline B: ML Preprocessing | Cleaned feature matrices and target demand vectors. |
| `src/gis/` | Pipeline A: Stage 1 | GIS candidate grid generation, KDE/distance rasterization, spatial overlay. *(Rashmitha et al., 2024)* |
| `src/mcdm/` | Pipeline A: Stage 2 | Objective weighting (CRITIC / Entropy) and multi-criteria ranking (TOPSIS / WASPAS). *(Rashmitha et al., 2024; Guo & Zhao, 2015)* |
| `src/ml/` | Pipeline B: Stage 3 | XGBoost regression training, cross-validation, and SHAP explainability. *(Zhang et al., 2025)* |
| `src/integration/` | Stage 4: Synthesis | Composite feasibility scoring and 12-scenario weight-perturbation sensitivity testing. |
| `notebooks/` | Exploration | Step-by-step interactive Jupyter notebooks for GIS, MCDM, and ML phases. |
| `outputs/` | Deliverables | Generated figures (SHAP plots, suitability maps), ranking tables, and reports. |
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

## 4. Running the GIS Pipeline (Milestone 2)

### Execution Modes (`sample` vs. `full`)
In `config/criteria.yaml`, you can configure the `mode` parameter:
- **`mode: "sample"` (Default):** Restricts the spatial fishnet grid to a small bounding box (~2.5 km $\times$ 2.7 km) covering central Varanasi (Godowlia / Dashashwamedh / Cantonment). This minimizes Google Places API quota usage while generating an authentic decision matrix for testing.
- **`mode: "full"`:** Queries OpenStreetMap Nominatim for the entire municipal extent of Varanasi and generates a city-wide fishnet grid.

### Execute Decision Matrix Generation
```bash
python src/gis/build_decision_matrix.py
```
Output:
The processed decision matrix is saved to `data/processed/gis/decision_matrix.csv`.

---

## 5. Running Tests

To run the complete test suite (with zero live network calls):
```bash
pytest tests/ -v
```

---

## 6. Documentation & Key Links

- **Implementation Roadmap:** See [docs/ROADMAP.md](docs/ROADMAP.md) for milestone status.
- **Data Sourcing & Pending Decisions:** Consult [docs/PENDING_DECISIONS.md](docs/PENDING_DECISIONS.md) for authoritative data source statuses and architectural decisions.
- **Standing Agent Rules:** Review [AGENTS.md](AGENTS.md) for coding conventions and policies.
