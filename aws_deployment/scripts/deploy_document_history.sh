#!/bin/bash

# Deploy Document History Lambda Function
# This script creates/updates the Lambda function for retrieving document analysis history

set -e

ACCOUNT_ID="439786465522"
REGION="us-east-1"
FUNCTION_NAME="ai-retail-document-history"
ROLE_ARN="arn:aws:iam::${ACCOUNT_ID}:role/AIRetailIntelligenceLambdaRole"

echo "=========================================="
echo "Deploying Document History Lambda Function"
echo "=========================================="

# Navigate to lambda functions directory
cd "$(dirname "$0")/../lambda_functions"

# Create deployment package
echo "Creating deployment package..."
zip -q lambda_document_history.zip lambda_document_history.py

# Check if function exists
if aws lambda get-function --function-name $FUNCTION_NAME --region $REGION 2>/dev/null; then
    echo "Updating existing Lambda function..."
    aws lambda update-function-code \
        --function-name $FUNCTION_NAME \
        --zip-file fileb://lambda_document_history.zip \
        --region $REGION
    
    echo "Waiting for function update to complete..."
    aws lambda wait function-updated --function-name $FUNCTION_NAME --region $REGION
    
    echo "Updating function configuration..."
    aws lambda update-function-configuration \
        --function-name $FUNCTION_NAME \
        --timeout 30 \
        --memory-size 256 \
        --region $REGION
else
    echo "Creating new Lambda function..."
    aws lambda create-function \
        --function-name $FUNCTION_NAME \
        --runtime python3.11 \
        --role $ROLE_ARN \
        --handler lambda_document_history.lambda_handler \
        --zip-file fileb://lambda_document_history.zip \
        --timeout 30 \
        --memory-size 256 \
        --region $REGION
fi

echo ""
echo "✅ Lambda function deployed successfully!"
echo ""
echo "Next steps:"
echo "1. Create DynamoDB table 'DocumentAnalysisHistory' if not exists"
echo "2. Add DynamoDB permissions to Lambda role"
echo "3. Create API Gateway endpoint: GET /document-history"
echo "4. Update dashboard to display history"
echo ""
