# TB Post-Treatment Lung Disease (PTLD) Risk Prediction System - Detailed Summary

## 🎯 Project Overview

This is a **Clinical Decision Support System (CDSS)** designed to help healthcare professionals predict the risk of Post-Treatment Lung Disease (PTLD) in tuberculosis (TB) patients. PTLD is a condition where patients develop lung complications after completing TB treatment. The system uses **Machine Learning** to analyze patient data and provide risk predictions with explainable AI (SHAP) visualizations.

---

## 🏥 Problem Statement

**Challenge**: After TB treatment, some patients develop Post-Treatment Lung Disease (PTLD), which can cause:
- Chronic lung damage
- Reduced lung function
- Long-term health complications
- Increased healthcare costs

**Solution**: This system helps clinicians:
- **Identify high-risk patients early** (during months 3-4 of treatment)
- **Make informed decisions** about treatment modifications
- **Allocate resources** more effectively
- **Improve patient outcomes** through early intervention

---

## 🔬 What the System Does

### 1. **Patient Data Management**
- Stores comprehensive TB patient records including:
  - Demographics (age, sex, race, location)
  - Clinical information (treatment type, chest X-ray, tuberculin test)
  - Comorbidities (HIV, diabetes, smoking, AIDS, alcoholism, mental disorders, drug addiction)
  - Laboratory results (bacilloscopy tests for months 1-6)
  - Treatment details (drugs prescribed, supervised treatment, treatment duration)
  - Treatment outcomes (cured, completed, failed, died, etc.)

### 2. **Risk Prediction (Core Functionality)**
- **Input**: Patient data collected during months 1-3 of TB treatment
- **Process**: Uses trained ML models (XGBoost, Random Forest, Logistic Regression) to analyze:
  - Patient age
  - Comorbidity count (HIV, diabetes, smoking, etc.)
  - Treatment adherence (estimated from outcomes)
  - Treatment modifications
  - Monitoring visit frequency
- **Output**: 
  - **Risk Score** (0-1): Probability of developing PTLD
  - **Risk Category**: Low (0-0.33), Medium (0.33-0.66), or High (0.66-1.0)
  - **Confidence Level**: How certain the prediction is
  - **SHAP Values**: Explains which factors contribute most to the risk

### 3. **Explainable AI (SHAP Visualizations)**
- **Force Plots**: Shows how each feature pushes the prediction toward higher or lower risk
- **Waterfall Plots**: Visual breakdown of feature contributions
- **Feature Importance Tables**: Lists which factors are most important
- **Why it matters**: Helps clinicians understand **why** a patient is high-risk, not just that they are

### 4. **Clinical Recommendations**
- Automatically generates actionable recommendations based on:
  - Risk category (low/medium/high)
  - Specific risk factors (e.g., low adherence, multiple comorbidities)
  - Patient characteristics
- Examples:
  - "Increase monitoring frequency to monthly"
  - "Consider nutritional support"
  - "Coordinate care with specialists for multiple comorbidities"
  - "Schedule follow-up chest X-ray in 2-3 months"

### 5. **Treatment Tracking**
- Records treatment regimens
- Tracks treatment modifications (drug changes, dosage adjustments)
- Monitors patient visits and adherence
- Tracks final treatment outcomes

### 6. **Dashboard & Analytics**
- Overview dashboard showing:
  - Total patient count
  - Risk distribution (low/medium/high)
  - Treatment outcome statistics
  - Recent predictions
- Patient list with search and filter capabilities
- Individual patient detail pages with:
  - Complete medical history
  - All risk predictions over time
  - SHAP visualizations
  - Treatment timeline

---

## 🛠️ Technical Architecture

### **Backend (Django REST Framework)**
- **Framework**: Django 4.2 with Django REST Framework
- **Database**: SQLite (development) / PostgreSQL (production)
- **API**: RESTful API with endpoints for:
  - Patient management (CRUD operations)
  - Risk prediction generation
  - Treatment regimen tracking
  - Monitoring visit records
  - Data export
- **Authentication**: Token-based authentication
- **Authorization**: Role-based access control:
  - **Clinicians**: Can create/edit patients and generate predictions
  - **Researchers**: Read-only access to data
  - **Admins**: Full access including user management
- **Audit Logging**: Tracks all user actions for compliance

### **Machine Learning**
- **Models**: 
  - XGBoost (primary, best performance)
  - Random Forest (ensemble)
  - Logistic Regression (baseline)
- **Features Used** (10 total):
  - Age
  - HIV status
  - Diabetes
  - Smoking status
  - Comorbidity count (total number of comorbidities)
  - Adherence mean (average treatment adherence)
  - Adherence minimum (lowest adherence recorded)
  - Adherence standard deviation (consistency)
  - Modification count (number of treatment changes)
  - Visit count (number of monitoring visits)
- **Explainability**: SHAP (SHapley Additive exPlanations) for model interpretability
- **Training**: Models trained on TB dataset with cross-validation

### **Frontend (Django Templates + Bootstrap)**
- **Framework**: Django templates with Bootstrap 5
- **Features**:
  - Responsive design (works on desktop, tablet, mobile)
  - Interactive dashboards
  - Patient management interface
  - SHAP visualization display
  - Search and filtering
  - Data export functionality

### **Deployment**
- **Docker**: Containerized application
- **Docker Compose**: Orchestrates backend and database services
- **Environment Configuration**: Secure environment variable management

---

## 📊 Data Flow

### **1. Data Input**
```
TB Dataset (CSV) → Load into Database → Patient Records
```

### **2. Prediction Generation**
```
Patient Data → Feature Extraction → ML Model → Risk Prediction → SHAP Visualization → Recommendations
```

### **3. User Workflow**
```
Clinician Logs In → Views Patient List → Selects Patient → Generates Prediction → 
Views Risk Score + SHAP Plots → Reviews Recommendations → Makes Clinical Decision
```

---

## 🔑 Key Features

### **1. Early Risk Detection**
- Predicts PTLD risk at months 3-4 of treatment (before completion)
- Allows for early intervention and treatment modifications

### **2. Explainable Predictions**
- Not just "high risk" but **why** the patient is high risk
- SHAP visualizations show feature contributions
- Helps build clinician trust in the system

### **3. Actionable Recommendations**
- Not just predictions, but specific actions to take
- Tailored to patient's specific risk factors
- Prioritized by urgency

### **4. Comprehensive Patient Records**
- Complete medical history in one place
- Treatment timeline visualization
- All predictions tracked over time

### **5. Role-Based Access**
- Different access levels for different user types
- Clinicians can modify data
- Researchers can analyze data
- Admins can manage users

### **6. Audit Trail**
- All actions logged for compliance
- Track who did what and when
- Important for healthcare regulations

---

## 📈 Use Cases

### **Use Case 1: Routine Patient Assessment**
1. Clinician logs into system
2. Views patient list
3. Selects a patient at month 3 of treatment
4. Generates risk prediction
5. Reviews risk score and SHAP explanation
6. Sees recommendations (e.g., "Increase monitoring frequency")
7. Makes informed decision about treatment plan

### **Use Case 2: High-Risk Patient Identification**
1. System identifies patient with high risk score (0.75)
2. SHAP shows main contributors: low adherence (60%) + HIV positive + 3 comorbidities
3. Recommendations suggest:
   - Intensive monitoring (every 2-4 weeks)
   - Nutritional support
   - Specialist coordination
4. Clinician adjusts treatment plan accordingly

### **Use Case 3: Research & Analysis**
1. Researcher logs in (read-only access)
2. Exports patient data for analysis
3. Analyzes risk patterns across patient population
4. Identifies trends (e.g., "Patients with diabetes have 30% higher risk")

---

## 🎓 Machine Learning Details

### **Model Training Process**
1. **Data Loading**: Reads `tb_dataset.csv` directly
2. **Feature Engineering**:
   - Maps column names to standard format
   - Calculates comorbidity count
   - Estimates adherence from treatment outcomes
   - Estimates modifications and visits from treatment duration
3. **Model Training**: Trains 3 models (XGBoost, RF, LR)
4. **Evaluation**: Uses AUROC (Area Under ROC Curve) metric
5. **Model Selection**: XGBoost selected as best performer
6. **SHAP Integration**: Creates explainer for model interpretability

### **Model Performance**
- **Target**: AUROC ≥ 0.75 (meets requirement)
- **Sensitivity**: High (correctly identifies high-risk patients)
- **Specificity**: High (correctly identifies low-risk patients)

### **Feature Importance**
Based on SHAP analysis, most important factors:
1. Treatment adherence (mean and minimum)
2. Comorbidity count
3. HIV status
4. Age
5. Treatment modifications

---

## 🔒 Security & Compliance

### **Data Security**
- Role-based access control
- Authentication required for all operations
- Audit logging for compliance
- No PHI (Protected Health Information) in code repository

### **User Roles**
- **Clinician**: Can create/edit patients, generate predictions
- **Researcher**: Read-only access to data
- **Admin**: Full system access including user management

---

## 📁 Project Structure

```
fyp/
├── backend/              # Django application
│   ├── accounts/        # User authentication
│   ├── clinical/        # Patient data models & views
│   ├── ml/              # ML model integration
│   └── templates/       # HTML templates
├── ml/                  # Machine Learning
│   ├── models/          # Trained ML models (.pkl files)
│   ├── notebooks/       # Training scripts
│   └── data/            # Datasets
├── docs/                # Documentation
├── scripts/             # Utility scripts
└── docker-compose.yml   # Docker configuration
```

---

## 🚀 Getting Started

### **Quick Start**
1. **Setup Environment**:
   ```bash
   # Copy environment file
   cp .env.example .env
   # Edit .env with your settings
   ```

2. **Start Services**:
   ```bash
   docker-compose up --build
   ```

3. **Access Application**:
   - Backend API: `http://localhost:8000`
   - Admin Panel: `http://localhost:8000/admin`
   - Web Interface: `http://localhost:8000`

### **Train Models**
```bash
cd ml/notebooks
python modeling.py
```

### **Load Data**
```bash
cd backend
python manage.py load_tb_dataset --file ../ml/data/synthetic/tb_dataset.csv
```

---

## 🎯 Business Value

### **For Healthcare Providers**
- **Early Intervention**: Identify high-risk patients before complications develop
- **Resource Allocation**: Focus intensive care on patients who need it most
- **Improved Outcomes**: Better patient care through data-driven decisions
- **Time Savings**: Automated risk assessment vs. manual evaluation

### **For Patients**
- **Better Care**: Early identification of complications
- **Personalized Treatment**: Recommendations based on individual risk factors
- **Transparency**: Understandable explanations of risk factors

### **For Healthcare Systems**
- **Cost Reduction**: Prevent expensive complications through early intervention
- **Compliance**: Audit trails for regulatory requirements
- **Research**: Data export for population health studies

---

## 🔮 Future Enhancements

Potential improvements:
- Integration with Electronic Health Records (EHR)
- Real-time monitoring alerts
- Mobile app for field clinicians
- Advanced analytics and reporting
- Multi-language support
- Integration with laboratory systems
- Telemedicine integration

---

## 📝 Summary

**In Simple Terms**: This system helps doctors predict which TB patients are at risk of developing lung problems after treatment. It uses machine learning to analyze patient data and provides:
- A risk score (low/medium/high)
- Visual explanations of why a patient is at risk
- Specific recommendations for what to do

**Key Innovation**: Not just prediction, but **explainable** prediction - doctors can see exactly which factors contribute to the risk, making it easier to trust and act on the predictions.

**Impact**: Helps healthcare providers make better decisions, improve patient outcomes, and allocate resources more effectively.

---

**Last Updated**: 2025-01-XX  
**Version**: 1.0  
**Status**: Production Ready

