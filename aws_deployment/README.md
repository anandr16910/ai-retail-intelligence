# AWS Deployment - AI Retail Intelligence Platform

This directory contains everything needed to deploy the AI Retail Intelligence platform to AWS using serverless architecture.

## 🏗️ Architecture

- **Amazon Bedrock**: AI/ML for forecasting and analysis
- **AWS Lambda**: Serverless compute
- **Amazon API Gateway**: REST API management
- **Amazon DynamoDB**: NoSQL database
- **Amazon S3**: Object storage
- **Amazon CloudWatch**: Monitoring and logging

## 📁 Directory Structure

```
aws_deployment/
├── lambda_functions/          # Lambda function code
│   ├── lambda_forecast.py     # Price forecasting with Bedrock
│   ├── lambda_pricing.py      # Competitive pricing analysis
│   └── lambda_copilot.py      # Market copilot chatbot
├── cloudformation/            # Infrastructure as Code
│   └── infrastructure.yaml    # Complete stack definition
├── scripts/                   # Deployment and utility scripts
│   ├── deploy.sh             # Main deployment script
│   └── load_data.py          # Data loading script
├── QUICK_START.md            # Quick start guide
└── README.md                 # This file
```

## 🚀 Quick Start

### Prerequisites

1. AWS Account with Bedrock access
2. AWS CLI configured
3. Python 3.11+

### Deploy in 3 Steps

```bash
# 1. Navigate to deployment directory
cd aws_deployment

# 2. Make script executable
chmod +x scripts/deploy.sh

# 3. Deploy!
./scripts/deploy.sh
```

That's it! Your API will be live in ~5 minutes.

## 📖 Documentation

- **[Quick Start Guide](QUICK_START.md)** - Step-by-step deployment
- **[Full Deployment Guide](../AWS_DEPLOYMENT_GUIDE.md)** - Complete architecture details
- **[API Documentation](#api-endpoints)** - API reference

## 🔌 API Endpoints

After deployment, you'll get an API endpoint like:
```
https://abc123.execute-api.us-east-1.amazonaws.com/prod
```

### Forecast Endpoint

```bash
POST /forecast
Content-Type: application/json

{
  "asset": "GOLD",
  "horizon": 30,
  "model": "claude-3-haiku"
}
```

**Response:**
```json
{
  "asset": "GOLD",
  "forecast": {
    "predictions": [...],
    "key_factors": [...],
    "risk_level": "Medium",
    "trend": "Upward"
  }
}
```

## 💰 Cost Estimate

**Monthly costs for moderate usage:**
- Bedrock: $10-20
- Lambda: $2-5
- DynamoDB: $1-3
- API Gateway: $3-5
- S3: $0.50-1
- **Total: ~$20-35/month**

## 🔒 Security

- All data encrypted at rest
- IAM roles with least privilege
- API Gateway with throttling
- CloudWatch logging enabled
- No hardcoded credentials

## 📊 Monitoring

View logs:
```bash
# Lambda logs
aws logs tail /aws/lambda/ai-retail-forecast --follow

# API Gateway logs
aws logs tail /aws/apigateway/ai-retail-intelligence --follow
```

## 🧹 Cleanup

Remove all resources:
```bash
aws cloudformation delete-stack --stack-name ai-retail-intelligence
```

## 🆘 Troubleshooting

**Issue: Bedrock access denied**
- Solution: Request model access in AWS Console → Bedrock → Model access

**Issue: Lambda timeout**
- Solution: Increase timeout in CloudFormation template

**Issue: High costs**
- Solution: Use Claude 3 Haiku instead of Sonnet (80% cheaper)

## 📚 Additional Resources

- [AWS Bedrock Documentation](https://docs.aws.amazon.com/bedrock/)
- [Lambda Best Practices](https://docs.aws.amazon.com/lambda/latest/dg/best-practices.html)
- [DynamoDB Best Practices](https://docs.aws.amazon.com/amazondynamodb/latest/developerguide/best-practices.html)

## 🤝 Support

For issues or questions:
1. Check [QUICK_START.md](QUICK_START.md)
2. Review [AWS_DEPLOYMENT_GUIDE.md](../AWS_DEPLOYMENT_GUIDE.md)
3. Check AWS CloudWatch logs
4. Open an issue on GitHub

---

**Ready to go serverless?** Follow the [Quick Start Guide](QUICK_START.md) to deploy in minutes!
