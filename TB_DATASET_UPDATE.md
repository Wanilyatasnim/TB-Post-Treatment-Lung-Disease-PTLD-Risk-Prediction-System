# TB Dataset Features Update

## Summary

Updated the database schema and related components to support the new TB dataset features. The system now includes all fields from the new dataset, with a focus on using months 1-3 data for predictions (prediction start point is months 3-4).

## Changes Made

### 1. Patient Model Updates (`backend/clinical/models.py`)

Added all new TB-specific fields to the `Patient` model:

#### Basic Demographics
- `notification_date` - Date of TB notification
- `race` - Patient race/ethnicity
- `state` - State or region

#### Baseline Clinical Information
- `treatment` - Treatment type/regimen
- `chest_x_ray` - Chest X-ray results
- `tuberculin_test` - Tuberculin test results
- `clinical_form` - Clinical form of TB

#### Comorbidities
- `aids_comorbidity` - AIDS comorbidity
- `alcoholism_comorbidity` - Alcoholism comorbidity
- `mental_disorder_comorbidity` - Mental disorder comorbidity
- `drug_addiction_comorbidity` - Drug addiction comorbidity
- `other_comorbidity` - Other comorbidities (CharField)

#### Laboratory Tests - Initial
- `bacilloscopy_sputum` - Initial sputum bacilloscopy
- `bacilloscopy_sputum_2` - Second sputum bacilloscopy
- `bacilloscopy_other` - Other bacilloscopy results
- `sputum_culture` - Sputum culture results

#### Monthly Bacilloscopy Results (Months 1-6)
- `bacilloscopy_month_1` through `bacilloscopy_month_6` - Monthly bacilloscopy results
- **Key for predictions**: Months 1-3 are used for prediction (months 3-4 is the prediction start point)

#### Treatment Drugs
- `rifampicin`, `isoniazid`, `ethambutol`, `streptomycin`, `pyrazinamide`, `ethionamide` - Individual drug flags
- `other_drugs` - Other drugs prescribed

#### Treatment Characteristics
- `supervised_treatment` - Supervised treatment flag
- `occupational_disease` - Occupational disease flag
- `days_in_treatment` - Total days in treatment
- `outcome_status` - Final treatment outcome (cured, completed, failed, lost, died, transferred)

### 2. Database Migration

Created migration: `0006_add_tb_dataset_features.py`

**To apply the migration:**
```bash
cd backend
python manage.py migrate clinical
```

**Note:** If using Supabase, the migration will need to be applied there as well.

### 3. Form Updates (`backend/clinical/forms.py`)

Updated `PatientForm` to include all new fields. The form now supports all TB dataset features.

### 4. Feature Extraction Updates (`backend/clinical/viewsets.py`)

Updated `_extract_patient_features()` method to:
- Extract bacilloscopy results for months 1-3 (prediction start point)
- Convert bacilloscopy results to numeric values
- Calculate bacilloscopy trend (improvement from month 1 to month 3)
- Calculate total comorbidity count
- Extract X-ray score from `chest_x_ray` field if `x_ray_score` not available
- Include additional features for future model retraining:
  - `bacilloscopy_m1`, `bacilloscopy_m2`, `bacilloscopy_m3`
  - `bacilloscopy_trend`
  - `comorbidity_count`
  - `days_in_treatment`
  - `supervised_treatment`

**Note:** The current ML model still uses the original feature set. The new features are calculated but not yet used by the model. You'll need to retrain the model with the new dataset to use these features.

### 5. Template Updates (`backend/templates/patients/detail.html`)

Added new sections to display:
- **TB-Specific Information**: Treatment, clinical form, chest X-ray, tuberculin test, sputum culture, supervised treatment, days in treatment, outcome status
- **Comorbidities**: All new comorbidity fields
- **Treatment Drugs**: All drug prescription flags
- **Monthly Bacilloscopy Results**: Visual table showing months 1-6, with emphasis on months 3-4 (prediction start point)

### 6. API Serializer

The `PatientSerializer` already uses `fields = "__all__"`, so it automatically includes all new fields in API responses.

## Dataset Field Mapping

| Dataset Field | Model Field | Type |
|--------------|-------------|------|
| Notification_Date | notification_date | DateField |
| Sex | sex | CharField (M/F) |
| Race | race | CharField |
| Age | age | PositiveIntegerField |
| Treatment | treatment | CharField |
| Chest_X_Ray | chest_x_ray | CharField |
| Tuberculin_Test | tuberculin_test | CharField |
| Clinical_Form | clinical_form | CharField |
| AIDS_Comorbidity | aids_comorbidity | BooleanField |
| Alcoholism_Comorbidity | alcoholism_comorbidity | BooleanField |
| Diabetes_Comorbidity | diabetes | BooleanField |
| Mental_Disorder_Comorbidity | mental_disorder_comorbidity | BooleanField |
| Other_Comorbidity | other_comorbidity | CharField |
| Drug_Addiction_Comorbidity | drug_addiction_comorbidity | BooleanField |
| Smoking_Comorbidity | smoker | BooleanField |
| Bacilloscopy_Sputum | bacilloscopy_sputum | CharField |
| Bacilloscopy_Sputum_2 | bacilloscopy_sputum_2 | CharField |
| Bacilloscopy_Other | bacilloscopy_other | CharField |
| Sputum_Culture | sputum_culture | CharField |
| HIV | hiv_positive | BooleanField |
| Rifampicin | rifampicin | BooleanField |
| Isoniazid | isoniazid | BooleanField |
| Ethambutol | ethambutol | BooleanField |
| Streptomycin | streptomycin | BooleanField |
| Pyrazinamide | pyrazinamide | BooleanField |
| Ethionamide | ethionamide | BooleanField |
| Other_Drugs | other_drugs | CharField |
| Supervised_Treatment | supervised_treatment | BooleanField |
| Occupational_Disease | occupational_disease | BooleanField |
| Bacilloscopy_Month_1 | bacilloscopy_month_1 | CharField |
| Bacilloscopy_Month_2 | bacilloscopy_month_2 | CharField |
| Bacilloscopy_Month_3 | bacilloscopy_month_3 | CharField |
| Bacilloscopy_Month_4 | bacilloscopy_month_4 | CharField |
| Bacilloscopy_Month_5 | bacilloscopy_month_5 | CharField |
| Bacilloscopy_Month_6 | bacilloscopy_month_6 | CharField |
| Outcome_Status | outcome_status | CharField |
| State | state | CharField |
| Days_In_Treatment | days_in_treatment | PositiveIntegerField |

## Prediction Logic

The prediction system uses data from **months 1-3** as the prediction start point is **months 3-4**. This means:
- When generating a prediction, the system extracts features from months 1-3 bacilloscopy results
- The bacilloscopy trend (improvement from month 1 to month 3) is calculated
- Other baseline features (comorbidities, treatment drugs, etc.) are also included

## Next Steps

### 1. Apply Migration
```bash
cd backend
python manage.py migrate clinical
```

### 2. Retrain ML Model (Recommended)

The current ML model was trained on a different feature set. To fully utilize the new TB dataset features:

1. Prepare your new dataset CSV with all the fields
2. Update the feature engineering in `ml/notebooks/modeling.py` to use:
   - Monthly bacilloscopy results (months 1-3)
   - All comorbidity flags
   - Treatment drug information
   - Other TB-specific features
3. Retrain the model with the new features
4. Update `model_metadata.json` with the new feature list
5. The feature extraction in `viewsets.py` will automatically use the new features

### 3. Data Import

If you have existing data in CSV format:
1. Use Django admin or create a data import script
2. Map CSV columns to model fields (see mapping table above)
3. Import patient records

### 4. Testing

Test the following:
- Patient creation/editing with new fields
- API endpoints return all new fields
- Feature extraction for predictions works correctly
- Patient detail page displays all new information
- Monthly bacilloscopy results are properly displayed

## Important Notes

1. **Backward Compatibility**: Existing patient records will have `null` or default values for new fields. This is safe.

2. **ML Model**: The current model still expects the original feature set. Predictions will work but won't use new features until the model is retrained.

3. **Supabase**: If using Supabase, remember to apply migrations there as well, or use Supabase migration tools.

4. **Form Display**: The form will show all fields. You may want to organize them into sections or use field groups for better UX.

5. **Data Validation**: Consider adding validation for:
   - Bacilloscopy results format (positive/negative/scanty, etc.)
   - Date ranges (notification_date should be before baseline_date)
   - Days in treatment consistency

## Model Method

Added helper method to Patient model:
- `get_bacilloscopy_month_3_4()` - Returns dict with month 3 and 4 bacilloscopy results for prediction start point

## Files Modified

1. `backend/clinical/models.py` - Patient model updated
2. `backend/clinical/forms.py` - PatientForm updated
3. `backend/clinical/viewsets.py` - Feature extraction updated
4. `backend/templates/patients/detail.html` - Template updated with new sections
5. `backend/clinical/migrations/0006_add_tb_dataset_features.py` - New migration created

## Files That May Need Updates (Future)

1. `ml/notebooks/modeling.py` - Retrain model with new features
2. `ml/notebooks/eda.py` - Update EDA for new dataset
3. `backend/clinical/views.py` - Add filters for new fields if needed
4. `backend/templates/patients/list.html` - Display new fields in list view if needed

