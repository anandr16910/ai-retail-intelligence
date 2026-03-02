#!/bin/bash

# Update IAM role to allow Bedrock access in all regions including us-west-2

echo "Updating IAM policy for Bedrock access in all regions..."

# Create policy document
cat > /tmp/bedrock-policy.json << 'EOF'
{
    "Version": "2012-10-17",
    "Statement": [
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
                "dynamodb:Scan",
                "dynamodb:UpdateItem"
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

# Update the inline policy
aws iam put-role-policy \
    --role-name AIRetailIntelligenceLambdaRole \
    --policy-name BedrockAndDynamoDBAccess \
    --policy-document file:///tmp/bedrock-policy.json

if [ $? -eq 0 ]; then
    echo "✅ IAM policy updated successfully"
    echo "Policy now allows Bedrock access in all regions including us-west-2"
else
    echo "❌ Failed to update IAM policy"
    exit 1
fi

# Clean up
rm /tmp/bedrock-policy.json

echo ""
echo "Next steps:"
echo "1. Deploy the updated Lambda function: ./deploy_document_analysis.sh"
echo "2. Test with Llama models in the dashboard"
