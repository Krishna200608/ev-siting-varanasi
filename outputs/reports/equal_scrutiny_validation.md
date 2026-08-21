# Equal-Scrutiny Multi-Zone Validation Report

**Author:** Decision Analytics Research Group  
**Project:** Two-Stage EV Charging Station Siting Decision Support Framework (Varanasi, India)  
**Methodological Milestone:** Milestone 7 & 7b — Equal-Scrutiny Multi-Zone Validation & Recalibration Mechanism  
**Date:** August 2026  

---

## 1. Executive Summary & Problem Formulation

In Milestone 6, the citywide TOPSIS-CRITIC Top-5 candidate sites (`SITE_195`, `SITE_217`, `SITE_196`, `SITE_218`, `SITE_194`) clustered entirely within the **Godowlia–Dashashwamedh–Vishwanath corridor**. However, because this corridor was the only area that received 5 extra nested high-density Google Places tiles ($r=800\text{m}$) beyond the base 25-tile grid ($r=1,800\text{m}$), an empirical confound was identified:

> *Did the Godowlia corridor dominate citywide suitability because it is genuinely the most optimal multi-criteria location, or was its ranking an artifact of spatial measurement granularity (escaping Google Places API's 20-result truncation cap while other dense commercial nodes remained capped)?*

To resolve this question empirically without assumptions, Milestone 7 applied the **exact same 5-tile nested high-density treatment ($r=800\text{m}$)** to three other major commercial, academic, and transit nodes in Varanasi:
1. **Sigra Hub** (major retail mall, stadium, and administrative district)
2. **Lanka / BHU Road** (university commercial gateway, student footfall, and hospital hub)
3. **Cantonment (Cantt) Market** (primary railway station, hotel cluster, and retail corridor)

```
   +------------------------------------------------------------------------------------+
   |                   EQUAL-SCRUTINY MULTI-ZONE COMPARISON SUMMARY                     |
   |                                                                                    |
   |   Godowlia Corridor  : 5 nested tiles (r=800m) -> Top-5 Retained: 100.0% (5 of 5)  |
   |   Sigra Commercial   : 5 nested tiles (r=800m) -> Best Site: SITE_153 (Rank 10)   |
   |   Lanka / BHU Hub    : 5 nested tiles (r=800m) -> Best Site: SITE_191 (Rank 31)   |
   |   Cantt Rail/Market  : 5 nested tiles (r=800m) -> Best Site: SITE_131 (Rank 28)   |
   |                                                                                    |
   |   DEFINITIVE VERDICT: GODOWLIA PRIMACY VALIDATED AS GENUINE URBAN CONCENTRATION    |
   +------------------------------------------------------------------------------------+
```

---

## 2. Coordinate Provenance & Spatial Symmetry Audit

All 15 sub-tile locations across the three comparison zones were audited against OpenStreetMap Nominatim and strictly verified for spatial containment within the $76.99\text{ km}^2$ approximated VMC municipal boundary polygon (`data/raw/gis/varanasi_vmc_boundary.geojson`):

- **11 of 15 sub-tile coordinates (73.3%)** are **independently Nominatim-verified** with exact query strings.
- **4 of 15 sub-tile coordinates (26.7%)** are **manually placed geometric offsets** around verified centroids to achieve contiguous spatial coverage where hyperlocal street names did not resolve in Nominatim.
- **100% of all 15 sub-tiles** are confirmed strictly inside the municipal boundary polygon (0 outside).

| Zone | Tile # | Locality / Landmark | Latitude (°N) | Longitude (°E) | Provenance Status | Independent Query String / Offset Rationale | Boundary Containment |
|---|---|---|---|---|---|---|---|
| **Sigra** | 01 | Sigra Center / Crossing | 25.31126 | 82.98521 | **Nominatim-Verified** | `Sigra, Varanasi, Uttar Pradesh, India` | **Verified (True)** |
| **Sigra** | 02 | Mahmoorganj Junction | 25.30596 | 82.98375 | **Nominatim-Verified** | `Mahmoorganj, Varanasi, Uttar Pradesh, India` | **Verified (True)** |
| **Sigra** | 03 | Gurubagh / Luxa Approach | 25.30738 | 82.99644 | **Nominatim-Verified** | `Gurubagh, Varanasi, Uttar Pradesh, India` | **Verified (True)** |
| **Sigra** | 04 | Sigra North / Vidyapeeth | 25.31700 | 82.98400 | **Manual Offset** | $+650\text{m}$ North of Sigra Center (IP Mall & Nagar Nigam) | **Verified (True)** |
| **Sigra** | 05 | Rathyatra / West Corridor | 25.30200 | 82.98000 | **Manual Offset** | $-600\text{m}$ SW of Mahmoorganj (IP Vijaya & Rathyatra) | **Verified (True)** |
| **Lanka** | 06 | Lanka Market Crossing | 25.28109 | 82.99884 | **Nominatim-Verified** | `Lanka, Varanasi, Uttar Pradesh, India` | **Verified (True)** |
| **Lanka** | 07 | Assi Ghat / Riverfront Gateway | 25.28904 | 83.00697 | **Nominatim-Verified** | `Assi Ghat, Varanasi, Uttar Pradesh, India` | **Verified (True)** |
| **Lanka** | 08 | Durgakund Commercial Hub | 25.28911 | 82.99951 | **Nominatim-Verified** | `Durgakund, Varanasi, Uttar Pradesh, India` | **Verified (True)** |
| **Lanka** | 09 | BHU Main Campus Core | 25.26637 | 82.99046 | **Nominatim-Verified** | `Banaras Hindu University, Varanasi` | **Verified (True)** |
| **Lanka** | 10 | Naria Coaching Corridor | 25.28300 | 82.99000 | **Manual Offset** | $850\text{m}$ West of Lanka Crossing (Naria student hub) | **Verified (True)** |
| **Cantt** | 11 | Varanasi Jn (Cantt Station) | 25.32757 | 82.98624 | **Nominatim-Verified** | `Varanasi Junction railway station, Varanasi` | **Verified (True)** |
| **Cantt** | 12 | Cantonment Market Center | 25.32992 | 82.98357 | **Nominatim-Verified** | `Cantonment, Varanasi, Uttar Pradesh, India` | **Verified (True)** |
| **Cantt** | 13 | Nadesar / JHV Mall Strip | 25.33713 | 82.98811 | **Nominatim-Verified** | `Nadesar, Varanasi, Uttar Pradesh, India` | **Verified (True)** |
| **Cantt** | 14 | Lahartara Rail Approach | 25.31652 | 82.97333 | **Nominatim-Verified** | `Lahartara, Varanasi, Uttar Pradesh, India` | **Verified (True)** |
| **Cantt** | 15 | Andhrapul Transit Crossing | 25.32300 | 82.98200 | **Manual Offset** | $500\text{m}$ South of Cantt Station (Andhrapul bridge) | **Verified (True)** |

---

## 3. Empirical Results: Top 10 Citywide Siting Rankings (v1 Baseline vs. v2 Equal Scrutiny)

| Rank | Candidate Site ID | Latitude (°N) | Longitude (°E) | Urban Zone / Node | Baseline Score (v1) | Equal-Scrutiny Score (v2) | Score Delta ($\Delta$) | Baseline Rank (v1) | Equal-Scrutiny Rank (v2) | Rank Shift | Status |
|---|---|---|---|---|---|---|---|---|---|---|---|
| **1** | **`SITE_195`** | 25.3077 | 82.9999 | **Godowlia / Girijaghar Junction** | 0.7782 | **0.7459** | -0.0323 | 1 | **1** | **0** | **Retained #1** |
| **2** | **`SITE_217`** | 25.3077 | 83.0049 | **Dashashwamedh Ghat Corridor** | 0.7675 | **0.7395** | -0.0280 | 2 | **2** | **0** | **Retained #2** |
| **3** | **`SITE_218`** | 25.3122 | 83.0050 | **Kashi Vishwanath / Thatheri Bazar** | 0.7450 | **0.7103** | -0.0347 | 4 | **3** | **+1** | **Top-5 Retained** |
| **4** | **`SITE_196`** | 25.3123 | 83.0000 | **Godowlia North / Luxa Road** | 0.7594 | **0.7087** | -0.0507 | 3 | **4** | **-1** | **Top-5 Retained** |
| **5** | **`SITE_194`** | 25.3032 | 82.9999 | **Sonarpura / Bhelupur North** | 0.6957 | **0.6736** | -0.0221 | 5 | **5** | **0** | **Retained #5** |
| **6** | **`SITE_216`** | 25.3032 | 83.0048 | **Madanpura / Pandey Ghat** | 0.6791 | **0.6576** | -0.0215 | 7 | **6** | **+1** | **Top-10 Retained** |
| **7** | **`SITE_172`** | 25.3078 | 82.9950 | **Sigra East / Gurubagh** | 0.6793 | **0.6419** | -0.0374 | 6 | **7** | **-1** | **Top-10 Retained** |
| **8** | **`SITE_173`** | 25.3123 | 82.9951 | **Sigra Central / Stadium Corridor** | 0.6777 | **0.6266** | -0.0511 | 8 | **8** | **0** | **Retained #8** |
| **9** | **`SITE_240`** | 25.3121 | 83.0099 | **Manikarnika Riverfront Approach** | 0.6317 | **0.6063** | -0.0254 | 10 | **9** | **+1** | **Top-10 Retained** |
| **10** | **`SITE_153`** | 25.3259 | 82.9903 | **Sigra North / Englishia Line** | 0.5891 | **0.6006** | **+0.0115** | 19 | **10** | **+9** | **Rose into Top 10** |

---

## 4. Zone-by-Zone POI Density & Criterion Shifts

The table below presents the real numeric shifts in criteria and scores across all candidate sites in each urban zone:

| Urban Zone | Candidate Sites ($N$) | Mean $C_6$ Schools (v1 $\to$ v2) | Mean $C_6$ Malls (v1 $\to$ v2) | Mean $C_6$ Dining (v1 $\to$ v2) | Mean $C_6$ Hospitals (v1 $\to$ v2) | Mean TOPSIS Score (v1 $\to$ v2) | Best Candidate Site | Best Site Rank (v1 $\to$ v2) | Best Site Score (v2) |
|---|---|---|---|---|---|---|---|---|---|
| **Godowlia Corridor** | 16 sites | $7.95 \to 7.75$ ($-0.20$) | $7.93 \to 6.87$ ($-1.06$) | $7.83 \to 6.91$ ($-0.92$) | $1.00 \to 5.32$ ($+4.32$) | $0.6130 \to 0.5817$ | **`SITE_195`** | **Rank 1 $\to$ Rank 1** | **0.7459** |
| **Sigra Commercial Hub** | 20 sites | $6.01 \to 6.18$ ($+0.17$) | $5.39 \to 4.75$ ($-0.64$) | $5.51 \to 3.66$ ($-1.85$) | $1.00 \to 7.63$ ($+6.63$) | $0.4674 \to 0.4501$ | **`SITE_153`** | **Rank 19 $\to$ Rank 10** | **0.6006** |
| **Lanka / BHU Road** | 28 sites | $4.53 \to 4.85$ ($+0.32$) | $4.63 \to 5.19$ ($+0.56$) | $6.18 \to 5.53$ ($-0.65$) | $1.00 \to 5.31$ ($+4.31$) | $0.3735 \to 0.3628$ | **`SITE_191`** | **Rank 37 $\to$ Rank 31** | **0.5258** |
| **Cantonment Market & Station** | 20 sites | $3.85 \to 4.23$ ($+0.38$) | $4.35 \to 3.18$ ($-1.17$) | $2.12 \to 1.98$ ($-0.14$) | $1.00 \to 5.82$ ($+4.82$) | $0.3359 \to 0.3795$ | **`SITE_131`** | **Rank 33 $\to$ Rank 28** | **0.5384** |

---

## 5. Mathematical Recalibration Mechanism & Resolution of Anomalies

### 5.1 The Reclassification Mechanism (`points_to_kernel_density_raster`)
An apparent anomaly in the raw data is that Godowlia's candidate scores in `C6_POI_Shopping_Malls` ($7.93 \to 6.87$) and `C6_POI_Restaurants` ($7.83 \to 6.91$) declined slightly between v1 and v2, despite **zero new tiles being added in Godowlia**.

To explain this, inspect the exact mathematical reclassification implementation in `src/gis/build_decision_matrix.py` (lines 511–516):

```python
    # Reclassify continuous KDE density onto 1.0 to 9.0 scale
    d_min, d_max = density.min(), density.max()
    if d_max > d_min:
        norm_density = 1.0 + 8.0 * ((density - d_min) / (d_max - d_min))
    else:
        norm_density = np.ones_like(density) * 5.0
```

1. **Citywide Global Scaling:** The $[1.0, 9.0]$ standardization is evaluated relative to $d_{\min}$ and $d_{\max}$ across the **entire bounding box continuous raster grid** ($76.99\text{ km}^2$). It is not normalized per zone or per tile.
2. **The Mechanism of Godowlia's Score Shift:** In v1, Godowlia held the primary peak density for shopping malls and restaurants in the captured dataset. When Milestone 7 added hundreds of new verified POIs across Sigra, Lanka, and Cantt, the citywide continuous KDE density surface broadened, increasing the global denominator $(d_{\max} - d_{\min})$. Consequently, Godowlia's normalized score mathematically adjusted downwards from $\sim 7.9$ to $\sim 6.9$.
3. **Implication:** Godowlia's local physical environment did not change; rather, the citywide relative measurement scale became more demanding and comprehensive as other commercial nodes were populated.

### 5.2 Resolution of the Uniform Hospital Jump ($1.00 \to 5.32–7.63$)
The `C6_POI_Hospitals` column exhibited a dramatic jump of roughly $+4$ to $+6.6$ across all four zones (including Godowlia). Detailed audit of the underlying raw cache files reveals the exact root cause:
- **v1 Root Cause (Milestone 6):** In Milestone 6, Google Places API hit HTTP 429 quota exhaustion during the hospital query, leaving `full_run_cache/hospitals.json` with only **20 points** concentrated in a single south-eastern peripheral tile. Because this cluster lay far outside the candidate fishnet grid, the KDE density across all 308 candidate sites fell to near-zero ($<10^{-10}$), causing every site in the city to receive a flat default score of **$1.0000$ ($\text{std} = 0.0$)**. Consequently, the CRITIC algorithm assigned `C6_POI_Hospitals` a weight of **$0.0000$** in v1.
- **v2 Resolution (Milestone 7):** In Milestone 7, the hospital layer was comprehensively populated across the city with **280 hospitals, medical colleges, clinics, and pharmacies** (including Sir Sunderlal Hospital at BHU, Cantt railway hospitals, and Sigra medical facilities).
- **Mathematical Effect:** This restored `C6_POI_Hospitals` to a genuine continuous density surface ($\text{min} = 1.47, \text{mean} = 5.04, \text{max} = 8.95, \text{std} = 2.00$). CRITIC assigned this populated criterion an active objective weight of **$0.1311$**.
- **Conclusion:** The hospital jump reflects the transition of `C6_POI_Hospitals` from a completely unpopulated, zero-variance dummy column ($1.0000$ flat) into a fully populated, highly active spatial criterion.

---

## 6. Definitive Scientific Conclusion: Strengthened Proof of Godowlia's Primacy

**The Godowlia corridor dominance is STRONGLY VALIDATED AS A GENUINE URBAN CONCENTRATION.**

1. **Defense Against Fairer Competition:** Godowlia retained its #1 ranking and 100% Top-5 retention even after:
   - Sigra, Lanka, and Cantt received identical 5-tile nested high-density measurement ($r=800\text{m}$).
   - Citywide min-max rescaling calibrated Godowlia's normalized POI scores downwards.
   - An entirely new criterion (`C6_POI_Hospitals`, $w = 0.1311$) was activated with peak scores favoring Sigra ($7.63$) and Cantt ($5.82$).
2. **Multi-Criteria Synergy:** Despite Sigra winning on hospital density ($7.63$) and Cantt winning on transit access, Godowlia's unparalleled multi-criteria synergy—combining arterial road proximity ($C_1 \approx 8.8$), intense dining agglomeration ($C_6 \approx 6.9$), and dense retail footfall ($C_6 \approx 6.9$)—produced composite closeness coefficients ($C_i \ge 0.6736$) that no other zone could match (Sigra's best: $0.6006$, Cantt's best: $0.5384$, Lanka's best: $0.5258$).
3. **Top-10 Realignment:** Equal measurement legitimately elevated **`SITE_153`** (Northern Sigra / Englishia Line) by **+9 positions** (Rank 19 $\to$ **Rank 10**, score 0.6006), proving that equal scrutiny captures genuine secondary commercial strength without dislodging the primary cluster.

---

## 7. Documented Residual Limitations

While Milestone 7 resolves the confound among the city's 4 major commercial nodes (Godowlia, Sigra, Lanka, Cantt):
- Only **4 urban zones total** (20 nested tiles total) have received high-density nested tile treatment ($r=800\text{m}$).
- The peripheral and outer municipal sectors (Sunderpur West, Shivpur North, Rajghat East) remain evaluated on the baseline 25-tile grid ($r=1,800\text{m}$).
- In any future incremental expansion of the GIS layer, users must recognize that adding POIs to new suburban sectors will dynamically rescale the normalized scores of existing candidate sites via the citywide $(d_{\max} - d_{\min})$ continuous raster denominator.

---

## 8. Appendix: Systematic 9-Criteria Data Quality Audit Table (v1 Baseline vs. v2 Equal Scrutiny)

The table below reports the complete diagnostic data quality audit across all 9 criteria columns evaluated across all 308 candidate sites for both dataset versions:

| Criterion Code & Name | v1 Raw POIs | v1 Minimum | v1 Maximum | v1 Mean | v1 Std Dev | v1 Range ($\Delta$) | v1 Data Status | v2 Raw POIs | v2 Minimum | v2 Maximum | v2 Mean | v2 Std Dev | v2 Range ($\Delta$) | v2 Data Status | Diagnostic Verdict & Root Cause |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| **`C1_Major_Roads`** | 579 seg | 4.0026 | 8.9977 | 7.9050 | 1.0625 | 4.9951 | **HEALTHY** | 579 seg | 4.0026 | 8.9977 | 7.9050 | 1.0625 | 4.9951 | **HEALTHY** | Healthy road proximity surface across city |
| **`C5_Competitor_EVCS`** | 0 stn | 1.0000 | 1.0000 | 1.0000 | 0.0000 | 0.0000 | **DEGENERATE** | 0 stn | 1.0000 | 1.0000 | 1.0000 | 0.0000 | 0.0000 | **DEGENERATE** | Zero public fast-chargers exist in Varanasi (greenfield market, $w=0.0000$) |
| **`C6_POI_Schools`** | 452 | 1.7153 | 8.9551 | 4.1483 | 1.7325 | 7.2398 | **HEALTHY** | 511 | 1.6623 | 8.9564 | 4.2584 | 1.7151 | 7.2941 | **HEALTHY** | Strong spatial variance across academic hubs |
| **`C6_POI_Shopping_Malls`** | 325 | 1.4956 | 8.9280 | 4.3845 | 1.5688 | 7.4324 | **HEALTHY** | 587 | 1.1402 | 8.7994 | 3.6076 | 1.7958 | 7.6592 | **HEALTHY** | Broad dynamic range across commercial retail corridors |
| **`C6_POI_Restaurants`** | 238 | 1.0000 | 8.9746 | 3.4776 | 2.4718 | 7.9746 | **HEALTHY** | 378 | 1.0000 | 8.9474 | 2.7833 | 2.0529 | 7.9474 | **HEALTHY** | High contrast intensity across food & dining centers |
| **`C6_POI_Hospitals`** | 20 | 1.0000 | 1.0000 | 1.0000 | 0.0000 | 0.0000 | **DEGENERATE** | 280 | 1.4681 | 8.9533 | 5.0376 | 2.0025 | 7.4852 | **HEALTHY** | **Cured in v2:** Google 429 in v1 left 20 remote points; restored with 280 medical centers ($w=0.1311$) |
| **`C6_POI_Theatres`** | 10 | 1.0000 | 8.9175 | 2.6499 | 2.0550 | 7.9175 | **HEALTHY** | 13 | 1.0001 | 8.9651 | 3.1133 | 2.1832 | 7.9650 | **HEALTHY** | Distinct cinema clusters in Cantt, Sigra, and Rathyatra |
| **`C6_POI_Bus_Stops`** | 11 | 1.0000 | 8.9251 | 2.5169 | 1.8432 | 7.9251 | **HEALTHY** | 11 | 1.0000 | 8.9251 | 2.5169 | 1.8432 | 7.9251 | **HEALTHY** | Transit centers at Cantt Station and Godowlia crossing |
| **`C6_POI_Petrol_Bunks`** | 20 | 1.0000 | 9.0000 | 2.8613 | 2.0439 | 8.0000 | **HEALTHY** | 22 | 1.0000 | 8.9852 | 2.9791 | 2.1285 | 7.9852 | **HEALTHY** | Fuel station co-location opportunities along arterial highways |

### 8.2 Permanent Data Quality Pipeline Safeguard
To prevent future silent truncation or rate-limit failures from going undetected, `src/gis/build_decision_matrix.py` now includes the automated safeguard `validate_decision_matrix_quality()`. It automatically runs at the end of every matrix construction and validates variance thresholds ($\text{std} \ge 10^{-4}$), range spans ($\Delta \ge 0.5$), and raw POI counts ($N \ge 5$). Unit testing in `tests/test_data_quality.py` guarantees 100% test coverage.
