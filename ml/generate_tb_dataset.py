"""
Generate single TB dataset CSV with exact features specified.
Generates 50 rows only.
"""

import argparse
import json
import os
from datetime import datetime, timedelta
from pathlib import Path

import numpy as np
import pandas as pd
from faker import Faker


def generate_tb_dataset(output_file, n_rows=50, seed=42):
    """
    Generate single TB dataset CSV with exact feature names.
    
    Args:
        output_file: Path to output CSV file
        n_rows: Number of rows to generate (default: 50)
        seed: Random seed for reproducibility
    """
    rng = np.random.default_rng(seed)
    fake = Faker()
    Faker.seed(seed)
    
    # Feature names exactly as specified
    features = [
        'Notification_Date', 'Sex', 'Race', 'Treatment', 'Chest_X_Ray', 
        'Tuberculin_Test', 'Clinical_Form', 'AIDS_Comorbidity', 
        'Alcoholism_Comorbidity', 'Diabetes_Comorbidity', 
        'Mental_Disorder_Comorbidity', 'Other_Comorbidity', 
        'Bacilloscopy_Sputum', 'Bacilloscopy_Sputum_2', 'Bacilloscopy_Other', 
        'Sputum_Culture', 'HIV', 'Rifampicin', 'Isoniazid', 'Ethambutol', 
        'Streptomycin', 'Pyrazinamide', 'Ethionamide', 'Other_Drugs', 
        'Supervised_Treatment', 'Occupational_Disease', 'Bacilloscopy_Month_1', 
        'Bacilloscopy_Month_2', 'Bacilloscopy_Month_3', 'Bacilloscopy_Month_4', 
        'Bacilloscopy_Month_5', 'Bacilloscopy_Month_6', 'Outcome_Status', 
        'Drug_Addiction_Comorbidity', 'Smoking_Comorbidity', 'State', 
        'Days_In_Treatment', 'Age'
    ]
    
    data = []
    
    for i in range(n_rows):
        # Notification Date
        notification_date = fake.date_between(start_date='-2y', end_date='today')
        
        # Sex
        sex = rng.choice(['M', 'F'])
        
        # Race
        race = rng.choice(['White', 'Asian', 'Black', 'Hispanic', 'Other', ''])
        
        # Treatment
        treatment = rng.choice(['6RHZE', '2RHZ/4RH', '2RHZE/4RH', 'Other', ''])
        
        # Chest X-Ray
        chest_x_ray = rng.choice(['Normal', 'Cavitary', 'Infiltrate', 'Pleural Effusion', ''])
        
        # Tuberculin Test
        tuberculin_test = rng.choice(['Positive', 'Negative', ''])
        
        # Clinical Form
        clinical_form = rng.choice(['Pulmonary', 'Extrapulmonary', 'Both', ''])
        
        # Comorbidities (Boolean fields)
        aids_comorbidity = bool(rng.choice([0, 1], p=[0.95, 0.05]))
        alcoholism_comorbidity = bool(rng.choice([0, 1], p=[0.9, 0.1]))
        diabetes_comorbidity = bool(rng.choice([0, 1], p=[0.85, 0.15]))
        mental_disorder_comorbidity = bool(rng.choice([0, 1], p=[0.92, 0.08]))
        drug_addiction_comorbidity = bool(rng.choice([0, 1], p=[0.93, 0.07]))
        smoking_comorbidity = bool(rng.choice([0, 1], p=[0.7, 0.3]))
        other_comorbidity = rng.choice(['', 'Hypertension', 'Cardiac Disease', 'Renal Disease'])
        
        # Laboratory Tests
        bacilloscopy_sputum = rng.choice(['Positive', 'Negative', '1+', '2+', '3+', 'Scanty', ''])
        bacilloscopy_sputum_2 = rng.choice(['Positive', 'Negative', '1+', '2+', '3+', 'Scanty', ''])
        bacilloscopy_other = rng.choice(['Positive', 'Negative', '1+', '2+', '3+', 'Scanty', ''])
        sputum_culture = rng.choice(['Positive', 'Negative', 'Contaminated', ''])
        
        # HIV (maps to hiv_positive in model)
        hiv = bool(rng.choice([0, 1], p=[0.9, 0.1]))
        
        # Treatment Drugs (Boolean)
        rifampicin = bool(rng.choice([0, 1], p=[0.1, 0.9]))  # Most get this
        isoniazid = bool(rng.choice([0, 1], p=[0.1, 0.9]))  # Most get this
        ethambutol = bool(rng.choice([0, 1], p=[0.15, 0.85]))
        streptomycin = bool(rng.choice([0, 1], p=[0.7, 0.3]))
        pyrazinamide = bool(rng.choice([0, 1], p=[0.2, 0.8]))
        ethionamide = bool(rng.choice([0, 1], p=[0.85, 0.15]))
        other_drugs = rng.choice(['', 'Levofloxacin', 'Moxifloxacin', 'Cycloserine'])
        
        # Treatment Characteristics
        supervised_treatment = bool(rng.choice([0, 1], p=[0.3, 0.7]))
        occupational_disease = bool(rng.choice([0, 1], p=[0.95, 0.05]))
        
        # Monthly Bacilloscopy Results
        # Month 1
        month1_pos = rng.choice([True, False], p=[0.3, 0.7])
        if month1_pos:
            bacilloscopy_month_1 = rng.choice(['Positive', '1+', '2+', '3+'])
        else:
            bacilloscopy_month_1 = rng.choice(['Negative', 'Scanty', ''])
        
        # Month 2
        month2_pos = "positive" in str(bacilloscopy_month_1).lower() or "+" in str(bacilloscopy_month_1)
        if month2_pos:
            bacilloscopy_month_2 = rng.choice(['Positive', '1+', 'Negative'], p=[0.2, 0.1, 0.7])
        else:
            bacilloscopy_month_2 = rng.choice(['Negative', 'Scanty', ''])
        
        # Month 3 (prediction start point)
        month3_pos = "positive" in str(bacilloscopy_month_2).lower() or "+" in str(bacilloscopy_month_2)
        if month3_pos:
            bacilloscopy_month_3 = rng.choice(['Positive', '1+', 'Negative'], p=[0.15, 0.05, 0.8])
        else:
            bacilloscopy_month_3 = rng.choice(['Negative', 'Scanty', ''])
        
        # Month 4
        month4_pos = "positive" in str(bacilloscopy_month_3).lower() or "+" in str(bacilloscopy_month_3)
        if month4_pos:
            bacilloscopy_month_4 = rng.choice(['Positive', 'Negative'], p=[0.1, 0.9])
        else:
            bacilloscopy_month_4 = 'Negative'
        
        # Month 5 & 6
        bacilloscopy_month_5 = rng.choice(['Negative', 'Scanty', ''], p=[0.9, 0.08, 0.02])
        bacilloscopy_month_6 = rng.choice(['Negative', 'Scanty', ''], p=[0.9, 0.08, 0.02])
        
        # Outcome Status
        outcome_status = rng.choice(['cured', 'completed', 'failed', 'lost', 'died', 'transferred', ''])
        
        # State
        state = rng.choice(['State A', 'State B', 'State C', 'State D', 'State E', ''])
        
        # Days In Treatment
        days_in_treatment = int(rng.integers(90, 270))  # 3-9 months
        
        # Age
        age = int(rng.integers(18, 85))
        
        # Build row with exact feature names
        row = {
            'Notification_Date': notification_date.strftime('%Y-%m-%d'),
            'Sex': sex,
            'Race': race,
            'Treatment': treatment,
            'Chest_X_Ray': chest_x_ray,
            'Tuberculin_Test': tuberculin_test,
            'Clinical_Form': clinical_form,
            'AIDS_Comorbidity': aids_comorbidity,
            'Alcoholism_Comorbidity': alcoholism_comorbidity,
            'Diabetes_Comorbidity': diabetes_comorbidity,
            'Mental_Disorder_Comorbidity': mental_disorder_comorbidity,
            'Other_Comorbidity': other_comorbidity,
            'Bacilloscopy_Sputum': bacilloscopy_sputum,
            'Bacilloscopy_Sputum_2': bacilloscopy_sputum_2,
            'Bacilloscopy_Other': bacilloscopy_other,
            'Sputum_Culture': sputum_culture,
            'HIV': hiv,
            'Rifampicin': rifampicin,
            'Isoniazid': isoniazid,
            'Ethambutol': ethambutol,
            'Streptomycin': streptomycin,
            'Pyrazinamide': pyrazinamide,
            'Ethionamide': ethionamide,
            'Other_Drugs': other_drugs,
            'Supervised_Treatment': supervised_treatment,
            'Occupational_Disease': occupational_disease,
            'Bacilloscopy_Month_1': bacilloscopy_month_1,
            'Bacilloscopy_Month_2': bacilloscopy_month_2,
            'Bacilloscopy_Month_3': bacilloscopy_month_3,
            'Bacilloscopy_Month_4': bacilloscopy_month_4,
            'Bacilloscopy_Month_5': bacilloscopy_month_5,
            'Bacilloscopy_Month_6': bacilloscopy_month_6,
            'Outcome_Status': outcome_status,
            'Drug_Addiction_Comorbidity': drug_addiction_comorbidity,
            'Smoking_Comorbidity': smoking_comorbidity,
            'State': state,
            'Days_In_Treatment': days_in_treatment,
            'Age': age,
        }
        
        data.append(row)
    
    # Create DataFrame with exact column order
    df = pd.DataFrame(data, columns=features)
    
    # Save to CSV
    output_path = Path(output_file)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(output_path, index=False)
    
    print(f"Generated TB dataset with {n_rows} rows")
    print(f"Saved to: {output_path}")
    print(f"Features: {len(features)}")
    print(f"\nFirst few rows:")
    print(df.head(3).to_string())


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate single TB dataset CSV")
    parser.add_argument("-n", "--num-rows", type=int, default=50, help="Number of rows to generate")
    parser.add_argument("-o", "--output", type=Path, default=Path("ml/data/synthetic/tb_dataset.csv"), 
                       help="Output CSV file path")
    parser.add_argument("-s", "--seed", type=int, default=42, help="Random seed")
    
    args = parser.parse_args()
    generate_tb_dataset(args.output, args.num_rows, args.seed)

