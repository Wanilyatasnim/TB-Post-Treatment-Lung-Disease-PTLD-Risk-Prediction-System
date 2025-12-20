# Project Structure

This document describes the organization of the TB PTLD Risk Prediction System project.

## Directory Structure

```
fyp/
├── backend/                 # Django backend application
│   ├── accounts/           # User authentication app
│   ├── app/                # Django project settings
│   ├── clinical/           # Main clinical data models and views
│   │   ├── management/
│   │   │   └── commands/   # Django management commands
│   │   ├── migrations/     # Database migrations
│   │   └── templatetags/   # Custom template tags
│   ├── ml/                 # ML model integration (predictor, SHAP, recommendations)
│   ├── templates/          # HTML templates
│   ├── static/             # Static files
│   ├── media/              # User uploads (SHAP plots)
│   └── manage.py           # Django management script
│
├── ml/                      # Machine Learning components
│   ├── data/
│   │   └── synthetic/      # Synthetic datasets and EDA outputs
│   ├── models/             # Trained ML models and artifacts
│   ├── notebooks/          # Jupyter notebooks for EDA and modeling
│   └── synthetic_data_generator.py  # Legacy data generator
│
├── docs/                    # Project documentation
│   ├── dataset/            # Dataset-related documentation
│   ├── project/            # Project status and planning docs
│   ├── setup/              # Setup and configuration guides
│   └── README.md           # Documentation index
│
├── scripts/                 # Utility scripts
│   ├── generate_tb_dataset.py  # Generate TB dataset CSV
│   └── utils/              # Utility scripts (user management, testing, verification)
│
├── frontend/                # Frontend application (if any)
├── infrastructure/          # Infrastructure configuration
├── docker-compose.yml       # Docker Compose configuration
└── README.md               # Main project README

```

## Key Directories

### `/backend`
Django backend application containing:
- **accounts/**: User authentication and authorization
- **clinical/**: Core clinical data models, views, forms, serializers
- **ml/**: ML model integration (prediction, SHAP visualization, recommendations)
- **templates/**: HTML templates for web interface
- **static/**: Static files (CSS, JS, images)
- **media/**: User-generated content (SHAP plots)

### `/ml`
Machine Learning components:
- **data/synthetic/**: Generated datasets and EDA visualizations
- **models/**: Trained models (.pkl files), metadata, and model cards
- **notebooks/**: Jupyter notebooks for exploratory analysis and model training

### `/docs`
Organized documentation:
- **dataset/**: Dataset structure, integration guides, feature documentation
- **project/**: Project status, phase reports, planning documents
- **setup/**: Setup guides, configuration, deployment documentation

### `/scripts`
Utility scripts:
- **generate_tb_dataset.py**: Generate synthetic TB dataset CSV
- **utils/**: Helper scripts for user management, testing, verification

## File Organization

### Documentation Files
All markdown documentation is organized in `/docs`:
- Dataset docs → `docs/dataset/`
- Project status/docs → `docs/project/`
- Setup guides → `docs/setup/`

### Scripts
- Data generation scripts → `scripts/`
- Utility scripts → `scripts/utils/`

### Data Files
- Dataset CSV → `ml/data/synthetic/tb_dataset.csv`
- EDA outputs → `ml/data/synthetic/*.png`
- ML models → `ml/models/*.pkl`

## Usage

### Load Dataset
```bash
cd backend
python manage.py load_tb_dataset --file ../ml/data/synthetic/tb_dataset.csv
```

### Generate Dataset
```bash
python scripts/generate_tb_dataset.py -n 50 -o ml/data/synthetic/tb_dataset.csv
```

### Run Development Server
```bash
cd backend
python manage.py runserver
```

