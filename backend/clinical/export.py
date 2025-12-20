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
        'Patient ID', 'Notification Date', 'Sex', 'Age', 'Race', 'State',
        'Treatment', 'Clinical Form', 'Chest X-Ray', 'Tuberculin Test',
        'HIV Positive', 'Diabetes', 'Smoker', 'AIDS', 'Alcoholism',
        'Mental Disorder', 'Drug Addiction', 'Other Comorbidity',
        'Bacilloscopy Sputum', 'Bacilloscopy Sputum 2', 'Bacilloscopy Other',
        'Sputum Culture', 'Bacilloscopy Month 1', 'Bacilloscopy Month 2',
        'Bacilloscopy Month 3', 'Bacilloscopy Month 4', 'Bacilloscopy Month 5',
        'Bacilloscopy Month 6', 'Rifampicin', 'Isoniazid', 'Ethambutol',
        'Streptomycin', 'Pyrazinamide', 'Ethionamide', 'Other Drugs',
        'Supervised Treatment', 'Occupational Disease', 'Days In Treatment',
        'Outcome Status', 'Created At'
    ])
    
    # Write data
    for patient in patients:
        writer.writerow([
            patient.patient_id,
            patient.notification_date.strftime('%Y-%m-%d') if patient.notification_date else '',
            patient.sex,
            patient.age,
            patient.race or '',
            patient.state or '',
            patient.treatment or '',
            patient.clinical_form or '',
            patient.chest_x_ray or '',
            patient.tuberculin_test or '',
            'Yes' if patient.hiv_positive else 'No',
            'Yes' if patient.diabetes else 'No',
            'Yes' if patient.smoker else 'No',
            'Yes' if patient.aids_comorbidity else 'No',
            'Yes' if patient.alcoholism_comorbidity else 'No',
            'Yes' if patient.mental_disorder_comorbidity else 'No',
            'Yes' if patient.drug_addiction_comorbidity else 'No',
            patient.other_comorbidity or '',
            patient.bacilloscopy_sputum or '',
            patient.bacilloscopy_sputum_2 or '',
            patient.bacilloscopy_other or '',
            patient.sputum_culture or '',
            patient.bacilloscopy_month_1 or '',
            patient.bacilloscopy_month_2 or '',
            patient.bacilloscopy_month_3 or '',
            patient.bacilloscopy_month_4 or '',
            patient.bacilloscopy_month_5 or '',
            patient.bacilloscopy_month_6 or '',
            'Yes' if patient.rifampicin else 'No',
            'Yes' if patient.isoniazid else 'No',
            'Yes' if patient.ethambutol else 'No',
            'Yes' if patient.streptomycin else 'No',
            'Yes' if patient.pyrazinamide else 'No',
            'Yes' if patient.ethionamide else 'No',
            patient.other_drugs or '',
            'Yes' if patient.supervised_treatment else 'No',
            'Yes' if patient.occupational_disease else 'No',
            patient.days_in_treatment or '',
            patient.outcome_status or '',
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






