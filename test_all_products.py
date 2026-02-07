#!/usr/bin/env python3
"""
Test All Products in Competitive Pricing Engine
===============================================

Quick test to verify all 16 products are loaded and working correctly.
"""

from src.competitive_pricing import CompetitivePricingEngine

def test_all_products():
    """Test price comparison for all products."""
    
    print("🧪 Testing All Products in Competitive Pricing Engine")
    print("=" * 60)
    
    # Initialize engine
    engine = CompetitivePricingEngine()
    
    # Get all products
    products = engine.get_product_list()
    print(f"\n✅ Total Products Loaded: {len(products)}")
    
    # Test each product
    print("\n📊 Testing Price Comparison for Each Product:")
    print("-" * 60)
    
    success_count = 0
    fail_count = 0
    
    for product in products:
        product_id = product['product_id']
        product_name = product['product_name']
        
        try:
            # Compare prices
            result = engine.compare_prices(product_id)
            
            if result:
                print(f"\n✅ {product_id}: {product_name}")
                print(f"   Lowest: {result.lowest_platform} (₹{result.lowest_price:.2f})")
                print(f"   Highest: {result.highest_platform} (₹{result.highest_price:.2f})")
                print(f"   Savings: ₹{result.savings_amount:.2f} ({result.price_difference_percentage:.1f}%)")
                success_count += 1
            else:
                print(f"\n❌ {product_id}: {product_name} - No comparison data")
                fail_count += 1
                
        except Exception as e:
            print(f"\n❌ {product_id}: {product_name} - Error: {str(e)}")
            fail_count += 1
    
    # Summary
    print("\n" + "=" * 60)
    print("📈 Test Summary:")
    print(f"   ✅ Successful: {success_count}/{len(products)}")
    print(f"   ❌ Failed: {fail_count}/{len(products)}")
    
    if fail_count == 0:
        print("\n🎉 All products working correctly!")
    else:
        print(f"\n⚠️ {fail_count} products need attention")
    
    # Test best deals
    print("\n" + "=" * 60)
    print("💰 Top 5 Best Deals:")
    print("-" * 60)
    
    deals = engine.get_best_deals(5)
    for i, deal in enumerate(deals, 1):
        print(f"{i}. {deal['product_name']}")
        print(f"   Save ₹{deal['savings_amount']:.2f} ({deal['savings_percentage']:.1f}%)")
        print(f"   Buy from: {deal['lowest_platform']} (₹{deal['lowest_price']:.2f})")
    
    # Platform summary
    print("\n" + "=" * 60)
    print("🏪 Platform Summary:")
    print("-" * 60)
    
    summary = engine.get_platform_summary()
    print(f"Total Products: {summary['total_products']}")
    print(f"Date Range: {summary['date_range']['start']} to {summary['date_range']['end']}")
    print(f"\nPlatform Statistics:")
    
    for platform, stats in summary['platform_stats'].items():
        print(f"\n{platform}:")
        print(f"  Avg Price: ₹{stats['avg_price']:.2f}")
        print(f"  Min Price: ₹{stats['min_price']:.2f}")
        print(f"  Max Price: ₹{stats['max_price']:.2f}")
        print(f"  Listings: {stats['total_listings']}")

if __name__ == "__main__":
    test_all_products()
