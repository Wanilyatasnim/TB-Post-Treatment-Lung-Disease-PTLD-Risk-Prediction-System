import random
from datetime import datetime

from rest_framework import permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

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
    RBAC placeholder: extend with per-role checks later.
    """

    def has_permission(self, request, view):
        if not super().has_permission(request, view):
            return False
        # Example: allow all authenticated for now; hook per-role logic here.
        return True


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

    @action(detail=False, methods=["post"])
    def predict(self, request):
        """
        Stub prediction endpoint (Phase 1/2): returns synthetic risk until real model is wired.
        Expects patient_id; optionally accepts payload for logging.
        """
        patient_id = request.data.get("patient_id")
        if not patient_id:
            return Response({"detail": "patient_id is required"}, status=status.HTTP_400_BAD_REQUEST)
        try:
            patient = Patient.objects.get(patient_id=patient_id)
        except Patient.DoesNotExist:
            return Response({"detail": "patient not found"}, status=status.HTTP_404_NOT_FOUND)

        # Simple heuristic stub
        base = 0.15
        score = base + random.random() * 0.6
        score = round(min(score, 0.99), 4)
        category = "low" if score < 0.33 else "medium" if score < 0.66 else "high"
        payload = {
            "prediction_id": f"PR-{patient_id}-{int(datetime.utcnow().timestamp())}",
            "patient": patient,
            "risk_score": score,
            "risk_category": category,
            "model_version": "v0.1.0-stub",
            "shap_values": {},
            "timestamp": datetime.utcnow(),
            "confidence": round(0.6 + random.random() * 0.35, 3),
        }
        prediction, _ = RiskPrediction.objects.update_or_create(prediction_id=payload["prediction_id"], defaults=payload)
        return Response(RiskPredictionSerializer(prediction).data, status=status.HTTP_201_CREATED)


