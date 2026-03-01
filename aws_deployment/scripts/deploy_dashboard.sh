#!/bin/bash

# Deploy Web Dashboard to AWS S3 + CloudFront
# This script creates a public website accessible from anywhere

set -e

echo "🚀 Deploying AI Retail Intelligence Dashboard to AWS..."

# Configuration
BUCKET_NAME="ai-retail-dashboard-$(aws sts get-caller-identity --query Account --output text)"
REGION="us-east-1"

# Step 1: Create S3 bucket for static website hosting
echo "📦 Creating S3 bucket: $BUCKET_NAME"
aws s3 mb s3://$BUCKET_NAME --region $REGION 2>/dev/null || echo "Bucket already exists"

# Step 2: Disable block public access FIRST
echo "🔐 Configuring public access settings..."
aws s3api put-public-access-block \
    --bucket $BUCKET_NAME \
    --public-access-block-configuration \
    "BlockPublicAcls=false,IgnorePublicAcls=false,BlockPublicPolicy=false,RestrictPublicBuckets=false"

# Step 3: Configure bucket for static website hosting
echo "🌐 Configuring static website hosting..."
aws s3 website s3://$BUCKET_NAME --index-document web_dashboard_full.html --error-document web_dashboard_full.html

# Step 4: Set bucket policy for public read access
echo "🔓 Setting public read policy..."
cat > /tmp/bucket-policy.json <<EOF
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Sid": "PublicReadGetObject",
      "Effect": "Allow",
      "Principal": "*",
      "Action": "s3:GetObject",
      "Resource": "arn:aws:s3:::$BUCKET_NAME/*"
    }
  ]
}
EOF

aws s3api put-bucket-policy --bucket $BUCKET_NAME --policy file:///tmp/bucket-policy.json

# Step 5: Upload dashboard files
echo "📤 Uploading dashboard files..."
aws s3 cp web_dashboard_full.html s3://$BUCKET_NAME/web_dashboard_full.html --content-type "text/html"
aws s3 cp web_dashboard.html s3://$BUCKET_NAME/web_dashboard.html --content-type "text/html"
aws s3 cp web_dashboard_full.html s3://$BUCKET_NAME/index.html --content-type "text/html"

# Step 6: Get website URL
WEBSITE_URL="http://$BUCKET_NAME.s3-website-$REGION.amazonaws.com"

echo ""
echo "✅ Dashboard deployed successfully!"
echo ""
echo "🌐 Your live dashboard URLs:"
echo "   Full Dashboard: $WEBSITE_URL"
echo "   Simple Dashboard: $WEBSITE_URL/web_dashboard.html"
echo ""
echo "📋 S3 Bucket: $BUCKET_NAME"
echo "🌍 Region: $REGION"
echo ""
echo "💡 To update the dashboard, run this script again"
echo "🗑️  To delete: aws s3 rb s3://$BUCKET_NAME --force"
echo ""
