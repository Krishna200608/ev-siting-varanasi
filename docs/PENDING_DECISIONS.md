# Pending Decisions & Data Sourcing Inventory (`ev-siting-varanasi`)

This document is the **authoritative reference** for confirmed vs. unverified data sources and pending architectural decisions. AI agents and contributors must strictly adhere to these classifications — do not fabricate, assume, or bypass unverified items.

---

## 1. Confirmed Data Sources & Methods
*(Safe to reference by name in code, docstrings, and tests)*

- **OpenStreetMap (OSM):** Road network layers and Point of Interest (POI) vectors (schools, malls, restaurants, hospitals, theatres, bus stops).
- **Census of India (2011, Extrapolated via IDW):** Wards/district population density layers interpolated into continuous raster surfaces.
- **OpenChargeMap:** Existing public EV charging station locations used for competition and coverage deficit scoring.
- **Google Earth Manual Extraction:** Method confirmed by foundational literature (Rashmitha et al., 2024) for petrol pump and grid point spatial coordinates, though the exact Varanasi-specific data file remains to be finalized.

---

## 2. Pending / Unverified Data Sources & Decisions
*(Must be verified before implementation; do NOT assume or fabricate)*

1. **Public EV Charging Demand Dataset:**
   - *Status:* Unconfirmed.
   - *Details:* The availability and current downloadability of Zhang et al. (2025)'s exact 43-feature California dataset on `data.gov` (or a suitable Kaggle EV session alternative) has not yet been independently verified.
   - *Action for Milestone 4:* Manually inspect and confirm access to a downloadable CSV with comparable feature richness before writing preprocessing scripts.

2. **Varanasi / UP Land Cost Data Sourcing:**
   - *Status:* Unconfirmed.
   - *Details:* Unlike Telangana (which provides the official *Dharani* land valuation portal used by Rashmitha et al.), Uttar Pradesh / Varanasi has no verified state land-valuation GIS portal. Commercial real estate listing aggregators (99acres, MagicBricks) remain a candidate fallback proxy.
   - *Action for Milestone 2:* Determine whether real estate portal scraping or zonal circle rates will serve as the commercial rental cost proxy.

3. **Power Grid & Substation Coordinates for Varanasi:**
   - *Status:* Unconfirmed.
   - *Details:* Public availability of official GIS substation location data from UPPCL (Uttar Pradesh Power Corporation Limited) is unconfirmed.
   - *Action for Milestone 2:* Verify whether OSM power tags (`power=substation`) or manual extraction via Google Earth / Bhuvan will supply substation node coordinates.

4. **Candidate Site Buffer Radius:**
   - *Status:* Undecided.
   - *Details:* Rashmitha et al. (2024) utilized a 300-meter buffer around electrical grid nodes. Whether a 300m radius is optimal for Varanasi's specific urban density, street geometry, and substation layout remains to be confirmed during spatial exploration.

5. **MCDM Algorithm Scope (4 Combinations vs. Primary Pair):**
   - *Status:* Undecided / Deferred.
   - *Details:* Whether to execute all four algorithm combinations ($\text{CRITIC} / \text{Entropy} \times \text{TOPSIS} / \text{WASPAS}$) or streamline directly to the primary benchmark winner ($\text{TOPSIS} + \text{CRITIC}$) is deferred to Milestone 3 based on semester timeline availability.
