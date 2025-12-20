import argparse
import json
import os
from datetime import datetime, timedelta
from pathlib import Path

import numpy as np
import pandas as pd
from faker import Faker


def risk_from_features(row: pd.Series, rng: np.random.Generator) -> float:
    """Simple heuristic risk score to mimic model output using new TB dataset features."""
    base = 0.15
    age_factor = (row["age"] - 18) / 82  # age 18-100 -> 0-1
    hiv_factor = 0.25 if row.get("hiv_positive", False) else 0.0
    smoker_factor = 0.1 if row.get("smoker", False) else 0.0
    diabetes_factor = 0.08 if row.get("diabetes", False) else 0.0
    aids_factor = 0.15 if row.get("aids_comorbidity", False) else 0.0
    comorbidity_count = row.get("comorbidity_count", 0) * 0.05
    # Bacilloscopy results at month 3 (positive = higher risk)
    bacilloscopy_m3_positive = 1 if row.get("bacilloscopy_month_3", "").lower() in ["positive", "pos", "+", "1"] else 0
    bacilloscopy_factor = bacilloscopy_m3_positive * 0.2
    adherence_penalty = (1 - row.get("adherence_mean", 0.9)) * 0.3
    noise = rng.normal(0, 0.03)
    score = base + age_factor * 0.2 + hiv_factor + smoker_factor + diabetes_factor + aids_factor + comorbidity_count + bacilloscopy_factor + adherence_penalty + noise
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
        hiv_positive = bool(rng.choice([0, 1], p=[0.9, 0.1]))
        diabetes = bool(rng.choice([0, 1], p=[0.82, 0.18]))
        smoker = bool(rng.choice([0, 1], p=[0.7, 0.3]))
        aids_comorbidity = bool(rng.choice([0, 1], p=[0.95, 0.05]))
        alcoholism_comorbidity = bool(rng.choice([0, 1], p=[0.85, 0.15]))
        mental_disorder_comorbidity = bool(rng.choice([0, 1], p=[0.88, 0.12]))
        drug_addiction_comorbidity = bool(rng.choice([0, 1], p=[0.92, 0.08]))
        
        race_options = ["Asian", "Black", "White", "Hispanic", "Other"]
        race = rng.choice(race_options)
        state_options = ["State A", "State B", "State C", "State D", "State E"]
        state = rng.choice(state_options)
        
        treatment_options = ["2RHZE/4RH", "2RHZES/4RH", "2RHZ/4RH", "6RHZE"]
        treatment = rng.choice(treatment_options)
        
        clinical_form_options = ["Pulmonary", "Extrapulmonary", "Both", ""]
        clinical_form = rng.choice(clinical_form_options)
        
        chest_xray_options = ["Normal", "Abnormal", "Cavitary", "Pleural Effusion", ""]
        chest_x_ray = rng.choice(chest_xray_options)
        
        tuberculin_options = ["Positive", "Negative", "Indeterminate", ""]
        tuberculin_test = rng.choice(tuberculin_options)
        
        bacilloscopy_options = ["Positive", "Negative", "Scanty", "1+", "2+", "3+"]
        
        notification_date = start_anchor + timedelta(days=int(rng.integers(0, 120)))
        treatment_days = int(rng.integers(160, 240))
        outcome = rng.choice(["cured", "completed", "failed", "lost", "died", "transferred"], p=[0.55, 0.2, 0.1, 0.1, 0.04, 0.01])

        patient_id = f"PT-{pid:05d}"
        regimen_id = f"RG-{pid:05d}"

        # Generate monthly bacilloscopy results
        bacilloscopy_sputum = rng.choice(bacilloscopy_options)
        bacilloscopy_sputum_2 = rng.choice(bacilloscopy_options)
        bacilloscopy_other = rng.choice(bacilloscopy_options + [""])
        
        # Monthly bacilloscopy (should show improvement over time)
        initial_pos = bacilloscopy_sputum.lower() in ["positive", "pos", "1+", "2+", "3+"]
        month1_pos_prob = 0.8 if initial_pos else 0.3
        if month1_pos_prob > 0.5:
            bacilloscopy_month_1 = rng.choice(["Positive", "2+", "3+"], p=[0.5, 0.3, 0.2])
        else:
            bacilloscopy_month_1 = rng.choice(bacilloscopy_options, p=[0.2, 0.7, 0.05, 0.03, 0.01, 0.01])
        
        month2_pos = "positive" in str(bacilloscopy_month_1).lower() or "+" in str(bacilloscopy_month_1)
        if month2_pos:
            bacilloscopy_month_2 = rng.choice(["Positive", "1+", "2+"], p=[0.4, 0.4, 0.2])
        else:
            bacilloscopy_month_2 = rng.choice(bacilloscopy_options, p=[0.1, 0.8, 0.05, 0.03, 0.01, 0.01])
        
        month3_pos = "positive" in str(bacilloscopy_month_2).lower() or "+" in str(bacilloscopy_month_2)
        if month3_pos:
            bacilloscopy_month_3 = rng.choice(["Positive", "1+", "Negative"], p=[0.15, 0.05, 0.8])
        else:
            bacilloscopy_month_3 = rng.choice(["Negative", "Scanty"], p=[0.92, 0.08])
        
        month4_pos = "positive" in str(bacilloscopy_month_3).lower() or "+" in str(bacilloscopy_month_3)
        if month4_pos:
            bacilloscopy_month_4 = rng.choice(["Positive", "Negative"], p=[0.1, 0.9])
        else:
            bacilloscopy_month_4 = "Negative"
        
        bacilloscopy_month_5 = rng.choice(["Negative", "Scanty", ""], p=[0.9, 0.08, 0.02])
        bacilloscopy_month_6 = rng.choice(["Negative", "Scanty", ""], p=[0.9, 0.08, 0.02])
        
        sputum_culture_options = ["Positive", "Negative", "Contaminated", ""]
        sputum_culture = rng.choice(sputum_culture_options)
        
        # Treatment drugs
        rifampicin = True  # Most patients get this
        isoniazid = True
        ethambutol = bool(rng.choice([0, 1], p=[0.15, 0.85]))
        streptomycin = bool(rng.choice([0, 1], p=[0.7, 0.3]))
        pyrazinamide = bool(rng.choice([0, 1], p=[0.2, 0.8]))
        ethionamide = bool(rng.choice([0, 1], p=[0.85, 0.15]))
        other_drugs = rng.choice(["", "Levofloxacin", "Moxifloxacin", "Cycloserine"])
        
        supervised_treatment = bool(rng.choice([0, 1], p=[0.3, 0.7]))
        occupational_disease = bool(rng.choice([0, 1], p=[0.95, 0.05]))
        other_comorbidity = rng.choice(["", "Hypertension", "Cardiac Disease", "Renal Disease"])

        patients.append(
            {
                "patient_id": patient_id,
                "notification_date": notification_date.date(),
                "sex": sex,
                "age": age,
                "race": race,
                "state": state,
                "treatment": treatment,
                "chest_x_ray": chest_x_ray,
                "tuberculin_test": tuberculin_test,
                "clinical_form": clinical_form,
                "hiv_positive": hiv_positive,
                "diabetes": diabetes,
                "smoker": smoker,
                "aids_comorbidity": aids_comorbidity,
                "alcoholism_comorbidity": alcoholism_comorbidity,
                "mental_disorder_comorbidity": mental_disorder_comorbidity,
                "drug_addiction_comorbidity": drug_addiction_comorbidity,
                "other_comorbidity": other_comorbidity,
                "bacilloscopy_sputum": bacilloscopy_sputum,
                "bacilloscopy_sputum_2": bacilloscopy_sputum_2,
                "bacilloscopy_other": bacilloscopy_other,
                "sputum_culture": sputum_culture,
                "bacilloscopy_month_1": bacilloscopy_month_1,
                "bacilloscopy_month_2": bacilloscopy_month_2,
                "bacilloscopy_month_3": bacilloscopy_month_3,
                "bacilloscopy_month_4": bacilloscopy_month_4,
                "bacilloscopy_month_5": bacilloscopy_month_5,
                "bacilloscopy_month_6": bacilloscopy_month_6,
                "rifampicin": rifampicin,
                "isoniazid": isoniazid,
                "ethambutol": ethambutol,
                "streptomycin": streptomycin,
                "pyrazinamide": pyrazinamide,
                "ethionamide": ethionamide,
                "other_drugs": other_drugs,
                "supervised_treatment": supervised_treatment,
                "occupational_disease": occupational_disease,
                "days_in_treatment": treatment_days,
                "outcome_status": outcome,
            }
        )

        start_date = notification_date + timedelta(days=int(rng.integers(0, 7)))  # Treatment starts within 7 days of notification
        end_date = start_date + timedelta(days=treatment_days)
        
        regimens.append(
            {
                "regimen_id": regimen_id,
                "patient_id": patient_id,
                "drugs": treatment,  # Use the same treatment type
                "start_date": start_date.date(),
                "end_date": end_date.date(),
                "outcome": outcome,
            }
        )

        # Modifications (0-3)
        mod_count = int(rng.integers(0, 4))
        for midx in range(mod_count):
            mod_date = start_date + timedelta(days=int(rng.integers(14, treatment_days - 10)))
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

        # Monitoring visits (monthly visits, aligned with bacilloscopy months)
        adherence_samples = []
        visit_dates = [
            start_date + timedelta(days=30),  # Month 1
            start_date + timedelta(days=60),  # Month 2
            start_date + timedelta(days=90),  # Month 3
            start_date + timedelta(days=120), # Month 4
            start_date + timedelta(days=150), # Month 5
            start_date + timedelta(days=180), # Month 6
        ]
        
        for vidx, visit_date in enumerate(visit_dates[:min(6, treatment_days // 30)]):
            if visit_date > start_date + timedelta(days=treatment_days):
                break
            adherence = float(np.clip(rng.normal(0.9, 0.1), 0.3, 1.0))
            adherence_samples.append(adherence)
            
            # Match smear result with bacilloscopy result for that month
            month_bacillo = [bacilloscopy_month_1, bacilloscopy_month_2, bacilloscopy_month_3, 
                           bacilloscopy_month_4, bacilloscopy_month_5, bacilloscopy_month_6][vidx]
            smear_result = "positive" if month_bacillo and "positive" in str(month_bacillo).lower() else "negative"
            
            visits.append(
                {
                    "visit_id": f"VS-{pid:05d}-{vidx+1}",
                    "patient_id": patient_id,
                    "date": visit_date.date(),
                    "adverse_reactions": rng.choice(["none", "nausea", "rash", "neuropathy", "hepatotoxicity"], p=[0.5, 0.2, 0.15, 0.1, 0.05]),
                    "adherence_pct": round(adherence * 100, 1),
                    "smear_result": smear_result,
                    "weight_kg": round(np.clip(rng.normal(60, 10), 40, 120), 1),
                }
            )

        adherence_mean = float(np.mean(adherence_samples)) if adherence_samples else 0.9
        comorbidity_count = sum([
            int(hiv_positive), int(diabetes), int(smoker), int(aids_comorbidity),
            int(alcoholism_comorbidity), int(mental_disorder_comorbidity), 
            int(drug_addiction_comorbidity), int(bool(other_comorbidity))
        ])
        
        risk_score = risk_from_features(
            pd.Series(
                {
                    "age": age,
                    "hiv_positive": hiv_positive,
                    "smoker": smoker,
                    "diabetes": diabetes,
                    "aids_comorbidity": aids_comorbidity,
                    "comorbidity_count": comorbidity_count,
                    "bacilloscopy_month_3": bacilloscopy_month_3,
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
            "aids_comorbidity": 0.10 if aids_comorbidity else -0.01,
            "comorbidity_count": round(comorbidity_count * 0.03, 3),
            "bacilloscopy_month_3": 0.15 if "positive" in str(bacilloscopy_month_3).lower() else -0.05,
            "adherence_mean": round((0.9 - adherence_mean), 3),
        }

        # Prediction timestamp should be at month 3-4 (prediction start point)
        prediction_date = start_date + timedelta(days=int(rng.integers(90, 120)))  # Month 3-4
        
        predictions.append(
            {
                "prediction_id": f"PR-{pid:05d}",
                "patient_id": patient_id,
                "risk_score": round(risk_score, 4),
                "risk_category": risk_category,
                "model_version": "v1.0.0-synth",
                "shap_values": json.dumps(shap_values),
                "timestamp": prediction_date.isoformat(),
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








