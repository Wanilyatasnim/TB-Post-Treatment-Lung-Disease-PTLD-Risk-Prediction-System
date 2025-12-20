# Scripts

This directory contains utility scripts for the project.

## Structure

- **`generate_tb_dataset.py`** - Script to generate TB dataset CSV file
- **`utils/`** - Utility scripts for database management, testing, and verification

## Usage

### Generate Dataset
```bash
python scripts/generate_tb_dataset.py -n 50 -o ml/data/synthetic/tb_dataset.csv
```

### Utility Scripts
Scripts in `utils/` directory are helper scripts for:
- User management (create_user.py, reset_password.py, check_admin.py)
- Verification (verify_login.py, verify_dashboard.py, verify_patient_count.py)
- Testing (test_supabase_connection.py, test_shap_visualization.py)

Most can be run directly with Python, but some require Django setup:
```bash
cd backend
python manage.py shell < ../scripts/utils/script_name.py
```

