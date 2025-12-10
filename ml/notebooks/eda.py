"""
PTLD Risk Prediction: Exploratory Data Analysis
Complete EDA with visualizations and statistical analysis
"""

import pandas as pd
import numpy as np
import matplotlib
matplotlib.use('Agg')  # Use non-interactive backend
import matplotlib.pyplot as plt
import seaborn as sns
import warnings
warnings.filterwarnings('ignore')

# Set style
sns.set_style("whitegrid")
plt.rcParams['figure.figsize'] = (12, 6)
plt.rcParams['font.size'] = 10

print("="*60)
print("PTLD Risk Prediction - Exploratory Data Analysis")
print("="*60)

# Load all datasets
print("\nLoading datasets...")
patients_df = pd.read_csv('../data/synthetic/patients.csv')
regimens_df = pd.read_csv('../data/synthetic/treatment_regimens.csv')
modifications_df = pd.read_csv('../data/synthetic/treatment_modifications.csv')
visits_df = pd.read_csv('../data/synthetic/monitoring_visits.csv')
predictions_df = pd.read_csv('../data/synthetic/risk_predictions.csv')

print(f"\nDataset Sizes:")
print(f"  Patients: {len(patients_df):,}")
print(f"  Regimens: {len(regimens_df):,}")
print(f"  Modifications: {len(modifications_df):,}")
print(f"  Visits: {len(visits_df):,}")
print(f"  Predictions: {len(predictions_df):,}")

# ============================================================================
# 1. DATA QUALITY CHECKS
# ============================================================================
print("\n" + "="*60)
print("1. DATA QUALITY ANALYSIS")
print("="*60)

print("\nMissing Values Analysis:")
for name, df in [('Patients', patients_df), ('Regimens', regimens_df), 
                  ('Modifications', modifications_df), ('Visits', visits_df)]:
    missing_pct = (df.isnull().sum() / len(df) * 100).round(2)
    if missing_pct.any():
        print(f"\n{name}:")
        print(missing_pct[missing_pct > 0])
    else:
        print(f"\n{name}: No missing values")

# ============================================================================
# 2. DEMOGRAPHIC ANALYSIS
# ============================================================================
print("\n" + "="*60)
print("2. DEMOGRAPHIC ANALYSIS")
print("="*60)

print("\nAge Statistics:")
print(patients_df['age'].describe())

# Age distribution
fig, axes = plt.subplots(1, 2, figsize=(14, 5))

axes[0].hist(patients_df['age'], bins=30, edgecolor='black', alpha=0.7, color='steelblue')
axes[0].axvline(patients_df['age'].median(), color='red', linestyle='--', 
                label=f'Median: {patients_df["age"].median():.0f}')
axes[0].set_xlabel('Age (years)')
axes[0].set_ylabel('Frequency')
axes[0].set_title('Age Distribution of TB Patients')
axes[0].legend()
axes[0].grid(alpha=0.3)

# Age by sex
age_by_sex = patients_df.groupby('sex')['age'].apply(list)
axes[1].boxplot([age_by_sex['M'], age_by_sex['F']], labels=['Male', 'Female'])
axes[1].set_ylabel('Age (years)')
axes[1].set_title('Age Distribution by Sex')
axes[1].grid(alpha=0.3)

plt.tight_layout()
plt.savefig('../data/synthetic/eda_age_distribution.png', dpi=300, bbox_inches='tight')
print("  Saved: eda_age_distribution.png")
plt.close()

# Sex distribution
sex_counts = patients_df['sex'].value_counts()
print(f"\nSex Distribution:")
print(sex_counts)

# BMI analysis
print(f"\nBMI Statistics:")
print(patients_df['bmi'].describe())

plt.figure(figsize=(12, 5))
plt.subplot(1, 2, 1)
plt.hist(patients_df['bmi'], bins=30, edgecolor='black', alpha=0.7, color='green')
plt.axvline(patients_df['bmi'].median(), color='red', linestyle='--', 
            label=f'Median: {patients_df["bmi"].median():.1f}')
plt.xlabel('BMI')
plt.ylabel('Frequency')
plt.title('BMI Distribution')
plt.legend()
plt.grid(alpha=0.3)

plt.subplot(1, 2, 2)
bmi_categories = pd.cut(patients_df['bmi'], bins=[0, 18.5, 25, 30, 100], 
                        labels=['Underweight', 'Normal', 'Overweight', 'Obese'])
bmi_cat_counts = bmi_categories.value_counts()
plt.bar(range(len(bmi_cat_counts)), bmi_cat_counts.values, color='teal', alpha=0.7)
plt.xticks(range(len(bmi_cat_counts)), bmi_cat_counts.index, rotation=45)
plt.ylabel('Count')
plt.title('BMI Categories')
plt.grid(alpha=0.3, axis='y')

plt.tight_layout()
plt.savefig('../data/synthetic/eda_bmi_analysis.png', dpi=300, bbox_inches='tight')
print("  Saved: eda_bmi_analysis.png")
plt.close()

# ============================================================================
# 3. COMORBIDITY ANALYSIS
# ============================================================================
print("\n" + "="*60)
print("3. COMORBIDITY ANALYSIS")
print("="*60)

comorbidities = {
    'HIV': patients_df['hiv_positive'].sum(),
    'Diabetes': patients_df['diabetes'].sum(),
    'Smoker': patients_df['smoker'].sum()
}

print("\nComorbidity Prevalence:")
for name, count in comorbidities.items():
    print(f"  {name}: {count} ({count/len(patients_df)*100:.1f}%)")

plt.figure(figsize=(10, 6))
bars = plt.bar(comorbidities.keys(), comorbidities.values(), 
               color=['#e74c3c', '#3498db', '#95a5a6'], alpha=0.8)
plt.ylabel('Number of Patients')
plt.title('Prevalence of Comorbidities (N=1000)')
plt.grid(alpha=0.3, axis='y')

for bar, (name, count) in zip(bars, comorbidities.items()):
    height = bar.get_height()
    plt.text(bar.get_x() + bar.get_width()/2., height,
             f'{count}\n({count/len(patients_df)*100:.1f}%)',
             ha='center', va='bottom', fontweight='bold')

plt.savefig('../data/synthetic/eda_comorbidities.png', dpi=300, bbox_inches='tight')
print("  Saved: eda_comorbidities.png")
plt.close()

# Comorbidity combinations
patients_df['comorbidity_count'] = (
    patients_df['hiv_positive'].astype(int) + 
    patients_df['diabetes'].astype(int) + 
    patients_df['smoker'].astype(int)
)

combo_counts = patients_df['comorbidity_count'].value_counts().sort_index()
print(f"\nComorbidity Burden:")
for count, num_patients in combo_counts.items():
    print(f"  {count} comorbidities: {num_patients} patients ({num_patients/len(patients_df)*100:.1f}%)")

# ============================================================================
# 4. TREATMENT PATTERN ANALYSIS
# ============================================================================
print("\n" + "="*60)
print("4. TREATMENT PATTERN ANALYSIS")
print("="*60)

print(f"\nTreatment Modification Statistics:")
print(f"  Total modifications: {len(modifications_df)}")
print(f"  Patients with modifications: {modifications_df['patient_id'].nunique()}")
print(f"  Avg modifications per affected patient: {len(modifications_df) / modifications_df['patient_id'].nunique():.2f}")

# Modification reasons
mod_reasons = modifications_df['reason'].value_counts()
print(f"\nModification Reasons:")
print(mod_reasons)

fig, axes = plt.subplots(1, 2, figsize=(14, 5))

axes[0].pie(mod_reasons.values, labels=mod_reasons.index, autopct='%1.1f%%', startangle=90)
axes[0].set_title('Treatment Modification Reasons')

mod_drugs = modifications_df['modified_drug'].value_counts()
axes[1].bar(range(len(mod_drugs)), mod_drugs.values, color='coral', alpha=0.8)
axes[1].set_xticks(range(len(mod_drugs)))
axes[1].set_xticklabels(mod_drugs.index)
axes[1].set_ylabel('Number of Modifications')
axes[1].set_title('Most Frequently Modified Drugs')
axes[1].grid(alpha=0.3, axis='y')

plt.tight_layout()
plt.savefig('../data/synthetic/eda_treatment_modifications.png', dpi=300, bbox_inches='tight')
print("  Saved: eda_treatment_modifications.png")
plt.close()

# Monitoring visits
print(f"\nMonitoring Visit Statistics:")
print(f"  Total visits: {len(visits_df)}")
print(f"  Avg visits per patient: {len(visits_df) / visits_df['patient_id'].nunique():.1f}")
print(f"  Mean adherence: {visits_df['adherence_pct'].mean():.1f}%")

# ============================================================================
# 5. RISK FACTOR CORRELATION ANALYSIS
# ============================================================================
print("\n" + "="*60)
print("5. RISK FACTOR CORRELATION ANALYSIS")
print("="*60)

# Aggregate features
visit_features = visits_df.groupby('patient_id').agg({
    'adherence_pct': ['mean', 'std', 'min'],
    'visit_id': 'count'
}).reset_index()
visit_features.columns = ['patient_id', 'adherence_mean', 'adherence_std', 
                          'adherence_min', 'visit_count']

mod_counts = modifications_df.groupby('patient_id').size().reset_index(name='modification_count')

pred_features = predictions_df[['patient_id', 'risk_score', 'risk_category']].copy()

# Merge all features
full_df = patients_df.merge(visit_features, on='patient_id', how='left')
full_df = full_df.merge(mod_counts, on='patient_id', how='left')
full_df = full_df.merge(pred_features, on='patient_id', how='left')
full_df = full_df.merge(regimens_df[['patient_id', 'outcome']], on='patient_id', how='left')

full_df['modification_count'] = full_df['modification_count'].fillna(0)
full_df['adherence_std'] = full_df['adherence_std'].fillna(0)

# Correlation matrix
numeric_features = ['age', 'bmi', 'hiv_positive', 'diabetes', 'smoker', 'x_ray_score',
                   'adherence_mean', 'adherence_min', 'modification_count', 
                   'visit_count', 'risk_score']

corr_matrix = full_df[numeric_features].corr()

plt.figure(figsize=(12, 10))
sns.heatmap(corr_matrix, annot=True, fmt='.2f', cmap='RdYlGn_r', center=0,
            square=True, linewidths=1, cbar_kws={"shrink": 0.8})
plt.title('Feature Correlation Matrix with Risk Score', fontsize=14, fontweight='bold')
plt.tight_layout()
plt.savefig('../data/synthetic/eda_correlation_matrix.png', dpi=300, bbox_inches='tight')
print("  Saved: eda_correlation_matrix.png")
plt.close()

risk_corr = corr_matrix['risk_score'].sort_values(ascending=False)
print("\nTop Risk Score Correlations:")
print(risk_corr.head(6))

# ============================================================================
# 6. TREATMENT OUTCOME ANALYSIS
# ============================================================================
print("\n" + "="*60)
print("6. TREATMENT OUTCOME ANALYSIS")
print("="*60)

outcome_counts = regimens_df['outcome'].value_counts()
print("\nTreatment Outcomes:")
print(outcome_counts)

success_rate = (outcome_counts.get('cured', 0) + outcome_counts.get('completed', 0))/len(regimens_df)*100
print(f"\nSuccess Rate (Cured + Completed): {success_rate:.1f}%")

# Save merged dataset
full_df.to_csv('../data/synthetic/merged_features.csv', index=False)
print(f"\nSaved merged features dataset: merged_features.csv")

# ============================================================================
# KEY FINDINGS SUMMARY
# ============================================================================
print("\n" + "="*60)
print("KEY FINDINGS SUMMARY")
print("="*60)

print(f"\n1. PATIENT DEMOGRAPHICS:")
print(f"   • Total patients: {len(patients_df):,}")
print(f"   • Age range: {patients_df['age'].min()}-{patients_df['age'].max()} years (median: {patients_df['age'].median():.0f})")
print(f"   • Mean BMI: {patients_df['bmi'].mean():.2f}")

print(f"\n2. COMORBIDITY BURDEN:")
print(f"   • HIV positive: {patients_df['hiv_positive'].sum()} ({patients_df['hiv_positive'].sum()/len(patients_df)*100:.1f}%)")
print(f"   • Diabetes: {patients_df['diabetes'].sum()} ({patients_df['diabetes'].sum()/len(patients_df)*100:.1f}%)")
print(f"   • Smokers: {patients_df['smoker'].sum()} ({patients_df['smoker'].sum()/len(patients_df)*100:.1f}%)")

print(f"\n3. TREATMENT PATTERNS:")
print(f"   • Modifications: {len(modifications_df)} ({modifications_df['patient_id'].nunique()/len(patients_df)*100:.1f}% of patients)")
print(f"   • Mean adherence: {visits_df['adherence_pct'].mean():.1f}%")
print(f"   • Avg visits per patient: {len(visits_df) / visits_df['patient_id'].nunique():.1f}")

print(f"\n4. RISK DISTRIBUTION:")
risk_cat_counts = full_df['risk_category'].value_counts()
print(f"   • High risk: {risk_cat_counts.get('high', 0)} ({risk_cat_counts.get('high', 0)/len(full_df)*100:.1f}%)")
print(f"   • Medium risk: {risk_cat_counts.get('medium', 0)} ({risk_cat_counts.get('medium', 0)/len(full_df)*100:.1f}%)")
print(f"   • Low risk: {risk_cat_counts.get('low', 0)} ({risk_cat_counts.get('low', 0)/len(full_df)*100:.1f}%)")

print(f"\n5. TREATMENT OUTCOMES:")
print(f"   • Success rate: {success_rate:.1f}%")

print("\n" + "="*60)
print("EDA COMPLETE - Ready for Model Training")
print("="*60)
print(f"\nGenerated {8} visualization files in ml/data/synthetic/")
print(f"Merged features saved for modeling: merged_features.csv")
