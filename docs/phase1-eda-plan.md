# Phase 1 - EDA & Modeling Plan

## Objectives
- Profile São Paulo TBWEB data (structure, missingness, drift).
- Define feature set (baseline + treatment patterns) for RF/XGBoost/LR ensemble.
- Produce 30–40 page report with 30–50 visuals (profiling + custom plots).
- Deliver baseline models with AUROC/Sensitivity metrics and SHAP analysis.

## Deliverables
- `ml/notebooks/eda.ipynb`: data dictionary, missingness maps, univariate/bivariate analysis, temporal trends.
- `ml/notebooks/modeling.ipynb`: feature engineering, train/val splits, metrics, SHAP.
- `ml/data/synthetic/*.csv`: 1k synthetic records for backend/frontend dev.
- Model artifacts in `ml/models/` (`.pkl`) plus model card.
- README updates + brief executive summary.

## Tasks (suggested order)
1. Load raw data (secure path), run `ydata-profiling` summary; export HTML/PDF.
2. Clean + type cast; handle outliers/missing; create data dictionary.
3. Feature engineering:
   - Demographics: age, sex, BMI, comorbidities, smoking, HIV.
   - Baseline imaging: x_ray_score, cavitation flag.
   - Treatment dynamics: regimen pattern, interruptions (>7d), modifications, adherence (%), adverse events counts.
   - Monitoring: smear conversion, weight change.
4. Split strategy: chronological or patient-level 80/20; 5-fold CV.
5. Models: Logistic Regression (baseline), Random Forest, XGBoost; consider stacking/voting.
6. Metrics: AUROC, AUPRC, sensitivity @ selected specificity; calibration plots.
7. SHAP: global (bar), local (force/waterfall), per-risk cohort breakdown.
8. Save models + preprocessing pipeline; version with `model_version`.
9. Draft report + recommendations for V1 deployment.

## Notes
- Keep PII off the repo; use synthetic data locally for demos.
- Ensure seeds for reproducibility; log parameters for each run.

 ## db supabase pass: akeLcKZezzw7MrKf






