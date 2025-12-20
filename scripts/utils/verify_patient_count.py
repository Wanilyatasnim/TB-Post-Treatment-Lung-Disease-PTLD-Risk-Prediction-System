import os
import sys
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'app.settings')
sys.path.insert(0, 'backend')
django.setup()

from clinical.models import Patient

count = Patient.objects.count()
print(f"Total patients in database: {count}")

if count > 0:
    print("\nFirst 10 patient IDs:")
    for p in Patient.objects.all()[:10]:
        print(f"  {p.patient_id}")

