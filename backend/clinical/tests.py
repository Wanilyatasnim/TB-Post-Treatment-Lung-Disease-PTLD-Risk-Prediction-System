"""
Tests for the clinical application.
"""

from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from django.urls import reverse
from clinical.models import Patient, RiskPrediction, TreatmentRegimen, MonitoringVisit, AuditLog
from clinical.audit import log_action

User = get_user_model()


class PatientModelTest(TestCase):
    """Test Patient model."""
    
    def setUp(self):
        """Set up test data."""
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123',
            role='clinician'
        )
        self.patient = Patient.objects.create(
            patient_id='TEST-001',
            sex='M',
            age=35,
            bmi=22.5,
            hiv_positive=False,
            diabetes=False,
            smoker=False,
            x_ray_score=5.0,
            district='Test District',
            created_by=self.user
        )
    
    def test_patient_creation(self):
        """Test patient creation."""
        self.assertEqual(self.patient.patient_id, 'TEST-001')
        self.assertEqual(self.patient.age, 35)
        self.assertEqual(self.patient.sex, 'M')
        self.assertFalse(self.patient.hiv_positive)
    
    def test_patient_str(self):
        """Test patient string representation."""
        self.assertEqual(str(self.patient), 'TEST-001 (35y M)')
    
    def test_patient_has_created_by(self):
        """Test patient has created_by field."""
        self.assertEqual(self.patient.created_by, self.user)


class RiskPredictionTest(TestCase):
    """Test RiskPrediction model."""
    
    def setUp(self):
        """Set up test data."""
        self.patient = Patient.objects.create(
            patient_id='TEST-002',
            sex='F',
            age=45,
            bmi=25.0
        )
        self.prediction = RiskPrediction.objects.create(
            prediction_id='PR-TEST-002-001',
            patient=self.patient,
            risk_score=0.75,
            risk_category='high',
            model_version='v1.0.0',
            confidence=0.85
        )
    
    def test_prediction_creation(self):
        """Test prediction creation."""
        self.assertEqual(self.prediction.prediction_id, 'PR-TEST-002-001')
        self.assertEqual(self.prediction.risk_score, 0.75)
        self.assertEqual(self.prediction.risk_category, 'high')
        self.assertEqual(self.prediction.patient, self.patient)
    
    def test_prediction_str(self):
        """Test prediction string representation."""
        self.assertEqual(str(self.prediction), 'PR-TEST-002-001 (high)')


class AuditLogTest(TestCase):
    """Test AuditLog model."""
    
    def setUp(self):
        """Set up test data."""
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123',
            role='clinician'
        )
    
    def test_audit_log_creation(self):
        """Test audit log creation."""
        log_action(
            user=self.user,
            action='create',
            model_name='Patient',
            object_id='TEST-003',
            description='Test audit log',
            request=None
        )
        
        log = AuditLog.objects.first()
        self.assertIsNotNone(log)
        self.assertEqual(log.user, self.user)
        self.assertEqual(log.action, 'create')
        self.assertEqual(log.model_name, 'Patient')
        self.assertEqual(log.object_id, 'TEST-003')


class PatientListViewTest(TestCase):
    """Test PatientListView."""
    
    def setUp(self):
        """Set up test data."""
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123',
            role='clinician'
        )
        self.patient = Patient.objects.create(
            patient_id='TEST-004',
            sex='M',
            age=30
        )
    
    def test_patient_list_requires_login(self):
        """Test that patient list requires login."""
        response = self.client.get(reverse('patients:patient-list'))
        self.assertEqual(response.status_code, 302)  # Redirect to login
    
    def test_patient_list_authenticated(self):
        """Test patient list for authenticated user."""
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(reverse('patients:patient-list'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'TEST-004')
    
    def test_patient_list_search(self):
        """Test patient list search functionality."""
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(reverse('patients:patient-list'), {'search': 'TEST-004'})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'TEST-004')


class PatientDetailViewTest(TestCase):
    """Test PatientDetailView."""
    
    def setUp(self):
        """Set up test data."""
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123',
            role='clinician'
        )
        self.patient = Patient.objects.create(
            patient_id='TEST-005',
            sex='F',
            age=40,
            bmi=23.0
        )
    
    def test_patient_detail_requires_login(self):
        """Test that patient detail requires login."""
        response = self.client.get(reverse('patients:patient-detail', args=['TEST-005']))
        self.assertEqual(response.status_code, 302)  # Redirect to login
    
    def test_patient_detail_authenticated(self):
        """Test patient detail for authenticated user."""
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(reverse('patients:patient-detail', args=['TEST-005']))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'TEST-005')
        self.assertContains(response, '40')


class DashboardViewTest(TestCase):
    """Test DashboardView."""
    
    def setUp(self):
        """Set up test data."""
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123',
            role='clinician'
        )
        # Create some test data
        Patient.objects.create(patient_id='TEST-006', sex='M', age=35)
        Patient.objects.create(patient_id='TEST-007', sex='F', age=45)
    
    def test_dashboard_requires_login(self):
        """Test that dashboard requires login."""
        response = self.client.get(reverse('patients:dashboard'))
        self.assertEqual(response.status_code, 302)  # Redirect to login
    
    def test_dashboard_authenticated(self):
        """Test dashboard for authenticated user."""
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(reverse('patients:dashboard'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Dashboard')
        self.assertContains(response, 'Total Patients')


class LoginViewTest(TestCase):
    """Test login functionality."""
    
    def setUp(self):
        """Set up test data."""
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123',
            role='clinician'
        )
    
    def test_login_page_loads(self):
        """Test that login page loads."""
        response = self.client.get(reverse('accounts:login'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Sign in')
    
    def test_login_success(self):
        """Test successful login."""
        response = self.client.post(
            reverse('accounts:login'),
            {'username': 'testuser', 'password': 'testpass123'}
        )
        self.assertEqual(response.status_code, 302)  # Redirect after login
        self.assertTrue(response.wsgi_request.user.is_authenticated)
    
    def test_login_failure(self):
        """Test failed login."""
        response = self.client.post(
            reverse('accounts:login'),
            {'username': 'testuser', 'password': 'wrongpass'}
        )
        self.assertEqual(response.status_code, 200)  # Stay on login page
        self.assertContains(response, 'Invalid username or password')


class LogoutViewTest(TestCase):
    """Test logout functionality."""
    
    def setUp(self):
        """Set up test data."""
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123',
            role='clinician'
        )
        self.client.login(username='testuser', password='testpass123')
    
    def test_logout(self):
        """Test logout."""
        response = self.client.get(reverse('accounts:logout'))
        self.assertEqual(response.status_code, 302)  # Redirect to login
        # User should be logged out
        response = self.client.get(reverse('patients:patient-list'))
        self.assertEqual(response.status_code, 302)  # Should redirect to login


