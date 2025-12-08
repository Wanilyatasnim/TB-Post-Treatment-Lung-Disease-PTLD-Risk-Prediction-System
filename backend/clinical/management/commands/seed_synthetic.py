import csv
import json
from datetime import datetime, date
from pathlib import Path

from django.core.management.base import BaseCommand

from clinical.models import MonitoringVisit, Patient, RiskPrediction, TreatmentModification, TreatmentRegimen


def _parse_date(value: str):
    if not value:
        return None
    try:
        return date.fromisoformat(value)
    except ValueError:
        return None


def _parse_datetime(value: str):
    if not value:
        return None
    try:
        return datetime.fromisoformat(value)
    except ValueError:
        return None


class Command(BaseCommand):
    help = "Seed database with synthetic CSVs (generated from ml/synthetic_data_generator.py)"

    def add_arguments(self, parser):
        parser.add_argument(
            "--path",
            type=str,
            default="ml/data/synthetic",
            help="Directory containing patients.csv, treatment_regimens.csv, treatment_modifications.csv, monitoring_visits.csv, risk_predictions.csv",
        )

    def handle(self, *args, **options):
        base = Path(options["path"])
        if not base.exists():
            self.stderr.write(self.style.ERROR(f"Path not found: {base}"))
            return

        self.stdout.write(f"Loading synthetic data from {base} ...")
        patients = self._load_patients(base / "patients.csv")
        regimens = self._load_regimens(base / "treatment_regimens.csv")
        modifications = self._load_modifications(base / "treatment_modifications.csv")
        visits = self._load_visits(base / "monitoring_visits.csv")
        predictions = self._load_predictions(base / "risk_predictions.csv")

        self.stdout.write(
            self.style.SUCCESS(
                f"Loaded {patients} patients, {regimens} regimens, {modifications} modifications, {visits} visits, {predictions} predictions"
            )
        )

    def _load_patients(self, file_path: Path) -> int:
        count = 0
        with file_path.open() as f:
            reader = csv.DictReader(f)
            for row in reader:
                Patient.objects.update_or_create(
                    patient_id=row["patient_id"],
                    defaults={
                        "sex": row.get("sex") or "M",
                        "age": int(row.get("age") or 0),
                        "bmi": float(row.get("bmi") or 0),
                        "hiv_positive": row.get("hiv_positive") in ("True", "true", "1", "yes"),
                        "diabetes": row.get("diabetes") in ("True", "true", "1", "yes"),
                        "smoker": row.get("smoker") in ("True", "true", "1", "yes"),
                        "x_ray_score": float(row.get("x_ray_score") or 0),
                        "district": row.get("district", ""),
                        "comorbidities": row.get("comorbidities", ""),
                        "baseline_date": _parse_date(row.get("baseline_date")),
                    },
                )
                count += 1
        return count

    def _load_regimens(self, file_path: Path) -> int:
        count = 0
        with file_path.open() as f:
            reader = csv.DictReader(f)
            for row in reader:
                patient = Patient.objects.get(patient_id=row["patient_id"])
                TreatmentRegimen.objects.update_or_create(
                    regimen_id=row["regimen_id"],
                    defaults={
                        "patient": patient,
                        "drugs": row.get("drugs", ""),
                        "start_date": _parse_date(row.get("start_date")),
                        "end_date": _parse_date(row.get("end_date")),
                        "outcome": row.get("outcome") or "",
                    },
                )
                count += 1
        return count

    def _load_modifications(self, file_path: Path) -> int:
        count = 0
        with file_path.open() as f:
            reader = csv.DictReader(f)
            for row in reader:
                regimen = TreatmentRegimen.objects.get(regimen_id=row["regimen_id"])
                patient = Patient.objects.get(patient_id=row["patient_id"])
                TreatmentModification.objects.update_or_create(
                    modification_id=row["modification_id"],
                    defaults={
                        "regimen": regimen,
                        "patient": patient,
                        "modified_drug": row.get("modified_drug", ""),
                        "reason": row.get("reason", ""),
                        "date": _parse_date(row.get("date")),
                        "new_dosage_mg": int(row.get("new_dosage_mg") or 0),
                    },
                )
                count += 1
        return count

    def _load_visits(self, file_path: Path) -> int:
        count = 0
        with file_path.open() as f:
            reader = csv.DictReader(f)
            for row in reader:
                patient = Patient.objects.get(patient_id=row["patient_id"])
                MonitoringVisit.objects.update_or_create(
                    visit_id=row["visit_id"],
                    defaults={
                        "patient": patient,
                        "date": _parse_date(row.get("date")),
                        "adverse_reactions": row.get("adverse_reactions", ""),
                        "adherence_pct": float(row.get("adherence_pct") or 0),
                        "smear_result": row.get("smear_result", ""),
                        "weight_kg": float(row.get("weight_kg") or 0),
                    },
                )
                count += 1
        return count

    def _load_predictions(self, file_path: Path) -> int:
        count = 0
        with file_path.open() as f:
            reader = csv.DictReader(f)
            for row in reader:
                patient = Patient.objects.get(patient_id=row["patient_id"])
                shap_payload = row.get("shap_values")
                shap_values = {}
                if shap_payload:
                    try:
                        shap_values = json.loads(shap_payload)
                    except json.JSONDecodeError:
                        shap_values = {}
                RiskPrediction.objects.update_or_create(
                    prediction_id=row["prediction_id"],
                    defaults={
                        "patient": patient,
                        "risk_score": float(row.get("risk_score") or 0),
                        "risk_category": row.get("risk_category", ""),
                        "model_version": row.get("model_version", ""),
                        "shap_values": shap_values,
                        "timestamp": _parse_datetime(row.get("timestamp")),
                        "confidence": float(row.get("confidence") or 0),
                    },
                )
                count += 1
        return count

