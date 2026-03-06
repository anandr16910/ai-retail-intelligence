# AWS AI Services Used in AI Retail Intelligence Platform

## ✅ AWS AI Services Currently Deployed

### 1. **Amazon Bedrock** (Primary AI Service)
**Status**: ✅ ACTIVELY USED

**What it is**: AWS's fully managed generative AI service providing access to foundation models from leading AI companies.

**How we use it**:
- **9 AI Models deployed** across 3 features
- **Document Analysis**: 7 models (Nova Micro/Lite/Pro, Llama 3.2/3.1/3.3/4)
- **Price Forecasting**: 6 models (Nova Lite/Pro, Llama 3.3/4, DeepSeek V3/R1)
- **Market Copilot**: 1 model (Nova Lite for conversational AI)

**API Calls**:
```python
bedrock = boto3.client('bedrock-runtime', region_name='us-east-1')
response = bedrock.invoke_model(
    modelId='amazon.nova-lite-v1:0',
    body=json.dumps({...})
)
```

**Regions Used**:
- `us-east-1`: Amazon Nova models, DeepSeek models
- `us-west-2`: Meta Llama inference profiles

**Cost**: Pay-per-use based on tokens processed

---

### 2. **AWS Lambda** (Compute Layer)
**Status**: ✅ ACTIVELY USED

**What it is**: Serverless compute service that runs code in response to events.

**How we use it**:
- **4 Lambda Functions** deployed:
  1. `ai-retail-document-analysis` - Invokes Bedrock for document analysis
  2. `ai-retail-forecast` - Invokes Bedrock for price predictions
  3. `ai-retail-market-copilot` - Invokes Bedrock for conversational AI
  4. `ai-retail-current-prices` - Fetches real-time price data

**Integration with AI**:
- Lambda functions act as the bridge between API Gateway and Bedrock
- Handle authentication, input validation, and response formatting
- Manage multi-region Bedrock client selection

---

### 3. **Amazon API Gateway** (API Layer)
**Status**: ✅ ACTIVELY USED

**What it is**: Fully managed service for creating, publishing, and managing APIs.

**How we use it**:
- **REST API**: `foiwdbvnx6.execute-api.us-east-1.amazonaws.com`
- **Endpoints**:
  - `/analyze-document` - Document analysis with AI
  - `/forecast` - Price forecasting with AI
  - `/copilot` - Conversational AI queries
  - `/current-prices` - Real-time price data

**AI Integration**: Routes user requests to Lambda functions that invoke Bedrock models

---

### 4. **Amazon DynamoDB** (Data Storage)
**Status**: ✅ ACTIVELY USED

**What it is**: Fully managed NoSQL database service.

**How we use it**:
- Store historical price data (gold, silver, ETF)
- Store product catalog and competitive pricing data
- Cache AI model responses for faster retrieval
- Store user query history for Market Copilot

**AI Enhancement**: Provides context data for AI models to make better predictions

---

### 5. **Amazon S3** (Static Hosting & Storage)
**Status**: ✅ ACTIVELY USED

**What it is**: Object storage service for storing and retrieving data.

**How we use it**:
- **Dashboard Hosting**: `ai-retail-dashboard-439786465522.s3-website-us-east-1.amazonaws.com`
- Store Lambda deployment packages
- Store model training data and historical datasets

---

### 6. **AWS IAM** (Security & Permissions)
**Status**: ✅ ACTIVELY USED

**What it is**: Identity and Access Management for AWS resources.

**How we use it**:
- **Role**: `AIRetailIntelligenceLambdaRole`
- **Permissions**: 
  - Bedrock model invocation (all regions)
  - DynamoDB read/write access
  - CloudWatch logging
  - Cross-region Bedrock access

---

## 🔄 Amazon Forecast - Recommended Addition

### **Amazon Forecast** (Time Series Forecasting Service)
**Status**: ⚠️ NOT CURRENTLY USED (Recommended for enhancement)

**What it is**: AWS's specialized time series forecasting service using machine learning.

**Why add it**:
1. **Purpose-built for forecasting**: Designed specifically for time series predictions
2. **AutoML capabilities**: Automatically selects best algorithms
3. **Handles seasonality**: Built-in support for Indian market patterns (festivals, holidays)
4. **Scalability**: Can handle millions of time series
5. **Accuracy**: Often outperforms generic ML models for time series data

**How to integrate**:
```python
import boto3

forecast = boto3.client('forecast', region_name='us-east-1')

# Create dataset
forecast.create_dataset(
    DatasetName='gold-prices',
    Domain='RETAIL',
    DatasetType='TARGET_TIME_SERIES',
    DataFrequency='D'
)

# Train predictor
forecast.create_predictor(
    PredictorName='gold-price-predictor',
    ForecastHorizon=30,
    PerformAutoML=True
)

# Generate forecast
forecast.create_forecast(
    ForecastName='gold-30day-forecast',
    PredictorArn='arn:aws:forecast:...'
)
```

**Benefits over current Bedrock approach**:
- **Specialized**: Built for time series, not general-purpose LLMs
- **Cost-effective**: Cheaper for pure forecasting tasks
- **Quantile forecasts**: Provides P10, P50, P90 predictions
- **What-if analysis**: Test different scenarios
- **Explainability**: Shows which factors drive predictions

**Hybrid Approach (Recommended)**:
- Use **Amazon Forecast** for numerical price predictions
- Use **Amazon Bedrock** for:
  - Explaining forecast results in natural language
  - Analyzing market sentiment from documents
  - Conversational interface (Market Copilot)
  - Generating insights and recommendations

---

## Complete AWS AI Stack Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    User Dashboard (S3)                  │
└─────────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────┐
│              API Gateway (REST Endpoints)               │
└─────────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────┐
│                  AWS Lambda Functions                   │
│  • Document Analysis  • Forecasting  • Copilot         │
└─────────────────────────────────────────────────────────┘
                          ↓
        ┌─────────────────┴─────────────────┐
        ↓                                   ↓
┌──────────────────┐              ┌──────────────────┐
│ Amazon Bedrock   │              │ Amazon Forecast  │
│ (Generative AI)  │              │ (Time Series ML) │
│                  │              │                  │
│ • 9 AI Models    │              │ • AutoML         │
│ • Multi-region   │              │ • Quantile       │
│ • Real-time      │              │ • What-if        │
└──────────────────┘              └──────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────┐
│              Amazon DynamoDB (Data Storage)             │
│  • Price History  • Products  • User Queries           │
└─────────────────────────────────────────────────────────┘
```

---

## AWS AI Services Comparison

| Service | Current Use | Purpose | Cost Model |
|---------|-------------|---------|------------|
| **Amazon Bedrock** | ✅ Active | Generative AI, NLP, Document Analysis | Pay per token |
| **AWS Lambda** | ✅ Active | Serverless compute for AI invocation | Pay per request |
| **API Gateway** | ✅ Active | API management and routing | Pay per request |
| **DynamoDB** | ✅ Active | Data storage for AI context | Pay per read/write |
| **S3** | ✅ Active | Dashboard hosting, data storage | Pay per GB |
| **IAM** | ✅ Active | Security and permissions | Free |
| **Amazon Forecast** | ⚠️ Recommended | Specialized time series forecasting | Pay per forecast |
| **CloudWatch** | ✅ Active | Logging and monitoring | Pay per log |

---

## Recommendation: Add Amazon Forecast

### Implementation Plan

#### Phase 1: Setup (Week 1)
1. Create Forecast dataset groups for gold, silver, ETF
2. Import historical price data from DynamoDB
3. Train initial predictors with AutoML

#### Phase 2: Integration (Week 2)
1. Create new Lambda function: `ai-retail-forecast-ml`
2. Integrate Forecast API calls
3. Add API Gateway endpoint: `/forecast-ml`

#### Phase 3: Hybrid Approach (Week 3)
1. Use Forecast for numerical predictions
2. Use Bedrock to explain Forecast results
3. Combine both in dashboard with model comparison

#### Phase 4: Enhancement (Week 4)
1. Add what-if analysis features
2. Implement quantile forecasts (P10, P50, P90)
3. Create forecast accuracy tracking

### Expected Benefits
- **Accuracy**: 5-10% improvement in forecast accuracy
- **Cost**: 30-40% reduction in forecasting costs
- **Features**: Quantile forecasts, what-if scenarios, explainability
- **Specialization**: Purpose-built for time series vs. general LLMs

---

## Summary

### ✅ Currently Using (6 AWS AI/ML Services)
1. Amazon Bedrock (9 AI models)
2. AWS Lambda (4 functions)
3. API Gateway (REST API)
4. DynamoDB (data storage)
5. S3 (hosting & storage)
6. IAM (security)

### ⚠️ Recommended Addition
7. Amazon Forecast (specialized time series ML)

### 🎯 Result
**Hybrid AI Architecture**: Bedrock for generative AI + Forecast for time series = Best of both worlds
