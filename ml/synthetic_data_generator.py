import argparse
import json
import os
from datetime import datetime, timedelta
from pathlib import Path

import numpy as np
import pandas as pd
from faker import Faker


def risk_from_features(row: pd.Series, rng: np.random.Generator) -> float:
    """Simple heuristic risk score to mimic model output."""
    base = 0.15
    age_factor = (row["age"] - 18) / 82  # age 18-100 -> 0-1
    hiv_factor = 0.25 if row["hiv_positive"] else 0.0
    smoker_factor = 0.1 if row["smoker"] else 0.0
    diabetes_factor = 0.08 if row["diabetes"] else 0.0
    xray_factor = row["x_ray_score"] / 20 * 0.25
    adherence_penalty = (1 - row["adherence_mean"]) * 0.3
    noise = rng.normal(0, 0.03)
    score = base + age_factor * 0.2 + hiv_factor + smoker_factor + diabetes_factor + xray_factor + adherence_penalty + noise
    return float(np.clip(score, 0, 1))


def generate_synthetic_data(output_dir: Path, n_patients: int, seed: int) -> None:
    rng = np.random.default_rng(seed)
    fake = Faker()
    Faker.seed(seed)

    patients = []
    regimens = []
    modifications = []
    visits = []
    predictions = []

    start_anchor = datetime(2023, 1, 1)

    for pid in range(1, n_patients + 1):
        sex = rng.choice(["M", "F"])
        age = int(rng.integers(18, 85))
        bmi = round(rng.normal(22, 3), 1)
        hiv_positive = bool(rng.choice([0, 1], p=[0.9, 0.1]))
        diabetes = bool(rng.choice([0, 1], p=[0.82, 0.18]))
        smoker = bool(rng.choice([0, 1], p=[0.7, 0.3]))
        xray = float(np.clip(rng.normal(6, 3), 0, 20))
        district = fake.city()
        comorbidities = ";".join([c for c, flag in [("HIV", hiv_positive), ("DM", diabetes), ("Smoker", smoker)] if flag]) or "None"

        patient_id = f"PT-{pid:05d}"
        regimen_id = f"RG-{pid:05d}"

        baseline_date = start_anchor + timedelta(days=int(rng.integers(0, 120)))
        treatment_days = int(rng.integers(160, 240))
        end_date = baseline_date + timedelta(days=treatment_days)
        outcome = rng.choice(["cured", "completed", "failed", "lost", "died"], p=[0.55, 0.2, 0.1, 0.1, 0.05])

        patients.append(
            {
                "patient_id": patient_id,
                "sex": sex,
                "age": age,
                "bmi": bmi,
                "hiv_positive": hiv_positive,
                "diabetes": diabetes,
                "smoker": smoker,
                "x_ray_score": round(xray, 2),
                "district": district,
                "comorbidities": comorbidities,
                "baseline_date": baseline_date.date(),
            }
        )

        regimens.append(
            {
                "regimen_id": regimen_id,
                "patient_id": patient_id,
                "drugs": "2RHZE/4RH",
                "start_date": baseline_date.date(),
                "end_date": end_date.date(),
                "outcome": outcome,
            }
        )

        # Modifications (0-3)
        mod_count = int(rng.integers(0, 4))
        for midx in range(mod_count):
            mod_date = baseline_date + timedelta(days=int(rng.integers(14, treatment_days - 10)))
            modifications.append(
                {
                    "modification_id": f"MD-{pid:05d}-{midx+1}",
                    "regimen_id": regimen_id,
                    "patient_id": patient_id,
                    "modified_drug": rng.choice(["R", "H", "Z", "E"]),
                    "reason": rng.choice(["toxicity", "non_adherence", "stockout", "clinical_failure"]),
                    "date": mod_date.date(),
                    "new_dosage_mg": int(rng.integers(150, 600)),
                }
            )

        # Monitoring visits (3-6)
        visit_count = int(rng.integers(3, 7))
        adherence_samples = []
        for vidx in range(visit_count):
            visit_date = baseline_date + timedelta(days=int(rng.integers(0, treatment_days)))
            adherence = float(np.clip(rng.normal(0.9, 0.1), 0.3, 1.0))
            adherence_samples.append(adherence)
            visits.append(
                {
                    "visit_id": f"VS-{pid:05d}-{vidx+1}",
                    "patient_id": patient_id,
                    "date": visit_date.date(),
                    "adverse_reactions": rng.choice(["none", "nausea", "rash", "neuropathy", "hepatotoxicity"], p=[0.5, 0.2, 0.15, 0.1, 0.05]),
                    "adherence_pct": round(adherence * 100, 1),
                    "smear_result": rng.choice(["positive", "negative"], p=[0.25, 0.75]),
                    "weight_kg": round(np.clip(rng.normal(60, 10), 40, 120), 1),
                }
            )

        adherence_mean = float(np.mean(adherence_samples)) if adherence_samples else 0.9
        risk_score = risk_from_features(
            pd.Series(
                {
                    "age": age,
                    "hiv_positive": hiv_positive,
                    "smoker": smoker,
                    "diabetes": diabetes,
                    "x_ray_score": xray,
                    "adherence_mean": adherence_mean,
                }
            ),
            rng,
        )
        risk_category = "low" if risk_score < 0.33 else "medium" if risk_score < 0.66 else "high"
        shap_values = {
            "age": round((age - 50) / 100, 3),
            "hiv_positive": 0.12 if hiv_positive else -0.02,
            "smoker": 0.05 if smoker else -0.01,
            "diabetes": 0.04 if diabetes else -0.01,
            "x_ray_score": round((xray - 6) / 24, 3),
            "adherence_mean": round((0.9 - adherence_mean), 3),
        }

        predictions.append(
            {
                "prediction_id": f"PR-{pid:05d}",
                "patient_id": patient_id,
                "risk_score": round(risk_score, 4),
                "risk_category": risk_category,
                "model_version": "v0.1.0-synth",
                "shap_values": json.dumps(shap_values),
                "timestamp": (baseline_date + timedelta(days=int(rng.integers(30, treatment_days)))).isoformat(),
                "confidence": round(float(rng.uniform(0.6, 0.95)), 3),
            }
        )

    output_dir.mkdir(parents=True, exist_ok=True)
    pd.DataFrame(patients).to_csv(output_dir / "patients.csv", index=False)
    pd.DataFrame(regimens).to_csv(output_dir / "treatment_regimens.csv", index=False)
    pd.DataFrame(modifications).to_csv(output_dir / "treatment_modifications.csv", index=False)
    pd.DataFrame(visits).to_csv(output_dir / "monitoring_visits.csv", index=False)
    pd.DataFrame(predictions).to_csv(output_dir / "risk_predictions.csv", index=False)

    print(f"Wrote synthetic data for {n_patients} patients to {output_dir}")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Generate synthetic TB PTLD dataset.")
    parser.add_argument("-n", "--num-patients", type=int, default=1000, help="Number of patients to generate")
    parser.add_argument("-o", "--output-dir", type=Path, default=Path("ml/data/synthetic"), help="Output directory for CSVs")
    parser.add_argument("-s", "--seed", type=int, default=42, help="Random seed")
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()
    generate_synthetic_data(args.output_dir, args.num_patients, args.seed)




