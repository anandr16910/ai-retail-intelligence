"""
Dashboard Configuration
======================

Configuration settings for the AI Retail Intelligence web dashboard.
This module contains all configurable parameters for the dashboard interface.
"""

import os
from typing import Dict, Any

class DashboardConfig:
    """Dashboard configuration class."""
    
    # Page Configuration
    PAGE_TITLE = "AI Retail Intelligence Dashboard"
    PAGE_ICON = "🛒"
    LAYOUT = "wide"
    INITIAL_SIDEBAR_STATE = "expanded"
    
    # API Configuration
    API_BASE_URL = os.getenv("API_BASE_URL", "http://localhost:8000/api/v1")
    API_TIMEOUT = int(os.getenv("API_TIMEOUT", "10"))
    
    # Dashboard Settings
    DEFAULT_FORECAST_HORIZON = 30
    MAX_FORECAST_HORIZON = 90
    MIN_FORECAST_HORIZON = 1
    
    # Chart Configuration
    CHART_HEIGHT = 400
    CHART_COLORS = {
        'gold': '#FFD700',
        'silver': '#C0C0C0',
        'best_price': '#28a745',
        'worst_price': '#dc3545',
        'neutral': '#17a2b8',
        'primary': '#007bff'
    }
    
    # Data Display Settings
    MAX_PRODUCTS_DISPLAY = 50
    MAX_DEALS_DISPLAY = 20
    DEFAULT_DEALS_LIMIT = 10
    
    # Chat Configuration
    MAX_CHAT_HISTORY = 50
    CHAT_WELCOME_MESSAGE = """Hello! I'm your AI Market Copilot. I can help you with:

• Price forecasting and trends
• Competitive pricing analysis
• Product comparisons
• Market insights

What would you like to know?"""
    
    # Performance Settings
    CACHE_TTL = 300  # 5 minutes
    MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB
    
    # UI Styling
    CUSTOM_CSS = """
    <style>
        .main-header {
            font-size: 2.5rem;
            font-weight: bold;
            color: #1f77b4;
            text-align: center;
            margin-bottom: 2rem;
        }
        .metric-card {
            background-color: #f0f2f6;
            padding: 1rem;
            border-radius: 0.5rem;
            border-left: 4px solid #1f77b4;
        }
        .success-card {
            background-color: #d4edda;
            padding: 1rem;
            border-radius: 0.5rem;
            border-left: 4px solid #28a745;
        }
        .warning-card {
            background-color: #fff3cd;
            padding: 1rem;
            border-radius: 0.5rem;
            border-left: 4px solid #ffc107;
        }
        .chat-message {
            padding: 1rem;
            border-radius: 0.5rem;
            margin: 0.5rem 0;
        }
        .user-message {
            background-color: #e3f2fd;
            margin-left: 2rem;
        }
        .bot-message {
            background-color: #f5f5f5;
            margin-right: 2rem;
        }
        .sidebar .sidebar-content {
            background-color: #f8f9fa;
        }
        .stButton > button {
            width: 100%;
        }
        .stSelectbox > div > div {
            background-color: white;
        }
    </style>
    """
    
    # Navigation Configuration
    NAVIGATION_PAGES = [
        "🏠 Dashboard Overview",
        "📈 Price Forecasting",
        "💰 Competitive Pricing",
        "🤖 Market Copilot",
        "📄 Document Analysis",
        "⚙️ Platform Status",
        "🔧 Amazon Q Integration"
    ]
    
    # Sample Documents for Testing
    SAMPLE_DOCUMENTS = {
        "Market Report": """Gold prices have risen 15% this quarter due to inflation concerns and geopolitical tensions. Silver has shown similar trends with a 12% increase. ETF investments in precious metals have surged by 25% as investors seek safe-haven assets. The Indian market has seen increased volatility with rupee depreciation affecting import costs.""",
        
        "Financial Analysis": """Q4 revenue reached ₹125.6 Cr, representing 11.8% growth YoY. Gross margin improved to 24.5% while net margin stood at 8.2%. Operating margin increased to 12.1% due to operational efficiencies. Market share increased to 3.2% with 2.1M active users across 6 major platforms. Customer acquisition cost decreased by 15% while lifetime value increased by 22%.""",
        
        "Competitive Intelligence": """Amazon leads with 35% market share, followed by Flipkart at 28% and JioMart at 18%. Price variations of up to 15% observed across platforms for electronics. Customer price sensitivity highest in electronics category with 78% using comparison tools. Zepto shows aggressive pricing in quick commerce with average 8% lower prices. DMart Ready maintains premium positioning with focus on quality."""
    }
    
    # Quick Action Queries
    QUICK_ACTIONS = {
        "📈 Gold Trends": "What are the current gold price trends?",
        "💰 Best Deals": "Show me the best deals available",
        "🔍 Compare Fridge": "Compare prices for Godrej Single Door Fridge",
        "📊 Market Summary": "Give me a market summary"
    }
    
    # Platform Status Configuration
    CORE_SERVICES = [
        ("Data Loader", "✅", "Online"),
        ("Forecasting Engine", "✅", "Online"),
        ("Pricing Engine", "✅", "Online"),
        ("Market Copilot", "✅", "Online"),
        ("Document Parser", "✅", "Online"),
        ("API Gateway", "✅", "Online")
    ]
    
    INTEGRATIONS = [
        ("Amazon Bedrock", "🔧", "Framework Ready"),
        ("Amazon Q", "⚠️", "Optional Extension"),
        ("FastAPI", "✅", "Running"),
        ("Streamlit Dashboard", "✅", "Active")
    ]
    
    # Error Messages
    ERROR_MESSAGES = {
        'api_connection': "Unable to connect to the API server. Please ensure the main platform is running.",
        'data_loading': "Error loading data. Please check the data files and try again.",
        'forecast_generation': "Error generating forecast. Please check your parameters and try again.",
        'price_comparison': "Error comparing prices. Please try a different product.",
        'document_analysis': "Error analyzing document. Please check the content and try again.",
        'chat_processing': "Error processing your query. Please try rephrasing your question."
    }
    
    # Success Messages
    SUCCESS_MESSAGES = {
        'forecast_generated': "Forecast generated successfully!",
        'prices_compared': "Price comparison completed!",
        'document_analyzed': "Document analysis completed!",
        'data_loaded': "Data loaded successfully!",
        'api_connected': "API connection successful!"
    }
    
    # Feature Flags
    FEATURES = {
        'enable_caching': True,
        'enable_file_upload': True,
        'enable_export': False,  # Future feature
        'enable_notifications': False,  # Future feature
        'enable_user_auth': False,  # Future feature
        'debug_mode': os.getenv("DEBUG", "false").lower() == "true"
    }
    
    @classmethod
    def get_chart_config(cls, chart_type: str = "default") -> Dict[str, Any]:
        """Get chart configuration for different chart types."""
        base_config = {
            'height': cls.CHART_HEIGHT,
            'use_container_width': True,
            'theme': 'streamlit'
        }
        
        if chart_type == "price_trend":
            return {
                **base_config,
                'title': "Price Trends",
                'xaxis_title': "Date",
                'yaxis_title': "Price (₹)"
            }
        elif chart_type == "platform_comparison":
            return {
                **base_config,
                'title': "Platform Price Comparison",
                'xaxis_title': "Platform",
                'yaxis_title': "Price (₹)"
            }
        elif chart_type == "forecast":
            return {
                **base_config,
                'title': "Price Forecast",
                'xaxis_title': "Date",
                'yaxis_title': "Price (₹)"
            }
        
        return base_config
    
    @classmethod
    def get_api_endpoint(cls, endpoint: str) -> str:
        """Get full API endpoint URL."""
        return f"{cls.API_BASE_URL}/{endpoint.lstrip('/')}"
    
    @classmethod
    def is_feature_enabled(cls, feature: str) -> bool:
        """Check if a feature is enabled."""
        return cls.FEATURES.get(feature, False)

# Create global config instance
config = DashboardConfig()