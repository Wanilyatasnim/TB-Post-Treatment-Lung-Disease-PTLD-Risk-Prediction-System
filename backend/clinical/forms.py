from django import forms

from clinical.models import MonitoringVisit, Patient, TreatmentModification, TreatmentRegimen


class PatientForm(forms.ModelForm):
    class Meta:
        model = Patient
        fields = [
            # Basic Demographics
            "patient_id", "notification_date", "sex", "age", "race", "state", "district",
            # Baseline Clinical
            "treatment", "chest_x_ray", "tuberculin_test", "clinical_form", "baseline_date",
            # Comorbidities
            "hiv_positive", "diabetes", "smoker", "aids_comorbidity", "alcoholism_comorbidity",
            "mental_disorder_comorbidity", "drug_addiction_comorbidity", "other_comorbidity",
            # Initial Laboratory Tests
            "bacilloscopy_sputum", "bacilloscopy_sputum_2", "bacilloscopy_other", "sputum_culture",
            # Monthly Bacilloscopy (Months 1-6)
            "bacilloscopy_month_1", "bacilloscopy_month_2", "bacilloscopy_month_3",
            "bacilloscopy_month_4", "bacilloscopy_month_5", "bacilloscopy_month_6",
            # Treatment Drugs
            "rifampicin", "isoniazid", "ethambutol", "streptomycin", "pyrazinamide",
            "ethionamide", "other_drugs",
            # Treatment Characteristics
            "supervised_treatment", "occupational_disease", "days_in_treatment",
            # Outcome
            "outcome_status",
            # Legacy/Additional
            "bmi", "x_ray_score", "comorbidities"
        ]


class TreatmentRegimenForm(forms.ModelForm):
    class Meta:
        model = TreatmentRegimen
        fields = ["regimen_id", "drugs", "start_date", "end_date", "outcome"]


class TreatmentModificationForm(forms.ModelForm):
    class Meta:
        model = TreatmentModification
        fields = ["modification_id", "modified_drug", "reason", "date", "new_dosage_mg"]


class MonitoringVisitForm(forms.ModelForm):
    class Meta:
        model = MonitoringVisit
        fields = ["visit_id", "date", "adverse_reactions", "adherence_pct", "smear_result", "weight_kg"]

