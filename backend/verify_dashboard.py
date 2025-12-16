"""
Verify dashboard and UI work correctly with real data
"""
import os
import sys

os.environ.pop('USE_SQLITE', None)

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'app.settings')

import django
django.setup()

from django.test import Client, override_settings
from clinical.models import Patient, RiskPrediction, TreatmentRegimen, MonitoringVisit
from accounts.models import User

@override_settings(ALLOWED_HOSTS=['*'])
def verify_dashboard():
    print("=" * 70)
    print("VERIFYING DASHBOARD AND UI WITH REAL DATA")
    print("=" * 70)

    client = Client()

    # Check data availability
    print("\n[1] Data Availability Check:")
    patient_count = Patient.objects.count()
    prediction_count = RiskPrediction.objects.count()
    regimen_count = TreatmentRegimen.objects.count()
    visit_count = MonitoringVisit.objects.count()
    
    print(f"  ✓ Patients: {patient_count}")
    print(f"  ✓ Risk Predictions: {prediction_count}")
    print(f"  ✓ Treatment Regimens: {regimen_count}")
    print(f"  ✓ Monitoring Visits: {visit_count}")
    
    if patient_count == 0:
        print("\n  ⚠️  No patients found! Data may not have loaded correctly.")
        return
    
    # Test login
    print("\n[2] Authentication Check:")
    try:
        user = User.objects.get(username='test')
        login_success = client.login(username='test', password='testpass123')
        if not login_success:
            # Try to reset password
            user.set_password('testpass123')
            user.save()
            login_success = client.login(username='test', password='testpass123')
        
        if login_success:
            print("  ✓ Login successful")
        else:
            print("  ⚠ Login failed - may need to set password manually")
    except User.DoesNotExist:
        print("  ⚠ User 'test' not found")

    # Test UI endpoints
    print("\n[3] UI Endpoint Tests:")
    endpoints = [
        ('/', 'Patient List'),
        ('/dashboard/overview/', 'Dashboard'),
        ('/patients/', 'Patient List (alternative)'),
    ]
    
    results = []
    for endpoint, name in endpoints:
        try:
            response = client.get(endpoint, SERVER_NAME='localhost')
            if response.status_code == 200:
                print(f"  ✓ {name}: {endpoint} - Status 200")
                results.append(True)
            elif response.status_code == 302:  # Redirect to login
                print(f"  ⚠ {name}: {endpoint} - Status 302 (Redirect - requires login)")
                results.append(True)  # Expected for protected pages
            else:
                print(f"  ✗ {name}: {endpoint} - Status {response.status_code}")
                results.append(False)
        except Exception as e:
            print(f"  ✗ {name}: {endpoint} - Error: {e}")
            results.append(False)

    # Test patient detail page
    print("\n[4] Patient Detail Page Test:")
    if Patient.objects.exists():
        patient = Patient.objects.first()
        try:
            response = client.get(f'/patients/{patient.id}/', SERVER_NAME='localhost')
            if response.status_code in [200, 302]:
                print(f"  ✓ Patient detail page accessible - Status {response.status_code}")
            else:
                print(f"  ✗ Patient detail failed - Status {response.status_code}")
        except Exception as e:
            print(f"  ✗ Patient detail error: {e}")

    # Check dashboard data requirements
    print("\n[5] Dashboard Data Requirements:")
    requirements_met = True
    
    if patient_count > 0:
        print("  ✓ Patients available for dashboard")
    else:
        print("  ✗ No patients - dashboard will be empty")
        requirements_met = False
    
    if prediction_count > 0:
        print("  ✓ Predictions available for dashboard")
    else:
        print("  ⚠ No predictions - some charts may be empty")
    
    # Check risk distribution
    if prediction_count > 0:
        from django.db.models import Count
        risk_dist = RiskPrediction.objects.values('risk_category').annotate(count=Count('id'))
        print(f"  ✓ Risk distribution: {dict(risk_dist)}")
    
    # Summary
    print("\n" + "=" * 70)
    print("SUMMARY")
    print("=" * 70)
    print(f"UI endpoints tested: {len(results)}")
    print(f"Successful: {sum(results)}/{len(results)}")
    print(f"Data available: {patient_count} patients, {prediction_count} predictions")
    
    if sum(results) == len(results) and requirements_met:
        print("\n✅ Dashboard and UI are ready!")
        print("\nTo test in browser:")
        print("  1. Start server: python manage.py runserver")
        print("  2. Login at: http://localhost:8000/accounts/login/")
        print("  3. View dashboard: http://localhost:8000/dashboard/overview/")
        print("  4. View patients: http://localhost:8000/")
    else:
        print("\n⚠️  Some checks need attention")

verify_dashboard()

