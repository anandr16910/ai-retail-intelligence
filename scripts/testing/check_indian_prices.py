#!/usr/bin/env python3
"""
Check Indian Prices
==================

Quick script to verify the current Indian gold and silver prices in the data files.
"""

import pandas as pd
import os
from datetime import datetime

def check_prices():
    """Check current prices in data files."""
    print("🇮🇳 Current Indian Precious Metals Prices")
    print("=" * 45)
    print(f"Checked at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 45)
    
    # Check Gold Prices
    gold_file = "data/gold_prices.csv"
    if os.path.exists(gold_file):
        try:
            gold_df = pd.read_csv(gold_file)
            if not gold_df.empty:
                latest_gold = gold_df['close'].iloc[-1]
                latest_date = gold_df['date'].iloc[-1]
                previous_gold = gold_df['close'].iloc[-2] if len(gold_df) > 1 else latest_gold
                change = latest_gold - previous_gold
                change_pct = (change / previous_gold) * 100 if previous_gold != 0 else 0
                
                print(f"🥇 24K Gold (per 10 grams):")
                print(f"   Current Price: ₹{latest_gold:,.2f}")
                print(f"   Date: {latest_date}")
                print(f"   Change: ₹{change:+,.2f} ({change_pct:+.2f}%)")
                print(f"   Records: {len(gold_df)} days")
            else:
                print("🥇 Gold: No data available")
        except Exception as e:
            print(f"🥇 Gold: Error reading data - {str(e)}")
    else:
        print("🥇 Gold: File not found")
    
    print()
    
    # Check Silver Prices
    silver_file = "data/silver_prices.csv"
    if os.path.exists(silver_file):
        try:
            silver_df = pd.read_csv(silver_file)
            if not silver_df.empty:
                latest_silver = silver_df['close'].iloc[-1]
                latest_date = silver_df['date'].iloc[-1]
                previous_silver = silver_df['close'].iloc[-2] if len(silver_df) > 1 else latest_silver
                change = latest_silver - previous_silver
                change_pct = (change / previous_silver) * 100 if previous_silver != 0 else 0
                
                print(f"🥈 Silver (per kg):")
                print(f"   Current Price: ₹{latest_silver:,.2f}")
                print(f"   Date: {latest_date}")
                print(f"   Change: ₹{change:+,.2f} ({change_pct:+.2f}%)")
                print(f"   Records: {len(silver_df)} days")
            else:
                print("🥈 Silver: No data available")
        except Exception as e:
            print(f"🥈 Silver: Error reading data - {str(e)}")
    else:
        print("🥈 Silver: File not found")
    
    print()
    
    # Check ETF Prices
    etf_file = "data/etf_prices.csv"
    if os.path.exists(etf_file):
        try:
            etf_df = pd.read_csv(etf_file)
            if not etf_df.empty:
                # Show GOLDBEES specifically
                goldbees = etf_df[etf_df['symbol'] == 'GOLDBEES']
                if not goldbees.empty:
                    latest_goldbees = goldbees['close'].iloc[-1]
                    latest_date = goldbees['date'].iloc[-1]
                    print(f"📊 GOLDBEES ETF:")
                    print(f"   Current Price: ₹{latest_goldbees:.2f}")
                    print(f"   Date: {latest_date}")
                
                # Show total ETF records
                unique_etfs = etf_df['symbol'].nunique() if 'symbol' in etf_df.columns else 1
                print(f"   Total ETFs: {unique_etfs}")
                print(f"   Total Records: {len(etf_df)}")
            else:
                print("📊 ETF: No data available")
        except Exception as e:
            print(f"📊 ETF: Error reading data - {str(e)}")
    else:
        print("📊 ETF: File not found")
    
    print("\n" + "=" * 45)
    print("💡 Expected Indian Market Rates (2026):")
    print("   • 24K Gold: ₹1.3-1.6 Lakh per 10g")
    print("   • Silver: ₹2.8-3.7 Lakh per kg")
    print("   • GOLDBEES: ₹140-160 per unit")
    print("\n🔄 If dashboard shows old prices:")
    print("   1. Run: python restart_services.py")
    print("   2. Or click 'Refresh Data' in dashboard")
    print("   3. Or refresh browser (F5)")

if __name__ == "__main__":
    check_prices()