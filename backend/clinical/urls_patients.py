from django.urls import path

from clinical.views import DashboardView, PatientDetailView, PatientListView

urlpatterns = [
    path("", PatientListView.as_view(), name="patient-list"),
    path("<str:patient_id>/", PatientDetailView.as_view(), name="patient-detail"),
    path("dashboard/overview/", DashboardView.as_view(), name="dashboard"),
]


