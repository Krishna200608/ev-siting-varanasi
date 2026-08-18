# EV Siting Varanasi (`ev-siting-varanasi`)

A data-driven, two-stage decision-support framework for Electric Vehicle (EV) charging station site selection and demand forecasting in Varanasi, India. Developed as a semester research project for **Managing Corporate Entrepreneurship**, this framework integrates spatial Multi-Criteria Decision-Making (MCDM) for physical site suitability with explainable Machine Learning (ML) for relative demand estimation, supporting entrepreneurial capital allocation and de-risking infrastructure deployment in under-studied Tier-2 Indian cities.

---

## 1. Pipeline Overview

The project combines two independent methodological pipelines that merge in the final evaluation phase:

```
[ Pipeline A: Spatial GIS & MCDM ]                 [ Pipeline B: ML Demand Forecasting ]
1. Raw GIS Layers (OSM, Bhuvan, Census)            1. Public EV Charging Dataset (Hourly)
2. Raster Surfaces (KDE & IDW)                     2. Feature Cleaning & Encoding
3. Candidate Buffers (300m at Substations)         3. XGBoost Training (5-fold CV)
4. Decision Matrix Generation                      4. SHAP Feature Attribution
5. CRITIC / Entropy Weighting                      5. Relative Demand Inference
6. TOPSIS / WASPAS Site Ranking                    
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
| `config/criteria.yaml` | Configuration | Defines MCDM criteria, categories, optimization directions, and parameters. |
| `data/raw/gis/` | Pipeline A: Data Ingestion | Raw spatial data: OSM shapefiles/GeoJSON, Census population, Bhuvan land cover. |
| `data/raw/demand/` | Pipeline B: Data Ingestion | External public hourly EV charging session dataset (e.g., California / Kaggle). |
| `data/processed/gis/` | Pipeline A: GIS Preprocessing | Standardized raster surfaces and generated decision matrix (`decision_matrix.csv`). |
| `data/processed/demand/` | Pipeline B: ML Preprocessing | Cleaned feature matrices and target demand vectors. |
| `src/gis/` | Pipeline A: Stage 1 | GIS layer loading, KDE/IDW rasterization, buffer generation, zonal stats extraction. *(Rashmitha et al., 2024)* |
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

### Option A: Standard Setup via `pip`
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

### Option B: Conda / Mamba Setup (Recommended for Windows GDAL/Rasterio)
`geopandas` and `rasterio` depend on underlying C/C++ GDAL, GEOS, and PROJ binaries. On Windows, if `pip install` encounters binary compilation errors, use Conda/Mamba:
```bash
conda create -n ev-siting python=3.11
conda activate ev-siting
conda install -c conda-forge geopandas rasterio shapely xgboost shap scikit-learn pandas pyyaml matplotlib jupyter pytest
```

### Configuration
Copy the environment template and configure optional API keys if needed:
```bash
cp .env.example .env
```

---

## 4. Running Tests

To verify the test harness:
```bash
pytest tests/ -v
```
*(Note: In Milestone 1, unit tests are cleanly marked as skipped until logic is implemented in Milestones 3 and 4.)*

---

## 5. Documentation & Key Links

- **Implementation Roadmap:** See [docs/ROADMAP.md](docs/ROADMAP.md) for milestone schedules.
- **Data Sourcing & Pending Decisions:** Consult [docs/PENDING_DECISIONS.md](docs/PENDING_DECISIONS.md) before referencing data sources.
- **Standing Agent Rules:** Review [AGENTS.md](AGENTS.md) for coding conventions and policies.
