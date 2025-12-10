from django.contrib import admin

from clinical.models import AuditLog, MonitoringVisit, Patient, RiskPrediction, TreatmentModification, TreatmentRegimen


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



