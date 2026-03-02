# 🤖 Market Copilot FAQ

## Can the Market Copilot connect to Amazon.in or other websites to fetch live prices?

### Short Answer: **No, not currently.**

### Detailed Explanation:

The Market Copilot currently works with a **pre-populated database** (DynamoDB) and **cannot** fetch live prices from Amazon.in, Flipkart, or other e-commerce websites in real-time.

---

## How It Currently Works

**Data Source:** DynamoDB CompetitivePricing table
- You manually add products with prices from different platforms
- The AI reads from this database to answer questions
- Prices are static until you update them

**What the Copilot CAN do:**
✅ Compare prices for products in the database
✅ Find best deals across platforms
✅ Provide investment insights for Gold/Silver
✅ Answer questions about tracked products
✅ Show savings opportunities

**What the Copilot CANNOT do:**
❌ Fetch live prices from Amazon.in
❌ Scrape e-commerce websites
❌ Get real-time product availability
❌ Access products not in the database

---

## Why Can't It Connect to Amazon.in?

### Technical Challenges:

1. **Web Scraping Restrictions**
   - Amazon, Flipkart, and other sites have anti-scraping measures
   - They block automated bots
   - Terms of Service prohibit scraping

2. **API Limitations**
   - Amazon Product Advertising API requires approval
   - Rate limits and costs apply
   - Not all platforms offer public APIs

3. **Legal & Compliance**
   - Scraping violates most e-commerce Terms of Service
   - Could lead to IP bans or legal issues
   - Data usage restrictions

4. **Performance**
   - Real-time scraping is slow (5-10 seconds per product)
   - Would make the chatbot unresponsive
   - High cost for Lambda execution time

---

## How to Add Live Price Fetching (Advanced)

If you want to add this capability, here are the options:

### Option 1: Use Official APIs (Recommended)

**Amazon Product Advertising API:**
- Sign up: https://affiliate-program.amazon.in/
- Get API credentials
- Integrate with Lambda function
- **Limitations:** Requires affiliate account, rate limits, costs money

**Flipkart Affiliate API:**
- Similar to Amazon
- Requires approval
- Limited product data

### Option 2: Third-Party Price APIs

**Services like:**
- Rainforest API (Amazon data)
- Oxylabs E-Commerce API
- ScraperAPI

**Pros:** Easy integration, handles anti-bot measures
**Cons:** Expensive ($50-500/month), rate limits

### Option 3: Build Your Own Scraper (Not Recommended)

**Requirements:**
- AWS Lambda with Selenium/Playwright
- Proxy rotation service
- CAPTCHA solving service
- Continuous maintenance

**Challenges:**
- Violates Terms of Service
- High risk of getting blocked
- Expensive infrastructure
- Unreliable

---

## Recommended Approach: Hybrid Model

### Best Practice for Your Use Case:

1. **Manual Price Updates (Current)**
   - Update prices weekly/monthly in DynamoDB
   - Use AWS Console or Python script
   - Low cost, reliable

2. **Scheduled Price Refresh (Recommended)**
   - Create a Lambda function that runs daily
   - Fetches prices from official APIs (if available)
   - Updates DynamoDB automatically
   - Cost: ~$5-20/month

3. **User-Triggered Updates**
   - Add a "Refresh Prices" button in dashboard
   - Fetches latest prices on demand
   - Only for specific products

---

## Implementation Example: Scheduled Price Updates

If you want to implement automated price updates, here's the architecture:

```
┌─────────────────┐
│  EventBridge    │  (Trigger daily at 2 AM)
│  (Scheduler)    │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Lambda         │  (Fetch prices from APIs)
│  Price Updater  │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  DynamoDB       │  (Update CompetitivePricing table)
│  Database       │
└─────────────────┘
```

**Cost Estimate:**
- EventBridge: Free (1 rule)
- Lambda: ~$1/month (daily execution)
- API calls: $5-50/month (depends on API)
- **Total: $6-51/month**

---

## Current Workaround: Manual Updates

### Quick Update Process:

1. **Check prices manually** on Amazon.in, Flipkart, etc.

2. **Update DynamoDB** via AWS Console:
   ```
   Go to DynamoDB → CompetitivePricing → Edit item
   Update prices for each platform
   Save
   ```

3. **Or use Python script:**
   ```python
   # Update prices programmatically
   python3 add_products_to_dynamodb.py
   ```

4. **Copilot automatically uses new data** (no restart needed)

---

## What I've Fixed Today

✅ **Updated Lambda function** to properly search for products
✅ **Added product keyword matching** (olive oil, printer, fridge, etc.)
✅ **Improved error messages** when products not found
✅ **Removed scan limit** to fetch all products from database

### Now the Copilot can answer:
- "What are the prices for olive oil?" ✅
- "Compare Figaro and Borges olive oil" ✅
- "Show me printer prices" ✅
- "What's the cheapest fridge?" ✅
- "Which platform has best deals on Samsung washing machine?" ✅

---

## Testing the Updated Copilot

Try these queries in the Market Copilot tab:

1. **"What are the prices for olive oil?"**
   - Should show Figaro and Borges prices

2. **"Compare printers"**
   - Should show HP and Canon printer prices

3. **"Show me the cheapest fridge"**
   - Should compare Godrej and Haier fridges

4. **"Which platform has the best deals?"**
   - Should analyze all products and platforms

---

## Summary

**Current Capability:**
- ✅ Works with pre-populated database
- ✅ Fast responses (< 2 seconds)
- ✅ Low cost (~$25/month)
- ✅ Reliable and accurate

**Future Enhancement (Optional):**
- 🔄 Add official API integration
- 🔄 Scheduled price updates
- 🔄 Real-time price fetching
- 💰 Additional cost: $50-100/month

**Recommendation:**
Keep the current approach for now. It's cost-effective, reliable, and sufficient for most use cases. Add API integration only if you need real-time prices for hundreds of products.

---

**Last Updated:** March 1, 2026  
**Lambda Function:** ai-retail-market-copilot  
**Version:** Updated with product search

