"""Market Copilot AI assistant for financial Q&A over market data."""

import re
import json
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass
from enum import Enum

from src.exceptions import LLMServiceError
from src.config import settings


class QueryType(Enum):
    """Types of queries the copilot can handle."""
    PRICE_INQUIRY = "price_inquiry"
    TREND_ANALYSIS = "trend_analysis"
    FORECAST_REQUEST = "forecast_request"
    COMPARISON = "comparison"
    MARKET_CONDITION = "market_condition"
    GENERAL_INFO = "general_info"
    UNKNOWN = "unknown"


@dataclass
class MarketQuery:
    """Data model for market queries."""
    query_id: str
    user_query: str
    processed_query: str
    response: str
    context_data: Dict[str, Any]
    confidence_score: float
    timestamp: datetime
    query_type: str = QueryType.UNKNOWN.value
    
    def is_high_confidence(self) -> bool:
        """Check if response has high confidence."""
        return self.confidence_score > 0.8
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            'query_id': self.query_id,
            'user_query': self.user_query,
            'processed_query': self.processed_query,
            'response': self.response,
            'context_data': self.context_data,
            'confidence_score': self.confidence_score,
            'query_type': self.query_type,
            'timestamp': self.timestamp.isoformat(),
            'high_confidence': self.is_high_confidence()
        }


class QueryProcessor:
    """Process and understand natural language queries about financial data."""
    
    def __init__(self):
        """Initialize query processor."""
        self.query_patterns = {
            QueryType.PRICE_INQUIRY: [
                r'(?:what|how much|price|cost|value).*(?:gold|silver|etf)',
                r'(?:current|latest|today).*(?:price|value)',
                r'(?:gold|silver|etf).*(?:price|cost|value)'
            ],
            QueryType.TREND_ANALYSIS: [
                r'(?:trend|direction|movement|going up|going down)',
                r'(?:bullish|bearish|rising|falling|increasing|decreasing)',
                r'(?:performance|how.*doing)'
            ],
            QueryType.FORECAST_REQUEST: [
                r'(?:predict|forecast|future|tomorrow|next|will)',
                r'(?:expect|projection|outlook)',
                r'(?:where.*heading|what.*happen)'
            ],
            QueryType.COMPARISON: [
                r'(?:compare|versus|vs|better|worse)',
                r'(?:difference|between)',
                r'(?:gold.*silver|silver.*gold)'
            ],
            QueryType.MARKET_CONDITION: [
                r'(?:market|condition|sentiment|mood)',
                r'(?:volatile|stability|risk)',
                r'(?:bull|bear).*market'
            ]
        }
        
        self.entity_patterns = {
            'assets': r'\b(?:gold|silver|etf|nifty|bank|junior)\w*\b',
            'timeframes': r'\b(?:today|yesterday|week|month|year|daily|weekly|monthly)\b',
            'metrics': r'\b(?:price|volume|volatility|trend|return|profit|loss)\b',
            'numbers': r'\b\d+(?:\.\d+)?(?:%|\$|₹)?\b'
        }
    
    def classify_query(self, query: str) -> Tuple[QueryType, float]:
        """Classify the type of query."""
        query_lower = query.lower()
        scores = {}
        
        for query_type, patterns in self.query_patterns.items():
            score = 0
            for pattern in patterns:
                matches = len(re.findall(pattern, query_lower))
                score += matches
            scores[query_type] = score
        
        if not scores or max(scores.values()) == 0:
            return QueryType.UNKNOWN, 0.5
        
        best_type = max(scores, key=scores.get)
        confidence = min(0.95, scores[best_type] / 3)  # Normalize confidence
        
        return best_type, confidence
    
    def extract_entities(self, query: str) -> Dict[str, List[str]]:
        """Extract entities from the query."""
        entities = {}
        query_lower = query.lower()
        
        for entity_type, pattern in self.entity_patterns.items():
            matches = re.findall(pattern, query_lower)
            if matches:
                entities[entity_type] = list(set(matches))  # Remove duplicates
        
        return entities
    
    def process_query(self, query: str) -> Dict[str, Any]:
        """Process and analyze the user query."""
        query_type, confidence = self.classify_query(query)
        entities = self.extract_entities(query)
        
        # Create processed query summary
        processed_query = f"Query type: {query_type.value}, Entities: {entities}"
        
        return {
            'original_query': query,
            'processed_query': processed_query,
            'query_type': query_type.value,
            'classification_confidence': confidence,
            'extracted_entities': entities,
            'processing_timestamp': datetime.now().isoformat()
        }


class ResponseGenerator:
    """Generate contextually appropriate responses to market queries."""
    
    def __init__(self):
        """Initialize response generator."""
        self.response_templates = {
            QueryType.PRICE_INQUIRY: [
                "Based on the latest data, {asset} is currently priced at ${price:.2f}.",
                "The current {asset} price is ${price:.2f}, {trend_description}.",
                "{asset} is trading at ${price:.2f} as of {timestamp}."
            ],
            QueryType.TREND_ANALYSIS: [
                "{asset} shows a {trend} trend with {strength} momentum.",
                "The {timeframe} trend for {asset} is {trend}, indicating {interpretation}.",
                "Market analysis suggests {asset} is experiencing {trend} movement."
            ],
            QueryType.FORECAST_REQUEST: [
                "Based on current patterns, {asset} is expected to {forecast_direction} in the {timeframe}.",
                "Our forecasting model predicts {asset} will {forecast_description}.",
                "The outlook for {asset} suggests {forecast_summary}."
            ],
            QueryType.COMPARISON: [
                "Comparing {asset1} and {asset2}: {comparison_summary}.",
                "{asset1} vs {asset2}: {performance_comparison}.",
                "Between {asset1} and {asset2}, {recommendation}."
            ],
            QueryType.MARKET_CONDITION: [
                "Current market conditions show {condition} sentiment with {volatility} volatility.",
                "The market is experiencing {condition} conditions, characterized by {description}.",
                "Market analysis indicates {condition} sentiment across {sectors}."
            ]
        }
        
        self.fallback_responses = [
            "I understand you're asking about market data. Could you be more specific about which asset or timeframe you're interested in?",
            "That's an interesting question about the market. Let me provide some general insights based on available data.",
            "I can help with market analysis. Could you clarify what specific information you're looking for?"
        ]
    
    def generate_response(self, query_info: Dict[str, Any], context_data: Dict[str, Any]) -> Tuple[str, float]:
        """Generate a response based on query analysis and context."""
        query_type = QueryType(query_info.get('query_type', QueryType.UNKNOWN.value))
        entities = query_info.get('extracted_entities', {})
        
        try:
            if query_type == QueryType.PRICE_INQUIRY:
                return self._generate_price_response(entities, context_data)
            elif query_type == QueryType.TREND_ANALYSIS:
                return self._generate_trend_response(entities, context_data)
            elif query_type == QueryType.FORECAST_REQUEST:
                return self._generate_forecast_response(entities, context_data)
            elif query_type == QueryType.COMPARISON:
                return self._generate_comparison_response(entities, context_data)
            elif query_type == QueryType.MARKET_CONDITION:
                return self._generate_market_condition_response(entities, context_data)
            else:
                return self._generate_fallback_response(query_info, context_data)
                
        except Exception as e:
            return f"I apologize, but I encountered an issue processing your query: {str(e)}", 0.3
    
    def _generate_price_response(self, entities: Dict, context_data: Dict) -> Tuple[str, float]:
        """Generate response for price inquiries."""
        assets = entities.get('assets', ['gold'])  # Default to gold
        asset = assets[0] if assets else 'gold'
        
        # Get price data from context
        price_data = context_data.get('price_data', {})
        
        if asset in price_data:
            current_price = price_data[asset].get('current_price', 0)
            trend = price_data[asset].get('trend', 'stable')
            
            trend_descriptions = {
                'upward': 'showing upward momentum',
                'downward': 'experiencing downward pressure',
                'stable': 'remaining relatively stable'
            }
            
            response = f"Based on the latest data, {asset} is currently priced at ${current_price:.2f}, {trend_descriptions.get(trend, 'with mixed signals')}."
            confidence = 0.8
        else:
            response = f"I don't have current pricing data for {asset}. Please check back later or ask about gold, silver, or ETF prices."
            confidence = 0.4
        
        return response, confidence
    
    def _generate_trend_response(self, entities: Dict, context_data: Dict) -> Tuple[str, float]:
        """Generate response for trend analysis."""
        assets = entities.get('assets', ['market'])
        asset = assets[0] if assets else 'market'
        
        market_data = context_data.get('market_analysis', {})
        
        if asset in market_data or 'overall' in market_data:
            data = market_data.get(asset, market_data.get('overall', {}))
            trend = data.get('trend', 'sideways')
            volatility = data.get('volatility', 'moderate')
            
            trend_interpretations = {
                'upward': 'bullish sentiment and positive momentum',
                'downward': 'bearish sentiment and negative momentum',
                'sideways': 'consolidation and mixed signals'
            }
            
            response = f"{asset.title()} shows a {trend} trend with {volatility} volatility, indicating {trend_interpretations.get(trend, 'uncertain market conditions')}."
            confidence = 0.7
        else:
            response = f"Based on general market patterns, {asset} appears to be following broader market trends. For more specific analysis, I'd need recent price data."
            confidence = 0.5
        
        return response, confidence
    
    def _generate_forecast_response(self, entities: Dict, context_data: Dict) -> Tuple[str, float]:
        """Generate response for forecast requests."""
        assets = entities.get('assets', ['market'])
        timeframes = entities.get('timeframes', ['short-term'])
        
        asset = assets[0] if assets else 'market'
        timeframe = timeframes[0] if timeframes else 'short-term'
        
        forecast_data = context_data.get('forecasts', {})
        
        if asset in forecast_data:
            forecast = forecast_data[asset]
            direction = forecast.get('direction', 'stable')
            confidence_level = forecast.get('confidence', 0.6)
            
            direction_descriptions = {
                'up': 'trend upward',
                'down': 'decline',
                'stable': 'remain relatively stable'
            }
            
            response = f"Based on current patterns and our forecasting models, {asset} is expected to {direction_descriptions.get(direction, 'show mixed movement')} in the {timeframe}."
            confidence = confidence_level
        else:
            response = f"While I don't have specific forecast data for {asset}, general market indicators suggest cautious optimism for the {timeframe}."
            confidence = 0.4
        
        return response, confidence
    
    def _generate_comparison_response(self, entities: Dict, context_data: Dict) -> Tuple[str, float]:
        """Generate response for comparison queries."""
        assets = entities.get('assets', [])
        
        if len(assets) >= 2:
            asset1, asset2 = assets[0], assets[1]
            
            price_data = context_data.get('price_data', {})
            
            if asset1 in price_data and asset2 in price_data:
                price1 = price_data[asset1].get('current_price', 0)
                price2 = price_data[asset2].get('current_price', 0)
                trend1 = price_data[asset1].get('trend', 'stable')
                trend2 = price_data[asset2].get('trend', 'stable')
                
                performance = "outperforming" if price1 > price2 else "underperforming"
                
                response = f"Comparing {asset1} and {asset2}: {asset1} (${price1:.2f}, {trend1}) is currently {performance} {asset2} (${price2:.2f}, {trend2})."
                confidence = 0.7
            else:
                response = f"I'd need current data for both {asset1} and {asset2} to provide an accurate comparison."
                confidence = 0.3
        else:
            response = "For comparisons, please specify which assets you'd like me to compare (e.g., gold vs silver)."
            confidence = 0.4
        
        return response, confidence
    
    def _generate_market_condition_response(self, entities: Dict, context_data: Dict) -> Tuple[str, float]:
        """Generate response for market condition queries."""
        market_data = context_data.get('market_analysis', {})
        
        if 'overall' in market_data:
            condition = market_data['overall'].get('condition', 'mixed')
            volatility = market_data['overall'].get('volatility', 'moderate')
            
            condition_descriptions = {
                'bullish': 'optimistic with strong buying interest',
                'bearish': 'pessimistic with selling pressure',
                'mixed': 'showing mixed signals with uncertainty'
            }
            
            response = f"Current market conditions show {condition} sentiment with {volatility} volatility, characterized by {condition_descriptions.get(condition, 'varied investor sentiment')}."
            confidence = 0.6
        else:
            response = "Market conditions appear to be in a state of transition. I'd recommend monitoring key indicators for clearer signals."
            confidence = 0.4
        
        return response, confidence
    
    def _generate_fallback_response(self, query_info: Dict, context_data: Dict) -> Tuple[str, float]:
        """Generate fallback response for unclear queries."""
        import random
        response = random.choice(self.fallback_responses)
        
        # Try to add some context if available
        if context_data.get('price_data'):
            available_assets = list(context_data['price_data'].keys())
            if available_assets:
                response += f" I have data available for: {', '.join(available_assets)}."
        
        return response, 0.3


class MarketCopilot:
    """Main conversational AI engine for market queries."""
    
    def __init__(self, competitive_pricing_copilot=None):
        """Initialize market copilot."""
        self.query_processor = QueryProcessor()
        self.response_generator = ResponseGenerator()
        self.conversation_history = []
        self.context_data = {}
        self.session_id = None
        self.competitive_pricing_copilot = competitive_pricing_copilot
        
    def process_query(self, query: str, context: Dict[str, Any] = None) -> str:
        """Process a user query and return a response."""
        try:
            # Check if this is a competitive pricing query
            if self.competitive_pricing_copilot and self._is_pricing_query(query):
                return self.competitive_pricing_copilot.process_pricing_query(query)
            
            # Generate unique query ID
            query_id = f"q_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{len(self.conversation_history)}"
            
            # Update context if provided
            if context:
                self.context_data.update(context)
            
            # Process the query
            query_info = self.query_processor.process_query(query)
            
            # Generate response
            response, confidence = self.response_generator.generate_response(query_info, self.context_data)
            
            # Create query record
            market_query = MarketQuery(
                query_id=query_id,
                user_query=query,
                processed_query=query_info['processed_query'],
                response=response,
                context_data=self.context_data.copy(),
                confidence_score=confidence,
                timestamp=datetime.now(),
                query_type=query_info['query_type']
            )
            
            # Add to conversation history
            self.conversation_history.append(market_query)
            
            # Maintain conversation history (keep last 10 exchanges)
            if len(self.conversation_history) > 10:
                self.conversation_history = self.conversation_history[-10:]
            
            return response
            
        except Exception as e:
            error_response = f"I apologize, but I encountered an error processing your query: {str(e)}"
            return error_response
    
    def _is_pricing_query(self, query: str) -> bool:
        """Check if query is related to competitive pricing."""
        pricing_keywords = [
            'compare prices', 'price comparison', 'cheapest', 'best deal', 
            'lowest price', 'highest price', 'save money', 'amazon', 
            'flipkart', 'jiomart', 'blinkit', 'zepto', 'dmart'
        ]
        
        query_lower = query.lower()
        return any(keyword in query_lower for keyword in pricing_keywords)
    
    def update_context(self, new_data: Dict[str, Any]) -> None:
        """Update the context data with new information."""
        self.context_data.update(new_data)
    
    def get_financial_insights(self, query: str) -> Dict[str, Any]:
        """Get detailed financial insights for a query."""
        try:
            query_info = self.query_processor.process_query(query)
            response, confidence = self.response_generator.generate_response(query_info, self.context_data)
            
            insights = {
                'query_analysis': query_info,
                'response': response,
                'confidence': confidence,
                'relevant_data': {},
                'recommendations': []
            }
            
            # Add relevant data based on query type
            query_type = query_info.get('query_type')
            entities = query_info.get('extracted_entities', {})
            
            if query_type == 'price_inquiry' and 'assets' in entities:
                for asset in entities['assets']:
                    if asset in self.context_data.get('price_data', {}):
                        insights['relevant_data'][asset] = self.context_data['price_data'][asset]
            
            # Generate recommendations
            if confidence > 0.7:
                insights['recommendations'].append("High confidence response - information is reliable")
            elif confidence > 0.5:
                insights['recommendations'].append("Moderate confidence - consider additional data sources")
            else:
                insights['recommendations'].append("Low confidence - recommend seeking more specific information")
            
            return insights
            
        except Exception as e:
            return {'error': f'Failed to generate insights: {str(e)}'}
    
    def maintain_conversation_history(self, query: str, response: str) -> None:
        """Maintain conversation history (called automatically by process_query)."""
        # This method is for external calls if needed
        pass
    
    def get_conversation_history(self) -> List[Dict[str, Any]]:
        """Get the conversation history."""
        return [query.to_dict() for query in self.conversation_history]
    
    def clear_conversation_history(self) -> None:
        """Clear the conversation history."""
        self.conversation_history = []
    
    def get_context_summary(self) -> Dict[str, Any]:
        """Get a summary of the current context."""
        summary = {
            'available_data_types': list(self.context_data.keys()),
            'conversation_length': len(self.conversation_history),
            'last_query_time': self.conversation_history[-1].timestamp.isoformat() if self.conversation_history else None,
            'context_size': len(str(self.context_data))
        }
        
        # Add data summaries
        if 'price_data' in self.context_data:
            summary['available_assets'] = list(self.context_data['price_data'].keys())
        
        if 'market_analysis' in self.context_data:
            summary['market_analysis_available'] = True
        
        if 'forecasts' in self.context_data:
            summary['forecasts_available'] = list(self.context_data['forecasts'].keys())
        
        return summary
    
    def suggest_queries(self) -> List[str]:
        """Suggest relevant queries based on available data."""
        suggestions = []
        
        if 'price_data' in self.context_data:
            assets = list(self.context_data['price_data'].keys())
            if assets:
                suggestions.extend([
                    f"What is the current price of {assets[0]}?",
                    f"How is {assets[0]} trending?",
                    f"Compare {assets[0]} and {assets[1] if len(assets) > 1 else 'silver'}"
                ])
        
        if 'forecasts' in self.context_data:
            suggestions.append("What are the price forecasts for next week?")
        
        if 'market_analysis' in self.context_data:
            suggestions.append("What are the current market conditions?")
        
        # Default suggestions
        if not suggestions:
            suggestions = [
                "What is the current gold price?",
                "How is the market trending?",
                "What are the forecasts for precious metals?",
                "Compare gold and silver performance"
            ]
        
        return suggestions[:5]  # Return top 5 suggestions
    
    def get_copilot_stats(self) -> Dict[str, Any]:
        """Get statistics about the copilot usage."""
        if not self.conversation_history:
            return {'total_queries': 0, 'average_confidence': 0, 'query_types': {}}
        
        total_queries = len(self.conversation_history)
        avg_confidence = sum(q.confidence_score for q in self.conversation_history) / total_queries
        
        # Count query types
        query_types = {}
        for query in self.conversation_history:
            qtype = query.query_type
            query_types[qtype] = query_types.get(qtype, 0) + 1
        
        return {
            'total_queries': total_queries,
            'average_confidence': avg_confidence,
            'query_types': query_types,
            'high_confidence_queries': sum(1 for q in self.conversation_history if q.is_high_confidence()),
            'session_duration': (datetime.now() - self.conversation_history[0].timestamp).total_seconds() / 60 if self.conversation_history else 0
        }