# AI for Retail, Commerce & Market Intelligence Platform

A comprehensive AI-powered platform for market intelligence, demand forecasting, and pricing optimization, specifically designed for precious metals (gold/silver coins) and popular Indian ETFs. Built for the AI for Bharat Hackathon.

**🌐 Live Dashboard**: [http://ai-retail-dashboard-439786465522.s3-website-us-east-1.amazonaws.com](http://ai-retail-dashboard-439786465522.s3-website-us-east-1.amazonaws.com)

**🇮🇳 Current Indian Market Integration (February 2026):**
- **24K Gold**: ₹1.3-1.6 Lakh per 10 grams (₹130,000-160,000)
- **Silver**: ₹2.8-3.7 Lakh per kg (₹280,000-370,000)
- **GOLDBEES ETF**: ₹140-170 per unit
- **Market Features**: GST integration, festival effects, Indian trading patterns

## 🚀 Features

### 🌐 Live Production Dashboard
**Access the platform**: [http://ai-retail-dashboard-439786465522.s3-website-us-east-1.amazonaws.com](http://ai-retail-dashboard-439786465522.s3-website-us-east-1.amazonaws.com)

The platform is fully deployed on AWS with:
- **Real-time Price Forecasting**: 6 AI models (Nova Lite/Pro, Llama 3.3 70B, Llama 4 Scout, DeepSeek V3/R1)
- **AI Document Analysis**: 7 AI models (Nova Micro/Lite/Pro, Llama 3.2 3B, 3.1 8B, 3.3 70B, 4 Scout)
- **Market Copilot**: Conversational AI with integrated pricing intelligence
- **Current Prices**: Real-time gold, silver, and ETF price tracking
- **Platform Status**: Live system health monitoring with 9 AI models

### Core Capabilities
- **Price Trend Forecasting**: ML-based prediction for gold, silver, and ETF prices
- **Intelligent Pricing Engine**: Market analysis and pricing recommendations
- **Competitive Pricing Intelligence**: Multi-platform price comparison across Amazon, Flipkart, JioMart, Blinkit, Zepto, DMart Ready
- **Document Intelligence**: LLM-powered financial document analysis
- **Market Copilot**: AI assistant for natural language market queries with integrated pricing insights
- **Real-time API**: FastAPI-based REST endpoints for integration
- **Amazon Bedrock Framework**: Advanced forecasting using Claude 3 and Titan foundation models

### Key Components
- **Data Pipeline**: Automated CSV data loading and preprocessing
- **ML Models**: Multiple forecasting algorithms (Moving Average, Random Forest, LSTM Neural Networks)
- **Bedrock Integration**: Framework for Claude 3 Sonnet/Haiku and Amazon Titan models
- **Pricing Strategies**: Conservative, balanced, and aggressive pricing approaches
- **Competitive Analysis**: Real-time price tracking and savings recommendations
- **Document Parser**: Extract insights from financial reports and market analysis
- **Conversational AI**: Natural language interface for market intelligence

### Advanced ML Features (Phase 2)
- **LSTM Neural Networks**: Deep learning-based time series forecasting with GPU acceleration
- **Model Checkpointing**: Automatic saving of best models during training
- **Early Stopping**: Prevents overfitting with intelligent training termination
- **GPU Support**: CUDA and Apple Silicon (MPS) acceleration for faster training
- **Configurable Architecture**: Adjustable layers, hidden units, and hyperparameters
- **See [LSTM Integration Guide](docs/LSTM_INTEGRATION.md) for detailed documentation**

### New Competitive Pricing Features
- **Multi-Platform Comparison**: Compare prices across 6 major Indian e-commerce platforms
- **Savings Calculator**: Automatic calculation of potential savings and best deals
- **Price Trend Analysis**: 7-day and 30-day price movement tracking
- **Smart Recommendations**: AI-powered purchase recommendations based on price analysis
- **API Integration**: RESTful endpoints for price comparison and deal discovery

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    Client Applications                       │
├─────────────────────────────────────────────────────────────┤
│                     FastAPI Gateway                         │
│  ┌─────────────┬─────────────┬─────────────┬─────────────┐  │
│  │ Forecasting │Competitive  │  Document   │   Market    │  │
│  │ Endpoints   │Pricing APIs │ Endpoints   │  Copilot    │  │
│  └─────────────┴─────────────┴─────────────┴─────────────┘  │
├─────────────────────────────────────────────────────────────┤
│                    Service Layer                            │
│  ┌─────────────┬─────────────┬─────────────┬─────────────┐  │
│  │Forecasting  │Competitive  │  Document   │   Market    │  │
│  │   Engine    │Pricing Eng. │   Parser    │  Copilot    │  │
│  └─────────────┴─────────────┴─────────────┴─────────────┘  │
├─────────────────────────────────────────────────────────────┤
│                     AI/ML Layer                             │
│  ┌─────────────┬─────────────┬─────────────┬─────────────┐  │
│  │Traditional  │   Bedrock   │     LLM     │  Amazon Q   │  │
│  │ML Models    │Foundation   │  Service    │(Optional)   │  │
│  │             │   Models    │             │             │  │
│  └─────────────┴─────────────┴─────────────┴─────────────┘  │
├─────────────────────────────────────────────────────────────┤
│                     Data Layer                              │
│  ┌─────────────┬─────────────┬─────────────┬─────────────┐  │
│  │    Data     │Competitive  │   Model     │    Logs     │  │
│  │   Loader    │Pricing Data │  Storage    │             │  │
│  └─────────────┴─────────────┴─────────────┴─────────────┘  │
└─────────────────────────────────────────────────────────────┘

Optional AWS Integration Layer:
┌─────────────────────────────────────────────────────────────┐
│                    AWS Services (Optional)                  │
│  ┌─────────────┬─────────────┬─────────────┬─────────────┐  │
│  │   Amazon    │   Amazon    │     AWS     │   Amazon    │  │
│  │  Bedrock    │     Q       │   Lambda    │     S3      │  │
│  │(Framework)  │(Framework)  │             │             │  │
│  └─────────────┴─────────────┴─────────────┴─────────────┘  │
└─────────────────────────────────────────────────────────────┘
```

## 📁 Repository Structure

```
ai-retail-intelligence/
├── data/                          # Sample datasets
│   ├── gold_prices.csv           # Historical gold price data
│   ├── silver_prices.csv         # Historical silver price data
│   ├── etf_prices.csv            # Indian ETF price data
│   └── competitive_pricing_sample.csv # Multi-platform pricing data
├── src/                          # Source code
│   ├── __init__.py
│   ├── config.py                 # Configuration management
│   ├── exceptions.py             # Custom exceptions
│   ├── logger.py                 # Logging setup
│   ├── data_loader.py            # Data loading and preprocessing
│   ├── data_generator.py         # Sample data generation
│   ├── forecasting_model.py      # ML forecasting models
│   ├── bedrock_forecasting.py    # Amazon Bedrock integration framework
│   ├── bedrock_config.py         # Bedrock configuration and settings
│   ├── amazon_q_extension.py     # Amazon Q integration framework (OPTIONAL)
│   ├── pricing_engine.py         # Pricing intelligence
│   ├── competitive_pricing.py    # Multi-platform price comparison
│   ├── document_parser.py        # LLM-based document analysis
│   ├── market_copilot.py         # AI assistant with pricing intelligence
│   └── api.py                    # FastAPI endpoints
├── models/                       # Trained ML models
├── logs/                         # Application logs
├── tests/                        # Test files
├── main.py                       # Main application entry point
├── requirements.txt              # Python dependencies
├── price_comparison.ipynb        # Competitive pricing visualization
├── BEDROCK_INTEGRATION.md        # Amazon Bedrock integration guide
├── .env.example                  # Environment configuration template
└── README.md                     # This file
```

## 🛠️ Installation & Setup

### Prerequisites
- Python 3.8+
- pip package manager
- Git

### Quick Installation

```bash
# Clone repository
git clone https://github.com/anandr16910/ai-retail-intelligence.git
cd ai-retail-intelligence

# Install dependencies
pip install -r requirements.txt

# Generate current Indian market data
python generate_indian_prices.py

# Verify data generation
python check_indian_prices.py

# Start services (automated)
python restart_services.py
```

### Manual Installation
- Python 3.8 or higher
- pip (Python package manager)

### Step 1: Clone Repository
```bash
git clone <repository-url>
cd ai-retail-intelligence
```

### Step 2: Create Virtual Environment (Recommended)
```bash
python -m venv venv

# On Windows
venv\Scripts\activate

# On macOS/Linux
source venv/bin/activate
```

### Step 3: Install Dependencies
```bash
pip install -r requirements.txt
```

### Step 4: Environment Configuration
```bash
# Copy environment template
cp .env.example .env

# Edit .env file with your settings (optional)
# Default settings work for local development
```

### Step 5: Generate Sample Data (if needed)
```bash
python src/data_generator.py
```

## 🚀 Quick Start

### Option 1: Run Interactive Demo
```bash
python main.py --mode demo
```

### Option 2: Start API Server
```bash
python main.py --mode server
```

### Option 3: Check System Status
```bash
python main.py --mode status
```

### Option 4: Development Server (with auto-reload)
```bash
python main.py --mode server --reload
```

## 📚 API Documentation

Once the server is running, access the interactive API documentation:

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **OpenAPI Schema**: http://localhost:8000/openapi.json

### Key API Endpoints

#### Price Forecasting
```http
POST /api/v1/forecast/{asset}
Content-Type: application/json

{
  "symbol": "GOLD",
  "horizon": 30,
  "model_name": "moving_average"
}
```

#### Pricing Recommendations
```http
POST /api/v1/pricing/recommend
Content-Type: application/json

{
  "symbol": "GOLD",
  "current_price": 1850.00,
  "strategy_type": "balanced"
}
```

#### Document Analysis
```http
POST /api/v1/documents/parse
Content-Type: application/json

{
  "content": "Gold prices have risen 15% this quarter...",
  "document_id": "market_report_q4"
}
```

#### Market Copilot
```http
POST /api/v1/copilot/query
Content-Type: application/json

{
  "query": "What is the current gold price trend?",
  "context": {}
}
```

### Example API Responses

#### Forecast Response
```json
{
  "success": true,
  "message": "Forecast generated for gold",
  "data": {
    "symbol": "GOLD",
    "forecast_horizon": 7,
    "predicted_prices": [1852.30, 1855.10, 1858.75, ...],
    "confidence_intervals": {
      "lower": [1760.69, 1762.35, ...],
      "upper": [1943.91, 1947.85, ...]
    },
    "model_metrics": {
      "accuracy": 0.85
    },
    "timestamp": "2024-01-15T10:30:00"
  }
}
```

#### Pricing Recommendation Response
```json
{
  "success": true,
  "message": "Pricing recommendation generated",
  "data": {
    "symbol": "GOLD",
    "current_price": 1850.00,
    "recommended_price": 1862.50,
    "confidence_score": 0.75,
    "price_change_percentage": 0.68,
    "market_conditions": {
      "trend": "upward",
      "volatility": 0.025,
      "market_condition": "bullish"
    },
    "reasoning": "Balanced strategy: 0.7% adjustment based on upward trend",
    "timestamp": "2024-01-15T10:30:00"
  }
}
```

## 🧪 Testing

### Run Demo Mode
```bash
python main.py --mode demo
```

### Manual Testing
```bash
# Test data loading
python -c "from src.data_loader import DataLoader; dl = DataLoader(); print(dl.load_all_data().keys())"

# Test forecasting
python -c "from src.forecasting_model import PriceForecastingEngine; fe = PriceForecastingEngine(); print(fe.get_available_models())"

# Test API server
curl http://localhost:8000/health
```

## ☁️ AWS Deployment

### Option 1: AWS Lambda + API Gateway

#### Step 1: Install AWS CLI
```bash
pip install awscli
aws configure
```

#### Step 2: Create Deployment Package
```bash
# Create deployment directory
mkdir aws-deployment
cp -r src/ aws-deployment/
cp requirements.txt aws-deployment/
cp main.py aws-deployment/

# Install dependencies for Lambda
cd aws-deployment
pip install -r requirements.txt -t .
```

#### Step 3: Create Lambda Function
```bash
# Create ZIP package
zip -r ai-retail-intelligence.zip .

# Create Lambda function
aws lambda create-function \
  --function-name ai-retail-intelligence \
  --runtime python3.9 \
  --role arn:aws:iam::YOUR-ACCOUNT:role/lambda-execution-role \
  --handler main.lambda_handler \
  --zip-file fileb://ai-retail-intelligence.zip
```

#### Step 4: Configure API Gateway
```bash
# Create API Gateway (use AWS Console or CLI)
# Connect Lambda function to API Gateway
# Deploy API to stage
```

### Option 2: AWS ECS (Containerized)

#### Step 1: Create Dockerfile
```dockerfile
FROM python:3.9-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
EXPOSE 8000

CMD ["python", "main.py", "--mode", "server", "--host", "0.0.0.0"]
```

#### Step 2: Build and Push to ECR
```bash
# Build Docker image
docker build -t ai-retail-intelligence .

# Tag for ECR
docker tag ai-retail-intelligence:latest YOUR-ACCOUNT.dkr.ecr.REGION.amazonaws.com/ai-retail-intelligence:latest

# Push to ECR
docker push YOUR-ACCOUNT.dkr.ecr.REGION.amazonaws.com/ai-retail-intelligence:latest
```

#### Step 3: Create ECS Service
```bash
# Create ECS cluster, task definition, and service
# Use AWS Console or CloudFormation template
```

### Option 3: AWS EC2

#### Step 1: Launch EC2 Instance
```bash
# Launch Ubuntu 20.04 LTS instance
# Configure security groups (port 8000, 22)
```

#### Step 2: Setup Application
```bash
# SSH to instance
ssh -i your-key.pem ubuntu@your-instance-ip

# Install Python and dependencies
sudo apt update
sudo apt install python3 python3-pip git -y

# Clone and setup application
git clone <your-repo-url>
cd ai-retail-intelligence
pip3 install -r requirements.txt

# Run application
python3 main.py --mode server --host 0.0.0.0
```

#### Step 3: Setup Process Manager (Optional)
```bash
# Install PM2 for Node.js or use systemd
sudo npm install -g pm2

# Create ecosystem file
echo 'module.exports = {
  apps: [{
    name: "ai-retail-intelligence",
    script: "python3",
    args: "main.py --mode server --host 0.0.0.0",
    cwd: "/home/ubuntu/ai-retail-intelligence"
  }]
}' > ecosystem.config.js

# Start with PM2
pm2 start ecosystem.config.js
pm2 save
pm2 startup
```

### AWS Services Integration

#### Amazon Bedrock (LLM Service)
```python
# Update src/config.py
LLM_MODEL_NAME = "aws-bedrock"
AWS_REGION = "us-east-1"

# The document parser will automatically use Bedrock when configured
```

#### Amazon S3 (Data Storage)
```python
# Store CSV files in S3
# Update data loader to read from S3
import boto3

s3 = boto3.client('s3')
# Modify DataLoader to read from S3 bucket
```

#### Amazon CloudWatch (Monitoring)
```python
# Add CloudWatch logging
import boto3

cloudwatch = boto3.client('cloudwatch')
# Send custom metrics to CloudWatch
```

## 🔧 Configuration

### Environment Variables
```bash
# Application Settings
DEBUG=false
APP_NAME="AI Retail Intelligence Platform"
APP_VERSION="1.0.0"

# API Settings
API_HOST=0.0.0.0
API_PORT=8000
API_PREFIX=/api/v1

# Data Settings
DATA_DIR=data
MODEL_DIR=models

# ML Model Settings
DEFAULT_FORECAST_HORIZON=30
CONFIDENCE_LEVEL=0.95

# LLM Settings
LLM_MODEL_NAME=mock
LLM_MAX_TOKENS=1000

# AWS Settings (optional)
AWS_REGION=us-east-1
AWS_ACCESS_KEY_ID=your_access_key
AWS_SECRET_ACCESS_KEY=your_secret_key

# Rate Limiting
RATE_LIMIT_REQUESTS=100
RATE_LIMIT_WINDOW=60
```

### Model Configuration
```python
# Available forecasting models
MODELS = {
    'moving_average': 'Simple Moving Average',
    'random_forest': 'Random Forest (requires scikit-learn)'
}

# Pricing strategies
STRATEGIES = {
    'conservative': 'Low risk, minimal price changes',
    'balanced': 'Moderate risk, balanced approach',
    'aggressive': 'High risk, maximum returns'
}
```

## 📊 Sample Data

The platform includes realistic sample datasets with current Indian market pricing:

### Gold Prices (gold_prices.csv)
- **Current Market Rate**: ₹1.3-1.6 Lakh per 10 grams (24K)
- **Period**: Last 90 days with current Indian market patterns
- **Records**: 90 daily prices with realistic OHLC data
- **Features**: Date, Open, High, Low, Close, Volume with Indian market characteristics
- **Patterns**: Festival season effects, GST considerations, trading center dynamics

### Silver Prices (silver_prices.csv)
- **Current Market Rate**: ₹2.8-3.7 Lakh per kg
- **Period**: Last 90 days with current Indian market patterns  
- **Records**: 90 daily prices with realistic OHLC data
- **Features**: Date, Open, High, Low, Close, Volume with higher volatility
- **Patterns**: Industrial demand patterns, festival season impacts

### Indian ETF Prices (etf_prices.csv)
- **Current Market Levels**: GOLDBEES ₹140-170, NIFTYBEES ₹280-320
- **Period**: Last 90 days reflecting 2026 market conditions
- **ETFs**: NIFTYBEES, GOLDBEES, BANKBEES, JUNIORBEES, LIQUIDBEES, PSUBNKBEES
- **Records**: 540 total records (6 ETFs × 90 days)
- **Features**: Date, Symbol, Open, High, Low, Close, Volume

## 🤖 Machine Learning Models

### Forecasting Models

#### 1. Simple Moving Average
- **Use Case**: Baseline forecasting, trend following
- **Advantages**: Fast, interpretable, no external dependencies
- **Parameters**: Window size (default: 30 days)

#### 2. Random Forest
- **Use Case**: Advanced forecasting with feature engineering
- **Advantages**: Handles non-linear patterns, feature importance
- **Requirements**: scikit-learn
- **Features**: Price lags, technical indicators, volatility

### Model Evaluation Metrics
- **MAE**: Mean Absolute Error
- **RMSE**: Root Mean Square Error
- **R²**: Coefficient of Determination
- **MAPE**: Mean Absolute Percentage Error
- **Directional Accuracy**: Percentage of correct trend predictions

## 💡 Usage Examples

### Python SDK Usage
```python
from src.data_loader import DataLoader
from src.forecasting_model import PriceForecastingEngine
from src.pricing_engine import PricingEngine

# Load data
loader = DataLoader()
gold_data = loader.load_gold_prices()

# Train forecasting model
engine = PriceForecastingEngine()
engine.train_model(gold_data, symbol='GOLD')

# Generate forecast
forecast = engine.predict_prices('GOLD', horizon=7)
print(f"7-day forecast: {forecast.predicted_prices}")

# Get pricing recommendation
pricing = PricingEngine()
recommendation = pricing.recommend_pricing(
    current_price=1850.0,
    symbol='GOLD',
    strategy_type='balanced'
)
print(f"Recommended price: ${recommendation.recommended_price:.2f}")
```

### Market Copilot Usage
```python
from src.market_copilot import MarketCopilot

copilot = MarketCopilot()

# Update with market data
copilot.update_context({
    'price_data': {
        'GOLD': {'current_price': 1850.0, 'trend': 'upward'}
    }
})

# Ask questions
response = copilot.process_query("What is the current gold price?")
print(response)

response = copilot.process_query("How is gold trending?")
print(response)
```

### Document Analysis Usage
```python
from src.document_parser import DocumentParser

parser = DocumentParser()

# Analyze financial document
analysis = parser.parse_document(
    text_content="Gold prices rose 15% this quarter due to inflation concerns...",
    document_id="market_report_q4"
)

print(f"Document type: {analysis.document_type}")
print(f"Entities: {len(analysis.extracted_entities)}")
print(f"Market insights: {analysis.market_insights}")
```

### Competitive Pricing Usage
```python
from src.competitive_pricing import CompetitivePricingEngine

# Initialize pricing engine
pricing_engine = CompetitivePricingEngine()

# Compare prices for a product
comparison = pricing_engine.compare_prices("P007")  # Borges Olive Oil
print(f"Product: {comparison.product_name}")
print(f"Lowest price: ₹{comparison.lowest_price} ({comparison.lowest_platform})")
print(f"Highest price: ₹{comparison.highest_price} ({comparison.highest_platform})")
print(f"Savings: ₹{comparison.savings_amount} ({comparison.price_difference_percentage:.1f}%)")
print(f"Recommendation: {comparison.recommendation}")

# Get best deals
deals = pricing_engine.get_best_deals(5)
for deal in deals:
    print(f"{deal['product_name']}: Save ₹{deal['savings_amount']:.2f}")

# Get product list
products = pricing_engine.get_product_list()
print(f"Total products tracked: {len(products)}")
```

#### Available Products (16 categories):
- **P001-P006**: Groceries & Appliances (Rice, Salt, Milk, Noodles, Bread, Fridge)
- **P007-P008**: Olive Oils (Borges, Figaro) - 2-year price history showing 33% decline
- **P009-P011**: Cooking Oils & Pulses (Sunflower, Mustard, Toor Dal)
- **P012-P016**: Personal Care & Household (Shampoo, Detergent, Dishwash, Tea, Toothpaste)

#### Real Customer Scenario Example:
```
🔍 Customer wants: Godrej Single Door Fridge

Platform        Price (₹)
--------------------------------
Zepto             16,299   ← Cheapest (Save ₹1,491)
Amazon            17,299
JioMart           17,500  
Flipkart          17,790   ← Highest

Variation: 9% difference between highest and lowest
Recommendation: Buy from Zepto to save ₹1,491 (9.1%)
```

### Amazon Bedrock Integration (Framework)
```python
from src.bedrock_forecasting import BedrockForecastingEngine

# Initialize Bedrock engine (framework only)
bedrock_engine = BedrockForecastingEngine()

# Generate advanced forecast using Claude 3
forecast = bedrock_engine.forecast_with_bedrock(
    symbol='GOLD',
    historical_data=price_data,
    horizon=30,
    model_name='claude'
)

print(f"Predictions: {forecast.predictions}")
print(f"Explanation: {forecast.model_explanation}")
print(f"Risk Assessment: {forecast.risk_assessment}")
```

### Amazon Q Optional Integration (Framework)
```python
from src.amazon_q_extension import AmazonQIntegrationManager

# Initialize Amazon Q manager (placeholder only)
q_manager = AmazonQIntegrationManager()

# Check capabilities
capabilities = q_manager.get_capabilities()
print(f"Amazon Q Available: {q_manager.is_available()}")

# Business reasoning (mock response)
market_data = {'platform_prices': {'Amazon': 17999, 'Flipkart': 18490}}
strategy = q_manager.business_reasoning.analyze_market_strategy(market_data)
print(f"Strategy: {strategy['strategy_type']}")

# PDF analysis (mock response)
pdf_analysis = q_manager.pdf_analyzer.analyze_large_pdf("report.pdf")
print(f"Analysis: {pdf_analysis['executive_summary']}")
```

## 🔧 Data Generation & Management Utilities

The platform includes comprehensive utilities for managing Indian market data:

### Indian Price Data Generation (`generate_indian_prices.py`)

Generate realistic Indian precious metals price data with current market rates:

```bash
# Generate 90 days of current Indian market data
python generate_indian_prices.py

# Generate specific duration
python generate_indian_prices.py --days 180

# Generate 22K gold data
python generate_indian_prices.py --gold-type 22K
```

**Features:**
- Current Indian market rates (₹1.3-1.6L gold, ₹2.8-3.7L silver)
- Festival season effects and salary cycle impacts
- Realistic volatility patterns for Indian markets
- OHLC data with proper price relationships
- ETF data reflecting current market levels

### Price Verification (`check_indian_prices.py`)

Verify current price data and market alignment:

```bash
python check_indian_prices.py
```

**Output:**
```
🇮🇳 Current Indian Precious Metals Prices
=============================================
🥇 24K Gold (per 10 grams):
   Current Price: ₹1,60,579.29
   Date: 2026-02-03
   Change: ₹+1,884.66 (+1.19%)

🥈 Silver (per kg):
   Current Price: ₹3,28,726.43
   Date: 2026-02-03
   Change: ₹-9,932.08 (-2.93%)
```

### Service Management (`restart_services.py`)

Automated service restart and data refresh:

```bash
# Restart all services with fresh data
python restart_services.py

# Stop all services
python restart_services.py --stop
```

**Features:**
- Automatic process management
- Data validation and verification
- Service health checks
- Port conflict resolution

### Data Pipeline Testing (`test_data_loading.py`)

Validate data loading and processing:

```bash
python test_data_loading.py
```

## 🎨 Web Dashboard (Sample Implementation)

A comprehensive web dashboard has been created as a sample implementation for Phase 2 development. The dashboard provides an intuitive interface for all platform capabilities.

### Dashboard Features

#### 🏠 Dashboard Overview
- **Real-time Metrics**: Live display of tracked products, current prices, and savings
- **Interactive Charts**: Price trends and platform comparisons with Plotly
- **System Status**: Health monitoring of all platform services
- **Quick Actions**: One-click access to common operations

#### 📈 Price Forecasting Interface
- **Asset Selection**: Gold, Silver, and ETF forecasting options
- **Parameter Control**: Adjustable forecast horizon (1-90 days) and model selection
- **Visual Results**: Interactive charts with confidence intervals
- **Performance Metrics**: Model accuracy and evaluation scores

#### 💰 Competitive Pricing Dashboard
- **Product Search**: Real-time search across product catalog
- **Price Comparison**: Side-by-side platform comparison with savings calculation
- **Visual Analytics**: Color-coded charts highlighting best deals
- **Trend Analysis**: 7-day and 30-day price movement indicators

#### 🤖 Market Copilot Chat
- **Conversational Interface**: WhatsApp-style chat with AI assistant
- **Context Awareness**: Maintains conversation history and context
- **Quick Actions**: Pre-defined buttons for common queries
- **Rich Responses**: Formatted answers with tables and insights

#### 📄 Document Analysis Interface
- **File Upload**: Support for TXT, PDF, and DOCX documents
- **Real-time Analysis**: Entity extraction and insight generation
- **Visual Results**: Confidence scores and categorized insights
- **Sample Documents**: Pre-loaded examples for testing

#### ⚙️ System Monitoring
- **Service Status**: Real-time health of all platform components
- **Performance Metrics**: Response times, cache rates, and error tracking
- **Configuration**: API settings and model parameters
- **Logs Viewer**: Recent system activity and events

### Quick Start Dashboard

```bash
# Install dashboard dependencies
cd dashboard
pip install -r requirements.txt

# Start the main platform API (required)
cd ..
python main.py --mode server

# Launch dashboard (in new terminal)
cd dashboard
streamlit run app.py

# Or use the convenient launcher
python run_dashboard.py
```

### Dashboard Access
- **Dashboard URL**: http://localhost:8501
- **API Documentation**: http://localhost:8000/docs

### Sample Dashboard Screenshots

The dashboard includes:
- **Interactive Visualizations**: Plotly-powered charts with zoom, pan, and export
- **Responsive Design**: Optimized for desktop and tablet viewing
- **Real-time Updates**: Live data from the platform API
- **Professional UI**: Clean, modern interface with intuitive navigation

### Dashboard Architecture

```
Dashboard Layer (Streamlit)
├── 🏠 Overview Page (Metrics, Charts, Status)
├── 📈 Forecasting Page (Interactive ML Models)
├── 💰 Pricing Page (Competitive Analysis)
├── 🤖 Copilot Page (Chat Interface)
├── 📄 Documents Page (Analysis Tools)
├── ⚙️ Status Page (System Monitoring)
└── 🔧 Amazon Q Page (Integration Demo)
```

**Note**: This is a sample implementation demonstrating the full potential of a web interface for the AI Retail Intelligence platform. It showcases all current capabilities in an intuitive, user-friendly format.

## 🔧 Amazon Q Optional Integration
Amazon Q integration provides advanced business reasoning, seller insights, and large PDF analysis capabilities. This is an **OPTIONAL** extension that enhances the platform with enterprise-grade AI capabilities.

**⚠️ Important**: Amazon Q integration is **NOT executed in local builds** and requires AWS credentials and Amazon Q access. The current implementation provides a framework for future integration.

### Capabilities

#### 🧠 Business Reasoning
- **Market Strategy Analysis**: Advanced strategic insights based on competitive data
- **Risk Assessment**: Comprehensive risk analysis with mitigation strategies  
- **Competitive Positioning**: Market position analysis and recommendations
- **Performance Benchmarking**: Compare against industry standards

#### 📊 Seller Insights
- **Performance Analysis**: Detailed seller performance metrics and trends
- **Improvement Opportunities**: AI-powered recommendations for growth
- **Market Opportunities**: Identification of untapped market segments
- **Competitive Analysis**: Position analysis vs competitors

#### 📄 Large PDF Analysis
- **Document Processing**: Handle large financial reports and market studies
- **Financial Metrics Extraction**: Automated extraction of key financial data
- **Trend Identification**: Identify market trends from document content
- **Executive Summaries**: Generate concise summaries of complex documents

### Integration Status

```python
# Check Amazon Q availability
from src.amazon_q_extension import AmazonQIntegrationManager

manager = AmazonQIntegrationManager()
status = manager.get_capabilities()

print(f"Enabled: {status['integration_status']['enabled']}")
print(f"AWS Credentials Required: {status['integration_status']['aws_credentials_required']}")
print(f"Local Build Compatible: {status['integration_status']['local_build_compatible']}")
```

### Framework Components

#### 1. Business Reasoning Module
```python
# Market strategy analysis
strategy_analysis = manager.business_reasoning.analyze_market_strategy({
    'platform_prices': {'Amazon': 17999, 'Flipkart': 18490, 'Zepto': 16999},
    'product_category': 'electronics',
    'market_segment': 'home_appliances'
})

# Returns strategic insights and recommendations
```

#### 2. PDF Analyzer Module  
```python
# Large document analysis
pdf_analysis = manager.pdf_analyzer.analyze_large_pdf(
    pdf_path="market_report.pdf",
    analysis_type="market_intelligence"
)

# Extract financial metrics
metrics = manager.pdf_analyzer.extract_financial_metrics(pdf_content)
```

#### 3. Integration Manager
```python
# Process business queries
response = manager.process_business_query(
    "What pricing strategy should we adopt for electronics?",
    context={'market_data': competitive_data}
)
```

### Future Implementation

When AWS credentials and Amazon Q access are available, the framework will support:

1. **Real-time Business Intelligence**: Live market analysis and strategic recommendations
2. **Advanced Document Processing**: Handle multi-hundred page financial reports
3. **Predictive Analytics**: Forecast market trends and business outcomes
4. **Automated Insights**: Generate executive summaries and action items

### Configuration

```bash
# Environment variables (when enabled)
export AWS_ACCESS_KEY_ID="your_access_key"
export AWS_SECRET_ACCESS_KEY="your_secret_key"
export AMAZON_Q_APPLICATION_ID="your_q_app_id"
export AMAZON_Q_REGION="us-east-1"
```

### API Endpoints (Future)

```bash
# Business reasoning
POST /api/v1/amazon-q/business-analysis
POST /api/v1/amazon-q/market-strategy

# Seller insights  
POST /api/v1/amazon-q/seller-analysis
GET /api/v1/amazon-q/performance-insights

# PDF analysis
POST /api/v1/amazon-q/pdf-analysis
POST /api/v1/amazon-q/extract-metrics
```

**Note**: All Amazon Q functionality currently returns placeholder responses for demonstration purposes. Real integration requires AWS setup and Amazon Q access.

## 📡 API Endpoints

### Core Forecasting APIs
```bash
# Generate price forecast
POST /api/v1/forecast/gold
POST /api/v1/forecast/silver  
POST /api/v1/forecast/etf

# Get available models
GET /api/v1/forecast/models
```

### Pricing Intelligence APIs
```bash
# Get pricing recommendation
POST /api/v1/pricing/recommend

# Get pricing analysis
GET /api/v1/pricing/analysis/{symbol}

# Generate pricing report
GET /api/v1/pricing/report
```

### Competitive Pricing APIs
```bash
# Compare prices by product name
GET /api/v1/price-comparison/{product_name}

# Compare prices by product ID
GET /api/v1/price-comparison/product/{product_id}

# Get available products
GET /api/v1/price-comparison/products

# Get best deals
GET /api/v1/price-comparison/best-deals?limit=10

# Get platform summary
GET /api/v1/price-comparison/platforms/summary
```

### Market Copilot APIs
```bash
# Query the AI assistant
POST /api/v1/copilot/query

# Get detailed insights
GET /api/v1/copilot/insights?query={query}

# Get conversation history
GET /api/v1/copilot/history

# Get query suggestions
GET /api/v1/copilot/suggestions
```

### Document Processing APIs
```bash
# Parse document content
POST /api/v1/documents/parse

# Upload and parse document
POST /api/v1/documents/upload

# Get document analysis
GET /api/v1/documents/{document_id}
```

### System APIs
```bash
# Health check
GET /health

# System information
GET /api/v1/system/info

# Data status
GET /api/v1/data/status

# Reload data
POST /api/v1/data/reload
```

## 🔍 Troubleshooting

### Common Issues

#### 1. Import Errors
```bash
# Error: ModuleNotFoundError
# Solution: Install dependencies
pip install -r requirements.txt

# Error: No module named 'src'
# Solution: Run from project root directory
cd ai-retail-intelligence
python main.py
```

#### 2. Data Loading Issues
```bash
# Error: File not found
# Solution: Generate sample data
python src/data_generator.py

# Error: Empty dataset
# Solution: Check CSV file format and content
```

#### 3. Model Training Failures
```bash
# Error: Insufficient data
# Solution: Ensure minimum 50 records in dataset

# Error: scikit-learn not available
# Solution: Install optional dependencies
pip install scikit-learn
```

#### 4. API Server Issues
```bash
# Error: Port already in use
# Solution: Use different port
python main.py --mode server --port 8001

# Error: FastAPI not available
# Solution: Install web dependencies
pip install fastapi uvicorn
```

### Performance Optimization

#### 1. Data Loading
```python
# Use data caching for repeated loads
# Implement data pagination for large datasets
# Use efficient data formats (Parquet, HDF5)
```

#### 2. Model Training
```python
# Use incremental learning for large datasets
# Implement model caching and versioning
# Use GPU acceleration for deep learning models
```

#### 3. API Performance
```python
# Implement response caching
# Use async endpoints for I/O operations
# Add request rate limiting
```

## 🤝 Contributing

### Development Setup
```bash
# Clone repository
git clone <repository-url>
cd ai-retail-intelligence

# Create development environment
python -m venv dev-env
source dev-env/bin/activate  # or dev-env\Scripts\activate on Windows

# Install development dependencies
pip install -r requirements.txt
pip install pytest black flake8 mypy

# Run code formatting
black src/
flake8 src/
mypy src/
```

### Testing
```bash
# Run unit tests
pytest tests/

# Run integration tests
python main.py --mode demo

# Test API endpoints
curl -X POST http://localhost:8000/api/v1/forecast/gold \
  -H "Content-Type: application/json" \
  -d '{"symbol": "GOLD", "horizon": 7}'
```

## 📄 License

This project is developed for the AI for Bharat Hackathon. Please refer to the hackathon guidelines for usage and distribution terms.

## 🆘 Support

For issues, questions, or contributions:

1. **Check Documentation**: Review this README and API docs
2. **Run Diagnostics**: Use `python main.py --mode status`
3. **Check Logs**: Review logs in the `logs/` directory
4. **Demo Mode**: Run `python main.py --mode demo` to verify setup

## 🎯 Roadmap

### Phase 1 (Current)
- ✅ Core forecasting models
- ✅ Pricing intelligence engine
- ✅ Document analysis with LLM
- ✅ Market copilot AI assistant
- ✅ REST API endpoints
- ✅ Competitive pricing intelligence
- ✅ Amazon Bedrock integration framework
- ✅ Amazon Q optional integration

### Phase 2 (Future)
- ✅ **Web dashboard interface** (Sample implementation available)
- ✅ **Advanced ML models** (LSTM Neural Networks with GPU acceleration)
- [ ] Facebook Prophet integration
- [ ] Real-time data integration
- [ ] Advanced analytics and reporting
- [ ] Multi-language support

### Phase 3 (Extended)
- [ ] Mobile application
- [ ] Advanced AI features
- [ ] Enterprise integrations
- [ ] Scalable cloud architecture
- [ ] Advanced security features

---

**Built with ❤️ by Anand Rajgopalan in Kiro for AWS AI for Bharat Hackathon**

*Empowering retail and commerce with intelligent market insights*
