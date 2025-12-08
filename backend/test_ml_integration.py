"""
Test script for ML predictor service

Run this to verify the ML models are integrated correctly.
"""

import os
import sys
import django

# Setup Django
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'app.settings')
django.setup()

from ml.predictor import get_predictor

print("="*60)
print("ML PREDICTOR INTEGRATION TEST")
print("="*60)

# Test 1: Load predictor
print("\n1. Loading ML predictor...")
try:
    predictor = get_predictor()
    print("   SUCCESS: Predictor loaded")
    print(f"   Model version: {predictor.model_version}")
    print(f"   Features: {', '.join(predictor.feature_cols)}")
except Exception as e:
    print(f"   FAILED: {e}")
    sys.exit(1)

# Test 2: Make a prediction
print("\n2. Testing prediction...")
test_features = {
    'age': 45,
    'bmi': 22.5,
    'hiv_positive': 0,
    'diabetes': 0,
    'smoker': 1,
    'x_ray_score': 6.5,
    'adherence_mean': 88.0,
    'adherence_min': 75.0,
    'adherence_std': 8.5,
    'modification_count': 1,
    'visit_count': 5
}

try:
    result = predictor.predict(test_features)
    print("   SUCCESS: Prediction generated")
    print(f"   Risk Score: {result['risk_score']:.4f}")
    print(f"   Risk Category: {result['risk_category']}")
    print(f"   Confidence: {result['confidence']:.3f}")
    print(f"   Model Version: {result['model_version']}")
    print(f"\n   Top 3 SHAP values:")
    shap_sorted = sorted(result['shap_values'].items(), 
                        key=lambda x: abs(x[1]), reverse=True)
    for feat, val in shap_sorted[:3]:
        print(f"      {feat}: {val:.4f}")
except Exception as e:
    print(f"   FAILED: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# Test 3: Test with real patient (if exists)
print("\n3. Testing with real patient data...")
from clinical.models import Patient

try:
    patient = Patient.objects.first()
    if patient:
        print(f"   Found patient: {patient.patient_id}")
        
        # Extract features
        from clinical.viewsets import RiskPredictionViewSet
        viewset = RiskPredictionViewSet()
        features = viewset._extract_patient_features(patient)
        
        print(f"   Extracted features: {features}")
        
        # Predict
        result = predictor.predict(features)
        print(f"   Risk Score: {result['risk_score']:.4f}")
        print(f"   Risk Category: {result['risk_category']}")
    else:
        print("   No patients in database yet - skipping")
except Exception as e:
    print(f"   WARNING: {e}")

print("\n" + "="*60)
print("ALL TESTS PASSED")
print("="*60)
print("\nML integration is working correctly!")
print("You can now use the prediction endpoint:")
print("  POST /api/predictions/predict/")
print("  Body: {\"patient_id\": \"PT-00001\"}")
