#!/usr/bin/env python3
"""
Test Data Loading
================

Quick test to verify that the Indian price data is being loaded correctly.
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.data_loader import DataLoader

def test_data_loading():
    """Test if the data loader is reading the updated Indian prices."""
    print("🧪 Testing Data Loading")
    print("=" * 25)
    
    try:
        # Initialize data loader
        loader = DataLoader()
        
        # Load all data
        all_data = loader.load_all_data()
        
        print(f"📊 Loaded {len(all_data)} datasets")
        
        # Check gold data
        if 'gold' in all_data and not all_data['gold'].empty:
            gold_df = all_data['gold']
            latest_gold = gold_df['close'].iloc[-1]
            latest_date = gold_df['date'].iloc[-1]
            print(f"🥇 Gold: ₹{latest_gold:,.2f} (Date: {latest_date})")
            print(f"   Records: {len(gold_df)}")
        else:
            print("❌ No gold data found")
        
        # Check silver data
        if 'silver' in all_data and not all_data['silver'].empty:
            silver_df = all_data['silver']
            latest_silver = silver_df['close'].iloc[-1]
            latest_date = silver_df['date'].iloc[-1]
            print(f"🥈 Silver: ₹{latest_silver:,.2f} (Date: {latest_date})")
            print(f"   Records: {len(silver_df)}")
        else:
            print("❌ No silver data found")
        
        # Check ETF data
        if 'etf' in all_data and not all_data['etf'].empty:
            etf_df = all_data['etf']
            goldbees = etf_df[etf_df['symbol'] == 'GOLDBEES']
            if not goldbees.empty:
                latest_goldbees = goldbees['close'].iloc[-1]
                latest_date = goldbees['date'].iloc[-1]
                print(f"📊 GOLDBEES: ₹{latest_goldbees:.2f} (Date: {latest_date})")
            print(f"   Total ETF records: {len(etf_df)}")
        else:
            print("❌ No ETF data found")
        
        print("\n✅ Data loading test complete!")
        return True
        
    except Exception as e:
        print(f"❌ Error testing data loading: {str(e)}")
        return False

if __name__ == "__main__":
    test_data_loading()