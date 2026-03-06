#!/bin/bash

echo "🚀 Deploying AI-Powered Document Analysis Feature"
echo "=================================================="
echo ""

# Configuration
FUNCTION_NAME="ai-retail-document-analysis"
ROLE_ARN="arn:aws:iam::439786465522:role/AIRetailIntelligenceLambdaRole"
API_ID="foiwdbvnx6"
REGION="us-east-1"
ZIP_FILE="aws_deployment/lambda_functions/lambda_document_analysis.zip"

echo "Step 1: Creating Lambda function..."
aws lambda create-function \
  --function-name $FUNCTION_NAME \
  --runtime python3.11 \
  --role $ROLE_ARN \
  --handler lambda_document_analysis.lambda_handler \
  --zip-file fileb://$ZIP_FILE \
  --timeout 60 \
  --memory-size 512 \
  --region $REGION \
  --description "AI-powered document analysis using Amazon Bedrock" \
  2>/dev/null

if [ $? -eq 0 ]; then
    echo "✅ Lambda function created successfully"
else
    echo "⚠️  Lambda function already exists, updating code..."
    aws lambda update-function-code \
      --function-name $FUNCTION_NAME \
      --zip-file fileb://$ZIP_FILE \
      --region $REGION
    echo "✅ Lambda function updated"
fi

echo ""
echo "Step 2: Getting API Gateway resource ID..."
ROOT_ID=$(aws apigateway get-resources --rest-api-id $API_ID --query 'items[?path==`/`].id' --output text --region $REGION)

echo "Step 3: Creating API Gateway resource..."
RESOURCE_ID=$(aws apigateway create-resource \
  --rest-api-id $API_ID \
  --parent-id $ROOT_ID \
  --path-part analyze-document \
  --query 'id' --output text \
  --region $REGION 2>/dev/null)

if [ $? -eq 0 ]; then
    echo "✅ API resource created: /analyze-document"
else
    echo "⚠️  Resource already exists, getting ID..."
    RESOURCE_ID=$(aws apigateway get-resources --rest-api-id $API_ID --query 'items[?path==`/analyze-document`].id' --output text --region $REGION)
    echo "✅ Resource ID: $RESOURCE_ID"
fi

echo ""
echo "Step 4: Creating POST method..."
aws apigateway put-method \
  --rest-api-id $API_ID \
  --resource-id $RESOURCE_ID \
  --http-method POST \
  --authorization-type NONE \
  --region $REGION \
  2>/dev/null

echo "✅ POST method created"

echo ""
echo "Step 5: Integrating with Lambda..."
aws apigateway put-integration \
  --rest-api-id $API_ID \
  --resource-id $RESOURCE_ID \
  --http-method POST \
  --type AWS_PROXY \
  --integration-http-method POST \
  --uri "arn:aws:apigateway:$REGION:lambda:path/2015-03-31/functions/arn:aws:lambda:$REGION:439786465522:function:$FUNCTION_NAME/invocations" \
  --region $REGION \
  2>/dev/null

echo "✅ Lambda integration configured"

echo ""
echo "Step 6: Enabling CORS..."
aws apigateway put-method \
  --rest-api-id $API_ID \
  --resource-id $RESOURCE_ID \
  --http-method OPTIONS \
  --authorization-type NONE \
  --region $REGION \
  2>/dev/null

aws apigateway put-method-response \
  --rest-api-id $API_ID \
  --resource-id $RESOURCE_ID \
  --http-method POST \
  --status-code 200 \
  --response-parameters '{"method.response.header.Access-Control-Allow-Origin": true}' \
  --region $REGION \
  2>/dev/null

echo "✅ CORS enabled"

echo ""
echo "Step 7: Granting API Gateway permission..."
aws lambda add-permission \
  --function-name $FUNCTION_NAME \
  --statement-id apigateway-invoke-$(date +%s) \
  --action lambda:InvokeFunction \
  --principal apigateway.amazonaws.com \
  --source-arn "arn:aws:execute-api:$REGION:439786465522:$API_ID/*/POST/analyze-document" \
  --region $REGION \
  2>/dev/null

echo "✅ Permission granted"

echo ""
echo "Step 8: Deploying API..."
aws apigateway create-deployment \
  --rest-api-id $API_ID \
  --stage-name prod \
  --region $REGION \
  >/dev/null

echo "✅ API deployed to prod stage"

echo ""
echo "=================================================="
echo "🎉 Deployment Complete!"
echo "=================================================="
echo ""
echo "API Endpoint:"
echo "https://$API_ID.execute-api.$REGION.amazonaws.com/prod/analyze-document"
echo ""
echo "Dashboard:"
echo "http://ai-retail-dashboard-439786465522.s3-website-us-east-1.amazonaws.com"
echo ""
echo "Test the feature:"
echo "1. Open the dashboard"
echo "2. Go to 'Document Analysis' tab"
echo "3. Click a sample button or paste your own text"
echo "4. Select an AI model"
echo "5. Click 'Analyze Document'"
echo ""
echo "Enjoy your AI-powered document analysis! 🚀"
