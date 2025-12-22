"""
Researcher-specific views and analytics endpoints.
Provides aggregated, anonymized data for research purposes.
"""

from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Avg, Count, Q, F
from django.http import JsonResponse
from django.views import View
from django.views.generic import TemplateView
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status

from clinical.models import Patient, RiskPrediction, TreatmentRegimen
from clinical.permissions import IsResearcher


class ResearcherDashboardView(LoginRequiredMixin, TemplateView):
    """Researcher dashboard with analytics."""
    login_url = "/accounts/login/"
    redirect_field_name = "next"
    template_name = "dashboard/researcher.html"
    
    def dispatch(self, request, *args, **kwargs):
        """Only researchers can access this dashboard."""
        if not request.user.is_authenticated:
            return self.handle_no_permission()
        
        if not hasattr(request.user, 'role') or request.user.role != 'researcher':
            from django.contrib import messages
            from django.shortcuts import redirect
            messages.error(request, "This dashboard is only available to researchers.")
            return redirect('patients:patient-list')
        
        return super().dispatch(request, *args, **kwargs)
    
    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        # Basic counts for display
        ctx["total_patients"] = Patient.objects.count()
        ctx["total_predictions"] = RiskPrediction.objects.count()
        return ctx


@api_view(['GET'])
@permission_classes([IsAuthenticated, IsResearcher])
def risk_trend_analysis(request):
    """
    Compute average PTLD risk over time (Months 1-4).
    Returns data for line chart: x-axis = treatment month, y-axis = average predicted risk.
    """
    # Group predictions by month of treatment (based on days_in_treatment)
    # For simplicity, we'll use prediction timestamp to estimate treatment month
    # In real scenario, this would be based on actual treatment start date
    
    # Get all predictions with patient treatment data
    # Group by treatment month based on days_in_treatment
    # Month 1 = days 0-30, Month 2 = days 31-60, Month 3 = days 61-90, Month 4 = days 91-120
    predictions = RiskPrediction.objects.select_related('patient').filter(
        patient__days_in_treatment__isnull=False
    ).values('patient__days_in_treatment', 'risk_score')
    
    # Group by treatment month
    month_data = {}
    for pred in predictions:
        days = pred['patient__days_in_treatment'] or 0
        # Calculate month: 1-30 days = month 1, 31-60 = month 2, etc.
        if days <= 30:
            month = 1
        elif days <= 60:
            month = 2
        elif days <= 90:
            month = 3
        elif days <= 120:
            month = 4
        else:
            continue  # Skip months beyond 4
        
        if month not in month_data:
            month_data[month] = []
        month_data[month].append(pred['risk_score'])
    
    # Calculate averages
    trend_data = []
    for month in sorted(month_data.keys()):
        avg_risk = sum(month_data[month]) / len(month_data[month])
        trend_data.append({
            'month': month,
            'average_risk': round(avg_risk, 3),
            'sample_size': len(month_data[month])
        })
    
    return Response({
        'data': trend_data,
        'x_axis': 'Treatment Month',
        'y_axis': 'Average Predicted Risk',
        'description': 'Average PTLD risk score by treatment month (Months 1-4)'
    })


@api_view(['GET'])
@permission_classes([IsAuthenticated, IsResearcher])
def risk_distribution(request):
    """
    Return count of low-risk, medium-risk, and high-risk patients.
    Suitable for bar or pie charts.
    """
    distribution = RiskPrediction.objects.values('risk_category').annotate(
        count=Count('id')
    ).order_by('risk_category')
    
    # Format for charts
    categories = {'low': 0, 'medium': 0, 'high': 0}
    for item in distribution:
        categories[item['risk_category']] = item['count']
    
    return Response({
        'data': [
            {'category': 'Low Risk', 'count': categories['low']},
            {'category': 'Medium Risk', 'count': categories['medium']},
            {'category': 'High Risk', 'count': categories['high']}
        ],
        'total': sum(categories.values()),
        'description': 'Distribution of patients by risk category'
    })


@api_view(['GET'])
@permission_classes([IsAuthenticated, IsResearcher])
def group_risk_comparison(request):
    """
    Aggregated risk by age group, sex, smoking status, and HIV status.
    Returns only aggregated statistics, no raw patient data.
    """
    group_type = request.GET.get('group', 'age')  # age, sex, smoking, hiv
    
    if group_type == 'age':
        # Age groups: 0-19, 20-29, 30-39, 40-49, 50-59, 60+
        age_groups = [
            (0, 19, '0-19'),
            (20, 29, '20-29'),
            (30, 39, '30-39'),
            (40, 49, '40-49'),
            (50, 59, '50-59'),
            (60, 200, '60+')
        ]
        
        results = []
        for min_age, max_age, label in age_groups:
            predictions = RiskPrediction.objects.filter(
                patient__age__gte=min_age,
                patient__age__lte=max_age
            )
            avg_risk = predictions.aggregate(avg=Avg('risk_score'))['avg'] or 0
            count = predictions.count()
            
            if count > 0:
                results.append({
                    'group': label,
                    'average_risk': round(avg_risk, 3),
                    'count': count
                })
    
    elif group_type == 'sex':
        results = []
        for sex in ['M', 'F']:
            predictions = RiskPrediction.objects.filter(patient__sex=sex)
            avg_risk = predictions.aggregate(avg=Avg('risk_score'))['avg'] or 0
            count = predictions.count()
            
            if count > 0:
                results.append({
                    'group': 'Male' if sex == 'M' else 'Female',
                    'average_risk': round(avg_risk, 3),
                    'count': count
                })
    
    elif group_type == 'smoking':
        results = []
        for smoker in [True, False]:
            predictions = RiskPrediction.objects.filter(patient__smoker=smoker)
            avg_risk = predictions.aggregate(avg=Avg('risk_score'))['avg'] or 0
            count = predictions.count()
            
            if count > 0:
                results.append({
                    'group': 'Smoker' if smoker else 'Non-Smoker',
                    'average_risk': round(avg_risk, 3),
                    'count': count
                })
    
    elif group_type == 'hiv':
        results = []
        for hiv in [True, False]:
            predictions = RiskPrediction.objects.filter(patient__hiv_positive=hiv)
            avg_risk = predictions.aggregate(avg=Avg('risk_score'))['avg'] or 0
            count = predictions.count()
            
            if count > 0:
                results.append({
                    'group': 'HIV Positive' if hiv else 'HIV Negative',
                    'average_risk': round(avg_risk, 3),
                    'count': count
                })
    
    else:
        return Response(
            {'error': 'Invalid group type. Use: age, sex, smoking, or hiv'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    return Response({
        'group_type': group_type,
        'data': results,
        'description': f'Average risk score by {group_type}'
    })


@api_view(['GET'])
@permission_classes([IsAuthenticated, IsResearcher])
def population_shap_analysis(request):
    """
    Returns global feature importance using mean absolute SHAP values.
    No per-patient SHAP explanations.
    Filters out BMI and x_ray_score features as they don't exist in the dataset.
    """
    # Features to exclude (removed from dataset)
    EXCLUDED_FEATURES = ['bmi', 'x_ray_score', 'xray_score', 'x_ray', 'xray']
    
    # Get all predictions with SHAP values
    predictions = RiskPrediction.objects.filter(shap_values__isnull=False).exclude(shap_values={})
    
    if not predictions.exists():
        return Response({
            'data': [],
            'description': 'No SHAP data available'
        })
    
    # Aggregate SHAP values across all predictions
    feature_importance = {}
    total_predictions = 0
    
    for pred in predictions:
        if pred.shap_values:
            total_predictions += 1
            for feature, value in pred.shap_values.items():
                # Filter out BMI and x_ray_score features (case-insensitive)
                feature_lower = feature.lower()
                if any(excluded in feature_lower for excluded in EXCLUDED_FEATURES):
                    continue  # Skip this feature
                
                if feature not in feature_importance:
                    feature_importance[feature] = []
                feature_importance[feature].append(abs(float(value)))
    
    # Calculate mean absolute SHAP values
    results = []
    for feature, values in feature_importance.items():
        mean_abs_shap = sum(values) / len(values) if values else 0
        results.append({
            'feature': feature,
            'mean_absolute_shap': round(mean_abs_shap, 4),
            'sample_size': len(values)
        })
    
    # Sort by importance (descending)
    results.sort(key=lambda x: x['mean_absolute_shap'], reverse=True)
    
    return Response({
        'data': results,
        'total_predictions': total_predictions,
        'description': 'Global feature importance based on mean absolute SHAP values (BMI and x_ray_score excluded)'
    })


@api_view(['GET'])
@permission_classes([IsAuthenticated, IsResearcher])
def outcome_association(request):
    """
    Compare predicted risk category vs final treatment outcome.
    Returns aggregated statistics (cross-tabulation).
    """
    # Get predictions with patient outcomes
    predictions = RiskPrediction.objects.select_related('patient').filter(
        patient__outcome_status__isnull=False
    ).exclude(patient__outcome_status='')
    
    # Create cross-tabulation
    outcome_categories = ['cured', 'completed', 'failed', 'died', 'lost', 'transferred']
    risk_categories = ['low', 'medium', 'high']
    
    # Initialize matrix
    matrix = {}
    for risk in risk_categories:
        matrix[risk] = {}
        for outcome in outcome_categories:
            matrix[risk][outcome] = 0
    
    # Count associations
    for pred in predictions:
        risk_cat = pred.risk_category
        outcome = pred.patient.outcome_status.lower()
        if risk_cat in matrix and outcome in matrix[risk_cat]:
            matrix[risk_cat][outcome] += 1
    
    # Format for response
    results = []
    for risk in risk_categories:
        row = {'risk_category': risk}
        total = 0
        for outcome in outcome_categories:
            count = matrix[risk][outcome]
            row[outcome] = count
            total += count
        row['total'] = total
        results.append(row)
    
    # Calculate success rates (cured + completed)
    summary = []
    for risk in risk_categories:
        total = sum(matrix[risk].values())
        if total > 0:
            success = matrix[risk].get('cured', 0) + matrix[risk].get('completed', 0)
            success_rate = (success / total) * 100
            summary.append({
                'risk_category': risk,
                'total_patients': total,
                'success_count': success,
                'success_rate': round(success_rate, 2)
            })
    
    return Response({
        'cross_tabulation': results,
        'summary': summary,
        'description': 'Association between predicted risk category and treatment outcome'
    })


@api_view(['GET'])
@permission_classes([IsAuthenticated, IsResearcher])
def export_anonymized_data(request):
    """
    Provide CSV export of anonymized, aggregated dataset.
    Ensures no identifiers (name, ID, address) are included.
    """
    import csv
    from django.http import HttpResponse
    from datetime import datetime
    
    # Create response
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = f'attachment; filename="anonymized_ptld_data_{datetime.now().strftime("%Y%m%d")}.csv"'
    
    writer = csv.writer(response)
    
    # Write header
    writer.writerow([
        'Age_Group', 'Sex', 'HIV_Status', 'Diabetes', 'Smoking', 'Comorbidity_Count',
        'Risk_Score', 'Risk_Category', 'Treatment_Outcome', 'Days_In_Treatment',
        'Adherence_Mean', 'Modification_Count', 'Visit_Count'
    ])
    
    # Get all predictions with patient data (anonymized)
    predictions = RiskPrediction.objects.select_related('patient').filter(
        patient__days_in_treatment__isnull=False
    )
    
    # Calculate age groups
    def get_age_group(age):
        if age < 20:
            return '0-19'
        elif age < 30:
            return '20-29'
        elif age < 40:
            return '30-39'
        elif age < 50:
            return '40-49'
        elif age < 60:
            return '50-59'
        else:
            return '60+'
    
    # Write data rows (anonymized)
    for pred in predictions:
        patient = pred.patient
        
        # Calculate comorbidity count
        comorbidity_count = (
            int(patient.hiv_positive) +
            int(patient.diabetes) +
            int(patient.smoker) +
            int(patient.aids_comorbidity) +
            int(patient.alcoholism_comorbidity) +
            int(patient.mental_disorder_comorbidity) +
            int(patient.drug_addiction_comorbidity) +
            (1 if patient.other_comorbidity else 0)
        )
        
        # Get adherence data (estimated from visits if available)
        visits = patient.visits.all()
        if visits.exists():
            adherence_values = [v.adherence_pct for v in visits if v.adherence_pct]
            adherence_mean = sum(adherence_values) / len(adherence_values) if adherence_values else None
        else:
            adherence_mean = None
        
        modification_count = patient.modifications.count()
        visit_count = visits.count()
        
        writer.writerow([
            get_age_group(patient.age),
            patient.sex,
            'Yes' if patient.hiv_positive else 'No',
            'Yes' if patient.diabetes else 'No',
            'Yes' if patient.smoker else 'No',
            comorbidity_count,
            round(pred.risk_score, 3),
            pred.risk_category,
            patient.outcome_status or '',
            patient.days_in_treatment or '',
            round(adherence_mean, 2) if adherence_mean else '',
            modification_count,
            visit_count
        ])
    
    return response

