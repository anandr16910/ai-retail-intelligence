# Document Analysis History Setup Guide

This guide walks you through setting up document analysis history storage using DynamoDB.

## Overview

The document history feature stores all analyzed documents in DynamoDB, allowing users to:
- View previously analyzed documents
- Reload past analyses
- Track analysis history over time
- Automatic cleanup after 90 days (TTL)

## Architecture

```
User → Dashboard → API Gateway → Lambda (Document Analysis) → DynamoDB
                                      ↓
                                 Lambda (History Retrieval) → Dashboard
```

## Prerequisites

- AWS CLI configured with credentials
- Lambda execution role with DynamoDB permissions
- API Gateway already set up

## Step 1: Create DynamoDB Table

Run the automated script:

```bash
cd aws_deployment/scripts
./create_dynamodb_table.sh
```

Or create manually in AWS Console:
1. Go to DynamoDB → Tables → Create table
2. Table name: `DocumentAnalysisHistory`
3. Partition key: `document_id` (String)
4. Billing mode: On-demand
5. Enable TTL on attribute: `ttl`

## Step 2: Update IAM Permissions

Run the automated script:

```bash
cd aws_deployment/scripts
./update_dynamodb_permissions.sh
```

Or add manually in IAM Console:
1. Go to IAM → Roles → lambda-execution-role
2. Add inline policy with DynamoDB permissions:
   - `dynamodb:PutItem`
   - `dynamodb:GetItem`
   - `dynamodb:Scan`
   - `dynamodb:Query`

## Step 3: Deploy Updated Document Analysis Lambda

The document analysis Lambda has been updated to save history automatically.

```bash
cd aws_deployment/lambda_functions

# Create deployment package
zip lambda_document_analysis.zip lambda_document_analysis.py

# Update Lambda function
aws lambda update-function-code \
    --function-name ai-retail-document-analysis \
    --zip-file fileb://lambda_document_analysis.zip \
    --region us-east-1
```

## Step 4: Deploy Document History Lambda

Deploy the new Lambda function for retrieving history:

```bash
cd aws_deployment/scripts
./deploy_document_history.sh
```

Or deploy manually:

```bash
cd aws_deployment/lambda_functions

# Create deployment package
zip lambda_document_history.zip lambda_document_history.py

# Create Lambda function
aws lambda create-function \
    --function-name ai-retail-document-history \
    --runtime python3.11 \
    --role arn:aws:iam::439786465522:role/lambda-execution-role \
    --handler lambda_document_history.lambda_handler \
    --zip-file fileb://lambda_document_history.zip \
    --timeout 30 \
    --memory-size 256 \
    --region us-east-1
```

## Step 5: Create API Gateway Endpoint

Add a new endpoint to your API Gateway:

### Using AWS Console:

1. Go to API Gateway → Your API (foiwdbvnx6)
2. Create Resource: `/document-history`
3. Create Method: `GET`
4. Integration type: Lambda Function
5. Lambda Function: `ai-retail-document-history`
6. Enable CORS
7. Deploy to `prod` stage

### Using AWS CLI:

```bash
# Get API ID and root resource ID
API_ID="foiwdbvnx6"
ROOT_ID=$(aws apigateway get-resources --rest-api-id $API_ID --region us-east-1 --query 'items[?path==`/`].id' --output text)

# Create resource
RESOURCE_ID=$(aws apigateway create-resource \
    --rest-api-id $API_ID \
    --parent-id $ROOT_ID \
    --path-part document-history \
    --region us-east-1 \
    --query 'id' --output text)

# Create GET method
aws apigateway put-method \
    --rest-api-id $API_ID \
    --resource-id $RESOURCE_ID \
    --http-method GET \
    --authorization-type NONE \
    --region us-east-1

# Integrate with Lambda
aws apigateway put-integration \
    --rest-api-id $API_ID \
    --resource-id $RESOURCE_ID \
    --http-method GET \
    --type AWS_PROXY \
    --integration-http-method POST \
    --uri arn:aws:apigateway:us-east-1:lambda:path/2015-03-31/functions/arn:aws:lambda:us-east-1:439786465522:function:ai-retail-document-history/invocations \
    --region us-east-1

# Add Lambda permission
aws lambda add-permission \
    --function-name ai-retail-document-history \
    --statement-id apigateway-get \
    --action lambda:InvokeFunction \
    --principal apigateway.amazonaws.com \
    --source-arn "arn:aws:execute-api:us-east-1:439786465522:$API_ID/*/GET/document-history" \
    --region us-east-1

# Deploy API
aws apigateway create-deployment \
    --rest-api-id $API_ID \
    --stage-name prod \
    --region us-east-1
```

## Step 6: Deploy Updated Dashboard

The dashboard has been updated with history UI.

```bash
cd aws_deployment/scripts
./deploy_dashboard.sh
```

## Testing

### Test Document Analysis (with history save):

```bash
curl -X POST https://foiwdbvnx6.execute-api.us-east-1.amazonaws.com/prod/analyze-document \
  -H "Content-Type: application/json" \
  -d '{
    "text": "Gold prices have risen 15% this quarter due to inflation concerns.",
    "analysis_type": "market_intelligence",
    "model": "nova-lite"
  }'
```

Expected response includes `document_id`.

### Test History Retrieval:

```bash
# Get all history
curl https://foiwdbvnx6.execute-api.us-east-1.amazonaws.com/prod/document-history?limit=10

# Get specific document
curl https://foiwdbvnx6.execute-api.us-east-1.amazonaws.com/prod/document-history?document_id=<document_id>
```

## Dashboard Features

Once deployed, users can:

1. **Analyze Documents**: Documents are automatically saved to history
2. **View History**: Click "Analysis History" section to see past analyses
3. **Reload Documents**: Click any history item to reload the document and analysis
4. **Refresh**: Click refresh button to update history list

## Data Retention

- Documents are stored for 90 days (TTL enabled)
- After 90 days, DynamoDB automatically deletes old records
- No manual cleanup required

## Troubleshooting

### History not saving:
- Check Lambda logs: `aws logs tail /aws/lambda/ai-retail-document-analysis --follow`
- Verify DynamoDB permissions in IAM role
- Check DynamoDB table exists

### History not loading:
- Check API Gateway endpoint is deployed
- Verify Lambda function has DynamoDB read permissions
- Check browser console for errors

### Empty history:
- Analyze a document first to create history
- Check DynamoDB table has items
- Verify TTL hasn't expired records

## Cost Estimate

- DynamoDB: ~$0.25/month per 1GB stored (on-demand)
- Lambda: ~$0.20 per 1M requests
- Typical usage: <$1/month for moderate use

## Security

- Documents stored in DynamoDB (encrypted at rest)
- TTL ensures automatic cleanup
- IAM roles restrict access
- CORS enabled for dashboard access only

## Next Steps

- Add search/filter to history
- Export history to CSV
- Add tags/categories to documents
- Implement user-specific history (with authentication)
