"""
Load TB dataset from single CSV file.
Maps CSV column names to Patient model fields.
"""

import csv
from datetime import date
from pathlib import Path

from django.core.management.base import BaseCommand

from clinical.models import Patient


def _parse_date(value: str):
    """Parse date string to date object."""
    if not value or value == '':
        return None
    try:
        return date.fromisoformat(str(value).strip())
    except (ValueError, AttributeError):
        return None


def _parse_boolean(value):
    """Parse boolean from various formats."""
    if value is None or value == '':
        return False
    value_str = str(value).strip()
    return value_str.lower() in ('true', '1', 'yes', 't')


class Command(BaseCommand):
    help = "Load TB dataset from single CSV file (tb_dataset.csv)"

    def add_arguments(self, parser):
        parser.add_argument(
            "--file",
            type=str,
            default="ml/data/synthetic/tb_dataset.csv",
            help="Path to tb_dataset.csv file",
        )

    def handle(self, *args, **options):
        file_path = Path(options["file"])
        if not file_path.exists():
            self.stderr.write(self.style.ERROR(f"File not found: {file_path}"))
            return

        self.stdout.write(f"Loading TB dataset from {file_path} ...")
        
        count = self._load_patients(file_path)
        
        self.stdout.write(
            self.style.SUCCESS(f"Loaded {count} patients from TB dataset")
        )

    def _load_patients(self, file_path: Path) -> int:
        """
        Load patients from CSV file.
        Maps CSV column names (with underscores and capitals) to model field names.
        """
        count = 0
        with file_path.open(encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for idx, row in enumerate(reader, start=1):
                # Generate patient_id if not present (format: PT-00001, PT-00002, etc.)
                patient_id = row.get('patient_id')
                if not patient_id:
                    patient_id = f"PT-{idx:05d}"
                
                # Map CSV column names to model field names
                # CSV has: Notification_Date, HIV, Smoking_Comorbidity, etc.
                # Model expects: notification_date, hiv_positive, smoker, etc.
                
                Patient.objects.update_or_create(
                    patient_id=patient_id,
                    defaults={
                        # Basic Demographics - map Notification_Date -> notification_date
                        "notification_date": _parse_date(row.get("Notification_Date")),
                        "sex": row.get("Sex", "M").strip()[:1].upper() or "M",
                        "age": int(row.get("Age") or 0),
                        "race": row.get("Race", "").strip(),
                        "state": row.get("State", "").strip(),
                        
                        # Baseline Clinical Information
                        "treatment": row.get("Treatment", "").strip(),
                        "chest_x_ray": row.get("Chest_X_Ray", "").strip(),
                        "tuberculin_test": row.get("Tuberculin_Test", "").strip(),
                        "clinical_form": row.get("Clinical_Form", "").strip(),
                        
                        # Comorbidities - map CSV names to model fields
                        "hiv_positive": _parse_boolean(row.get("HIV")),  # HIV -> hiv_positive
                        "diabetes": _parse_boolean(row.get("Diabetes_Comorbidity")),  # Diabetes_Comorbidity -> diabetes
                        "smoker": _parse_boolean(row.get("Smoking_Comorbidity")),  # Smoking_Comorbidity -> smoker
                        "aids_comorbidity": _parse_boolean(row.get("AIDS_Comorbidity")),
                        "alcoholism_comorbidity": _parse_boolean(row.get("Alcoholism_Comorbidity")),
                        "mental_disorder_comorbidity": _parse_boolean(row.get("Mental_Disorder_Comorbidity")),
                        "drug_addiction_comorbidity": _parse_boolean(row.get("Drug_Addiction_Comorbidity")),
                        "other_comorbidity": row.get("Other_Comorbidity", "").strip(),
                        
                        # Laboratory Tests - Initial
                        "bacilloscopy_sputum": row.get("Bacilloscopy_Sputum", "").strip(),
                        "bacilloscopy_sputum_2": row.get("Bacilloscopy_Sputum_2", "").strip(),
                        "bacilloscopy_other": row.get("Bacilloscopy_Other", "").strip(),
                        "sputum_culture": row.get("Sputum_Culture", "").strip(),
                        
                        # Monthly Bacilloscopy Results
                        "bacilloscopy_month_1": row.get("Bacilloscopy_Month_1", "").strip(),
                        "bacilloscopy_month_2": row.get("Bacilloscopy_Month_2", "").strip(),
                        "bacilloscopy_month_3": row.get("Bacilloscopy_Month_3", "").strip(),
                        "bacilloscopy_month_4": row.get("Bacilloscopy_Month_4", "").strip(),
                        "bacilloscopy_month_5": row.get("Bacilloscopy_Month_5", "").strip(),
                        "bacilloscopy_month_6": row.get("Bacilloscopy_Month_6", "").strip(),
                        
                        # Treatment Drugs
                        "rifampicin": _parse_boolean(row.get("Rifampicin")),
                        "isoniazid": _parse_boolean(row.get("Isoniazid")),
                        "ethambutol": _parse_boolean(row.get("Ethambutol")),
                        "streptomycin": _parse_boolean(row.get("Streptomycin")),
                        "pyrazinamide": _parse_boolean(row.get("Pyrazinamide")),
                        "ethionamide": _parse_boolean(row.get("Ethionamide")),
                        "other_drugs": row.get("Other_Drugs", "").strip(),
                        
                        # Treatment Characteristics
                        "supervised_treatment": _parse_boolean(row.get("Supervised_Treatment")),
                        "occupational_disease": _parse_boolean(row.get("Occupational_Disease")),
                        "days_in_treatment": int(row.get("Days_In_Treatment") or 0) if row.get("Days_In_Treatment") else None,
                        
                        # Outcome
                        "outcome_status": row.get("Outcome_Status", "").strip(),
                    },
                )
                count += 1
        return count

