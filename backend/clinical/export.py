"""
Export functionality for patient data and predictions.

Supports CSV and PDF export formats.
"""

import csv
import io
from datetime import datetime
from django.http import HttpResponse
from django.db.models import QuerySet
from clinical.models import Patient, RiskPrediction
from clinical.audit import log_action


def export_patients_csv(patients: QuerySet, user=None, request=None) -> HttpResponse:
    """
    Export patients to CSV format.
    
    Args:
        patients: QuerySet of Patient objects
        user: User performing the export
        request: Django request object
    
    Returns:
        HttpResponse with CSV file
    """
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = f'attachment; filename="patients_export_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv"'
    
    writer = csv.writer(response)
    
    # Write header
    writer.writerow([
        'Patient ID', 'Sex', 'Age', 'BMI', 'HIV Positive', 'Diabetes', 'Smoker',
        'X-Ray Score', 'District', 'Comorbidities', 'Baseline Date', 'Created At'
    ])
    
    # Write data
    for patient in patients:
        writer.writerow([
            patient.patient_id,
            patient.sex,
            patient.age,
            patient.bmi or '',
            'Yes' if patient.hiv_positive else 'No',
            'Yes' if patient.diabetes else 'No',
            'Yes' if patient.smoker else 'No',
            patient.x_ray_score or '',
            patient.district,
            patient.comorbidities,
            patient.baseline_date.strftime('%Y-%m-%d') if patient.baseline_date else '',
            patient.created_at.strftime('%Y-%m-%d %H:%M:%S')
        ])
    
    # Log export action
    log_action(
        user=user,
        action='export',
        model_name='Patient',
        object_id='',
        description=f'Exported {patients.count()} patients to CSV',
        request=request
    )
    
    return response


def export_predictions_csv(predictions: QuerySet, user=None, request=None) -> HttpResponse:
    """
    Export risk predictions to CSV format.
    
    Args:
        predictions: QuerySet of RiskPrediction objects
        user: User performing the export
        request: Django request object
    
    Returns:
        HttpResponse with CSV file
    """
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = f'attachment; filename="predictions_export_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv"'
    
    writer = csv.writer(response)
    
    # Write header
    writer.writerow([
        'Prediction ID', 'Patient ID', 'Risk Score', 'Risk Category', 'Confidence',
        'Model Version', 'Timestamp', 'Created At'
    ])
    
    # Write data
    for prediction in predictions.select_related('patient'):
        writer.writerow([
            prediction.prediction_id,
            prediction.patient.patient_id,
            f"{prediction.risk_score:.4f}",
            prediction.risk_category,
            f"{prediction.confidence:.2f}" if prediction.confidence else '',
            prediction.model_version,
            prediction.timestamp.strftime('%Y-%m-%d %H:%M:%S') if prediction.timestamp else '',
            prediction.created_at.strftime('%Y-%m-%d %H:%M:%S')
        ])
    
    # Log export action
    log_action(
        user=user,
        action='export',
        model_name='RiskPrediction',
        object_id='',
        description=f'Exported {predictions.count()} predictions to CSV',
        request=request
    )
    
    return response


def export_patient_report_pdf(patient: Patient, predictions: QuerySet = None, user=None, request=None) -> HttpResponse:
    """
    Export a comprehensive patient report as PDF.
    
    Note: This is a simplified version. For production, use libraries like reportlab or weasyprint.
    
    Args:
        patient: Patient object
        predictions: QuerySet of RiskPrediction objects for this patient
        user: User performing the export
        request: Django request object
    
    Returns:
        HttpResponse with PDF file (or HTML for now)
    """
    # For now, return HTML. In production, convert to PDF using reportlab or weasyprint
    from django.template.loader import render_to_string
    
    if predictions is None:
        predictions = patient.predictions.all().order_by('-timestamp')
    
    html_content = render_to_string('patients/report.html', {
        'patient': patient,
        'predictions': predictions,
        'regimens': patient.regimens.all(),
        'visits': patient.visits.all(),
        'modifications': patient.modifications.all(),
        'export_date': datetime.now()
    })
    
    response = HttpResponse(html_content, content_type='text/html')
    response['Content-Disposition'] = f'attachment; filename="patient_report_{patient.patient_id}_{datetime.now().strftime("%Y%m%d")}.html"'
    
    # Log export action
    log_action(
        user=user,
        action='export',
        model_name='Patient',
        object_id=patient.patient_id,
        description=f'Exported patient report for {patient.patient_id}',
        request=request
    )
    
    return response






