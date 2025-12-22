# ML Notebooks

This directory contains scripts for exploratory data analysis (EDA) and model training.

## Quick Start

### Train Models (Recommended - Uses tb_dataset.csv directly)

```bash
cd ml/notebooks
python modeling.py
```

The `modeling.py` script:
- Reads `tb_dataset.csv` directly from `../data/synthetic/`
- Performs all feature engineering automatically
- Trains XGBoost, Random Forest, and Logistic Regression models
- Saves trained models to `../models/`

**No separate EDA step needed!** The modeling script handles everything.

## What the Modeling Script Does

1. **Loads** `tb_dataset.csv`
2. **Maps columns** to standard names (e.g., `HIV` → `hiv_positive`, `Age` → `age`)
3. **Calculates** `comorbidity_count` from all comorbidity fields
4. **Estimates** missing features:
   - `adherence_mean`, `adherence_min`, `adherence_std`: Estimated from treatment outcome
   - `modification_count`: Estimated from comorbidity count and treatment duration
   - `visit_count`: Estimated from treatment duration (assumes monthly visits)
5. **Generates** `risk_score` using a heuristic for training target
6. **Trains** three models (XGBoost, Random Forest, Logistic Regression)
7. **Saves** all models and artifacts

## Features Used

The model uses these features (all derived from `tb_dataset.csv`):

- `age`: Patient age
- `hiv_positive`: HIV status
- `diabetes`: Diabetes comorbidity
- `smoker`: Smoking comorbidity
- `comorbidity_count`: Total count of comorbidities (calculated)
- `adherence_mean`: Mean adherence (estimated from outcome)
- `adherence_min`: Minimum adherence (estimated)
- `adherence_std`: Standard deviation of adherence (estimated)
- `modification_count`: Treatment modifications (estimated)
- `visit_count`: Number of monitoring visits (estimated)

## Output Files

After running `modeling.py`, you'll get:

**Models:**
- `xgboost_model.pkl`: Trained XGBoost model (best performer)
- `random_forest_model.pkl`: Trained Random Forest model
- `logistic_regression_model.pkl`: Trained Logistic Regression model
- `scaler.pkl`: Feature scaler
- `shap_explainer.pkl`: SHAP explainer for model interpretability
- `model_metadata.json`: Model metadata and feature list

**Visualizations:**
- `roc_curves.png`: ROC curve comparison
- `confusion_matrix.png`: Confusion matrix for best model
- `shap_summary.png`: SHAP summary plot

## Alternative: Separate EDA Script

If you want to do exploratory data analysis separately, you can use:

```bash
python eda_tb_dataset.py
```

This creates:
- `merged_features.csv`: Processed features (optional - modeling.py doesn't need this)
- Visualization files: `eda_age_distribution.png`, `eda_comorbidities.png`, `eda_correlation_matrix.png`

**Note:** The EDA script is optional. The modeling script does everything you need.

## Old Workflow (Not Needed)

The old workflow required separate CSV files and an EDA step:
```bash
python eda.py  # Required separate CSV files
python modeling.py  # Required merged_features.csv
```

This is no longer needed. Just run `modeling.py` directly with `tb_dataset.csv`!
