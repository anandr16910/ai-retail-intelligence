#!/bin/bash

# Deploy Hybrid Forecasting Feature (Amazon Forecast + Amazon Bedrock)

echo "🚀 Deploying Hybrid Forecasting Feature"
echo "========================================"
echo ""

# Configuration
FUNCTION_NAME="ai-retail-forecast-hybrid"
ROLE_ARN="arn:aws:iam::439786465522:role/AIRetailIntelligenceLambdaRole"
API_ID="foiwdbvnx6"
REGION="us-east-1"

# Step 1: Create Lambda deployment package
echo "Step 1: Creating Lambda deployment package..."
cd aws_deployment/lambda_functions
zip lambda_forecast_hybrid.zip lambda_forecast_hybrid.py
cd ../..

# Step 2: Check if Lambda function exists
echo "Step 2: Checking if Lambda function exists..."
if aws lambda get-function --function-name $FUNCTION_NAME --region $REGION 2>/dev/null; then
    echo "⚠️  Lambda function already exists, updating code..."
    aws lambda update-function-code \
        --function-name $FUNCTION_NAME \
        --zip-file fileb://aws_deployment/lambda_functions/lambda_forecast_hybrid.zip \
        --region $REGION
    echo "✅ Lambda function updated"
else
    echo "Creating new Lambda function..."
    aws lambda create-function \
        --function-name $FUNCTION_NAME \
        --runtime python3.11 \
        --role $ROLE_ARN \
        --handler lambda_forecast_hybrid.lambda_handler \
        --zip-file fileb://aws_deployment/lambda_functions/lambda_forecast_hybrid.zip \
        --timeout 60 \
        --memory-size 512 \
        --description "Hybrid forecasting with Amazon Forecast + Bedrock" \
        --region $REGION
    echo "✅ Lambda function created"
fi

# Step 3: Update IAM permissions for Amazon Forecast
echo ""
echo "Step 3: Updating IAM permissions for Amazon Forecast..."
cat > /tmp/forecast-policy.json << 'EOF'
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Action": [
                "forecast:QueryForecast",
                "forecast:DescribeForecast",
                "forecast:ListForecasts"
            ],
            "Resource": "arn:aws:forecast:*:439786465522:*"
        },
        {
            "Effect": "Allow",
            "Action": [
                "bedrock:InvokeModel",
                "bedrock:InvokeModelWithResponseStream"
            ],
            "Resource": [
                "arn:aws:bedrock:*::foundation-model/*",
                "arn:aws:bedrock:*:439786465522:inference-profile/*"
            ]
        },
        {
            "Effect": "Allow",
            "Action": [
                "dynamodb:GetItem",
                "dynamodb:PutItem",
                "dynamodb:Query",
                "dynamodb:Scan"
            ],
            "Resource": "arn:aws:dynamodb:us-east-1:439786465522:table/*"
        },
        {
            "Effect": "Allow",
            "Action": [
                "logs:CreateLogGroup",
                "logs:CreateLogStream",
                "logs:PutLogEvents"
            ],
            "Resource": "arn:aws:logs:*:*:*"
        }
    ]
}
EOF

aws iam put-role-policy \
    --role-name AIRetailIntelligenceLambdaRole \
    --policy-name ForecastBedrockDynamoDBAccess \
    --policy-document file:///tmp/forecast-policy.json

rm /tmp/forecast-policy.json
echo "✅ IAM permissions updated"

# Step 4: Create API Gateway resource
echo ""
echo "Step 4: Creating API Gateway resource..."
RESOURCE_ID=$(aws apigateway get-resources --rest-api-id $API_ID --region $REGION \
    --query "items[?path=='/forecast-hybrid'].id" --output text)

if [ -z "$RESOURCE_ID" ]; then
    ROOT_ID=$(aws apigateway get-resources --rest-api-id $API_ID --region $REGION \
        --query "items[?path=='/'].id" --output text)
    
    RESOURCE_ID=$(aws apigateway create-resource \
        --rest-api-id $API_ID \
        --parent-id $ROOT_ID \
        --path-part forecast-hybrid \
        --region $REGION \
        --query 'id' --output text)
    echo "✅ Resource created: $RESOURCE_ID"
else
    echo "⚠️  Resource already exists, getting ID..."
    echo "✅ Resource ID: $RESOURCE_ID"
fi

# Step 5: Create POST method
echo ""
echo "Step 5: Creating POST method..."
aws apigateway put-method \
    --rest-api-id $API_ID \
    --resource-id $RESOURCE_ID \
    --http-method POST \
    --authorization-type NONE \
    --region $REGION 2>/dev/null || echo "⚠️  Method already exists"
echo "✅ POST method created"

# Step 6: Integrate with Lambda
echo ""
echo "Step 6: Integrating with Lambda..."
LAMBDA_ARN="arn:aws:lambda:$REGION:439786465522:function:$FUNCTION_NAME"

aws apigateway put-integration \
    --rest-api-id $API_ID \
    --resource-id $RESOURCE_ID \
    --http-method POST \
    --type AWS_PROXY \
    --integration-http-method POST \
    --uri "arn:aws:apigateway:$REGION:lambda:path/2015-03-31/functions/$LAMBDA_ARN/invocations" \
    --region $REGION
echo "✅ Lambda integration configured"

# Step 7: Enable CORS
echo ""
echo "Step 7: Enabling CORS..."
aws apigateway put-method \
    --rest-api-id $API_ID \
    --resource-id $RESOURCE_ID \
    --http-method OPTIONS \
    --authorization-type NONE \
    --region $REGION 2>/dev/null || echo "⚠️  OPTIONS method already exists"

aws apigateway put-integration \
    --rest-api-id $API_ID \
    --resource-id $RESOURCE_ID \
    --http-method OPTIONS \
    --type MOCK \
    --request-templates '{"application/json": "{\"statusCode\": 200}"}' \
    --region $REGION 2>/dev/null

aws apigateway put-method-response \
    --rest-api-id $API_ID \
    --resource-id $RESOURCE_ID \
    --http-method OPTIONS \
    --status-code 200 \
    --response-parameters '{"method.response.header.Access-Control-Allow-Headers": true, "method.response.header.Access-Control-Allow-Methods": true, "method.response.header.Access-Control-Allow-Origin": true}' \
    --region $REGION 2>/dev/null

aws apigateway put-integration-response \
    --rest-api-id $API_ID \
    --resource-id $RESOURCE_ID \
    --http-method OPTIONS \
    --status-code 200 \
    --response-parameters '{"method.response.header.Access-Control-Allow-Headers": "'"'"'Content-Type,X-Amz-Date,Authorization,X-Api-Key,X-Amz-Security-Token'"'"'", "method.response.header.Access-Control-Allow-Methods": "'"'"'POST,OPTIONS'"'"'", "method.response.header.Access-Control-Allow-Origin": "'"'"'*'"'"'"}' \
    --region $REGION 2>/dev/null

echo "✅ CORS enabled"

# Step 8: Grant API Gateway permission
echo ""
echo "Step 8: Granting API Gateway permission..."
STATEMENT_ID="apigateway-invoke-hybrid-$(date +%s)"

aws lambda add-permission \
    --function-name $FUNCTION_NAME \
    --statement-id $STATEMENT_ID \
    --action lambda:InvokeFunction \
    --principal apigateway.amazonaws.com \
    --source-arn "arn:aws:execute-api:$REGION:439786465522:$API_ID/*/POST/forecast-hybrid" \
    --region $REGION 2>/dev/null || echo "⚠️  Permission already exists"
echo "✅ Permission granted"

# Step 9: Deploy API
echo ""
echo "Step 9: Deploying API..."
aws apigateway create-deployment \
    --rest-api-id $API_ID \
    --stage-name prod \
    --region $REGION
echo "✅ API deployed to prod stage"

echo ""
echo "=================================================="
echo "🎉 Hybrid Forecasting Deployment Complete!"
echo "=================================================="
echo ""
echo "API Endpoint:"
echo "https://$API_ID.execute-api.$REGION.amazonaws.com/prod/forecast-hybrid"
echo ""
echo "Test the feature:"
echo "curl -X POST https://$API_ID.execute-api.$REGION.amazonaws.com/prod/forecast-hybrid \\"
echo "  -H 'Content-Type: application/json' \\"
echo "  -d '{\"symbol\": \"GOLD\", \"horizon\": 7, \"model\": \"hybrid\"}'"
echo ""
echo "Model Options:"
echo "  - hybrid: Amazon Forecast + Bedrock (recommended)"
echo "  - forecast-only: Amazon Forecast ML only"
echo "  - bedrock-only: Amazon Bedrock AI only"
echo ""
echo "Note: Amazon Forecast predictors need to be trained separately."
echo "See HYBRID_FORECAST_SETUP.md for complete setup instructions."
echo ""
