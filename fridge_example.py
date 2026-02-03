#!/usr/bin/env python3
"""
Simple Fridge Price Comparison Example
=====================================

Exactly matching the user's scenario:
Customer wants a fridge, checks various websites.
Our project finds the best lowest price.
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from competitive_pricing import CompetitivePricingEngine


def main():
    print("🔍 Customer Scenario: Looking for Godrej Single Door Fridge")
    print("=" * 60)
    
    # Initialize our pricing engine
    engine = CompetitivePricingEngine()
    
    # Customer searches for fridge
    comparison = engine.compare_prices("P006")  # Godrej fridge
    
    if comparison:
        print(f"\nProduct: {comparison.product_name}")
        print("\nPlatform        Price (₹)")
        print("-" * 32)
        
        # Sort platforms by price for better display
        sorted_prices = sorted(comparison.current_prices.items(), key=lambda x: x[1])
        
        for platform, price in sorted_prices:
            marker = "   ← Cheapest" if platform == comparison.lowest_platform else ""
            print(f"{platform:<15} {price:>8,.0f}{marker}")
        
        print(f"\nVariation: {comparison.price_difference_percentage:.0f}% difference between highest and lowest.")
        print(f"Recommendation: {comparison.recommendation}")
        
        print(f"\n💰 SAVINGS SUMMARY:")
        print(f"Save ₹{comparison.savings_amount:,.0f} by choosing {comparison.lowest_platform} over {comparison.highest_platform}")
        
    else:
        print("❌ Product not found")


if __name__ == "__main__":
    main()