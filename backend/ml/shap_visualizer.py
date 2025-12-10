"""
SHAP Visualization Service

Generates visual explanations for PTLD risk predictions using SHAP values.
"""

import shap
import matplotlib.pyplot as plt
import matplotlib
matplotlib.use('Agg')  # Non-interactive backend for server-side rendering
import numpy as np
from pathlib import Path
import logging

logger = logging.getLogger(__name__)


class SHAPVisualizer:
    """
    Generate SHAP visualization plots for model explanations.
    
    Usage:
        visualizer = SHAPVisualizer(media_root='/path/to/media')
        plot_path = visualizer.generate_waterfall_plot(
            shap_values, feature_values, feature_names, prediction_id
        )
    """
    
    def __init__(self, media_root=None):
        """
        Initialize the SHAP visualizer.
        
        Args:
            media_root: Path to media directory. Defaults to backend/media/
        """
        if media_root is None:
            # Default: backend/ml/ -> ../media/
            base_dir = Path(__file__).parent.parent
            media_root = base_dir / 'media'
        else:
            media_root = Path(media_root)
        
        self.media_root = media_root
        self.plots_dir = media_root / 'shap_plots'
        
        # Create directory if it doesn't exist
        self.plots_dir.mkdir(parents=True, exist_ok=True)
        logger.info(f"SHAP plots will be saved to: {self.plots_dir}")
    
    def generate_waterfall_plot(self, shap_values_dict, feature_values, 
                                feature_names, prediction_id, base_value=0.5):
        """
        Generate a waterfall plot showing feature contributions.
        
        Args:
            shap_values_dict: Dict of feature -> SHAP value
            feature_values: Dict of feature -> actual value
            feature_names: List of feature names (in order)
            prediction_id: Unique ID for the prediction (for filename)
            base_value: Expected value (average prediction)
        
        Returns:
            str: Relative path to saved plot (e.g., 'shap_plots/PR-123_waterfall.png')
        """
        try:
            # Convert dict to array in correct order
            shap_values = np.array([shap_values_dict.get(f, 0.0) for f in feature_names])
            feature_vals = np.array([feature_values.get(f, 0.0) for f in feature_names])
            
            # Create SHAP Explanation object
            explanation = shap.Explanation(
                values=shap_values,
                base_values=base_value,
                data=feature_vals,
                feature_names=feature_names
            )
            
            # Generate waterfall plot
            plt.figure(figsize=(10, 6))
            shap.plots.waterfall(explanation, show=False)
            plt.tight_layout()
            
            # Save to file
            filename = f"{prediction_id}_waterfall.png"
            filepath = self.plots_dir / filename
            plt.savefig(filepath, dpi=150, bbox_inches='tight')
            plt.close()
            
            logger.info(f"Generated waterfall plot: {filepath}")
            
            # Return relative path from media root
            return f"shap_plots/{filename}"
            
        except Exception as e:
            logger.error(f"Error generating waterfall plot: {e}")
            raise
    
    def generate_force_plot(self, shap_values_dict, feature_values, 
                           feature_names, prediction_id, base_value=0.5):
        """
        Generate a force plot showing feature contributions.
        
        Note: Force plots are typically interactive HTML. For static images,
        we'll use a bar chart of SHAP values as an alternative.
        
        Args:
            shap_values_dict: Dict of feature -> SHAP value
            feature_values: Dict of feature -> actual value
            feature_names: List of feature names
            prediction_id: Unique ID for the prediction
            base_value: Expected value
        
        Returns:
            str: Relative path to saved plot
        """
        try:
            # Convert to arrays
            shap_values = np.array([shap_values_dict.get(f, 0.0) for f in feature_names])
            
            # Sort by absolute SHAP value
            sorted_indices = np.argsort(np.abs(shap_values))[::-1]
            sorted_features = [feature_names[i] for i in sorted_indices]
            sorted_shap = [shap_values[i] for i in sorted_indices]
            
            # Create bar chart
            fig, ax = plt.subplots(figsize=(10, 6))
            colors = ['#ff0051' if val > 0 else '#008bfb' for val in sorted_shap]
            
            bars = ax.barh(sorted_features, sorted_shap, color=colors)
            ax.axvline(x=0, color='black', linewidth=0.8)
            ax.set_xlabel('SHAP Value (Impact on Prediction)', fontsize=12)
            ax.set_title('Feature Impact on PTLD Risk Prediction', fontsize=14, fontweight='bold')
            ax.set_ylabel('Features', fontsize=12)
            
            # Add value labels
            for i, (bar, val) in enumerate(zip(bars, sorted_shap)):
                label_x = val + (0.01 if val > 0 else -0.01)
                ha = 'left' if val > 0 else 'right'
                ax.text(label_x, i, f'{val:.3f}', va='center', ha=ha, fontsize=9)
            
            plt.tight_layout()
            
            # Save to file
            filename = f"{prediction_id}_force.png"
            filepath = self.plots_dir / filename
            plt.savefig(filepath, dpi=150, bbox_inches='tight')
            plt.close()
            
            logger.info(f"Generated force plot: {filepath}")
            
            return f"shap_plots/{filename}"
            
        except Exception as e:
            logger.error(f"Error generating force plot: {e}")
            raise
    
    def generate_feature_importance_table(self, shap_values_dict, feature_names):
        """
        Generate a sorted list of features by absolute SHAP value.
        
        Args:
            shap_values_dict: Dict of feature -> SHAP value
            feature_names: List of feature names
        
        Returns:
            list: List of tuples (feature_name, shap_value, abs_shap_value) sorted by importance
        """
        importance = []
        for feature in feature_names:
            shap_val = shap_values_dict.get(feature, 0.0)
            importance.append({
                'feature': feature,
                'shap_value': round(shap_val, 4),
                'abs_shap_value': round(abs(shap_val), 4),
                'impact': 'increases' if shap_val > 0 else 'decreases'
            })
        
        # Sort by absolute SHAP value (most important first)
        importance.sort(key=lambda x: x['abs_shap_value'], reverse=True)
        
        return importance


# Singleton instance
_visualizer_instance = None


def get_visualizer():
    """
    Get or create singleton visualizer instance.
    
    Returns:
        SHAPVisualizer: Initialized visualizer
    """
    global _visualizer_instance
    if _visualizer_instance is None:
        logger.info("Initializing SHAP visualizer singleton")
        _visualizer_instance = SHAPVisualizer()
    return _visualizer_instance
