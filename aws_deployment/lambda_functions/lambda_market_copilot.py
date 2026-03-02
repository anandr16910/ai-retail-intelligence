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
        products_response = competitive_pricing_table.scan()
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
    """Generate intelligent response using Amazon Bedrock Nova"""
    
    # Build detailed context prompt with ALL product data
    context_prompt = f"""You are an expert AI Market Copilot for retail intelligence. Provide accurate, data-driven market insights.

MARKET DATA (February 2026):

Gold (24K): ₹{context_data.get('gold_price', 0):,.2f}
- 30-day average: ₹{context_data.get('gold_avg_30d', 0):,.2f}
- Trend: {context_data.get('gold_trend', 'stable').upper()}
- 30-day change: {context_data.get('gold_change_30d', 0):+.2f}%

Silver: ₹{context_data.get('silver_price', 0):,.2f}
- 30-day average: ₹{context_data.get('silver_avg_30d', 0):,.2f}
- Trend: {context_data.get('silver_trend', 'stable').upper()}
- 30-day change: {context_data.get('silver_change_30d', 0):+.2f}%

PRODUCTS DATABASE ({len(context_data.get('products', []))} products):
"""
    
    # Add ALL product details to context
    products = context_data.get('products', [])
    if products:
        for product in products:
            name = product.get('product_name', 'Unknown')
            prices = product.get('prices', {})
            
            if isinstance(prices, dict):
                from decimal import Decimal
                price_values = {k: float(v) for k, v in prices.items() if isinstance(v, (int, float, Decimal))}
                
                if price_values:
                    min_price = min(price_values.values())
                    best_platform = [k for k, v in price_values.items() if v == min_price][0]
                    
                    context_prompt += f"\n{name}:\n"
                    context_prompt += f"  Best: ₹{min_price:,.0f} on {best_platform}\n"
                    context_prompt += f"  Prices: "
                    context_prompt += ", ".join([f"{k}=₹{v:,.0f}" for k, v in sorted(price_values.items(), key=lambda x: x[1])])
                    context_prompt += "\n"
    
    context_prompt += "\nPlatforms: Amazon, Flipkart, Zepto, Blinkit, BigBasket, Swiggy\n"
    
    if context_data.get('best_deals'):
        context_prompt += "\nTOP SAVINGS:\n"
        for i, deal in enumerate(context_data['best_deals'][:3], 1):
            context_prompt += f"{i}. {deal['product']}: Save ₹{deal['savings']:,.2f} ({deal['savings_pct']:.1f}%)\n"
    
    context_prompt += f"""
Question: {user_message}

Provide a helpful, specific answer using the product data above. Use ₹ for prices. Be concise (2-4 sentences for simple questions).

Answer:"""
    
    try:
        # Call Amazon Bedrock Nova Lite (no approval needed!)
        model_id = "amazon.nova-lite-v1:0"
        
        request_body = {
            "messages": [
                {
                    "role": "user",
                    "content": [{"text": context_prompt}]
                }
            ],
            "inferenceConfig": {
                "max_new_tokens": 2000,
                "temperature": 0.5,
                "topP": 0.9
            }
        }
        
        response = bedrock.invoke_model(
            modelId=model_id,
            body=json.dumps(request_body)
        )
        
        response_body = json.loads(response['body'].read())
        assistant_message = response_body['output']['message']['content'][0]['text']
        
        return assistant_message
    
    except Exception as e:
        print(f"Error calling Bedrock: {str(e)}")
        # Fallback to rule-based responses
        return generate_fallback_response(user_message, context_data)

def generate_fallback_response(user_message, context_data):
    """Enhanced rule-based responses with real data"""
    
    message_lower = user_message.lower()
    
    # Gold-related queries
    if 'gold' in message_lower:
        gold_price = context_data.get('gold_price', 0)
        gold_trend = context_data.get('gold_trend', 'stable')
        gold_change = context_data.get('gold_change_30d', 0)
        gold_avg = context_data.get('gold_avg_30d', 0)
        
        response = f"**Gold Market Analysis (Feb 2026)**\n\n"
        response += f"📊 Current Price: ₹{gold_price:,.2f}\n"
        response += f"📈 30-Day Average: ₹{gold_avg:,.2f}\n"
        response += f"📉 30-Day Change: {gold_change:+.2f}%\n"
        response += f"🎯 Trend: {gold_trend.upper()}\n\n"
        
        if 'invest' in message_lower or 'buy' in message_lower or 'should i' in message_lower:
            if gold_trend == 'down':
                response += f"**Investment Insight:** Gold prices are currently {gold_change:.2f}% below the 30-day average. This could present a buying opportunity if you believe in long-term value. However, the downward trend suggests waiting for stabilization might be prudent."
            else:
                response += f"**Investment Insight:** Gold prices are trending {gold_trend} with a {gold_change:+.2f}% change. Consider your investment timeline and risk tolerance. Gold typically serves as a hedge against inflation and economic uncertainty."
        elif 'trend' in message_lower or 'forecast' in message_lower:
            response += f"**Trend Analysis:** The 30-day trend shows prices are {gold_trend}. "
            if gold_change < -2:
                response += "Significant decline observed, which may indicate reduced demand or market correction."
            elif gold_change > 2:
                response += "Strong upward momentum, possibly driven by inflation concerns or geopolitical factors."
            else:
                response += "Relatively stable movement, suggesting balanced market conditions."
        else:
            response += f"Gold is currently {'below' if gold_price < gold_avg else 'above'} its 30-day average, indicating {'potential value' if gold_price < gold_avg else 'premium pricing'}."
        
        return response
    
    # Silver-related queries
    elif 'silver' in message_lower:
        silver_price = context_data.get('silver_price', 0)
        silver_trend = context_data.get('silver_trend', 'stable')
        silver_change = context_data.get('silver_change_30d', 0)
        silver_avg = context_data.get('silver_avg_30d', 0)
        
        response = f"**Silver Market Analysis (Feb 2026)**\n\n"
        response += f"📊 Current Price: ₹{silver_price:,.2f}\n"
        response += f"📈 30-Day Average: ₹{silver_avg:,.2f}\n"
        response += f"📉 30-Day Change: {silver_change:+.2f}%\n"
        response += f"🎯 Trend: {silver_trend.upper()}\n\n"
        
        if 'invest' in message_lower or 'buy' in message_lower:
            response += f"**Investment Insight:** Silver is trading at ₹{silver_price:,.2f}, {silver_change:+.2f}% from 30 days ago. Silver typically has higher volatility than gold but also offers industrial demand drivers. "
            if silver_trend == 'down':
                response += "Current downtrend may offer entry points for long-term investors."
            else:
                response += "Upward trend suggests strong market sentiment."
        else:
            response += f"Silver shows a {silver_trend} trend with {'significant' if abs(silver_change) > 3 else 'moderate'} price movement."
        
        return response
    
    # Comparison queries
    elif ('compare' in message_lower or 'vs' in message_lower or 'versus' in message_lower) and ('gold' in message_lower or 'silver' in message_lower):
        gold_price = context_data.get('gold_price', 0)
        silver_price = context_data.get('silver_price', 0)
        gold_change = context_data.get('gold_change_30d', 0)
        silver_change = context_data.get('silver_change_30d', 0)
        
        response = f"**Gold vs Silver Comparison (Feb 2026)**\n\n"
        response += f"🥇 Gold: ₹{gold_price:,.2f} ({gold_change:+.2f}% 30-day)\n"
        response += f"🥈 Silver: ₹{silver_price:,.2f} ({silver_change:+.2f}% 30-day)\n\n"
        response += f"**Performance:** "
        
        if abs(gold_change) > abs(silver_change):
            response += f"Gold showing more volatility ({abs(gold_change):.2f}% vs {abs(silver_change):.2f}%).\n"
        else:
            response += f"Silver showing more volatility ({abs(silver_change):.2f}% vs {abs(gold_change):.2f}%).\n"
        
        response += f"\n**Recommendation:** "
        if gold_change < 0 and silver_change < 0:
            response += "Both metals are declining. Consider waiting for trend reversal or dollar-cost averaging."
        elif gold_change > silver_change:
            response += "Gold outperforming silver. Gold may be better for stability, silver for growth potential."
        else:
            response += "Silver outperforming gold. Silver offers higher risk-reward ratio."
        
        return response
    
    # Best deals queries
    elif 'best deal' in message_lower or 'savings' in message_lower or 'discount' in message_lower:
        if context_data.get('best_deals'):
            response = "**🔥 Top Savings Opportunities**\n\n"
            for i, deal in enumerate(context_data['best_deals'], 1):
                response += f"{i}. **{deal['product']}**\n"
                response += f"   💰 Save: ₹{deal['savings']:,.2f} ({deal['savings_pct']:.1f}% discount)\n\n"
            response += "These are real-time price differences across Amazon, Flipkart, Zepto, Blinkit, BigBasket, and Swiggy Instamart."
            return response
        return "I don't have current deal information available. Please check back later."
    
    # Specific product queries (olive oil, printer, fridge, etc.)
    elif any(keyword in message_lower for keyword in ['olive oil', 'olive', 'printer', 'fridge', 'refrigerator', 'washing machine', 'washer', 'microwave', 'dishwasher', 'ac', 'air conditioner', 'figaro', 'borges', 'hp', 'canon', 'samsung', 'lg', 'whirlpool', 'godrej', 'haier', 'bosch']):
        products = context_data.get('products', [])
        
        # Search for matching products
        matching_products = []
        search_keywords = ['olive', 'printer', 'fridge', 'refrigerator', 'washing', 'microwave', 'dishwasher', 'figaro', 'borges', 'hp', 'canon', 'samsung', 'lg', 'whirlpool', 'godrej', 'haier', 'bosch', 'ac']
        
        for product in products:
            product_name = product.get('product_name', '').lower()
            if any(keyword in product_name for keyword in search_keywords if keyword in message_lower):
                matching_products.append(product)
        
        if matching_products:
            response = f"**Found {len(matching_products)} Product(s)**\n\n"
            
            for product in matching_products[:5]:  # Show top 5 matches
                name = product.get('product_name', 'Unknown')
                prices = product.get('prices', {})
                
                if isinstance(prices, dict):
                    price_values = {k: float(v) for k, v in prices.items() if isinstance(v, (int, float, Decimal))}
                    
                    if price_values:
                        min_price = min(price_values.values())
                        max_price = max(price_values.values())
                        best_platform = [k for k, v in price_values.items() if v == min_price][0]
                        savings = max_price - min_price
                        savings_pct = (savings / max_price) * 100
                        
                        response += f"**{name}**\n"
                        response += f"💰 Best Price: ₹{min_price:,.0f} on {best_platform}\n"
                        response += f"💵 Save: ₹{savings:,.0f} ({savings_pct:.1f}%)\n\n"
                        response += f"All Prices:\n"
                        for platform, price in sorted(price_values.items(), key=lambda x: x[1]):
                            response += f"  • {platform}: ₹{price:,.0f}\n"
                        response += "\n"
            
            return response
        else:
            response = f"**Product Not Found in Database**\n\n"
            response += f"I currently track {len(products)} products:\n"
            response += f"• Home Appliances (Fridges, Washing Machines, Microwaves, ACs, Dishwashers)\n"
            response += f"• Electronics (Printers)\n"
            response += f"• Groceries (Olive Oil)\n\n"
            response += f"**Note:** I can only compare prices for products in my database. I cannot fetch live prices from Amazon.in or other websites.\n\n"
            response += f"To add this product, update the DynamoDB CompetitivePricing table."
            return response
    
    # Product comparison queries
    elif 'compare' in message_lower and ('price' in message_lower or 'product' in message_lower or 'fridge' in message_lower or 'washing' in message_lower):
        response = f"**Product Price Comparison**\n\n"
        response += f"I can compare prices across 6 major platforms:\n"
        response += f"• Amazon\n• Flipkart\n• Zepto\n• Blinkit\n• BigBasket\n• Swiggy Instamart\n\n"
        response += f"Currently tracking {len(context_data.get('products', []))} products.\n\n"
        
        if context_data.get('best_deals'):
            response += f"**Top Deal Right Now:**\n"
            top_deal = context_data['best_deals'][0]
            response += f"{top_deal['product']} - Save ₹{top_deal['savings']:,.2f} ({top_deal['savings_pct']:.1f}%)"
        
        return response
    
    # Market summary queries
    elif 'market summary' in message_lower or 'summary' in message_lower or 'overview' in message_lower:
        gold_price = context_data.get('gold_price', 0)
        silver_price = context_data.get('silver_price', 0)
        gold_change = context_data.get('gold_change_30d', 0)
        silver_change = context_data.get('silver_change_30d', 0)
        
        response = f"**Market Summary - February 2026**\n\n"
        response += f"📊 **Precious Metals:**\n"
        response += f"• Gold: ₹{gold_price:,.2f} ({gold_change:+.2f}% 30-day)\n"
        response += f"• Silver: ₹{silver_price:,.2f} ({silver_change:+.2f}% 30-day)\n\n"
        response += f"💰 **Retail Intelligence:**\n"
        response += f"• Products tracked: {len(context_data.get('products', []))}\n"
        response += f"• Platforms monitored: 6\n\n"
        
        if context_data.get('best_deals'):
            response += f"🔥 **Best Opportunity:**\n"
            top_deal = context_data['best_deals'][0]
            response += f"{top_deal['product']} - Save ₹{top_deal['savings']:,.2f}\n\n"
        
        response += f"**Market Sentiment:** "
        if gold_change < 0 and silver_change < 0:
            response += "Bearish - Both metals declining"
        elif gold_change > 0 and silver_change > 0:
            response += "Bullish - Both metals rising"
        else:
            response += "Mixed - Divergent trends"
        
        return response
    
    # Default helpful response
    else:
        gold_price = context_data.get('gold_price', 0)
        silver_price = context_data.get('silver_price', 0)
        
        response = f"**AI Market Copilot - How Can I Help?**\n\n"
        response += f"I can assist you with:\n\n"
        response += f"📈 **Price Analysis**\n"
        response += f"• Gold trends and forecasts\n"
        response += f"• Silver market insights\n"
        response += f"• Investment recommendations\n\n"
        response += f"💰 **Retail Intelligence**\n"
        response += f"• Product price comparisons\n"
        response += f"• Best deals across 6 platforms\n"
        response += f"• Savings opportunities\n\n"
        response += f"**Current Snapshot:**\n"
        response += f"• Gold: ₹{gold_price:,.2f}\n"
        response += f"• Silver: ₹{silver_price:,.2f}\n"
        response += f"• Products: {len(context_data.get('products', []))} tracked\n\n"
        response += f"Try asking: \"What are gold price trends?\" or \"Show me best deals\""
        
        return response

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
