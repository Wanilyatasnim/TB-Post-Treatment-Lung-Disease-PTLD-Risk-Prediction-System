# TB Post-Treatment Lung Disease (PTLD) Risk Prediction System

Monorepo for the PTLD clinical decision support tool. Aligned with the PRD and organized for phased delivery:
- `ml/`: EDA, feature engineering, model training, synthetic data generator.
- `backend/`: Django REST backend, prediction API, RBAC, audit logging.
- `frontend/`: Django templates + Bootstrap 5 UI and dashboards.
- `docs/`: PRD mapping, EDA report drafts, architecture notes.
- `infrastructure/`: Infra scripts and deployment helpers.

## Quickstart (local/dev)
1) Copy `.env.example` to `.env` (edit secrets as needed).
2) Build and start services:
```
docker-compose up --build
```
3) Backend will run on `http://localhost:8000`, Postgres on `5432`.

## Phase Plan (condensed)
- Phase 1: EDA, synthetic data generator, baseline models (RF/XGBoost/LR), SHAP templates.
- Phase 2: Django project, Postgres schema for Patient/TreatmentRegimen/Modification/MonitoringVisit/RiskPrediction/User.
- Phase 3: Django templates + Bootstrap UI, patient flows, dashboard with Chart.js/Plotly.
- Phase 4: Model integration, SHAP visuals, recommendation engine.
- Phase 5: Tests, dockerized deployment, docs/UAT.

## Synthetic data
Use `ml/synthetic_data_generator.py` to create 1,000 fake patient/treatment records matching the schema for parallel backend/frontend development. Outputs CSVs with consistent keys.




