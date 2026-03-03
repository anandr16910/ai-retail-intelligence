"""
AWS Lambda Function: Hybrid Price Forecasting
Combines Amazon Forecast (time series ML) with Amazon Bedrock (generative AI)
"""
import json
import boto3
from datetime import datetime, timedelta
from decimal import Decimal

# Initialize AWS clients
forecast = boto3.client('forecast', region_name='us-east-1')
forecastquery = boto3.client('forecastquery', region_name='us-east-1')
bedrock = boto3.client('bedrock-runtime', region_name='us-east-1')
dynamodb = boto3.resource('dynamodb', region_name='us-east-1')


def lambda_handler(event, context):
    """
    Hybrid forecasting: Amazon Forecast + Amazon Bedrock
    
    Request body:
    {
        "symbol": "GOLD|SILVER|ETF",
        "horizon": 7,
        "model": "hybrid|forecast-only|bedrock-only"
    }
    """
    try:
        # Parse request
        body = json.loads(event.get('body', '{}'))
        symbol = body.get('symbol', 'GOLD').upper()
        horizon = int(body.get('horizon', 7))
        model_type = body.get('model', 'hybrid')
        
        # Validate inputs
        if symbol not in ['GOLD', 'SILVER', 'ETF']:
            return error_response(400, 'Invalid symbol. Use GOLD, SILVER, or ETF')
        
        if horizon < 1 or horizon > 90:
            return error_response(400, 'Horizon must be between 1 and 90 days')
        
        # Get historical data for context
        historical_data = get_historical_data(symbol)
        
        # Generate forecast based on model type
        if model_type == 'forecast-only':
            result = forecast_only(symbol, horizon, historical_data)
        elif model_type == 'bedrock-only':
            result = bedrock_only(symbol, horizon, historical_data)
        else:  # hybrid (default)
            result = hybrid_forecast(symbol, horizon, historical_data)
        
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
                'success': True,
                'symbol': symbol,
                'horizon': horizon,
                'model_type': model_type,
                'forecast': result,
                'timestamp': datetime.now().isoformat()
            }, default=decimal_default)
        }
        
    except Exception as e:
        print(f"Error: {str(e)}")
        return error_response(500, f'Internal server error: {str(e)}')


def hybrid_forecast(symbol, horizon, historical_data):
    """
    Hybrid approach: Amazon Forecast + Amazon Bedrock
    1. Get numerical predictions from Amazon Forecast
    2. Get AI explanation and insights from Amazon Bedrock
    """
    
    # Step 1: Get Amazon Forecast predictions (if available)
    forecast_predictions = get_amazon_forecast_predictions(symbol, horizon)
    
    # Step 2: Get Bedrock AI analysis
    bedrock_analysis = get_bedrock_analysis(symbol, horizon, historical_data, forecast_predictions)
    
    # Step 3: Combine results
    return {
        'method': 'hybrid',
        'forecast_ml': forecast_predictions,
        'ai_analysis': bedrock_analysis,
        'combined_insights': {
            'predictions': forecast_predictions.get('predictions', []),
            'confidence': forecast_predictions.get('confidence', 'medium'),
            'explanation': bedrock_analysis.get('explanation', ''),
            'recommendations': bedrock_analysis.get('recommendations', []),
            'risk_factors': bedrock_analysis.get('risk_factors', []),
            'market_sentiment': bedrock_analysis.get('sentiment', 'neutral')
        }
    }


def forecast_only(symbol, horizon, historical_data):
    """Amazon Forecast only (time series ML)"""
    predictions = get_amazon_forecast_predictions(symbol, horizon)
    
    return {
        'method': 'forecast_ml',
        'predictions': predictions.get('predictions', []),
        'quantiles': predictions.get('quantiles', {}),
        'confidence': predictions.get('confidence', 'medium'),
        'model_info': 'Amazon Forecast AutoML'
    }


def bedrock_only(symbol, horizon, historical_data):
    """Amazon Bedrock only (generative AI)"""
    analysis = get_bedrock_analysis(symbol, horizon, historical_data, None)
    
    return {
        'method': 'bedrock_ai',
        'predictions': analysis.get('predictions', []),
        'explanation': analysis.get('explanation', ''),
        'recommendations': analysis.get('recommendations', []),
        'sentiment': analysis.get('sentiment', 'neutral'),
        'model_info': 'Amazon Nova Lite'
    }


def get_amazon_forecast_predictions(symbol, horizon):
    """
    Get predictions from Amazon Forecast
    Note: Requires pre-trained Forecast predictor
    """
    try:
        # Forecast ARN (would be created during setup)
        forecast_arn = f"arn:aws:forecast:us-east-1:439786465522:forecast/{symbol.lower()}-forecast"
        
        # Query forecast
        response = forecastquery.query_forecast(
            ForecastArn=forecast_arn,
            Filters={
                "item_id": symbol
            }
        )
        
        # Extract predictions
        predictions = []
        quantiles = {'p10': [], 'p50': [], 'p90': []}
        
        if 'Forecast' in response and 'Predictions' in response['Forecast']:
            forecast_data = response['Forecast']['Predictions']
            
            # Extract quantile predictions
            for quantile, values in forecast_data.items():
                if quantile == 'p10':
                    quantiles['p10'] = [float(v['Value']) for v in values[:horizon]]
                elif quantile == 'p50':
                    quantiles['p50'] = [float(v['Value']) for v in values[:horizon]]
                    predictions = quantiles['p50']  # Use median as main prediction
                elif quantile == 'p90':
                    quantiles['p90'] = [float(v['Value']) for v in values[:horizon]]
        
        return {
            'available': True,
            'predictions': predictions,
            'quantiles': quantiles,
            'confidence': calculate_confidence(quantiles),
            'source': 'Amazon Forecast'
        }
        
    except Exception as e:
        print(f"Amazon Forecast not available: {str(e)}")
        # Fallback: Use simple moving average
        return get_fallback_predictions(symbol, horizon)


def get_fallback_predictions(symbol, horizon):
    """Fallback predictions using simple moving average"""
    try:
        table = dynamodb.Table('RetailPrices')
        
        # Get last 30 days of data
        response = table.query(
            KeyConditionExpression='symbol = :symbol',
            ExpressionAttributeValues={':symbol': symbol},
            ScanIndexForward=False,
            Limit=30
        )
        
        if not response['Items']:
            return {'available': False, 'predictions': [], 'source': 'fallback'}
        
        # Calculate moving average
        prices = [float(item['price']) for item in response['Items']]
        avg_price = sum(prices) / len(prices)
        
        # Simple trend calculation
        recent_avg = sum(prices[:7]) / min(7, len(prices))
        trend = (recent_avg - avg_price) / avg_price if avg_price > 0 else 0
        
        # Generate predictions with trend
        predictions = []
        for i in range(horizon):
            predicted_price = avg_price * (1 + trend * (i + 1) / horizon)
            predictions.append(round(predicted_price, 2))
        
        return {
            'available': True,
            'predictions': predictions,
            'quantiles': {
                'p10': [p * 0.95 for p in predictions],
                'p50': predictions,
                'p90': [p * 1.05 for p in predictions]
            },
            'confidence': 'medium',
            'source': 'Moving Average (Fallback)'
        }
        
    except Exception as e:
        print(f"Fallback prediction error: {str(e)}")
        return {'available': False, 'predictions': [], 'source': 'error'}


def get_bedrock_analysis(symbol, horizon, historical_data, forecast_predictions):
    """Get AI analysis and explanation from Amazon Bedrock"""
    
    # Prepare context for Bedrock
    current_price = historical_data[-1]['price'] if historical_data else 0
    price_trend = calculate_trend(historical_data)
    
    # Build prompt
    prompt = f"""You are an expert financial analyst specializing in precious metals and commodities.

Asset: {symbol}
Current Price: ₹{current_price:,.2f}
Recent Trend: {price_trend}
Forecast Horizon: {horizon} days

"""
    
    if forecast_predictions and forecast_predictions.get('available'):
        predictions = forecast_predictions.get('predictions', [])
        prompt += f"""Amazon Forecast ML Predictions:
- Day 1: ₹{predictions[0]:,.2f}
- Day {horizon}: ₹{predictions[-1]:,.2f}
- Average: ₹{sum(predictions)/len(predictions):,.2f}

"""
    
    prompt += """Provide a comprehensive analysis in JSON format:
{
    "predictions": [list of predicted prices for each day],
    "explanation": "2-3 sentence explanation of the forecast",
    "recommendations": ["recommendation 1", "recommendation 2"],
    "risk_factors": ["risk 1", "risk 2"],
    "opportunities": ["opportunity 1", "opportunity 2"],
    "sentiment": "bullish|neutral|bearish",
    "confidence_score": 0.85
}

Consider Indian market factors: festivals, GST, seasonal patterns, global trends.
Return ONLY valid JSON, no additional text."""
    
    try:
        # Invoke Bedrock
        response = bedrock.invoke_model(
            modelId='amazon.nova-lite-v1:0',
            body=json.dumps({
                'messages': [{
                    'role': 'user',
                    'content': [{'text': prompt}]
                }],
                'inferenceConfig': {
                    'maxTokens': 1500,
                    'temperature': 0.3
                }
            })
        )
        
        # Parse response
        result = json.loads(response['body'].read())
        analysis_text = result['output']['message']['content'][0]['text']
        
        # Extract JSON
        start_idx = analysis_text.find('{')
        end_idx = analysis_text.rfind('}') + 1
        
        if start_idx != -1 and end_idx > start_idx:
            analysis = json.loads(analysis_text[start_idx:end_idx])
            return analysis
        else:
            return create_fallback_analysis(symbol, current_price)
            
    except Exception as e:
        print(f"Bedrock analysis error: {str(e)}")
        return create_fallback_analysis(symbol, current_price)


def get_historical_data(symbol):
    """Get historical price data from DynamoDB"""
    try:
        table = dynamodb.Table('RetailPrices')
        
        response = table.query(
            KeyConditionExpression='symbol = :symbol',
            ExpressionAttributeValues={':symbol': symbol},
            ScanIndexForward=False,
            Limit=90
        )
        
        return response.get('Items', [])
        
    except Exception as e:
        print(f"Error fetching historical data: {str(e)}")
        return []


def calculate_trend(historical_data):
    """Calculate price trend from historical data"""
    if len(historical_data) < 2:
        return 'stable'
    
    recent_price = float(historical_data[0]['price'])
    old_price = float(historical_data[-1]['price'])
    
    change_pct = ((recent_price - old_price) / old_price) * 100
    
    if change_pct > 2:
        return 'upward'
    elif change_pct < -2:
        return 'downward'
    else:
        return 'stable'


def calculate_confidence(quantiles):
    """Calculate confidence based on quantile spread"""
    if not quantiles or not quantiles.get('p50'):
        return 'medium'
    
    p50 = quantiles['p50'][0]
    p10 = quantiles['p10'][0]
    p90 = quantiles['p90'][0]
    
    spread = (p90 - p10) / p50 if p50 > 0 else 1
    
    if spread < 0.1:
        return 'high'
    elif spread < 0.2:
        return 'medium'
    else:
        return 'low'


def create_fallback_analysis(symbol, current_price):
    """Create fallback analysis when Bedrock fails"""
    return {
        'predictions': [],
        'explanation': f'Analysis for {symbol} at current price ₹{current_price:,.2f}',
        'recommendations': ['Monitor market conditions', 'Consider diversification'],
        'risk_factors': ['Market volatility', 'Global economic conditions'],
        'opportunities': ['Long-term investment potential'],
        'sentiment': 'neutral',
        'confidence_score': 0.70
    }


def decimal_default(obj):
    """JSON serializer for Decimal objects"""
    if isinstance(obj, Decimal):
        return float(obj)
    raise TypeError


def error_response(status_code, message):
    """Return error response"""
    return {
        'statusCode': status_code,
        'headers': {
            'Content-Type': 'application/json',
            'Access-Control-Allow-Origin': '*'
        },
        'body': json.dumps({
            'success': False,
            'error': message,
            'timestamp': datetime.now().isoformat()
        })
    }
