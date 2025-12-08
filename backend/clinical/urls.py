from django.urls import include, path
from rest_framework.routers import DefaultRouter

from clinical import viewsets, views

router = DefaultRouter()
router.register("patients", viewsets.PatientViewSet, basename="patients")
router.register("regimens", viewsets.TreatmentRegimenViewSet, basename="regimens")
router.register("modifications", viewsets.TreatmentModificationViewSet, basename="modifications")
router.register("visits", viewsets.MonitoringVisitViewSet, basename="visits")
router.register("predictions", viewsets.RiskPredictionViewSet, basename="predictions")

urlpatterns = [
    path("health/", views.health, name="api-health"),
    path("", include(router.urls)),
]


