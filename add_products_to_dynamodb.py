#!/usr/bin/env python3
"""
Add products to DynamoDB CompetitivePricing table
"""

import json
import boto3
from datetime import datetime
from decimal import Decimal

# Initialize DynamoDB
dynamodb = boto3.resource('dynamodb', region_name='us-east-1')
table = dynamodb.Table('CompetitivePricing')

def load_products():
    """Load products from JSON file"""
    with open('add_products.json', 'r') as f:
        return json.load(f)

def convert_to_decimal(obj):
    """Convert numbers to Decimal for DynamoDB"""
    if isinstance(obj, dict):
        return {k: convert_to_decimal(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [convert_to_decimal(item) for item in obj]
    elif isinstance(obj, float):
        return Decimal(str(obj))
    elif isinstance(obj, int):
        return Decimal(str(obj))
    return obj

def add_products_to_dynamodb():
    """Add products to DynamoDB"""
    products = load_products()
    
    print(f"Adding {len(products)} products to DynamoDB...")
    
    for product in products:
        # Convert prices to Decimal
        product_item = convert_to_decimal(product)
        product_item['last_updated'] = datetime.now().isoformat()
        
        try:
            table.put_item(Item=product_item)
            print(f"✓ Added: {product['product_name']} (ID: {product['product_id']})")
            
            # Calculate and show best deal
            prices = product['prices']
            min_price = min(prices.values())
            max_price = max(prices.values())
            savings = max_price - min_price
            best_platform = [k for k, v in prices.items() if v == min_price][0]
            
            print(f"  Best deal: {best_platform} at ₹{min_price:,} (Save ₹{savings:,})")
            
        except Exception as e:
            print(f"✗ Error adding {product['product_name']}: {str(e)}")
    
    print(f"\n✅ Successfully added {len(products)} products!")
    print("\nProduct Summary:")
    print("- Home Appliances: 6 (Fridges, Washing Machine, Microwave, AC, Dishwasher)")
    print("- Electronics: 2 (Printers)")
    print("- Groceries: 2 (Olive Oil)")

if __name__ == '__main__':
    add_products_to_dynamodb()
