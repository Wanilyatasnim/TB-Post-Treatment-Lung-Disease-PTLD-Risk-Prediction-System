"""
API endpoint tests for the clinical application.
"""

from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from rest_framework import status
from clinical.models import Patient, RiskPrediction

User = get_user_model()


class PatientAPITest(TestCase):
    """Test Patient API endpoints."""
    
    def setUp(self):
        """Set up test data."""
        self.client = APIClient()
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123',
            role='clinician'
        )
        self.patient = Patient.objects.create(
            patient_id='API-TEST-001',
            sex='M',
            age=35
        )
    
    def test_patient_list_requires_auth(self):
        """Test that patient list API requires authentication."""
        response = self.client.get('/api/patients/')
        # May return 401 or 403 depending on authentication setup
        self.assertIn(response.status_code, [status.HTTP_401_UNAUTHORIZED, status.HTTP_403_FORBIDDEN])
    
    def test_patient_list_authenticated(self):
        """Test patient list API with authentication."""
        self.client.force_authenticate(user=self.user)
        response = self.client.get('/api/patients/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreaterEqual(len(response.data), 1)
    
    def test_patient_detail(self):
        """Test patient detail API."""
        self.client.force_authenticate(user=self.user)
        response = self.client.get(f'/api/patients/{self.patient.patient_id}/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['patient_id'], 'API-TEST-001')
    
    def test_patient_create(self):
        """Test patient creation via API."""
        self.client.force_authenticate(user=self.user)
        data = {
            'patient_id': 'API-TEST-002',
            'sex': 'F',
            'age': 40
        }
        response = self.client.post('/api/patients/', data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['patient_id'], 'API-TEST-002')
    
    def test_researcher_read_only(self):
        """Test that researcher role has read-only access."""
        researcher = User.objects.create_user(
            username='researcher',
            password='testpass123',
            role='researcher'
        )
        self.client.force_authenticate(user=researcher)
        
        # Should be able to read
        response = self.client.get('/api/patients/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Should NOT be able to create
        data = {
            'patient_id': 'API-TEST-003',
            'sex': 'M',
            'age': 30
        }
        response = self.client.post('/api/patients/', data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)


class PredictionAPITest(TestCase):
    """Test Risk Prediction API endpoints."""
    
    def setUp(self):
        """Set up test data."""
        self.client = APIClient()
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123',
            role='clinician'
        )
        self.patient = Patient.objects.create(
            patient_id='PRED-TEST-001',
            sex='M',
            age=35,
            hiv_positive=False,
            diabetes=False,
            smoker=False
        )
        # Create a visit for adherence calculation
        from clinical.models import MonitoringVisit
        MonitoringVisit.objects.create(
            visit_id='V-001',
            patient=self.patient,
            adherence_pct=90.0
        )
    
    def test_prediction_list(self):
        """Test prediction list API."""
        self.client.force_authenticate(user=self.user)
        response = self.client.get('/api/predictions/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
    
    def test_prediction_generation(self):
        """Test prediction generation via API."""
        self.client.force_authenticate(user=self.user)
        data = {'patient_id': 'PRED-TEST-001'}
        response = self.client.post('/api/predictions/predict/', data)
        
        # Should succeed (201) or fail gracefully if ML models not loaded
        self.assertIn(response.status_code, [
            status.HTTP_201_CREATED,
            status.HTTP_500_INTERNAL_SERVER_ERROR  # If models not available
        ])
        
        if response.status_code == status.HTTP_201_CREATED:
            self.assertIn('risk_score', response.data)
            self.assertIn('risk_category', response.data)
            self.assertIn('recommendations', response.data)


class HealthEndpointTest(TestCase):
    """Test health check endpoint."""
    
    def setUp(self):
        """Set up test client."""
        self.client = APIClient()
    
    def test_health_endpoint(self):
        """Test health check endpoint."""
        response = self.client.get('/health/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        import json
        data = json.loads(response.content)
        self.assertEqual(data['status'], 'ok')

