#!/bin/bash

# AWS Deployment Script for AI Retail Intelligence Platform
# This script deploys the entire infrastructure to AWS

set -e

echo "=========================================="
echo "AI Retail Intelligence - AWS Deployment"
echo "=========================================="
echo ""

# Configuration
AWS_REGION="us-east-1"
STACK_NAME="ai-retail-intelligence"
S3_BUCKET="ai-retail-intelligence-deployment"

# Colors for output
GREEN='\033[0.32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Check if AWS CLI is installed
if ! command -v aws &> /dev/null; then
    echo -e "${RED}Error: AWS CLI is not installed${NC}"
    echo "Please install AWS CLI: https://aws.amazon.com/cli/"
    exit 1
fi

# Check if AWS credentials are configured
if ! aws sts get-caller-identity &> /dev/null; then
    echo -e "${RED}Error: AWS credentials not configured${NC}"
    echo "Please run: aws configure"
    exit 1
fi

echo -e "${GREEN}✓ AWS CLI configured${NC}"
echo ""

# Step 1: Create S3 bucket for deployment artifacts
echo "Step 1: Creating S3 bucket for deployment..."
if aws s3 ls "s3://${S3_BUCKET}" 2>&1 | grep -q 'NoSuchBucket'; then
    aws s3 mb "s3://${S3_BUCKET}" --region ${AWS_REGION}
    echo -e "${GREEN}✓ S3 bucket created${NC}"
else
    echo -e "${YELLOW}S3 bucket already exists${NC}"
fi
echo ""

# Step 2: Package Lambda functions
echo "Step 2: Packaging Lambda functions..."
cd lambda_functions

for func in lambda_*.py; do
    func_name="${func%.py}"
    echo "  Packaging ${func_name}..."
    
    # Create temporary directory
    mkdir -p "/tmp/${func_name}"
    cp "${func}" "/tmp/${func_name}/"
    
    # Install dependencies if requirements.txt exists
    if [ -f "requirements_${func_name}.txt" ]; then
        pip install -r "requirements_${func_name}.txt" -t "/tmp/${func_name}/" --quiet
    fi
    
    # Create zip file
    cd "/tmp/${func_name}"
    zip -r "${func_name}.zip" . > /dev/null
    mv "${func_name}.zip" "${OLDPWD}/"
    cd "${OLDPWD}"
    
    # Upload to S3
    aws s3 cp "${func_name}.zip" "s3://${S3_BUCKET}/lambda/${func_name}.zip"
    
    echo -e "${GREEN}  ✓ ${func_name} packaged and uploaded${NC}"
done

cd ..
echo ""

# Step 3: Deploy CloudFormation stack
echo "Step 3: Deploying CloudFormation stack..."
aws cloudformation deploy \
    --template-file cloudformation/infrastructure.yaml \
    --stack-name ${STACK_NAME} \
    --parameter-overrides \
        DeploymentBucket=${S3_BUCKET} \
    --capabilities CAPABILITY_IAM \
    --region ${AWS_REGION}

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✓ CloudFormation stack deployed${NC}"
else
    echo -e "${RED}✗ CloudFormation deployment failed${NC}"
    exit 1
fi
echo ""

# Step 4: Get stack outputs
echo "Step 4: Retrieving API endpoints..."
API_ENDPOINT=$(aws cloudformation describe-stacks \
    --stack-name ${STACK_NAME} \
    --query 'Stacks[0].Outputs[?OutputKey==`ApiEndpoint`].OutputValue' \
    --output text \
    --region ${AWS_REGION})

WEBSOCKET_ENDPOINT=$(aws cloudformation describe-stacks \
    --stack-name ${STACK_NAME} \
    --query 'Stacks[0].Outputs[?OutputKey==`WebSocketEndpoint`].OutputValue' \
    --output text \
    --region ${AWS_REGION})

echo -e "${GREEN}✓ API Endpoint: ${API_ENDPOINT}${NC}"
echo -e "${GREEN}✓ WebSocket Endpoint: ${WEBSOCKET_ENDPOINT}${NC}"
echo ""

# Step 5: Load initial data
echo "Step 5: Loading initial data to DynamoDB..."
python3 scripts/load_data.py --region ${AWS_REGION}

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✓ Initial data loaded${NC}"
else
    echo -e "${YELLOW}⚠ Data loading had some issues (check logs)${NC}"
fi
echo ""

# Step 6: Test deployment
echo "Step 6: Testing deployment..."
echo "  Testing forecast endpoint..."
curl -X POST "${API_ENDPOINT}/forecast" \
    -H "Content-Type: application/json" \
    -d '{"asset":"GOLD","horizon":30}' \
    --silent --output /dev/null --write-out "  Status: %{http_code}\n"

echo ""

# Summary
echo "=========================================="
echo "Deployment Complete!"
echo "=========================================="
echo ""
echo "API Endpoint: ${API_ENDPOINT}"
echo "WebSocket Endpoint: ${WEBSOCKET_ENDPOINT}"
echo ""
echo "Next steps:"
echo "1. Test the API endpoints"
echo "2. Deploy the dashboard"
echo "3. Set up monitoring in CloudWatch"
echo ""
echo "Documentation: See AWS_DEPLOYMENT_GUIDE.md"
echo "=========================================="
