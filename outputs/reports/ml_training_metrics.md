# ML Demand Forecasting: Model Evaluation Report (Stage 3)

**Dataset Foundation:** ACN-Data (Caltech Adaptive Charging Network; Lee, Li & Low, 2019, *ACM e-Energy '19*)  
**Sample Size:** 2,396 cleaned EV charging session records (Caltech + JPL sites)  
**Target Variable:** Energy Delivered ($y = \text{kWhDelivered}$, mean = 12.32 kWh, std = 11.07 kWh)  

---

## 5-Fold Cross-Validation Performance Comparison

| Model Architecture | Mean $R^2$ | $R^2$ Std | Mean RMSE (kWh) | Mean MAE (kWh) |
|---|---|---|---|---|
| **Linear Regression (Baseline)** | 0.4068 | $\pm$ 0.0391 | 8.4860 | 5.8710 |
| **Random Forest Regressor** | 0.5058 | $\pm$ 0.0358 | 7.7572 | 5.2644 |
| **XGBoost Regressor (Selected)** | **0.4832** | **$\pm$ 0.0336** | **7.9299** | **5.3362** |

---

## Methodological Insights & Transferability Rationale
- **Predictive Signal Validation:** Unlike synthetic benchmark datasets, ACN-Data demonstrates robust empirical predictability ($R^2 \approx 0.483$, RMSE $\approx 7.93\text{ kWh}$).
- **Core Drivers:** Charging duration and arrival connection hour capture fundamental physical and behavioral charging characteristics transferable as diurnal demand priors to Varanasi candidate site feasibility scoring.
