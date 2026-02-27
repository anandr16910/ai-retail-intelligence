"""Machine learning-based price forecasting for AI Retail Intelligence Platform."""

import os
import json
import pickle
from abc import ABC, abstractmethod
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple, Any, Union
from dataclasses import dataclass
import warnings
warnings.filterwarnings('ignore')

try:
    import pandas as pd
    import numpy as np
    from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
    from sklearn.preprocessing import StandardScaler
    from sklearn.ensemble import RandomForestRegressor
    SKLEARN_AVAILABLE = True
except ImportError:
    SKLEARN_AVAILABLE = False

from src.exceptions import ModelTrainingError, ForecastingError
from src.config import settings

# Try to import LSTM forecaster
try:
    from src.lstm_forecaster import LSTMForecaster
    LSTM_AVAILABLE = True
except ImportError:
    LSTM_AVAILABLE = False
    print("Warning: LSTM forecaster not available. Install PyTorch to enable LSTM models.")

# Try to import Prophet forecaster
try:
    from src.prophet_forecaster import ProphetForecaster
    PROPHET_AVAILABLE = True
except ImportError:
    PROPHET_AVAILABLE = False
    print("Warning: Prophet forecaster not available. Install prophet to enable Prophet models.")


@dataclass
class ForecastResult:
    """Data model for forecast results."""
    symbol: str
    forecast_horizon: int
    predicted_prices: List[float]
    confidence_intervals: Dict[str, List[float]]
    model_metrics: Dict[str, float]
    timestamp: datetime
    
    def get_accuracy_score(self) -> float:
        """Get model accuracy score."""
        return self.model_metrics.get('accuracy', 0.0)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            'symbol': self.symbol,
            'forecast_horizon': self.forecast_horizon,
            'predicted_prices': self.predicted_prices,
            'confidence_intervals': self.confidence_intervals,
            'model_metrics': self.model_metrics,
            'timestamp': self.timestamp.isoformat()
        }


class TimeSeriesModel(ABC):
    """Abstract base class for time series forecasting models."""
    
    def __init__(self, name: str):
        self.name = name
        self.is_trained = False
        self.model = None
        self.scaler = None
        
    @abstractmethod
    def fit(self, data: pd.DataFrame, target_column: str = 'close') -> None:
        """Train the model on historical data."""
        pass
    
    @abstractmethod
    def predict(self, horizon: int) -> Tuple[List[float], Dict[str, List[float]]]:
        """Generate predictions for specified horizon."""
        pass
    
    @abstractmethod
    def evaluate(self, test_data: pd.DataFrame, target_column: str = 'close') -> Dict[str, float]:
        """Evaluate model performance on test data."""
        pass


class SimpleMovingAverageModel(TimeSeriesModel):
    """Simple moving average model for basic forecasting."""
    
    def __init__(self, window: int = 30):
        super().__init__("Simple Moving Average")
        self.window = window
        self.historical_data = None
        
    def fit(self, data: pd.DataFrame, target_column: str = 'close') -> None:
        """Train the moving average model."""
        try:
            if target_column not in data.columns:
                raise ModelTrainingError(f"Target column '{target_column}' not found in data")
            
            self.historical_data = data[target_column].values
            self.is_trained = True
            
        except Exception as e:
            raise ModelTrainingError(f"Failed to train moving average model: {str(e)}")
    
    def predict(self, horizon: int) -> Tuple[List[float], Dict[str, List[float]]]:
        """Generate predictions using moving average."""
        if not self.is_trained:
            raise ForecastingError("Model must be trained before making predictions")
        
        try:
            # Use last window values for prediction
            recent_values = self.historical_data[-self.window:]
            base_prediction = float(np.mean(recent_values))
            
            # Generate predictions (simple approach: use moving average with slight trend)
            predictions = []
            trend = (recent_values[-1] - recent_values[0]) / len(recent_values)
            
            for i in range(horizon):
                pred = base_prediction + (trend * i)
                predictions.append(pred)
            
            # Simple confidence intervals (±5% of prediction)
            confidence_intervals = {
                'lower': [p * 0.95 for p in predictions],
                'upper': [p * 1.05 for p in predictions]
            }
            
            return predictions, confidence_intervals
            
        except Exception as e:
            raise ForecastingError(f"Prediction failed: {str(e)}")
    
    def evaluate(self, test_data: pd.DataFrame, target_column: str = 'close') -> Dict[str, float]:
        """Evaluate model performance."""
        try:
            if not self.is_trained:
                return {'mae': float('inf'), 'rmse': float('inf'), 'r2': -1.0}
            
            actual = test_data[target_column].values
            
            # Generate predictions for test period
            predictions = []
            for i in range(len(actual)):
                if i < self.window:
                    # Use available historical data
                    window_data = np.concatenate([self.historical_data[-(self.window-i):], actual[:i]])
                else:
                    window_data = actual[i-self.window:i]
                
                pred = np.mean(window_data)
                predictions.append(pred)
            
            predictions = np.array(predictions)
            
            # Calculate metrics
            mae = float(np.mean(np.abs(actual - predictions)))
            rmse = float(np.sqrt(np.mean((actual - predictions) ** 2)))
            
            # R² score
            ss_res = np.sum((actual - predictions) ** 2)
            ss_tot = np.sum((actual - np.mean(actual)) ** 2)
            r2 = 1 - (ss_res / ss_tot) if ss_tot != 0 else 0
            
            return {
                'mae': mae,
                'rmse': rmse,
                'r2': float(r2),
                'accuracy': max(0, min(1, r2))  # Normalized accuracy
            }
            
        except Exception as e:
            return {'mae': float('inf'), 'rmse': float('inf'), 'r2': -1.0, 'accuracy': 0.0}


class RandomForestModel(TimeSeriesModel):
    """Random Forest model for time series forecasting."""
    
    def __init__(self, n_estimators: int = 100, lookback_window: int = 30):
        super().__init__("Random Forest")
        self.n_estimators = n_estimators
        self.lookback_window = lookback_window
        self.feature_columns = []
        
        if SKLEARN_AVAILABLE:
            self.model = RandomForestRegressor(n_estimators=n_estimators, random_state=42)
            self.scaler = StandardScaler()
        else:
            raise ModelTrainingError("scikit-learn not available. Please install required dependencies.")
    
    def _create_features(self, data: pd.DataFrame, target_column: str) -> Tuple[np.ndarray, np.ndarray]:
        """Create features for time series forecasting."""
        try:
            # Create lagged features
            features = []
            targets = []
            
            prices = data[target_column].values
            
            for i in range(self.lookback_window, len(prices)):
                # Use previous prices as features
                feature_row = prices[i-self.lookback_window:i]
                
                # Add technical indicators if available
                if 'ma_7' in data.columns:
                    feature_row = np.append(feature_row, data['ma_7'].iloc[i])
                if 'ma_30' in data.columns:
                    feature_row = np.append(feature_row, data['ma_30'].iloc[i])
                if 'volatility' in data.columns:
                    feature_row = np.append(feature_row, data['volatility'].iloc[i])
                if 'price_change' in data.columns:
                    feature_row = np.append(feature_row, data['price_change'].iloc[i])
                
                features.append(feature_row)
                targets.append(prices[i])
            
            return np.array(features), np.array(targets)
            
        except Exception as e:
            raise ModelTrainingError(f"Feature creation failed: {str(e)}")
    
    def fit(self, data: pd.DataFrame, target_column: str = 'close') -> None:
        """Train the Random Forest model."""
        try:
            if not SKLEARN_AVAILABLE:
                raise ModelTrainingError("scikit-learn not available")
            
            if target_column not in data.columns:
                raise ModelTrainingError(f"Target column '{target_column}' not found in data")
            
            # Create features
            X, y = self._create_features(data, target_column)
            
            if len(X) == 0:
                raise ModelTrainingError("Insufficient data for training")
            
            # Scale features
            X_scaled = self.scaler.fit_transform(X)
            
            # Train model
            self.model.fit(X_scaled, y)
            self.is_trained = True
            
            # Store last values for prediction
            self.last_values = data[target_column].tail(self.lookback_window).values
            self.last_data = data.tail(self.lookback_window).copy()
            
        except Exception as e:
            raise ModelTrainingError(f"Failed to train Random Forest model: {str(e)}")
    
    def predict(self, horizon: int) -> Tuple[List[float], Dict[str, List[float]]]:
        """Generate predictions using Random Forest."""
        if not self.is_trained:
            raise ForecastingError("Model must be trained before making predictions")
        
        try:
            predictions = []
            current_values = self.last_values.copy()
            
            for _ in range(horizon):
                # Create feature vector
                feature_row = current_values.copy()
                
                # Add technical indicators (simplified)
                if len(current_values) >= 7:
                    ma_7 = np.mean(current_values[-7:])
                    feature_row = np.append(feature_row, ma_7)
                
                if len(current_values) >= 30:
                    ma_30 = np.mean(current_values[-30:])
                    feature_row = np.append(feature_row, ma_30)
                else:
                    feature_row = np.append(feature_row, np.mean(current_values))
                
                # Volatility
                volatility = np.std(current_values[-min(30, len(current_values)):])
                feature_row = np.append(feature_row, volatility)
                
                # Price change
                price_change = (current_values[-1] - current_values[-2]) / current_values[-2] if len(current_values) > 1 else 0
                feature_row = np.append(feature_row, price_change)
                
                # Scale and predict
                feature_scaled = self.scaler.transform([feature_row])
                pred = self.model.predict(feature_scaled)[0]
                
                predictions.append(float(pred))
                
                # Update current values for next prediction
                current_values = np.append(current_values[1:], pred)
            
            # Generate confidence intervals using model uncertainty
            # For Random Forest, use prediction variance across trees
            confidence_intervals = {
                'lower': [p * 0.92 for p in predictions],  # Simplified confidence intervals
                'upper': [p * 1.08 for p in predictions]
            }
            
            return predictions, confidence_intervals
            
        except Exception as e:
            raise ForecastingError(f"Prediction failed: {str(e)}")
    
    def evaluate(self, test_data: pd.DataFrame, target_column: str = 'close') -> Dict[str, float]:
        """Evaluate Random Forest model performance."""
        try:
            if not self.is_trained or not SKLEARN_AVAILABLE:
                return {'mae': float('inf'), 'rmse': float('inf'), 'r2': -1.0, 'accuracy': 0.0}
            
            # Create test features
            X_test, y_test = self._create_features(test_data, target_column)
            
            if len(X_test) == 0:
                return {'mae': float('inf'), 'rmse': float('inf'), 'r2': -1.0, 'accuracy': 0.0}
            
            # Scale features
            X_test_scaled = self.scaler.transform(X_test)
            
            # Make predictions
            y_pred = self.model.predict(X_test_scaled)
            
            # Calculate metrics
            mae = mean_absolute_error(y_test, y_pred)
            rmse = np.sqrt(mean_squared_error(y_test, y_pred))
            r2 = r2_score(y_test, y_pred)
            
            return {
                'mae': float(mae),
                'rmse': float(rmse),
                'r2': float(r2),
                'accuracy': max(0, min(1, r2))  # Normalized accuracy
            }
            
        except Exception as e:
            return {'mae': float('inf'), 'rmse': float('inf'), 'r2': -1.0, 'accuracy': 0.0}


class ProphetModel(TimeSeriesModel):
    """Facebook Prophet model wrapper for time series forecasting."""
    
    def __init__(self, seasonality_mode: str = 'multiplicative',
                 changepoint_prior_scale: float = 0.05,
                 include_indian_holidays: bool = True,
                 yearly_seasonality: bool = True,
                 weekly_seasonality: bool = True):
        """Initialize Prophet model wrapper.
        
        Args:
            seasonality_mode: 'additive' or 'multiplicative' seasonality
            changepoint_prior_scale: Flexibility of trend changes
            include_indian_holidays: Include Indian market holiday calendar
            yearly_seasonality: Enable yearly seasonality
            weekly_seasonality: Enable weekly seasonality
        """
        super().__init__("Facebook Prophet")
        
        if not PROPHET_AVAILABLE:
            raise ModelTrainingError("Prophet forecaster not available. Please install prophet.")
        
        self.prophet_forecaster = ProphetForecaster(
            seasonality_mode=seasonality_mode,
            changepoint_prior_scale=changepoint_prior_scale,
            include_indian_holidays=include_indian_holidays,
            yearly_seasonality=yearly_seasonality,
            weekly_seasonality=weekly_seasonality,
            daily_seasonality=False
        )
        self.training_info = None
    
    def fit(self, data: pd.DataFrame, target_column: str = 'close') -> None:
        """Train the Prophet model."""
        try:
            if target_column not in data.columns:
                raise ModelTrainingError(f"Target column '{target_column}' not found in data")
            
            # Train the Prophet forecaster
            self.training_info = self.prophet_forecaster.fit(data, target_column)
            self.is_trained = True
            
        except Exception as e:
            raise ModelTrainingError(f"Failed to train Prophet model: {str(e)}")
    
    def predict(self, horizon: int) -> Tuple[List[float], Dict[str, List[float]]]:
        """Generate predictions using Prophet."""
        if not self.is_trained:
            raise ForecastingError("Model must be trained before making predictions")
        
        try:
            predictions, confidence_intervals = self.prophet_forecaster.predict(horizon)
            return predictions, confidence_intervals
            
        except Exception as e:
            raise ForecastingError(f"Prophet prediction failed: {str(e)}")
    
    def evaluate(self, test_data: pd.DataFrame, target_column: str = 'close') -> Dict[str, float]:
        """Evaluate Prophet model performance."""
        try:
            if not self.is_trained:
                return {'mae': float('inf'), 'rmse': float('inf'), 'r2': -1.0, 'accuracy': 0.0}
            
            metrics = self.prophet_forecaster.evaluate(test_data, target_column)
            return metrics
            
        except Exception as e:
            return {'mae': float('inf'), 'rmse': float('inf'), 'r2': -1.0, 'accuracy': 0.0}
    
    def get_training_info(self) -> Optional[Dict[str, Any]]:
        """Get training information including changepoints and seasonality."""
        return self.training_info
    
    def get_model_info(self) -> Dict[str, Any]:
        """Get detailed model information."""
        return self.prophet_forecaster.get_model_info()
    
    def get_changepoint_analysis(self) -> Dict[str, Any]:
        """Get changepoint detection analysis."""
        return self.prophet_forecaster.get_changepoint_analysis()
    
    def get_seasonality_analysis(self) -> Dict[str, Any]:
        """Get seasonality detection analysis."""
        return self.prophet_forecaster.get_seasonality_analysis()
    
    def get_holiday_impact(self) -> Dict[str, Any]:
        """Get holiday impact analysis."""
        return self.prophet_forecaster.get_holiday_impact()


class LSTMModel(TimeSeriesModel):
    """LSTM neural network model wrapper for time series forecasting."""
    
    def __init__(self, sequence_length: int = 60, hidden_size: int = 64,
                 num_layers: int = 2, dropout: float = 0.2, 
                 learning_rate: float = 0.001, batch_size: int = 32,
                 epochs: int = 100, early_stopping_patience: int = 10):
        """Initialize LSTM model wrapper.
        
        Args:
            sequence_length: Length of input sequences (lookback window)
            hidden_size: Number of hidden units in LSTM layers
            num_layers: Number of stacked LSTM layers
            dropout: Dropout rate for regularization
            learning_rate: Learning rate for optimizer
            batch_size: Batch size for training
            epochs: Maximum number of training epochs
            early_stopping_patience: Patience for early stopping
        """
        super().__init__("LSTM Neural Network")
        
        if not LSTM_AVAILABLE:
            raise ModelTrainingError("LSTM forecaster not available. Please install PyTorch.")
        
        self.lstm_forecaster = LSTMForecaster(
            sequence_length=sequence_length,
            hidden_size=hidden_size,
            num_layers=num_layers,
            dropout=dropout,
            learning_rate=learning_rate,
            batch_size=batch_size,
            epochs=epochs,
            early_stopping_patience=early_stopping_patience
        )
        self.training_info = None
    
    def fit(self, data: pd.DataFrame, target_column: str = 'close') -> None:
        """Train the LSTM model."""
        try:
            if target_column not in data.columns:
                raise ModelTrainingError(f"Target column '{target_column}' not found in data")
            
            # Train the LSTM forecaster
            self.training_info = self.lstm_forecaster.fit(data, target_column)
            self.is_trained = True
            
        except Exception as e:
            raise ModelTrainingError(f"Failed to train LSTM model: {str(e)}")
    
    def predict(self, horizon: int) -> Tuple[List[float], Dict[str, List[float]]]:
        """Generate predictions using LSTM."""
        if not self.is_trained:
            raise ForecastingError("Model must be trained before making predictions")
        
        try:
            predictions, confidence_intervals = self.lstm_forecaster.predict(horizon)
            return predictions, confidence_intervals
            
        except Exception as e:
            raise ForecastingError(f"LSTM prediction failed: {str(e)}")
    
    def evaluate(self, test_data: pd.DataFrame, target_column: str = 'close') -> Dict[str, float]:
        """Evaluate LSTM model performance."""
        try:
            if not self.is_trained:
                return {'mae': float('inf'), 'rmse': float('inf'), 'r2': -1.0, 'accuracy': 0.0}
            
            metrics = self.lstm_forecaster.evaluate(test_data, target_column)
            return metrics
            
        except Exception as e:
            return {'mae': float('inf'), 'rmse': float('inf'), 'r2': -1.0, 'accuracy': 0.0}
    
    def get_training_info(self) -> Optional[Dict[str, Any]]:
        """Get training information including history and metrics."""
        return self.training_info
    
    def get_model_info(self) -> Dict[str, Any]:
        """Get detailed model information."""
        return self.lstm_forecaster.get_model_info()


class ModelEvaluator:
    """Evaluate and compare forecasting models."""
    
    @staticmethod
    def calculate_metrics(actual: List[float], predicted: List[float]) -> Dict[str, float]:
        """Calculate comprehensive evaluation metrics."""
        try:
            actual = np.array(actual)
            predicted = np.array(predicted)
            
            # Basic metrics
            mae = float(np.mean(np.abs(actual - predicted)))
            rmse = float(np.sqrt(np.mean((actual - predicted) ** 2)))
            
            # R² score
            ss_res = np.sum((actual - predicted) ** 2)
            ss_tot = np.sum((actual - np.mean(actual)) ** 2)
            r2 = 1 - (ss_res / ss_tot) if ss_tot != 0 else 0
            
            # Mean Absolute Percentage Error
            mape = float(np.mean(np.abs((actual - predicted) / actual)) * 100)
            
            # Directional accuracy (percentage of correct direction predictions)
            actual_direction = np.diff(actual) > 0
            predicted_direction = np.diff(predicted) > 0
            directional_accuracy = float(np.mean(actual_direction == predicted_direction)) if len(actual) > 1 else 0
            
            return {
                'mae': mae,
                'rmse': rmse,
                'r2': float(r2),
                'mape': mape,
                'directional_accuracy': directional_accuracy,
                'accuracy': max(0, min(1, r2))  # Normalized accuracy
            }
            
        except Exception as e:
            return {
                'mae': float('inf'),
                'rmse': float('inf'),
                'r2': -1.0,
                'mape': float('inf'),
                'directional_accuracy': 0.0,
                'accuracy': 0.0
            }


class PriceForecastingEngine:
    """Main forecasting engine for price prediction."""
    
    def __init__(self, model_dir: str = None):
        """Initialize forecasting engine."""
        self.model_dir = model_dir or settings.model_dir
        os.makedirs(self.model_dir, exist_ok=True)
        
        self.models = {}
        self.evaluator = ModelEvaluator()
        self.trained_symbols = set()
        
        # Initialize available models
        self._initialize_models()
    
    def _initialize_models(self):
        """Initialize available forecasting models."""
        try:
            # Always available models
            self.models['moving_average'] = SimpleMovingAverageModel()
            
            # Conditional models based on dependencies
            if SKLEARN_AVAILABLE:
                self.models['random_forest'] = RandomForestModel()
            
            # Prophet model (requires prophet library)
            if PROPHET_AVAILABLE:
                self.models['prophet'] = ProphetModel(
                    seasonality_mode='multiplicative',
                    changepoint_prior_scale=0.05,
                    include_indian_holidays=True,
                    yearly_seasonality=True,
                    weekly_seasonality=True
                )
            
            # LSTM model (requires PyTorch)
            if LSTM_AVAILABLE:
                self.models['lstm'] = LSTMModel(
                    sequence_length=30,  # Reduced from 60 to work with smaller datasets
                    hidden_size=64,
                    num_layers=2,
                    dropout=0.2,
                    learning_rate=0.001,
                    batch_size=16,  # Reduced batch size for smaller datasets
                    epochs=50,  # Reduced epochs for faster training
                    early_stopping_patience=10
                )
            
        except Exception as e:
            print(f"Warning: Some models could not be initialized: {str(e)}")
    
    def get_available_models(self) -> List[str]:
        """Get list of available model names."""
        return list(self.models.keys())
    
    def train_model(self, data: pd.DataFrame, target_column: str = 'close', 
                   model_name: str = 'moving_average', symbol: str = 'UNKNOWN') -> None:
        """Train a specific model on historical data."""
        try:
            if model_name not in self.models:
                raise ModelTrainingError(f"Model '{model_name}' not available. Available models: {list(self.models.keys())}")
            
            if target_column not in data.columns:
                raise ModelTrainingError(f"Target column '{target_column}' not found in data")
            
            if len(data) < 50:  # Minimum data requirement
                raise ModelTrainingError("Insufficient data for training (minimum 50 records required)")
            
            # Train the model
            model = self.models[model_name]
            model.fit(data, target_column)
            
            # Save trained model
            self._save_model(model, symbol, model_name)
            self.trained_symbols.add(symbol)
            
        except Exception as e:
            raise ModelTrainingError(f"Failed to train model '{model_name}': {str(e)}")
    
    def predict_prices(self, symbol: str, horizon: int = None, 
                      model_name: str = 'moving_average') -> ForecastResult:
        """Generate price predictions for specified horizon."""
        try:
            horizon = horizon or settings.default_forecast_horizon
            
            if model_name not in self.models:
                raise ForecastingError(f"Model '{model_name}' not available")
            
            model = self.models[model_name]
            if not model.is_trained:
                # Try to load saved model
                if not self._load_model(model, symbol, model_name):
                    raise ForecastingError(f"Model '{model_name}' for symbol '{symbol}' is not trained")
            
            # Generate predictions
            predictions, confidence_intervals = model.predict(horizon)
            
            # Create result
            result = ForecastResult(
                symbol=symbol,
                forecast_horizon=horizon,
                predicted_prices=predictions,
                confidence_intervals=confidence_intervals,
                model_metrics={'model_name': model_name},
                timestamp=datetime.now()
            )
            
            return result
            
        except Exception as e:
            raise ForecastingError(f"Failed to generate predictions: {str(e)}")
    
    def get_confidence_intervals(self, predictions: List[float], 
                               confidence_level: float = None) -> Tuple[List[float], List[float]]:
        """Calculate confidence intervals for predictions."""
        confidence_level = confidence_level or settings.confidence_level
        
        try:
            # Simple confidence interval calculation
            alpha = 1 - confidence_level
            margin = alpha / 2
            
            lower_bounds = [p * (1 - margin) for p in predictions]
            upper_bounds = [p * (1 + margin) for p in predictions]
            
            return lower_bounds, upper_bounds
            
        except Exception as e:
            # Return predictions as bounds if calculation fails
            return predictions.copy(), predictions.copy()
    
    def evaluate_model(self, test_data: pd.DataFrame, symbol: str, 
                      target_column: str = 'close', model_name: str = 'moving_average') -> Dict[str, float]:
        """Evaluate model performance on test data."""
        try:
            if model_name not in self.models:
                raise ForecastingError(f"Model '{model_name}' not available")
            
            model = self.models[model_name]
            if not model.is_trained:
                if not self._load_model(model, symbol, model_name):
                    raise ForecastingError(f"Model '{model_name}' for symbol '{symbol}' is not trained")
            
            # Evaluate model
            metrics = model.evaluate(test_data, target_column)
            
            return metrics
            
        except Exception as e:
            return {'mae': float('inf'), 'rmse': float('inf'), 'r2': -1.0, 'accuracy': 0.0}
    
    def _save_model(self, model: TimeSeriesModel, symbol: str, model_name: str):
        """Save trained model to disk."""
        try:
            # LSTM models use their own checkpoint system
            if isinstance(model, LSTMModel):
                model.lstm_forecaster.save_model(symbol)
                return
            
            # For other models, use pickle
            model_path = os.path.join(self.model_dir, f"{symbol}_{model_name}.pkl")
            
            model_data = {
                'model': model,
                'symbol': symbol,
                'model_name': model_name,
                'timestamp': datetime.now().isoformat()
            }
            
            with open(model_path, 'wb') as f:
                pickle.dump(model_data, f)
                
        except Exception as e:
            print(f"Warning: Could not save model: {str(e)}")
    
    def _load_model(self, model: TimeSeriesModel, symbol: str, model_name: str) -> bool:
        """Load trained model from disk."""
        try:
            # LSTM models use their own checkpoint system
            if isinstance(model, LSTMModel):
                return model.lstm_forecaster.load_model(symbol)
            
            # For other models, use pickle
            model_path = os.path.join(self.model_dir, f"{symbol}_{model_name}.pkl")
            
            if not os.path.exists(model_path):
                return False
            
            with open(model_path, 'rb') as f:
                model_data = pickle.load(f)
            
            # Update model with loaded data
            loaded_model = model_data['model']
            model.is_trained = loaded_model.is_trained
            model.model = loaded_model.model
            model.scaler = loaded_model.scaler
            
            # Copy model-specific attributes
            if hasattr(loaded_model, 'historical_data'):
                model.historical_data = loaded_model.historical_data
            if hasattr(loaded_model, 'last_values'):
                model.last_values = loaded_model.last_values
            if hasattr(loaded_model, 'last_data'):
                model.last_data = loaded_model.last_data
            
            return True
            
        except Exception as e:
            print(f"Warning: Could not load model: {str(e)}")
            return False
    
    def get_model_info(self) -> Dict[str, Any]:
        """Get information about available models and their status."""
        info = {
            'available_models': list(self.models.keys()),
            'trained_symbols': list(self.trained_symbols),
            'dependencies': {
                'sklearn_available': SKLEARN_AVAILABLE,
                'prophet_available': PROPHET_AVAILABLE,
                'lstm_available': LSTM_AVAILABLE
            },
            'model_details': {}
        }
        
        for name, model in self.models.items():
            info['model_details'][name] = {
                'name': model.name,
                'is_trained': model.is_trained,
                'type': type(model).__name__
            }
        
        return info