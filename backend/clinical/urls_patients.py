from django.urls import path

from clinical.views import PatientListView

urlpatterns = [
    path("", PatientListView.as_view(), name="patient-list"),
]


