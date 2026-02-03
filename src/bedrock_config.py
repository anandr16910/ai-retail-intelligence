"""Configuration and setup for Amazon Bedrock integration.

This module provides configuration management for Bedrock foundation models
and integration settings for the AI Retail Intelligence Platform.
"""

import os
from typing import Dict, Any, List, Optional
from dataclasses import dataclass
from enum import Enum

from src.config import settings


class BedrockModel(Enum):
    """Available Bedrock foundation models."""
    CLAUDE_3_SONNET = "anthropic.claude-3-sonnet-20240229-v1:0"
    CLAUDE_3_HAIKU = "anthropic.claude-3-haiku-20240307-v1:0"
    CLAUDE_3_OPUS = "anthropic.claude-3-opus-20240229-v1:0"
    TITAN_TEXT_PREMIER = "amazon.titan-text-premier-v1:0"
    TITAN_TEXT_EXPRESS = "amazon.titan-text-express-v1"
    COHERE_COMMAND_TEXT = "cohere.command-text-v14"
    AI21_JURASSIC_ULTRA = "ai21.j2-ultra-v1"


class BedrockRegion(Enum):
    """AWS regions supporting Bedrock."""
    US_EAST_1 = "us-east-1"
    US_WEST_2 = "us-west-2"
    EU_WEST_1 = "eu-west-1"
    AP_SOUTHEAST_1 = "ap-southeast-1"


@dataclass
class ModelConfiguration:
    """Configuration for a specific Bedrock model."""
    model_id: str
    display_name: str
    provider: str
    max_tokens: int
    temperature_range: tuple
    use_cases: List[str]
    cost_per_1k_tokens: float
    strengths: List[str]
    limitations: List[str]


class BedrockModelRegistry:
    """Registry of available Bedrock models with their configurations."""
    
    def __init__(self):
        """Initialize model registry."""
        self.models = {
            BedrockModel.CLAUDE_3_SONNET: ModelConfiguration(
                model_id=BedrockModel.CLAUDE_3_SONNET.value,
                display_name="Claude 3 Sonnet",
                provider="Anthropic",
                max_tokens=4096,
                temperature_range=(0.0, 1.0),
                use_cases=[
                    "Complex financial analysis",
                    "Long-term forecasting",
                    "Risk assessment",
                    "Market sentiment analysis"
                ],
                cost_per_1k_tokens=0.003,
                strengths=[
                    "Superior reasoning capabilities",
                    "Detailed explanations",
                    "Context understanding",
                    "Risk analysis"
                ],
                limitations=[
                    "Higher cost",
                    "Slower inference",
                    "Token limits"
                ]
            ),
            
            BedrockModel.CLAUDE_3_HAIKU: ModelConfiguration(
                model_id=BedrockModel.CLAUDE_3_HAIKU.value,
                display_name="Claude 3 Haiku",
                provider="Anthropic",
                max_tokens=4096,
                temperature_range=(0.0, 1.0),
                use_cases=[
                    "Quick analysis",
                    "Real-time predictions",
                    "Simple forecasting",
                    "Data summarization"
                ],
                cost_per_1k_tokens=0.00025,
                strengths=[
                    "Fast inference",
                    "Cost-effective",
                    "Good for simple tasks",
                    "Low latency"
                ],
                limitations=[
                    "Less complex reasoning",
                    "Shorter responses",
                    "Limited context"
                ]
            ),
            
            BedrockModel.TITAN_TEXT_PREMIER: ModelConfiguration(
                model_id=BedrockModel.TITAN_TEXT_PREMIER.value,
                display_name="Titan Text Premier",
                provider="Amazon",
                max_tokens=3000,
                temperature_range=(0.0, 1.0),
                use_cases=[
                    "General forecasting",
                    "Market analysis",
                    "Content generation",
                    "Data interpretation"
                ],
                cost_per_1k_tokens=0.0005,
                strengths=[
                    "AWS native integration",
                    "Balanced performance",
                    "Good cost-performance ratio",
                    "Reliable predictions"
                ],
                limitations=[
                    "Less specialized for finance",
                    "Moderate reasoning depth",
                    "Generic responses"
                ]
            )
        }
    
    def get_model_config(self, model: BedrockModel) -> ModelConfiguration:
        """Get configuration for a specific model."""
        return self.models.get(model)
    
    def get_models_by_use_case(self, use_case: str) -> List[BedrockModel]:
        """Get models suitable for a specific use case."""
        suitable_models = []
        for model, config in self.models.items():
            if use_case.lower() in [uc.lower() for uc in config.use_cases]:
                suitable_models.append(model)
        return suitable_models
    
    def get_cost_comparison(self) -> Dict[str, float]:
        """Get cost comparison across models."""
        return {
            config.display_name: config.cost_per_1k_tokens 
            for config in self.models.values()
        }


class BedrockSettings:
    """Settings and configuration for Bedrock integration."""
    
    def __init__(self):
        """Initialize Bedrock settings."""
        self.aws_region = os.getenv('BEDROCK_REGION', BedrockRegion.US_EAST_1.value)
        self.aws_access_key_id = os.getenv('AWS_ACCESS_KEY_ID')
        self.aws_secret_access_key = os.getenv('AWS_SECRET_ACCESS_KEY')
        self.aws_session_token = os.getenv('AWS_SESSION_TOKEN')
        
        # Model preferences
        self.default_model = BedrockModel.CLAUDE_3_SONNET
        self.fallback_model = BedrockModel.TITAN_TEXT_PREMIER
        
        # Request settings
        self.default_max_tokens = 3000
        self.default_temperature = 0.1
        self.request_timeout = 30
        self.max_retries = 3
        
        # Cost management
        self.daily_cost_limit = 50.0  # USD
        self.monthly_cost_limit = 1000.0  # USD
        self.cost_tracking_enabled = True
        
        # Performance settings
        self.enable_caching = True
        self.cache_ttl = 3600  # 1 hour
        self.parallel_requests = 5
        
    def get_model_parameters(self, model: BedrockModel) -> Dict[str, Any]:
        """Get default parameters for a model."""
        registry = BedrockModelRegistry()
        config = registry.get_model_config(model)
        
        if not config:
            return {}
        
        return {
            'max_tokens': min(self.default_max_tokens, config.max_tokens),
            'temperature': max(
                config.temperature_range[0], 
                min(self.default_temperature, config.temperature_range[1])
            ),
            'top_p': 0.9,
            'stop_sequences': []
        }
    
    def validate_credentials(self) -> bool:
        """Validate AWS credentials."""
        required_vars = ['AWS_ACCESS_KEY_ID', 'AWS_SECRET_ACCESS_KEY']
        return all(os.getenv(var) for var in required_vars)
    
    def get_client_config(self) -> Dict[str, Any]:
        """Get configuration for Bedrock client."""
        return {
            'region_name': self.aws_region,
            'aws_access_key_id': self.aws_access_key_id,
            'aws_secret_access_key': self.aws_secret_access_key,
            'aws_session_token': self.aws_session_token,
            'config': {
                'retries': {'max_attempts': self.max_retries},
                'read_timeout': self.request_timeout
            }
        }


class BedrockPromptTemplates:
    """Templates for Bedrock prompts for different use cases."""
    
    @staticmethod
    def forecasting_prompt(
        symbol: str, 
        historical_data: str, 
        horizon: int, 
        context: Optional[str] = None
    ) -> str:
        """Generate forecasting prompt template."""
        return f"""
You are an expert financial analyst specializing in {symbol} price forecasting. 
Analyze the provided historical data and generate accurate price predictions.

Asset: {symbol}
Forecast Horizon: {horizon} days
Historical Data: {historical_data}
{f"Additional Context: {context}" if context else ""}

Please provide:
1. Daily price predictions for the next {horizon} days
2. 95% confidence intervals for each prediction
3. Detailed reasoning for your forecast
4. Risk assessment and volatility expectations
5. Key factors influencing the forecast
6. Alternative scenarios (bull/bear cases)

Format your response as structured JSON with clear numerical predictions and explanations.
"""
    
    @staticmethod
    def risk_assessment_prompt(market_data: str, symbol: str) -> str:
        """Generate risk assessment prompt template."""
        return f"""
As a risk management expert, analyze the following market data for {symbol} and provide 
a comprehensive risk assessment.

Market Data: {market_data}

Provide analysis on:
1. Overall risk level (low/medium/high)
2. Volatility forecast
3. Downside risk percentage
4. Key risk factors
5. Risk mitigation strategies
6. Stress test scenarios
7. Correlation risks with other assets

Format as JSON with quantitative risk metrics and qualitative insights.
"""
    
    @staticmethod
    def market_sentiment_prompt(news_data: str, symbol: str) -> str:
        """Generate market sentiment analysis prompt."""
        return f"""
Analyze the market sentiment for {symbol} based on the following information:

News and Market Data: {news_data}

Provide sentiment analysis including:
1. Overall sentiment score (-1 to +1)
2. Sentiment trend (improving/declining/stable)
3. Key sentiment drivers
4. Impact on price expectations
5. Sentiment-based trading recommendations
6. Confidence level in sentiment assessment

Return structured JSON with sentiment metrics and explanations.
"""
    
    @staticmethod
    def competitive_analysis_prompt(competitor_data: str, symbol: str) -> str:
        """Generate competitive analysis prompt."""
        return f"""
Perform competitive analysis for {symbol} in the retail/commerce market:

Competitor Data: {competitor_data}

Analyze:
1. Competitive positioning
2. Market share implications
3. Pricing strategy recommendations
4. Competitive advantages/disadvantages
5. Market opportunity assessment
6. Strategic recommendations

Provide actionable insights in JSON format.
"""


class BedrockUseCaseMapper:
    """Maps business use cases to optimal Bedrock models and configurations."""
    
    def __init__(self):
        """Initialize use case mapper."""
        self.use_case_mappings = {
            'short_term_forecasting': {
                'primary_model': BedrockModel.CLAUDE_3_HAIKU,
                'fallback_model': BedrockModel.TITAN_TEXT_EXPRESS,
                'parameters': {'temperature': 0.05, 'max_tokens': 2000},
                'prompt_template': 'forecasting_prompt'
            },
            'long_term_forecasting': {
                'primary_model': BedrockModel.CLAUDE_3_SONNET,
                'fallback_model': BedrockModel.CLAUDE_3_HAIKU,
                'parameters': {'temperature': 0.1, 'max_tokens': 4000},
                'prompt_template': 'forecasting_prompt'
            },
            'risk_assessment': {
                'primary_model': BedrockModel.CLAUDE_3_SONNET,
                'fallback_model': BedrockModel.TITAN_TEXT_PREMIER,
                'parameters': {'temperature': 0.0, 'max_tokens': 3000},
                'prompt_template': 'risk_assessment_prompt'
            },
            'market_sentiment': {
                'primary_model': BedrockModel.CLAUDE_3_SONNET,
                'fallback_model': BedrockModel.CLAUDE_3_HAIKU,
                'parameters': {'temperature': 0.2, 'max_tokens': 2500},
                'prompt_template': 'market_sentiment_prompt'
            },
            'competitive_analysis': {
                'primary_model': BedrockModel.CLAUDE_3_SONNET,
                'fallback_model': BedrockModel.TITAN_TEXT_PREMIER,
                'parameters': {'temperature': 0.15, 'max_tokens': 3500},
                'prompt_template': 'competitive_analysis_prompt'
            },
            'real_time_analysis': {
                'primary_model': BedrockModel.CLAUDE_3_HAIKU,
                'fallback_model': BedrockModel.TITAN_TEXT_EXPRESS,
                'parameters': {'temperature': 0.1, 'max_tokens': 1500},
                'prompt_template': 'forecasting_prompt'
            }
        }
    
    def get_optimal_config(self, use_case: str) -> Dict[str, Any]:
        """Get optimal model configuration for a use case."""
        return self.use_case_mappings.get(use_case, {})
    
    def get_available_use_cases(self) -> List[str]:
        """Get list of available use cases."""
        return list(self.use_case_mappings.keys())


# Cost tracking and monitoring
class BedrockCostTracker:
    """Track and monitor Bedrock usage costs."""
    
    def __init__(self):
        """Initialize cost tracker."""
        self.daily_usage = {}
        self.monthly_usage = {}
        self.cost_alerts = []
    
    def track_request(self, model: BedrockModel, tokens_used: int) -> float:
        """Track a Bedrock request and calculate cost."""
        registry = BedrockModelRegistry()
        config = registry.get_model_config(model)
        
        if not config:
            return 0.0
        
        cost = (tokens_used / 1000) * config.cost_per_1k_tokens
        
        # Update usage tracking
        today = str(datetime.now().date())
        month = str(datetime.now().strftime('%Y-%m'))
        
        self.daily_usage[today] = self.daily_usage.get(today, 0) + cost
        self.monthly_usage[month] = self.monthly_usage.get(month, 0) + cost
        
        return cost
    
    def check_cost_limits(self, settings: BedrockSettings) -> List[str]:
        """Check if cost limits are exceeded."""
        alerts = []
        
        today = str(datetime.now().date())
        month = str(datetime.now().strftime('%Y-%m'))
        
        daily_cost = self.daily_usage.get(today, 0)
        monthly_cost = self.monthly_usage.get(month, 0)
        
        if daily_cost > settings.daily_cost_limit:
            alerts.append(f"Daily cost limit exceeded: ${daily_cost:.2f}")
        
        if monthly_cost > settings.monthly_cost_limit:
            alerts.append(f"Monthly cost limit exceeded: ${monthly_cost:.2f}")
        
        return alerts
    
    def get_usage_report(self) -> Dict[str, Any]:
        """Get usage and cost report."""
        return {
            'daily_usage': self.daily_usage,
            'monthly_usage': self.monthly_usage,
            'total_requests': sum(len(usage) for usage in [self.daily_usage, self.monthly_usage]),
            'alerts': self.cost_alerts
        }


# Example configuration usage
def example_bedrock_config():
    """Example of Bedrock configuration usage."""
    
    # Initialize components
    settings = BedrockSettings()
    registry = BedrockModelRegistry()
    mapper = BedrockUseCaseMapper()
    cost_tracker = BedrockCostTracker()
    
    print("Bedrock Configuration Framework:")
    print(f"Default Model: {settings.default_model.value}")
    print(f"Available Models: {len(registry.models)}")
    print(f"Use Cases: {mapper.get_available_use_cases()}")
    
    # Get optimal config for forecasting
    forecast_config = mapper.get_optimal_config('long_term_forecasting')
    print(f"Forecasting Model: {forecast_config.get('primary_model')}")
    
    return {
        'settings': settings,
        'registry': registry,
        'mapper': mapper,
        'cost_tracker': cost_tracker
    }


if __name__ == "__main__":
    example_bedrock_config()