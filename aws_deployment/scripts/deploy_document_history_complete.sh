#!/bin/bash

# Complete Document History Deployment Script
# This script deploys all components for document history feature

set -e

echo "=========================================="
echo "Document History Complete Deployment"
echo "=========================================="
echo ""

# Step 1: Create DynamoDB Table
echo "Step 1/5: Creating DynamoDB table..."
./create_dynamodb_table.sh
echo ""

# Step 2: Update IAM Permissions
echo "Step 2/5: Updating IAM permissions..."
./update_dynamodb_permissions.sh
echo ""

# Step 3: Deploy Document Analysis Lambda (updated)
echo "Step 3/5: Deploying updated Document Analysis Lambda..."
cd ../lambda_functions
zip -q lambda_document_analysis.zip lambda_document_analysis.py
aws lambda update-function-code \
    --function-name ai-retail-document-analysis \
    --zip-file fileb://lambda_document_analysis.zip \
    --region us-east-1
echo "✅ Document Analysis Lambda updated"
cd ../scripts
echo ""

# Step 4: Deploy Document History Lambda
echo "Step 4/5: Deploying Document History Lambda..."
./deploy_document_history.sh
echo ""

# Step 5: Deploy Dashboard
echo "Step 5/5: Deploying updated dashboard..."
./deploy_dashboard.sh
echo ""

echo "=========================================="
echo "✅ Deployment Complete!"
echo "=========================================="
echo ""
echo "Next steps:"
echo "1. Create API Gateway endpoint: GET /document-history"
echo "2. Test document analysis to create history"
echo "3. View history in dashboard"
echo ""
echo "API Gateway Setup:"
echo "  Resource: /document-history"
echo "  Method: GET"
echo "  Integration: Lambda (ai-retail-document-history)"
echo "  Enable CORS: Yes"
echo ""
echo "Test URLs:"
echo "  Analyze: https://foiwdbvnx6.execute-api.us-east-1.amazonaws.com/prod/analyze-document"
echo "  History: https://foiwdbvnx6.execute-api.us-east-1.amazonaws.com/prod/document-history"
echo "  Dashboard: http://ai-retail-dashboard-439786465522.s3-website-us-east-1.amazonaws.com"
echo ""
