"""
PTLD Risk Prediction Service

This module provides ML-based risk prediction for Post-Treatment Lung Disease (PTLD)
using trained XGBoost models with SHAP explainability.
"""

import pickle
import numpy as np
from pathlib import Path
import logging

logger = logging.getLogger(__name__)


class PTLDPredictor:
    """
    ML-based PTLD risk predictor using XGBoost model.
    
    Usage:
        predictor = PTLDPredictor()
        result = predictor.predict(patient_features)
    """
    
    def __init__(self, models_dir=None):
        """
        Initialize the predictor by loading trained models.
        
        Args:
            models_dir: Path to directory containing .pkl model files.
                       Defaults to ../ml/models relative to backend/
        """
        if models_dir is None:
            # Default path: backend/ml/ -> ../../ml/models/
            base_dir = Path(__file__).parent.parent.parent
            models_dir = base_dir / 'ml' / 'models'
        else:
            models_dir = Path(models_dir)
        
        self.models_dir = models_dir
        
        try:
            # Load XGBoost model (best performer)
            logger.info(f"Loading XGBoost model from {self.models_dir}")
            with open(self.models_dir / 'xgboost_model.pkl', 'rb') as f:
                self.model = pickle.load(f)
            
            # Load SHAP explainer
            logger.info("Loading SHAP explainer")
            with open(self.models_dir / 'shap_explainer.pkl', 'rb') as f:
                self.explainer = pickle.load(f)
            
            # Load metadata
            import json
            with open(self.models_dir / 'model_metadata.json') as f:
                self.metadata = json.load(f)
                self.feature_cols = self.metadata['feature_cols']
                self.model_version = self.metadata['model_version']
            
            logger.info(f"Models loaded successfully. Version: {self.model_version}")
            logger.info(f"Features: {', '.join(self.feature_cols)}")
            
        except FileNotFoundError as e:
            logger.error(f"Model files not found: {e}")
            raise RuntimeError(
                f"Could not load ML models from {self.models_dir}. "
                "Please ensure models are trained and saved."
            ) from e
        except Exception as e:
            logger.error(f"Error loading models: {e}")
            raise
    
    def predict(self, patient_features):
        """
        Predict PTLD risk for a patient.
        
        Args:
            patient_features: dict with keys matching self.feature_cols:
                - age: int (years)
                - bmi: float
                - hiv_positive: int (0 or 1)
                - diabetes: int (0 or 1)
                - smoker: int (0 or 1)
                - x_ray_score: float (0-20)
                - adherence_mean: float (0-100)
                - adherence_min: float (0-100)
                - adherence_std: float
                - modification_count: int
                - visit_count: int
        
        Returns:
            dict: {
                'risk_score': float (0-1),
                'risk_category': str ('low', 'medium', 'high'),
                'shap_values': dict of feature -> SHAP value,
                'model_version': str,
                'confidence': float (0-1)
            }
        
        Raises:
            ValueError: If required features are missing
        """
        # Validate features
        missing_features = set(self.feature_cols) - set(patient_features.keys())
        if missing_features:
            raise ValueError(f"Missing required features: {missing_features}")
        
        # Extract features in correct order
        feature_array = np.array([[
            patient_features[feat] for feat in self.feature_cols
        ]])
        
        # Predict probability
        try:
            risk_proba = self.model.predict_proba(feature_array)[0]
            risk_score = float(risk_proba[1])  # Probability of high risk class
        except Exception as e:
            logger.error(f"Prediction error: {e}")
            raise RuntimeError(f"Model prediction failed: {e}") from e
        
        # Categorize risk
        if risk_score < 0.33:
            risk_category = 'low'
        elif risk_score < 0.66:
            risk_category = 'medium'
        else:
            risk_category = 'high'
        
        # Calculate SHAP values for explainability
        try:
            shap_vals = self.explainer.shap_values(feature_array)[0]
            shap_dict = {
                feat: float(val) 
                for feat, val in zip(self.feature_cols, shap_vals)
            }
        except Exception as e:
            logger.warning(f"SHAP calculation failed: {e}")
            shap_dict = {feat: 0.0 for feat in self.feature_cols}
        
        # Calculate confidence (based on prediction probability)
        # Higher confidence when prediction is more certain (closer to 0 or 1)
        confidence = max(risk_proba[0], risk_proba[1])
        
        return {
            'risk_score': risk_score,
            'risk_category': risk_category,
            'shap_values': shap_dict,
            'model_version': self.model_version,
            'confidence': float(confidence)
        }
    
    def get_model_info(self):
        """
        Get information about loaded models.
        
        Returns:
            dict: Model metadata
        """
        return {
            'model_version': self.model_version,
            'features': self.feature_cols,
            'performance': self.metadata.get('performance', {}),
            'training_date': self.metadata.get('training_date')
        }


# Singleton instance - initialized once when Django starts
_predictor_instance = None


def get_predictor():
    """
    Get or create singleton predictor instance.
    
    Returns:
        PTLDPredictor: Initialized predictor
    """
    global _predictor_instance
    if _predictor_instance is None:
        logger.info("Initializing PTLD predictor singleton")
        _predictor_instance = PTLDPredictor()
    return _predictor_instance
