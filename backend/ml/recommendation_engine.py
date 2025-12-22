"""
PTLD Risk Recommendation Engine

Generates clinical recommendations based on risk predictions and patient features.
Provides actionable insights for clinicians to manage PTLD risk.
"""

import logging
from typing import Dict, List, Any

logger = logging.getLogger(__name__)


class RecommendationEngine:
    """
    Generates clinical recommendations for PTLD risk management.
    
    Usage:
        engine = RecommendationEngine()
        recommendations = engine.generate_recommendations(
            risk_category='high',
            risk_score=0.85,
            patient_features={...},
            shap_values={...}
        )
    """
    
    def __init__(self):
        """Initialize the recommendation engine."""
        self.recommendation_templates = self._load_recommendation_templates()
    
    def _load_recommendation_templates(self) -> Dict[str, List[Dict]]:
        """Load recommendation templates based on risk categories and features."""
        return {
            'low': [
                {
                    'category': 'monitoring',
                    'priority': 'low',
                    'title': 'Routine Monitoring',
                    'description': 'Continue standard TB treatment monitoring protocols.',
                    'actions': [
                        'Maintain current treatment regimen',
                        'Schedule routine follow-up visits every 2-3 months',
                        'Monitor adherence and adverse reactions'
                    ]
                }
            ],
            'medium': [
                {
                    'category': 'monitoring',
                    'priority': 'medium',
                    'title': 'Enhanced Monitoring',
                    'description': 'Increase monitoring frequency and assess treatment response.',
                    'actions': [
                        'Schedule follow-up visits monthly',
                        'Monitor adherence closely (target >90%)',
                        'Consider chest X-ray every 3 months',
                        'Assess for treatment modifications if needed'
                    ]
                },
                {
                    'category': 'adherence',
                    'priority': 'medium',
                    'title': 'Adherence Support',
                    'description': 'Provide additional support to improve treatment adherence.',
                    'actions': [
                        'Counsel patient on importance of adherence',
                        'Consider directly observed therapy (DOT)',
                        'Address barriers to adherence'
                    ]
                }
            ],
            'high': [
                {
                    'category': 'monitoring',
                    'priority': 'high',
                    'title': 'Intensive Monitoring',
                    'description': 'High risk detected. Implement intensive monitoring protocol.',
                    'actions': [
                        'Schedule follow-up visits every 2-4 weeks',
                        'Perform chest X-ray every 2-3 months',
                        'Monitor lung function tests',
                        'Consider referral to pulmonologist'
                    ]
                },
                {
                    'category': 'treatment',
                    'priority': 'high',
                    'title': 'Treatment Review',
                    'description': 'Review current treatment regimen for optimization.',
                    'actions': [
                        'Assess treatment response and efficacy',
                        'Consider treatment modification if indicated',
                        'Review drug interactions and adverse effects',
                        'Optimize drug dosages based on patient factors'
                    ]
                },
                {
                    'category': 'comorbidities',
                    'priority': 'high',
                    'title': 'Comorbidity Management',
                    'description': 'Manage comorbidities that may increase PTLD risk.',
                    'actions': [
                        'Optimize management of existing comorbidities',
                        'Screen for and manage diabetes if present',
                        'Provide smoking cessation support if applicable',
                        'Ensure HIV treatment is optimized if HIV-positive'
                    ]
                }
            ]
        }
    
    def generate_recommendations(
        self,
        risk_category: str,
        risk_score: float,
        patient_features: Dict[str, Any],
        shap_values: Dict[str, float]
    ) -> List[Dict[str, Any]]:
        """
        Generate personalized recommendations based on risk prediction.
        
        Args:
            risk_category: 'low', 'medium', or 'high'
            risk_score: Risk score (0-1)
            patient_features: Patient feature dictionary
            shap_values: SHAP values for feature importance
        
        Returns:
            List of recommendation dictionaries with category, priority, title, description, and actions
        """
        recommendations = []
        
        # Base recommendations from risk category
        base_recs = self.recommendation_templates.get(risk_category, [])
        recommendations.extend(base_recs.copy())
        
        # Feature-specific recommendations
        feature_recs = self._get_feature_specific_recommendations(
            patient_features, shap_values, risk_category
        )
        recommendations.extend(feature_recs)
        
        # Adherence-specific recommendations
        if 'adherence_mean' in patient_features:
            adherence_recs = self._get_adherence_recommendations(
                patient_features['adherence_mean'],
                risk_category
            )
            recommendations.extend(adherence_recs)
        
        # Comorbidity-specific recommendations
        comorbidity_recs = self._get_comorbidity_recommendations(
            patient_features, shap_values
        )
        recommendations.extend(comorbidity_recs)
        
        # Remove duplicates and sort by priority
        recommendations = self._deduplicate_recommendations(recommendations)
        recommendations = sorted(
            recommendations,
            key=lambda x: {'high': 3, 'medium': 2, 'low': 1}.get(x.get('priority', 'low'), 0),
            reverse=True
        )
        
        return recommendations
    
    def _get_feature_specific_recommendations(
        self,
        patient_features: Dict[str, Any],
        shap_values: Dict[str, float],
        risk_category: str
    ) -> List[Dict[str, Any]]:
        """Generate recommendations based on specific features driving risk."""
        recommendations = []
        
        # Find top risk-increasing features
        top_risk_features = sorted(
            [(k, v) for k, v in shap_values.items() if v > 0],
            key=lambda x: x[1],
            reverse=True
        )[:3]
        
        for feature, shap_value in top_risk_features:
            if feature == 'age' and patient_features.get('age', 0) > 60:
                recommendations.append({
                    'category': 'demographics',
                    'priority': 'medium' if risk_category == 'high' else 'low',
                    'title': 'Age-Related Risk Management',
                    'description': f'Patient age ({patient_features.get("age")} years) is contributing to increased risk.',
                    'actions': [
                        'Consider age-appropriate treatment adjustments',
                        'Monitor for age-related complications',
                        'Ensure adequate nutritional support'
                    ]
                })
            
            elif feature == 'comorbidity_count' and patient_features.get('comorbidity_count', 0) >= 3:
                recommendations.append({
                    'category': 'comorbidity',
                    'priority': 'high' if risk_category == 'high' else 'medium',
                    'title': 'Multiple Comorbidities',
                    'description': f'Patient has {patient_features.get("comorbidity_count", 0)} comorbidities, which increases PTLD risk.',
                    'actions': [
                        'Coordinate care with specialists',
                        'Review medication interactions',
                        'Monitor for complications',
                        'Consider treatment modifications'
                    ]
                })
            
            elif feature == 'comorbidity_count' and patient_features.get('comorbidity_count', 0) >= 2:
                recommendations.append({
                    'category': 'comorbidity',
                    'priority': 'medium',
                    'title': 'Comorbidity Management',
                    'description': f'Patient has {patient_features.get("comorbidity_count", 0)} comorbidities requiring attention.',
                    'actions': [
                        'Coordinate care with relevant specialists',
                        'Review medication interactions',
                        'Monitor for complications'
                        'Consider CT scan for detailed assessment',
                        'Monitor for progression of lung changes',
                        'Assess response to treatment'
                    ]
                })
            
            elif feature == 'modification_count' and patient_features.get('modification_count', 0) > 2:
                recommendations.append({
                    'category': 'treatment',
                    'priority': 'medium',
                    'title': 'Treatment Stability',
                    'description': f'Multiple treatment modifications ({patient_features.get("modification_count", 0)}) may indicate treatment challenges.',
                    'actions': [
                        'Review reasons for previous modifications',
                        'Assess current treatment efficacy',
                        'Consider treatment optimization',
                        'Monitor for adverse reactions'
                    ]
                })
        
        return recommendations
    
    def _get_adherence_recommendations(
        self,
        adherence_mean: float,
        risk_category: str
    ) -> List[Dict[str, Any]]:
        """Generate recommendations based on treatment adherence."""
        recommendations = []
        
        if adherence_mean < 80:
            recommendations.append({
                'category': 'adherence',
                'priority': 'high' if risk_category == 'high' else 'medium',
                'title': 'Critical Adherence Intervention',
                'description': f'Low adherence ({adherence_mean:.1f}%) is significantly impacting risk.',
                'actions': [
                    'Implement directly observed therapy (DOT)',
                    'Identify and address adherence barriers',
                    'Provide patient education on importance of adherence',
                    'Consider treatment simplification if possible',
                    'Schedule more frequent follow-ups to monitor adherence'
                ]
            })
        elif adherence_mean < 90:
            recommendations.append({
                'category': 'adherence',
                'priority': 'medium',
                'title': 'Adherence Improvement',
                'description': f'Adherence ({adherence_mean:.1f}%) is below optimal target (90%+).',
                'actions': [
                    'Counsel patient on importance of consistent adherence',
                    'Identify barriers to adherence',
                    'Consider adherence support interventions',
                    'Monitor adherence closely'
                ]
            })
        
        return recommendations
    
    def _get_comorbidity_recommendations(
        self,
        patient_features: Dict[str, Any],
        shap_values: Dict[str, float]
    ) -> List[Dict[str, Any]]:
        """Generate recommendations based on comorbidities."""
        recommendations = []
        
        if patient_features.get('hiv_positive', 0) == 1:
            hiv_shap = shap_values.get('hiv_positive', 0)
            if hiv_shap > 0.1:  # HIV is contributing to risk
                recommendations.append({
                    'category': 'comorbidities',
                    'priority': 'high',
                    'title': 'HIV Co-infection Management',
                    'description': 'HIV co-infection is contributing to increased PTLD risk.',
                    'actions': [
                        'Ensure optimal HIV treatment (ART)',
                        'Monitor CD4 count and viral load',
                        'Assess for drug interactions between TB and HIV medications',
                        'Coordinate care with HIV specialist',
                        'Monitor for opportunistic infections'
                    ]
                })
        
        if patient_features.get('diabetes', 0) == 1:
            diabetes_shap = shap_values.get('diabetes', 0)
            if diabetes_shap > 0.1:  # Diabetes is contributing to risk
                recommendations.append({
                    'category': 'comorbidities',
                    'priority': 'high',
                    'title': 'Diabetes Management',
                    'description': 'Diabetes is contributing to increased PTLD risk.',
                    'actions': [
                        'Optimize diabetes control (target HbA1c <7%)',
                        'Monitor blood glucose levels',
                        'Assess for diabetic complications',
                        'Coordinate with endocrinologist if needed',
                        'Consider impact of TB medications on glucose control'
                    ]
                })
        
        if patient_features.get('smoker', 0) == 1:
            smoker_shap = shap_values.get('smoker', 0)
            if smoker_shap > 0.1:  # Smoking is contributing to risk
                recommendations.append({
                    'category': 'lifestyle',
                    'priority': 'high',
                    'title': 'Smoking Cessation',
                    'description': 'Smoking is significantly contributing to PTLD risk.',
                    'actions': [
                        'Provide smoking cessation counseling',
                        'Offer smoking cessation support (counseling, medications)',
                        'Monitor smoking status at each visit',
                        'Educate on risks of continued smoking',
                        'Consider referral to smoking cessation program'
                    ]
                })
        
        return recommendations
    
    def _deduplicate_recommendations(
        self,
        recommendations: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """Remove duplicate recommendations based on title."""
        seen_titles = set()
        unique_recs = []
        
        for rec in recommendations:
            title = rec.get('title', '')
            if title not in seen_titles:
                seen_titles.add(title)
                unique_recs.append(rec)
            else:
                # Merge actions if same title but different actions
                for existing_rec in unique_recs:
                    if existing_rec.get('title') == title:
                        existing_actions = set(existing_rec.get('actions', []))
                        new_actions = set(rec.get('actions', []))
                        existing_rec['actions'] = list(existing_actions.union(new_actions))
                        break
        
        return unique_recs


# Singleton instance
_recommendation_engine_instance = None


def get_recommendation_engine():
    """
    Get or create singleton recommendation engine instance.
    
    Returns:
        RecommendationEngine: Initialized recommendation engine
    """
    global _recommendation_engine_instance
    if _recommendation_engine_instance is None:
        logger.info("Initializing recommendation engine singleton")
        _recommendation_engine_instance = RecommendationEngine()
    return _recommendation_engine_instance






