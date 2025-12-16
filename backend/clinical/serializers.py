from rest_framework import serializers

from clinical.models import MonitoringVisit, Patient, RiskPrediction, TreatmentModification, TreatmentRegimen


class PatientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Patient
        fields = "__all__"


class TreatmentRegimenSerializer(serializers.ModelSerializer):
    patient_id = serializers.ReadOnlyField(source="patient.patient_id")

    class Meta:
        model = TreatmentRegimen
        fields = "__all__"


class TreatmentModificationSerializer(serializers.ModelSerializer):
    patient_id = serializers.ReadOnlyField(source="patient.patient_id")
    regimen_id = serializers.ReadOnlyField(source="regimen.regimen_id")

    class Meta:
        model = TreatmentModification
        fields = "__all__"


class MonitoringVisitSerializer(serializers.ModelSerializer):
    patient_id = serializers.ReadOnlyField(source="patient.patient_id")

    class Meta:
        model = MonitoringVisit
        fields = "__all__"


class RiskPredictionSerializer(serializers.ModelSerializer):
    patient_id = serializers.ReadOnlyField(source="patient.patient_id")

    class Meta:
        model = RiskPrediction
        fields = "__all__"




