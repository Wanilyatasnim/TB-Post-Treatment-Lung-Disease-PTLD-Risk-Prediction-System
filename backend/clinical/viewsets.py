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


class AllowAnyForPredict(permissions.BasePermission):
    """
    Allow prediction endpoint to be accessed without authentication for development.
    In production, this should require authentication.
    """
    
    def has_permission(self, request, view):
        # Allow POST to predict endpoint without authentication
        if view.action == 'predict' and request.method == 'POST':
            return True
        # For other actions, require authentication
        return request.user and request.user.is_authenticated


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
    permission_classes = [AllowAnyForPredict]  # Allow predictions without auth for now
    lookup_field = "prediction_id"

    @action(detail=False, methods=["post"])
    def predict(self, request):
        """
        Generate PTLD risk prediction using ML model.
        Expects patient_id in request data.
        """
        patient_id = request.data.get("patient_id")
        if not patient_id:
            return Response({"detail": "patient_id is required"}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            patient = Patient.objects.get(patient_id=patient_id)
        except Patient.DoesNotExist:
            return Response({"detail": "patient not found"}, status=status.HTTP_404_NOT_FOUND)

        # Extract patient features for ML model
        try:
            features = self._extract_patient_features(patient)
        except Exception as e:
            return Response(
                {"detail": f"Feature extraction failed: {str(e)}"}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
        
        # Get prediction from ML model
        from ml.predictor import get_predictor
        try:
            predictor = get_predictor()
            result = predictor.predict(features)
        except Exception as e:
            return Response(
                {"detail": f"Prediction failed: {str(e)}"}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
        
        # Save prediction to database
        prediction_id = f"PR-{patient_id}-{int(datetime.utcnow().timestamp())}"
        prediction = RiskPrediction.objects.create(
            prediction_id=prediction_id,
            patient=patient,
            risk_score=result['risk_score'],
            risk_category=result['risk_category'],
            model_version=result['model_version'],
            shap_values=result['shap_values'],
            timestamp=datetime.utcnow(),
            confidence=result['confidence']
        )
        
        # Generate SHAP visualizations
        from ml.shap_visualizer import get_visualizer
        try:
            visualizer = get_visualizer()
            
            # Get feature names from predictor metadata
            feature_names = predictor.feature_cols
            
            # Generate waterfall plot
            waterfall_path = visualizer.generate_waterfall_plot(
                shap_values_dict=result['shap_values'],
                feature_values=features,
                feature_names=feature_names,
                prediction_id=prediction_id
            )
            
            # Generate force plot (bar chart)
            force_path = visualizer.generate_force_plot(
                shap_values_dict=result['shap_values'],
                feature_values=features,
                feature_names=feature_names,
                prediction_id=prediction_id
            )
            
            # Update prediction with plot paths
            prediction.waterfall_plot = waterfall_path
            prediction.force_plot = force_path
            prediction.save()
            
        except Exception as e:
            # Log error but don't fail the request
            import logging
            logger = logging.getLogger(__name__)
            logger.warning(f"SHAP visualization generation failed: {e}")
        
        return Response(RiskPredictionSerializer(prediction).data, status=status.HTTP_201_CREATED)
    
    def _extract_patient_features(self, patient):
        """
        Extract features from patient record for ML prediction.
        
        Args:
            patient: Patient model instance
        
        Returns:
            dict: Feature dictionary matching model requirements
        """
        import numpy as np
        
        # Get visit statistics
        visits = patient.visits.all()
        adherence_values = list(visits.values_list('adherence_pct', flat=True))
        
        # Calculate adherence statistics
        if adherence_values:
            adherence_mean = float(np.mean(adherence_values))
            adherence_min = float(np.min(adherence_values))
            adherence_std = float(np.std(adherence_values))
        else:
            # Default values if no visits yet
            adherence_mean = 90.0
            adherence_min = 85.0
            adherence_std = 5.0
        
        # Count modifications
        modification_count = patient.modifications.count()
        
        # Count visits
        visit_count = visits.count()
        
        return {
            'age': int(patient.age),
            'bmi': float(patient.bmi) if patient.bmi else 22.0,
            'hiv_positive': int(patient.hiv_positive),
            'diabetes': int(patient.diabetes),
            'smoker': int(patient.smoker),
            'x_ray_score': float(patient.x_ray_score) if patient.x_ray_score else 5.0,
            'adherence_mean': adherence_mean,
            'adherence_min': adherence_min,
            'adherence_std': adherence_std,
            'modification_count': modification_count,
            'visit_count': visit_count
        }


