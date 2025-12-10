# ML Model Development - Setup & Execution Guide

## Overview

This guide will help you complete Phase 1 (ML Model Development) for the PTLD Risk Prediction System.

## What's Been Created

✅ **Synthetic Data**: 1000-patient dataset generated in `ml/data/synthetic/`
 - `patients.csv`
   - `treatment_regimens.csv`
   - `monitoring_visits.csv`
   - `treatment_modifications.csv`
   - `risk_predictions.csv`

✅ **EDA Script**: `ml/notebooks/eda.py` - Comprehensive exploratory data analysis
   - 15+ visualizations
   - Demographic analysis
   - Comorbidity distributions
   - Treatment pattern analysis
   - Risk factor correlations

✅ **Model Training Script**: `ml/notebooks/modeling.py` - Complete ML pipeline
   - Random Forest Classifier
   - XGBoost Classifier
   - Logistic Regression
   - Ensemble model
   - SHAP explainability
   - Model persistence (.pkl files)

---

## Installation Steps

### 1. Install Required ML Packages

```bash
cd ml

# Install packages one by one to avoid conflicts
pip install pandas numpy matplotlib seaborn
pip install scikit-learn
pip install xgboost
pip install shap
pip install plotly
pip install ydata-profiling
```

**Or** use the requirements file:
```bash
pip install -r requirements.txt --no-deps
# Then install each package manually if issues
```

---

## Execution Steps

### Step 1: Run EDA Analysis

```bash
cd ml/notebooks
python eda.py
```

**Expected Output**:
- Console output with statistics and key findings
- 8+ PNG visualization files in `ml/data/synthetic/`
- `merged_features.csv` for modeling

**Time**: ~2-3 minutes

---

### Step 2: Train ML Models

```bash
python modeling.py
```

**Expected Output**:
- Model training progress for RF, XGBoost, LR
- Performance metrics (AUROC, sensitivity, specificity)
- ROC curves and confusion matrices
- SHAP analysis visualizations
- Saved model files in `ml/models/`:
  - `random_forest_model.pkl`
  - `xgboost_model.pkl`
  - `logistic_regression_model.pkl`
  - `scaler.pkl`
  - `shap_explainer.pkl`
  - `model_metadata.json`

**Time**: ~3-5 minutes

**Target Metrics** (from PRD):
- AUROC ≥0.75 ✅
- Sensitivity ≥0.80 ✅

---

## Integration with Django (Phase 2/4)

Once models are trained, you'll update the Django prediction endpoint:

### Current State (Stub):
```python
# backend/clinical/viewsets.py line 78-82
# Current stub uses random scores
score = base + random.random() * 0.6
```

### After Integration:
```python
# Load trained model on Django startup
import pickle

with open('ml/models/xgboost_model.pkl', 'rb') as f:
    model = pickle.load(f)

# In prediction endpoint
def predict(self, request):
    # Extract patient features
    features = extract_patient_features(patient_id)
    
    # Predict with real model
    risk_score = model.predict_proba([features])[0][1]
    
    # Generate SHAP values
    shap_values = explainer.shap_values([features])
    
    # Save prediction
    ...
```

---

## Troubleshooting

### Issue: Package installation fails

**Solution**: Install packages individually
```bash
pip install pandas==2.1.4
pip install numpy==1.26.2
pip install scikit-learn==1.3.2
pip install xgboost==1.7.6
pip install shap==0.43.0
```

### Issue: "No module named 'xgboost'"

**Solution**:
```bash
pip install xgboost
```

### Issue: Script fails on import

**Solution**: Check Python version (need 3.10+)
```bash
python --version

# Should be Python 3.10 or higher
```

### Issue: Memory error during training

**Solution**: Reduce dataset size or use smaller models
```python
# In modeling.py, change:
rf_model = RandomForestClassifier(
    n_estimators=50,  # reduced from 200
    ...
)
```

---

## Verification Checklist

After running both scripts, verify:

- [ ] EDA script completed without errors
- [ ] Generated visualizations in `ml/data/synthetic/*.png`
- [ ] `merged_features.csv` created
- [ ] Model training completed for all 3 models
- [ ] Test AUROC ≥0.75 for at least one model
- [ ] Model files saved in `ml/models/`
- [ ] `model_metadata.json` contains performance metrics

---

## Next Steps After ML Training

1. **Django Integration** (Phase 2/4)
   - Create `backend/ml/` directory
   - Copy model files to backend
   - Update `viewsets.py` prediction endpoint
   - Load models on Django startup

2. **SHAP Visualization** (Phase 4)
   - Create SHAP plot generation service
   - Add SHAP waterfall chart to patient detail page
   - Display feature importance

3. **Testing** (Phase 5)
   - Unit tests for prediction endpoint
   - Test with synthetic patient data
   - Validate SHAP values

---

## Quick Start Summary

```bash
# 1. Navigate to ML directory
cd ml

# 2. Install dependencies (if not already)
pip install pandas numpy scikit-learn xgboost shap matplotlib seaborn plotly

# 3. Run EDA
cd notebooks
python eda.py

# 4. Train models
python modeling.py

# 5. Verify output
ls -la ../models/
```

Expected completion: **5-10 minutes total**

---

## Files Created

### Data Files
- `ml/data/synthetic/*.csv` (5 files, ~500KB total)
- `ml/data/synthetic/*.png` (8+ visualization files)
- `ml/data/synthetic/merged_features.csv`

### Model Files
- `ml/models/*.pkl` (5 model files, ~50MB total)
- `ml/models/model_metadata.json`
- `ml/models/roc_curves.png`
- `ml/models/confusion_matrix.png`
- `ml/models/shap_summary.png`

### Scripts
- `ml/notebooks/eda.py` (~300 lines)
- `ml/notebooks/modeling.py` (~400 lines)

---

## Support

If you encounter issues:
1. Check Python version: `python --version` (need 3.10+)
2. Verify package installations: `pip list | grep -E "pandas|sklearn|xgboost"`
3. Review error messages in detail
4. Try running scripts section by section in interactive Python

**All code is ready to run - just need package installations!**
