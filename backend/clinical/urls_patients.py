from django.urls import path

from clinical.views import DashboardView, PatientCreateView, PatientDetailView, PatientListView, PatientUpdateView

urlpatterns = [
    path("", PatientListView.as_view(), name="patient-list"),
    path("new/", PatientCreateView.as_view(), name="patient-create"),
    path("<str:patient_id>/edit/", PatientUpdateView.as_view(), name="patient-edit"),
    path("<str:patient_id>/", PatientDetailView.as_view(), name="patient-detail"),
    path("dashboard/overview/", DashboardView.as_view(), name="dashboard"),
]


