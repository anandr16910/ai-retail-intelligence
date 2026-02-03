#!/usr/bin/env python3
"""
Generate Indian Gold & Silver Prices Script
==========================================

This script generates realistic Indian gold and silver prices in INR (₹) 
with current dates for the dashboard. Prices are based on Indian market rates.

Indian Gold Prices:
- 24K Gold: ₹6,000-7,500 per gram
- 22K Gold: ₹5,500-6,900 per gram
- 10 grams = 1 tola (common Indian unit)

Indian Silver Prices:
- Silver: ₹70-90 per gram
- 1 kg Silver: ₹70,000-90,000

Usage:
    python generate_indian_prices.py [--days DAYS]
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import argparse
import os

def generate_realistic_indian_prices(start_price, days, volatility=0.015):
    """Generate realistic Indian price data using random walk with Indian market characteristics."""
    prices = [start_price]
    
    for i in range(days - 1):
        # Indian markets have specific patterns
        # Higher volatility during festival seasons, geopolitical events
        
        # Random price change with slight upward bias (inflation)
        daily_change = np.random.normal(0.0002, volatility)  # Slight upward bias
        
        # Add weekly patterns (Monday/Tuesday often higher, Friday profit booking)
        day_of_week = (i + 1) % 7
        if day_of_week in [0, 1]:  # Monday, Tuesday - higher demand
            daily_change += 0.0005
        elif day_of_week == 4:  # Friday - profit booking
            daily_change -= 0.0003
        
        # Add monthly patterns (month-end salary effect)
        day_of_month = (i + 1) % 30
        if day_of_month in [28, 29, 0, 1, 2]:  # Month-end/start
            daily_change += 0.0003
        
        # Festival season effect (assume some days have higher demand)
        if np.random.random() < 0.05:  # 5% chance of festival effect
            daily_change += np.random.uniform(0.005, 0.02)
        
        new_price = prices[-1] * (1 + daily_change)
        
        # Ensure price doesn't go too low (support levels)
        new_price = max(new_price, start_price * 0.8)
        
        prices.append(new_price)
    
    return prices

def generate_indian_ohlc_data(close_prices, volatility=0.012):
    """Generate OHLC data for Indian markets."""
    data = []
    
    for i, close in enumerate(close_prices):
        if i == 0:
            open_price = close
        else:
            # Indian markets often have gaps due to international overnight prices
            gap = np.random.normal(0, volatility * 0.7)
            open_price = close_prices[i-1] * (1 + gap)
        
        # Generate high and low around close price
        # Indian gold/silver markets have good intraday volatility
        daily_range = np.random.uniform(0.008, volatility * 1.5)
        high = close * (1 + daily_range/2)
        low = close * (1 - daily_range/2)
        
        # Ensure OHLC relationships
        high = max(high, open_price, close)
        low = min(low, open_price, close)
        
        # Generate volume (Indian markets have good volume)
        base_volume = np.random.randint(80000, 300000)
        volume_multiplier = np.random.uniform(0.6, 2.2)
        volume = int(base_volume * volume_multiplier)
        
        data.append({
            'open': round(open_price, 2),
            'high': round(high, 2),
            'low': round(low, 2),
            'close': round(close, 2),
            'volume': volume
        })
    
    return data

def create_indian_gold_data(days=90, gold_type="24K"):
    """Create Indian gold price data in INR per 10 grams."""
    print(f"🥇 Generating {days} days of Indian {gold_type} gold price data...")
    
    # Indian gold prices (per 10 grams) - Updated to current 2026 market rates
    if gold_type == "24K":
        start_price = 155000.0  # ₹1,55,000 per 10 grams (24K) - Current market rate
        volatility = 0.015
    else:  # 22K
        start_price = 142000.0  # ₹1,42,000 per 10 grams (22K) - Current market rate
        volatility = 0.014
    
    # Generate dates (ending today)
    end_date = datetime.now().date()
    start_date = end_date - timedelta(days=days-1)
    dates = pd.date_range(start=start_date, end=end_date, freq='D')
    
    # Generate realistic Indian gold prices
    close_prices = generate_realistic_indian_prices(start_price, days, volatility)
    ohlc_data = generate_indian_ohlc_data(close_prices, volatility)
    
    # Create DataFrame
    df = pd.DataFrame(ohlc_data)
    df['date'] = dates
    
    # Reorder columns
    df = df[['date', 'open', 'high', 'low', 'close', 'volume']]
    
    current_price = df['close'].iloc[-1]
    previous_price = df['close'].iloc[-2] if len(df) > 1 else current_price
    change = current_price - previous_price
    change_pct = (change / previous_price) * 100 if previous_price != 0 else 0
    
    print(f"  💰 Current {gold_type} gold price: ₹{current_price:,.2f} per 10g")
    print(f"  📈 Change: ₹{change:+,.2f} ({change_pct:+.2f}%)")
    print(f"  📊 Price range: ₹{df['low'].min():,.2f} - ₹{df['high'].max():,.2f}")
    
    return df

def create_indian_silver_data(days=90):
    """Create Indian silver price data in INR per kg."""
    print(f"🥈 Generating {days} days of Indian silver price data...")
    
    # Indian silver prices (per kg) - Updated to current 2026 market rates
    start_price = 320000.0  # ₹3,20,000 per kg - Current market rate
    volatility = 0.022  # Silver is more volatile than gold
    
    # Generate dates (ending today)
    end_date = datetime.now().date()
    start_date = end_date - timedelta(days=days-1)
    dates = pd.date_range(start=start_date, end=end_date, freq='D')
    
    # Generate realistic Indian silver prices
    close_prices = generate_realistic_indian_prices(start_price, days, volatility)
    ohlc_data = generate_indian_ohlc_data(close_prices, volatility * 1.2)
    
    # Create DataFrame
    df = pd.DataFrame(ohlc_data)
    df['date'] = dates
    
    # Reorder columns
    df = df[['date', 'open', 'high', 'low', 'close', 'volume']]
    
    current_price = df['close'].iloc[-1]
    previous_price = df['close'].iloc[-2] if len(df) > 1 else current_price
    change = current_price - previous_price
    change_pct = (change / previous_price) * 100 if previous_price != 0 else 0
    
    print(f"  💰 Current silver price: ₹{current_price:,.2f} per kg")
    print(f"  📈 Change: ₹{change:+,.2f} ({change_pct:+.2f}%)")
    print(f"  📊 Price range: ₹{df['low'].min():,.2f} - ₹{df['high'].max():,.2f}")
    
    return df

def create_indian_etf_data(days=90):
    """Create Indian ETF price data."""
    print(f"📊 Generating {days} days of Indian ETF price data...")
    
    # Generate dates (ending today)
    end_date = datetime.now().date()
    start_date = end_date - timedelta(days=days-1)
    dates = pd.date_range(start=start_date, end=end_date, freq='D')
    
    # Indian ETFs with realistic prices - Updated for 2026 market levels
    etfs = [
        ('NIFTYBEES', 285.50),    # Nifty 50 ETF (higher due to market growth)
        ('GOLDBEES', 147.25),     # Gold ETF (reflects higher gold prices)
        ('BANKBEES', 535.80),     # Bank Nifty ETF
        ('JUNIORBEES', 395.40),   # Junior Nifty ETF
        ('LIQUIDBEES', 1000.15),  # Liquid ETF (stable)
        ('PSUBNKBEES', 38.90)     # PSU Bank ETF
    ]
    
    all_data = []
    
    for etf_name, start_price in etfs:
        # Different volatility for different ETFs
        if 'GOLD' in etf_name:
            volatility = 0.018  # Gold ETF follows gold prices
        elif 'BANK' in etf_name:
            volatility = 0.025  # Banking sector is volatile
        elif 'LIQUID' in etf_name:
            volatility = 0.002  # Liquid funds are stable
        else:
            volatility = 0.020  # General equity ETFs
        
        close_prices = generate_realistic_indian_prices(start_price, days, volatility)
        ohlc_data = generate_indian_ohlc_data(close_prices, volatility)
        
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
        previous_price = df[df['symbol'] == etf_name]['close'].iloc[-2]
        change = current_price - previous_price
        change_pct = (change / previous_price) * 100
        print(f"  💰 {etf_name}: ₹{current_price:.2f} ({change_pct:+.2f}%)")
    
    return df

def add_indian_market_context():
    """Add context about Indian precious metals market."""
    print("\n📋 Indian Precious Metals Market Context:")
    print("=" * 50)
    print("🥇 Gold Prices:")
    print("  • 24K Gold: Premium quality, highest purity")
    print("  • 22K Gold: Most common for jewelry in India")
    print("  • Prices include 3% GST + making charges")
    print("  • Major trading centers: Mumbai, Delhi, Chennai")
    print("  • Current range: ₹1.3-1.6 Lakh per 10g (24K)")
    
    print("\n🥈 Silver Prices:")
    print("  • Industrial and investment demand")
    print("  • Higher volatility than gold")
    print("  • Popular during festival seasons")
    print("  • Prices per kg (1000 grams)")
    print("  • Current range: ₹2.8-3.7 Lakh per kg")
    
    print("\n📊 ETF Information:")
    print("  • GOLDBEES: Tracks gold prices")
    print("  • NIFTYBEES: Tracks Nifty 50 index")
    print("  • BANKBEES: Banking sector exposure")
    print("  • All prices in INR (₹)")
    print("  • ETF prices adjusted for current market levels")

def main():
    """Main function."""
    parser = argparse.ArgumentParser(description="Generate Indian gold and silver prices in INR")
    parser.add_argument("--days", type=int, default=90, help="Number of days to generate (default: 90)")
    parser.add_argument("--gold-type", choices=["24K", "22K"], default="24K", help="Gold purity (default: 24K)")
    args = parser.parse_args()
    
    print("🇮🇳 Generating Indian Precious Metals Price Data")
    print("=" * 55)
    print(f"Currency: Indian Rupees (₹)")
    print(f"Market: Indian precious metals market")
    print(f"Period: Last {args.days} days ending today")
    print("=" * 55)
    
    # Ensure data directory exists
    os.makedirs("data", exist_ok=True)
    
    try:
        # Generate Indian gold data
        gold_df = create_indian_gold_data(args.days, args.gold_type)
        gold_df.to_csv("data/gold_prices.csv", index=False)
        print("  ✅ Indian gold data saved to data/gold_prices.csv")
        
        # Generate Indian silver data
        silver_df = create_indian_silver_data(args.days)
        silver_df.to_csv("data/silver_prices.csv", index=False)
        print("  ✅ Indian silver data saved to data/silver_prices.csv")
        
        # Generate Indian ETF data
        etf_df = create_indian_etf_data(args.days)
        etf_df.to_csv("data/etf_prices.csv", index=False)
        print("  ✅ Indian ETF data saved to data/etf_prices.csv")
        
        print("\n" + "=" * 55)
        print("✅ All Indian price data generated successfully!")
        
        # Show summary
        print(f"\n📊 Data Summary:")
        print(f"  • Gold records: {len(gold_df)} ({args.gold_type})")
        print(f"  • Silver records: {len(silver_df)}")
        print(f"  • ETF records: {len(etf_df)}")
        print(f"  • Date range: {gold_df['date'].min().strftime('%Y-%m-%d')} to {gold_df['date'].max().strftime('%Y-%m-%d')}")
        
        # Current prices summary
        print(f"\n💰 Current Prices (as of {gold_df['date'].max().strftime('%Y-%m-%d')}):")
        print(f"  • {args.gold_type} Gold: ₹{gold_df['close'].iloc[-1]:,.2f} per 10g (~₹{gold_df['close'].iloc[-1]/100000:.1f} Lakh)")
        print(f"  • Silver: ₹{silver_df['close'].iloc[-1]:,.2f} per kg (~₹{silver_df['close'].iloc[-1]/100000:.1f} Lakh)")
        print(f"  • GOLDBEES ETF: ₹{etf_df[etf_df['symbol']=='GOLDBEES']['close'].iloc[-1]:.2f}")
        
        # Add market context
        add_indian_market_context()
        
        print(f"\n💡 Next steps:")
        print("1. Restart the API server: python main.py --mode server")
        print("2. Refresh the dashboard in your browser")
        print("3. Check the Dashboard Overview for updated Indian rates")
        print("4. Try Market Copilot: 'What is the current gold price in India?'")
        print("5. Prices now reflect current 2026 Indian market levels")
        
        return 0
        
    except Exception as e:
        print(f"❌ Error generating Indian price data: {str(e)}")
        return 1

if __name__ == "__main__":
    exit(main())