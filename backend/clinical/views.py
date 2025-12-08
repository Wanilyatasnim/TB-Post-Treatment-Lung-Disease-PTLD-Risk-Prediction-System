from django.http import JsonResponse
from django.views.generic import ListView

from clinical.models import Patient


def health(request):
    return JsonResponse({"status": "ok", "service": "clinical-api"})


class PatientListView(ListView):
    model = Patient
    template_name = "patients/list.html"
    context_object_name = "patients"
    paginate_by = 25


