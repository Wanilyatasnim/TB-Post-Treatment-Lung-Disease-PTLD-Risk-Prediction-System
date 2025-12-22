# TB PTLD Risk Prediction System - Testing Checklist

This document provides a comprehensive testing checklist to verify the project's completeness and functionality.

## 📋 Project Overview

**Project**: TB Post-Treatment Lung Disease (PTLD) Risk Prediction System  
**Stack**: Django REST API + ML Models (XGBoost/Random Forest/Logistic Regression) + Django Templates  
**Database**: SQLite (local) / PostgreSQL/Supabase (production)

---

## ✅ 1. Environment Setup & Configuration

### 1.1 Prerequisites
- [ ] Python 3.10+ installed
- [ ] Docker and Docker Compose installed
- [ ] Git repository cloned
- [ ] Virtual environment created (if not using Docker)

### 1.2 Configuration Files
- [ ] `.env` file created from `env.example`
- [ ] `DJANGO_SECRET_KEY` set
- [ ] `DJANGO_DEBUG` set appropriately
- [ ] `SUPABASE_URL` configured (if using Supabase)
- [ ] `SUPABASE_ANON_KEY` configured (if using Supabase)
- [ ] Database settings configured (SQLite or PostgreSQL)

### 1.3 Dependencies
- [ ] Backend dependencies installed (`pip install -r backend/requirements.txt`)
- [ ] ML dependencies installed (`pip install -r ml/requirements.txt`)
- [ ] All packages install without errors

---

## ✅ 2. Database Setup & Migrations

### 2.1 Database Initialization
- [ ] Database file created (`db.sqlite3` for SQLite)
- [ ] PostgreSQL container running (if using Docker)
- [ ] Database connection successful

### 2.2 Migrations
- [ ] Run `python manage.py makemigrations` (no pending migrations)
- [ ] Run `python manage.py migrate` (all migrations applied)
- [ ] Check migration status: `python manage.py showmigrations`
- [ ] Verify all apps migrated: `accounts`, `clinical`

### 2.3 Database Schema Verification
- [ ] `Patient` model tables exist
- [ ] `TreatmentRegimen` model tables exist
- [ ] `TreatmentModification` model tables exist
- [ ] `MonitoringVisit` model tables exist
- [ ] `RiskPrediction` model tables exist
- [ ] `AuditLog` model tables exist
- [ ] `User` model tables exist

---

## ✅ 3. User Management & Authentication

### 3.1 Superuser Creation
- [ ] Create superuser: `python manage.py createsuperuser`
- [ ] Login to Django admin with superuser
- [ ] Verify admin interface accessible at `/admin/`

### 3.2 User Roles
- [ ] Create clinician user (using `scripts/utils/create_user.py`)
- [ ] Create researcher user
- [ ] Create admin user
- [ ] Verify role-based permissions work

### 3.3 Authentication
- [ ] Login page accessible at `/accounts/login/`
- [ ] Successful login redirects to dashboard
- [ ] Failed login shows error message
- [ ] Logout functionality works
- [ ] Session persistence works
- [ ] API token authentication works (`/api/token-auth/`)

### 3.4 Authorization & Permissions
- [ ] Clinician can create/edit patients
- [ ] Researcher can only read patients (no create/edit)
- [ ] Unauthenticated users redirected to login
- [ ] API endpoints enforce permissions correctly

---

## ✅ 4. Data Loading & Management

### 4.1 Synthetic Data Generation
- [ ] Run `ml/synthetic_data_generator.py` to generate test data
- [ ] Verify CSV files generated in `ml/data/synthetic/`
- [ ] Check data files exist:
  - `patients.csv`
  - `treatment_regimens.csv`
  - `treatment_modifications.csv`
  - `monitoring_visits.csv`
  - `risk_predictions.csv`
  - `tb_dataset.csv`

### 4.2 Data Loading Commands
- [ ] Load TB dataset: `python manage.py load_tb_dataset --file ml/data/synthetic/tb_dataset.csv`
- [ ] Load synthetic data: `python manage.py seed_synthetic`
- [ ] Verify patients loaded into database
- [ ] Verify patient count matches expected

### 4.3 Data Verification Scripts
- [ ] Run `scripts/utils/verify_patient_count.py`
- [ ] Run `scripts/utils/verify_dataset_integration.py`
- [ ] Run `scripts/utils/verify_dashboard.py`
- [ ] All verification scripts pass

---

## ✅ 5. API Endpoints Testing

### 5.1 Health Check
- [ ] `GET /health/` returns `{"status": "ok"}`
- [ ] `GET /api/health/` returns `{"status": "ok"}`

### 5.2 Patient API (`/api/patients/`)
- [ ] `GET /api/patients/` - List all patients (requires auth)
- [ ] `GET /api/patients/{patient_id}/` - Get patient detail
- [ ] `POST /api/patients/` - Create new patient (clinician only)
- [ ] `PUT /api/patients/{patient_id}/` - Update patient (clinician only)
- [ ] `PATCH /api/patients/{patient_id}/` - Partial update
- [ ] `DELETE /api/patients/{patient_id}/` - Delete patient (admin only)
- [ ] Search/filter functionality works
- [ ] Pagination works

### 5.3 Treatment Regimen API (`/api/regimens/`)
- [ ] `GET /api/regimens/` - List regimens
- [ ] `GET /api/regimens/{id}/` - Get regimen detail
- [ ] `POST /api/regimens/` - Create regimen
- [ ] Update/delete operations work

### 5.4 Treatment Modification API (`/api/modifications/`)
- [ ] `GET /api/modifications/` - List modifications
- [ ] `GET /api/modifications/{visit_id}/` - Get modification detail
- [ ] `POST /api/modifications/` - Create modification
- [ ] Filter by patient works

### 5.5 Monitoring Visit API (`/api/visits/`)
- [ ] `GET /api/visits/` - List visits
- [ ] `GET /api/visits/{visit_id}/` - Get visit detail
- [ ] `POST /api/visits/` - Create visit
- [ ] Filter by patient works

### 5.6 Risk Prediction API (`/api/predictions/`)
- [ ] `GET /api/predictions/` - List predictions
- [ ] `GET /api/predictions/{prediction_id}/` - Get prediction detail
- [ ] `POST /api/predictions/predict/` - Generate new prediction
  - [ ] Prediction returns `risk_score`
  - [ ] Prediction returns `risk_category` (low/medium/high)
  - [ ] Prediction returns `recommendations`
  - [ ] Prediction returns `shap_values`
  - [ ] SHAP plots generated (force plot, waterfall plot)
  - [ ] Error handling for missing patient
  - [ ] Error handling for missing features

### 5.7 API Documentation
- [ ] Swagger UI accessible at `/api/docs/`
- [ ] API schema accessible at `/api/schema/`
- [ ] All endpoints documented
- [ ] Request/response examples shown

---

## ✅ 6. ML Model Integration

### 6.1 Model Files Verification
- [ ] Model files exist in `ml/models/`:
  - [ ] `xgboost_model.pkl`
  - [ ] `random_forest_model.pkl`
  - [ ] `logistic_regression_model.pkl`
  - [ ] `scaler.pkl`
  - [ ] `shap_explainer.pkl`
  - [ ] `model_metadata.json`
  - [ ] `model_card.md`

### 6.2 Model Loading
- [ ] Predictor loads successfully on Django startup
- [ ] No errors in logs when loading models
- [ ] Model version information accessible
- [ ] Feature list matches expected features

### 6.3 Prediction Functionality
- [ ] Predictor extracts patient features correctly
- [ ] Predictions return valid risk scores (0-1)
- [ ] Risk categories assigned correctly (low/medium/high)
- [ ] SHAP values calculated correctly
- [ ] Confidence scores calculated
- [ ] Handles missing features gracefully
- [ ] Handles edge cases (all zeros, all ones, etc.)

### 6.4 SHAP Visualization
- [ ] Force plots generated successfully
- [ ] Waterfall plots generated successfully
- [ ] Plots saved to `backend/media/shap_plots/`
- [ ] Plot URLs accessible via API
- [ ] Test script works: `python scripts/utils/test_shap_visualization.py`

### 6.5 Recommendation Engine
- [ ] Recommendations generated based on risk category
- [ ] Recommendations are relevant and actionable
- [ ] High-risk patients get appropriate recommendations
- [ ] Medium-risk patients get appropriate recommendations
- [ ] Low-risk patients get appropriate recommendations

---

## ✅ 7. Frontend/Web Interface Testing

### 7.1 Login Page
- [ ] Login page loads at `/accounts/login/`
- [ ] Form validation works
- [ ] Error messages display correctly
- [ ] Successful login redirects properly

### 7.2 Dashboard (`/`)
- [ ] Dashboard accessible after login
- [ ] Total patient count displayed
- [ ] Risk distribution chart displayed
- [ ] Recent predictions shown
- [ ] Navigation menu works

### 7.3 Patient List (`/patients/`)
- [ ] Patient list page loads
- [ ] All patients displayed
- [ ] Search functionality works
- [ ] Filtering works
- [ ] Pagination works (if many patients)
- [ ] Links to patient detail pages work

### 7.4 Patient Detail (`/patients/{patient_id}/`)
- [ ] Patient detail page loads
- [ ] All patient information displayed
- [ ] Treatment history shown
- [ ] Monitoring visits shown
- [ ] Risk predictions history shown
- [ ] SHAP visualizations displayed
- [ ] "Generate Prediction" button works
- [ ] Edit patient form works (if permitted)

### 7.5 Patient Form (`/patients/new/` or `/patients/{patient_id}/edit/`)
- [ ] Create patient form loads
- [ ] All required fields present
- [ ] Form validation works
- [ ] Submit creates/updates patient
- [ ] Success message displayed
- [ ] Redirects to patient detail after save

### 7.6 Static Files
- [ ] CSS files load correctly
- [ ] JavaScript files load correctly
- [ ] Bootstrap styling applied
- [ ] Images/icons display correctly
- [ ] Charts (Chart.js/Plotly) render correctly

---

## ✅ 8. Audit Logging

### 8.1 Audit Log Creation
- [ ] Patient creation logged
- [ ] Patient update logged
- [ ] Patient deletion logged
- [ ] Prediction generation logged
- [ ] User actions logged

### 8.2 Audit Log Access
- [ ] Audit logs accessible in admin
- [ ] Audit logs include user information
- [ ] Audit logs include timestamp
- [ ] Audit logs include action description
- [ ] Audit logs include object ID

---

## ✅ 9. Docker Deployment

### 9.1 Docker Compose
- [ ] `docker-compose.yml` file exists
- [ ] Services defined: `db`, `backend`
- [ ] Environment variables configured
- [ ] Volumes mounted correctly
- [ ] Ports exposed correctly

### 9.2 Docker Build
- [ ] `docker-compose build` succeeds
- [ ] No build errors
- [ ] All dependencies installed in container

### 9.3 Docker Run
- [ ] `docker-compose up` starts services
- [ ] Database container running
- [ ] Backend container running
- [ ] Backend accessible at `http://localhost:8000`
- [ ] Database accessible on port 5432
- [ ] Logs show no errors

### 9.4 Docker Functionality
- [ ] Migrations run automatically (or manually)
- [ ] Static files collected
- [ ] Media files accessible
- [ ] Database persists after container restart

---

## ✅ 10. Unit Tests

### 10.1 Run Django Tests
- [ ] Run `python manage.py test` - all tests pass
- [ ] Model tests pass (`backend/clinical/tests.py`)
- [ ] View tests pass
- [ ] API tests pass (`backend/clinical/tests_api.py`)
- [ ] Permission tests pass
- [ ] Audit log tests pass

### 10.2 Test Coverage
- [ ] Test coverage > 70% (if using coverage tool)
- [ ] Critical paths tested
- [ ] Edge cases tested
- [ ] Error handling tested

---

## ✅ 11. Integration Testing

### 11.1 End-to-End Workflows
- [ ] Complete patient creation workflow
  1. Login as clinician
  2. Create new patient
  3. Add treatment regimen
  4. Add monitoring visit
  5. Generate risk prediction
  6. View SHAP plots
  7. Review recommendations
- [ ] Patient update workflow
- [ ] Prediction history workflow
- [ ] Data export workflow (if implemented)

### 11.2 Data Flow
- [ ] Data flows correctly from CSV → Database → API → Frontend
- [ ] ML predictions integrate with patient data
- [ ] SHAP visualizations link to predictions
- [ ] Recommendations link to predictions

---

## ✅ 12. Performance & Security

### 12.1 Performance
- [ ] API response times < 500ms for list endpoints
- [ ] API response times < 1s for prediction endpoint
- [ ] Database queries optimized (check with Django Debug Toolbar)
- [ ] No N+1 query problems
- [ ] Static files served efficiently

### 12.2 Security
- [ ] CSRF protection enabled
- [ ] SQL injection protection (using ORM)
- [ ] XSS protection (template auto-escaping)
- [ ] Authentication required for protected endpoints
- [ ] Role-based access control enforced
- [ ] Sensitive data not exposed in logs
- [ ] Environment variables not committed to git

---

## ✅ 13. Documentation

### 13.1 Code Documentation
- [ ] README.md exists and is up-to-date
- [ ] API documentation available
- [ ] Code comments present for complex logic
- [ ] Docstrings present for functions/classes

### 13.2 Setup Documentation
- [ ] Installation instructions clear
- [ ] Configuration guide available
- [ ] Database setup guide available
- [ ] ML model setup guide available (`ml/ML_SETUP_GUIDE.md`)

### 13.3 User Documentation
- [ ] User guide available (if applicable)
- [ ] Feature documentation available
- [ ] Troubleshooting guide available

---

## ✅ 14. Data Validation & Quality

### 14.1 Input Validation
- [ ] Patient ID format validated
- [ ] Age range validated
- [ ] Required fields enforced
- [ ] Data type validation works
- [ ] Invalid data rejected with clear errors

### 14.2 Data Integrity
- [ ] Foreign key constraints work
- [ ] Unique constraints enforced
- [ ] Data relationships maintained
- [ ] No orphaned records

---

## ✅ 15. Error Handling

### 15.1 API Error Handling
- [ ] 400 errors for bad requests
- [ ] 401 errors for unauthorized
- [ ] 403 errors for forbidden
- [ ] 404 errors for not found
- [ ] 500 errors handled gracefully
- [ ] Error messages are user-friendly

### 15.2 Frontend Error Handling
- [ ] Form validation errors displayed
- [ ] Network errors handled
- [ ] 404 pages exist
- [ ] 500 error pages exist
- [ ] User-friendly error messages

---

## ✅ 16. Browser Compatibility

### 16.1 Modern Browsers
- [ ] Chrome/Edge (latest)
- [ ] Firefox (latest)
- [ ] Safari (latest)
- [ ] Mobile browsers (if applicable)

### 16.2 Responsive Design
- [ ] Desktop layout works
- [ ] Tablet layout works
- [ ] Mobile layout works
- [ ] Forms usable on mobile

---

## ✅ 17. ML Model Quality

### 17.1 Model Performance
- [ ] Model accuracy acceptable (> 70%)
- [ ] ROC-AUC score acceptable (> 0.75)
- [ ] Confusion matrix reviewed
- [ ] Model performance documented

### 17.2 Model Artifacts
- [ ] Model metadata file complete
- [ ] Model card document complete
- [ ] Feature importance documented
- [ ] Training data documented

---

## ✅ 18. Final Verification

### 18.1 Complete System Test
- [ ] Start fresh database
- [ ] Run all migrations
- [ ] Load test data
- [ ] Create test user
- [ ] Login and navigate all pages
- [ ] Create patient
- [ ] Generate prediction
- [ ] View all features
- [ ] Export data (if applicable)
- [ ] Logout

### 18.2 Production Readiness
- [ ] DEBUG = False in production settings
- [ ] Secret key not in code
- [ ] All environment variables set
- [ ] Static files collected
- [ ] Database backed up
- [ ] Logging configured
- [ ] Monitoring setup (if applicable)

---

## 📊 Testing Summary

After completing all tests, document:

- **Total Tests**: ___ / ___
- **Passed**: ___
- **Failed**: ___
- **Skipped**: ___
- **Critical Issues**: ___
- **Minor Issues**: ___

### Known Issues
[List any issues found during testing]

### Recommendations
[List recommendations for improvements]

---

## 🚀 Quick Test Commands

```bash
# Run all tests
cd backend
python manage.py test

# Run specific test file
python manage.py test clinical.tests
python manage.py test clinical.tests_api

# Check migrations
python manage.py showmigrations

# Verify patient count
python scripts/utils/verify_patient_count.py

# Test SHAP visualization
python scripts/utils/test_shap_visualization.py

# Test Supabase connection (if using)
python scripts/utils/test_supabase_connection.py

# Start Docker services
docker-compose up --build

# Check API health
curl http://localhost:8000/health/
```

---

## 📝 Notes

- Mark each item as complete when tested
- Document any issues found
- Update this checklist as new features are added
- Use this checklist for regression testing after changes

---

**Last Updated**: [Date]  
**Tested By**: [Name]  
**Version**: 1.0

