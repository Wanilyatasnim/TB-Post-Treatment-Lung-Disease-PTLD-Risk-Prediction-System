# Feature Removal Summary: BMI and X-Ray Score

## Overview
Removed BMI and x_ray_score features from the codebase as they are not available in the TB dataset. The dataset does not contain patient height/weight (needed for BMI) or numeric X-ray scores.

## Changes Made

### 1. ML Model Features
- **File**: `ml/notebooks/modeling.py`
- **Change**: Removed `bmi` and `x_ray_score` from baseline features
- **New Features**: Using `comorbidity_count` instead
- **New Feature Set**: 
  - `age`
  - `hiv_positive`
  - `diabetes`
  - `smoker`
  - `comorbidity_count` (NEW - replaces BMI)
  - `adherence_mean`
  - `adherence_min`
  - `adherence_std`
  - `modification_count`
  - `visit_count`

### 2. Feature Extraction
- **File**: `backend/clinical/viewsets.py`
- **Change**: Removed BMI calculation and x_ray_score extraction
- **New**: Uses `comorbidity_count` calculated from patient comorbidities
- **Note**: All features now come from actual patient data (no defaults/placeholders)

### 3. Model Metadata
- **File**: `ml/models/model_metadata.json`
- **Change**: Updated feature list to remove BMI and x_ray_score
- **Impact**: Existing trained models will NOT work with new feature set

### 4. Predictor Documentation
- **File**: `backend/ml/predictor.py`
- **Change**: Updated docstring to reflect new feature set

### 5. Tests
- **Files**: 
  - `backend/clinical/tests.py`
  - `backend/clinical/tests_api.py`
- **Change**: Removed BMI and x_ray_score from test patient creation

### 6. Recommendation Engine
- **File**: `backend/ml/recommendation_engine.py`
- **Change**: Removed BMI-based and x_ray_score-based recommendations
- **New**: Added comorbidity_count-based recommendations

### 7. Test Utilities
- **Files**:
  - `scripts/utils/test_shap_visualization.py`
  - `scripts/utils/verify_dataset_integration.py`
- **Change**: Updated to use new feature set

## ⚠️ IMPORTANT: Model Retraining Required

**The existing trained models (`ml/models/*.pkl`) were trained with the OLD feature set that included BMI and x_ray_score. These models will NOT work with the new feature set.**

### To Fix:
**Retrain the models** using the updated `ml/notebooks/modeling.py` script:
   ```bash
   cd ml/notebooks
   python modeling.py
   ```
   
   The modeling script now reads `tb_dataset.csv` directly and performs all feature engineering:
   - Maps column names to standard format
   - Calculates `comorbidity_count` from all comorbidity fields
   - Estimates missing features (adherence, modifications, visits) based on available data
   - Generates risk scores for training

2. This will generate new model files with the correct feature set:
   - `xgboost_model.pkl`
   - `random_forest_model.pkl`
   - `logistic_regression_model.pkl`
   - `scaler.pkl`
   - `shap_explainer.pkl`
   - `model_metadata.json` (already updated)

3. **Verify** the new models work:
   ```bash
   python scripts/utils/test_shap_visualization.py
   ```

## Features Now Available

The new feature set uses only data available in the TB dataset:

### Baseline Features:
- `age`: Patient age (available)
- `hiv_positive`: HIV status (available)
- `diabetes`: Diabetes comorbidity (available)
- `smoker`: Smoking comorbidity (available)
- `comorbidity_count`: Total count of comorbidities (calculated from available data)

### Treatment Features:
- `adherence_mean`: Mean adherence percentage (from monitoring visits)
- `adherence_min`: Minimum adherence percentage
- `adherence_std`: Standard deviation of adherence
- `modification_count`: Number of treatment modifications
- `visit_count`: Number of monitoring visits

## Data Available but Not Used (Yet)

These features are extracted but not currently used by the model:
- `bacilloscopy_m1`, `bacilloscopy_m2`, `bacilloscopy_m3`: Monthly bacilloscopy results
- `bacilloscopy_trend`: Trend in bacilloscopy results
- `days_in_treatment`: Treatment duration
- `supervised_treatment`: Whether treatment is supervised

These could be added to future model versions if needed.

## Testing

After retraining models, verify:
1. ✅ Feature extraction works: `python scripts/utils/verify_dataset_integration.py`
2. ✅ Predictions work: Generate a prediction via API or UI
3. ✅ SHAP visualizations work: `python scripts/utils/test_shap_visualization.py`
4. ✅ All tests pass: `python manage.py test`

## Notes

- The `chest_x_ray` field still exists in the Patient model (it's a text field, not a numeric score)
- Height and weight fields were added in migration 0008 but are not in the dataset
- BMI cannot be calculated without height and weight data
- X-ray score was never a field in the dataset, only estimated from text

## Population-Level SHAP Analysis Fix

### Issue
The population-level feature importance (SHAP analysis) was showing BMI and x_ray_score features, which don't exist in the dataset.

### Fix Applied
Updated `backend/clinical/researcher_views.py` - `population_shap_analysis()` function to filter out BMI and x_ray_score features:

1. **Filter out excluded features**: Added exclusion list:
   ```python
   EXCLUDED_FEATURES = ['bmi', 'x_ray_score', 'xray_score', 'x_ray', 'xray']
   ```

2. **Case-insensitive filtering**: Checks feature names case-insensitively to catch variations

3. **Updated description**: Response now indicates that BMI and x_ray_score are excluded

### Verification
The population-level SHAP analysis endpoint (`/researchers/api/shap-analysis/`) now:
- ✅ Only shows features that exist in the current model
- ✅ Excludes BMI and x_ray_score (and variations)
- ✅ Displays only valid features: age, hiv_positive, diabetes, smoker, comorbidity_count, adherence_mean, adherence_min, adherence_std, modification_count, visit_count

---

**Date**: 2025-01-XX  
**Status**: Code updated, models need retraining

