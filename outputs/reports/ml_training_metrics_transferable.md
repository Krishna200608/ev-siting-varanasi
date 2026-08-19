# ML Demand Forecasting: Transferability-Constrained Siting Report (Milestone 4b)

**Academic Context:** Operationalizing Demand Forecasting for Ex-Ante Candidate EV Siting in Varanasi, India  
**Dataset Foundation:** ACN-Data (Lee, Li & Low, 2019; Caltech + JPL, $N = 2,396$ sessions)  

---

## 1. Tripartite Model Comparison Across Observability Tiers

| Observability Tier | Model Architecture | Features Included | Ex-Ante Observability in Varanasi | Mean $R^2$ | Mean RMSE (kWh) | Mean MAE (kWh) |
|---|---|---|---|---|---|---|
| **Tier 1: Pure Transferable** | XGBoost Regressor | `connection_hour`, `day_of_week`, `is_weekend`, `month` | **Fully Observable** (exogenous temporal calendar) | **0.0213** ($\pm 0.0192$) | 10.9116 | 8.0311 |
| **Tier 2: Proxy-Extended** | XGBoost Regressor | Temporal + Proxied `dwell_duration_hours` | **Observable via Proxy** (estimated from POI/land-use type) | **0.1734** ($\pm 0.0473$) | 10.0327 | 7.2553 |
| **Tier 3: Full Diagnostic** | XGBoost Regressor | Temporal + Dwell + `charging_duration_hours` | **Unobservable Ex-Ante** (requires existing station) | **0.4832** ($\pm 0.0336$) | 7.9299 | 5.3362 |

---

## 2. Core Empirical Findings & Siting Implications

1. **The Ex-Ante Variance Gap:**
   - Pure temporal variables explain only **2.13%** of single-session energy variance ($R^2 = 0.0213$).
   - This large drop from Tier 3 ($R^2 = 0.4832$) is an authentic, defensible empirical result: **most variance in EV charging demand is session-dependent and cannot be known before a site exists**.
2. **Methodological Justification for Two-Stage Framework:**
   - Because temporal demand models explain limited ex-ante variance on their own, spatial GIS-MCDM (Stage A: POI density, road accessibility, competitor deficit) is mathematically and methodologically indispensable for candidate site screening.
3. **Role of Proxy-Extended Model (Tier 2):**
   - Incorporating a contextual dwell-time proxy (e.g. 2–3h for retail/mall, 6–8h for workplace, 0.5–1h for transit corridor) raises explained variance to **17.34%** ($R^2 = 0.1734$), providing a structured bridge for Milestone 5 integration.

---

## 3. Milestone 5 Operational Designation
- **Milestone 5 Siting Integration:** Will utilize the **Transferable / Proxy-Extended Demand Models** to infer candidate relative demand potential scores without data leakage.
- **Academic Research Contribution:** Tier 3 Full Diagnostic Model remains the primary artifact for explaining generalized demand drivers under Research Question 2.
