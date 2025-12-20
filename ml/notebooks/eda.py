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

# Age group analysis (replacing BMI)
print(f"\nAge Distribution:")
print(f"   Min: {patients_df['age'].min()}, Max: {patients_df['age'].max()}, Median: {patients_df['age'].median()}")

# Days in treatment analysis (replacing BMI)
if 'days_in_treatment' in patients_df.columns:
    plt.figure(figsize=(12, 5))
    plt.subplot(1, 2, 1)
    plt.hist(patients_df['days_in_treatment'].dropna(), bins=30, edgecolor='black', alpha=0.7, color='green')
    plt.axvline(patients_df['days_in_treatment'].median(), color='red', linestyle='--', 
                label=f'Median: {patients_df["days_in_treatment"].median():.0f} days')
    plt.xlabel('Days in Treatment')
    plt.ylabel('Frequency')
    plt.title('Treatment Duration Distribution')
    plt.legend()
    plt.grid(alpha=0.3)

    plt.subplot(1, 2, 2)
    treatment_categories = pd.cut(patients_df['days_in_treatment'].dropna(), bins=[0, 120, 180, 240, 365], 
                            labels=['<4 months', '4-6 months', '6-8 months', '8-12 months'])
    treat_cat_counts = treatment_categories.value_counts()
    plt.bar(range(len(treat_cat_counts)), treat_cat_counts.values, color='teal', alpha=0.7)
    plt.xticks(range(len(treat_cat_counts)), treat_cat_counts.index, rotation=45)
    plt.ylabel('Count')
    plt.title('Treatment Duration Categories')
    plt.grid(alpha=0.3, axis='y')

    plt.tight_layout()
    plt.savefig('../data/synthetic/eda_treatment_duration_analysis.png', dpi=300, bbox_inches='tight')
    print("  Saved: eda_treatment_duration_analysis.png")
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
full_df = full_df.merge(regimens_df[['patient_id', 'outcome']], on='patient_id', how='left', suffixes=('', '_regimen'))

full_df['modification_count'] = full_df['modification_count'].fillna(0)
full_df['adherence_std'] = full_df['adherence_std'].fillna(0)
full_df['adherence_mean'] = full_df['adherence_mean'].fillna(0.9)
full_df['adherence_min'] = full_df['adherence_min'].fillna(0.85)
full_df['visit_count'] = full_df['visit_count'].fillna(0)

# Convert boolean fields to int for correlation
bool_fields = ['hiv_positive', 'diabetes', 'smoker', 'aids_comorbidity', 
               'alcoholism_comorbidity', 'mental_disorder_comorbidity', 
               'drug_addiction_comorbidity', 'supervised_treatment', 
               'occupational_disease', 'rifampicin', 'isoniazid', 'ethambutol',
               'streptomycin', 'pyrazinamide', 'ethionamide']
for field in bool_fields:
    if field in full_df.columns:
        full_df[field] = full_df[field].astype(int) if full_df[field].dtype == 'bool' else full_df[field].fillna(0).astype(int)

# Convert bacilloscopy to numeric (positive=1, negative=0)
bacilloscopy_fields = ['bacilloscopy_month_1', 'bacilloscopy_month_2', 'bacilloscopy_month_3']
for field in bacilloscopy_fields:
    if field in full_df.columns:
        full_df[f'{field}_numeric'] = full_df[field].apply(
            lambda x: 1 if x and any(pos in str(x).lower() for pos in ['positive', '+', 'pos', '1', '2', '3']) else 0
        )

# Calculate comorbidity count
def safe_column_sum(df, col_name, default=0):
    """Safely get column and convert to int, returning default if column doesn't exist."""
    if col_name in df.columns:
        return df[col_name].fillna(0).astype(int)
    else:
        return pd.Series([default] * len(df), index=df.index)

full_df['comorbidity_count'] = (
    safe_column_sum(full_df, 'hiv_positive') +
    safe_column_sum(full_df, 'diabetes') +
    safe_column_sum(full_df, 'smoker') +
    safe_column_sum(full_df, 'aids_comorbidity') +
    safe_column_sum(full_df, 'alcoholism_comorbidity') +
    safe_column_sum(full_df, 'mental_disorder_comorbidity') +
    safe_column_sum(full_df, 'drug_addiction_comorbidity') +
    (full_df['other_comorbidity'].notna() & (full_df['other_comorbidity'] != '')).astype(int)
    if 'other_comorbidity' in full_df.columns else pd.Series([0] * len(full_df), index=full_df.index)
)

# Correlation matrix - use new TB dataset features
numeric_features = ['age', 'hiv_positive', 'diabetes', 'smoker', 'aids_comorbidity',
                   'alcoholism_comorbidity', 'mental_disorder_comorbidity', 
                   'drug_addiction_comorbidity', 'comorbidity_count',
                   'bacilloscopy_month_3_numeric', 'supervised_treatment',
                   'adherence_mean', 'adherence_min', 'adherence_std', 
                   'modification_count', 'visit_count', 'days_in_treatment', 'risk_score']

# Filter to only existing columns
numeric_features = [f for f in numeric_features if f in full_df.columns]

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
if 'notification_date' in patients_df.columns:
    print(f"   • Notification date range: {patients_df['notification_date'].min()} to {patients_df['notification_date'].max()}")

print(f"\n2. COMORBIDITY BURDEN:")
if 'hiv_positive' in patients_df.columns:
    hiv_count = patients_df['hiv_positive'].sum() if patients_df['hiv_positive'].dtype == 'bool' else (patients_df['hiv_positive'] == 1).sum()
    print(f"   • HIV positive: {hiv_count} ({hiv_count/len(patients_df)*100:.1f}%)")
if 'diabetes' in patients_df.columns:
    diabetes_count = patients_df['diabetes'].sum() if patients_df['diabetes'].dtype == 'bool' else (patients_df['diabetes'] == 1).sum()
    print(f"   • Diabetes: {diabetes_count} ({diabetes_count/len(patients_df)*100:.1f}%)")
if 'smoker' in patients_df.columns:
    smoker_count = patients_df['smoker'].sum() if patients_df['smoker'].dtype == 'bool' else (patients_df['smoker'] == 1).sum()
    print(f"   • Smokers: {smoker_count} ({smoker_count/len(patients_df)*100:.1f}%)")
if 'aids_comorbidity' in patients_df.columns:
    aids_count = patients_df['aids_comorbidity'].sum() if patients_df['aids_comorbidity'].dtype == 'bool' else (patients_df['aids_comorbidity'] == 1).sum()
    print(f"   • AIDS: {aids_count} ({aids_count/len(patients_df)*100:.1f}%)")

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
