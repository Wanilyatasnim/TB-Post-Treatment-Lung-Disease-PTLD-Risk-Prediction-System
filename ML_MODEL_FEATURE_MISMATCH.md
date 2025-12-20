# ML Model Feature Mismatch Issue

## Problem Summary

The ML model is **still using the OLD dataset features**, but the current patient dataset uses **NEW TB dataset features**. This causes:

1. **BMI appears in SHAP values** even though BMI is not in the new dataset (no weight/height fields)
2. **x_ray_score appears in SHAP values** even though the new dataset only has `chest_x_ray` (text field)
3. **Predictions use hardcoded/default values** for BMI (22.0) and extracted/estimated x_ray_score (5.0 or extracted from chest_x_ray text)
4. **New TB features** (bacilloscopy_month_1-6, new comorbidities, etc.) are calculated but **NOT used by the model**

## Current State

### Model Expected Features (from `ml/models/model_metadata.json`):
```json
[
  "age",
  "bmi",              ❌ NOT in new dataset
  "hiv_positive",
  "diabetes",
  "smoker",
  "x_ray_score",      ❌ NOT in new dataset (only chest_x_ray text)
  "adherence_mean",
  "adherence_min",
  "adherence_std",
  "modification_count",
  "visit_count"
]
```

### What Feature Extraction Does (`backend/clinical/viewsets.py`):
- Provides **hardcoded BMI = 22.0** (default value)
- Attempts to extract numeric value from `chest_x_ray` text field, defaults to 5.0
- Calculates new features but **doesn't use them** (bacilloscopy_m1, bacilloscopy_m2, etc.)

### What New Dataset Has:
- ✅ `notification_date`, `race`, `state`
- ✅ `clinical_form`, `chest_x_ray` (text), `tuberculin_test`
- ✅ New comorbidities: `aids_comorbidity`, `alcoholism_comorbidity`, `mental_disorder_comorbidity`, `drug_addiction_comorbidity`
- ✅ `bacilloscopy_month_1` through `bacilloscopy_month_6`
- ✅ Treatment drugs: `rifampicin`, `isoniazid`, `ethambutol`, etc.
- ✅ `supervised_treatment`, `occupational_disease`, `days_in_treatment`
- ❌ **NO BMI** (no weight/height fields)
- ❌ **NO x_ray_score** (only text field `chest_x_ray`)

## Solutions

### Option 1: Retrain Model with New Features (RECOMMENDED)

**Steps:**
1. Update `ml/notebooks/modeling.py` to use new TB dataset features
2. Remove BMI and x_ray_score from features
3. Add new features like:
   - `bacilloscopy_month_3_numeric` (binary: positive=1, negative=0)
   - `comorbidity_count` (total count)
   - `supervised_treatment` (binary)
   - `days_in_treatment`
   - Potentially other new features
4. Retrain models and update `model_metadata.json`
5. Update `backend/clinical/viewsets.py` `_extract_patient_features()` to match new model

### Option 2: Keep Current Model, Improve Feature Extraction (TEMPORARY)

**Update feature extraction to:**
- Use more realistic BMI estimation if possible (or document that 22.0 is default)
- Improve x_ray_score extraction from chest_x_ray text
- Add comments/warnings that these are estimated values

### Option 3: Hybrid Approach (CURRENT - Backward Compatible)

**Current implementation** (in `viewsets.py`):
- Provides defaults for missing features (BMI=22.0, x_ray_score=5.0)
- Maintains backward compatibility with existing model
- Calculates new features for future model retraining

**Pros:**
- System continues to work
- No model retraining needed immediately

**Cons:**
- SHAP values show BMI/x_ray_score that aren't real patient data
- New TB features not utilized
- Predictions may be less accurate

## Recommendation

**Retrain the model** (Option 1) because:
1. The new dataset has more relevant features (bacilloscopy results, new comorbidities)
2. BMI and x_ray_score defaults are not meaningful
3. The model should reflect the actual data structure
4. Better predictions with real features

## Next Steps

1. ✅ Dataset updated with new TB features
2. ✅ Feature extraction calculates new features
3. ⚠️ **Model still expects old features** ← NEEDS FIXING
4. ⬜ Retrain model with new features
5. ⬜ Update feature extraction to match retrained model
6. ⬜ Update SHAP visualization for new features

