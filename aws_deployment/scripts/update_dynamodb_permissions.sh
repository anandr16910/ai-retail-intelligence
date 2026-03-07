#!/bin/bash

# Update Lambda IAM Role with DynamoDB Permissions

set -e

ACCOUNT_ID="439786465522"
REGION="us-east-1"
ROLE_NAME="AIRetailIntelligenceLambdaRole"
TABLE_NAME="DocumentAnalysisHistory"

echo "=========================================="
echo "Updating IAM Permissions for DynamoDB"
echo "=========================================="

# Create policy document
POLICY_DOC=$(cat <<EOF
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Action": [
                "dynamodb:PutItem",
                "dynamodb:GetItem",
                "dynamodb:Scan",
                "dynamodb:Query",
                "dynamodb:UpdateItem",
                "dynamodb:DeleteItem"
            ],
            "Resource": [
                "arn:aws:dynamodb:${REGION}:${ACCOUNT_ID}:table/${TABLE_NAME}",
                "arn:aws:dynamodb:${REGION}:${ACCOUNT_ID}:table/${TABLE_NAME}/index/*"
            ]
        }
    ]
}
EOF
)

# Create or update inline policy
echo "Adding DynamoDB permissions to Lambda role..."
aws iam put-role-policy \
    --role-name $ROLE_NAME \
    --policy-name DynamoDBDocumentHistoryAccess \
    --policy-document "$POLICY_DOC"

echo ""
echo "✅ IAM permissions updated successfully!"
echo ""
echo "Permissions added:"
echo "  - dynamodb:PutItem (save documents)"
echo "  - dynamodb:GetItem (retrieve specific document)"
echo "  - dynamodb:Scan (list all documents)"
echo "  - dynamodb:Query (query by timestamp)"
echo ""
