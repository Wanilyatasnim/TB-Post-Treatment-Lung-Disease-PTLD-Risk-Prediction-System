"""
PTLD Risk Prediction: EDA for TB Dataset
Works directly with tb_dataset.csv (single file format)
"""

import pandas as pd
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import seaborn as sns
import warnings
warnings.filterwarnings('ignore')

# Set style
sns.set_style("whitegrid")
plt.rcParams['figure.figsize'] = (12, 6)
plt.rcParams['font.size'] = 10

print("="*60)
print("PTLD Risk Prediction - EDA for TB Dataset")
print("="*60)

# Load TB dataset
print("\nLoading TB dataset...")
df = pd.read_csv('../data/synthetic/tb_dataset.csv')
print(f"Dataset shape: {df.shape}")
print(f"Columns: {list(df.columns)}")

# ============================================================================
# 1. DATA QUALITY CHECKS
# ============================================================================
print("\n" + "="*60)
print("1. DATA QUALITY ANALYSIS")
print("="*60)

print("\nMissing Values Analysis:")
missing_pct = (df.isnull().sum() / len(df) * 100).round(2)
if missing_pct.any():
    print(missing_pct[missing_pct > 0])
else:
    print("No missing values")

# ============================================================================
# 2. FEATURE ENGINEERING
# ============================================================================
print("\n" + "="*60)
print("2. FEATURE ENGINEERING")
print("="*60)

# Create patient_id if it doesn't exist
if 'patient_id' not in df.columns:
    df['patient_id'] = df.index.map(lambda x: f'PT-{x+1:05d}')

# Map column names to standard format
column_mapping = {
    'Age': 'age',
    'Sex': 'sex',
    'HIV': 'hiv_positive',
    'Diabetes_Comorbidity': 'diabetes',
    'Smoking_Comorbidity': 'smoker',
    'AIDS_Comorbidity': 'aids_comorbidity',
    'Alcoholism_Comorbidity': 'alcoholism_comorbidity',
    'Mental_Disorder_Comorbidity': 'mental_disorder_comorbidity',
    'Drug_Addiction_Comorbidity': 'drug_addiction_comorbidity',
    'Other_Comorbidity': 'other_comorbidity',
    'Days_In_Treatment': 'days_in_treatment',
    'Supervised_Treatment': 'supervised_treatment',
    'Bacilloscopy_Month_1': 'bacilloscopy_month_1',
    'Bacilloscopy_Month_2': 'bacilloscopy_month_2',
    'Bacilloscopy_Month_3': 'bacilloscopy_month_3',
    'Bacilloscopy_Month_4': 'bacilloscopy_month_4',
    'Bacilloscopy_Month_5': 'bacilloscopy_month_5',
    'Bacilloscopy_Month_6': 'bacilloscopy_month_6',
    'Outcome_Status': 'outcome',
}

# Rename columns
for old_col, new_col in column_mapping.items():
    if old_col in df.columns:
        df[new_col] = df[old_col]

# Convert boolean fields
bool_fields = ['hiv_positive', 'diabetes', 'smoker', 'aids_comorbidity',
               'alcoholism_comorbidity', 'mental_disorder_comorbidity',
               'drug_addiction_comorbidity', 'supervised_treatment']
for field in bool_fields:
    if field in df.columns:
        df[field] = df[field].astype(int) if df[field].dtype == 'bool' else df[field].fillna(0).astype(int)

# Calculate comorbidity count
def safe_column_sum(series, default=0):
    """Safely sum a series, returning default if empty."""
    if series is None or len(series) == 0:
        return default
    return series.fillna(0).astype(int).sum()

df['comorbidity_count'] = (
    df.get('hiv_positive', pd.Series([0] * len(df))).fillna(0).astype(int) +
    df.get('diabetes', pd.Series([0] * len(df))).fillna(0).astype(int) +
    df.get('smoker', pd.Series([0] * len(df))).fillna(0).astype(int) +
    df.get('aids_comorbidity', pd.Series([0] * len(df))).fillna(0).astype(int) +
    df.get('alcoholism_comorbidity', pd.Series([0] * len(df))).fillna(0).astype(int) +
    df.get('mental_disorder_comorbidity', pd.Series([0] * len(df))).fillna(0).astype(int) +
    df.get('drug_addiction_comorbidity', pd.Series([0] * len(df))).fillna(0).astype(int) +
    (df.get('other_comorbidity', pd.Series([''] * len(df))).notna() & 
     (df.get('other_comorbidity', pd.Series([''] * len(df))) != '')).astype(int)
)

# Convert bacilloscopy to numeric (positive=1, negative=0)
bacilloscopy_fields = ['bacilloscopy_month_1', 'bacilloscopy_month_2', 'bacilloscopy_month_3']
for field in bacilloscopy_fields:
    if field in df.columns:
        df[f'{field}_numeric'] = df[field].apply(
            lambda x: 1 if x and any(pos in str(x).lower() for pos in ['positive', '+', 'pos', '1', '2', '3', 'scanty']) else 0
        )

# Since tb_dataset.csv doesn't have monitoring visits or modifications,
# we need to estimate these features based on available data
print("\nEstimating treatment features (not in dataset):")

# Estimate adherence based on days_in_treatment and outcome
# Patients with longer treatment and better outcomes likely have better adherence
if 'days_in_treatment' in df.columns and 'outcome' in df.columns:
    # Base adherence on outcome: cured/completed = higher adherence
    outcome_adherence_map = {
        'cured': 0.95,
        'completed': 0.90,
        'died': 0.60,
        'failure': 0.70,
        'defaulted': 0.50,
        'transferred': 0.85
    }
    df['adherence_mean'] = df['outcome'].map(outcome_adherence_map).fillna(0.85) * 100
    
    # Add some variation
    np.random.seed(42)
    df['adherence_mean'] = df['adherence_mean'] + np.random.normal(0, 5, len(df))
    df['adherence_mean'] = df['adherence_mean'].clip(50, 100)
    
    # Calculate min and std from mean
    df['adherence_min'] = df['adherence_mean'] - np.random.uniform(5, 15, len(df))
    df['adherence_min'] = df['adherence_min'].clip(40, 100)
    
    df['adherence_std'] = np.random.uniform(2, 8, len(df))
else:
    # Default values if outcome not available
    df['adherence_mean'] = 85.0
    df['adherence_min'] = 75.0
    df['adherence_std'] = 5.0

# Estimate modification count based on comorbidities and treatment duration
# More comorbidities and longer treatment = more likely to have modifications
if 'comorbidity_count' in df.columns and 'days_in_treatment' in df.columns:
    # Higher comorbidity count and longer treatment = more modifications
    base_modifications = (df['comorbidity_count'] * 0.3 + 
                          (df['days_in_treatment'] / 180) * 0.5)
    df['modification_count'] = np.random.poisson(base_modifications.clip(0, 5))
else:
    df['modification_count'] = 0

# Estimate visit count based on treatment duration
# Assume monthly visits, so visits = days_in_treatment / 30
if 'days_in_treatment' in df.columns:
    df['visit_count'] = (df['days_in_treatment'] / 30).round().astype(int).clip(1, 12)
else:
    df['visit_count'] = 6  # Default: 6 months of treatment

# Create risk_score based on features (for training target)
# This is a heuristic risk score - in real scenario, this would come from actual predictions
print("\nCalculating risk scores (heuristic):")
risk_scores = []
for idx, row in df.iterrows():
    base_risk = 0.2
    # Age factor (older = higher risk)
    age_factor = (row.get('age', 40) - 18) / 82 * 0.15
    # Comorbidity factor
    comorbidity_factor = row.get('comorbidity_count', 0) * 0.08
    # HIV factor
    hiv_factor = row.get('hiv_positive', 0) * 0.15
    # Adherence factor (lower adherence = higher risk)
    adherence_factor = (1 - row.get('adherence_mean', 85) / 100) * 0.25
    # Modification factor (more modifications = higher risk)
    mod_factor = row.get('modification_count', 0) * 0.05
    # Bacilloscopy at month 3 (positive = higher risk)
    bac_m3 = row.get('bacilloscopy_month_3_numeric', 0) * 0.12
    
    risk = base_risk + age_factor + comorbidity_factor + hiv_factor + adherence_factor + mod_factor + bac_m3
    risk = np.clip(risk + np.random.normal(0, 0.05), 0, 1)
    risk_scores.append(risk)

df['risk_score'] = risk_scores

# Categorize risk
df['risk_category'] = pd.cut(df['risk_score'], 
                             bins=[0, 0.33, 0.66, 1.0],
                             labels=['low', 'medium', 'high'])

print(f"Risk distribution:")
print(df['risk_category'].value_counts())

# ============================================================================
# 3. DEMOGRAPHIC ANALYSIS
# ============================================================================
print("\n" + "="*60)
print("3. DEMOGRAPHIC ANALYSIS")
print("="*60)

print("\nAge Statistics:")
print(df['age'].describe())

# Age distribution
fig, axes = plt.subplots(1, 2, figsize=(14, 5))
axes[0].hist(df['age'], bins=30, edgecolor='black', alpha=0.7, color='steelblue')
axes[0].axvline(df['age'].median(), color='red', linestyle='--', 
                label=f'Median: {df["age"].median():.0f}')
axes[0].set_xlabel('Age (years)')
axes[0].set_ylabel('Frequency')
axes[0].set_title('Age Distribution of TB Patients')
axes[0].legend()
axes[0].grid(alpha=0.3)

# Age by sex
if 'sex' in df.columns:
    age_by_sex = df.groupby('sex')['age'].apply(list)
    if len(age_by_sex) > 0:
        sex_data = [age_by_sex[sex] for sex in age_by_sex.index if len(age_by_sex[sex]) > 0]
        sex_labels = [sex for sex in age_by_sex.index if len(age_by_sex[sex]) > 0]
        if sex_data:
            axes[1].boxplot(sex_data, labels=sex_labels)
            axes[1].set_ylabel('Age (years)')
            axes[1].set_title('Age Distribution by Sex')
            axes[1].grid(alpha=0.3)

plt.tight_layout()
plt.savefig('../data/synthetic/eda_age_distribution.png', dpi=300, bbox_inches='tight')
print("  Saved: eda_age_distribution.png")
plt.close()

# Sex distribution
if 'sex' in df.columns:
    sex_counts = df['sex'].value_counts()
    print(f"\nSex Distribution:")
    print(sex_counts)

# ============================================================================
# 4. COMORBIDITY ANALYSIS
# ============================================================================
print("\n" + "="*60)
print("4. COMORBIDITY ANALYSIS")
print("="*60)

comorbidities = {}
if 'hiv_positive' in df.columns:
    comorbidities['HIV'] = df['hiv_positive'].sum()
if 'diabetes' in df.columns:
    comorbidities['Diabetes'] = df['diabetes'].sum()
if 'smoker' in df.columns:
    comorbidities['Smoker'] = df['smoker'].sum()

if comorbidities:
    print("\nComorbidity Prevalence:")
    for name, count in comorbidities.items():
        print(f"  {name}: {count} ({count/len(df)*100:.1f}%)")

    plt.figure(figsize=(10, 6))
    bars = plt.bar(comorbidities.keys(), comorbidities.values(), 
                   color=['#e74c3c', '#3498db', '#95a5a6'], alpha=0.8)
    plt.ylabel('Number of Patients')
    plt.title('Prevalence of Comorbidities')
    plt.grid(alpha=0.3, axis='y')

    for bar, (name, count) in zip(bars, comorbidities.items()):
        height = bar.get_height()
        plt.text(bar.get_x() + bar.get_width()/2., height,
                 f'{count}\n({count/len(df)*100:.1f}%)',
                 ha='center', va='bottom', fontweight='bold')

    plt.savefig('../data/synthetic/eda_comorbidities.png', dpi=300, bbox_inches='tight')
    print("  Saved: eda_comorbidities.png")
    plt.close()

# Comorbidity count distribution
if 'comorbidity_count' in df.columns:
    combo_counts = df['comorbidity_count'].value_counts().sort_index()
    print(f"\nComorbidity Burden:")
    for count, num_patients in combo_counts.items():
        print(f"  {count} comorbidities: {num_patients} patients ({num_patients/len(df)*100:.1f}%)")

# ============================================================================
# 5. CORRELATION ANALYSIS
# ============================================================================
print("\n" + "="*60)
print("5. RISK FACTOR CORRELATION ANALYSIS")
print("="*60)

# Select numeric features for correlation
numeric_features = ['age', 'hiv_positive', 'diabetes', 'smoker', 'comorbidity_count',
                   'adherence_mean', 'adherence_min', 'adherence_std', 
                   'modification_count', 'visit_count', 'risk_score']

# Filter to only existing columns
numeric_features = [f for f in numeric_features if f in df.columns]

if len(numeric_features) > 1:
    corr_matrix = df[numeric_features].corr()
    
    plt.figure(figsize=(12, 10))
    sns.heatmap(corr_matrix, annot=True, fmt='.2f', cmap='RdYlGn_r', center=0,
                square=True, linewidths=1, cbar_kws={"shrink": 0.8})
    plt.title('Feature Correlation Matrix with Risk Score', fontsize=14, fontweight='bold')
    plt.tight_layout()
    plt.savefig('../data/synthetic/eda_correlation_matrix.png', dpi=300, bbox_inches='tight')
    print("  Saved: eda_correlation_matrix.png")
    plt.close()
    
    if 'risk_score' in corr_matrix.columns:
        risk_corr = corr_matrix['risk_score'].sort_values(ascending=False)
        print("\nTop Risk Score Correlations:")
        print(risk_corr.head(6))

# ============================================================================
# 6. TREATMENT OUTCOME ANALYSIS
# ============================================================================
print("\n" + "="*60)
print("6. TREATMENT OUTCOME ANALYSIS")
print("="*60)

if 'outcome' in df.columns:
    outcome_counts = df['outcome'].value_counts()
    print("\nTreatment Outcomes:")
    print(outcome_counts)
    
    success_rate = (outcome_counts.get('cured', 0) + outcome_counts.get('completed', 0))/len(df)*100
    print(f"\nSuccess Rate (Cured + Completed): {success_rate:.1f}%")

# ============================================================================
# 7. SAVE MERGED FEATURES
# ============================================================================
print("\n" + "="*60)
print("7. SAVING MERGED FEATURES")
print("="*60)

# Select columns for modeling
feature_cols = ['patient_id', 'age', 'hiv_positive', 'diabetes', 'smoker', 
                'comorbidity_count', 'adherence_mean', 'adherence_min', 'adherence_std',
                'modification_count', 'visit_count', 'risk_score', 'risk_category']

# Add outcome if available
if 'outcome' in df.columns:
    feature_cols.append('outcome')

# Filter to existing columns
feature_cols = [col for col in feature_cols if col in df.columns]

# Create final dataset
merged_df = df[feature_cols].copy()

# Save merged dataset
merged_df.to_csv('../data/synthetic/merged_features.csv', index=False)
print(f"\nSaved merged features dataset: merged_features.csv")
print(f"Shape: {merged_df.shape}")
print(f"Columns: {list(merged_df.columns)}")

# ============================================================================
# KEY FINDINGS SUMMARY
# ============================================================================
print("\n" + "="*60)
print("KEY FINDINGS SUMMARY")
print("="*60)

print(f"\n1. PATIENT DEMOGRAPHICS:")
print(f"   • Total patients: {len(df):,}")
print(f"   • Age range: {df['age'].min()}-{df['age'].max()} years (median: {df['age'].median():.0f})")

print(f"\n2. COMORBIDITY BURDEN:")
if 'hiv_positive' in df.columns:
    hiv_count = df['hiv_positive'].sum()
    print(f"   • HIV positive: {hiv_count} ({hiv_count/len(df)*100:.1f}%)")
if 'diabetes' in df.columns:
    diabetes_count = df['diabetes'].sum()
    print(f"   • Diabetes: {diabetes_count} ({diabetes_count/len(df)*100:.1f}%)")
if 'smoker' in df.columns:
    smoker_count = df['smoker'].sum()
    print(f"   • Smokers: {smoker_count} ({smoker_count/len(df)*100:.1f}%)")

print(f"\n3. TREATMENT FEATURES (Estimated):")
print(f"   • Mean adherence: {df['adherence_mean'].mean():.1f}%")
print(f"   • Avg modifications per patient: {df['modification_count'].mean():.1f}")
print(f"   • Avg visits per patient: {df['visit_count'].mean():.1f}")

print(f"\n4. RISK DISTRIBUTION:")
if 'risk_category' in df.columns:
    risk_cat_counts = df['risk_category'].value_counts()
    for cat, count in risk_cat_counts.items():
        print(f"   • {cat} risk: {count} ({count/len(df)*100:.1f}%)")

if 'outcome' in df.columns:
    print(f"\n5. TREATMENT OUTCOMES:")
    success_rate = ((df['outcome'] == 'cured').sum() + (df['outcome'] == 'completed').sum())/len(df)*100
    print(f"   • Success rate: {success_rate:.1f}%")

print("\n" + "="*60)
print("EDA COMPLETE - Ready for Model Training")
print("="*60)
print(f"\nGenerated visualization files in ml/data/synthetic/")
print(f"Merged features saved for modeling: merged_features.csv")

