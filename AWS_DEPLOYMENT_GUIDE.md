# AWS Deployment Guide - AI Retail Intelligence Platform

## Architecture Overview

This guide provides a complete AWS deployment architecture using:
- **Amazon Bedrock** - AI/ML for forecasting and market intelligence
- **AWS Lambda** - Serverless compute for API endpoints
- **Amazon API Gateway** - RESTful API management
- **Amazon DynamoDB** - NoSQL database for pricing data
- **Amazon S3** - Storage for historical data and models
- **Amazon EC2** (optional) - For dashboard hosting
- **Amazon CloudWatch** - Monitoring and logging
- **AWS IAM** - Security and access management

## Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                         Users/Clients                            │
└────────────────────────┬────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│                    Amazon CloudFront (CDN)                       │
│                  (Optional - for dashboard)                      │
└────────────────────────┬────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│                    Amazon API Gateway                            │
│              (REST API + WebSocket API)                          │
└────────┬────────────────────────────────────────────────────────┘
         │
         ├──────────────┬──────────────┬──────────────┬───────────┐
         ▼              ▼              ▼              ▼           ▼
    ┌────────┐    ┌────────┐    ┌────────┐    ┌────────┐   ┌────────┐
    │Lambda  │    │Lambda  │    │Lambda  │    │Lambda  │   │Lambda  │
    │Forecast│    │Pricing │    │Copilot │    │Document│   │Data    │
    └────┬───┘    └────┬───┘    └────┬───┘    └────┬───┘   └────┬───┘
         │             │              │              │            │
         ▼             ▼              ▼              ▼            ▼
    ┌─────────────────────────────────────────────────────────────┐
    │                    Amazon Bedrock                            │
    │         (Claude 3, Titan Text, Foundation Models)            │
    └─────────────────────────────────────────────────────────────┘
         │             │              │              │            │
         ▼             ▼              ▼              ▼            ▼
    ┌─────────────────────────────────────────────────────────────┐
    │                    Amazon DynamoDB                           │
    │    (Price Data, Products, User Sessions, Cache)              │
    └─────────────────────────────────────────────────────────────┘
         │             │              │
         ▼             ▼              ▼
    ┌─────────────────────────────────────────────────────────────┐
    │                       Amazon S3                              │
    │  (Historical Data, ML Models, Documents, Backups)            │
    └─────────────────────────────────────────────────────────────┘
```

## Component Breakdown

### 1. Amazon Bedrock (AI/ML Layer)

**Purpose**: Foundation models for forecasting, market analysis, and natural language processing

**Models to Use**:
- **Claude 3 Sonnet**: Complex market analysis, detailed forecasting explanations
- **Claude 3 Haiku**: Fast inference for real-time queries, cost-effective
- **Amazon Titan Text**: Embeddings for document search, text generation

**Use Cases**:
- Price forecasting with explanations
- Market sentiment analysis
- Document parsing and entity extraction
- Natural language queries (Market Copilot)
- Competitive pricing insights

**Cost Optimization**:
- Use Haiku for simple queries (80% cheaper than Sonnet)
- Cache frequently used prompts
- Batch processing for non-real-time requests

### 2. AWS Lambda Functions

**Architecture**: Serverless microservices

#### Lambda Function 1: Price Forecasting
```python
# lambda_forecast.py
import json
import boto3
from datetime import datetime

bedrock = boto3.client('bedrock-runtime')
dynamodb = boto3.resource('dynamodb')

def lambda_handler(event, context):
    """
    Forecast prices using Bedrock and historical data from DynamoDB
    """
    # Parse request
    body = json.loads(event['body'])
    asset = body.get('asset')  # GOLD, SILVER, ETF
    horizon = body.get('horizon', 30)
    
    # Get historical data from DynamoDB
    table = dynamodb.Table('PriceHistory')
    response = table.query(
        KeyConditionExpression='asset = :asset',
        ExpressionAttributeValues={':asset': asset},
        Limit=90,
        ScanIndexForward=False
    )
    
    historical_data = response['Items']
    
    # Call Bedrock for forecasting
    prompt = f"""
    Based on the following historical price data for {asset}, 
    provide a {horizon}-day price forecast with confidence intervals.
    
    Historical Data: {json.dumps(historical_data[-30:])}
    
    Provide:
    1. Predicted prices for next {horizon} days
    2. Confidence intervals (95%)
    3. Key factors influencing the forecast
    4. Risk assessment
    """
    
    bedrock_response = bedrock.invoke_model(
        modelId='anthropic.claude-3-sonnet-20240229-v1:0',
        body=json.dumps({
            'anthropic_version': 'bedrock-2023-05-31',
            'max_tokens': 2000,
            'messages': [{
                'role': 'user',
                'content': prompt
            }]
        })
    )
    
    # Parse Bedrock response
    result = json.loads(bedrock_response['body'].read())
    forecast = result['content'][0]['text']
    
    # Store forecast in DynamoDB
    forecast_table = dynamodb.Table('Forecasts')
    forecast_table.put_item(
        Item={
            'asset': asset,
            'timestamp': datetime.now().isoformat(),
            'horizon': horizon,
            'forecast': forecast,
            'ttl': int(datetime.now().timestamp()) + 86400  # 24 hour TTL
        }
    )
    
    return {
        'statusCode': 200,
        'headers': {
            'Content-Type': 'application/json',
            'Access-Control-Allow-Origin': '*'
        },
        'body': json.dumps({
            'asset': asset,
            'forecast': forecast,
            'timestamp': datetime.now().isoformat()
        })
    }
```

#### Lambda Function 2: Competitive Pricing
```python
# lambda_pricing.py
import json
import boto3

dynamodb = boto3.resource('dynamodb')
bedrock = boto3.client('bedrock-runtime')

def lambda_handler(event, context):
    """
    Compare prices across platforms and provide recommendations
    """
    product_id = event['pathParameters']['product_id']
    
    # Get pricing data from DynamoDB
    table = dynamodb.Table('CompetitivePricing')
    response = table.get_item(Key={'product_id': product_id})
    
    if 'Item' not in response:
        return {
            'statusCode': 404,
            'body': json.dumps({'error': 'Product not found'})
        }
    
    pricing_data = response['Item']
    
    # Use Bedrock for intelligent pricing analysis
    prompt = f"""
    Analyze the following pricing data and provide recommendations:
    
    Product: {pricing_data['product_name']}
    Prices: {json.dumps(pricing_data['prices'])}
    
    Provide:
    1. Best platform to buy from
    2. Potential savings
    3. Price trend analysis
    4. Purchase timing recommendation
    """
    
    bedrock_response = bedrock.invoke_model(
        modelId='anthropic.claude-3-haiku-20240307-v1:0',  # Haiku for cost efficiency
        body=json.dumps({
            'anthropic_version': 'bedrock-2023-05-31',
            'max_tokens': 1000,
            'messages': [{
                'role': 'user',
                'content': prompt
            }]
        })
    )
    
    result = json.loads(bedrock_response['body'].read())
    analysis = result['content'][0]['text']
    
    return {
        'statusCode': 200,
        'headers': {
            'Content-Type': 'application/json',
            'Access-Control-Allow-Origin': '*'
        },
        'body': json.dumps({
            'product': pricing_data,
            'analysis': analysis
        })
    }
```

#### Lambda Function 3: Market Copilot
```python
# lambda_copilot.py
import json
import boto3

bedrock = boto3.client('bedrock-runtime')
dynamodb = boto3.resource('dynamodb')

def lambda_handler(event, context):
    """
    Natural language interface for market queries
    """
    body = json.loads(event['body'])
    query = body.get('query')
    session_id = body.get('session_id')
    
    # Get conversation history from DynamoDB
    sessions_table = dynamodb.Table('ChatSessions')
    session = sessions_table.get_item(Key={'session_id': session_id})
    
    history = session.get('Item', {}).get('history', [])
    
    # Get current market context
    prices_table = dynamodb.Table('CurrentPrices')
    current_prices = prices_table.scan()['Items']
    
    # Build context-aware prompt
    context = f"""
    Current Market Data:
    {json.dumps(current_prices)}
    
    Conversation History:
    {json.dumps(history[-5:])}  # Last 5 messages
    
    User Query: {query}
    
    Provide a helpful, accurate response about the market data.
    """
    
    bedrock_response = bedrock.invoke_model(
        modelId='anthropic.claude-3-haiku-20240307-v1:0',
        body=json.dumps({
            'anthropic_version': 'bedrock-2023-05-31',
            'max_tokens': 1500,
            'messages': [{
                'role': 'user',
                'content': context
            }]
        })
    )
    
    result = json.loads(bedrock_response['body'].read())
    response_text = result['content'][0]['text']
    
    # Update conversation history
    history.append({'query': query, 'response': response_text})
    sessions_table.put_item(
        Item={
            'session_id': session_id,
            'history': history,
            'updated_at': datetime.now().isoformat()
        }
    )
    
    return {
        'statusCode': 200,
        'headers': {
            'Content-Type': 'application/json',
            'Access-Control-Allow-Origin': '*'
        },
        'body': json.dumps({
            'response': response_text,
            'session_id': session_id
        })
    }
```

### 3. Amazon DynamoDB Tables

#### Table 1: PriceHistory
```json
{
  "TableName": "PriceHistory",
  "KeySchema": [
    {"AttributeName": "asset", "KeyType": "HASH"},
    {"AttributeName": "timestamp", "KeyType": "RANGE"}
  ],
  "AttributeDefinitions": [
    {"AttributeName": "asset", "AttributeType": "S"},
    {"AttributeName": "timestamp", "AttributeType": "S"}
  ],
  "BillingMode": "PAY_PER_REQUEST",
  "StreamSpecification": {
    "StreamEnabled": true,
    "StreamViewType": "NEW_AND_OLD_IMAGES"
  }
}
```

**Sample Item**:
```json
{
  "asset": "GOLD",
  "timestamp": "2026-03-01T10:00:00Z",
  "open": 160000.00,
  "high": 161000.00,
  "low": 159500.00,
  "close": 160579.29,
  "volume": 450000
}
```

#### Table 2: CompetitivePricing
```json
{
  "TableName": "CompetitivePricing",
  "KeySchema": [
    {"AttributeName": "product_id", "KeyType": "HASH"}
  ],
  "AttributeDefinitions": [
    {"AttributeName": "product_id", "AttributeType": "S"}
  ],
  "BillingMode": "PAY_PER_REQUEST",
  "GlobalSecondaryIndexes": [
    {
      "IndexName": "CategoryIndex",
      "KeySchema": [
        {"AttributeName": "category", "KeyType": "HASH"}
      ],
      "Projection": {"ProjectionType": "ALL"}
    }
  ]
}
```

**Sample Item**:
```json
{
  "product_id": "PROD001",
  "product_name": "Basmati Rice 5kg",
  "category": "Groceries",
  "prices": {
    "Amazon": 450.00,
    "Flipkart": 485.00,
    "JioMart": 440.00,
    "Blinkit": 515.00,
    "Zepto": 475.00,
    "DMart": 425.00
  },
  "lowest_price": 425.00,
  "highest_price": 515.00,
  "best_platform": "DMart",
  "savings_amount": 90.00,
  "updated_at": "2026-03-01T10:00:00Z"
}
```

#### Table 3: Forecasts
```json
{
  "TableName": "Forecasts",
  "KeySchema": [
    {"AttributeName": "asset", "KeyType": "HASH"},
    {"AttributeName": "timestamp", "KeyType": "RANGE"}
  ],
  "AttributeDefinitions": [
    {"AttributeName": "asset", "AttributeType": "S"},
    {"AttributeName": "timestamp", "AttributeType": "S"}
  ],
  "BillingMode": "PAY_PER_REQUEST",
  "TimeToLiveSpecification": {
    "Enabled": true,
    "AttributeName": "ttl"
  }
}
```

#### Table 4: ChatSessions
```json
{
  "TableName": "ChatSessions",
  "KeySchema": [
    {"AttributeName": "session_id", "KeyType": "HASH"}
  ],
  "AttributeDefinitions": [
    {"AttributeName": "session_id", "AttributeType": "S"}
  ],
  "BillingMode": "PAY_PER_REQUEST",
  "TimeToLiveSpecification": {
    "Enabled": true,
    "AttributeName": "ttl"
  }
}
```

### 4. Amazon S3 Buckets

#### Bucket 1: Historical Data
```
s3://ai-retail-intelligence-data/
├── historical/
│   ├── gold/
│   │   ├── 2024/
│   │   ├── 2025/
│   │   └── 2026/
│   ├── silver/
│   └── etf/
├── models/
│   ├── lstm/
│   ├── prophet/
│   └── ensemble/
└── documents/
    ├── market-reports/
    └── financial-docs/
```

#### Bucket 2: Dashboard Assets
```
s3://ai-retail-intelligence-dashboard/
├── static/
│   ├── css/
│   ├── js/
│   └── images/
└── index.html
```

### 5. Amazon API Gateway

#### REST API Configuration

**Base URL**: `https://api.ai-retail-intelligence.com/v1`

**Endpoints**:

```yaml
/forecast:
  POST:
    summary: Generate price forecast
    parameters:
      - asset: string (GOLD, SILVER, ETF)
      - horizon: integer (1-90 days)
    integration: Lambda (lambda_forecast)
    
/pricing/compare/{product_id}:
  GET:
    summary: Compare prices across platforms
    parameters:
      - product_id: string
    integration: Lambda (lambda_pricing)
    
/pricing/best-deals:
  GET:
    summary: Get best deals
    parameters:
      - limit: integer (default: 10)
    integration: Lambda (lambda_pricing)
    
/copilot/query:
  POST:
    summary: Ask market copilot
    parameters:
      - query: string
      - session_id: string
    integration: Lambda (lambda_copilot)
    
/data/prices:
  GET:
    summary: Get current prices
    integration: Lambda (lambda_data)
```

#### WebSocket API Configuration

**WebSocket URL**: `wss://ws.ai-retail-intelligence.com`

**Routes**:
- `$connect`: Connection handler
- `$disconnect`: Disconnection handler
- `subscribe`: Subscribe to price updates
- `unsubscribe`: Unsubscribe from updates

### 6. IAM Roles and Policies

#### Lambda Execution Role
```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "bedrock:InvokeModel",
        "bedrock:InvokeModelWithResponseStream"
      ],
      "Resource": [
        "arn:aws:bedrock:*::foundation-model/anthropic.claude-3-sonnet-20240229-v1:0",
        "arn:aws:bedrock:*::foundation-model/anthropic.claude-3-haiku-20240307-v1:0",
        "arn:aws:bedrock:*::foundation-model/amazon.titan-text-premier-v1:0"
      ]
    },
    {
      "Effect": "Allow",
      "Action": [
        "dynamodb:GetItem",
        "dynamodb:PutItem",
        "dynamodb:Query",
        "dynamodb:Scan",
        "dynamodb:UpdateItem"
      ],
      "Resource": [
        "arn:aws:dynamodb:*:*:table/PriceHistory",
        "arn:aws:dynamodb:*:*:table/CompetitivePricing",
        "arn:aws:dynamodb:*:*:table/Forecasts",
        "arn:aws:dynamodb:*:*:table/ChatSessions"
      ]
    },
    {
      "Effect": "Allow",
      "Action": [
        "s3:GetObject",
        "s3:PutObject"
      ],
      "Resource": [
        "arn:aws:s3:::ai-retail-intelligence-data/*"
      ]
    },
    {
      "Effect": "Allow",
      "Action": [
        "logs:CreateLogGroup",
        "logs:CreateLogStream",
        "logs:PutLogEvents"
      ],
      "Resource": "arn:aws:logs:*:*:*"
    }
  ]
}
```

## Deployment Steps

### Step 1: Set Up AWS Account and Bedrock Access

```bash
# Configure AWS CLI
aws configure

# Enable Bedrock models (one-time setup)
aws bedrock list-foundation-models --region us-east-1

# Request access to Claude 3 and Titan models in AWS Console
# Go to: Bedrock > Model access > Request access
```

### Step 2: Create DynamoDB Tables

```bash
# Create PriceHistory table
aws dynamodb create-table \
  --table-name PriceHistory \
  --attribute-definitions \
    AttributeName=asset,AttributeType=S \
    AttributeName=timestamp,AttributeType=S \
  --key-schema \
    AttributeName=asset,KeyType=HASH \
    AttributeName=timestamp,KeyType=RANGE \
  --billing-mode PAY_PER_REQUEST \
  --stream-specification StreamEnabled=true,StreamViewType=NEW_AND_OLD_IMAGES

# Create CompetitivePricing table
aws dynamodb create-table \
  --table-name CompetitivePricing \
  --attribute-definitions \
    AttributeName=product_id,AttributeType=S \
  --key-schema \
    AttributeName=product_id,KeyType=HASH \
  --billing-mode PAY_PER_REQUEST

# Create Forecasts table with TTL
aws dynamodb create-table \
  --table-name Forecasts \
  --attribute-definitions \
    AttributeName=asset,AttributeType=S \
    AttributeName=timestamp,AttributeType=S \
  --key-schema \
    AttributeName=asset,KeyType=HASH \
    AttributeName=timestamp,KeyType=RANGE \
  --billing-mode PAY_PER_REQUEST

aws dynamodb update-time-to-live \
  --table-name Forecasts \
  --time-to-live-specification Enabled=true,AttributeName=ttl

# Create ChatSessions table
aws dynamodb create-table \
  --table-name ChatSessions \
  --attribute-definitions \
    AttributeName=session_id,AttributeType=S \
  --key-schema \
    AttributeName=session_id,KeyType=HASH \
  --billing-mode PAY_PER_REQUEST
```

### Step 3: Create S3 Buckets

```bash
# Create data bucket
aws s3 mb s3://ai-retail-intelligence-data

# Create dashboard bucket
aws s3 mb s3://ai-retail-intelligence-dashboard

# Enable versioning
aws s3api put-bucket-versioning \
  --bucket ai-retail-intelligence-data \
  --versioning-configuration Status=Enabled

# Upload historical data
aws s3 sync ./data/ s3://ai-retail-intelligence-data/historical/
```

### Step 4: Deploy Lambda Functions

```bash
# Package Lambda function
cd lambda_functions
pip install -r requirements.txt -t .
zip -r lambda_forecast.zip .

# Create Lambda function
aws lambda create-function \
  --function-name ai-retail-forecast \
  --runtime python3.11 \
  --role arn:aws:iam::ACCOUNT_ID:role/LambdaBedrockRole \
  --handler lambda_forecast.lambda_handler \
  --zip-file fileb://lambda_forecast.zip \
  --timeout 60 \
  --memory-size 512

# Repeat for other Lambda functions
```

### Step 5: Create API Gateway

```bash
# Create REST API
aws apigateway create-rest-api \
  --name "AI Retail Intelligence API" \
  --description "API for AI Retail Intelligence Platform"

# Create resources and methods
# (Use AWS Console or CloudFormation for easier setup)
```

### Step 6: Load Initial Data

```python
# load_data_to_dynamodb.py
import boto3
import pandas as pd
from datetime import datetime

dynamodb = boto3.resource('dynamodb')

# Load gold prices
gold_df = pd.read_csv('data/gold_prices.csv')
price_table = dynamodb.Table('PriceHistory')

for _, row in gold_df.iterrows():
    price_table.put_item(
        Item={
            'asset': 'GOLD',
            'timestamp': row['date'],
            'open': float(row['open']),
            'high': float(row['high']),
            'low': float(row['low']),
            'close': float(row['close']),
            'volume': int(row['volume'])
        }
    )

# Load competitive pricing
pricing_df = pd.read_csv('data/competitive_pricing_sample.csv')
pricing_table = dynamodb.Table('CompetitivePricing')

for _, row in pricing_df.iterrows():
    pricing_table.put_item(
        Item={
            'product_id': row['product_id'],
            'product_name': row['product_name'],
            'category': row['category'],
            'prices': {
                'Amazon': float(row['amazon_price']),
                'Flipkart': float(row['flipkart_price']),
                'JioMart': float(row['jiomart_price']),
                'Blinkit': float(row['blinkit_price']),
                'Zepto': float(row['zepto_price']),
                'DMart': float(row['dmart_price'])
            },
            'updated_at': datetime.now().isoformat()
        }
    )

print("Data loaded successfully!")
```

## Cost Estimation

### Monthly Cost Breakdown (Estimated)

**Amazon Bedrock**:
- Claude 3 Haiku: $0.25 per 1M input tokens, $1.25 per 1M output tokens
- Estimated: 10M tokens/month = ~$15/month

**AWS Lambda**:
- 1M requests/month, 512MB memory, 3s avg duration
- Estimated: $5/month (within free tier for first year)

**Amazon DynamoDB**:
- On-demand pricing: $1.25 per million write requests, $0.25 per million read requests
- Estimated: 1M reads, 100K writes = $0.38/month

**Amazon S3**:
- Standard storage: $0.023 per GB
- Estimated: 10GB = $0.23/month

**Amazon API Gateway**:
- REST API: $3.50 per million requests
- WebSocket: $1.00 per million messages
- Estimated: 1M requests = $3.50/month

**Total Estimated Cost**: ~$25-30/month for moderate usage

## Monitoring and Logging

### CloudWatch Dashboards

```python
# Create CloudWatch dashboard
import boto3

cloudwatch = boto3.client('cloudwatch')

dashboard_body = {
    "widgets": [
        {
            "type": "metric",
            "properties": {
                "metrics": [
                    ["AWS/Lambda", "Invocations", {"stat": "Sum"}],
                    [".", "Errors", {"stat": "Sum"}],
                    [".", "Duration", {"stat": "Average"}]
                ],
                "period": 300,
                "stat": "Average",
                "region": "us-east-1",
                "title": "Lambda Metrics"
            }
        },
        {
            "type": "metric",
            "properties": {
                "metrics": [
                    ["AWS/DynamoDB", "ConsumedReadCapacityUnits"],
                    [".", "ConsumedWriteCapacityUnits"]
                ],
                "period": 300,
                "stat": "Sum",
                "region": "us-east-1",
                "title": "DynamoDB Metrics"
            }
        }
    ]
}

cloudwatch.put_dashboard(
    DashboardName='AIRetailIntelligence',
    DashboardBody=json.dumps(dashboard_body)
)
```

## Security Best Practices

1. **Enable encryption at rest** for DynamoDB and S3
2. **Use VPC endpoints** for Lambda to access AWS services
3. **Implement API throttling** in API Gateway
4. **Enable CloudTrail** for audit logging
5. **Use AWS Secrets Manager** for API keys and credentials
6. **Implement CORS** properly in API Gateway
7. **Use AWS WAF** for API protection

## Next Steps

1. **Deploy infrastructure** using the steps above
2. **Test API endpoints** with Postman or curl
3. **Deploy dashboard** to S3 + CloudFront or EC2
4. **Set up monitoring** with CloudWatch
5. **Configure auto-scaling** for Lambda concurrency
6. **Implement CI/CD** with AWS CodePipeline

## Support

For issues or questions:
- AWS Support: https://console.aws.amazon.com/support
- Bedrock Documentation: https://docs.aws.amazon.com/bedrock
- Lambda Documentation: https://docs.aws.amazon.com/lambda

---

**Note**: This is a production-ready architecture. Start with the basic setup and scale as needed. All services use pay-as-you-go pricing, so costs scale with usage.
