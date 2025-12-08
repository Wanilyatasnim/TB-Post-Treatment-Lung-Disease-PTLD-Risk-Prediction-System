from rest_framework import permissions, viewsets

from clinical.models import MonitoringVisit, Patient, RiskPrediction, TreatmentModification, TreatmentRegimen
from clinical.serializers import (
    MonitoringVisitSerializer,
    PatientSerializer,
    RiskPredictionSerializer,
    TreatmentModificationSerializer,
    TreatmentRegimenSerializer,
)


class BasePermission(permissions.IsAuthenticated):
    """
    Placeholder for future RBAC; currently requires authentication.
    """

    pass


class PatientViewSet(viewsets.ModelViewSet):
    queryset = Patient.objects.all().order_by("-created_at")
    serializer_class = PatientSerializer
    permission_classes = [BasePermission]
    lookup_field = "patient_id"


class TreatmentRegimenViewSet(viewsets.ModelViewSet):
    queryset = TreatmentRegimen.objects.select_related("patient").all().order_by("-start_date")
    serializer_class = TreatmentRegimenSerializer
    permission_classes = [BasePermission]
    lookup_field = "regimen_id"


class TreatmentModificationViewSet(viewsets.ModelViewSet):
    queryset = TreatmentModification.objects.select_related("patient", "regimen").all().order_by("-date")
    serializer_class = TreatmentModificationSerializer
    permission_classes = [BasePermission]
    lookup_field = "modification_id"


class MonitoringVisitViewSet(viewsets.ModelViewSet):
    queryset = MonitoringVisit.objects.select_related("patient").all().order_by("-date")
    serializer_class = MonitoringVisitSerializer
    permission_classes = [BasePermission]
    lookup_field = "visit_id"


class RiskPredictionViewSet(viewsets.ModelViewSet):
    queryset = RiskPrediction.objects.select_related("patient").all().order_by("-timestamp")
    serializer_class = RiskPredictionSerializer
    permission_classes = [BasePermission]
    lookup_field = "prediction_id"


