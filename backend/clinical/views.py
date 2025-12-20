from django.contrib.auth.mixins import LoginRequiredMixin
from django.db import models
from django.db.models import Count, Q, Avg
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.urls import reverse_lazy
from django.views.generic import DetailView, ListView, TemplateView, UpdateView, CreateView

from clinical.forms import MonitoringVisitForm, PatientForm, TreatmentModificationForm, TreatmentRegimenForm
from clinical.models import MonitoringVisit, Patient, RiskPrediction, TreatmentModification, TreatmentRegimen
from clinical.export import export_patients_csv, export_predictions_csv, export_patient_report_pdf
from clinical.audit import log_action


def health(request):
    return JsonResponse({"status": "ok", "service": "clinical-api"})


class PatientListView(LoginRequiredMixin, ListView):
    login_url = "/accounts/login/"
    redirect_field_name = "next"
    model = Patient
    template_name = "patients/list.html"
    context_object_name = "patients"
    paginate_by = 25

    def get_queryset(self):
        # Optimize queryset to prevent N+1 queries
        # Use annotations to check existence without extra queries
        from django.db.models import Exists, OuterRef, Prefetch
        
        queryset = Patient.objects.select_related('created_by').annotate(
            has_regimens=Exists(
                TreatmentRegimen.objects.filter(patient_id=OuterRef('pk'))
            ),
            has_modifications=Exists(
                TreatmentModification.objects.filter(patient_id=OuterRef('pk'))
            ),
        ).prefetch_related(
            Prefetch('regimens', queryset=TreatmentRegimen.objects.only('patient_id', 'drugs', 'outcome', 'start_date').order_by('-start_date')[:1], to_attr='first_regimen'),
            Prefetch('modifications', queryset=TreatmentModification.objects.only('patient_id', 'reason', 'date').order_by('-date')[:1], to_attr='first_modification'),
            Prefetch('visits', queryset=MonitoringVisit.objects.only('patient_id', 'smear_result', 'date').order_by('-date')[:1], to_attr='first_visit'),
        )
        
        # Search by patient_id or state
        search = self.request.GET.get('search')
        if search:
            queryset = queryset.filter(
                models.Q(patient_id__icontains=search) |
                models.Q(state__icontains=search)
            )
        
        # Filter by sex
        sex = self.request.GET.get('sex')
        if sex:
            queryset = queryset.filter(sex=sex)
        
        # Filter by HIV status
        hiv = self.request.GET.get('hiv')
        if hiv == '1':
            queryset = queryset.filter(hiv_positive=True)
        elif hiv == '0':
            queryset = queryset.filter(hiv_positive=False)
        
        # Filter by diabetes
        diabetes = self.request.GET.get('diabetes')
        if diabetes == '1':
            queryset = queryset.filter(diabetes=True)
        elif diabetes == '0':
            queryset = queryset.filter(diabetes=False)
        
        # Filter by smoker
        smoker = self.request.GET.get('smoker')
        if smoker == '1':
            queryset = queryset.filter(smoker=True)
        elif smoker == '0':
            queryset = queryset.filter(smoker=False)
        
        # Filter by age group
        age_group = self.request.GET.get('age_group')
        if age_group:
            if age_group == '0_19':
                queryset = queryset.filter(age__lt=20)
            elif age_group == '20_29':
                queryset = queryset.filter(age__gte=20, age__lt=30)
            elif age_group == '30_39':
                queryset = queryset.filter(age__gte=30, age__lt=40)
            elif age_group == '40_49':
                queryset = queryset.filter(age__gte=40, age__lt=50)
            elif age_group == '50_59':
                queryset = queryset.filter(age__gte=50, age__lt=60)
            elif age_group == '60_plus':
                queryset = queryset.filter(age__gte=60)
        
        # Filter by age range
        age_min = self.request.GET.get('age_min')
        age_max = self.request.GET.get('age_max')
        if age_min:
            try:
                queryset = queryset.filter(age__gte=int(age_min))
            except ValueError:
                pass
        if age_max:
            try:
                queryset = queryset.filter(age__lte=int(age_max))
            except ValueError:
                pass
        
        # Filter by treated before (has regimens)
        treated_before = self.request.GET.get('treated_before')
        if treated_before == '1':
            queryset = queryset.filter(regimens__isnull=False).distinct()
        elif treated_before == '0':
            queryset = queryset.filter(regimens__isnull=True)
        
        # Filter by regimen change (has modifications)
        regimen_change = self.request.GET.get('regimen_change')
        if regimen_change == '1':
            queryset = queryset.filter(modifications__isnull=False).distinct()
        elif regimen_change == '0':
            queryset = queryset.filter(modifications__isnull=True)
        
        # Filter by X-Ray score range
        xray_min = self.request.GET.get('xray_min')
        xray_max = self.request.GET.get('xray_max')
        if xray_min:
            try:
                queryset = queryset.filter(x_ray_score__gte=float(xray_min))
            except (ValueError, TypeError):
                pass
        if xray_max:
            try:
                queryset = queryset.filter(x_ray_score__lte=float(xray_max))
            except (ValueError, TypeError):
                pass
        
        return queryset.order_by('-created_at')


class PatientCreateView(LoginRequiredMixin, CreateView):
    login_url = "/accounts/login/"
    redirect_field_name = "next"
    model = Patient
    form_class = PatientForm
    template_name = "patients/form.html"
    success_url = reverse_lazy("patients:patient-list")


class PatientUpdateView(LoginRequiredMixin, UpdateView):
    login_url = "/accounts/login/"
    redirect_field_name = "next"
    model = Patient
    form_class = PatientForm
    slug_field = "patient_id"
    slug_url_kwarg = "patient_id"
    template_name = "patients/form.html"
    success_url = reverse_lazy("patients:patient-list")


class PatientDetailView(LoginRequiredMixin, DetailView):
    login_url = "/accounts/login/"
    redirect_field_name = "next"
    model = Patient
    slug_field = "patient_id"
    slug_url_kwarg = "patient_id"
    template_name = "patients/detail.html"
    context_object_name = "patient"

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        patient = self.get_object()
        # Optimize queries to prevent N+1
        ctx["regimens"] = patient.regimens.all().order_by('-start_date')
        ctx["modifications"] = patient.modifications.all().order_by('-date')
        ctx["visits"] = patient.visits.all().order_by('-date')
        predictions = patient.predictions.select_related('patient').order_by("-timestamp")[:5]
        
        # Sort SHAP values for each prediction (for template display)
        for pred in predictions:
            if pred.shap_values:
                # Sort by absolute value, descending
                pred.shap_values_sorted = sorted(
                    pred.shap_values.items(),
                    key=lambda x: abs(x[1]),
                    reverse=True
                )
        
        ctx["predictions"] = predictions
        ctx["regimen_form"] = TreatmentRegimenForm()
        ctx["mod_form"] = TreatmentModificationForm()
        ctx["visit_form"] = MonitoringVisitForm()
        return ctx


class DashboardView(LoginRequiredMixin, TemplateView):
    login_url = "/accounts/login/"
    redirect_field_name = "next"
    template_name = "dashboard/overview.html"

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        
        # Patient statistics
        ctx["total_patients"] = Patient.objects.count()
        ctx["total_regimens"] = TreatmentRegimen.objects.count()
        ctx["total_visits"] = MonitoringVisit.objects.count()
        ctx["total_predictions"] = RiskPrediction.objects.count()
        
        # Risk breakdown
        ctx["risk_breakdown"] = (
            RiskPrediction.objects.values("risk_category")
            .annotate(count=Count("id"))
            .order_by("risk_category")
        )
        
        # High risk patients count
        high_risk_count = RiskPrediction.objects.filter(risk_category="high").values("patient").distinct().count()
        ctx["high_risk_patients"] = high_risk_count
        
        # Recent predictions
        ctx["recent_predictions"] = RiskPrediction.objects.select_related("patient").order_by("-timestamp")[:10]
        
        # Treatment outcomes
        ctx["outcomes"] = TreatmentRegimen.objects.values("outcome").annotate(count=Count("id"))
        
        # Average risk score
        avg_risk = RiskPrediction.objects.aggregate(avg=Avg("risk_score"))["avg"]
        ctx["avg_risk_score"] = round(avg_risk, 3) if avg_risk else 0
        
        # Patient demographics
        ctx["male_count"] = Patient.objects.filter(sex="M").count()
        ctx["female_count"] = Patient.objects.filter(sex="F").count()
        ctx["hiv_positive_count"] = Patient.objects.filter(hiv_positive=True).count()
        ctx["diabetes_count"] = Patient.objects.filter(diabetes=True).count()
        ctx["smoker_count"] = Patient.objects.filter(smoker=True).count()
        
        return ctx


class ExportPatientsView(LoginRequiredMixin, ListView):
    """Export patients to CSV."""
    login_url = "/accounts/login/"
    model = Patient
    
    def get(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        return export_patients_csv(queryset, user=request.user, request=request)
    
    def get_queryset(self):
        return Patient.objects.all()


class ExportPredictionsView(LoginRequiredMixin, ListView):
    """Export predictions to CSV."""
    login_url = "/accounts/login/"
    model = RiskPrediction
    
    def get(self, request, *args, **kwargs):
        queryset = RiskPrediction.objects.select_related('patient').all().order_by('-timestamp')
        return export_predictions_csv(queryset, user=request.user, request=request)


class ExportPatientReportView(LoginRequiredMixin, DetailView):
    """Export patient report."""
    login_url = "/accounts/login/"
    model = Patient
    lookup_field = "patient_id"
    
    def get(self, request, *args, **kwargs):
        patient = self.get_object()
        predictions = patient.predictions.all().order_by('-timestamp')
        return export_patient_report_pdf(patient, predictions, user=request.user, request=request)
