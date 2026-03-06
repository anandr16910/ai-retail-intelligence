#!/usr/bin/env python3
"""
Import household items from CSV to DynamoDB
- CompetitivePricing table: Latest prices for Market Copilot
- PriceHistory table: Historical data for Price Forecasting
"""

import csv
import boto3
from datetime import datetime
from decimal import Decimal
from collections import defaultdict

# Initialize DynamoDB
dynamodb = boto3.resource('dynamodb', region_name='us-east-1')
competitive_pricing_table = dynamodb.Table('CompetitivePricing')
price_history_table = dynamodb.Table('PriceHistory')

def load_csv_data():
    """Load data from CSV file"""
    products_data = defaultdict(list)
    
    with open('data/household_items_2years.csv', 'r') as f:
        reader = csv.DictReader(f)
        for row in reader:
            product_id = row['product_id']
            products_data[product_id].append(row)
    
    return products_data

def add_to_competitive_pricing(products_data):
    """Add latest prices to CompetitivePricing table for Market Copilot"""
    print("\n📊 Adding products to CompetitivePricing (Market Copilot)...")
    
    for product_id, records in products_data.items():
        # Get the latest record (last date)
        latest_record = records[-1]
        
        product_name = latest_record['product_name']
        
        # Map CSV columns to platform names
        prices = {
            'Amazon': Decimal(str(latest_record['amazon'])),
            'Flipkart': Decimal(str(latest_record['flipkart'])),
            'JioMart': Decimal(str(latest_record['jiomart'])),
            'Blinkit': Decimal(str(latest_record['blinkit'])),
            'Zepto': Decimal(str(latest_record['zepto'])),
            'DMart': Decimal(str(latest_record['dmart_ready']))
        }
        
        # Calculate best deal
        price_values = {k: float(v) for k, v in prices.items()}
        min_price = min(price_values.values())
        max_price = max(price_values.values())
        savings = max_price - min_price
        best_platform = [k for k, v in price_values.items() if v == min_price][0]
        
        item = {
            'product_id': product_id,
            'product_name': product_name,
            'category': 'household_items',
            'prices': prices,
            'last_updated': latest_record['date']
        }
        
        try:
            competitive_pricing_table.put_item(Item=item)
            print(f"✓ {product_name}")
            print(f"  Best: ₹{min_price:.2f} on {best_platform} (Save ₹{savings:.2f})")
        except Exception as e:
            print(f"✗ Error adding {product_name}: {str(e)}")

def add_to_price_history(products_data):
    """Add historical data to PriceHistory table for Price Forecasting"""
    print("\n📈 Adding historical data to PriceHistory (Price Forecasting)...")
    
    for product_id, records in products_data.items():
        product_name = records[0]['product_name']
        print(f"\n{product_name} ({len(records)} records)...")
        
        # Add records in batches
        batch_size = 25  # DynamoDB batch limit
        for i in range(0, len(records), batch_size):
            batch = records[i:i + batch_size]
            
            with price_history_table.batch_writer() as writer:
                for record in batch:
                    # Calculate average price across all platforms
                    prices = [
                        float(record['amazon']),
                        float(record['flipkart']),
                        float(record['jiomart']),
                        float(record['blinkit']),
                        float(record['zepto']),
                        float(record['dmart_ready'])
                    ]
                    avg_price = sum(prices) / len(prices)
                    
                    item = {
                        'asset': product_id,  # Use product_id as asset identifier
                        'timestamp': record['date'],
                        'open': Decimal(str(min(prices))),
                        'high': Decimal(str(max(prices))),
                        'low': Decimal(str(min(prices))),
                        'close': Decimal(str(avg_price)),
                        'volume': Decimal('1000'),  # Placeholder volume
                        'product_name': product_name
                    }
                    
                    writer.put_item(Item=item)
            
            print(f"  ✓ Batch {i//batch_size + 1}/{(len(records)-1)//batch_size + 1}")
        
        print(f"  ✅ Completed {product_name}")

def main():
    """Main import function"""
    print("🚀 Importing Household Items from CSV...")
    print("=" * 60)
    
    # Load data
    products_data = load_csv_data()
    print(f"\n📦 Found {len(products_data)} products")
    
    for product_id, records in products_data.items():
        print(f"  • {records[0]['product_name']}: {len(records)} price records")
    
    # Add to CompetitivePricing (for Market Copilot)
    add_to_competitive_pricing(products_data)
    
    # Add to PriceHistory (for Price Forecasting)
    add_to_price_history(products_data)
    
    print("\n" + "=" * 60)
    print("✅ Import Complete!")
    print("\n📊 Summary:")
    print(f"  • Products added to Market Copilot: {len(products_data)}")
    print(f"  • Historical records added for Forecasting: {sum(len(r) for r in products_data.values())}")
    print("\n🎯 What You Can Do Now:")
    print("  1. Market Copilot: Ask about Fortune Oil, Toor Dal, Dove Shampoo, etc.")
    print("  2. Price Forecasting: Select these products from dropdown (need to update UI)")
    print("\n💡 Try in Market Copilot:")
    print('  • "What are the prices for Fortune Sunflower Oil?"')
    print('  • "Compare prices for Dove Shampoo"')
    print('  • "Show me the cheapest cooking oil"')
    print('  • "Which platform has best deals on household items?"')

if __name__ == '__main__':
    main()
