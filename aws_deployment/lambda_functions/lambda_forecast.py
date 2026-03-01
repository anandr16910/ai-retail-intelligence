"""
AWS Lambda Function: Price Forecasting with Amazon Bedrock
"""
import json
import boto3
from datetime import datetime, timedelta
from decimal import Decimal

# Initialize AWS clients
bedrock = boto3.client('bedrock-runtime', region_name='us-east-1')
dynamodb = boto3.resource('dynamodb', region_name='us-east-1')

# DynamoDB tables
price_history_table = dynamodb.Table('PriceHistory')
forecasts_table = dynamodb.Table('Forecasts')


def lambda_handler(event, context):
    """
    Generate price forecast using Amazon Bedrock
    
    Request body:
    {
        "asset": "GOLD|SILVER|ETF",
        "horizon": 30,
        "model": "claude-3-sonnet|claude-3-haiku"
    }
    """
    try:
        # Parse request
        body = json.loads(event.get('body', '{}'))
        asset = body.get('asset', 'GOLD')
        horizon = int(body.get('horizon', 30))
        model_choice = body.get('model', 'claude-3-haiku')
        
        # Validate inputs
        if asset not in ['GOLD', 'SILVER', 'ETF']:
            return error_response(400, 'Invalid asset. Must be GOLD, SILVER, or ETF')
        
        if horizon < 1 or horizon > 90:
            return error_response(400, 'Horizon must be between 1 and 90 days')
        
        # Get historical data from DynamoDB
        historical_data = get_historical_data(asset, days=90)
        
        if not historical_data:
            return error_response(404, f'No historical data found for {asset}')
        
        # Select Bedrock model
        model_id = get_model_id(model_choice)
        
        # Generate forecast using Bedrock
        forecast_result = generate_forecast_with_bedrock(
            asset, historical_data, horizon, model_id
        )
        
        # Store forecast in DynamoDB
        store_forecast(asset, forecast_result, horizon)
        
        # Return response
        return {
            'statusCode': 200,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Methods': 'POST, OPTIONS',
                'Access-Control-Allow-Headers': 'Content-Type'
            },
            'body': json.dumps({
                'asset': asset,
                'horizon': horizon,
                'forecast': forecast_result,
                'timestamp': datetime.now().isoformat(),
                'model_used': model_choice
            }, default=decimal_default)
        }
        
    except Exception as e:
        print(f"Error: {str(e)}")
        return error_response(500, f'Internal server error: {str(e)}')


def get_historical_data(asset, days=90):
    """Get historical price data from DynamoDB"""
    try:
        # Calculate date range
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)
        
        # Query DynamoDB
        response = price_history_table.query(
            KeyConditionExpression='asset = :asset AND #ts BETWEEN :start AND :end',
            ExpressionAttributeNames={'#ts': 'timestamp'},
            ExpressionAttributeValues={
                ':asset': asset,
                ':start': start_date.isoformat(),
                ':end': end_date.isoformat()
            },
            ScanIndexForward=False,
            Limit=days
        )
        
        return response.get('Items', [])
        
    except Exception as e:
        print(f"Error fetching historical data: {str(e)}")
        return []


def generate_forecast_with_bedrock(asset, historical_data, horizon, model_id):
    """Generate forecast using Amazon Bedrock"""
    
    # Prepare historical data summary
    recent_data = historical_data[:30]  # Last 30 days
    data_summary = []
    
    for item in recent_data:
        data_summary.append({
            'date': item['timestamp'],
            'close': float(item['close']),
            'volume': int(item.get('volume', 0))
        })
    
    # Calculate statistics
    prices = [float(item['close']) for item in recent_data]
    avg_price = sum(prices) / len(prices)
    min_price = min(prices)
    max_price = max(prices)
    volatility = calculate_volatility(prices)
    
    # Build prompt for Bedrock
    prompt = f"""You are a financial forecasting expert. Analyze the following historical price data for {asset} and provide a detailed {horizon}-day forecast.

Historical Data (Last 30 days):
Average Price: ₹{avg_price:,.2f}
Min Price: ₹{min_price:,.2f}
Max Price: ₹{max_price:,.2f}
Volatility: {volatility:.2f}%

Recent Prices:
{json.dumps(data_summary[:10], indent=2)}

Please provide:
1. Predicted prices for the next {horizon} days (provide at least 5 key dates)
2. Confidence intervals (95% confidence level)
3. Key factors influencing the forecast
4. Risk assessment (Low/Medium/High)
5. Trend direction (Upward/Downward/Stable)

Format your response as JSON with the following structure:
{{
    "predictions": [
        {{"date": "YYYY-MM-DD", "price": 160000.00, "confidence_low": 158000.00, "confidence_high": 162000.00}},
        ...
    ],
    "key_factors": ["factor1", "factor2", ...],
    "risk_level": "Medium",
    "trend": "Upward",
    "summary": "Brief summary of the forecast"
}}
"""
    
    try:
        # Call Bedrock
        response = bedrock.invoke_model(
            modelId=model_id,
            body=json.dumps({
                'anthropic_version': 'bedrock-2023-05-31',
                'max_tokens': 2000,
                'temperature': 0.7,
                'messages': [{
                    'role': 'user',
                    'content': prompt
                }]
            })
        )
        
        # Parse response
        result = json.loads(response['body'].read())
        forecast_text = result['content'][0]['text']
        
        # Try to extract JSON from response
        try:
            # Find JSON in the response
            start_idx = forecast_text.find('{')
            end_idx = forecast_text.rfind('}') + 1
            if start_idx != -1 and end_idx > start_idx:
                forecast_json = json.loads(forecast_text[start_idx:end_idx])
                return forecast_json
            else:
                # Return structured response with text
                return {
                    'predictions': generate_simple_predictions(avg_price, horizon),
                    'key_factors': ['Historical trends', 'Market volatility'],
                    'risk_level': 'Medium',
                    'trend': 'Stable',
                    'summary': forecast_text[:500]
                }
        except json.JSONDecodeError:
            # Fallback: return text response
            return {
                'predictions': generate_simple_predictions(avg_price, horizon),
                'key_factors': ['Historical trends'],
                'risk_level': 'Medium',
                'trend': 'Stable',
                'summary': forecast_text[:500]
            }
            
    except Exception as e:
        print(f"Bedrock error: {str(e)}")
        # Fallback to simple forecast
        return {
            'predictions': generate_simple_predictions(avg_price, horizon),
            'key_factors': ['Historical average'],
            'risk_level': 'Medium',
            'trend': 'Stable',
            'summary': f'Forecast based on historical average of ₹{avg_price:,.2f}'
        }


def generate_simple_predictions(base_price, horizon):
    """Generate simple predictions as fallback"""
    predictions = []
    current_date = datetime.now()
    
    for i in range(min(horizon, 10)):  # Generate up to 10 predictions
        date = current_date + timedelta(days=i+1)
        # Simple prediction with small random variation
        variation = (i % 3 - 1) * 0.01  # -1%, 0%, +1%
        price = base_price * (1 + variation)
        
        predictions.append({
            'date': date.strftime('%Y-%m-%d'),
            'price': round(price, 2),
            'confidence_low': round(price * 0.98, 2),
            'confidence_high': round(price * 1.02, 2)
        })
    
    return predictions


def calculate_volatility(prices):
    """Calculate price volatility"""
    if len(prices) < 2:
        return 0.0
    
    returns = []
    for i in range(1, len(prices)):
        ret = (prices[i] - prices[i-1]) / prices[i-1]
        returns.append(ret)
    
    # Standard deviation of returns
    mean_return = sum(returns) / len(returns)
    variance = sum((r - mean_return) ** 2 for r in returns) / len(returns)
    volatility = (variance ** 0.5) * 100  # Convert to percentage
    
    return round(volatility, 2)


def store_forecast(asset, forecast_result, horizon):
    """Store forecast in DynamoDB"""
    try:
        ttl = int((datetime.now() + timedelta(days=1)).timestamp())
        
        forecasts_table.put_item(
            Item={
                'asset': asset,
                'timestamp': datetime.now().isoformat(),
                'horizon': horizon,
                'forecast': forecast_result,
                'ttl': ttl
            }
        )
    except Exception as e:
        print(f"Error storing forecast: {str(e)}")


def get_model_id(model_choice):
    """Get Bedrock model ID"""
    models = {
        'claude-3-sonnet': 'anthropic.claude-3-sonnet-20240229-v1:0',
        'claude-3-haiku': 'anthropic.claude-3-haiku-20240307-v1:0',
        'titan-text': 'amazon.titan-text-premier-v1:0'
    }
    return models.get(model_choice, models['claude-3-haiku'])


def error_response(status_code, message):
    """Return error response"""
    return {
        'statusCode': status_code,
        'headers': {
            'Content-Type': 'application/json',
            'Access-Control-Allow-Origin': '*'
        },
        'body': json.dumps({
            'error': message,
            'timestamp': datetime.now().isoformat()
        })
    }


def decimal_default(obj):
    """JSON serializer for Decimal objects"""
    if isinstance(obj, Decimal):
        return float(obj)
    raise TypeError(f"Object of type {type(obj)} is not JSON serializable")
