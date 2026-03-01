"""
AWS Lambda Function: Get Current Prices
Fetches the latest Gold and Silver prices from DynamoDB
"""

import json
import boto3
from datetime import datetime
from decimal import Decimal

dynamodb = boto3.resource('dynamodb')
price_history_table = dynamodb.Table('PriceHistory')

def decimal_default(obj):
    """JSON serializer for Decimal objects"""
    if isinstance(obj, Decimal):
        return float(obj)
    raise TypeError

def lambda_handler(event, context):
    """
    Get current prices for Gold and Silver
    
    Returns:
        {
            "gold": {
                "price": 160579.29,
                "date": "2026-02-03",
                "change": 1884.66,
                "change_percent": 1.19
            },
            "silver": {
                "price": 328726.43,
                "date": "2026-02-03",
                "change": -9932.08,
                "change_percent": -2.93
            }
        }
    """
    
    try:
        # Get latest Gold price
        gold_response = price_history_table.query(
            KeyConditionExpression='asset = :asset',
            ExpressionAttributeValues={':asset': 'GOLD'},
            ScanIndexForward=False,  # Descending order (latest first)
            Limit=2  # Get last 2 records to calculate change
        )
        
        # Get latest Silver price
        silver_response = price_history_table.query(
            KeyConditionExpression='asset = :asset',
            ExpressionAttributeValues={':asset': 'SILVER'},
            ScanIndexForward=False,
            Limit=2
        )
        
        result = {}
        
        # Process Gold data
        if gold_response['Items']:
            latest_gold = gold_response['Items'][0]
            result['gold'] = {
                'price': float(latest_gold['close']),
                'date': latest_gold['timestamp'],
                'open': float(latest_gold.get('open', latest_gold['close'])),
                'high': float(latest_gold.get('high', latest_gold['close'])),
                'low': float(latest_gold.get('low', latest_gold['close'])),
            }
            
            # Calculate change if we have previous day
            if len(gold_response['Items']) > 1:
                prev_gold = gold_response['Items'][1]
                change = float(latest_gold['close']) - float(prev_gold['close'])
                change_percent = (change / float(prev_gold['close'])) * 100
                result['gold']['change'] = round(change, 2)
                result['gold']['change_percent'] = round(change_percent, 2)
            else:
                result['gold']['change'] = 0
                result['gold']['change_percent'] = 0
        
        # Process Silver data
        if silver_response['Items']:
            latest_silver = silver_response['Items'][0]
            result['silver'] = {
                'price': float(latest_silver['close']),
                'date': latest_silver['timestamp'],
                'open': float(latest_silver.get('open', latest_silver['close'])),
                'high': float(latest_silver.get('high', latest_silver['close'])),
                'low': float(latest_silver.get('low', latest_silver['close'])),
            }
            
            # Calculate change if we have previous day
            if len(silver_response['Items']) > 1:
                prev_silver = silver_response['Items'][1]
                change = float(latest_silver['close']) - float(prev_silver['close'])
                change_percent = (change / float(prev_silver['close'])) * 100
                result['silver']['change'] = round(change, 2)
                result['silver']['change_percent'] = round(change_percent, 2)
            else:
                result['silver']['change'] = 0
                result['silver']['change_percent'] = 0
        
        return {
            'statusCode': 200,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Headers': 'Content-Type',
                'Access-Control-Allow-Methods': 'GET,OPTIONS'
            },
            'body': json.dumps(result, default=decimal_default)
        }
    
    except Exception as e:
        print(f"Error: {str(e)}")
        return {
            'statusCode': 500,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps({
                'error': str(e),
                'message': 'Failed to fetch current prices'
            })
        }
