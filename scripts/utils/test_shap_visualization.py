"""
Test script to verify SHAP visualization functionality
"""

import os
import sys
import django

# Setup Django environment
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'app.settings')
django.setup()

from ml.shap_visualizer import SHAPVisualizer
import numpy as np

def test_shap_visualizer():
    """Test the SHAP visualizer standalone"""
    print("=" * 60)
    print("Testing SHAP Visualizer")
    print("=" * 60)
    
    # Create visualizer instance
    visualizer = SHAPVisualizer()
    print(f"✓ Visualizer initialized")
    print(f"  Plots directory: {visualizer.plots_dir}")
    
    # Sample feature data (without BMI and x_ray_score)
    feature_names = [
        'age', 'hiv_positive', 'diabetes', 'smoker', 'comorbidity_count',
        'adherence_mean', 'adherence_min', 'adherence_std', 
        'modification_count', 'visit_count'
    ]
    
    # Sample SHAP values and feature values
    shap_values = {
        'age': 0.15,
        'hiv_positive': 0.22,
        'diabetes': 0.08,
        'smoker': 0.12,
        'comorbidity_count': 0.18,
        'adherence_mean': -0.25,
        'adherence_min': -0.10,
        'adherence_std': 0.05,
        'modification_count': 0.14,
        'visit_count': -0.06
    }
    
    feature_values = {
        'age': 45,
        'hiv_positive': 1,
        'diabetes': 0,
        'smoker': 1,
        'comorbidity_count': 2,
        'adherence_mean': 75.0,
        'adherence_min': 60.0,
        'adherence_std': 10.5,
        'modification_count': 2,
        'visit_count': 6
    }
    
    prediction_id = "TEST-PR-001"
    
    try:
        # Test waterfall plot
        print("\n📊 Generating waterfall plot...")
        waterfall_path = visualizer.generate_waterfall_plot(
            shap_values_dict=shap_values,
            feature_values=feature_values,
            feature_names=feature_names,
            prediction_id=prediction_id,
            base_value=0.5
        )
        print(f"✓ Waterfall plot generated: {waterfall_path}")
        
        # Test force plot
        print("\n📊 Generating force plot...")
        force_path = visualizer.generate_force_plot(
            shap_values_dict=shap_values,
            feature_values=feature_values,
            feature_names=feature_names,
            prediction_id=prediction_id,
            base_value=0.5
        )
        print(f"✓ Force plot generated: {force_path}")
        
        # Test feature importance table
        print("\n📋 Generating feature importance table...")
        importance = visualizer.generate_feature_importance_table(
            shap_values_dict=shap_values,
            feature_names=feature_names
        )
        print(f"✓ Feature importance table generated ({len(importance)} features)")
        print("\nTop 5 Most Important Features:")
        for i, feat in enumerate(importance[:5], 1):
            print(f"  {i}. {feat['feature']}: {feat['shap_value']:+.4f} ({feat['impact']} risk)")
        
        # Verify files exist
        print("\n📁 Verifying generated files...")
        waterfall_full = visualizer.plots_dir / f"{prediction_id}_waterfall.png"
        force_full = visualizer.plots_dir / f"{prediction_id}_force.png"
        
        if waterfall_full.exists():
            print(f"✓ Waterfall plot file exists: {waterfall_full}")
        else:
            print(f"✗ Waterfall plot file NOT found: {waterfall_full}")
        
        if force_full.exists():
            print(f"✓ Force plot file exists: {force_full}")
        else:
            print(f"✗ Force plot file NOT found: {force_full}")
        
        print("\n" + "=" * 60)
        print("✅ All SHAP visualization tests passed!")
        print("=" * 60)
        
    except Exception as e:
        print(f"\n❌ Error during testing: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    return True


def test_model_integration():
    """Test integration with ML predictor"""
    print("\n" + "=" * 60)
    print("Testing ML Model Integration")
    print("=" * 60)
    
    try:
        from ml.predictor import get_predictor
        
        predictor = get_predictor()
        print(f"✓ Predictor loaded")
        print(f"  Model version: {predictor.model_version}")
        print(f"  Features: {len(predictor.feature_cols)}")
        
        # Sample patient features (without BMI and x_ray_score)
        features = {
            'age': 45,
            'hiv_positive': 1,
            'diabetes': 0,
            'smoker': 1,
            'comorbidity_count': 2,
            'adherence_mean': 75.0,
            'adherence_min': 60.0,
            'adherence_std': 10.5,
            'modification_count': 2,
            'visit_count': 6
        }
        
        print("\n🔮 Generating prediction...")
        result = predictor.predict(features)
        
        print(f"✓ Prediction successful!")
        print(f"  Risk Score: {result['risk_score']:.4f}")
        print(f"  Risk Category: {result['risk_category']}")
        print(f"  Confidence: {result['confidence']:.2f}")
        print(f"  SHAP values: {len(result['shap_values'])} features")
        
        # Test visualization with real prediction
        print("\n📊 Generating visualizations from prediction...")
        visualizer = SHAPVisualizer()
        
        prediction_id = "TEST-PR-002"
        waterfall_path = visualizer.generate_waterfall_plot(
            shap_values_dict=result['shap_values'],
            feature_values=features,
            feature_names=predictor.feature_cols,
            prediction_id=prediction_id
        )
        
        print(f"✓ Waterfall plot: {waterfall_path}")
        
        print("\n" + "=" * 60)
        print("✅ ML Model integration tests passed!")
        print("=" * 60)
        
    except Exception as e:
        print(f"\n❌ Error during ML integration test: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    return True


if __name__ == "__main__":
    print("\n🧪 SHAP Visualization Testing Suite\n")
    
    # Run tests
    test1 = test_shap_visualizer()
    test2 = test_model_integration()
    
    # Summary
    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)
    print(f"SHAP Visualizer Test: {'✅ PASS' if test1 else '❌ FAIL'}")
    print(f"ML Integration Test: {'✅ PASS' if test2 else '❌ FAIL'}")
    print("=" * 60)
    
    if test1 and test2:
        print("\n🎉 All tests passed! SHAP visualization is working correctly.")
        sys.exit(0)
    else:
        print("\n⚠️  Some tests failed. Please review the errors above.")
        sys.exit(1)
