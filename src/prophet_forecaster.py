"""Facebook Prophet implementation for time series forecasting with seasonality.

This module provides Prophet-based forecasting capabilities with automatic seasonality
detection, holiday calendar support for Indian markets, and changepoint detection
for the AI Retail Intelligence Platform.
"""

import os
import json
import numpy as np
import pandas as pd
from typing import Dict, List, Optional, Tuple, Any
from datetime import datetime, timedelta
import warnings
warnings.filterwarnings('ignore')

try:
    from prophet import Prophet
    from prophet.diagnostics import cross_validation, performance_metrics
    PROPHET_AVAILABLE = True
except ImportError:
    PROPHET_AVAILABLE = False
    print("Warning: Prophet not available. Install prophet to enable Prophet forecasting.")

from src.exceptions import ModelTrainingError, ForecastingError
from src.config import settings


class IndianHolidayCalendar:
    """Indian market holiday calendar for precious metals trading."""
    
    @staticmethod
    def get_indian_holidays(start_year: int = 2020, end_year: int = 2027) -> pd.DataFrame:
        """Get Indian market holidays for precious metals trading.
        
        Args:
            start_year: Start year for holiday calendar
            end_year: End year for holiday calendar
            
        Returns:
            DataFrame with columns: holiday, ds, lower_window, upper_window
        """
        holidays = []
        
        # Major Indian festivals affecting precious metals markets
        # Note: These are approximate dates; actual dates vary by lunar calendar
        
        for year in range(start_year, end_year + 1):
            # Diwali (major gold buying season) - October/November
            # Approximate dates, actual dates vary
            diwali_dates = {
                2020: '2020-11-14',
                2021: '2021-11-04',
                2022: '2022-10-24',
                2023: '2023-11-12',
                2024: '2024-11-01',
                2025: '2025-10-20',
                2026: '2026-11-08',
                2027: '2027-10-29'
            }
            
            if year in diwali_dates:
                holidays.append({
                    'holiday': 'Diwali',
                    'ds': pd.to_datetime(diwali_dates[year]),
                    'lower_window': -5,  # 5 days before
                    'upper_window': 2    # 2 days after
                })
            
            # Dhanteras (2 days before Diwali) - major gold buying day
            if year in diwali_dates:
                dhanteras_date = pd.to_datetime(diwali_dates[year]) - timedelta(days=2)
                holidays.append({
                    'holiday': 'Dhanteras',
                    'ds': dhanteras_date,
                    'lower_window': -2,
                    'upper_window': 1
                })
            
            # Akshaya Tritiya (April/May) - auspicious for gold buying
            akshaya_tritiya_dates = {
                2020: '2020-04-26',
                2021: '2021-05-14',
                2022: '2022-05-03',
                2023: '2023-04-22',
                2024: '2024-05-10',
                2025: '2025-04-29',
                2026: '2026-04-18',
                2027: '2027-05-08'
            }
            
            if year in akshaya_tritiya_dates:
                holidays.append({
                    'holiday': 'Akshaya Tritiya',
                    'ds': pd.to_datetime(akshaya_tritiya_dates[year]),
                    'lower_window': -3,
                    'upper_window': 1
                })
            
            # Wedding Season (November to February) - high gold demand
            holidays.append({
                'holiday': 'Wedding Season Start',
                'ds': pd.to_datetime(f'{year}-11-15'),
                'lower_window': 0,
                'upper_window': 90  # 3 months
            })
            
            # Pushya Nakshatra (monthly auspicious day for gold)
            # Approximate monthly occurrence
            for month in range(1, 13):
                try:
                    pushya_date = pd.to_datetime(f'{year}-{month:02d}-15')
                    holidays.append({
                        'holiday': 'Pushya Nakshatra',
                        'ds': pushya_date,
                        'lower_window': 0,
                        'upper_window': 1
                    })
                except:
                    pass
            
            # Navratri (September/October) - festival season
            navratri_dates = {
                2020: '2020-10-17',
                2021: '2021-10-07',
                2022: '2022-09-26',
                2023: '2023-10-15',
                2024: '2024-10-03',
                2025: '2025-09-22',
                2026: '2026-10-12',
                2027: '2027-10-02'
            }
            
            if year in navratri_dates:
                holidays.append({
                    'holiday': 'Navratri',
                    'ds': pd.to_datetime(navratri_dates[year]),
                    'lower_window': 0,
                    'upper_window': 9  # 9 days
                })
        
        return pd.DataFrame(holidays)


class ProphetForecaster:
    """Facebook Prophet-based time series forecaster with Indian market support."""
    
    def __init__(self, 
                 seasonality_mode: str = 'multiplicative',
                 changepoint_prior_scale: float = 0.05,
                 seasonality_prior_scale: float = 10.0,
                 holidays_prior_scale: float = 10.0,
                 yearly_seasonality: bool = True,
                 weekly_seasonality: bool = True,
                 daily_seasonality: bool = False,
                 include_indian_holidays: bool = True,
                 growth: str = 'linear',
                 changepoint_range: float = 0.8,
                 n_changepoints: int = 25,
                 interval_width: float = 0.95,
                 mcmc_samples: int = 0):
        """Initialize Prophet forecaster.
        
        Args:
            seasonality_mode: 'additive' or 'multiplicative' seasonality
            changepoint_prior_scale: Flexibility of trend changes (higher = more flexible)
            seasonality_prior_scale: Strength of seasonality (higher = stronger)
            holidays_prior_scale: Strength of holiday effects (higher = stronger)
            yearly_seasonality: Enable yearly seasonality
            weekly_seasonality: Enable weekly seasonality
            daily_seasonality: Enable daily seasonality
            include_indian_holidays: Include Indian market holiday calendar
            growth: 'linear' or 'logistic' growth
            changepoint_range: Proportion of history for changepoint detection
            n_changepoints: Number of potential changepoints
            interval_width: Width of uncertainty intervals (0.95 = 95%)
            mcmc_samples: Number of MCMC samples for full Bayesian inference (0 = MAP)
        """
        if not PROPHET_AVAILABLE:
            raise ModelTrainingError("Prophet is not available. Please install prophet.")
        
        self.seasonality_mode = seasonality_mode
        self.changepoint_prior_scale = changepoint_prior_scale
        self.seasonality_prior_scale = seasonality_prior_scale
        self.holidays_prior_scale = holidays_prior_scale
        self.yearly_seasonality = yearly_seasonality
        self.weekly_seasonality = weekly_seasonality
        self.daily_seasonality = daily_seasonality
        self.include_indian_holidays = include_indian_holidays
        self.growth = growth
        self.changepoint_range = changepoint_range
        self.n_changepoints = n_changepoints
        self.interval_width = interval_width
        self.mcmc_samples = mcmc_samples
        
        self.model = None
        self.is_trained = False
        self.training_data = None
        self.forecast_result = None
        self.changepoints = None
        self.seasonality_components = None
        
        # Indian holiday calendar
        self.indian_holidays = None
        if self.include_indian_holidays:
            self.indian_holidays = IndianHolidayCalendar.get_indian_holidays()
        
        print(f"Prophet Forecaster initialized with {seasonality_mode} seasonality")
    
    def _prepare_data(self, data: pd.DataFrame, target_column: str) -> pd.DataFrame:
        """Prepare data in Prophet format (ds, y columns).
        
        Args:
            data: Input DataFrame with date index or date column
            target_column: Column name for target variable
            
        Returns:
            DataFrame with 'ds' (date) and 'y' (target) columns
        """
        try:
            df = data.copy()
            
            # Ensure we have a date column
            if 'date' in df.columns:
                df['ds'] = pd.to_datetime(df['date'])
            elif isinstance(df.index, pd.DatetimeIndex):
                df['ds'] = df.index
            else:
                raise ModelTrainingError("Data must have a date column or DatetimeIndex")
            
            # Set target column
            if target_column not in df.columns:
                raise ModelTrainingError(f"Target column '{target_column}' not found in data")
            
            df['y'] = df[target_column]
            
            # Select only required columns
            prophet_df = df[['ds', 'y']].copy()
            
            # Remove any NaN values
            prophet_df = prophet_df.dropna()
            
            # Sort by date
            prophet_df = prophet_df.sort_values('ds').reset_index(drop=True)
            
            return prophet_df
            
        except Exception as e:
            raise ModelTrainingError(f"Data preparation failed: {str(e)}")
    
    def fit(self, data: pd.DataFrame, target_column: str = 'close') -> Dict[str, Any]:
        """Train the Prophet model on historical data.
        
        Args:
            data: Historical price data
            target_column: Column name for target variable
            
        Returns:
            Training information and diagnostics
        """
        try:
            if len(data) < 30:
                raise ModelTrainingError(
                    f"Insufficient data for training. Need at least 30 records, got {len(data)}"
                )
            
            # Prepare data
            self.training_data = self._prepare_data(data, target_column)
            
            print(f"Training Prophet model on {len(self.training_data)} data points...")
            
            # Initialize Prophet model
            self.model = Prophet(
                growth=self.growth,
                changepoint_range=self.changepoint_range,
                n_changepoints=self.n_changepoints,
                changepoint_prior_scale=self.changepoint_prior_scale,
                seasonality_mode=self.seasonality_mode,
                seasonality_prior_scale=self.seasonality_prior_scale,
                holidays_prior_scale=self.holidays_prior_scale,
                yearly_seasonality=self.yearly_seasonality,
                weekly_seasonality=self.weekly_seasonality,
                daily_seasonality=self.daily_seasonality,
                interval_width=self.interval_width,
                mcmc_samples=self.mcmc_samples
            )
            
            # Add Indian holidays if enabled
            if self.include_indian_holidays and self.indian_holidays is not None:
                self.model.holidays = self.indian_holidays
                print(f"Added {len(self.indian_holidays)} Indian market holidays")
            
            # Add custom seasonalities for Indian market patterns
            # Monthly seasonality (salary cycle effects)
            self.model.add_seasonality(
                name='monthly',
                period=30.5,
                fourier_order=5
            )
            
            # Quarterly seasonality (festival seasons)
            self.model.add_seasonality(
                name='quarterly',
                period=91.25,
                fourier_order=8
            )
            
            # Fit the model
            self.model.fit(self.training_data)
            
            self.is_trained = True
            
            # Extract changepoints
            self.changepoints = self._extract_changepoints()
            
            # Extract seasonality components
            self.seasonality_components = self._extract_seasonality_components()
            
            print("Training completed successfully")
            
            return {
                'training_samples': len(self.training_data),
                'changepoints_detected': len(self.changepoints) if self.changepoints is not None else 0,
                'seasonality_components': list(self.seasonality_components.keys()) if self.seasonality_components else [],
                'model_parameters': {
                    'seasonality_mode': self.seasonality_mode,
                    'changepoint_prior_scale': self.changepoint_prior_scale,
                    'n_changepoints': self.n_changepoints
                }
            }
            
        except Exception as e:
            raise ModelTrainingError(f"Failed to train Prophet model: {str(e)}")
    
    def predict(self, horizon: int) -> Tuple[List[float], Dict[str, List[float]]]:
        """Generate predictions for specified horizon.
        
        Args:
            horizon: Number of time steps to predict
            
        Returns:
            Tuple of (predictions, confidence_intervals)
        """
        if not self.is_trained:
            raise ForecastingError("Model must be trained before making predictions")
        
        try:
            # Create future dataframe
            future = self.model.make_future_dataframe(periods=horizon, freq='D')
            
            # Make predictions
            forecast = self.model.predict(future)
            
            # Store full forecast for analysis
            self.forecast_result = forecast
            
            # Extract predictions for the forecast horizon
            predictions = forecast['yhat'].tail(horizon).tolist()
            
            # Extract confidence intervals
            lower_bounds = forecast['yhat_lower'].tail(horizon).tolist()
            upper_bounds = forecast['yhat_upper'].tail(horizon).tolist()
            
            confidence_intervals = {
                'lower': lower_bounds,
                'upper': upper_bounds
            }
            
            return predictions, confidence_intervals
            
        except Exception as e:
            raise ForecastingError(f"Prediction failed: {str(e)}")
    
    def evaluate(self, test_data: pd.DataFrame, target_column: str = 'close') -> Dict[str, float]:
        """Evaluate model performance on test data.
        
        Args:
            test_data: Test dataset
            target_column: Column name for target variable
            
        Returns:
            Dictionary of evaluation metrics
        """
        if not self.is_trained:
            return {'mae': float('inf'), 'rmse': float('inf'), 'r2': -1.0, 'accuracy': 0.0}
        
        try:
            # Prepare test data
            test_df = self._prepare_data(test_data, target_column)
            
            if len(test_df) == 0:
                return {'mae': float('inf'), 'rmse': float('inf'), 'r2': -1.0, 'accuracy': 0.0}
            
            # Make predictions for test period
            forecast = self.model.predict(test_df[['ds']])
            
            # Extract actual and predicted values
            actual = test_df['y'].values
            predicted = forecast['yhat'].values
            
            # Calculate metrics
            mae = float(np.mean(np.abs(actual - predicted)))
            rmse = float(np.sqrt(np.mean((actual - predicted) ** 2)))
            
            # R² score
            ss_res = np.sum((actual - predicted) ** 2)
            ss_tot = np.sum((actual - np.mean(actual)) ** 2)
            r2 = 1 - (ss_res / ss_tot) if ss_tot != 0 else 0
            
            # Mean Absolute Percentage Error
            mape = float(np.mean(np.abs((actual - predicted) / actual)) * 100)
            
            # Coverage (percentage of actuals within confidence intervals)
            lower = forecast['yhat_lower'].values
            upper = forecast['yhat_upper'].values
            coverage = float(np.mean((actual >= lower) & (actual <= upper)))
            
            return {
                'mae': mae,
                'rmse': rmse,
                'r2': float(r2),
                'mape': mape,
                'coverage': coverage,
                'accuracy': max(0, min(1, r2))
            }
            
        except Exception as e:
            print(f"Evaluation error: {str(e)}")
            return {'mae': float('inf'), 'rmse': float('inf'), 'r2': -1.0, 'accuracy': 0.0}
    
    def _extract_changepoints(self) -> Optional[pd.DataFrame]:
        """Extract detected changepoints from the model.
        
        Returns:
            DataFrame with changepoint dates and trend changes
        """
        try:
            if self.model is None or not self.is_trained:
                return None
            
            # Get changepoints
            changepoints = self.model.changepoints
            
            if len(changepoints) == 0:
                return None
            
            # Get trend changes at changepoints
            deltas = self.model.params['delta'].mean(axis=0)
            
            changepoint_df = pd.DataFrame({
                'date': changepoints,
                'trend_change': deltas
            })
            
            # Filter significant changepoints (absolute change > threshold)
            threshold = np.abs(deltas).mean()
            significant = changepoint_df[np.abs(changepoint_df['trend_change']) > threshold]
            
            return significant.sort_values('date').reset_index(drop=True)
            
        except Exception as e:
            print(f"Warning: Could not extract changepoints: {str(e)}")
            return None
    
    def _extract_seasonality_components(self) -> Optional[Dict[str, Any]]:
        """Extract seasonality components from the model.
        
        Returns:
            Dictionary with seasonality information
        """
        try:
            if self.forecast_result is None:
                return None
            
            components = {}
            
            # Extract available seasonality components
            if 'yearly' in self.forecast_result.columns:
                yearly_strength = float(self.forecast_result['yearly'].std())
                components['yearly'] = {
                    'strength': yearly_strength,
                    'enabled': True
                }
            
            if 'weekly' in self.forecast_result.columns:
                weekly_strength = float(self.forecast_result['weekly'].std())
                components['weekly'] = {
                    'strength': weekly_strength,
                    'enabled': True
                }
            
            if 'monthly' in self.forecast_result.columns:
                monthly_strength = float(self.forecast_result['monthly'].std())
                components['monthly'] = {
                    'strength': monthly_strength,
                    'enabled': True
                }
            
            if 'quarterly' in self.forecast_result.columns:
                quarterly_strength = float(self.forecast_result['quarterly'].std())
                components['quarterly'] = {
                    'strength': quarterly_strength,
                    'enabled': True
                }
            
            return components
            
        except Exception as e:
            print(f"Warning: Could not extract seasonality components: {str(e)}")
            return None
    
    def get_changepoint_analysis(self) -> Dict[str, Any]:
        """Get detailed changepoint analysis.
        
        Returns:
            Dictionary with changepoint information
        """
        if self.changepoints is None or len(self.changepoints) == 0:
            return {
                'changepoints_detected': 0,
                'significant_changes': []
            }
        
        significant_changes = []
        for _, row in self.changepoints.iterrows():
            significant_changes.append({
                'date': row['date'].strftime('%Y-%m-%d'),
                'trend_change': float(row['trend_change']),
                'direction': 'increase' if row['trend_change'] > 0 else 'decrease'
            })
        
        return {
            'changepoints_detected': len(self.changepoints),
            'significant_changes': significant_changes
        }
    
    def get_seasonality_analysis(self) -> Dict[str, Any]:
        """Get detailed seasonality analysis.
        
        Returns:
            Dictionary with seasonality information
        """
        if self.seasonality_components is None:
            return {
                'seasonality_detected': False,
                'components': {}
            }
        
        return {
            'seasonality_detected': True,
            'components': self.seasonality_components,
            'mode': self.seasonality_mode
        }
    
    def get_holiday_impact(self) -> Dict[str, Any]:
        """Get holiday impact analysis.
        
        Returns:
            Dictionary with holiday impact information
        """
        if not self.include_indian_holidays or self.forecast_result is None:
            return {
                'holidays_included': False,
                'impact': {}
            }
        
        try:
            # Extract holiday effects from forecast
            if 'holidays' in self.forecast_result.columns:
                holiday_impact = float(self.forecast_result['holidays'].std())
                
                return {
                    'holidays_included': True,
                    'total_holidays': len(self.indian_holidays),
                    'impact_strength': holiday_impact,
                    'major_holidays': ['Diwali', 'Dhanteras', 'Akshaya Tritiya', 'Wedding Season']
                }
            
            return {
                'holidays_included': True,
                'total_holidays': len(self.indian_holidays),
                'impact': 'Holiday effects incorporated in model'
            }
            
        except Exception as e:
            return {
                'holidays_included': True,
                'error': str(e)
            }
    
    def get_model_info(self) -> Dict[str, Any]:
        """Get comprehensive model information.
        
        Returns:
            Dictionary with model configuration and analysis
        """
        info = {
            'model_type': 'Prophet',
            'is_trained': self.is_trained,
            'configuration': {
                'seasonality_mode': self.seasonality_mode,
                'growth': self.growth,
                'changepoint_prior_scale': self.changepoint_prior_scale,
                'seasonality_prior_scale': self.seasonality_prior_scale,
                'holidays_prior_scale': self.holidays_prior_scale,
                'n_changepoints': self.n_changepoints,
                'interval_width': self.interval_width
            },
            'features': {
                'yearly_seasonality': self.yearly_seasonality,
                'weekly_seasonality': self.weekly_seasonality,
                'daily_seasonality': self.daily_seasonality,
                'monthly_seasonality': True,
                'quarterly_seasonality': True,
                'indian_holidays': self.include_indian_holidays
            }
        }
        
        if self.is_trained:
            info['training_samples'] = len(self.training_data) if self.training_data is not None else 0
            info['changepoint_analysis'] = self.get_changepoint_analysis()
            info['seasonality_analysis'] = self.get_seasonality_analysis()
            info['holiday_impact'] = self.get_holiday_impact()
        
        return info
