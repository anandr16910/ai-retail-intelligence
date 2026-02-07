#!/usr/bin/env python3
"""
Generate Household Items Price History
======================================

Generate price history for various household items that have shown
significant price variations in the Indian market over the past 2 years.
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta

def generate_household_items():
    """Generate 2-year price history for household items with variations."""
    
    print("🏠 Generating Household Items Price History (2 Years)")
    print("=" * 60)
    
    # Date range: 2 years (730 days) ending today
    end_date = datetime.now().date()
    start_date = end_date - timedelta(days=730)
    dates = pd.date_range(start=start_date, end=end_date, freq='D')
    
    all_data = []
    
    # Product 1: Sunflower Oil 1L (Price increased due to Ukraine crisis)
    print("\n🌻 Fortune Sunflower Oil 1L")
    print("   Starting Price: ₹140 → Current Price: ₹180 (↑29%)")
    print("   Reason: Ukraine-Russia conflict impact on supply")
    
    sunflower_data = generate_product_prices(
        dates=dates,
        product_id="P009",
        product_name="Fortune Sunflower Oil 1L",
        start_price=140.0,
        end_price=180.0,
        trend_type="increase",
        platform_variations={
            'amazon': 0.0,
            'flipkart': 3.0,
            'jiomart': -5.0,
            'blinkit': 8.0,
            'zepto': 7.0,
            'dmart_ready': -8.0
        }
    )
    all_data.extend(sunflower_data)
    
    # Product 2: Mustard Oil 1L (Volatile pricing)
    print("\n🌾 Dhara Mustard Oil 1L")
    print("   Starting Price: ₹165 → Current Price: ₹195 (↑18%)")
    print("   Reason: Crop yield variations, seasonal demand")
    
    mustard_data = generate_product_prices(
        dates=dates,
        product_id="P010",
        product_name="Dhara Mustard Oil 1L",
        start_price=165.0,
        end_price=195.0,
        trend_type="increase",
        platform_variations={
            'amazon': 0.0,
            'flipkart': 4.0,
            'jiomart': -6.0,
            'blinkit': 10.0,
            'zepto': 9.0,
            'dmart_ready': -10.0
        }
    )
    all_data.extend(mustard_data)
    
    # Product 3: Toor Dal 1kg (High volatility)
    print("\n🫘 Toor Dal 1kg")
    print("   Starting Price: ₹120 → Current Price: ₹160 (↑33%)")
    print("   Reason: Monsoon impact, import dependency")
    
    toor_dal_data = generate_product_prices(
        dates=dates,
        product_id="P011",
        product_name="Toor Dal 1kg",
        start_price=120.0,
        end_price=160.0,
        trend_type="increase",
        platform_variations={
            'amazon': 0.0,
            'flipkart': 5.0,
            'jiomart': -8.0,
            'blinkit': 12.0,
            'zepto': 10.0,
            'dmart_ready': -12.0
        }
    )
    all_data.extend(toor_dal_data)
    
    # Product 4: Dove Shampoo 650ml (Price decreased due to competition)
    print("\n🧴 Dove Shampoo 650ml")
    print("   Starting Price: ₹450 → Current Price: ₹320 (↓29%)")
    print("   Reason: Increased competition, local brands")
    
    shampoo_data = generate_product_prices(
        dates=dates,
        product_id="P012",
        product_name="Dove Shampoo 650ml",
        start_price=450.0,
        end_price=320.0,
        trend_type="decrease",
        platform_variations={
            'amazon': 0.0,
            'flipkart': 10.0,
            'jiomart': -15.0,
            'blinkit': 20.0,
            'zepto': 18.0,
            'dmart_ready': -25.0
        }
    )
    all_data.extend(shampoo_data)
    
    # Product 5: Surf Excel Detergent 2kg (Gradual increase)
    print("\n🧼 Surf Excel Detergent 2kg")
    print("   Starting Price: ₹380 → Current Price: ₹450 (↑18%)")
    print("   Reason: Raw material cost increase")
    
    detergent_data = generate_product_prices(
        dates=dates,
        product_id="P013",
        product_name="Surf Excel Detergent 2kg",
        start_price=380.0,
        end_price=450.0,
        trend_type="increase",
        platform_variations={
            'amazon': 0.0,
            'flipkart': 8.0,
            'jiomart': -12.0,
            'blinkit': 15.0,
            'zepto': 13.0,
            'dmart_ready': -18.0
        }
    )
    all_data.extend(detergent_data)
    
    # Product 6: Vim Dishwash Gel 750ml (Stable with promotions)
    print("\n🍽️ Vim Dishwash Gel 750ml")
    print("   Starting Price: ₹180 → Current Price: ₹165 (↓8%)")
    print("   Reason: Aggressive promotions, market competition")
    
    dishwash_data = generate_product_prices(
        dates=dates,
        product_id="P014",
        product_name="Vim Dishwash Gel 750ml",
        start_price=180.0,
        end_price=165.0,
        trend_type="decrease",
        platform_variations={
            'amazon': 0.0,
            'flipkart': 5.0,
            'jiomart': -8.0,
            'blinkit': 10.0,
            'zepto': 9.0,
            'dmart_ready': -12.0
        }
    )
    all_data.extend(dishwash_data)
    
    # Product 7: Red Label Tea 1kg (Seasonal variations)
    print("\n☕ Red Label Tea 1kg")
    print("   Starting Price: ₹420 → Current Price: ₹480 (↑14%)")
    print("   Reason: Tea plantation yield, export demand")
    
    tea_data = generate_product_prices(
        dates=dates,
        product_id="P015",
        product_name="Red Label Tea 1kg",
        start_price=420.0,
        end_price=480.0,
        trend_type="increase",
        platform_variations={
            'amazon': 0.0,
            'flipkart': 6.0,
            'jiomart': -10.0,
            'blinkit': 12.0,
            'zepto': 11.0,
            'dmart_ready': -15.0
        }
    )
    all_data.extend(tea_data)
    
    # Product 8: Colgate Toothpaste 500g (Stable pricing)
    print("\n🦷 Colgate Toothpaste 500g")
    print("   Starting Price: ₹220 → Current Price: ₹235 (↑7%)")
    print("   Reason: Inflation adjustment")
    
    toothpaste_data = generate_product_prices(
        dates=dates,
        product_id="P016",
        product_name="Colgate Toothpaste 500g",
        start_price=220.0,
        end_price=235.0,
        trend_type="increase",
        platform_variations={
            'amazon': 0.0,
            'flipkart': 5.0,
            'jiomart': -8.0,
            'blinkit': 10.0,
            'zepto': 9.0,
            'dmart_ready': -12.0
        }
    )
    all_data.extend(toothpaste_data)
    
    # Create DataFrame
    df = pd.DataFrame(all_data)
    
    # Save to CSV
    output_file = "data/household_items_2years.csv"
    df.to_csv(output_file, index=False)
    
    print(f"\n✅ Generated {len(df)} records")
    print(f"✅ Saved to: {output_file}")
    
    # Show summary
    show_summary(df)
    
    return df

def generate_product_prices(dates, product_id, product_name, start_price, end_price, 
                           trend_type, platform_variations):
    """Generate price history for a single product."""
    
    num_days = len(dates)
    data = []
    
    # Calculate overall change
    total_change = end_price - start_price
    
    for i, date in enumerate(dates):
        progress = i / num_days
        
        # Calculate base price based on trend type
        if trend_type == "increase":
            # Gradual increase with some volatility
            base_price = start_price + (total_change * progress)
            
            # Add seasonal spikes (festival seasons)
            month = date.month
            if month in [10, 11]:  # Diwali season
                base_price *= 1.03
            elif month in [3, 4]:  # Holi season
                base_price *= 1.02
                
        else:  # decrease
            # Gradual decrease with promotions
            base_price = start_price + (total_change * progress)
            
            # Add promotional drops
            if np.random.random() < 0.08:  # 8% chance
                base_price *= 0.92  # 8% discount
        
        # Add random daily fluctuations
        daily_variation = np.random.uniform(-0.03, 0.03)
        base_price *= (1 + daily_variation)
        
        # Generate prices for each platform
        row = {
            'date': date.strftime('%Y-%m-%d'),
            'product_id': product_id,
            'product_name': product_name
        }
        
        for platform, variation in platform_variations.items():
            platform_price = base_price + variation
            
            # Add platform-specific volatility
            platform_volatility = np.random.uniform(-5, 5)
            platform_price += platform_volatility
            
            # Ensure reasonable minimum
            min_price = min(start_price, end_price) * 0.85
            platform_price = max(platform_price, min_price)
            
            row[platform] = round(platform_price, 2)
        
        data.append(row)
    
    return data

def show_summary(df):
    """Show price summary for all products."""
    
    print("\n📊 Price Summary:")
    print("=" * 60)
    
    for product_id in df['product_id'].unique():
        product_data = df[df['product_id'] == product_id]
        product_name = product_data['product_name'].iloc[0]
        
        print(f"\n{product_name}:")
        
        for platform in ['amazon', 'flipkart', 'jiomart', 'blinkit', 'zepto', 'dmart_ready']:
            if platform in product_data.columns:
                prices = product_data[platform].dropna()
                if len(prices) > 0:
                    start_price = prices.iloc[0]
                    end_price = prices.iloc[-1]
                    change = end_price - start_price
                    change_pct = (change / start_price) * 100
                    
                    arrow = "↑" if change > 0 else "↓" if change < 0 else "→"
                    print(f"  {platform:12s}: ₹{start_price:,.2f} → ₹{end_price:,.2f} "
                          f"({arrow}₹{abs(change):.2f}, {change_pct:+.1f}%)")

def append_to_main_csv(household_df):
    """Append household items data to main competitive pricing CSV."""
    
    print("\n📝 Appending to main competitive pricing CSV...")
    
    try:
        main_csv = "data/competitive_pricing_sample.csv"
        existing_df = pd.read_csv(main_csv)
        
        # Combine dataframes
        combined_df = pd.concat([existing_df, household_df], ignore_index=True)
        
        # Sort by date and product_id
        combined_df['date'] = pd.to_datetime(combined_df['date'])
        combined_df = combined_df.sort_values(['date', 'product_id']).reset_index(drop=True)
        
        # Save back
        combined_df.to_csv(main_csv, index=False)
        
        print(f"✅ Updated {main_csv}")
        print(f"   Total records: {len(combined_df)}")
        
    except Exception as e:
        print(f"⚠️ Could not append to main CSV: {str(e)}")
        print("   Household items data saved separately")

def show_market_insights():
    """Show market insights for household items."""
    
    print("\n" + "=" * 60)
    print("📈 Indian Household Items Market Insights (2022-2024)")
    print("=" * 60)
    
    print("\n🔴 PRICE INCREASES:")
    print("  1. Cooking Oils (Sunflower +29%, Mustard +18%)")
    print("     → Ukraine crisis, crop yield variations")
    print("  2. Pulses (Toor Dal +33%)")
    print("     → Monsoon impact, import dependency")
    print("  3. Detergents (Surf Excel +18%)")
    print("     → Raw material cost increase")
    print("  4. Tea (Red Label +14%)")
    print("     → Plantation yield, export demand")
    
    print("\n🟢 PRICE DECREASES:")
    print("  1. Olive Oil (Borges/Figaro -33%)")
    print("     → Increased competition, bulk procurement")
    print("  2. Personal Care (Dove Shampoo -29%)")
    print("     → Local brand competition")
    print("  3. Cleaning Products (Vim -8%)")
    print("     → Aggressive promotions")
    
    print("\n💡 CONSUMER STRATEGIES:")
    print("  • Buy cooking oils in bulk during low-price periods")
    print("  • Stock pulses before monsoon season")
    print("  • Take advantage of personal care promotions")
    print("  • DMart Ready consistently offers lowest prices")
    print("  • Quick commerce (Blinkit/Zepto) premium for convenience")
    
    print("\n🏪 PLATFORM INSIGHTS:")
    print("  • DMart Ready: Best for staples (avg -12% vs others)")
    print("  • JioMart: Competitive on FMCG (-8% avg)")
    print("  • Amazon/Flipkart: Mid-range, frequent sales")
    print("  • Quick Commerce: Premium pricing (+10-15%)")

if __name__ == "__main__":
    # Generate household items prices
    household_df = generate_household_items()
    
    # Show market insights
    show_market_insights()
    
    print("\n" + "=" * 60)
    print("💡 Next Steps:")
    print("1. Review: data/household_items_2years.csv")
    print("2. Append to main CSV: Uncomment append_to_main_csv() below")
    print("3. Restart services: python restart_services.py")
    
    # Append to main CSV
    append_to_main_csv(household_df)
