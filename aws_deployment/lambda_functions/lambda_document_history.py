"""
AWS Lambda Function: Document Analysis History Retrieval
Retrieves document analysis history from DynamoDB
"""
import json
import boto3
from datetime import datetime
from boto3.dynamodb.conditions import Key
from decimal import Decimal

# Initialize DynamoDB
dynamodb = boto3.resource('dynamodb', region_name='us-east-1')
history_table = dynamodb.Table('DocumentAnalysisHistory')


def lambda_handler(event, context):
    """
    Retrieve document analysis history
    
    Query parameters:
    - limit: Number of records to return (default: 20, max: 100)
    - document_id: Specific document ID to retrieve
    """
    try:
        # Parse query parameters
        params = event.get('queryStringParameters', {}) or {}
        limit = min(int(params.get('limit', 20)), 100)
        document_id = params.get('document_id')
        
        if document_id:
            # Get specific document
            response = history_table.get_item(Key={'document_id': document_id})
            
            if 'Item' not in response:
                return error_response(404, 'Document not found')
            
            item = convert_decimals(response['Item'])
            
            return {
                'statusCode': 200,
                'headers': get_cors_headers(),
                'body': json.dumps({
                    'document': item,
                    'timestamp': datetime.now().isoformat()
                })
            }
        else:
            # Get recent documents (scan with limit)
            response = history_table.scan(
                Limit=limit,
                ProjectionExpression='document_id, #ts, text_preview, analysis_type, model_used, summary, sentiment, confidence_score, document_length',
                ExpressionAttributeNames={'#ts': 'timestamp'}
            )
            
            items = [convert_decimals(item) for item in response.get('Items', [])]
            
            # Sort by timestamp descending
            items.sort(key=lambda x: x.get('timestamp', ''), reverse=True)
            
            return {
                'statusCode': 200,
                'headers': get_cors_headers(),
                'body': json.dumps({
                    'documents': items,
                    'count': len(items),
                    'timestamp': datetime.now().isoformat()
                })
            }
        
    except Exception as e:
        print(f"Error: {str(e)}")
        return error_response(500, f'Internal server error: {str(e)}')


def convert_decimals(obj):
    """Convert DynamoDB Decimal types to float/int"""
    if isinstance(obj, list):
        return [convert_decimals(i) for i in obj]
    elif isinstance(obj, dict):
        return {k: convert_decimals(v) for k, v in obj.items()}
    elif isinstance(obj, Decimal):
        return float(obj) if obj % 1 else int(obj)
    else:
        return obj


def get_cors_headers():
    """Get CORS headers"""
    return {
        'Content-Type': 'application/json',
        'Access-Control-Allow-Origin': '*',
        'Access-Control-Allow-Methods': 'GET, OPTIONS',
        'Access-Control-Allow-Headers': 'Content-Type'
    }


def error_response(status_code, message):
    """Return error response"""
    return {
        'statusCode': status_code,
        'headers': get_cors_headers(),
        'body': json.dumps({
            'error': message,
            'timestamp': datetime.now().isoformat()
        })
    }
