"""Data loading and preprocessing for AI Retail Intelligence Platform."""

import os
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass

from src.config import settings
from src.exceptions import DataLoadingError, DataValidationError
from src.logger import app_logger


@dataclass
class PriceData:
    """Data model for price information."""
    timestamp: datetime
    open_price: float
    high_price: float
    low_price: float
    close_price: float
    volume: Optional[int] = None
    symbol: str = ""
    
    def validate(self) -> bool:
        """Validate price data integrity."""
        return (
            self.high_price >= self.low_price and 
            self.high_price >= self.open_price and 
            self.high_price >= self.close_price and
            self.low_price <= self.open_price and 
            self.low_price <= self.close_price and
            all(price > 0 for price in [self.open_price, self.high_price, self.low_price, self.close_price])
        )


class PriceDataValidator:
    """Validates price data format and integrity."""
    
    @staticmethod
    def validate_dataframe(df: pd.DataFrame, required_columns: List[str]) -> bool:
        """Validate DataFrame structure and content."""
        try:
            # Check required columns
            missing_columns = set(required_columns) - set(df.columns)
            if missing_columns:
                raise DataValidationError(f"Missing required columns: {missing_columns}")
            
            # Check for empty DataFrame
            if df.empty:
                raise DataValidationError("DataFrame is empty")
            
            # Check for null values in critical columns
            price_columns = ['open', 'high', 'low', 'close']
            for col in price_columns:
                if col in df.columns and df[col].isnull().any():
                    app_logger.warning(f"Found null values in {col} column")
            
            # Validate price relationships
            if all(col in df.columns for col in price_columns):
                invalid_rows = ~(
                    (df['high'] >= df['low']) &
                    (df['high'] >= df['open']) &
                    (df['high'] >= df['close']) &
                    (df['low'] <= df['open']) &
                    (df['low'] <= df['close']) &
                    (df[price_columns] > 0).all(axis=1)
                )
                
                if invalid_rows.any():
                    app_logger.warning(f"Found {invalid_rows.sum()} rows with invalid price relationships")
                    return False
            
            return True
            
        except Exception as e:
            raise DataValidationError(f"Data validation failed: {str(e)}")
    
    @staticmethod
    def validate_date_column(df: pd.DataFrame, date_column: str = 'date') -> pd.DataFrame:
        """Validate and convert date column."""
        try:
            if date_column not in df.columns:
                raise DataValidationError(f"Date column '{date_column}' not found")
            
            # Convert to datetime
            df[date_column] = pd.to_datetime(df[date_column])
            
            # Check for duplicate dates
            if df[date_column].duplicated().any():
                app_logger.warning("Found duplicate dates in data")
            
            # Sort by date
            df = df.sort_values(date_column).reset_index(drop=True)
            
            return df
            
        except Exception as e:
            raise DataValidationError(f"Date validation failed: {str(e)}")


class DataPreprocessor:
    """Handles data cleaning, normalization, and feature engineering."""
    
    @staticmethod
    def clean_data(df: pd.DataFrame) -> pd.DataFrame:
        """Clean and preprocess price data."""
        try:
            # Remove duplicates
            df = df.drop_duplicates()
            
            # Handle missing values
            price_columns = ['open', 'high', 'low', 'close']
            for col in price_columns:
                if col in df.columns:
                    # Forward fill missing values
                    df[col] = df[col].fillna(method='ffill')
                    # Backward fill remaining missing values
                    df[col] = df[col].fillna(method='bfill')
            
            # Remove rows with all NaN values
            df = df.dropna(how='all')
            
            return df
            
        except Exception as e:
            raise DataLoadingError(f"Data cleaning failed: {str(e)}")
    
    @staticmethod
    def add_technical_indicators(df: pd.DataFrame) -> pd.DataFrame:
        """Add technical indicators for analysis."""
        try:
            if 'close' not in df.columns:
                return df
            
            # Moving averages
            df['ma_7'] = df['close'].rolling(window=7).mean()
            df['ma_30'] = df['close'].rolling(window=30).mean()
            
            # Volatility (rolling standard deviation)
            df['volatility'] = df['close'].rolling(window=30).std()
            
            # Price change
            df['price_change'] = df['close'].pct_change()
            
            # Daily range
            if all(col in df.columns for col in ['high', 'low']):
                df['daily_range'] = df['high'] - df['low']
                df['daily_range_pct'] = df['daily_range'] / df['close']
            
            return df
            
        except Exception as e:
            app_logger.warning(f"Failed to add technical indicators: {str(e)}")
            return df
    
    @staticmethod
    def normalize_data(df: pd.DataFrame, columns: List[str]) -> pd.DataFrame:
        """Normalize specified columns."""
        try:
            for col in columns:
                if col in df.columns:
                    df[f'{col}_normalized'] = (df[col] - df[col].mean()) / df[col].std()
            
            return df
            
        except Exception as e:
            app_logger.warning(f"Data normalization failed: {str(e)}")
            return df


class DataLoader:
    """Main class for loading and preprocessing CSV data."""
    
    def __init__(self, data_dir: str = None):
        """Initialize DataLoader with data directory."""
        self.data_dir = data_dir or settings.data_dir
        self.validator = PriceDataValidator()
        self.preprocessor = DataPreprocessor()
        
        # Ensure data directory exists
        os.makedirs(self.data_dir, exist_ok=True)
        
        app_logger.info(f"DataLoader initialized with data directory: {self.data_dir}")
    
    def load_gold_prices(self, file_path: str = None) -> pd.DataFrame:
        """Load gold price data from CSV file."""
        try:
            file_path = file_path or os.path.join(self.data_dir, "gold_prices.csv")
            
            if not os.path.exists(file_path):
                raise DataLoadingError(f"Gold price file not found: {file_path}")
            
            app_logger.info(f"Loading gold price data from: {file_path}")
            
            df = pd.read_csv(file_path)
            
            # Standardize column names
            df.columns = df.columns.str.lower().str.strip()
            
            # Validate required columns
            required_columns = ['date', 'open', 'high', 'low', 'close']
            self.validator.validate_dataframe(df, required_columns)
            
            # Validate and convert date column
            df = self.validator.validate_date_column(df)
            
            # Clean and preprocess data
            df = self.preprocessor.clean_data(df)
            df = self.preprocessor.add_technical_indicators(df)
            
            # Add symbol column
            df['symbol'] = 'GOLD'
            
            app_logger.info(f"Successfully loaded {len(df)} gold price records")
            return df
            
        except Exception as e:
            raise DataLoadingError(f"Failed to load gold prices: {str(e)}")
    
    def load_silver_prices(self, file_path: str = None) -> pd.DataFrame:
        """Load silver price data from CSV file."""
        try:
            file_path = file_path or os.path.join(self.data_dir, "silver_prices.csv")
            
            if not os.path.exists(file_path):
                raise DataLoadingError(f"Silver price file not found: {file_path}")
            
            app_logger.info(f"Loading silver price data from: {file_path}")
            
            df = pd.read_csv(file_path)
            
            # Standardize column names
            df.columns = df.columns.str.lower().str.strip()
            
            # Validate required columns
            required_columns = ['date', 'open', 'high', 'low', 'close']
            self.validator.validate_dataframe(df, required_columns)
            
            # Validate and convert date column
            df = self.validator.validate_date_column(df)
            
            # Clean and preprocess data
            df = self.preprocessor.clean_data(df)
            df = self.preprocessor.add_technical_indicators(df)
            
            # Add symbol column
            df['symbol'] = 'SILVER'
            
            app_logger.info(f"Successfully loaded {len(df)} silver price records")
            return df
            
        except Exception as e:
            raise DataLoadingError(f"Failed to load silver prices: {str(e)}")
    
    def load_etf_prices(self, file_path: str = None) -> pd.DataFrame:
        """Load ETF price data from CSV file."""
        try:
            file_path = file_path or os.path.join(self.data_dir, "etf_prices.csv")
            
            if not os.path.exists(file_path):
                raise DataLoadingError(f"ETF price file not found: {file_path}")
            
            app_logger.info(f"Loading ETF price data from: {file_path}")
            
            df = pd.read_csv(file_path)
            
            # Standardize column names
            df.columns = df.columns.str.lower().str.strip()
            
            # Validate required columns
            required_columns = ['date', 'open', 'high', 'low', 'close']
            self.validator.validate_dataframe(df, required_columns)
            
            # Validate and convert date column
            df = self.validator.validate_date_column(df)
            
            # Clean and preprocess data
            df = self.preprocessor.clean_data(df)
            df = self.preprocessor.add_technical_indicators(df)
            
            # Add symbol column if not present
            if 'symbol' not in df.columns:
                df['symbol'] = 'ETF'
            
            app_logger.info(f"Successfully loaded {len(df)} ETF price records")
            return df
            
        except Exception as e:
            raise DataLoadingError(f"Failed to load ETF prices: {str(e)}")
    
    def validate_price_data(self, data: pd.DataFrame) -> bool:
        """Validate price data format and integrity."""
        try:
            required_columns = ['date', 'open', 'high', 'low', 'close']
            return self.validator.validate_dataframe(data, required_columns)
        except Exception as e:
            app_logger.error(f"Price data validation failed: {str(e)}")
            return False
    
    def preprocess_data(self, data: pd.DataFrame) -> pd.DataFrame:
        """Preprocess data with cleaning and feature engineering."""
        try:
            # Clean data
            data = self.preprocessor.clean_data(data)
            
            # Add technical indicators
            data = self.preprocessor.add_technical_indicators(data)
            
            return data
            
        except Exception as e:
            raise DataLoadingError(f"Data preprocessing failed: {str(e)}")
    
    def load_all_data(self) -> Dict[str, pd.DataFrame]:
        """Load all available price data."""
        data = {}
        
        try:
            data['gold'] = self.load_gold_prices()
        except DataLoadingError as e:
            app_logger.warning(f"Could not load gold data: {str(e)}")
        
        try:
            data['silver'] = self.load_silver_prices()
        except DataLoadingError as e:
            app_logger.warning(f"Could not load silver data: {str(e)}")
        
        try:
            data['etf'] = self.load_etf_prices()
        except DataLoadingError as e:
            app_logger.warning(f"Could not load ETF data: {str(e)}")
        
        app_logger.info(f"Loaded data for {len(data)} asset types")
        return data
    
    def get_data_summary(self, data: pd.DataFrame) -> Dict[str, Any]:
        """Get summary statistics for price data."""
        try:
            summary = {
                'total_records': len(data),
                'date_range': {
                    'start': data['date'].min().strftime('%Y-%m-%d') if 'date' in data.columns else None,
                    'end': data['date'].max().strftime('%Y-%m-%d') if 'date' in data.columns else None
                },
                'price_statistics': {}
            }
            
            price_columns = ['open', 'high', 'low', 'close']
            for col in price_columns:
                if col in data.columns:
                    summary['price_statistics'][col] = {
                        'mean': float(data[col].mean()),
                        'std': float(data[col].std()),
                        'min': float(data[col].min()),
                        'max': float(data[col].max())
                    }
            
            return summary
            
        except Exception as e:
            app_logger.error(f"Failed to generate data summary: {str(e)}")
            return {}