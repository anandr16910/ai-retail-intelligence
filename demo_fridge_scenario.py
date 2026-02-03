#!/usr/bin/env python3
"""
Demo: Fridge Price Comparison Scenario
=====================================

This demo shows how a customer looking for a Godrej Single Door Fridge
can use our AI Retail Intelligence Platform to find the best deals
across multiple Indian e-commerce platforms.

Scenario: Customer wants to buy a fridge and checks various websites.
Our system finds the best lowest price automatically.
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from competitive_pricing import CompetitivePricingEngine, CompetitivePricingCopilot
from market_copilot import MarketCopilot


def print_header(title):
    """Print formatted header."""
    print("\n" + "="*60)
    print(f"  {title}")
    print("="*60)


def print_section(title):
    """Print formatted section."""
    print(f"\n📋 {title}")
    print("-" * 40)


def demo_direct_api():
    """Demo using direct API calls."""
    print_header("DIRECT API DEMO: Fridge Price Comparison")
    
    # Initialize the competitive pricing engine
    engine = CompetitivePricingEngine()
    
    print("🔍 Searching for Godrej Single Door Fridge...")
    
    # Search for the fridge
    products = engine.search_products("Godrej")
    if products:
        product = products[0]  # Get the fridge
        print(f"✅ Found: {product['product_name']} (ID: {product['product_id']})")
        
        # Get price comparison
        comparison = engine.compare_prices(product['product_id'])
        
        if comparison:
            print_section("PRICE COMPARISON RESULTS")
            
            print(f"Product: {comparison.product_name}")
            print(f"Analysis Date: {comparison.analysis_timestamp.strftime('%Y-%m-%d %H:%M:%S')}")
            print()
            
            # Show platform prices in a table format
            print("Platform        Price (₹)    Status")
            print("-" * 40)
            
            for platform, price in comparison.current_prices.items():
                status = ""
                if platform == comparison.lowest_platform:
                    status = "← CHEAPEST 🏆"
                elif platform == comparison.highest_platform:
                    status = "← HIGHEST 💸"
                
                print(f"{platform:<15} {price:>8,.0f}    {status}")
            
            print()
            print_section("SAVINGS ANALYSIS")
            print(f"💰 Lowest Price:  ₹{comparison.lowest_price:,.0f} ({comparison.lowest_platform})")
            print(f"💸 Highest Price: ₹{comparison.highest_price:,.0f} ({comparison.highest_platform})")
            print(f"💵 You Save:      ₹{comparison.savings_amount:,.0f}")
            print(f"📊 Variation:     {comparison.price_difference_percentage:.1f}% difference between highest and lowest")
            
            print_section("RECOMMENDATION")
            print(f"🎯 {comparison.recommendation}")
            
            # Show price trends
            if comparison.trend_7_days:
                print_section("7-DAY PRICE TRENDS")
                for platform, trend in comparison.trend_7_days.items():
                    trend_icon = "📈" if trend > 0 else "📉" if trend < 0 else "➡️"
                    trend_text = "increasing" if trend > 0 else "decreasing" if trend < 0 else "stable"
                    print(f"{platform}: {trend:+.1f}% ({trend_text}) {trend_icon}")
        
        else:
            print("❌ No pricing data available for this product")
    else:
        print("❌ No Godrej products found")


def demo_natural_language():
    """Demo using natural language queries."""
    print_header("NATURAL LANGUAGE DEMO: Market Copilot")
    
    # Initialize engines
    pricing_engine = CompetitivePricingEngine()
    pricing_copilot = CompetitivePricingCopilot(pricing_engine)
    market_copilot = MarketCopilot(pricing_copilot)
    
    # Customer queries
    customer_queries = [
        "I want to buy a fridge, can you help me find the best price?",
        "Compare prices for Godrej fridge",
        "Which platform has the cheapest fridge?",
        "How much can I save on the fridge?",
        "Show me the best deals available"
    ]
    
    print("🤖 Customer interacting with AI Market Copilot:")
    print()
    
    for i, query in enumerate(customer_queries, 1):
        print(f"👤 Customer Query {i}: {query}")
        
        # Process query through market copilot
        response = market_copilot.process_query(query)
        
        print(f"🤖 AI Assistant: {response}")
        print()
        print("-" * 50)
        print()


def demo_api_endpoints():
    """Demo showing API endpoint responses."""
    print_header("API ENDPOINTS DEMO: REST API Responses")
    
    engine = CompetitivePricingEngine()
    
    print_section("GET /api/v1/price-comparison/products")
    products = engine.get_product_list()
    print("Available products:")
    for product in products:
        print(f"  - {product['product_name']} (ID: {product['product_id']})")
    
    print_section("GET /api/v1/price-comparison/Godrej")
    fridge_products = engine.search_products("Godrej")
    if fridge_products:
        product_id = fridge_products[0]['product_id']
        comparison = engine.compare_prices(product_id)
        
        if comparison:
            # Simulate API JSON response
            api_response = {
                "success": True,
                "message": "Price comparison for Godrej Single Door Fridge",
                "data": comparison.to_dict()
            }
            
            print("API Response (JSON):")
            import json
            print(json.dumps(api_response, indent=2, default=str))
    
    print_section("GET /api/v1/price-comparison/best-deals")
    deals = engine.get_best_deals(3)
    print("Top 3 Best Deals:")
    for i, deal in enumerate(deals, 1):
        print(f"{i}. {deal['product_name']}")
        print(f"   Save ₹{deal['savings_amount']:.2f} by buying from {deal['lowest_platform']}")
        print(f"   Price: ₹{deal['lowest_price']:.2f} (vs ₹{deal['highest_price']:.2f})")
        print()


def demo_business_value():
    """Demo showing business value and metrics."""
    print_header("BUSINESS VALUE DEMO: Platform Analytics")
    
    engine = CompetitivePricingEngine()
    
    print_section("PLATFORM SUMMARY")
    summary = engine.get_platform_summary()
    
    print(f"📊 Total Products Tracked: {summary.get('total_products', 0)}")
    print(f"🏪 Platforms Monitored: {len(summary.get('platforms', []))}")
    print(f"📅 Data Range: {summary.get('date_range', {}).get('start')} to {summary.get('date_range', {}).get('end')}")
    print()
    
    print("Platform Statistics:")
    platform_stats = summary.get('platform_stats', {})
    for platform, stats in platform_stats.items():
        print(f"  {platform}:")
        print(f"    Average Price: ₹{stats.get('avg_price', 0):,.2f}")
        print(f"    Price Range: ₹{stats.get('min_price', 0):,.2f} - ₹{stats.get('max_price', 0):,.2f}")
        print(f"    Total Listings: {stats.get('total_listings', 0)}")
        print()
    
    print_section("CUSTOMER SAVINGS POTENTIAL")
    deals = engine.get_best_deals(5)
    total_savings = sum(deal['savings_amount'] for deal in deals)
    
    print(f"💰 Total Potential Savings Across Top 5 Products: ₹{total_savings:.2f}")
    print(f"📈 Average Savings Per Product: ₹{total_savings/len(deals):.2f}")
    print()
    
    print("Savings Breakdown:")
    for deal in deals:
        savings_pct = (deal['savings_amount'] / deal['highest_price']) * 100
        print(f"  {deal['product_name']}: ₹{deal['savings_amount']:.2f} ({savings_pct:.1f}%)")


def main():
    """Run all demos."""
    print("🚀 AI RETAIL INTELLIGENCE PLATFORM")
    print("   Competitive Pricing Intelligence Demo")
    print("   Scenario: Customer looking for best fridge prices")
    
    try:
        # Run all demo scenarios
        demo_direct_api()
        demo_natural_language()
        demo_api_endpoints()
        demo_business_value()
        
        print_header("DEMO COMPLETE")
        print("✅ All scenarios completed successfully!")
        print()
        print("🎯 Key Takeaways:")
        print("  • Customers can save significant money through price comparison")
        print("  • Natural language interface makes it easy to find deals")
        print("  • REST API enables integration with existing systems")
        print("  • Real-time price tracking across major Indian platforms")
        print("  • Comprehensive analytics for business intelligence")
        
    except Exception as e:
        print(f"❌ Demo failed: {str(e)}")
        return 1
    
    return 0


if __name__ == "__main__":
    exit(main())