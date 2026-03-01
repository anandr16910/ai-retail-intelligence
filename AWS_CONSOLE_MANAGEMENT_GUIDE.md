# 🎛️ AWS Console Management Guide

Complete guide to manage your AI Retail Intelligence Dashboard directly from AWS Console (no Kiro needed!)

## 📋 Table of Contents
1. [Edit Dashboard HTML](#edit-dashboard-html)
2. [Update Prices (Gold, Silver, Products)](#update-prices)
3. [Manage Lambda Functions](#manage-lambda-functions)
4. [View Logs and Monitor](#view-logs)
5. [Add New Features](#add-new-features)

---

## 1. 📝 Edit Dashboard HTML

### Option A: Using S3 Console (Easiest)

**Step 1: Open S3 Console**
1. Go to AWS Console → S3
2. Search for bucket: `ai-retail-dashboard-439786465522`
3. Click on the bucket name

**Step 2: Edit HTML File**
1. Find file: `index.html` or `web_dashboard_full.html`
2. Click the checkbox next to the file
3. Click **"Actions"** → **"Download"**
4. Edit the file on your computer using any text editor (Notepad, VS Code, etc.)
5. Make your changes (colors, text, layout, etc.)

**Step 3: Upload Updated File**
1. Back in S3 console, click **"Upload"**
2. Drag your edited HTML file
3. Click **"Upload"**
4. Changes appear immediately on your live site!

### Option B: Using S3 Built-in Editor

1. In S3 bucket, click on the file name (not checkbox)
2. Click **"Open"** or **"Edit"** button
3. Make changes directly in browser
4. Click **"Save changes"**

### What You Can Edit:
- **Colors**: Search for `#667eea` or `#764ba2` (purple gradient)
- **Text**: Change titles, descriptions, labels
- **Metrics**: Update placeholder values
- **Layout**: Modify grid layouts, card sizes
- **Features**: Add/remove sections

---

## 2. 💰 Update Prices (Gold, Silver, Products)

### A. Update Gold & Silver Prices

**Using DynamoDB Console:**

**Step 1: Open DynamoDB**
1. AWS Console → DynamoDB
2. Click **"Tables"** → **"PriceHistory"**

**Step 2: Add New Price Record**
1. Click **"Explore table items"**
2. Click **"Create item"**
3. Fill in the form:
   ```
   asset: GOLD (or SILVER)
   timestamp: 2026-02-04 (use format: YYYY-MM-DD)
   open: 160000 (opening price)
   high: 162000 (highest price)
   low: 159000 (lowest price)
   close: 161000 (closing price)
   volume: 400000 (trading volume)
   ```
4. Click **"Create item"**

**Step 3: Verify**
- Refresh your dashboard
- New prices appear automatically!

### B. Update Product Prices (Fridge, etc.)

**Using DynamoDB Console:**

**Step 1: Open CompetitivePricing Table**
1. AWS Console → DynamoDB
2. Click **"Tables"** → **"CompetitivePricing"**

**Step 2: Add/Update Product**
1. Click **"Explore table items"**
2. Click **"Create item"**
3. Fill in the form:
   ```json
   {
     "product_id": "P001",
     "product_name": "Godrej Single Door Fridge",
     "category": "home_appliances",
     "prices": {
       "Amazon": 17999,
       "Flipkart": 18490,
       "Zepto": 16999,
       "Blinkit": 17500,
       "BigBasket": 18200,
       "Swiggy": 17800
     },
     "last_updated": "2026-02-04T10:00:00Z"
   }
   ```
4. Click **"Create item"**

**Step 3: Add More Products**
Repeat for other products:
- Samsung Washing Machine (P002)
- LG Microwave (P003)
- Whirlpool AC (P004)
- Haier Refrigerator (P005)
- Bosch Dishwasher (P006)

### C. Bulk Upload Prices

**Using DynamoDB Import:**

1. Create CSV file with your data:
   ```csv
   asset,timestamp,open,high,low,close,volume
   GOLD,2026-02-04,160000,162000,159000,161000,400000
   SILVER,2026-02-04,330000,335000,328000,332000,250000
   ```

2. Upload to S3:
   - AWS Console → S3
   - Upload your CSV file

3. Import to DynamoDB:
   - DynamoDB Console → Tables → PriceHistory
   - Click **"Actions"** → **"Import from S3"**
   - Select your CSV file
   - Click **"Import"**

---

## 3. 🔧 Manage Lambda Functions

### Edit Lambda Function Code

**Step 1: Open Lambda Console**
1. AWS Console → Lambda
2. Find your functions:
   - `ai-retail-forecast` (forecasting)
   - `ai-retail-current-prices` (current prices)

**Step 2: Edit Code**
1. Click on function name
2. Scroll to **"Code source"** section
3. Click on the file (e.g., `lambda_forecast.py`)
4. Edit directly in browser
5. Click **"Deploy"** to save changes

**Step 3: Test Changes**
1. Click **"Test"** tab
2. Create test event with sample data
3. Click **"Test"** button
4. View results

### What You Can Change:
- **AI Model**: Change from `claude-3-haiku` to `claude-3-sonnet`
- **Forecast Logic**: Modify prediction algorithms
- **Response Format**: Change JSON structure
- **Error Messages**: Customize error responses

### Example: Change AI Model

Find this line in `lambda_forecast.py`:
```python
model_id = "anthropic.claude-3-haiku-20240307-v1:0"
```

Change to:
```python
model_id = "anthropic.claude-3-sonnet-20240229-v1:0"
```

Click **"Deploy"** and your API now uses Sonnet!

---

## 4. 📊 View Logs and Monitor

### CloudWatch Logs

**Step 1: Open CloudWatch**
1. AWS Console → CloudWatch
2. Click **"Logs"** → **"Log groups"**

**Step 2: View Lambda Logs**
1. Find log group: `/aws/lambda/ai-retail-forecast`
2. Click to view logs
3. See all API calls, errors, and responses

**Step 3: View API Gateway Logs**
1. Find log group: `/aws/apigateway/ai-retail-intelligence`
2. View all HTTP requests to your API

### Monitor Usage

**CloudWatch Metrics:**
1. CloudWatch → Metrics → Lambda
2. View:
   - Invocations (how many times API called)
   - Duration (response time)
   - Errors (failed requests)
   - Throttles (rate limiting)

**Cost Monitoring:**
1. AWS Console → Billing
2. View costs by service:
   - Lambda invocations
   - Bedrock API calls
   - DynamoDB reads/writes
   - S3 storage

---

## 5. ➕ Add New Features

### Add New API Endpoint

**Step 1: Create New Lambda Function**
1. Lambda Console → **"Create function"**
2. Name: `ai-retail-product-search`
3. Runtime: Python 3.11
4. Click **"Create function"**

**Step 2: Write Code**
```python
import json
import boto3

dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table('CompetitivePricing')

def lambda_handler(event, context):
    # Get query from request
    query = event.get('queryStringParameters', {}).get('q', '')
    
    # Search products
    response = table.scan(
        FilterExpression='contains(product_name, :query)',
        ExpressionAttributeValues={':query': query}
    )
    
    return {
        'statusCode': 200,
        'headers': {
            'Access-Control-Allow-Origin': '*',
            'Content-Type': 'application/json'
        },
        'body': json.dumps(response['Items'])
    }
```

**Step 3: Add to API Gateway**
1. API Gateway Console
2. Find: `AI Retail Intelligence API`
3. Click **"Create Resource"**
4. Resource name: `search`
5. Click **"Create Method"** → GET
6. Integration type: Lambda Function
7. Select your new function
8. Click **"Deploy API"**

**Step 4: Update Dashboard**
1. Edit `index.html` in S3
2. Add search functionality
3. Call new endpoint: `/prod/search?q=fridge`

### Add New Page to Dashboard

**Step 1: Edit HTML**
1. Download `index.html` from S3
2. Add new navigation item:
```html
<div class="nav-item" onclick="showPage('analytics')">
    📊 Analytics
</div>
```

**Step 2: Add Page Content**
```html
<div id="analytics" class="page">
    <div class="header">
        <h1>📊 Analytics</h1>
        <p>Platform analytics and insights</p>
    </div>
    
    <div class="card">
        <h2>Your analytics content here</h2>
    </div>
</div>
```

**Step 3: Upload to S3**
- Upload updated HTML file
- Changes appear immediately!

---

## 🎯 Common Tasks

### Task 1: Change Dashboard Colors

**File:** `index.html` in S3

**Find and replace:**
- Purple gradient: `#667eea` → Your color
- Secondary purple: `#764ba2` → Your color
- Background: `linear-gradient(135deg, #667eea 0%, #764ba2 100%)`

### Task 2: Add Today's Gold Price

**DynamoDB Console:**
1. Open PriceHistory table
2. Create item:
   ```
   asset: GOLD
   timestamp: 2026-03-01
   close: 162000
   ```
3. Dashboard updates automatically!

### Task 3: Add New Product

**DynamoDB Console:**
1. Open CompetitivePricing table
2. Create item with product details
3. Product appears in comparisons!

### Task 4: Change Forecast Model

**Lambda Console:**
1. Open `ai-retail-forecast` function
2. Find: `claude-3-haiku`
3. Change to: `claude-3-sonnet`
4. Click **"Deploy"**
5. More detailed forecasts!

### Task 5: View API Usage

**CloudWatch Console:**
1. Metrics → Lambda → Invocations
2. See graph of API calls
3. Monitor costs and usage

---

## 🔒 Security Best Practices

### 1. Enable CloudTrail
- Track all AWS Console actions
- See who changed what and when

### 2. Set Up Billing Alerts
1. Billing Console → Budgets
2. Create budget: $50/month
3. Get email when exceeded

### 3. Backup DynamoDB
1. DynamoDB Console → Backups
2. Enable point-in-time recovery
3. Create on-demand backups

### 4. Version Control for Lambda
1. Lambda Console → Versions
2. Publish new version after changes
3. Rollback if needed

---

## 📞 Quick Reference

### AWS Services You'll Use:

| Service | Purpose | Console Link |
|---------|---------|--------------|
| **S3** | Dashboard HTML files | console.aws.amazon.com/s3 |
| **DynamoDB** | Price data storage | console.aws.amazon.com/dynamodb |
| **Lambda** | API functions | console.aws.amazon.com/lambda |
| **API Gateway** | REST API endpoints | console.aws.amazon.com/apigateway |
| **CloudWatch** | Logs and monitoring | console.aws.amazon.com/cloudwatch |
| **Bedrock** | AI models | console.aws.amazon.com/bedrock |

### Your Resources:

- **S3 Bucket:** `ai-retail-dashboard-439786465522`
- **DynamoDB Tables:** 
  - `PriceHistory` (Gold, Silver, ETF)
  - `CompetitivePricing` (Products)
  - `Forecasts` (Cached predictions)
- **Lambda Functions:**
  - `ai-retail-forecast`
  - `ai-retail-current-prices`
- **API Gateway:** `AI Retail Intelligence API`
- **API Endpoint:** `https://foiwdbvnx6.execute-api.us-east-1.amazonaws.com/prod`

---

## 💡 Pro Tips

1. **Test Before Deploy**: Use Lambda test feature before deploying changes
2. **Check Logs**: Always check CloudWatch logs if something doesn't work
3. **Backup First**: Download files from S3 before editing
4. **Use Versions**: Publish Lambda versions to enable rollback
5. **Monitor Costs**: Set up billing alerts to avoid surprises
6. **Cache Data**: Use DynamoDB TTL to auto-delete old forecasts
7. **Optimize**: Use Haiku model for cost savings (80% cheaper than Sonnet)

---

## 🆘 Troubleshooting

### Dashboard Not Updating?
1. Clear browser cache (Ctrl+Shift+R)
2. Check S3 file was uploaded successfully
3. Verify file name is correct (`index.html`)

### Prices Not Showing?
1. Check DynamoDB has data
2. View Lambda logs in CloudWatch
3. Test Lambda function directly
4. Check API Gateway logs

### API Errors?
1. CloudWatch → Lambda logs
2. Look for error messages
3. Check IAM permissions
4. Verify Bedrock model access

### High Costs?
1. Check CloudWatch metrics
2. Reduce forecast frequency
3. Use Haiku instead of Sonnet
4. Enable DynamoDB auto-scaling

---

## 📚 Additional Resources

- [AWS S3 Documentation](https://docs.aws.amazon.com/s3/)
- [DynamoDB Developer Guide](https://docs.aws.amazon.com/dynamodb/)
- [Lambda Developer Guide](https://docs.aws.amazon.com/lambda/)
- [Bedrock User Guide](https://docs.aws.amazon.com/bedrock/)

---

**Last Updated:** March 1, 2026  
**AWS Account:** 439786465522  
**Region:** us-east-1

**Need Help?** Check CloudWatch logs first, then AWS Support!
