from django import forms

from clinical.models import Patient, TreatmentModification, TreatmentRegimen


class PatientForm(forms.ModelForm):
    class Meta:
        model = Patient
        fields = ["patient_id", "sex", "age", "bmi", "hiv_positive", "diabetes", "smoker", "x_ray_score", "district", "comorbidities", "baseline_date"]


class TreatmentRegimenForm(forms.ModelForm):
    class Meta:
        model = TreatmentRegimen
        fields = ["regimen_id", "drugs", "start_date", "end_date", "outcome"]


class TreatmentModificationForm(forms.ModelForm):
    class Meta:
        model = TreatmentModification
        fields = ["modification_id", "modified_drug", "reason", "date", "new_dosage_mg"]

