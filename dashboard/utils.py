"""
Dashboard Utilities
==================

Utility functions and helpers for the AI Retail Intelligence dashboard.
This module contains common functions used across different dashboard pages.
"""

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
import requests
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple
import json
import time

from config import config

class APIClient:
    """Client for interacting with the AI Retail Intelligence API."""
    
    def __init__(self, base_url: str = None, timeout: int = None):
        self.base_url = base_url or config.API_BASE_URL
        self.timeout = timeout or config.API_TIMEOUT
        self.session = requests.Session()
    
    def get(self, endpoint: str, params: Dict = None) -> Optional[Dict]:
        """Make GET request to API."""
        try:
            url = f"{self.base_url}/{endpoint.lstrip('/')}"
            response = self.session.get(url, params=params, timeout=self.timeout)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            st.error(f"API request failed: {str(e)}")
            return None
    
    def post(self, endpoint: str, data: Dict = None) -> Optional[Dict]:
        """Make POST request to API."""
        try:
            url = f"{self.base_url}/{endpoint.lstrip('/')}"
            response = self.session.post(url, json=data, timeout=self.timeout)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            st.error(f"API request failed: {str(e)}")
            return None
    
    def health_check(self) -> bool:
        """Check if API is healthy."""
        try:
            response = self.session.get(f"{self.base_url.replace('/api/v1', '')}/health", timeout=5)
            return response.status_code == 200
        except:
            return False

class ChartBuilder:
    """Helper class for building Plotly charts."""
    
    @staticmethod
    def create_price_trend_chart(data: pd.DataFrame, title: str = "Price Trends") -> go.Figure:
        """Create a price trend chart."""
        fig = go.Figure()
        
        if 'date' in data.columns and 'close' in data.columns:
            fig.add_trace(go.Scatter(
                x=data['date'],
                y=data['close'],
                mode='lines',
                name='Price',
                line=dict(color=config.CHART_COLORS['primary'], width=2)
            ))
        
        fig.update_layout(
            title=title,
            xaxis_title="Date",
            yaxis_title="Price (₹)",
            height=config.CHART_HEIGHT,
            showlegend=True
        )
        
        return fig
    
    @staticmethod
    def create_forecast_chart(historical_data: pd.DataFrame, forecast_data: Dict, 
                            title: str = "Price Forecast") -> go.Figure:
        """Create a forecast chart with historical and predicted data."""
        fig = go.Figure()
        
        # Historical data
        if 'date' in historical_data.columns and 'close' in historical_data.columns:
            fig.add_trace(go.Scatter(
                x=historical_data['date'].tail(60),
                y=historical_data['close'].tail(60),
                mode='lines',
                name='Historical',
                line=dict(color=config.CHART_COLORS['primary'], width=2)
            ))
        
        # Forecast data
        if forecast_data and 'predicted_prices' in forecast_data:
            last_date = historical_data['date'].iloc[-1] if 'date' in historical_data.columns else datetime.now()
            forecast_dates = [last_date + timedelta(days=i+1) for i in range(len(forecast_data['predicted_prices']))]
            
            fig.add_trace(go.Scatter(
                x=forecast_dates,
                y=forecast_data['predicted_prices'],
                mode='lines',
                name='Forecast',
                line=dict(color='red', width=2, dash='dash')
            ))
            
            # Confidence intervals
            if 'confidence_intervals' in forecast_data:
                ci = forecast_data['confidence_intervals']
                if 'lower' in ci and 'upper' in ci:
                    fig.add_trace(go.Scatter(
                        x=forecast_dates + forecast_dates[::-1],
                        y=ci['upper'] + ci['lower'][::-1],
                        fill='toself',
                        fillcolor='rgba(255,0,0,0.2)',
                        line=dict(color='rgba(255,255,255,0)'),
                        name='Confidence Interval'
                    ))
        
        fig.update_layout(
            title=title,
            xaxis_title="Date",
            yaxis_title="Price (₹)",
            height=config.CHART_HEIGHT,
            showlegend=True
        )
        
        return fig
    
    @staticmethod
    def create_price_comparison_chart(platforms: List[str], prices: List[float], 
                                    lowest_platform: str, highest_platform: str,
                                    title: str = "Price Comparison") -> go.Figure:
        """Create a price comparison bar chart."""
        # Color code bars
        colors = []
        for platform in platforms:
            if platform == lowest_platform:
                colors.append(config.CHART_COLORS['best_price'])
            elif platform == highest_platform:
                colors.append(config.CHART_COLORS['worst_price'])
            else:
                colors.append(config.CHART_COLORS['neutral'])
        
        fig = go.Figure(data=[
            go.Bar(x=platforms, y=prices, marker_color=colors)
        ])
        
        fig.update_layout(
            title=title,
            xaxis_title="Platform",
            yaxis_title="Price (₹)",
            height=config.CHART_HEIGHT,
            showlegend=False
        )
        
        return fig
    
    @staticmethod
    def create_platform_summary_chart(platform_stats: Dict) -> go.Figure:
        """Create platform summary chart."""
        platforms = list(platform_stats.keys())
        avg_prices = [stats['avg_price'] for stats in platform_stats.values()]
        
        fig = px.bar(
            x=platforms,
            y=avg_prices,
            title="Average Prices by Platform",
            labels={'x': 'Platform', 'y': 'Average Price (₹)'}
        )
        
        fig.update_layout(height=config.CHART_HEIGHT)
        return fig

class DataFormatter:
    """Helper class for formatting data for display."""
    
    @staticmethod
    def format_currency(amount: float, currency: str = "₹") -> str:
        """Format currency amount."""
        return f"{currency}{amount:,.2f}"
    
    @staticmethod
    def format_percentage(value: float, decimals: int = 1) -> str:
        """Format percentage value."""
        return f"{value:.{decimals}f}%"
    
    @staticmethod
    def format_trend_indicator(trend: float) -> str:
        """Get trend indicator emoji."""
        if trend > 0:
            return "📈"
        elif trend < 0:
            return "📉"
        else:
            return "➡️"
    
    @staticmethod
    def format_status_indicator(status: str) -> str:
        """Get status indicator."""
        status_map = {
            'online': '✅',
            'offline': '❌',
            'warning': '⚠️',
            'info': 'ℹ️',
            'success': '✅',
            'error': '❌'
        }
        return status_map.get(status.lower(), '❓')
    
    @staticmethod
    def create_comparison_dataframe(comparison_data: Dict) -> pd.DataFrame:
        """Create DataFrame for price comparison display."""
        if not comparison_data or 'current_prices' not in comparison_data:
            return pd.DataFrame()
        
        data = []
        for platform, price in comparison_data['current_prices'].items():
            status = '🏆 Best' if platform == comparison_data['lowest_platform'] else \
                    '💸 Highest' if platform == comparison_data['highest_platform'] else \
                    '⚖️ Average'
            
            difference = price - comparison_data['lowest_price']
            
            data.append({
                'Platform': platform,
                'Price (₹)': f"{price:.2f}",
                'Difference': f"{difference:+.2f}",
                'Status': status
            })
        
        return pd.DataFrame(data)

class CacheManager:
    """Simple caching manager for dashboard data."""
    
    def __init__(self):
        if 'cache' not in st.session_state:
            st.session_state.cache = {}
    
    def get(self, key: str) -> Optional[Any]:
        """Get cached value."""
        if key in st.session_state.cache:
            data, timestamp = st.session_state.cache[key]
            if time.time() - timestamp < config.CACHE_TTL:
                return data
            else:
                # Cache expired
                del st.session_state.cache[key]
        return None
    
    def set(self, key: str, value: Any) -> None:
        """Set cached value."""
        st.session_state.cache[key] = (value, time.time())
    
    def clear(self) -> None:
        """Clear all cached data."""
        st.session_state.cache = {}

class UIHelpers:
    """Helper functions for UI components."""
    
    @staticmethod
    def render_metric_card(title: str, value: str, delta: str = None, 
                          delta_color: str = "normal") -> None:
        """Render a metric card."""
        st.metric(
            label=title,
            value=value,
            delta=delta,
            delta_color=delta_color
        )
    
    @staticmethod
    def render_status_card(title: str, status: str, message: str) -> None:
        """Render a status card."""
        if status == "success":
            st.success(f"✅ {title}: {message}")
        elif status == "warning":
            st.warning(f"⚠️ {title}: {message}")
        elif status == "error":
            st.error(f"❌ {title}: {message}")
        else:
            st.info(f"ℹ️ {title}: {message}")
    
    @staticmethod
    def render_loading_spinner(message: str = "Loading...") -> None:
        """Render loading spinner with message."""
        with st.spinner(message):
            time.sleep(0.1)  # Brief pause for visual effect
    
    @staticmethod
    def render_error_message(error_type: str, custom_message: str = None) -> None:
        """Render standardized error message."""
        message = custom_message or config.ERROR_MESSAGES.get(error_type, "An error occurred")
        st.error(f"❌ {message}")
    
    @staticmethod
    def render_success_message(success_type: str, custom_message: str = None) -> None:
        """Render standardized success message."""
        message = custom_message or config.SUCCESS_MESSAGES.get(success_type, "Operation successful")
        st.success(f"✅ {message}")
    
    @staticmethod
    def render_info_box(title: str, content: str, expandable: bool = False) -> None:
        """Render information box."""
        if expandable:
            with st.expander(title):
                st.info(content)
        else:
            st.info(f"**{title}:** {content}")

class ValidationHelpers:
    """Helper functions for data validation."""
    
    @staticmethod
    def validate_forecast_params(horizon: int, model_type: str) -> Tuple[bool, str]:
        """Validate forecast parameters."""
        if not (config.MIN_FORECAST_HORIZON <= horizon <= config.MAX_FORECAST_HORIZON):
            return False, f"Horizon must be between {config.MIN_FORECAST_HORIZON} and {config.MAX_FORECAST_HORIZON} days"
        
        valid_models = ['moving_average', 'random_forest']
        if model_type not in valid_models:
            return False, f"Model type must be one of: {', '.join(valid_models)}"
        
        return True, "Valid parameters"
    
    @staticmethod
    def validate_file_upload(uploaded_file) -> Tuple[bool, str]:
        """Validate uploaded file."""
        if uploaded_file is None:
            return False, "No file uploaded"
        
        if uploaded_file.size > config.MAX_FILE_SIZE:
            return False, f"File size exceeds {config.MAX_FILE_SIZE / (1024*1024):.1f}MB limit"
        
        valid_types = ['text/plain', 'application/pdf', 'application/vnd.openxmlformats-officedocument.wordprocessingml.document']
        if uploaded_file.type not in valid_types:
            return False, "Invalid file type. Supported: TXT, PDF, DOCX"
        
        return True, "Valid file"
    
    @staticmethod
    def validate_text_input(text: str, min_length: int = 10, max_length: int = 10000) -> Tuple[bool, str]:
        """Validate text input."""
        if not text or not text.strip():
            return False, "Text cannot be empty"
        
        text_length = len(text.strip())
        if text_length < min_length:
            return False, f"Text must be at least {min_length} characters"
        
        if text_length > max_length:
            return False, f"Text cannot exceed {max_length} characters"
        
        return True, "Valid text"

# Global instances
api_client = APIClient()
chart_builder = ChartBuilder()
data_formatter = DataFormatter()
cache_manager = CacheManager()
ui_helpers = UIHelpers()
validation_helpers = ValidationHelpers()