from django.contrib import admin

from clinical.models import MonitoringVisit, Patient, RiskPrediction, TreatmentModification, TreatmentRegimen


@admin.register(Patient)
class PatientAdmin(admin.ModelAdmin):
    list_display = ("patient_id", "sex", "age", "hiv_positive", "diabetes", "smoker", "baseline_date")
    search_fields = ("patient_id", "district", "comorbidities")
    list_filter = ("sex", "hiv_positive", "diabetes", "smoker")


@admin.register(TreatmentRegimen)
class TreatmentRegimenAdmin(admin.ModelAdmin):
    list_display = ("regimen_id", "patient", "drugs", "start_date", "end_date", "outcome")
    search_fields = ("regimen_id", "patient__patient_id")
    list_filter = ("outcome",)


@admin.register(TreatmentModification)
class TreatmentModificationAdmin(admin.ModelAdmin):
    list_display = ("modification_id", "patient", "modified_drug", "reason", "date")
    search_fields = ("modification_id", "patient__patient_id")
    list_filter = ("modified_drug", "reason")


@admin.register(MonitoringVisit)
class MonitoringVisitAdmin(admin.ModelAdmin):
    list_display = ("visit_id", "patient", "date", "adverse_reactions", "adherence_pct", "smear_result")
    search_fields = ("visit_id", "patient__patient_id")
    list_filter = ("smear_result",)


@admin.register(RiskPrediction)
class RiskPredictionAdmin(admin.ModelAdmin):
    list_display = ("prediction_id", "patient", "risk_score", "risk_category", "model_version", "timestamp")
    search_fields = ("prediction_id", "patient__patient_id", "model_version")
    list_filter = ("risk_category",)


