"""
URL patterns for researcher-specific views and API endpoints.
"""
from django.urls import path
from clinical.researcher_views import (
    ResearcherDashboardView,
    risk_trend_analysis,
    risk_distribution,
    group_risk_comparison,
    population_shap_analysis,
    outcome_association,
    export_anonymized_data
)

app_name = "researchers"

urlpatterns = [
    # Dashboard
    path("dashboard/", ResearcherDashboardView.as_view(), name="dashboard"),
    
    # API Endpoints
    path("api/risk-trend/", risk_trend_analysis, name="risk-trend"),
    path("api/risk-distribution/", risk_distribution, name="risk-distribution"),
    path("api/group-comparison/", group_risk_comparison, name="group-comparison"),
    path("api/shap-analysis/", population_shap_analysis, name="shap-analysis"),
    path("api/outcome-association/", outcome_association, name="outcome-association"),
    path("api/export/", export_anonymized_data, name="export-data"),
]

