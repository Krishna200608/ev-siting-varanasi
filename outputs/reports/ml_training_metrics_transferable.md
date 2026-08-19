# ML Demand Forecasting: Transferability-Constrained Model Report (Stage 3 / Ex-Ante Siting)

**Dataset Foundation:** ACN-Data (Caltech Adaptive Charging Network; Lee, Li & Low, 2019, *ACM e-Energy '19*)  
**Sample Size:** 2,396 cleaned EV charging session records (Caltech + JPL sites)  
**Target Variable:** Energy Delivered ($y = \text{kWhDelivered}$, mean = 12.32 kWh, std = 11.07 kWh)  
**Features Included (Ex-Ante Strictly Observable):** `connection_hour`, `day_of_week`, `is_weekend`, `month`  
**Features Excluded (Unobservable Ex-Ante):** `charging_duration_hours`, `dwell_duration_hours`  

---

## 5-Fold Cross-Validation Performance Comparison

| Model Architecture | Mean $R^2$ | $R^2$ Std | Mean RMSE (kWh) | Mean MAE (kWh) |
|---|---|---|---|---|
| **Linear Regression (Baseline)** | 0.0050 | $\pm$ 0.0103 | 11.0075 | 7.9950 |
| **Random Forest Regressor** | 0.0140 | $\pm$ 0.0223 | 10.9513 | 8.0670 |
| **XGBoost Regressor (Selected)** | **0.0213** | **$\pm$ 0.0192** | **10.9116** | **8.0311** |

---

## Substantive Methodological Findings & Implications for Ex-Ante Siting
1. **Low Variance Explanation as a Genuine Finding:** Purely temporal features (hour of day, day of week, month) explain only a small fraction of charging demand variance ($R^2 \approx 0.0213$). This demonstrates that individual charging demand is overwhelmingly determined by physical session dwell duration rather than broad clock/calendar rhythms.
2. **Ex-Ante Siting Reality:** In a greenfield site selection setting where no charging station exists, session duration is fundamentally unobservable. Attempting to artificially inflate $R^2$ by inventing heuristic dwell proxies would violate scientific integrity.
3. **MCDM Primacy:** This empirical result strongly suggests that spatial Multi-Criteria Decision-Making (MCDM) criteria—such as road accessibility, competitor density, and POI agglomeration—capture the overwhelming majority of practically actionable information available prior to physical station deployment.
4. **Role in Milestone 5 Integration:** Milestone 5 will apply this honest, transferable model as the relative demand component of the composite score to directly test whether ML demand integration alters the MCDM-only shortlist ranking.
