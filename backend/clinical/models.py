from django.conf import settings
from django.db import models


class TimestampedModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class Patient(TimestampedModel):
    patient_id = models.CharField(max_length=20, unique=True)
    sex = models.CharField(max_length=1, choices=[("M", "Male"), ("F", "Female")])
    age = models.PositiveIntegerField()
    bmi = models.FloatField(null=True, blank=True)
    hiv_positive = models.BooleanField(default=False)
    diabetes = models.BooleanField(default=False)
    smoker = models.BooleanField(default=False)
    x_ray_score = models.FloatField(null=True, blank=True)
    district = models.CharField(max_length=255, blank=True)
    comorbidities = models.TextField(blank=True)
    baseline_date = models.DateField(null=True, blank=True)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL, related_name="patients")

    def __str__(self) -> str:
        return f"{self.patient_id} ({self.age}y {self.sex})"


class TreatmentRegimen(TimestampedModel):
    regimen_id = models.CharField(max_length=20, unique=True)
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name="regimens")
    drugs = models.CharField(max_length=255)
    start_date = models.DateField()
    end_date = models.DateField(null=True, blank=True)
    outcome = models.CharField(
        max_length=20,
        choices=[("cured", "Cured"), ("completed", "Completed"), ("failed", "Failed"), ("lost", "Lost"), ("died", "Died")],
        blank=True,
    )

    def __str__(self) -> str:
        return f"{self.regimen_id} for {self.patient.patient_id}"


class TreatmentModification(TimestampedModel):
    modification_id = models.CharField(max_length=30, unique=True)
    regimen = models.ForeignKey(TreatmentRegimen, on_delete=models.CASCADE, related_name="modifications")
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name="modifications")
    modified_drug = models.CharField(max_length=10)
    reason = models.CharField(max_length=50)
    date = models.DateField()
    new_dosage_mg = models.PositiveIntegerField(null=True, blank=True)

    def __str__(self) -> str:
        return f"{self.modification_id} ({self.modified_drug})"


class MonitoringVisit(TimestampedModel):
    visit_id = models.CharField(max_length=30, unique=True)
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name="visits")
    date = models.DateField()
    adverse_reactions = models.CharField(max_length=50, blank=True)
    adherence_pct = models.FloatField(null=True, blank=True)
    smear_result = models.CharField(max_length=20, blank=True)
    weight_kg = models.FloatField(null=True, blank=True)

    def __str__(self) -> str:
        return f"{self.visit_id} for {self.patient.patient_id}"


class RiskPrediction(TimestampedModel):
    prediction_id = models.CharField(max_length=30, unique=True)
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name="predictions")
    risk_score = models.FloatField()
    risk_category = models.CharField(max_length=10)
    model_version = models.CharField(max_length=50)
    shap_values = models.JSONField(null=True, blank=True)
    timestamp = models.DateTimeField()
    confidence = models.FloatField(null=True, blank=True)

    def __str__(self) -> str:
        return f"{self.prediction_id} ({self.risk_category})"


