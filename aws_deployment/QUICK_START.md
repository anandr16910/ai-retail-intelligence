# Quick Start Guide - AWS Deployment

## Prerequisites

1. **AWS Account** with appropriate permissions
2. **AWS CLI** installed and configured
3. **Python 3.11+** installed
4. **Access to Amazon Bedrock** (request access in AWS Console)

## Step-by-Step Deployment

### 1. Configure AWS CLI

```bash
aws configure
# Enter your AWS Access Key ID
# Enter your AWS Secret Access Key
# Enter default region: us-east-1
# Enter default output format: json
```

### 2. Enable Amazon Bedrock Models

1. Go to AWS Console → Amazon Bedrock
2. Click "Model access" in the left sidebar
3. Click "Request model access"
4. Select these models:
   - Claude 3 Sonnet
   - Claude 3 Haiku
   - Amazon Titan Text Premier
5. Click "Request model access"
6. Wait for approval (usually instant)

### 3. Deploy Infrastructure

```bash
cd aws_deployment

# Make deployment script executable
chmod +x scripts/deploy.sh

# Run deployment
./scripts/deploy.sh
```

This will:
- Create S3 buckets
- Deploy DynamoDB tables
- Package and deploy Lambda functions
- Create API Gateway
- Load initial data

### 4. Test the Deployment

```bash
# Get your API endpoint
API_ENDPOINT=$(aws cloudformation describe-stacks \
    --stack-name ai-retail-intelligence \
    --query 'Stacks[0].Outputs[?OutputKey==`ApiEndpoint`].OutputValue' \
    --output text)

echo "API Endpoint: $API_ENDPOINT"

# Test forecast endpoint
curl -X POST "${API_ENDPOINT}/forecast" \
    -H "Content-Type: application/json" \
    -d '{
        "asset": "GOLD",
        "horizon": 30,
        "model": "claude-3-haiku"
    }' | jq '.'
```

### 5. Expected Response

```json
{
  "asset": "GOLD",
  "horizon": 30,
  "forecast": {
    "predictions": [
      {
        "date": "2026-03-02",
        "price": 160500.00,
        "confidence_low": 158000.00,
        "confidence_high": 163000.00
      },
      ...
    ],
    "key_factors": [
      "Historical price trends",
      "Market volatility patterns",
      "Seasonal demand factors"
    ],
    "risk_level": "Medium",
    "trend": "Upward",
    "summary": "Based on historical data analysis..."
  },
  "timestamp": "2026-03-01T10:00:00Z",
  "model_used": "claude-3-haiku"
}
```

## API Endpoints

### 1. Price Forecasting

```bash
POST /forecast
Content-Type: application/json

{
  "asset": "GOLD|SILVER|ETF",
  "horizon": 30,
  "model": "claude-3-haiku|claude-3-sonnet"
}
```

### 2. Competitive Pricing (Coming Soon)

```bash
GET /pricing/compare/{product_id}
```

### 3. Market Copilot (Coming Soon)

```bash
POST /copilot/query
Content-Type: application/json

{
  "query": "What are the current gold price trends?",
  "session_id": "user-session-123"
}
```

## Monitoring

### View Lambda Logs

```bash
# View forecast function logs
aws logs tail /aws/lambda/ai-retail-forecast --follow
```

### View API Gateway Logs

```bash
# View API logs
aws logs tail /aws/apigateway/ai-retail-intelligence --follow
```

### CloudWatch Dashboard

1. Go to AWS Console → CloudWatch
2. Click "Dashboards"
3. Look for "AIRetailIntelligence" dashboard

## Cost Monitoring

### View Current Costs

```bash
# Get cost estimate for current month
aws ce get-cost-and-usage \
    --time-period Start=$(date -u +%Y-%m-01),End=$(date -u +%Y-%m-%d) \
    --granularity MONTHLY \
    --metrics BlendedCost \
    --group-by Type=SERVICE
```

### Expected Monthly Costs

- **Amazon Bedrock**: $10-20 (depends on usage)
- **AWS Lambda**: $2-5
- **DynamoDB**: $1-3
- **API Gateway**: $3-5
- **S3**: $0.50-1
- **Total**: ~$20-35/month for moderate usage

## Troubleshooting

### Issue: "Access Denied" for Bedrock

**Solution**: Make sure you've requested access to Bedrock models in the AWS Console.

```bash
# Check Bedrock access
aws bedrock list-foundation-models --region us-east-1
```

### Issue: Lambda timeout

**Solution**: Increase Lambda timeout in CloudFormation template:

```yaml
Timeout: 120  # Increase from 60 to 120 seconds
```

### Issue: DynamoDB throttling

**Solution**: Tables use on-demand billing, so no throttling should occur. If it does, check your request patterns.

### Issue: High costs

**Solution**: 
1. Use Claude 3 Haiku instead of Sonnet (80% cheaper)
2. Implement caching for frequent queries
3. Set up billing alerts in AWS Console

## Next Steps

1. **Add More Lambda Functions**: Deploy pricing and copilot functions
2. **Set Up Custom Domain**: Use Route 53 + API Gateway custom domain
3. **Deploy Dashboard**: Host dashboard on S3 + CloudFront
4. **Enable HTTPS**: Use AWS Certificate Manager
5. **Set Up CI/CD**: Use AWS CodePipeline for automated deployments

## Cleanup

To remove all resources:

```bash
# Delete CloudFormation stack
aws cloudformation delete-stack --stack-name ai-retail-intelligence

# Delete S3 buckets (must be empty first)
aws s3 rm s3://ai-retail-intelligence-deployment --recursive
aws s3 rb s3://ai-retail-intelligence-deployment

aws s3 rm s3://ai-retail-intelligence-data-ACCOUNT_ID --recursive
aws s3 rb s3://ai-retail-intelligence-data-ACCOUNT_ID
```

## Support

- **AWS Documentation**: https://docs.aws.amazon.com/
- **Bedrock Documentation**: https://docs.aws.amazon.com/bedrock/
- **Lambda Documentation**: https://docs.aws.amazon.com/lambda/
- **DynamoDB Documentation**: https://docs.aws.amazon.com/dynamodb/

## Security Best Practices

1. **Enable MFA** on your AWS account
2. **Use IAM roles** instead of access keys where possible
3. **Enable CloudTrail** for audit logging
4. **Set up billing alerts** to avoid unexpected costs
5. **Use AWS Secrets Manager** for sensitive data
6. **Enable encryption** at rest for DynamoDB and S3

---

**Ready to deploy?** Run `./scripts/deploy.sh` and you'll have a production-ready AI platform in minutes!
