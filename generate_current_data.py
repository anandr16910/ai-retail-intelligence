#!/usr/bin/env python3
"""
Generate Current Data Script
===========================

This script generates fresh sample data with current dates for the dashboard.
It creates realistic price data for gold, silver, and ETFs with recent dates.

Usage:
    python generate_current_data.py [--days DAYS] [--start-price PRICE]
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import argparse
import os

def generate_realistic_prices(start_price, days, volatility=0.02):
    """Generate realistic price data using random walk."""
    prices = [start_price]
    
    for _ in range(days - 1):
        # Random price change with mean reversion tendency
        change = np.random.normal(0, volatility)
        
        # Add slight upward bias (long-term growth)
        change += 0.0001
        
        new_price = prices[-1] * (1 + change)
        
        # Ensure price doesn't go negative
        new_price = max(new_price, start_price * 0.5)
        
        prices.append(new_price)
    
    return prices

def generate_ohlc_data(close_prices, volatility=0.01):
    """Generate OHLC data from close prices."""
    data = []
    
    for i, close in enumerate(close_prices):
        if i == 0:
            open_price = close
        else:
            # Open is close to previous close with some gap
            gap = np.random.normal(0, volatility * 0.5)
            open_price = close_prices[i-1] * (1 + gap)
        
        # Generate high and low around close price
        daily_range = np.random.uniform(0.005, volatility)
        high = close * (1 + daily_range/2)
        low = close * (1 - daily_range/2)
        
        # Ensure OHLC relationships
        high = max(high, open_price, close)
        low = min(low, open_price, close)
        
        # Generate volume
        base_volume = np.random.randint(50000, 200000)
        volume_multiplier = np.random.uniform(0.5, 2.0)
        volume = int(base_volume * volume_multiplier)
        
        data.append({
            'open': round(open_price, 2),
            'high': round(high, 2),
            'low': round(low, 2),
            'close': round(close, 2),
            'volume': volume
        })
    
    return data

def create_current_gold_data(days=90, start_price=2000.0):
    """Create current gold price data."""
    print(f"📈 Generating {days} days of gold price data...")
    
    # Generate dates (ending today)
    end_date = datetime.now().date()
    start_date = end_date - timedelta(days=days-1)
    dates = pd.date_range(start=start_date, end=end_date, freq='D')
    
    # Generate realistic gold prices
    close_prices = generate_realistic_prices(start_price, days, volatility=0.015)
    ohlc_data = generate_ohlc_data(close_prices, volatility=0.02)
    
    # Create DataFrame
    df = pd.DataFrame(ohlc_data)
    df['date'] = dates
    
    # Reorder columns
    df = df[['date', 'open', 'high', 'low', 'close', 'volume']]
    
    current_price = df['close'].iloc[-1]
    print(f"  💰 Current gold price: ${current_price:.2f}")
    
    return df

def create_current_silver_data(days=90, start_price=25.0):
    """Create current silver price data."""
    print(f"🥈 Generating {days} days of silver price data...")
    
    # Generate dates (ending today)
    end_date = datetime.now().date()
    start_date = end_date - timedelta(days=days-1)
    dates = pd.date_range(start=start_date, end=end_date, freq='D')
    
    # Generate realistic silver prices (more volatile than gold)
    close_prices = generate_realistic_prices(start_price, days, volatility=0.025)
    ohlc_data = generate_ohlc_data(close_prices, volatility=0.03)
    
    # Create DataFrame
    df = pd.DataFrame(ohlc_data)
    df['date'] = dates
    
    # Reorder columns
    df = df[['date', 'open', 'high', 'low', 'close', 'volume']]
    
    current_price = df['close'].iloc[-1]
    print(f"  💰 Current silver price: ${current_price:.2f}")
    
    return df

def create_current_etf_data(days=90):
    """Create current ETF price data."""
    print(f"📊 Generating {days} days of ETF price data...")
    
    # Generate dates (ending today)
    end_date = datetime.now().date()
    start_date = end_date - timedelta(days=days-1)
    dates = pd.date_range(start=start_date, end=end_date, freq='D')
    
    etfs = [
        ('NIFTYBEES', 180.0),
        ('GOLDBEES', 45.0),
        ('BANKBEES', 420.0),
        ('JUNIORBEES', 280.0)
    ]
    
    all_data = []
    
    for etf_name, start_price in etfs:
        close_prices = generate_realistic_prices(start_price, days, volatility=0.02)
        ohlc_data = generate_ohlc_data(close_prices, volatility=0.025)
        
        for i, (date, ohlc) in enumerate(zip(dates, ohlc_data)):
            all_data.append({
                'date': date,
                'symbol': etf_name,
                'open': ohlc['open'],
                'high': ohlc['high'],
                'low': ohlc['low'],
                'close': ohlc['close'],
                'volume': ohlc['volume']
            })
    
    df = pd.DataFrame(all_data)
    
    # Show current prices for each ETF
    for etf_name, _ in etfs:
        current_price = df[df['symbol'] == etf_name]['close'].iloc[-1]
        print(f"  💰 Current {etf_name} price: ₹{current_price:.2f}")
    
    return df

def main():
    """Main function."""
    parser = argparse.ArgumentParser(description="Generate current price data for dashboard")
    parser.add_argument("--days", type=int, default=90, help="Number of days to generate (default: 90)")
    parser.add_argument("--gold-price", type=float, default=2000.0, help="Starting gold price (default: 2000)")
    parser.add_argument("--silver-price", type=float, default=25.0, help="Starting silver price (default: 25)")
    args = parser.parse_args()
    
    print("🔄 Generating Current Price Data for Dashboard")
    print("=" * 50)
    
    # Ensure data directory exists
    os.makedirs("data", exist_ok=True)
    
    try:
        # Generate gold data
        gold_df = create_current_gold_data(args.days, args.gold_price)
        gold_df.to_csv("data/gold_prices.csv", index=False)
        print("  ✅ Gold data saved to data/gold_prices.csv")
        
        # Generate silver data
        silver_df = create_current_silver_data(args.days, args.silver_price)
        silver_df.to_csv("data/silver_prices.csv", index=False)
        print("  ✅ Silver data saved to data/silver_prices.csv")
        
        # Generate ETF data
        etf_df = create_current_etf_data(args.days)
        etf_df.to_csv("data/etf_prices.csv", index=False)
        print("  ✅ ETF data saved to data/etf_prices.csv")
        
        print("\n" + "=" * 50)
        print("✅ All current price data generated successfully!")
        
        # Show summary
        print(f"\n📊 Data Summary:")
        print(f"  • Gold records: {len(gold_df)}")
        print(f"  • Silver records: {len(silver_df)}")
        print(f"  • ETF records: {len(etf_df)}")
        print(f"  • Date range: {gold_df['date'].min().strftime('%Y-%m-%d')} to {gold_df['date'].max().strftime('%Y-%m-%d')}")
        
        print(f"\n💡 Next steps:")
        print("1. Restart the API server: python main.py --mode server")
        print("2. Refresh the dashboard in your browser")
        print("3. Check the Dashboard Overview for updated rates")
        
        return 0
        
    except Exception as e:
        print(f"❌ Error generating data: {str(e)}")
        return 1

if __name__ == "__main__":
    exit(main())