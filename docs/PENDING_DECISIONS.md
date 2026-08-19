# Pending Decisions & Data Sourcing Inventory (`ev-siting-varanasi`)

This document is the **authoritative reference** for confirmed data sources, resolved architectural decisions, and pending/unverified items. Contributors and AI agents must strictly adhere to these classifications — do not fabricate, assume, or bypass unverified items.

---

## 1. Resolved / Architectural Decisions

### AD-1: Candidate Site Generation Method (Fishnet Grid)
- **Decision:** Generate candidate site alternatives as a **regular fishnet spatial grid** of points (spacing configurable, default 500 meters, projected in metric UTM Zone 44N / `EPSG:32644`) across Varanasi's urban boundary.
- **Deviation from Source Paper:** Rashmitha et al. (2024) placed 300m buffers around power grid substations in Telangana.
- **Rationale for Deviation:** Official GIS coordinates for electrical substations in Varanasi remain on the pending list. Rather than fabricating unverified substation locations, a regular spatial grid provides unbiased, continuous territorial coverage across the city, allowing suitability and demand scores to be evaluated uniformly across candidate coordinate points.

### AD-2: API Quota & Runtime Control (`sample` vs. `full` Mode)
- **Decision:** Introduce a dual execution mode (`sample` vs. `full`) in `config/criteria.yaml`.
- **Rationale:** `sample` mode restricts queries to a ~1.5 km² bounding box covering central Varanasi landmarks (Godowlia / Dashashwamedh corridor), enabling full end-to-end integration and verification without consuming excessive Google Places API quota during development and automated runs.

### AD-3: MCDM Dual Weighting & Ranking Scope (Resolved in Milestone 3)
- **Decision:** Implement all 4 algorithmic combinations ($\text{CRITIC} / \text{Entropy} \times \text{TOPSIS} / \text{WASPAS}$) and export composite ranking matrices with Spearman correlation checks, matching Rashmitha et al. (2024).

### AD-4: Empirical Rejection of Synthetic Kaggle Dataset & Transition to ACN-Data (Milestone 4)
- **Empirical Rejection of Kaggle Dataset (`valakhorasani/electric-vehicle-charging-patterns`):**
  - Downloaded and analyzed 1,320 records across 20 features.
  - Rigorous 5-fold cross-validation yielded $R^2 \approx -0.04$ and $\text{RMSE} \approx 22.87\text{ kWh}$ across Linear Regression, Random Forest, and XGBoost Regressor.
  - Feature-target correlation analysis showed all feature correlations with energy consumed were $< 0.05$.
  - **Conclusion:** The dataset is synthetic/randomly generated tutorial noise rather than real EV charging telemetry, lacking physical/behavioral predictive signal. Retaining it would violate project scientific standards.
- **Replacement Selection (ACN-Data):**
  - Selected **ACN-Data** (Caltech Adaptive Charging Network; Lee, Li & Low, 2019, *ACM e-Energy '19*), a real, peer-reviewed public dataset of EV charging sessions from Caltech, JPL, and Office-1 sites.
  - Real fields include `connectionTime`, `disconnectTime`, `kWhDelivered`, `doneChargingTime`, `userInputs`, `siteID`, `stationID`, `spaceID`.
- **Blocking Status:**
  - ACN-Data API requires free user registration at `https://ev.caltech.edu/dataset` to obtain an `ACNDATA_API_TOKEN`.
  - Contributor must register, obtain token, and add `ACNDATA_API_TOKEN=<token>` to `.env`.

---

## 2. Confirmed Data Sources & Implemented APIs
*(Safe to reference by name and implemented in `src/gis/build_decision_matrix.py`)*

- **OpenStreetMap (Overpass API):** Road network layers (motorway, trunk, primary, secondary, tertiary roads) for accessibility and road proximity raster surfaces.
- **OpenChargeMap API:** Existing public EV charging station locations used for competition and coverage deficit scoring.
- **Google Places API (Nearby Search):** Reusable Point of Interest (POI) fetcher for 7 confirmed urban categories:
  1. Schools (`school`)
  2. Shopping Malls (`shopping_mall`)
  3. Restaurants (`restaurant`)
  4. Hospitals (`hospital`)
  5. Theatres (`movie_theater`)
  6. Transit / Bus Stops (`transit_station`)
  7. Petrol Bunks (`gas_station`)

---

## 3. Pending / Unverified Data Sources & Decisions
*(Must be verified before implementation; do NOT assume or fabricate)*

1. **ACN-Data API Token (`ACNDATA_API_TOKEN`):**
   - *Status:* Blocked on Manual Token Acquisition.
   - *Manual Action:* Contributor must register at `https://ev.caltech.edu/dataset` and add `ACNDATA_API_TOKEN=<token>` to `.env`.

2. **Population Density Data (Census of India 2011):**
   - *Status:* Pending Manual Acquisition / Verification.
   - *Resolution Finding:* No clean, automated public REST API exists for ward-level Census 2011 demographic shapefiles for Varanasi.
   - *Manual Acquisition Steps:*
     1. Download District Census Handbook (DCHB) for Varanasi (2011 Census).
     2. Obtain Varanasi ward boundary GeoJSON/Shapefile from Municipal Corporation portal or Census GIS portal.
     3. Join ward population totals to ward polygons and interpolate to continuous raster using Inverse Distance Weighting (IDW).
   - *Code Status:* Stubbed with `NotImplementedError` in `src/gis/build_decision_matrix.py`.

3. **Land Use / Land Cover (LULC) Data:**
   - *Status:* Pending Manual Acquisition / Verification.
   - *Resolution Finding:* ISRO Bhuvan requires interactive portal authentication; Esri 10m Sentinel-2 LULC requires manual raster tile downloads.
   - *Manual Acquisition Steps:*
     1. Access Esri 10m Annual Land Use/Land Cover portal (or Copernicus Global Land Service).
     2. Download GeoTIFF tile covering Varanasi bounding box (`EPSG:4326` or `EPSG:32644`).
     3. Place raster in `data/raw/gis/varanasi_lulc.tif` and reclassify land classes (commercial=9, mixed=7, residential=5, agricultural=3, water/forest=1).
   - *Code Status:* Stubbed with `NotImplementedError` in `src/gis/build_decision_matrix.py`.

4. **Varanasi / UP Land Cost Data Sourcing:**
   - *Status:* Pending / Unconfirmed.
   - *Details:* Uttar Pradesh has no confirmed state land-valuation GIS portal equivalent to Telangana's *Dharani* portal. Real-estate listing portals (99acres, MagicBricks) remain a candidate fallback proxy.
   - *Code Status:* Stubbed with `NotImplementedError` in `src/gis/build_decision_matrix.py`.

5. **Power Grid & Substation Coordinates for Varanasi:**
   - *Status:* Pending / Unconfirmed.
   - *Details:* Public availability of official GIS substation location data from UPPCL (Uttar Pradesh Power Corporation Limited) is unconfirmed.
   - *Code Status:* Stubbed with `NotImplementedError` in `src/gis/build_decision_matrix.py`.

