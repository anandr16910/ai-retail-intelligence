"""Competitive Pricing Intelligence module for AI Retail Intelligence Platform."""

import os
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass

from src.config import settings
from src.exceptions import DataLoadingError, PricingEngineError
from src.logger import app_logger


@dataclass
class PriceComparison:
    """Data model for price comparison results."""
    product_id: str
    product_name: str
    current_prices: Dict[str, float]
    lowest_platform: str
    highest_platform: str
    lowest_price: float
    highest_price: float
    price_difference_percentage: float
    savings_amount: float
    recommendation: str
    trend_7_days: Dict[str, float]
    trend_30_days: Dict[str, float]
    analysis_timestamp: datetime
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            'product_id': self.product_id,
            'product_name': self.product_name,
            'current_prices': self.current_prices,
            'lowest_platform': self.lowest_platform,
            'highest_platform': self.highest_platform,
            'lowest_price': self.lowest_price,
            'highest_price': self.highest_price,
            'price_difference_percentage': self.price_difference_percentage,
            'savings_amount': self.savings_amount,
            'recommendation': self.recommendation,
            'trend_7_days': self.trend_7_days,
            'trend_30_days': self.trend_30_days,
            'analysis_timestamp': self.analysis_timestamp.isoformat()
        }


class CompetitivePricingEngine:
    """Engine for competitive pricing analysis across multiple platforms."""
    
    def __init__(self, data_dir: str = None):
        """Initialize competitive pricing engine."""
        self.data_dir = data_dir or settings.data_dir
        self.platforms = [
            'Amazon', 'Flipkart', 'JioMart', 
            'Blinkit', 'Zepto', 'DMart_Ready'
        ]
        self.pricing_data = None
        self.load_pricing_data()
    
    def load_pricing_data(self):
        """Load competitive pricing data from CSV."""
        try:
            csv_path = os.path.join(self.data_dir, "competitive_pricing_sample.csv")
            
            if not os.path.exists(csv_path):
                app_logger.warning(f"Competitive pricing CSV not found: {csv_path}")
                return
            
            self.pricing_data = pd.read_csv(csv_path)
            
            # Convert date column to datetime
            if 'date' in self.pricing_data.columns:
                self.pricing_data['date'] = pd.to_datetime(self.pricing_data['date'])
            
            app_logger.info(f"Loaded competitive pricing data: {len(self.pricing_data)} records")
            
        except Exception as e:
            app_logger.error(f"Failed to load competitive pricing data: {str(e)}")
            self.pricing_data = None
    
    def compare_prices(self, product_id: str) -> Optional[PriceComparison]:
        """Compare prices across platforms for a specific product."""
        try:
            if self.pricing_data is None:
                raise PricingEngineError("Pricing data not loaded")
            
            # Filter data for the specific product
            product_data = self.pricing_data[
                self.pricing_data['product_id'] == product_id
            ].copy()
            
            if product_data.empty:
                app_logger.warning(f"No data found for product_id: {product_id}")
                return None
            
            # Get the most recent data for current prices
            latest_date = product_data['date'].max()
            current_data = product_data[product_data['date'] == latest_date]
            
            if current_data.empty:
                return None
            
            # Extract current prices for each platform
            current_prices = {}
            for platform in self.platforms:
                platform_col = platform.lower().replace('_', '_')
                if platform_col in current_data.columns:
                    price = current_data[platform_col].iloc[0]
                    if pd.notna(price) and price > 0:
                        current_prices[platform] = float(price)
            
            if not current_prices:
                return None
            
            # Find lowest and highest prices
            lowest_platform = min(current_prices, key=current_prices.get)
            highest_platform = max(current_prices, key=current_prices.get)
            lowest_price = current_prices[lowest_platform]
            highest_price = current_prices[highest_platform]
            
            # Calculate price difference percentage
            price_diff_pct = ((highest_price - lowest_price) / lowest_price) * 100
            savings_amount = highest_price - lowest_price
            
            # Generate recommendation
            recommendation = f"Buy from {lowest_platform} to save ₹{savings_amount:.2f} ({price_diff_pct:.1f}%)"
            
            # Calculate trends
            trend_7_days = self._calculate_trend(product_data, 7)
            trend_30_days = self._calculate_trend(product_data, 30)
            
            # Get product name
            product_name = current_data['product_name'].iloc[0] if 'product_name' in current_data.columns else product_id
            
            return PriceComparison(
                product_id=product_id,
                product_name=product_name,
                current_prices=current_prices,
                lowest_platform=lowest_platform,
                highest_platform=highest_platform,
                lowest_price=lowest_price,
                highest_price=highest_price,
                price_difference_percentage=price_diff_pct,
                savings_amount=savings_amount,
                recommendation=recommendation,
                trend_7_days=trend_7_days,
                trend_30_days=trend_30_days,
                analysis_timestamp=datetime.now()
            )
            
        except Exception as e:
            app_logger.error(f"Price comparison failed for {product_id}: {str(e)}")
            return None
    
    def _calculate_trend(self, product_data: pd.DataFrame, days: int) -> Dict[str, float]:
        """Calculate price trends over specified number of days."""
        try:
            cutoff_date = product_data['date'].max() - timedelta(days=days)
            trend_data = product_data[product_data['date'] >= cutoff_date]
            
            trends = {}
            for platform in self.platforms:
                platform_col = platform.lower().replace('_', '_')
                if platform_col in trend_data.columns:
                    platform_prices = trend_data[platform_col].dropna()
                    
                    if len(platform_prices) >= 2:
                        # Calculate percentage change from first to last
                        first_price = platform_prices.iloc[0]
                        last_price = platform_prices.iloc[-1]
                        
                        if first_price > 0:
                            trend_pct = ((last_price - first_price) / first_price) * 100
                            trends[platform] = round(trend_pct, 2)
            
            return trends
            
        except Exception as e:
            app_logger.error(f"Trend calculation failed: {str(e)}")
            return {}
    
    def get_product_list(self) -> List[Dict[str, str]]:
        """Get list of available products."""
        try:
            if self.pricing_data is None:
                return []
            
            products = self.pricing_data[['product_id', 'product_name']].drop_duplicates()
            return products.to_dict('records')
            
        except Exception as e:
            app_logger.error(f"Failed to get product list: {str(e)}")
            return []
    
    def search_products(self, query: str) -> List[Dict[str, str]]:
        """Search products by name."""
        try:
            if self.pricing_data is None:
                return []
            
            # Case-insensitive search
            mask = self.pricing_data['product_name'].str.contains(
                query, case=False, na=False
            )
            
            products = self.pricing_data[mask][['product_id', 'product_name']].drop_duplicates()
            return products.to_dict('records')
            
        except Exception as e:
            app_logger.error(f"Product search failed: {str(e)}")
            return []
    
    def get_platform_summary(self) -> Dict[str, Any]:
        """Get summary statistics for all platforms."""
        try:
            if self.pricing_data is None:
                return {}
            
            summary = {
                'total_products': len(self.pricing_data['product_id'].unique()),
                'platforms': self.platforms,
                'date_range': {
                    'start': self.pricing_data['date'].min().strftime('%Y-%m-%d'),
                    'end': self.pricing_data['date'].max().strftime('%Y-%m-%d')
                },
                'platform_stats': {}
            }
            
            # Calculate stats for each platform
            for platform in self.platforms:
                platform_col = platform.lower().replace('_', '_')
                if platform_col in self.pricing_data.columns:
                    platform_prices = self.pricing_data[platform_col].dropna()
                    
                    if len(platform_prices) > 0:
                        summary['platform_stats'][platform] = {
                            'avg_price': float(platform_prices.mean()),
                            'min_price': float(platform_prices.min()),
                            'max_price': float(platform_prices.max()),
                            'total_listings': len(platform_prices)
                        }
            
            return summary
            
        except Exception as e:
            app_logger.error(f"Platform summary failed: {str(e)}")
            return {}
    
    def get_best_deals(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get products with the highest savings potential."""
        try:
            if self.pricing_data is None:
                return []
            
            deals = []
            products = self.pricing_data['product_id'].unique()
            
            for product_id in products[:limit]:  # Limit for performance
                comparison = self.compare_prices(product_id)
                if comparison and comparison.savings_amount > 0:
                    deals.append({
                        'product_id': comparison.product_id,
                        'product_name': comparison.product_name,
                        'savings_amount': comparison.savings_amount,
                        'savings_percentage': comparison.price_difference_percentage,
                        'lowest_platform': comparison.lowest_platform,
                        'lowest_price': comparison.lowest_price,
                        'highest_price': comparison.highest_price
                    })
            
            # Sort by savings amount (descending)
            deals.sort(key=lambda x: x['savings_amount'], reverse=True)
            return deals[:limit]
            
        except Exception as e:
            app_logger.error(f"Best deals calculation failed: {str(e)}")
            return []


def compare_prices(product_id: str) -> Optional[Dict[str, Any]]:
    """Standalone function for price comparison."""
    engine = CompetitivePricingEngine()
    result = engine.compare_prices(product_id)
    return result.to_dict() if result else None


# Integration with Market Copilot
class CompetitivePricingCopilot:
    """Integration class for competitive pricing with Market Copilot."""
    
    def __init__(self, pricing_engine: CompetitivePricingEngine):
        """Initialize with pricing engine."""
        self.pricing_engine = pricing_engine
    
    def process_pricing_query(self, query: str) -> str:
        """Process pricing-related queries."""
        query_lower = query.lower()
        
        try:
            # Extract product name or ID from query
            if 'compare' in query_lower or 'price' in query_lower:
                # Simple keyword extraction
                words = query.split()
                
                # Look for product names in the query
                products = self.pricing_engine.get_product_list()
                
                for product in products:
                    product_name = product['product_name'].lower()
                    if any(word in product_name for word in words):
                        # Found a matching product
                        comparison = self.pricing_engine.compare_prices(product['product_id'])
                        
                        if comparison:
                            return self._format_comparison_response(comparison)
                
                # If no specific product found, return general guidance
                return "I can help you compare prices! Please specify a product name. Available products include: " + \
                       ", ".join([p['product_name'] for p in products[:5]])
            
            elif 'best deal' in query_lower or 'cheapest' in query_lower:
                deals = self.pricing_engine.get_best_deals(5)
                if deals:
                    response = "Here are the best deals I found:\n"
                    for i, deal in enumerate(deals, 1):
                        response += f"{i}. {deal['product_name']}: Save ₹{deal['savings_amount']:.2f} " \
                                  f"by buying from {deal['lowest_platform']} (₹{deal['lowest_price']:.2f})\n"
                    return response
                else:
                    return "No deals data available at the moment."
            
            else:
                return "I can help you compare prices across platforms. Try asking: 'Compare prices for [product name]' or 'Show me best deals'"
                
        except Exception as e:
            return f"Sorry, I encountered an error while processing your pricing query: {str(e)}"
    
    def _format_comparison_response(self, comparison: PriceComparison) -> str:
        """Format price comparison into readable response."""
        response = f"Price comparison for {comparison.product_name}:\n\n"
        
        # Current prices
        response += "Current Prices:\n"
        for platform, price in comparison.current_prices.items():
            marker = " 🏆" if platform == comparison.lowest_platform else ""
            marker += " 💸" if platform == comparison.highest_platform else ""
            response += f"• {platform}: ₹{price:.2f}{marker}\n"
        
        response += f"\n{comparison.recommendation}\n"
        
        # Trends
        if comparison.trend_7_days:
            response += "\n7-day trends:\n"
            for platform, trend in comparison.trend_7_days.items():
                trend_icon = "📈" if trend > 0 else "📉" if trend < 0 else "➡️"
                response += f"• {platform}: {trend:+.1f}% {trend_icon}\n"
        
        return response