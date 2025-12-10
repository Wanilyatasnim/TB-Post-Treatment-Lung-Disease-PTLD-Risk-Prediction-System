from django.urls import path

from clinical.views import (
    DashboardView, 
    ExportPatientReportView,
    ExportPatientsView,
    ExportPredictionsView,
    PatientCreateView, 
    PatientDetailView, 
    PatientListView, 
    PatientUpdateView
)

urlpatterns = [
    path("", PatientListView.as_view(), name="patient-list"),
    path("new/", PatientCreateView.as_view(), name="patient-create"),
    path("<str:patient_id>/edit/", PatientUpdateView.as_view(), name="patient-edit"),
    path("<str:patient_id>/", PatientDetailView.as_view(), name="patient-detail"),
    path("dashboard/overview/", DashboardView.as_view(), name="dashboard"),
    path("export/patients/", ExportPatientsView.as_view(), name="export-patients"),
    path("export/predictions/", ExportPredictionsView.as_view(), name="export-predictions"),
    path("<str:patient_id>/export/", ExportPatientReportView.as_view(), name="export-patient-report"),
]


