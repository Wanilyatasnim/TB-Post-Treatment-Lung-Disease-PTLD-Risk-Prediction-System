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
from clinical.permissions import PatientPermission, PredictionPermission, IsClinician
from clinical.audit import log_action




class PatientViewSet(viewsets.ModelViewSet):
    queryset = Patient.objects.all().order_by("-created_at")
    serializer_class = PatientSerializer
    permission_classes = [PatientPermission]
    lookup_field = "patient_id"
    
    def perform_create(self, serializer):
        """Create patient and log action."""
        instance = serializer.save(created_by=self.request.user if self.request.user.is_authenticated else None)
        log_action(
            user=self.request.user if self.request.user.is_authenticated else None,
            action='create',
            model_name='Patient',
            object_id=instance.patient_id,
            description=f'Created patient {instance.patient_id}',
            request=self.request
        )
        return instance
    
    def perform_update(self, serializer):
        """Update patient and log action."""
        instance = serializer.save()
        log_action(
            user=self.request.user if self.request.user.is_authenticated else None,
            action='update',
            model_name='Patient',
            object_id=instance.patient_id,
            description=f'Updated patient {instance.patient_id}',
            request=self.request
        )
        return instance
    
    def perform_destroy(self, instance):
        """Delete patient and log action."""
        patient_id = instance.patient_id
        log_action(
            user=self.request.user if self.request.user.is_authenticated else None,
            action='delete',
            model_name='Patient',
            object_id=patient_id,
            description=f'Deleted patient {patient_id}',
            request=self.request
        )
        instance.delete()


class TreatmentRegimenViewSet(viewsets.ModelViewSet):
    queryset = TreatmentRegimen.objects.select_related("patient").all().order_by("-start_date")
    serializer_class = TreatmentRegimenSerializer
    permission_classes = [IsClinician]
    lookup_field = "regimen_id"


class TreatmentModificationViewSet(viewsets.ModelViewSet):
    queryset = TreatmentModification.objects.select_related("patient", "regimen").all().order_by("-date")
    serializer_class = TreatmentModificationSerializer
    permission_classes = [IsClinician]
    lookup_field = "modification_id"


class MonitoringVisitViewSet(viewsets.ModelViewSet):
    queryset = MonitoringVisit.objects.select_related("patient").all().order_by("-date")
    serializer_class = MonitoringVisitSerializer
    permission_classes = [IsClinician]
    lookup_field = "visit_id"


class RiskPredictionViewSet(viewsets.ModelViewSet):
    queryset = RiskPrediction.objects.select_related("patient").all().order_by("-timestamp")
    serializer_class = RiskPredictionSerializer
    permission_classes = [PredictionPermission]
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
        
        # Generate recommendations
        from ml.recommendation_engine import get_recommendation_engine
        recommendations = []
        try:
            recommendation_engine = get_recommendation_engine()
            recommendations = recommendation_engine.generate_recommendations(
                risk_category=result['risk_category'],
                risk_score=result['risk_score'],
                patient_features=features,
                shap_values=result['shap_values']
            )
        except Exception as e:
            import logging
            logger = logging.getLogger(__name__)
            logger.warning(f"Recommendation generation failed: {e}")
        
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
            confidence=result['confidence'],
            recommendations=recommendations if recommendations else None
        )
        
        # Log prediction generation
        log_action(
            user=request.user if request.user.is_authenticated else None,
            action='predict',
            model_name='RiskPrediction',
            object_id=prediction_id,
            description=f'Generated prediction for patient {patient_id}. Risk: {result["risk_category"]} ({result["risk_score"]:.3f})',
            request=request
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
        Uses data from months 1-3 as prediction start point is month 3-4.
        
        Args:
            patient: Patient model instance
        
        Returns:
            dict: Feature dictionary matching model requirements
        """
        import numpy as np
        
        # Get visit statistics from MonitoringVisit (if available)
        visits = patient.visits.all()
        adherence_values = list(visits.values_list('adherence_pct', flat=True))
        
        # Calculate adherence statistics
        if adherence_values:
            adherence_mean = float(np.mean(adherence_values))
            adherence_min = float(np.min(adherence_values))
            adherence_std = float(np.std(adherence_values))
        else:
            # Default values if no visits yet
            # Could also calculate from days_in_treatment if available
            adherence_mean = 90.0
            adherence_min = 85.0
            adherence_std = 5.0
        
        # Count modifications
        modification_count = patient.modifications.count()
        
        # Count visits
        visit_count = visits.count()
        
        # Extract bacilloscopy results for months 1-3 (available at prediction start)
        # Convert to binary/numeric features if needed
        def bacilloscopy_to_numeric(value):
            """Convert bacilloscopy result to numeric (positive=1, negative/blank=0)"""
            if not value:
                return 0
            value_lower = str(value).lower()
            if any(pos in value_lower for pos in ['positive', '+', 'pos', '1']):
                return 1
            return 0
        
        bacilloscopy_m1 = bacilloscopy_to_numeric(patient.bacilloscopy_month_1)
        bacilloscopy_m2 = bacilloscopy_to_numeric(patient.bacilloscopy_month_2)
        bacilloscopy_m3 = bacilloscopy_to_numeric(patient.bacilloscopy_month_3)
        
        # Calculate bacilloscopy trend (improvement/stability)
        # Positive values indicate improvement (fewer positives over time)
        bacilloscopy_trend = bacilloscopy_m1 - bacilloscopy_m3  # Improvement from M1 to M3
        
        # Calculate total comorbidity count
        comorbidity_count = (
            int(patient.aids_comorbidity) +
            int(patient.alcoholism_comorbidity) +
            int(patient.diabetes) +
            int(patient.mental_disorder_comorbidity) +
            int(patient.drug_addiction_comorbidity) +
            int(patient.smoker) +
            (1 if patient.other_comorbidity else 0)
        )
        
        # Return features matching the updated model (without BMI and x_ray_score)
        # Features: age, hiv_positive, diabetes, smoker, comorbidity_count, 
        #           adherence_mean, adherence_min, adherence_std, modification_count, visit_count
        return {
            'age': int(patient.age),
            'hiv_positive': int(patient.hiv_positive),
            'diabetes': int(patient.diabetes),
            'smoker': int(patient.smoker),
            'comorbidity_count': comorbidity_count,
            'adherence_mean': adherence_mean,
            'adherence_min': adherence_min,
            'adherence_std': adherence_std,
            'modification_count': modification_count,
            'visit_count': visit_count,
            # Additional features calculated for reference (not used by current model)
            'bacilloscopy_m1': bacilloscopy_m1,
            'bacilloscopy_m2': bacilloscopy_m2,
            'bacilloscopy_m3': bacilloscopy_m3,
            'bacilloscopy_trend': bacilloscopy_trend,
            'days_in_treatment': int(patient.days_in_treatment) if patient.days_in_treatment else 90,
            'supervised_treatment': int(patient.supervised_treatment),
        }


