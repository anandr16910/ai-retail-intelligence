# ⚡ Quick Start: Update Prices from AWS Console

**5-Minute Guide to Update Gold, Silver, and Product Prices**

---

## 🥇 Update Gold Price (2 minutes)

### Step-by-Step:

1. **Open AWS Console** → Type "DynamoDB" in search → Click **DynamoDB**

2. **Open Table** → Click **"Tables"** (left sidebar) → Click **"PriceHistory"**

3. **View Items** → Click **"Explore table items"** button

4. **Create New Price** → Click **"Create item"** button (top right)

5. **Fill Form:**
   ```
   asset (String):     GOLD
   timestamp (String): 2026-03-01
   open (Number):      161000
   high (Number):      163000
   low (Number):       160000
   close (Number):     162000
   volume (Number):    450000
   ```

6. **Save** → Click **"Create item"** button at bottom

7. **Done!** → Refresh your dashboard to see new price

---

## 🥈 Update Silver Price (2 minutes)

Same steps as Gold, but use:
```
asset (String):     SILVER
timestamp (String): 2026-03-01
open (Number):      330000
high (Number):      338000
low (Number):       329000
close (Number):     335000
volume (Number):    280000
```

---

## 🧊 Update Fridge Price (3 minutes)

### Step-by-Step:

1. **Open DynamoDB** → Click **"Tables"** → Click **"CompetitivePricing"**

2. **View Items** → Click **"Explore table items"**

3. **Create Product** → Click **"Create item"**

4. **Switch to JSON View** → Toggle from "Form" to "JSON" (top right)

5. **Paste This:**
   ```json
   {
     "product_id": {
       "S": "P001"
     },
     "product_name": {
       "S": "Godrej Single Door Fridge 190L"
     },
     "category": {
       "S": "home_appliances"
     },
     "prices": {
       "M": {
         "Amazon": {
           "N": "17999"
         },
         "Flipkart": {
           "N": "18490"
         },
         "Zepto": {
           "N": "16999"
         },
         "Blinkit": {
           "N": "17500"
         },
         "BigBasket": {
           "N": "18200"
         },
         "Swiggy": {
           "N": "17800"
         }
       }
     },
     "last_updated": {
       "S": "2026-03-01T10:00:00Z"
     }
   }
   ```

6. **Save** → Click **"Create item"**

7. **Done!** → Product now appears in competitive pricing

---

## 🎨 Change Dashboard Colors (1 minute)

### Step-by-Step:

1. **Open S3** → AWS Console → Type "S3" → Click **S3**

2. **Open Bucket** → Click **"ai-retail-dashboard-439786465522"**

3. **Download File** → Check **"index.html"** → Click **"Actions"** → **"Download"**

4. **Edit File** → Open with Notepad/TextEdit

5. **Find & Replace:**
   - Find: `#667eea` (purple)
   - Replace with: `#FF6B6B` (red) or any color you want

6. **Upload** → Back to S3 → Click **"Upload"** → Drag edited file → Click **"Upload"**

7. **Done!** → Refresh dashboard to see new colors

---

## 📊 Add More Products

### Quick Template (Copy & Modify):

```json
{
  "product_id": {"S": "P002"},
  "product_name": {"S": "Samsung Washing Machine 7kg"},
  "category": {"S": "home_appliances"},
  "prices": {
    "M": {
      "Amazon": {"N": "22999"},
      "Flipkart": {"N": "23500"},
      "Zepto": {"N": "22500"},
      "Blinkit": {"N": "23000"},
      "BigBasket": {"N": "24000"},
      "Swiggy": {"N": "23200"}
    }
  },
  "last_updated": {"S": "2026-03-01T10:00:00Z"}
}
```

**Just change:**
- `P002` → `P003`, `P004`, etc.
- Product name
- Prices for each platform

---

## 🔍 View Your Changes

### Check Logs:

1. **CloudWatch** → AWS Console → Type "CloudWatch"

2. **Logs** → Click **"Logs"** → **"Log groups"**

3. **Lambda Logs** → Click `/aws/lambda/ai-retail-current-prices`

4. **View** → See all API calls and data fetches

---

## 💰 Monitor Costs

### Set Up Alert:

1. **Billing** → AWS Console → Click your name (top right) → **"Billing Dashboard"**

2. **Budgets** → Click **"Budgets"** (left sidebar)

3. **Create** → Click **"Create budget"**

4. **Set Amount** → Enter $50 (or your limit)

5. **Email** → Enter your email for alerts

6. **Done!** → Get notified if costs exceed limit

---

## 🎯 Most Common Tasks

| Task | Service | Time |
|------|---------|------|
| Update Gold/Silver price | DynamoDB → PriceHistory | 2 min |
| Add product | DynamoDB → CompetitivePricing | 3 min |
| Change colors | S3 → Download/Edit/Upload | 1 min |
| View logs | CloudWatch → Logs | 30 sec |
| Check costs | Billing Dashboard | 30 sec |

---

## 📱 Mobile Access

You can do all of this from your phone!

1. Download **AWS Console Mobile App**
2. Login with your credentials
3. Access DynamoDB, S3, CloudWatch
4. Update prices on the go!

---

## ⚠️ Important Notes

- **Timestamp Format:** Always use `YYYY-MM-DD` (e.g., 2026-03-01)
- **Number Format:** No commas, just digits (e.g., 162000 not 162,000)
- **Backup First:** Download files before editing
- **Test Changes:** Check dashboard after updates

---

## 🆘 Quick Troubleshooting

**Dashboard not updating?**
→ Clear browser cache (Ctrl+Shift+R or Cmd+Shift+R)

**Price not showing?**
→ Check DynamoDB item was created successfully

**Error on dashboard?**
→ Check CloudWatch logs for Lambda function

**High costs?**
→ Check Billing Dashboard → Cost Explorer

---

## 📞 Need Help?

1. Check **AWS_CONSOLE_MANAGEMENT_GUIDE.md** for detailed instructions
2. View CloudWatch logs for errors
3. Contact AWS Support from console

---

**Your Dashboard:** http://ai-retail-dashboard-439786465522.s3-website-us-east-1.amazonaws.com

**AWS Console:** https://console.aws.amazon.com

**Account:** 439786465522  
**Region:** us-east-1

---

**Pro Tip:** Bookmark your DynamoDB tables in browser for quick access!
