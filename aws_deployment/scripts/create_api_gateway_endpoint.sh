#!/bin/bash

# Create API Gateway Endpoint for Document History

set -e

ACCOUNT_ID="439786465522"
REGION="us-east-1"
API_ID="foiwdbvnx6"
FUNCTION_NAME="ai-retail-document-history"

echo "=========================================="
echo "Creating API Gateway Endpoint"
echo "=========================================="

# Get root resource ID
echo "Getting root resource ID..."
ROOT_ID=$(aws apigateway get-resources --rest-api-id $API_ID --region $REGION --query 'items[?path==`/`].id' --output text)
echo "Root ID: $ROOT_ID"

# Create resource
echo "Creating /document-history resource..."
RESOURCE_ID=$(aws apigateway create-resource \
    --rest-api-id $API_ID \
    --parent-id $ROOT_ID \
    --path-part document-history \
    --region $REGION \
    --query 'id' --output text 2>/dev/null || \
    aws apigateway get-resources --rest-api-id $API_ID --region $REGION --query 'items[?path==`/document-history`].id' --output text)
echo "Resource ID: $RESOURCE_ID"

# Create GET method
echo "Creating GET method..."
aws apigateway put-method \
    --rest-api-id $API_ID \
    --resource-id $RESOURCE_ID \
    --http-method GET \
    --authorization-type NONE \
    --region $REGION 2>/dev/null || echo "Method already exists"

# Integrate with Lambda
echo "Integrating with Lambda..."
aws apigateway put-integration \
    --rest-api-id $API_ID \
    --resource-id $RESOURCE_ID \
    --http-method GET \
    --type AWS_PROXY \
    --integration-http-method POST \
    --uri arn:aws:apigateway:${REGION}:lambda:path/2015-03-31/functions/arn:aws:lambda:${REGION}:${ACCOUNT_ID}:function:${FUNCTION_NAME}/invocations \
    --region $REGION 2>/dev/null || echo "Integration already exists"

# Add Lambda permission
echo "Adding Lambda permission..."
aws lambda add-permission \
    --function-name $FUNCTION_NAME \
    --statement-id apigateway-get-${RESOURCE_ID} \
    --action lambda:InvokeFunction \
    --principal apigateway.amazonaws.com \
    --source-arn "arn:aws:execute-api:${REGION}:${ACCOUNT_ID}:${API_ID}/*/GET/document-history" \
    --region $REGION 2>/dev/null || echo "Permission already exists"

# Enable CORS - OPTIONS method
echo "Enabling CORS..."
aws apigateway put-method \
    --rest-api-id $API_ID \
    --resource-id $RESOURCE_ID \
    --http-method OPTIONS \
    --authorization-type NONE \
    --region $REGION 2>/dev/null || echo "OPTIONS method already exists"

aws apigateway put-integration \
    --rest-api-id $API_ID \
    --resource-id $RESOURCE_ID \
    --http-method OPTIONS \
    --type MOCK \
    --request-templates '{"application/json": "{\"statusCode\": 200}"}' \
    --region $REGION 2>/dev/null || echo "OPTIONS integration already exists"

aws apigateway put-method-response \
    --rest-api-id $API_ID \
    --resource-id $RESOURCE_ID \
    --http-method OPTIONS \
    --status-code 200 \
    --response-parameters '{"method.response.header.Access-Control-Allow-Headers": false, "method.response.header.Access-Control-Allow-Methods": false, "method.response.header.Access-Control-Allow-Origin": false}' \
    --region $REGION 2>/dev/null || echo "OPTIONS method response already exists"

aws apigateway put-integration-response \
    --rest-api-id $API_ID \
    --resource-id $RESOURCE_ID \
    --http-method OPTIONS \
    --status-code 200 \
    --response-parameters '{"method.response.header.Access-Control-Allow-Headers": "'"'"'Content-Type,X-Amz-Date,Authorization,X-Api-Key,X-Amz-Security-Token'"'"'", "method.response.header.Access-Control-Allow-Methods": "'"'"'GET,OPTIONS'"'"'", "method.response.header.Access-Control-Allow-Origin": "'"'"'*'"'"'"}' \
    --region $REGION 2>/dev/null || echo "OPTIONS integration response already exists"

# Deploy API
echo "Deploying API to prod stage..."
aws apigateway create-deployment \
    --rest-api-id $API_ID \
    --stage-name prod \
    --region $REGION

echo ""
echo "✅ API Gateway endpoint created successfully!"
echo ""
echo "Endpoint URL:"
echo "  https://${API_ID}.execute-api.${REGION}.amazonaws.com/prod/document-history"
echo ""
echo "Test commands:"
echo "  # List recent documents"
echo "  curl https://${API_ID}.execute-api.${REGION}.amazonaws.com/prod/document-history?limit=10"
echo ""
echo "  # Get specific document"
echo "  curl https://${API_ID}.execute-api.${REGION}.amazonaws.com/prod/document-history?document_id=<id>"
echo ""
