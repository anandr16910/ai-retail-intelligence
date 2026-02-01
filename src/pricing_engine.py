"""Pricing intelligence engine for AI Retail Intelligence Platform."""

import math
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass
from enum import Enum

try:
    import pandas as pd
    import numpy as np
    PANDAS_AVAILABLE = True
except ImportError:
    PANDAS_AVAILABLE = False

from src.exceptions import PricingEngineError
from src.config import settings


class MarketCondition(Enum):
    """Market condition classifications."""
    BULLISH = "bullish"
    BEARISH = "bearish"
    SIDEWAYS = "sideways"
    VOLATILE = "volatile"


@dataclass
class PricingRecommendation:
    """Data model for pricing recommendations."""
    symbol: str
    current_price: float
    recommended_price: float
    confidence_score: float
    market_conditions: Dict[str, Any]
    reasoning: str
    timestamp: datetime
    
    def get_price_change_percentage(self) -> float:
        """Calculate price change percentage."""
        if self.current_price == 0:
            return 0.0
        return ((self.recommended_price - self.current_price) / self.current_price) * 100
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            'symbol': self.symbol,
            'current_price': self.current_price,
            'recommended_price': self.recommended_price,
            'confidence_score': self.confidence_score,
            'market_conditions': self.market_conditions,
            'reasoning': self.reasoning,
            'price_change_percentage': self.get_price_change_percentage(),
            'timestamp': self.timestamp.isoformat()
        }


class MarketAnalyzer:
    """Analyze market conditions and trends."""
    
    @staticmethod
    def calculate_volatility(prices: List[float], window: int = 30) -> float:
        """Calculate price volatility using standard deviation."""
        try:
            if len(prices) < 2:
                return 0.0
            
            # Use last 'window' prices or all available prices
            recent_prices = prices[-min(window, len(prices)):]
            
            if len(recent_prices) < 2:
                return 0.0
            
            # Calculate returns
            returns = []
            for i in range(1, len(recent_prices)):
                if recent_prices[i-1] != 0:
                    ret = (recent_prices[i] - recent_prices[i-1]) / recent_prices[i-1]
                    returns.append(ret)
            
            if not returns:
                return 0.0
            
            # Calculate standard deviation
            mean_return = sum(returns) / len(returns)
            variance = sum((r - mean_return) ** 2 for r in returns) / len(returns)
            volatility = math.sqrt(variance)
            
            return volatility
            
        except Exception as e:
            return 0.0
    
    @staticmethod
    def detect_trend(prices: List[float], window: int = 20) -> Tuple[str, float]:
        """Detect price trend direction and strength."""
        try:
            if len(prices) < window:
                return "sideways", 0.0
            
            recent_prices = prices[-window:]
            
            # Simple linear trend calculation
            x_values = list(range(len(recent_prices)))
            n = len(recent_prices)
            
            # Calculate slope using least squares
            sum_x = sum(x_values)
            sum_y = sum(recent_prices)
            sum_xy = sum(x * y for x, y in zip(x_values, recent_prices))
            sum_x2 = sum(x * x for x in x_values)
            
            if n * sum_x2 - sum_x * sum_x == 0:
                return "sideways", 0.0
            
            slope = (n * sum_xy - sum_x * sum_y) / (n * sum_x2 - sum_x * sum_x)
            
            # Normalize slope by average price
            avg_price = sum_y / n
            normalized_slope = slope / avg_price if avg_price != 0 else 0
            
            # Determine trend
            if normalized_slope > 0.001:  # 0.1% per period
                return "upward", abs(normalized_slope)
            elif normalized_slope < -0.001:
                return "downward", abs(normalized_slope)
            else:
                return "sideways", abs(normalized_slope)
                
        except Exception as e:
            return "sideways", 0.0
    
    @staticmethod
    def calculate_support_resistance(prices: List[float], window: int = 20) -> Tuple[float, float]:
        """Calculate support and resistance levels."""
        try:
            if len(prices) < window:
                return min(prices), max(prices)
            
            recent_prices = prices[-window:]
            
            # Simple approach: use recent min/max as support/resistance
            support = min(recent_prices)
            resistance = max(recent_prices)
            
            return support, resistance
            
        except Exception as e:
            return 0.0, 0.0
    
    @staticmethod
    def analyze_market_condition(prices: List[float]) -> MarketCondition:
        """Analyze overall market condition."""
        try:
            if len(prices) < 10:
                return MarketCondition.SIDEWAYS
            
            # Calculate volatility
            volatility = MarketAnalyzer.calculate_volatility(prices)
            
            # Calculate trend
            trend, trend_strength = MarketAnalyzer.detect_trend(prices)
            
            # Determine market condition
            if volatility > 0.03:  # High volatility threshold
                return MarketCondition.VOLATILE
            elif trend == "upward" and trend_strength > 0.002:
                return MarketCondition.BULLISH
            elif trend == "downward" and trend_strength > 0.002:
                return MarketCondition.BEARISH
            else:
                return MarketCondition.SIDEWAYS
                
        except Exception as e:
            return MarketCondition.SIDEWAYS


class PricingStrategy:
    """Different pricing strategies for various market scenarios."""
    
    @staticmethod
    def conservative_strategy(current_price: float, market_analysis: Dict[str, Any]) -> Tuple[float, str]:
        """Conservative pricing strategy with minimal risk."""
        try:
            volatility = market_analysis.get('volatility', 0.02)
            trend = market_analysis.get('trend', 'sideways')
            
            # Conservative adjustment based on trend
            if trend == 'upward':
                adjustment = min(0.02, volatility)  # Max 2% increase
            elif trend == 'downward':
                adjustment = -min(0.02, volatility)  # Max 2% decrease
            else:
                adjustment = 0.0  # No change for sideways
            
            recommended_price = current_price * (1 + adjustment)
            reasoning = f"Conservative strategy: {adjustment*100:.1f}% adjustment based on {trend} trend"
            
            return recommended_price, reasoning
            
        except Exception as e:
            return current_price, "Conservative strategy: No change due to analysis error"
    
    @staticmethod
    def aggressive_strategy(current_price: float, market_analysis: Dict[str, Any]) -> Tuple[float, str]:
        """Aggressive pricing strategy for higher returns."""
        try:
            volatility = market_analysis.get('volatility', 0.02)
            trend = market_analysis.get('trend', 'sideways')
            trend_strength = market_analysis.get('trend_strength', 0.0)
            
            # Aggressive adjustment based on trend and volatility
            base_adjustment = trend_strength * 2  # Amplify trend strength
            
            if trend == 'upward':
                adjustment = min(0.05, base_adjustment + volatility)  # Max 5% increase
            elif trend == 'downward':
                adjustment = -min(0.05, base_adjustment + volatility)  # Max 5% decrease
            else:
                adjustment = volatility * 0.5  # Small positive adjustment for sideways
            
            recommended_price = current_price * (1 + adjustment)
            reasoning = f"Aggressive strategy: {adjustment*100:.1f}% adjustment based on {trend} trend and volatility"
            
            return recommended_price, reasoning
            
        except Exception as e:
            return current_price, "Aggressive strategy: No change due to analysis error"
    
    @staticmethod
    def balanced_strategy(current_price: float, market_analysis: Dict[str, Any]) -> Tuple[float, str]:
        """Balanced pricing strategy combining conservative and aggressive approaches."""
        try:
            # Get both strategies
            conservative_price, _ = PricingStrategy.conservative_strategy(current_price, market_analysis)
            aggressive_price, _ = PricingStrategy.aggressive_strategy(current_price, market_analysis)
            
            # Take weighted average (70% conservative, 30% aggressive)
            recommended_price = (conservative_price * 0.7) + (aggressive_price * 0.3)
            
            change_pct = ((recommended_price - current_price) / current_price) * 100
            reasoning = f"Balanced strategy: {change_pct:.1f}% adjustment (70% conservative, 30% aggressive)"
            
            return recommended_price, reasoning
            
        except Exception as e:
            return current_price, "Balanced strategy: No change due to analysis error"


class PricingEngine:
    """Main pricing optimization engine."""
    
    def __init__(self):
        """Initialize pricing engine."""
        self.analyzer = MarketAnalyzer()
        self.strategy = PricingStrategy()
        self.price_history = {}  # Store price history for analysis
    
    def analyze_market_conditions(self, price_data: List[Dict[str, Any]], symbol: str = "UNKNOWN") -> Dict[str, Any]:
        """Analyze current market conditions for given price data."""
        try:
            if not price_data:
                raise PricingEngineError("No price data provided for analysis")
            
            # Extract prices
            prices = []
            dates = []
            
            for record in price_data:
                if 'close' in record:
                    prices.append(float(record['close']))
                elif 'price' in record:
                    prices.append(float(record['price']))
                else:
                    continue
                
                if 'date' in record:
                    dates.append(record['date'])
            
            if not prices:
                raise PricingEngineError("No valid price data found")
            
            # Store price history
            self.price_history[symbol] = prices
            
            # Perform analysis
            volatility = self.analyzer.calculate_volatility(prices)
            trend, trend_strength = self.analyzer.detect_trend(prices)
            support, resistance = self.analyzer.calculate_support_resistance(prices)
            market_condition = self.analyzer.analyze_market_condition(prices)
            
            # Calculate additional metrics
            current_price = prices[-1]
            price_range = max(prices) - min(prices)
            avg_price = sum(prices) / len(prices)
            
            # Price momentum (recent vs older prices)
            if len(prices) >= 10:
                recent_avg = sum(prices[-5:]) / 5
                older_avg = sum(prices[-10:-5]) / 5
                momentum = (recent_avg - older_avg) / older_avg if older_avg != 0 else 0
            else:
                momentum = 0
            
            analysis = {
                'symbol': symbol,
                'current_price': current_price,
                'volatility': volatility,
                'trend': trend,
                'trend_strength': trend_strength,
                'support_level': support,
                'resistance_level': resistance,
                'market_condition': market_condition.value,
                'price_range': price_range,
                'average_price': avg_price,
                'momentum': momentum,
                'analysis_timestamp': datetime.now().isoformat(),
                'data_points': len(prices)
            }
            
            return analysis
            
        except Exception as e:
            raise PricingEngineError(f"Market analysis failed: {str(e)}")
    
    def recommend_pricing(self, current_price: float, forecast: Dict[str, Any] = None, 
                         strategy_type: str = "balanced", symbol: str = "UNKNOWN") -> PricingRecommendation:
        """Generate pricing recommendations based on market analysis."""
        try:
            # Get market analysis
            if symbol in self.price_history:
                # Use stored price history for analysis
                price_data = [{'close': p} for p in self.price_history[symbol]]
                market_analysis = self.analyze_market_conditions(price_data, symbol)
            else:
                # Create minimal analysis with current price
                market_analysis = {
                    'current_price': current_price,
                    'volatility': 0.02,
                    'trend': 'sideways',
                    'trend_strength': 0.0,
                    'market_condition': 'sideways'
                }
            
            # Incorporate forecast if available
            if forecast and 'predicted_prices' in forecast:
                predicted_prices = forecast['predicted_prices']
                if predicted_prices:
                    # Adjust analysis based on forecast
                    forecast_trend = "upward" if predicted_prices[-1] > current_price else "downward"
                    forecast_strength = abs(predicted_prices[-1] - current_price) / current_price
                    
                    # Blend current analysis with forecast
                    market_analysis['trend'] = forecast_trend
                    market_analysis['trend_strength'] = max(market_analysis.get('trend_strength', 0), forecast_strength)
            
            # Apply pricing strategy
            if strategy_type == "conservative":
                recommended_price, reasoning = self.strategy.conservative_strategy(current_price, market_analysis)
                confidence = 0.8
            elif strategy_type == "aggressive":
                recommended_price, reasoning = self.strategy.aggressive_strategy(current_price, market_analysis)
                confidence = 0.6
            else:  # balanced
                recommended_price, reasoning = self.strategy.balanced_strategy(current_price, market_analysis)
                confidence = 0.7
            
            # Adjust confidence based on data quality
            data_points = market_analysis.get('data_points', 0)
            if data_points < 10:
                confidence *= 0.7
            elif data_points < 30:
                confidence *= 0.85
            
            # Create recommendation
            recommendation = PricingRecommendation(
                symbol=symbol,
                current_price=current_price,
                recommended_price=recommended_price,
                confidence_score=confidence,
                market_conditions=market_analysis,
                reasoning=reasoning,
                timestamp=datetime.now()
            )
            
            return recommendation
            
        except Exception as e:
            raise PricingEngineError(f"Pricing recommendation failed: {str(e)}")
    
    def calculate_volatility(self, price_data: List[float]) -> float:
        """Calculate price volatility."""
        return self.analyzer.calculate_volatility(price_data)
    
    def generate_pricing_report(self, symbols: List[str] = None, 
                              strategy_type: str = "balanced") -> Dict[str, Any]:
        """Generate comprehensive pricing report."""
        try:
            symbols = symbols or list(self.price_history.keys())
            
            if not symbols:
                return {
                    'report_timestamp': datetime.now().isoformat(),
                    'symbols_analyzed': 0,
                    'recommendations': [],
                    'summary': 'No symbols available for analysis'
                }
            
            recommendations = []
            total_symbols = 0
            
            for symbol in symbols:
                try:
                    if symbol in self.price_history:
                        current_price = self.price_history[symbol][-1]
                        recommendation = self.recommend_pricing(
                            current_price=current_price,
                            strategy_type=strategy_type,
                            symbol=symbol
                        )
                        recommendations.append(recommendation.to_dict())
                        total_symbols += 1
                except Exception as e:
                    continue
            
            # Generate summary statistics
            if recommendations:
                avg_confidence = sum(r['confidence_score'] for r in recommendations) / len(recommendations)
                price_changes = [r['price_change_percentage'] for r in recommendations]
                avg_price_change = sum(price_changes) / len(price_changes)
                
                summary = f"Analyzed {total_symbols} symbols with average confidence {avg_confidence:.2f} and average price change {avg_price_change:.2f}%"
            else:
                summary = "No valid recommendations generated"
            
            report = {
                'report_timestamp': datetime.now().isoformat(),
                'strategy_type': strategy_type,
                'symbols_analyzed': total_symbols,
                'recommendations': recommendations,
                'summary_statistics': {
                    'average_confidence': avg_confidence if recommendations else 0,
                    'average_price_change': avg_price_change if recommendations else 0,
                    'total_recommendations': len(recommendations)
                },
                'summary': summary
            }
            
            return report
            
        except Exception as e:
            raise PricingEngineError(f"Report generation failed: {str(e)}")
    
    def analyze_cross_asset_correlation(self, asset1_prices: List[float], 
                                      asset2_prices: List[float]) -> float:
        """Analyze correlation between two assets."""
        try:
            if len(asset1_prices) != len(asset2_prices) or len(asset1_prices) < 2:
                return 0.0
            
            # Calculate returns
            returns1 = []
            returns2 = []
            
            for i in range(1, len(asset1_prices)):
                if asset1_prices[i-1] != 0 and asset2_prices[i-1] != 0:
                    ret1 = (asset1_prices[i] - asset1_prices[i-1]) / asset1_prices[i-1]
                    ret2 = (asset2_prices[i] - asset2_prices[i-1]) / asset2_prices[i-1]
                    returns1.append(ret1)
                    returns2.append(ret2)
            
            if len(returns1) < 2:
                return 0.0
            
            # Calculate correlation coefficient
            n = len(returns1)
            sum1 = sum(returns1)
            sum2 = sum(returns2)
            sum1_sq = sum(r * r for r in returns1)
            sum2_sq = sum(r * r for r in returns2)
            sum_prod = sum(r1 * r2 for r1, r2 in zip(returns1, returns2))
            
            numerator = n * sum_prod - sum1 * sum2
            denominator = math.sqrt((n * sum1_sq - sum1 * sum1) * (n * sum2_sq - sum2 * sum2))
            
            if denominator == 0:
                return 0.0
            
            correlation = numerator / denominator
            return correlation
            
        except Exception as e:
            return 0.0
    
    def get_pricing_insights(self, symbol: str) -> Dict[str, Any]:
        """Get detailed pricing insights for a symbol."""
        try:
            if symbol not in self.price_history:
                return {'error': f'No price history available for {symbol}'}
            
            prices = self.price_history[symbol]
            current_price = prices[-1]
            
            # Analyze market conditions
            price_data = [{'close': p} for p in prices]
            market_analysis = self.analyze_market_conditions(price_data, symbol)
            
            # Generate recommendations for different strategies
            conservative_rec = self.recommend_pricing(current_price, strategy_type="conservative", symbol=symbol)
            balanced_rec = self.recommend_pricing(current_price, strategy_type="balanced", symbol=symbol)
            aggressive_rec = self.recommend_pricing(current_price, strategy_type="aggressive", symbol=symbol)
            
            insights = {
                'symbol': symbol,
                'current_price': current_price,
                'market_analysis': market_analysis,
                'recommendations': {
                    'conservative': conservative_rec.to_dict(),
                    'balanced': balanced_rec.to_dict(),
                    'aggressive': aggressive_rec.to_dict()
                },
                'insights_timestamp': datetime.now().isoformat()
            }
            
            return insights
            
        except Exception as e:
            return {'error': f'Failed to generate insights: {str(e)}'}
    
    def update_price_history(self, symbol: str, prices: List[float]):
        """Update price history for a symbol."""
        self.price_history[symbol] = prices
    
    def get_available_symbols(self) -> List[str]:
        """Get list of symbols with available price history."""
        return list(self.price_history.keys())