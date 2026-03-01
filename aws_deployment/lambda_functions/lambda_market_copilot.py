"""
AWS Lambda Function: Market Copilot with Amazon Q Business
Provides intelligent market insights using Amazon Q
"""

import json
import boto3
from datetime import datetime
from decimal import Decimal

# Initialize AWS clients
bedrock = boto3.client('bedrock-runtime', region_name='us-east-1')
dynamodb = boto3.resource('dynamodb', region_name='us-east-1')

# DynamoDB tables
price_history_table = dynamodb.Table('PriceHistory')
competitive_pricing_table = dynamodb.Table('CompetitivePricing')

def decimal_default(obj):
    """JSON serializer for Decimal objects"""
    if isinstance(obj, Decimal):
        return float(obj)
    raise TypeError

def lambda_handler(event, context):
    """
    Market Copilot Chat Handler
    
    Request body:
    {
        "message": "What are the gold price trends?",
        "session_id": "optional-session-id"
    }
    """
    
    try:
        # Parse request
        body = json.loads(event.get('body', '{}'))
        user_message = body.get('message', '').strip()
        session_id = body.get('session_id', f"session-{datetime.now().timestamp()}")
        
        if not user_message:
            return error_response(400, 'Message is required')
        
        # Get context data from DynamoDB
        context_data = get_market_context()
        
        # Generate response using Amazon Bedrock (Claude)
        response_text = generate_copilot_response(user_message, context_data)
        
        return {
            'statusCode': 200,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Headers': 'Content-Type',
                'Access-Control-Allow-Methods': 'POST,OPTIONS'
            },
            'body': json.dumps({
                'response': response_text,
                'session_id': session_id,
                'timestamp': datetime.now().isoformat(),
                'context_used': {
                    'gold_price': context_data.get('gold_price'),
                    'silver_price': context_data.get('silver_price'),
                    'products_count': len(context_data.get('products', []))
                }
            }, default=decimal_default)
        }
    
    except Exception as e:
        print(f"Error: {str(e)}")
        import traceback
        traceback.print_exc()
        return error_response(500, str(e))

def get_market_context():
    """Fetch current market data for context"""
    context = {}
    
    try:
        # Get latest Gold price
        gold_response = price_history_table.query(
            KeyConditionExpression='asset = :asset',
            ExpressionAttributeValues={':asset': 'GOLD'},
            ScanIndexForward=False,
            Limit=30  # Last 30 days
        )
        
        if gold_response['Items']:
            gold_prices = [float(item['close']) for item in gold_response['Items']]
            context['gold_price'] = gold_prices[0]
            context['gold_avg_30d'] = sum(gold_prices) / len(gold_prices)
            context['gold_trend'] = 'up' if gold_prices[0] > context['gold_avg_30d'] else 'down'
            context['gold_change_30d'] = ((gold_prices[0] - gold_prices[-1]) / gold_prices[-1]) * 100
        
        # Get latest Silver price
        silver_response = price_history_table.query(
            KeyConditionExpression='asset = :asset',
            ExpressionAttributeValues={':asset': 'SILVER'},
            ScanIndexForward=False,
            Limit=30
        )
        
        if silver_response['Items']:
            silver_prices = [float(item['close']) for item in silver_response['Items']]
            context['silver_price'] = silver_prices[0]
            context['silver_avg_30d'] = sum(silver_prices) / len(silver_prices)
            context['silver_trend'] = 'up' if silver_prices[0] > context['silver_avg_30d'] else 'down'
            context['silver_change_30d'] = ((silver_prices[0] - silver_prices[-1]) / silver_prices[-1]) * 100
        
        # Get product pricing data
        products_response = competitive_pricing_table.scan(Limit=10)
        context['products'] = products_response.get('Items', [])
        
        # Calculate best deals
        if context['products']:
            deals = []
            for product in context['products']:
                if 'prices' in product:
                    prices = product['prices']
                    if isinstance(prices, dict):
                        price_values = [float(p) for p in prices.values() if isinstance(p, (int, float, Decimal))]
                        if price_values:
                            min_price = min(price_values)
                            max_price = max(price_values)
                            savings = max_price - min_price
                            savings_pct = (savings / max_price) * 100
                            deals.append({
                                'product': product.get('product_name', 'Unknown'),
                                'savings': savings,
                                'savings_pct': savings_pct
                            })
            
            context['best_deals'] = sorted(deals, key=lambda x: x['savings'], reverse=True)[:3]
    
    except Exception as e:
        print(f"Error getting context: {str(e)}")
    
    return context

def generate_copilot_response(user_message, context_data):
    """Generate intelligent response using Amazon Bedrock Claude"""
    
    # Build context prompt
    context_prompt = f"""You are an AI Market Copilot for a retail intelligence platform. You help users understand market trends, pricing, and make data-driven decisions.

Current Market Data:
- Gold Price: ₹{context_data.get('gold_price', 'N/A'):,.2f} (30-day trend: {context_data.get('gold_trend', 'N/A')}, change: {context_data.get('gold_change_30d', 0):.2f}%)
- Silver Price: ₹{context_data.get('silver_price', 'N/A'):,.2f} (30-day trend: {context_data.get('silver_trend', 'N/A')}, change: {context_data.get('silver_change_30d', 0):.2f}%)
- Products Tracked: {len(context_data.get('products', []))}
"""
    
    if context_data.get('best_deals'):
        context_prompt += "\nTop Savings Opportunities:\n"
        for deal in context_data['best_deals']:
            context_prompt += f"- {deal['product']}: Save ₹{deal['savings']:,.2f} ({deal['savings_pct']:.1f}%)\n"
    
    context_prompt += f"\nUser Question: {user_message}\n\nProvide a helpful, concise response based on the data above. Use Indian Rupee (₹) for prices."
    
    try:
        # Call Amazon Bedrock Claude
        model_id = "anthropic.claude-3-haiku-20240307-v1:0"
        
        request_body = {
            "anthropic_version": "bedrock-2023-05-31",
            "max_tokens": 1000,
            "messages": [
                {
                    "role": "user",
                    "content": context_prompt
                }
            ],
            "temperature": 0.7
        }
        
        response = bedrock.invoke_model(
            modelId=model_id,
            body=json.dumps(request_body)
        )
        
        response_body = json.loads(response['body'].read())
        assistant_message = response_body['content'][0]['text']
        
        return assistant_message
    
    except Exception as e:
        print(f"Error calling Bedrock: {str(e)}")
        # Fallback to rule-based responses
        return generate_fallback_response(user_message, context_data)

def generate_fallback_response(user_message, context_data):
    """Fallback rule-based responses if Bedrock fails"""
    
    message_lower = user_message.lower()
    
    if 'gold' in message_lower and 'trend' in message_lower:
        gold_price = context_data.get('gold_price', 0)
        gold_trend = context_data.get('gold_trend', 'stable')
        gold_change = context_data.get('gold_change_30d', 0)
        return f"Gold prices are currently at ₹{gold_price:,.2f}. The 30-day trend is {gold_trend} with a {gold_change:+.2f}% change. {'Prices are rising, which could indicate increased demand or inflation concerns.' if gold_trend == 'up' else 'Prices are declining, which might suggest reduced demand or market stability.'}"
    
    elif 'silver' in message_lower and 'trend' in message_lower:
        silver_price = context_data.get('silver_price', 0)
        silver_trend = context_data.get('silver_trend', 'stable')
        silver_change = context_data.get('silver_change_30d', 0)
        return f"Silver prices are currently at ₹{silver_price:,.2f}. The 30-day trend is {silver_trend} with a {silver_change:+.2f}% change. Silver often follows gold trends but with higher volatility."
    
    elif 'best deal' in message_lower or 'savings' in message_lower:
        if context_data.get('best_deals'):
            deals_text = "Here are the top savings opportunities:\n\n"
            for i, deal in enumerate(context_data['best_deals'], 1):
                deals_text += f"{i}. {deal['product']}: Save ₹{deal['savings']:,.2f} ({deal['savings_pct']:.1f}%)\n"
            return deals_text
        return "I don't have current deal information available."
    
    elif 'compare' in message_lower or 'price' in message_lower:
        return f"I can help you compare prices across 6 major platforms: Amazon, Flipkart, Zepto, Blinkit, BigBasket, and Swiggy Instamart. We're currently tracking {len(context_data.get('products', []))} products. What specific product would you like to compare?"
    
    elif 'market summary' in message_lower or 'summary' in message_lower:
        gold_price = context_data.get('gold_price', 0)
        silver_price = context_data.get('silver_price', 0)
        return f"""Market Summary:

📈 Precious Metals:
• Gold: ₹{gold_price:,.2f} ({context_data.get('gold_trend', 'stable')} trend)
• Silver: ₹{silver_price:,.2f} ({context_data.get('silver_trend', 'stable')} trend)

💰 Retail Intelligence:
• Products tracked: {len(context_data.get('products', []))}
• Platforms monitored: 6 (Amazon, Flipkart, Zepto, Blinkit, BigBasket, Swiggy)

The market shows {'positive momentum' if context_data.get('gold_trend') == 'up' else 'stable conditions'} with opportunities for savings across multiple product categories."""
    
    else:
        return f"""I'm your AI Market Copilot! I can help you with:

• Price forecasting and trends (Gold, Silver, ETF)
• Competitive pricing analysis across 6 platforms
• Product comparisons and best deals
• Market insights and recommendations

Current market snapshot:
• Gold: ₹{context_data.get('gold_price', 0):,.2f}
• Silver: ₹{context_data.get('silver_price', 0):,.2f}
• Products tracked: {len(context_data.get('products', []))}

What would you like to know?"""

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
