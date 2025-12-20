from django.conf import settings
from django.db import models


class TimestampedModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class Patient(TimestampedModel):
    # Basic Demographics
    patient_id = models.CharField(max_length=20, unique=True)
    notification_date = models.DateField(null=True, blank=True, help_text="Date of TB notification")
    sex = models.CharField(max_length=1, choices=[("M", "Male"), ("F", "Female")])
    age = models.PositiveIntegerField()
    race = models.CharField(max_length=50, blank=True, help_text="Patient race/ethnicity")
    state = models.CharField(max_length=100, blank=True, help_text="State or region")
    
    # Baseline Clinical Information
    treatment = models.CharField(max_length=50, blank=True, help_text="Treatment type/regimen")
    chest_x_ray = models.CharField(max_length=50, blank=True, help_text="Chest X-ray results")
    tuberculin_test = models.CharField(max_length=50, blank=True, help_text="Tuberculin test results")
    clinical_form = models.CharField(max_length=50, blank=True, help_text="Clinical form of TB")
    
    # Comorbidities
    hiv_positive = models.BooleanField(default=False, help_text="HIV status (maps from HIV field)")
    diabetes = models.BooleanField(default=False, help_text="Diabetes comorbidity (maps from Diabetes_Comorbidity)")
    smoker = models.BooleanField(default=False, help_text="Smoking comorbidity (maps from Smoking_Comorbidity)")
    aids_comorbidity = models.BooleanField(default=False, help_text="AIDS comorbidity")
    alcoholism_comorbidity = models.BooleanField(default=False, help_text="Alcoholism comorbidity")
    mental_disorder_comorbidity = models.BooleanField(default=False, help_text="Mental disorder comorbidity")
    drug_addiction_comorbidity = models.BooleanField(default=False, help_text="Drug addiction comorbidity")
    other_comorbidity = models.CharField(max_length=255, blank=True, help_text="Other comorbidities")
    
    # Laboratory Tests - Initial
    bacilloscopy_sputum = models.CharField(max_length=50, blank=True, help_text="Initial sputum bacilloscopy")
    bacilloscopy_sputum_2 = models.CharField(max_length=50, blank=True, help_text="Second sputum bacilloscopy")
    bacilloscopy_other = models.CharField(max_length=50, blank=True, help_text="Other bacilloscopy results")
    sputum_culture = models.CharField(max_length=50, blank=True, help_text="Sputum culture results")
    
    # Monthly Bacilloscopy Results (Months 1-6)
    bacilloscopy_month_1 = models.CharField(max_length=50, blank=True, help_text="Bacilloscopy result at month 1")
    bacilloscopy_month_2 = models.CharField(max_length=50, blank=True, help_text="Bacilloscopy result at month 2")
    bacilloscopy_month_3 = models.CharField(max_length=50, blank=True, help_text="Bacilloscopy result at month 3")
    bacilloscopy_month_4 = models.CharField(max_length=50, blank=True, help_text="Bacilloscopy result at month 4")
    bacilloscopy_month_5 = models.CharField(max_length=50, blank=True, help_text="Bacilloscopy result at month 5")
    bacilloscopy_month_6 = models.CharField(max_length=50, blank=True, help_text="Bacilloscopy result at month 6")
    
    # Treatment Drugs
    rifampicin = models.BooleanField(default=False, help_text="Rifampicin prescribed")
    isoniazid = models.BooleanField(default=False, help_text="Isoniazid prescribed")
    ethambutol = models.BooleanField(default=False, help_text="Ethambutol prescribed")
    streptomycin = models.BooleanField(default=False, help_text="Streptomycin prescribed")
    pyrazinamide = models.BooleanField(default=False, help_text="Pyrazinamide prescribed")
    ethionamide = models.BooleanField(default=False, help_text="Ethionamide prescribed")
    other_drugs = models.CharField(max_length=255, blank=True, help_text="Other drugs prescribed")
    
    # Treatment Characteristics
    supervised_treatment = models.BooleanField(default=False, help_text="Supervised treatment")
    occupational_disease = models.BooleanField(default=False, help_text="Occupational disease")
    days_in_treatment = models.PositiveIntegerField(null=True, blank=True, help_text="Total days in treatment")
    
    # Outcome
    outcome_status = models.CharField(
        max_length=50, 
        blank=True,
        choices=[
            ("cured", "Cured"),
            ("completed", "Completed"),
            ("failed", "Failed"),
            ("lost", "Lost"),
            ("died", "Died"),
            ("transferred", "Transferred"),
        ],
        help_text="Final treatment outcome status"
    )
    
    # System Fields
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL, related_name="patients")

    def __str__(self) -> str:
        return f"{self.patient_id} ({self.age}y {self.sex})"
    
    def get_bacilloscopy_month_3_4(self):
        """
        Get bacilloscopy results for months 3-4 (prediction start point).
        Returns dict with month 3 and 4 results.
        """
        return {
            'month_3': self.bacilloscopy_month_3 or '',
            'month_4': self.bacilloscopy_month_4 or ''
        }


class TreatmentRegimen(TimestampedModel):
    regimen_id = models.CharField(max_length=20, unique=True)
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name="regimens")
    drugs = models.CharField(max_length=255)
    start_date = models.DateField(null=True, blank=True)
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
    date = models.DateField(null=True, blank=True)
    new_dosage_mg = models.PositiveIntegerField(null=True, blank=True)

    def __str__(self) -> str:
        return f"{self.modification_id} ({self.modified_drug})"


class MonitoringVisit(TimestampedModel):
    visit_id = models.CharField(max_length=30, unique=True)
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name="visits")
    date = models.DateField(null=True, blank=True)
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
    timestamp = models.DateTimeField(null=True, blank=True)
    confidence = models.FloatField(null=True, blank=True)
    
    # SHAP visualization plots
    waterfall_plot = models.CharField(max_length=255, null=True, blank=True)
    force_plot = models.CharField(max_length=255, null=True, blank=True)
    
    # Clinical recommendations
    recommendations = models.JSONField(null=True, blank=True, help_text="Clinical recommendations based on risk prediction")

    def __str__(self) -> str:
        return f"{self.prediction_id} ({self.risk_category})"


class AuditLog(TimestampedModel):
    """
    Audit log for tracking user actions and system events.
    """
    ACTION_CHOICES = [
        ('create', 'Create'),
        ('update', 'Update'),
        ('delete', 'Delete'),
        ('view', 'View'),
        ('predict', 'Generate Prediction'),
        ('export', 'Export Data'),
        ('login', 'Login'),
        ('logout', 'Logout'),
    ]
    
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name="audit_logs")
    action = models.CharField(max_length=20, choices=ACTION_CHOICES)
    model_name = models.CharField(max_length=50, help_text="Model/entity that was acted upon")
    object_id = models.CharField(max_length=100, blank=True, help_text="ID of the object")
    description = models.TextField(help_text="Description of the action")
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(blank=True)
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['-created_at']),
            models.Index(fields=['user', '-created_at']),
            models.Index(fields=['action', '-created_at']),
        ]
    
    def __str__(self) -> str:
        return f"{self.user} - {self.action} - {self.model_name} - {self.created_at}"
