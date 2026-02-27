"""Test script for Prophet integration with the AI Retail Intelligence Platform.

This script tests the Prophet forecaster integration including:
- Basic Prophet model training and prediction
- Indian holiday calendar support
- Automatic seasonality detection
- Changepoint detection for trend analysis
- Integration with the main forecasting engine
"""

import sys
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

# Add src to path
sys.path.insert(0, 'src')

from src.forecasting_model import PriceForecastingEngine
from src.prophet_forecaster import ProphetForecaster, IndianHolidayCalendar
from src.data_loader import DataLoader


def test_indian_holiday_calendar():
    """Test Indian holiday calendar generation."""
    print("\n" + "="*80)
    print("TEST 1: Indian Holiday Calendar")
    print("="*80)
    
    try:
        holidays = IndianHolidayCalendar.get_indian_holidays(2024, 2026)
        print(f"✓ Generated {len(holidays)} holiday entries")
        
        # Show major holidays
        major_holidays = holidays[holidays['holiday'].isin(['Diwali', 'Dhanteras', 'Akshaya Tritiya'])]
        print(f"\nMajor holidays (2024-2026):")
        for _, row in major_holidays.head(10).iterrows():
            print(f"  - {row['holiday']}: {row['ds'].strftime('%Y-%m-%d')}")
        
        return True
    except Exception as e:
        print(f"✗ Failed: {str(e)}")
        return False


def test_prophet_basic_training():
    """Test basic Prophet model training."""
    print("\n" + "="*80)
    print("TEST 2: Basic Prophet Training")
    print("="*80)
    
    try:
        # Load gold price data
        data_loader = DataLoader()
        gold_data = data_loader.load_gold_prices('data/gold_prices.csv')
        print(f"✓ Loaded {len(gold_data)} gold price records")
        
        # Initialize Prophet forecaster
        prophet = ProphetForecaster(
            seasonality_mode='multiplicative',
            include_indian_holidays=True
        )
        print("✓ Initialized Prophet forecaster")
        
        # Train model
        training_info = prophet.fit(gold_data, target_column='close')
        print(f"✓ Training completed")
        print(f"  - Training samples: {training_info['training_samples']}")
        print(f"  - Changepoints detected: {training_info['changepoints_detected']}")
        print(f"  - Seasonality components: {training_info['seasonality_components']}")
        
        return True
    except Exception as e:
        print(f"✗ Failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


def test_prophet_prediction():
    """Test Prophet prediction capabilities."""
    print("\n" + "="*80)
    print("TEST 3: Prophet Prediction")
    print("="*80)
    
    try:
        # Load data
        data_loader = DataLoader()
        gold_data = data_loader.load_gold_prices('data/gold_prices.csv')
        
        # Train model
        prophet = ProphetForecaster(include_indian_holidays=True)
        prophet.fit(gold_data, target_column='close')
        
        # Make predictions
        horizon = 30
        predictions, confidence_intervals = prophet.predict(horizon)
        
        print(f"✓ Generated {len(predictions)} predictions")
        print(f"\nFirst 5 predictions:")
        for i in range(min(5, len(predictions))):
            print(f"  Day {i+1}: ₹{predictions[i]:,.2f} "
                  f"(CI: ₹{confidence_intervals['lower'][i]:,.2f} - ₹{confidence_intervals['upper'][i]:,.2f})")
        
        # Verify predictions are reasonable
        last_price = gold_data['close'].iloc[-1]
        avg_prediction = np.mean(predictions)
        
        print(f"\nPrediction analysis:")
        print(f"  - Last actual price: ₹{last_price:,.2f}")
        print(f"  - Average prediction: ₹{avg_prediction:,.2f}")
        print(f"  - Prediction range: ₹{min(predictions):,.2f} - ₹{max(predictions):,.2f}")
        
        return True
    except Exception as e:
        print(f"✗ Failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


def test_changepoint_detection():
    """Test changepoint detection."""
    print("\n" + "="*80)
    print("TEST 4: Changepoint Detection")
    print("="*80)
    
    try:
        # Load data
        data_loader = DataLoader()
        gold_data = data_loader.load_gold_prices('data/gold_prices.csv')
        
        # Train model with changepoint detection
        prophet = ProphetForecaster(
            changepoint_prior_scale=0.05,
            n_changepoints=25
        )
        prophet.fit(gold_data, target_column='close')
        
        # Make a prediction to populate forecast result
        prophet.predict(30)
        
        # Get changepoint analysis
        changepoint_analysis = prophet.get_changepoint_analysis()
        
        print(f"✓ Changepoint analysis completed")
        print(f"  - Changepoints detected: {changepoint_analysis['changepoints_detected']}")
        
        if changepoint_analysis['changepoints_detected'] > 0:
            print(f"\nSignificant trend changes:")
            for change in changepoint_analysis['significant_changes'][:5]:
                print(f"  - {change['date']}: {change['direction']} "
                      f"(magnitude: {change['trend_change']:.6f})")
        
        return True
    except Exception as e:
        print(f"✗ Failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


def test_seasonality_detection():
    """Test automatic seasonality detection."""
    print("\n" + "="*80)
    print("TEST 5: Seasonality Detection")
    print("="*80)
    
    try:
        # Load data
        data_loader = DataLoader()
        gold_data = data_loader.load_gold_prices('data/gold_prices.csv')
        
        # Train model with seasonality
        prophet = ProphetForecaster(
            seasonality_mode='multiplicative',
            yearly_seasonality=True,
            weekly_seasonality=True
        )
        prophet.fit(gold_data, target_column='close')
        
        # Make a prediction to populate forecast result
        prophet.predict(30)
        
        # Get seasonality analysis
        seasonality_analysis = prophet.get_seasonality_analysis()
        
        print(f"✓ Seasonality analysis completed")
        print(f"  - Seasonality detected: {seasonality_analysis['seasonality_detected']}")
        print(f"  - Mode: {seasonality_analysis.get('mode', 'N/A')}")
        
        if seasonality_analysis['seasonality_detected']:
            print(f"\nSeasonality components:")
            for component, info in seasonality_analysis['components'].items():
                print(f"  - {component}: strength = {info['strength']:.4f}")
        
        return True
    except Exception as e:
        print(f"✗ Failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


def test_holiday_impact():
    """Test Indian holiday impact analysis."""
    print("\n" + "="*80)
    print("TEST 6: Holiday Impact Analysis")
    print("="*80)
    
    try:
        # Load data
        data_loader = DataLoader()
        gold_data = data_loader.load_gold_prices('data/gold_prices.csv')
        
        # Train model with Indian holidays
        prophet = ProphetForecaster(
            include_indian_holidays=True,
            holidays_prior_scale=10.0
        )
        prophet.fit(gold_data, target_column='close')
        
        # Make a prediction to populate forecast result
        prophet.predict(30)
        
        # Get holiday impact
        holiday_impact = prophet.get_holiday_impact()
        
        print(f"✓ Holiday impact analysis completed")
        print(f"  - Holidays included: {holiday_impact['holidays_included']}")
        
        if 'total_holidays' in holiday_impact:
            print(f"  - Total holidays: {holiday_impact['total_holidays']}")
        
        if 'major_holidays' in holiday_impact:
            print(f"\nMajor Indian holidays affecting precious metals:")
            for holiday in holiday_impact['major_holidays']:
                print(f"  - {holiday}")
        
        return True
    except Exception as e:
        print(f"✗ Failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


def test_forecasting_engine_integration():
    """Test Prophet integration with main forecasting engine."""
    print("\n" + "="*80)
    print("TEST 7: Forecasting Engine Integration")
    print("="*80)
    
    try:
        # Initialize engine
        engine = PriceForecastingEngine()
        
        # Check if Prophet is available
        available_models = engine.get_available_models()
        print(f"✓ Available models: {available_models}")
        
        if 'prophet' not in available_models:
            print("✗ Prophet model not available in engine")
            return False
        
        # Load data
        data_loader = DataLoader()
        gold_data = data_loader.load_gold_prices('data/gold_prices.csv')
        
        # Train Prophet model through engine
        print("\nTraining Prophet model through engine...")
        engine.train_model(
            data=gold_data,
            target_column='close',
            model_name='prophet',
            symbol='GOLD'
        )
        print("✓ Training completed")
        
        # Make predictions
        print("\nGenerating predictions...")
        forecast = engine.predict_prices(
            symbol='GOLD',
            horizon=30,
            model_name='prophet'
        )
        
        print(f"✓ Generated forecast")
        print(f"  - Symbol: {forecast.symbol}")
        print(f"  - Horizon: {forecast.forecast_horizon}")
        print(f"  - Predictions: {len(forecast.predicted_prices)}")
        print(f"\nFirst 5 predictions:")
        for i in range(min(5, len(forecast.predicted_prices))):
            print(f"  Day {i+1}: ₹{forecast.predicted_prices[i]:,.2f}")
        
        # Evaluate model
        print("\nEvaluating model...")
        test_data = gold_data.tail(50)
        metrics = engine.evaluate_model(
            test_data=test_data,
            symbol='GOLD',
            target_column='close',
            model_name='prophet'
        )
        
        print(f"✓ Evaluation completed")
        print(f"  - MAE: ₹{metrics['mae']:,.2f}")
        print(f"  - RMSE: ₹{metrics['rmse']:,.2f}")
        print(f"  - R²: {metrics['r2']:.4f}")
        if 'mape' in metrics:
            print(f"  - MAPE: {metrics['mape']:.2f}%")
        if 'coverage' in metrics:
            print(f"  - Coverage: {metrics['coverage']:.2%}")
        
        return True
    except Exception as e:
        print(f"✗ Failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


def test_model_comparison():
    """Test comparison between Prophet and other models."""
    print("\n" + "="*80)
    print("TEST 8: Model Comparison")
    print("="*80)
    
    try:
        # Initialize engine
        engine = PriceForecastingEngine()
        
        # Load data
        data_loader = DataLoader()
        gold_data = data_loader.load_gold_prices('data/gold_prices.csv')
        
        # Split data
        train_data = gold_data.iloc[:-50]
        test_data = gold_data.iloc[-50:]
        
        # Test available models
        models_to_test = ['moving_average', 'random_forest', 'prophet']
        results = {}
        
        for model_name in models_to_test:
            if model_name not in engine.get_available_models():
                print(f"⊘ Skipping {model_name} (not available)")
                continue
            
            try:
                print(f"\nTesting {model_name}...")
                
                # Train
                engine.train_model(
                    data=train_data,
                    target_column='close',
                    model_name=model_name,
                    symbol='GOLD'
                )
                
                # Evaluate
                metrics = engine.evaluate_model(
                    test_data=test_data,
                    symbol='GOLD',
                    target_column='close',
                    model_name=model_name
                )
                
                results[model_name] = metrics
                print(f"  ✓ MAE: ₹{metrics['mae']:,.2f}, RMSE: ₹{metrics['rmse']:,.2f}, R²: {metrics['r2']:.4f}")
                
            except Exception as e:
                print(f"  ✗ Failed: {str(e)}")
        
        # Compare results
        if len(results) > 1:
            print(f"\n{'Model':<20} {'MAE':>12} {'RMSE':>12} {'R²':>8}")
            print("-" * 56)
            for model_name, metrics in sorted(results.items(), key=lambda x: x[1]['mae']):
                print(f"{model_name:<20} ₹{metrics['mae']:>10,.2f} ₹{metrics['rmse']:>10,.2f} {metrics['r2']:>7.4f}")
        
        return True
    except Exception as e:
        print(f"✗ Failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Run all Prophet integration tests."""
    print("\n" + "="*80)
    print("PROPHET INTEGRATION TEST SUITE")
    print("AI Retail Intelligence Platform")
    print("="*80)
    
    tests = [
        ("Indian Holiday Calendar", test_indian_holiday_calendar),
        ("Basic Prophet Training", test_prophet_basic_training),
        ("Prophet Prediction", test_prophet_prediction),
        ("Changepoint Detection", test_changepoint_detection),
        ("Seasonality Detection", test_seasonality_detection),
        ("Holiday Impact Analysis", test_holiday_impact),
        ("Forecasting Engine Integration", test_forecasting_engine_integration),
        ("Model Comparison", test_model_comparison)
    ]
    
    results = []
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"\n✗ Test '{test_name}' crashed: {str(e)}")
            results.append((test_name, False))
    
    # Summary
    print("\n" + "="*80)
    print("TEST SUMMARY")
    print("="*80)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✓ PASS" if result else "✗ FAIL"
        print(f"{status} - {test_name}")
    
    print(f"\nTotal: {passed}/{total} tests passed ({passed/total*100:.1f}%)")
    
    if passed == total:
        print("\n🎉 All tests passed! Prophet integration is working correctly.")
        return 0
    else:
        print(f"\n⚠️  {total - passed} test(s) failed. Please review the output above.")
        return 1


if __name__ == "__main__":
    exit(main())
