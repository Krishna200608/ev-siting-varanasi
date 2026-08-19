# ML Demand Forecasting: Full-Feature Model Evaluation Report (Stage 3)

**Dataset Foundation:** ACN-Data (Caltech Adaptive Charging Network; Lee, Li & Low, 2019, *ACM e-Energy '19*)  
**Sample Size:** 2,396 cleaned EV charging session records (Caltech + JPL sites)  
**Target Variable:** Energy Delivered ($y = \text{kWhDelivered}$, mean = 12.32 kWh, std = 11.07 kWh)  
**Features Included:** `connection_hour`, `day_of_week`, `is_weekend`, `month`, `dwell_duration_hours`, `charging_duration_hours`  

---

## 5-Fold Cross-Validation Performance Comparison

| Model Architecture | Mean $R^2$ | $R^2$ Std | Mean RMSE (kWh) | Mean MAE (kWh) |
|---|---|---|---|---|
| **Linear Regression (Baseline)** | 0.4068 | $\pm$ 0.0391 | 8.4860 | 5.8710 |
| **Random Forest Regressor** | 0.5058 | $\pm$ 0.0358 | 7.7572 | 5.2644 |
| **XGBoost Regressor (Selected)** | **0.4832** | **$\pm$ 0.0336** | **7.9299** | **5.3362** |

---

## Model Selection Rationale (Random Forest vs. XGBoost)
Random Forest achieved a marginally higher point estimate for cross-validated explained variance ($R^2 = 0.5058 \pm 0.0358$) compared to XGBoost ($R^2 = 0.4832 \pm 0.0336$). However, the empirical cross-validation standard deviation intervals overlap substantially, indicating that the performance difference is not statistically significant. XGBoost was retained as the primary architectural model for the following deliberate, methodological reasons:
1. **Methodological Consistency:** Aligns directly with the gradient boosting baseline established in Zhang, Peng & Zeng (2025).
2. **Regularization & Generalization:** XGBoost incorporates $L_1$ (Lasso) and $L_2$ (Ridge) tree complexity penalties that reduce overfitting risks during spatial transfer learning.
3. **Interpretability:** Native integration with `shap.TreeExplainer` enables exact, high-performance polynomial-time Shapley feature attribution.

---

## Methodological Insights & Transferability Boundary
- **Diagnostic Value (RQ2):** The full model demonstrates strong empirical predictability ($R^2 \approx 0.483$, RMSE $\approx 7.93\text{ kWh}$) and identifies `charging_duration_hours` as the single dominant demand driver ($\sim 75.8\%$ SHAP weight).
- **Transferability Limitation:** Because `charging_duration_hours` is unobservable prior to station construction, this model cannot be directly applied ex-ante to unbuilt Varanasi candidate sites without circular data leakage. See [`outputs/reports/ml_training_metrics_transferable.md`](ml_training_metrics_transferable.md) for the operational siting model.
