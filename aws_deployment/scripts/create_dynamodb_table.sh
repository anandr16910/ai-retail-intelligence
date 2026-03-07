#!/bin/bash

# Create DynamoDB Table for Document Analysis History

set -e

REGION="us-east-1"
TABLE_NAME="DocumentAnalysisHistory"

echo "=========================================="
echo "Creating DynamoDB Table: $TABLE_NAME"
echo "=========================================="

# Check if table exists
if aws dynamodb describe-table --table-name $TABLE_NAME --region $REGION 2>/dev/null; then
    echo "✅ Table already exists!"
    exit 0
fi

# Create table
echo "Creating table..."
aws dynamodb create-table \
    --table-name $TABLE_NAME \
    --attribute-definitions \
        AttributeName=document_id,AttributeType=S \
    --key-schema \
        AttributeName=document_id,KeyType=HASH \
    --billing-mode PAY_PER_REQUEST \
    --region $REGION \
    --tags Key=Project,Value=AIRetailIntelligence Key=Feature,Value=DocumentHistory

echo "Waiting for table to be active..."
aws dynamodb wait table-exists --table-name $TABLE_NAME --region $REGION

# Enable TTL for automatic cleanup
echo "Enabling TTL (90 days)..."
aws dynamodb update-time-to-live \
    --table-name $TABLE_NAME \
    --time-to-live-specification "Enabled=true, AttributeName=ttl" \
    --region $REGION

echo ""
echo "✅ DynamoDB table created successfully!"
echo ""
echo "Table details:"
echo "  Name: $TABLE_NAME"
echo "  Region: $REGION"
echo "  Billing: Pay-per-request"
echo "  TTL: 90 days (automatic cleanup)"
echo ""
