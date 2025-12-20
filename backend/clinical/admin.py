from django.contrib import admin

from clinical.models import AuditLog, MonitoringVisit, Patient, RiskPrediction, TreatmentModification, TreatmentRegimen


@admin.register(Patient)
class PatientAdmin(admin.ModelAdmin):
    list_display = ("patient_id", "sex", "age", "notification_date", "state", "hiv_positive", "outcome_status", "days_in_treatment")
    search_fields = ("patient_id", "district", "state", "race", "comorbidities")
    list_filter = (
        "sex", 
        "hiv_positive", 
        "diabetes", 
        "smoker", 
        "aids_comorbidity",
        "outcome_status",
        "supervised_treatment",
        "state"
    )
    fieldsets = (
        ("Basic Demographics", {
            "fields": ("patient_id", "notification_date", "sex", "age", "race", "state", "district")
        }),
        ("Clinical Information", {
            "fields": ("treatment", "clinical_form", "chest_x_ray", "tuberculin_test", "baseline_date")
        }),
        ("Comorbidities", {
            "fields": (
                "hiv_positive", "diabetes", "smoker", "aids_comorbidity",
                "alcoholism_comorbidity", "mental_disorder_comorbidity",
                "drug_addiction_comorbidity", "other_comorbidity", "comorbidities"
            )
        }),
        ("Laboratory Tests - Initial", {
            "fields": ("bacilloscopy_sputum", "bacilloscopy_sputum_2", "bacilloscopy_other", "sputum_culture")
        }),
        ("Monthly Bacilloscopy Results", {
            "fields": (
                "bacilloscopy_month_1", "bacilloscopy_month_2", "bacilloscopy_month_3",
                "bacilloscopy_month_4", "bacilloscopy_month_5", "bacilloscopy_month_6"
            ),
            "description": "Months 1-3 are used for prediction (prediction start is months 3-4)"
        }),
        ("Treatment Drugs", {
            "fields": (
                "rifampicin", "isoniazid", "ethambutol", "streptomycin",
                "pyrazinamide", "ethionamide", "other_drugs"
            )
        }),
        ("Treatment Characteristics", {
            "fields": ("supervised_treatment", "occupational_disease", "days_in_treatment", "outcome_status")
        }),
        ("Additional Information", {
            "fields": ("bmi", "x_ray_score"),
            "classes": ("collapse",)
        }),
        ("System", {
            "fields": ("created_by", "created_at", "updated_at"),
            "classes": ("collapse",)
        }),
    )
    readonly_fields = ("created_at", "updated_at")


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


@admin.register(AuditLog)
class AuditLogAdmin(admin.ModelAdmin):
    list_display = ("user", "action", "model_name", "object_id", "created_at", "ip_address")
    list_filter = ("action", "model_name", "created_at")
    search_fields = ("user__username", "object_id", "description")
    readonly_fields = ("user", "action", "model_name", "object_id", "description", "ip_address", "user_agent", "created_at", "updated_at")
    date_hierarchy = "created_at"
    
    def has_add_permission(self, request):
        return False  # Audit logs should only be created by the system
    
    def has_change_permission(self, request, obj=None):
        return False  # Audit logs should not be modified



