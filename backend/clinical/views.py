from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Count
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.urls import reverse_lazy
from django.views.generic import DetailView, ListView, TemplateView, UpdateView, CreateView

from clinical.forms import PatientForm, TreatmentRegimenForm
from clinical.models import Patient, RiskPrediction, TreatmentRegimen


def health(request):
    return JsonResponse({"status": "ok", "service": "clinical-api"})


class PatientListView(LoginRequiredMixin, ListView):
    login_url = "/admin/login/"
    redirect_field_name = "next"
    model = Patient
    template_name = "patients/list.html"
    context_object_name = "patients"
    paginate_by = 25


class PatientCreateView(LoginRequiredMixin, CreateView):
    login_url = "/admin/login/"
    redirect_field_name = "next"
    model = Patient
    form_class = PatientForm
    template_name = "patients/form.html"
    success_url = reverse_lazy("patients:patient-list")


class PatientUpdateView(LoginRequiredMixin, UpdateView):
    login_url = "/admin/login/"
    redirect_field_name = "next"
    model = Patient
    form_class = PatientForm
    slug_field = "patient_id"
    slug_url_kwarg = "patient_id"
    template_name = "patients/form.html"
    success_url = reverse_lazy("patients:patient-list")


class PatientDetailView(LoginRequiredMixin, DetailView):
    login_url = "/admin/login/"
    redirect_field_name = "next"
    model = Patient
    slug_field = "patient_id"
    slug_url_kwarg = "patient_id"
    template_name = "patients/detail.html"
    context_object_name = "patient"

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        patient = self.get_object()
        ctx["regimens"] = patient.regimens.all()
        ctx["modifications"] = patient.modifications.all()
        ctx["visits"] = patient.visits.all()
        ctx["predictions"] = patient.predictions.all().order_by("-timestamp")[:5]
        return ctx


class DashboardView(LoginRequiredMixin, TemplateView):
    login_url = "/admin/login/"
    redirect_field_name = "next"
    template_name = "dashboard/overview.html"

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["total_patients"] = Patient.objects.count()
        ctx["risk_breakdown"] = (
            RiskPrediction.objects.values("risk_category").annotate(count=Count("id")).order_by("risk_category")
        )
        ctx["recent_predictions"] = RiskPrediction.objects.order_by("-timestamp")[:10]
        ctx["outcomes"] = TreatmentRegimen.objects.values("outcome").annotate(count=Count("id"))
        return ctx
