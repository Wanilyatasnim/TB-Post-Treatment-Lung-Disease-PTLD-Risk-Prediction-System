from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import JsonResponse
from django.views.generic import ListView

from clinical.models import Patient


def health(request):
    return JsonResponse({"status": "ok", "service": "clinical-api"})


class PatientListView(LoginRequiredMixin, ListView):
    login_url = "/admin/login/"
    redirect_field_name = "next"
    model = Patient
    template_name = "patients/list.html"
    context_object_name = "patients"
    paginate_by = 25
