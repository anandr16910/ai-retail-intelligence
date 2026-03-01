"""
Load initial data to DynamoDB tables
"""
import boto3
import pandas as pd
import argparse
from datetime import datetime
import sys
import os

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))


def load_price_history(region='us-east-1'):
    """Load historical price data to DynamoDB"""
    print("Loading price history data...")
    
    dynamodb = boto3.resource('dynamodb', region_name=region)
    table = dynamodb.Table('PriceHistory')
    
    # Load gold prices
    try:
        gold_df = pd.read_csv('../../data/gold_prices.csv')
        print(f"  Loading {len(gold_df)} gold price records...")
        
        for _, row in gold_df.iterrows():
            table.put_item(
                Item={
                    'asset': 'GOLD',
                    'timestamp': str(row['date']),
                    'open': float(row['open']),
                    'high': float(row['high']),
                    'low': float(row['low']),
                    'close': float(row['close']),
                    'volume': int(row['volume'])
                }
            )
        print("  ✓ Gold prices loaded")
    except Exception as e:
        print(f"  ✗ Error loading gold prices: {e}")
    
    # Load silver prices
    try:
        silver_df = pd.read_csv('../../data/silver_prices.csv')
        print(f"  Loading {len(silver_df)} silver price records...")
        
        for _, row in silver_df.iterrows():
            table.put_item(
                Item={
                    'asset': 'SILVER',
                    'timestamp': str(row['date']),
                    'open': float(row['open']),
                    'high': float(row['high']),
                    'low': float(row['low']),
                    'close': float(row['close']),
                    'volume': int(row['volume'])
                }
            )
        print("  ✓ Silver prices loaded")
    except Exception as e:
        print(f"  ✗ Error loading silver prices: {e}")
    
    # Load ETF prices
    try:
        etf_df = pd.read_csv('../../data/etf_prices.csv')
        print(f"  Loading {len(etf_df)} ETF price records...")
        
        for _, row in etf_df.iterrows():
            table.put_item(
                Item={
                    'asset': 'ETF',
                    'timestamp': str(row['date']),
                    'open': float(row['open']),
                    'high': float(row['high']),
                    'low': float(row['low']),
                    'close': float(row['close']),
                    'volume': int(row.get('volume', 0))
                }
            )
        print("  ✓ ETF prices loaded")
    except Exception as e:
        print(f"  ✗ Error loading ETF prices: {e}")


def load_competitive_pricing(region='us-east-1'):
    """Load competitive pricing data to DynamoDB"""
    print("Loading competitive pricing data...")
    
    dynamodb = boto3.resource('dynamodb', region_name=region)
    table = dynamodb.Table('CompetitivePricing')
    
    try:
        pricing_df = pd.read_csv('../../data/competitive_pricing_sample.csv')
        print(f"  Loading {len(pricing_df)} product records...")
        
        # Group by product
        for product_id in pricing_df['product_id'].unique():
            product_data = pricing_df[pricing_df['product_id'] == product_id].iloc[0]
            
            # Get prices from all platforms
            prices = {}
            for platform in ['Amazon', 'Flipkart', 'JioMart', 'Blinkit', 'Zepto', 'DMart']:
                col_name = f'{platform.lower()}_price'
                if col_name in product_data:
                    prices[platform] = float(product_data[col_name])
            
            # Calculate best deal
            if prices:
                lowest_price = min(prices.values())
                highest_price = max(prices.values())
                best_platform = min(prices, key=prices.get)
                savings = highest_price - lowest_price
                
                table.put_item(
                    Item={
                        'product_id': str(product_id),
                        'product_name': str(product_data['product_name']),
                        'category': str(product_data.get('category', 'General')),
                        'prices': prices,
                        'lowest_price': lowest_price,
                        'highest_price': highest_price,
                        'best_platform': best_platform,
                        'savings_amount': savings,
                        'updated_at': datetime.now().isoformat()
                    }
                )
        
        print("  ✓ Competitive pricing data loaded")
    except Exception as e:
        print(f"  ✗ Error loading competitive pricing: {e}")


def main():
    parser = argparse.ArgumentParser(description='Load data to DynamoDB')
    parser.add_argument('--region', default='us-east-1', help='AWS region')
    args = parser.parse_args()
    
    print("=" * 50)
    print("Loading Initial Data to DynamoDB")
    print("=" * 50)
    print()
    
    load_price_history(args.region)
    print()
    load_competitive_pricing(args.region)
    print()
    
    print("=" * 50)
    print("Data loading complete!")
    print("=" * 50)


if __name__ == '__main__':
    main()
