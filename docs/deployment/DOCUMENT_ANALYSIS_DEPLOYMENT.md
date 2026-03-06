# 📄 AI-Powered Document Analysis - Deployment Guide

## Overview
This feature adds AI-powered document analysis to your dashboard using Amazon Bedrock. Users can paste any document (market reports, financial statements, research papers) and get intelligent insights extracted by AI.

## Features
- ✅ AI-powered entity extraction
- ✅ Sentiment analysis
- ✅ Key metrics identification
- ✅ Actionable insights and recommendations
- ✅ Risk and opportunity analysis
- ✅ Multiple AI model support (Nova Lite, Claude, Llama)

---

## Step 1: Create Lambda Function

### Option A: Using AWS Console (Recommended)

1. Go to AWS Lambda Console: https://console.aws.amazon.com/lambda
2. Click **Create function**
3. Configure:
   - **Function name:** `ai-retail-document-analysis`
   - **Runtime:** Python 3.11
   - **Architecture:** x86_64
   - **Execution role:** Use existing role `AIRetailIntelligenceLambdaRole`
4. Click **Create function**
5. In the **Code** tab, click **Upload from** → **.zip file**
6. Upload: `aws_deployment/lambda_functions/lambda_document_analysis.zip`
7. Click **Save**
8. Go to **Configuration** → **General configuration**
   - **Timeout:** 60 seconds
   - **Memory:** 512 MB
9. Click **Save**

### Option B: Using AWS CLI

```bash
# Create the Lambda function
aws lambda create-function \
  --function-name ai-retail-document-analysis \
  --runtime python3.11 \
  --role arn:aws:iam::439786465522:role/AIRetailIntelligenceLambdaRole \
  --handler lambda_document_analysis.lambda_handler \
  --zip-file fileb://aws_deployment/lambda_functions/lambda_document_analysis.zip \
  --timeout 60 \
  --memory-size 512 \
  --region us-east-1
```

---

## Step 2: Create API Gateway Endpoint

### Using AWS Console:

1. Go to API Gateway Console: https://console.aws.amazon.com/apigateway
2. Find your API: **ai-retail-intelligence-api**
3. Click **Resources**
4. Click **Actions** → **Create Resource**
   - **Resource Name:** `analyze-document`
   - **Resource Path:** `/analyze-document`
   - Enable CORS: ✅
5. Click **Create Resource**
6. Select the new `/analyze-document` resource
7. Click **Actions** → **Create Method** → **POST**
8. Configure:
   - **Integration type:** Lambda Function
   - **Lambda Function:** `ai-retail-document-analysis`
   - **Use Lambda Proxy integration:** ✅
9. Click **Save**
10. Click **Actions** → **Enable CORS**
    - Accept defaults
11. Click **Actions** → **Deploy API**
    - **Deployment stage:** prod
12. Note the **Invoke URL** (should be: `https://foiwdbvnx6.execute-api.us-east-1.amazonaws.com/prod`)

### Using AWS CLI:

```bash
# Get API ID
API_ID="foiwdbvnx6"

# Get root resource ID
ROOT_ID=$(aws apigateway get-resources --rest-api-id $API_ID --query 'items[?path==`/`].id' --output text)

# Create resource
RESOURCE_ID=$(aws apigateway create-resource \
  --rest-api-id $API_ID \
  --parent-id $ROOT_ID \
  --path-part analyze-document \
  --query 'id' --output text)

# Create POST method
aws apigateway put-method \
  --rest-api-id $API_ID \
  --resource-id $RESOURCE_ID \
  --http-method POST \
  --authorization-type NONE

# Integrate with Lambda
aws apigateway put-integration \
  --rest-api-id $API_ID \
  --resource-id $RESOURCE_ID \
  --http-method POST \
  --type AWS_PROXY \
  --integration-http-method POST \
  --uri arn:aws:apigateway:us-east-1:lambda:path/2015-03-31/functions/arn:aws:lambda:us-east-1:439786465522:function:ai-retail-document-analysis/invocations

# Enable CORS
aws apigateway put-method \
  --rest-api-id $API_ID \
  --resource-id $RESOURCE_ID \
  --http-method OPTIONS \
  --authorization-type NONE

# Deploy API
aws apigateway create-deployment \
  --rest-api-id $API_ID \
  --stage-name prod
```

---

## Step 3: Grant API Gateway Permission to Invoke Lambda

```bash
aws lambda add-permission \
  --function-name ai-retail-document-analysis \
  --statement-id apigateway-invoke \
  --action lambda:InvokeFunction \
  --principal apigateway.amazonaws.com \
  --source-arn "arn:aws:execute-api:us-east-1:439786465522:foiwdbvnx6/*/POST/analyze-document" \
  --region us-east-1
```

---

## Step 4: Deploy Updated Dashboard

```bash
aws s3 cp web_dashboard_full.html \
  s3://ai-retail-dashboard-439786465522/web_dashboard_full.html \
  --content-type "text/html" \
  --cache-control "no-cache, no-store, must-revalidate" \
  --metadata-directive REPLACE
```

---

## Step 5: Test the Feature

1. Open dashboard: http://ai-retail-dashboard-439786465522.s3-website-us-east-1.amazonaws.com
2. Go to **Document Analysis** tab
3. Try a sample document:
   - Click "Market Report" button
   - Select AI model (Nova Lite recommended)
   - Click "🔍 Analyze Document"
4. View AI-generated insights!

---

## API Endpoint

**URL:** `https://foiwdbvnx6.execute-api.us-east-1.amazonaws.com/prod/analyze-document`

**Method:** POST

**Request Body:**
```json
{
  "text": "Your document content here...",
  "analysis_type": "market_intelligence",
  "model": "nova-lite"
}
```

**Response:**
```json
{
  "analysis": {
    "summary": "Brief summary...",
    "key_entities": ["Entity1", "Entity2"],
    "key_metrics": [
      {"metric": "Revenue", "value": "₹125 Cr", "context": "Q4 2025"}
    ],
    "insights": ["Insight 1", "Insight 2"],
    "sentiment": "positive",
    "confidence_score": 0.87,
    "recommendations": ["Recommendation 1"],
    "risk_factors": ["Risk 1"],
    "opportunities": ["Opportunity 1"]
  },
  "model_used": "nova-lite",
  "timestamp": "2026-03-01T17:30:00Z"
}
```

---

## Supported Models

- **Amazon Nova Lite** (Fast, cost-effective) - $0.06/1M tokens
- **Claude 3 Haiku** (Balanced quality) - $0.25/1M tokens
- **Meta Llama 3.3 70B** (Detailed analysis) - Free (open source)

---

## Cost Estimate

- **Per analysis:** ~$0.001 - $0.005 (depending on document length and model)
- **100 analyses/day:** ~$0.10 - $0.50/day
- **Monthly (3000 analyses):** ~$3 - $15/month

Very affordable! 💰

---

## Troubleshooting

### Error: "Analysis failed"
- Check Lambda function logs in CloudWatch
- Verify IAM role has Bedrock permissions
- Ensure document text is between 50-50,000 characters

### Error: "403 Forbidden"
- Check API Gateway CORS settings
- Verify Lambda permission for API Gateway

### Slow response
- Try Nova Lite model (fastest)
- Reduce document length
- Check Lambda timeout (should be 60s)

---

## What's Next?

You can enhance this feature by:
- Adding file upload support (PDF, DOCX)
- Saving analysis history to DynamoDB
- Adding comparison between multiple documents
- Exporting analysis as PDF reports

Enjoy your AI-powered document analysis! 🎉
