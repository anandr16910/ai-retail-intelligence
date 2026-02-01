"""Generate realistic sample data for AI Retail Intelligence Platform."""

import csv
import random
import math
from datetime import datetime, timedelta
from typing import List, Tuple
import os


class SampleDataGenerator:
    """Generate realistic sample datasets for testing and demonstration."""
    
    def __init__(self, data_dir: str = "data"):
        """Initialize data generator."""
        self.data_dir = data_dir
        os.makedirs(self.data_dir, exist_ok=True)
    
    def generate_gold_prices(self, 
                           start_date: str = "2020-01-01",
                           end_date: str = "2024-01-01",
                           initial_price: float = 1800.0) -> List[dict]:
        """Generate realistic gold price data."""
        
        start = datetime.strptime(start_date, "%Y-%m-%d")
        end = datetime.strptime(end_date, "%Y-%m-%d")
        
        # Generate date range
        current_date = start
        dates = []
        while current_date <= end:
            dates.append(current_date)
            current_date += timedelta(days=1)
        
        n_days = len(dates)
        
        # Generate price movements with realistic patterns
        random.seed(42)  # For reproducible data
        
        data = []
        current_price = initial_price
        
        for i, date in enumerate(dates):
            # Add trend and seasonality
            trend_factor = 1 + (0.3 * i / n_days)  # 30% increase over period
            seasonal_factor = 1 + 0.05 * math.sin(2 * math.pi * i / 365.25)
            
            # Random daily movement
            daily_change = random.uniform(-0.03, 0.03)  # ±3% daily change
            current_price *= (1 + daily_change) * trend_factor * seasonal_factor / (1 + (0.3 * (i-1) / n_days) if i > 0 else 1)
            
            # Generate OHLC data
            close = round(current_price, 2)
            daily_vol = random.uniform(0.005, 0.025)  # 0.5% to 2.5% daily range
            
            # Open price (close to previous close with some gap)
            open_price = round(close * random.uniform(0.995, 1.005), 2)
            
            # High and low based on open and close
            high = round(max(open_price, close) * random.uniform(1.0, 1.0 + daily_vol), 2)
            low = round(min(open_price, close) * random.uniform(1.0 - daily_vol, 1.0), 2)
            
            # Volume (higher volume on higher volatility days)
            volume = int(random.uniform(50000, 200000) * (1 + abs(daily_change) * 10))
            
            data.append({
                'date': date.strftime('%Y-%m-%d'),
                'open': open_price,
                'high': high,
                'low': low,
                'close': close,
                'volume': volume
            })
        
        print(f"Generated {len(data)} gold price records")
        return data
    
    def generate_silver_prices(self,
                             start_date: str = "2020-01-01", 
                             end_date: str = "2024-01-01",
                             initial_price: float = 25.0) -> List[dict]:
        """Generate realistic silver price data."""
        
        start = datetime.strptime(start_date, "%Y-%m-%d")
        end = datetime.strptime(end_date, "%Y-%m-%d")
        
        current_date = start
        dates = []
        while current_date <= end:
            dates.append(current_date)
            current_date += timedelta(days=1)
        
        n_days = len(dates)
        
        random.seed(43)  # Different seed for silver
        
        data = []
        current_price = initial_price
        
        for i, date in enumerate(dates):
            # Silver is more volatile than gold
            trend_factor = 1 + (0.4 * i / n_days)  # 40% increase over period
            seasonal_factor = 1 + 0.08 * math.sin(2 * math.pi * i / 365.25)
            
            daily_change = random.uniform(-0.05, 0.05)  # ±5% daily change (more volatile)
            current_price *= (1 + daily_change) * trend_factor * seasonal_factor / (1 + (0.4 * (i-1) / n_days) if i > 0 else 1)
            
            close = round(current_price, 2)
            daily_vol = random.uniform(0.01, 0.04)  # Higher volatility than gold
            
            open_price = round(close * random.uniform(0.99, 1.01), 2)
            high = round(max(open_price, close) * random.uniform(1.0, 1.0 + daily_vol), 2)
            low = round(min(open_price, close) * random.uniform(1.0 - daily_vol, 1.0), 2)
            
            volume = int(random.uniform(100000, 500000) * (1 + abs(daily_change) * 15))
            
            data.append({
                'date': date.strftime('%Y-%m-%d'),
                'open': open_price,
                'high': high,
                'low': low,
                'close': close,
                'volume': volume
            })
        
        print(f"Generated {len(data)} silver price records")
        return data
    
    def generate_etf_prices(self,
                          start_date: str = "2020-01-01",
                          end_date: str = "2024-01-01") -> List[dict]:
        """Generate realistic Indian ETF price data."""
        
        start = datetime.strptime(start_date, "%Y-%m-%d")
        end = datetime.strptime(end_date, "%Y-%m-%d")
        
        current_date = start
        dates = []
        while current_date <= end:
            dates.append(current_date)
            current_date += timedelta(days=1)
        
        n_days = len(dates)
        
        # Generate data for multiple popular Indian ETFs
        etfs = [
            {'symbol': 'NIFTYBEES', 'initial_price': 150.0, 'volatility': 0.018},
            {'symbol': 'GOLDBEES', 'initial_price': 40.0, 'volatility': 0.015},
            {'symbol': 'BANKBEES', 'initial_price': 300.0, 'volatility': 0.025},
            {'symbol': 'JUNIORBEES', 'initial_price': 250.0, 'volatility': 0.022}
        ]
        
        all_data = []
        
        for etf_info in etfs:
            random.seed(hash(etf_info['symbol']) % 1000)  # Consistent seed per ETF
            
            symbol = etf_info['symbol']
            initial_price = etf_info['initial_price']
            volatility = etf_info['volatility']
            current_price = initial_price
            
            for i, date in enumerate(dates):
                # ETF trends follow market patterns
                if 'GOLD' in symbol:
                    trend_factor = 1 + (0.25 * i / n_days)  # Gold ETF follows gold
                elif 'BANK' in symbol:
                    trend_factor = 1 + (0.35 * i / n_days)  # Banking sector growth
                else:
                    trend_factor = 1 + (0.30 * i / n_days)  # General market growth
                
                seasonal_factor = 1 + 0.03 * math.sin(2 * math.pi * i / 365.25)
                daily_change = random.uniform(-volatility*2, volatility*2)
                
                current_price *= (1 + daily_change) * trend_factor * seasonal_factor / (1 + (0.30 * (i-1) / n_days) if i > 0 else 1)
                
                close = round(current_price, 2)
                daily_vol = random.uniform(0.005, 0.03)
                
                open_price = round(close * random.uniform(0.998, 1.002), 2)
                high = round(max(open_price, close) * random.uniform(1.0, 1.0 + daily_vol), 2)
                low = round(min(open_price, close) * random.uniform(1.0 - daily_vol, 1.0), 2)
                
                volume = int(random.uniform(10000, 100000) * (1 + abs(daily_change) * 20))
                
                all_data.append({
                    'date': date.strftime('%Y-%m-%d'),
                    'symbol': symbol,
                    'open': open_price,
                    'high': high,
                    'low': low,
                    'close': close,
                    'volume': volume
                })
        
        print(f"Generated {len(all_data)} ETF price records for {len(etfs)} ETFs")
        return all_data
    
    def save_all_datasets(self):
        """Generate and save all sample datasets."""
        
        # Generate gold prices
        gold_data = self.generate_gold_prices()
        gold_path = os.path.join(self.data_dir, "gold_prices.csv")
        with open(gold_path, 'w', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=['date', 'open', 'high', 'low', 'close', 'volume'])
            writer.writeheader()
            writer.writerows(gold_data)
        print(f"Saved gold prices to {gold_path}")
        
        # Generate silver prices
        silver_data = self.generate_silver_prices()
        silver_path = os.path.join(self.data_dir, "silver_prices.csv")
        with open(silver_path, 'w', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=['date', 'open', 'high', 'low', 'close', 'volume'])
            writer.writeheader()
            writer.writerows(silver_data)
        print(f"Saved silver prices to {silver_path}")
        
        # Generate ETF prices
        etf_data = self.generate_etf_prices()
        etf_path = os.path.join(self.data_dir, "etf_prices.csv")
        with open(etf_path, 'w', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=['date', 'symbol', 'open', 'high', 'low', 'close', 'volume'])
            writer.writeheader()
            writer.writerows(etf_data)
        print(f"Saved ETF prices to {etf_path}")
        
        return {
            'gold': gold_path,
            'silver': silver_path,
            'etf': etf_path
        }


if __name__ == "__main__":
    # Generate sample data when run directly
    generator = SampleDataGenerator()
    paths = generator.save_all_datasets()
    print("Sample datasets generated:")
    for asset, path in paths.items():
        print(f"  {asset}: {path}")