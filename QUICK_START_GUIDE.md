# Quick Start Guide - Running the Project

## ✅ Project is Now Running!

The Django development server has been started. Here's how to access it:

### 🌐 Access Points

1. **Main Web Interface**: 
   - URL: http://localhost:8000
   - Login required (use your superuser credentials)

2. **Admin Panel**: 
   - URL: http://localhost:8000/admin
   - Django admin interface for managing data

3. **API Endpoints**:
   - Health Check: http://localhost:8000/health/
   - API Docs: http://localhost:8000/api/docs/
   - API Schema: http://localhost:8000/api/schema/

4. **Dashboard**:
   - URL: http://localhost:8000/
   - Main dashboard after login

### 👤 Login Credentials

You already have a superuser account. If you need to create a new one or reset password:

```bash
cd backend
python manage.py createsuperuser
```

### 📊 Loading Test Data

To load the TB dataset:

```bash
cd backend
python manage.py load_tb_dataset --file ../ml/data/synthetic/tb_dataset.csv
```

### 🛑 Stopping the Server

Press `Ctrl+C` in the terminal where the server is running, or:

```bash
# Find and kill the process
taskkill /F /IM python.exe /FI "WINDOWTITLE eq *runserver*"
```

### 🔄 Restarting the Server

```bash
cd backend
python manage.py runserver
```

### 📝 Next Steps

1. **Login** to the system at http://localhost:8000/accounts/login/
2. **View Dashboard** to see overview statistics
3. **Load Patient Data** using the management command above
4. **Create/View Patients** from the patient list
5. **Generate Predictions** for patients to see risk scores and SHAP visualizations

### 🐳 Alternative: Using Docker

If you prefer to use Docker:

```bash
# Build and start services
docker-compose up --build

# This will start:
# - PostgreSQL database on port 5432
# - Django backend on port 8000
```

### ⚙️ Configuration

The project uses SQLite by default for local development. To switch to PostgreSQL:

1. Edit `backend/.env` file
2. Set `USE_SQLITE=False`
3. Configure PostgreSQL connection details
4. Restart the server

### 🔍 Troubleshooting

**Port 8000 already in use?**
```bash
# Use a different port
python manage.py runserver 8001
```

**Database errors?**
```bash
# Reset database (WARNING: deletes all data)
cd backend
rm db.sqlite3
python manage.py migrate
python manage.py createsuperuser
```

**ML models not loading?**
- Make sure models are trained: `cd ml/notebooks && python modeling.py`
- Check that model files exist in `ml/models/`

### 📚 More Information

- See `PROJECT_SUMMARY.md` for detailed project overview
- See `TESTING_CHECKLIST.md` for testing procedures
- See `README.md` for general project information

---

**Server Status**: ✅ Running on http://localhost:8000

