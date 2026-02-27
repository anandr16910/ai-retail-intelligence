"""Test script for LSTM integration with the forecasting engine."""

import sys
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

# Add src to path
sys.path.insert(0, 'src')

from src.forecasting_model import PriceForecastingEngine
from src.data_loader import DataLoader

def test_lstm_integration():
    """Test LSTM model integration."""
    print("=" * 60)
    print("Testing LSTM Integration with Forecasting Engine")
    print("=" * 60)
    
    # Initialize forecasting engine
    print("\n1. Initializing forecasting engine...")
    engine = PriceForecastingEngine()
    
    # Check available models
    print("\n2. Available models:")
    available_models = engine.get_available_models()
    for model in available_models:
        print(f"   - {model}")
    
    # Check if LSTM is available
    if 'lstm' not in available_models:
        print("\n❌ LSTM model not available. Please install PyTorch.")
        return False
    
    print("\n✓ LSTM model is available!")
    
    # Get model info
    print("\n3. Model information:")
    model_info = engine.get_model_info()
    print(f"   Dependencies:")
    print(f"   - sklearn_available: {model_info['dependencies']['sklearn_available']}")
    print(f"   - lstm_available: {model_info['dependencies']['lstm_available']}")
    
    # Load sample data
    print("\n4. Loading sample gold price data...")
    try:
        data_loader = DataLoader()
        gold_data = data_loader.load_gold_prices('data/gold_prices.csv')
        print(f"   Loaded {len(gold_data)} records")
        print(f"   Date range: {gold_data['date'].min()} to {gold_data['date'].max()}")
    except Exception as e:
        print(f"   ❌ Error loading data: {str(e)}")
        return False
    
    # Train LSTM model
    print("\n5. Training LSTM model (this may take a few minutes)...")
    try:
        engine.train_model(
            data=gold_data,
            target_column='close',
            model_name='lstm',
            symbol='GOLD'
        )
        print("   ✓ LSTM model trained successfully!")
    except Exception as e:
        print(f"   ❌ Error training LSTM model: {str(e)}")
        import traceback
        traceback.print_exc()
        return False
    
    # Make predictions
    print("\n6. Generating predictions for next 30 days...")
    try:
        forecast = engine.predict_prices(
            symbol='GOLD',
            horizon=30,
            model_name='lstm'
        )
        
        print(f"   ✓ Generated {len(forecast.predicted_prices)} predictions")
        print(f"   First 5 predictions: {[f'{p:.2f}' for p in forecast.predicted_prices[:5]]}")
        print(f"   Last 5 predictions: {[f'{p:.2f}' for p in forecast.predicted_prices[-5:]]}")
        
    except Exception as e:
        print(f"   ❌ Error making predictions: {str(e)}")
        import traceback
        traceback.print_exc()
        return False
    
    # Evaluate model
    print("\n7. Evaluating model on test data...")
    try:
        # Use last 100 records as test data
        test_data = gold_data.tail(100)
        metrics = engine.evaluate_model(
            test_data=test_data,
            symbol='GOLD',
            target_column='close',
            model_name='lstm'
        )
        
        print(f"   Model Performance Metrics:")
        print(f"   - MAE: {metrics['mae']:.2f}")
        print(f"   - RMSE: {metrics['rmse']:.2f}")
        print(f"   - R²: {metrics['r2']:.4f}")
        print(f"   - Accuracy: {metrics['accuracy']:.4f}")
        
    except Exception as e:
        print(f"   ❌ Error evaluating model: {str(e)}")
        import traceback
        traceback.print_exc()
        return False
    
    print("\n" + "=" * 60)
    print("✓ All LSTM integration tests passed!")
    print("=" * 60)
    
    return True

if __name__ == "__main__":
    success = test_lstm_integration()
    sys.exit(0 if success else 1)
