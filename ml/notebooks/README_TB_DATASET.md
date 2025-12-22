# Using TB Dataset for Model Training

This guide explains how to train models using the `tb_dataset.csv` file directly.

## Quick Start

1. **Run EDA script** (creates `merged_features.csv`):
   ```bash
   cd ml/notebooks
   python eda_tb_dataset.py
   ```

2. **Train models**:
   ```bash
   python modeling.py
   ```

## What the EDA Script Does

The `eda_tb_dataset.py` script:

1. **Loads** `tb_dataset.csv` from `../data/synthetic/`
2. **Maps columns** to standard names (e.g., `HIV` → `hiv_positive`)
3. **Calculates** `comorbidity_count` from all comorbidity fields
4. **Estimates** missing features:
   - `adherence_mean`, `adherence_min`, `adherence_std`: Estimated from treatment outcome
   - `modification_count`: Estimated from comorbidity count and treatment duration
   - `visit_count`: Estimated from treatment duration (assumes monthly visits)
5. **Generates** `risk_score` using a heuristic based on available features
6. **Saves** `merged_features.csv` for model training

## Features Used

The final model uses these features (all available from or derived from `tb_dataset.csv`):

- `age`: Patient age
- `hiv_positive`: HIV status
- `diabetes`: Diabetes comorbidity
- `smoker`: Smoking comorbidity
- `comorbidity_count`: Total count of comorbidities
- `adherence_mean`: Mean adherence (estimated from outcome)
- `adherence_min`: Minimum adherence (estimated)
- `adherence_std`: Standard deviation of adherence (estimated)
- `modification_count`: Treatment modifications (estimated)
- `visit_count`: Number of monitoring visits (estimated from treatment duration)

## Note on Estimated Features

Since `tb_dataset.csv` doesn't contain monitoring visit or treatment modification data, these features are estimated using:
- **Adherence**: Based on treatment outcome (cured/completed = higher adherence)
- **Modifications**: Based on comorbidity count and treatment duration
- **Visits**: Based on treatment duration (assumes monthly visits)

These estimates are reasonable approximations for model training, but in production, you would use actual monitoring visit and modification data.

## Output Files

After running `eda_tb_dataset.py`, you'll get:
- `merged_features.csv`: Ready for model training
- `eda_age_distribution.png`: Age distribution visualization
- `eda_comorbidities.png`: Comorbidity prevalence chart
- `eda_correlation_matrix.png`: Feature correlation heatmap

After running `modeling.py`, you'll get:
- `xgboost_model.pkl`: Trained XGBoost model
- `random_forest_model.pkl`: Trained Random Forest model
- `logistic_regression_model.pkl`: Trained Logistic Regression model
- `scaler.pkl`: Feature scaler
- `shap_explainer.pkl`: SHAP explainer
- `model_metadata.json`: Model metadata
- `roc_curves.png`: ROC curve comparison
- `confusion_matrix.png`: Confusion matrix
- `shap_summary.png`: SHAP summary plot

## Alternative: Using Separate CSV Files

If you have separate CSV files (`patients.csv`, `treatment_regimens.csv`, etc.), you can use the original `eda.py` script instead:

```bash
python eda.py
```

This script expects the full synthetic data structure with separate files for patients, regimens, modifications, visits, and predictions.

