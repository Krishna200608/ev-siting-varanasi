# Standing Rules for AI Agents (`ev-siting-varanasi`)

This repository implements a multi-week, two-stage decision-support framework for EV charging station siting in Varanasi, India, combining GIS-based Multi-Criteria Decision-Making (MCDM) with explainable Machine Learning (ML) demand forecasting.

All AI coding assistants and subagents working in this repository must strictly adhere to the following standing rules:

---

## 1. Code Quality & Standards
- **Python Version:** Target **Python 3.11+**.
- **Style & Standards:** Strict adherence to **PEP 8**. Maintain clean formatting and meaningful variable naming.
- **Type Annotations:** Every function signature must contain complete, explicit type hints (arguments and return types). Avoid unconstrained `Any` unless interfacing with dynamic third-party payloads.
- **Module Docstrings:** Every Python module must begin with a comprehensive module-level docstring explicitly declaring:
  1. The **Synopsis Stage / Pipeline** to which the module belongs:
     - `Pipeline A: GIS Data Preparation`
     - `Pipeline A: MCDM Decision Analysis`
     - `Pipeline B: ML Demand Forecasting`
     - `Stage 4: Two-Stage Integration & Sensitivity Analysis`
  2. The theoretical and literature foundation (e.g., Rashmitha et al., 2024; Zhang et al., 2025).
  3. The specific inputs, transformations, and outputs handled by the module.

---

## 2. Zero-Assumption Data Policy
- **No Hallucinated Data Sources:** Never fabricate, guess, or silently substitute a data source, file path, API endpoint, coordinate system, or dataset that has not been explicitly confirmed.
- **Authoritative Decisions:** Check `docs/PENDING_DECISIONS.md` before referencing or integrating any external data source.
- **Flagging Missing Items:** If a task requires an unconfirmed data source or pending architectural decision, **stop immediately** and document the item in `docs/PENDING_DECISIONS.md` rather than bypassing it with assumptions.

---

## 3. Stubs & Incremental Implementation
- **Strict Stub Convention:** In incomplete or upcoming milestones, stub functions must raise:
  ```python
  raise NotImplementedError("Milestone N — see docs/ROADMAP.md")
  ```
- **No Pseudo-Implementations:** Do not write mock or placeholder calculations that mimic real logic without actual mathematical rigor. Keep stubs cleanly typed and explicit about their milestone status.

---

## 4. Security & Environment Configuration
- **No Hardcoded Secrets:** Never commit API keys, credentials, or private tokens (e.g., Google Places API, OpenChargeMap API).
- **Environment Variables:** All sensitive or configurable variables must be loaded via `python-dotenv` and documented in `.env.example`.
- **Reproducibility:** When training models or executing stochastic algorithms, always set fixed random seeds (e.g., `numpy.random.seed(42)`).

---

## 5. Milestone Cadence
- Refer to `docs/ROADMAP.md` for the multi-week implementation schedule.
- Only implement logic designated for the active milestone. Do not bleed future milestone implementation into earlier setup passes.
