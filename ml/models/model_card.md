# Model Card (Template) - PTLD Risk

## Overview
- Task: PTLD risk prediction during TB treatment.
- Inputs: Baseline demographics/comorbidities, imaging score, treatment patterns, adherence/monitoring.
- Outputs: Risk score (0-1), category (low/medium/high), SHAP values, confidence.

## Intended Use
- Clinical decision support for pulmonologists/TB clinicians during treatment.
- Not for standalone diagnosis; requires clinician oversight.

## Training Data
- Source: São Paulo TBWEB (277,870 cases) — secured, not in repo.
- Splits: 80/20 patient-level, 5-fold CV; note any temporal splits.

## Metrics
- Target: AUROC ≥0.75, Sensitivity ≥0.80. Also report AUPRC, specificity, calibration.

## Limitations
- Synthetic data for demos; real-world drift possible.
- Missing external validation may reduce generalizability.

## Safety/Compliance
- HIPAA-aligned handling; no PHI in repo. Encryption in transit/rest in deployment.

## Versioning
- `model_version`: increment on retrain. Store artifacts in `ml/models/`.

## Explainability
- SHAP global/local views; note top contributors and directionality.


