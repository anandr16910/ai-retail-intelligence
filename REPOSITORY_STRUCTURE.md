# Repository Structure

## 📁 Directory Organization

```
ai-retail-intelligence/
├── README.md                          # Main documentation with live dashboard link
├── requirements.txt                   # Python dependencies
├── main.py                           # Main application entry point
│
├── docs/                             # 📚 All Documentation
│   ├── deployment/                   # Deployment guides
│   │   ├── AWS_DEPLOYMENT_GUIDE.md
│   │   ├── QUICK_START_AWS_CONSOLE.md
│   │   ├── AWS_CONSOLE_MANAGEMENT_GUIDE.md
│   │   ├── DOCUMENT_ANALYSIS_DEPLOYMENT.md
│   │   └── HYBRID_FORECAST_SETUP.md
│   │
│   └── reference/                    # Reference documentation
│       ├── BEDROCK_MODELS_AVAILABLE.md
│       ├── MARKET_COPILOT_FAQ.md
│       └── sample_documents_for_testing.md
│
├── scripts/                          # 🛠️ Utility Scripts
│   ├── deployment/                   # Deployment automation
│   │   ├── deploy_document_analysis.sh
│   │   ├── deploy_hybrid_forecast.sh
│   │   └── update_bedrock_permissions.sh
│   │
│   ├── data/                         # Data management
│   │   ├── generate_indian_prices.py
│   │   ├── update_current_prices.py
│   │   ├── add_products_to_dynamodb.py
│   │   ├── add_products.json
│   │   └── import_household_items.py
│   │
│   └── testing/                      # Testing utilities
│       ├── test_data_loading.py
│       ├── test_all_products.py
│       ├── check_indian_prices.py
│       └── restart_services.py
│
├── aws_deployment/                   # ☁️ AWS Lambda Functions
│   ├── lambda_functions/
│   │   ├── lambda_document_analysis.py
│   │   ├── lambda_forecast.py
│   │   ├── lambda_forecast_hybrid.py
│   │   ├── lambda_market_copilot.py
│   │   └── lambda_current_prices.py
│   │
│   ├── cloudformation/
│   │   └── infrastructure.yaml
│   │
│   └── scripts/
│       ├── deploy.sh
│       ├── deploy_dashboard.sh
│       └── load_data.py
│
├── dashboard/                        # 🌐 Web Dashboard
│   ├── app.py
│   ├── config.py
│   ├── requirements.txt
│   └── data/                         # Dashboard assets
│
├── data/                             # 📊 Sample Data
│   ├── gold_prices.csv
│   ├── silver_prices.csv
│   ├── etf_prices.csv
│   ├── household_items_2years.csv
│   └── competitive_pricing_sample.csv
│
├── src/                              # 💻 Source Code
│   ├── __init__.py
│   ├── config.py
│   ├── data_loader.py
│   ├── forecasting_model.py
│   ├── bedrock_forecasting.py
│   ├── pricing_engine.py
│   ├── competitive_pricing.py
│   ├── document_parser.py
│   ├── market_copilot.py
│   └── api.py
│
├── models/                           # 🤖 Presentation Materials
│   └── AI_MODELS_PRESENTATION.md
│
├── .kiro/                            # Kiro AI specs
│   └── specs/
│       └── ai-retail-intelligence/
│
└── web_dashboard_full.html           # 🚀 Production Dashboard

```

## 🗂️ File Categories

### Core Application Files
- `main.py` - Application entry point
- `requirements.txt` - Python dependencies
- `README.md` - Main documentation
- `.env.example` - Environment configuration template

### Documentation (`docs/`)
- **deployment/** - Step-by-step deployment guides for AWS
- **reference/** - API references, model lists, FAQs

### Scripts (`scripts/`)
- **deployment/** - Automated deployment scripts
- **data/** - Data generation and management utilities
- **testing/** - Test scripts and validation tools

### AWS Deployment (`aws_deployment/`)
- **lambda_functions/** - All Lambda function code
- **cloudformation/** - Infrastructure as Code
- **scripts/** - AWS-specific deployment automation

### Dashboard (`dashboard/`)
- Streamlit-based web dashboard (local development)
- Production dashboard: `web_dashboard_full.html`

### Data (`data/`)
- Sample CSV files for gold, silver, ETF prices
- Household items and competitive pricing data

### Source Code (`src/`)
- Core Python modules for forecasting, pricing, document analysis
- API endpoints and business logic

## 🚀 Quick Start

### View Live Dashboard
http://ai-retail-dashboard-439786465522.s3-website-us-east-1.amazonaws.com

### Deploy Features
```bash
# Document Analysis
./scripts/deployment/deploy_document_analysis.sh

# Hybrid Forecasting
./scripts/deployment/deploy_hybrid_forecast.sh

# Update Bedrock Permissions
./scripts/deployment/update_bedrock_permissions.sh
```

### Manage Data
```bash
# Update current prices
python scripts/data/update_current_prices.py

# Add products to DynamoDB
python scripts/data/add_products_to_dynamodb.py

# Generate Indian market prices
python scripts/data/generate_indian_prices.py
```

### Run Tests
```bash
# Test data loading
python scripts/testing/test_data_loading.py

# Check current prices
python scripts/testing/check_indian_prices.py

# Test all products
python scripts/testing/test_all_products.py
```

## 📚 Documentation Index

### Getting Started
- [README.md](README.md) - Overview and features
- [Quick Start Guide](docs/deployment/QUICK_START_AWS_CONSOLE.md)

### Deployment
- [AWS Deployment Guide](docs/deployment/AWS_DEPLOYMENT_GUIDE.md)
- [AWS Console Management](docs/deployment/AWS_CONSOLE_MANAGEMENT_GUIDE.md)
- [Document Analysis Setup](docs/deployment/DOCUMENT_ANALYSIS_DEPLOYMENT.md)
- [Hybrid Forecast Setup](docs/deployment/HYBRID_FORECAST_SETUP.md)

### Reference
- [Bedrock Models Available](docs/reference/BEDROCK_MODELS_AVAILABLE.md)
- [Market Copilot FAQ](docs/reference/MARKET_COPILOT_FAQ.md)
- [Sample Documents](docs/reference/sample_documents_for_testing.md)

### Presentation
- [AI Models Presentation](models/AI_MODELS_PRESENTATION.md)

## 🔧 Maintenance

### Update Dependencies
```bash
pip install -r requirements.txt
```

### Restart Services
```bash
python scripts/testing/restart_services.py
```

### Check System Status
```bash
python main.py --mode status
```

## 📝 Notes

- All deployment scripts are in `scripts/deployment/`
- Data management scripts are in `scripts/data/`
- Testing utilities are in `scripts/testing/`
- Lambda functions are in `aws_deployment/lambda_functions/`
- Documentation is organized in `docs/` by category

## 🤝 Contributing

When adding new files:
- Documentation → `docs/`
- Scripts → `scripts/` (appropriate subdirectory)
- Lambda functions → `aws_deployment/lambda_functions/`
- Source code → `src/`
- Data files → `data/`

Keep the root directory clean with only essential files!
