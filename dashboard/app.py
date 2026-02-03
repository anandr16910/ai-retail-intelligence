"""
AI Retail Intelligence Web Dashboard
===================================

A comprehensive web dashboard built with Streamlit for the AI Retail Intelligence platform.
This dashboard provides an intuitive interface for all platform capabilities including
price forecasting, competitive pricing, market copilot, and document analysis.

Features:
- Interactive price forecasting charts
- Real-time competitive pricing comparison
- Market copilot chat interface
- Document analysis and insights
- Platform analytics and reporting
- Amazon Bedrock integration status

Note: This is a sample implementation for demonstration purposes.
"""

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime, timedelta
import requests
import json
from typing import Dict, List, Any, Optional
import sys
import os

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from src.competitive_pricing import CompetitivePricingEngine
    from src.forecasting_model import PriceForecastingEngine
    from src.market_copilot import MarketCopilot
    from src.document_parser import DocumentParser
    from src.data_loader import DataLoader
    from src.amazon_q_extension import AmazonQIntegrationManager
except ImportError:
    st.error("Unable to import platform modules. Please ensure the dashboard is run from the project root.")
    st.stop()

# Page configuration
st.set_page_config(
    page_title="AI Retail Intelligence Dashboard",
    page_icon="🛒",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
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
</style>
""", unsafe_allow_html=True)

class DashboardApp:
    """Main dashboard application class."""
    
    def __init__(self):
        """Initialize dashboard components."""
        self.api_base_url = "http://localhost:8000/api/v1"
        self.initialize_components()
        
    def initialize_components(self):
        """Initialize platform components."""
        try:
            self.pricing_engine = CompetitivePricingEngine()
            self.forecasting_engine = PriceForecastingEngine()
            self.market_copilot = MarketCopilot()
            self.document_parser = DocumentParser()
            self.data_loader = DataLoader()
            self.amazon_q_manager = AmazonQIntegrationManager()
            
            # Load sample data
            self.load_sample_data()
            
        except Exception as e:
            st.error(f"Error initializing components: {str(e)}")
            
    def load_sample_data(self):
        """Load sample data for dashboard."""
        try:
            # Clear any cached data first
            if hasattr(self, 'gold_data'):
                del self.gold_data
            if hasattr(self, 'silver_data'):
                del self.silver_data
            if hasattr(self, 'etf_data'):
                del self.etf_data
            
            # Load pricing data
            self.products = self.pricing_engine.get_product_list()
            
            # Load market data - force fresh load
            all_data = self.data_loader.load_all_data()
            self.gold_data = all_data.get('gold', pd.DataFrame())
            self.silver_data = all_data.get('silver', pd.DataFrame())
            self.etf_data = all_data.get('etf', pd.DataFrame())
            
            # Log current prices for debugging
            if not self.gold_data.empty and 'close' in self.gold_data.columns:
                current_gold = self.gold_data['close'].iloc[-1]
                print(f"DEBUG: Loaded gold price: ₹{current_gold:.2f}")
            
            if not self.silver_data.empty and 'close' in self.silver_data.columns:
                current_silver = self.silver_data['close'].iloc[-1]
                print(f"DEBUG: Loaded silver price: ₹{current_silver:.2f}")
            
        except Exception as e:
            st.warning(f"Could not load all sample data: {str(e)}")
            self.products = []
            self.gold_data = pd.DataFrame()
            self.silver_data = pd.DataFrame()
            self.etf_data = pd.DataFrame()

    def render_sidebar(self):
        """Render sidebar navigation."""
        st.sidebar.markdown("## 🛒 AI Retail Intelligence")
        st.sidebar.markdown("---")
        
        # Navigation
        page = st.sidebar.selectbox(
            "Navigate to:",
            [
                "🏠 Dashboard Overview",
                "📈 Price Forecasting",
                "💰 Competitive Pricing",
                "🤖 Market Copilot",
                "📄 Document Analysis",
                "⚙️ Platform Status",
                "🔧 Amazon Q Integration"
            ]
        )
        
        st.sidebar.markdown("---")
        
        # Quick stats
        st.sidebar.markdown("### Quick Stats")
        if self.products:
            st.sidebar.metric("Products Tracked", len(self.products))
        
        if not self.gold_data.empty:
            latest_gold = self.gold_data['close'].iloc[-1] if 'close' in self.gold_data.columns else 0
            st.sidebar.metric("Latest Gold Price", f"₹{latest_gold:.2f}")
        
        # Platform status
        st.sidebar.markdown("### Platform Status")
        st.sidebar.success("✅ Core Services Online")
        st.sidebar.info("ℹ️ Bedrock Framework Ready")
        st.sidebar.warning("⚠️ Amazon Q (Optional)")
        
        # Data refresh button
        st.sidebar.markdown("---")
        if st.sidebar.button("🔄 Refresh Data"):
            # Clear Streamlit cache
            st.cache_data.clear()
            # Reload data
            self.load_sample_data()
            st.sidebar.success("Data refreshed!")
            st.rerun()
        
        return page.split(" ", 1)[1]  # Remove emoji from page name

    def render_overview(self):
        """Render dashboard overview page."""
        st.markdown('<h1 class="main-header">AI Retail Intelligence Dashboard</h1>', unsafe_allow_html=True)
        
        # Key metrics row
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric(
                label="Products Tracked",
                value=len(self.products),
                delta="6 platforms"
            )
        
        with col2:
            if not self.gold_data.empty and 'close' in self.gold_data.columns:
                current_gold = self.gold_data['close'].iloc[-1]
                prev_gold = self.gold_data['close'].iloc[-2] if len(self.gold_data) > 1 else current_gold
                delta_gold = current_gold - prev_gold
                st.metric(
                    label="Gold Price (₹)",
                    value=f"{current_gold:.2f}",
                    delta=f"{delta_gold:.2f}"
                )
            else:
                st.metric("Gold Price", "No data")
        
        with col3:
            if not self.silver_data.empty and 'close' in self.silver_data.columns:
                current_silver = self.silver_data['close'].iloc[-1]
                prev_silver = self.silver_data['close'].iloc[-2] if len(self.silver_data) > 1 else current_silver
                delta_silver = current_silver - prev_silver
                st.metric(
                    label="Silver Price (₹)",
                    value=f"{current_silver:.2f}",
                    delta=f"{delta_silver:.2f}"
                )
            else:
                st.metric("Silver Price", "No data")
        
        with col4:
            # Calculate best deal savings
            best_deals = self.pricing_engine.get_best_deals(1)
            if best_deals:
                savings = best_deals[0]['savings_amount']
                st.metric(
                    label="Best Deal Savings",
                    value=f"₹{savings:.2f}",
                    delta=f"{best_deals[0]['savings_percentage']:.1f}%"
                )
            else:
                st.metric("Best Deal Savings", "No data")
        
        st.markdown("---")
        
        # Charts row
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("📈 Price Trends")
            if not self.gold_data.empty and 'date' in self.gold_data.columns:
                fig = go.Figure()
                
                # Add gold prices
                if 'close' in self.gold_data.columns:
                    fig.add_trace(go.Scatter(
                        x=self.gold_data['date'],
                        y=self.gold_data['close'],
                        mode='lines',
                        name='Gold',
                        line=dict(color='gold', width=2)
                    ))
                
                # Add silver prices if available
                if not self.silver_data.empty and 'close' in self.silver_data.columns:
                    fig.add_trace(go.Scatter(
                        x=self.silver_data['date'],
                        y=self.silver_data['close'],
                        mode='lines',
                        name='Silver',
                        line=dict(color='silver', width=2)
                    ))
                
                fig.update_layout(
                    title="Precious Metals Price Trends",
                    xaxis_title="Date",
                    yaxis_title="Price (₹)",
                    height=400
                )
                
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("No price trend data available")
        
        with col2:
            st.subheader("💰 Platform Comparison")
            
            # Get platform summary
            platform_summary = self.pricing_engine.get_platform_summary()
            
            if platform_summary and 'platform_stats' in platform_summary:
                platforms = []
                avg_prices = []
                
                for platform, stats in platform_summary['platform_stats'].items():
                    platforms.append(platform)
                    avg_prices.append(stats['avg_price'])
                
                if platforms and avg_prices:
                    fig = px.bar(
                        x=platforms,
                        y=avg_prices,
                        title="Average Prices by Platform",
                        labels={'x': 'Platform', 'y': 'Average Price (₹)'}
                    )
                    fig.update_layout(height=400)
                    st.plotly_chart(fig, use_container_width=True)
                else:
                    st.info("No platform comparison data available")
            else:
                st.info("No platform data available")
        
        # Recent activity
        st.subheader("🔄 Recent Activity")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("### Best Deals")
            best_deals = self.pricing_engine.get_best_deals(5)
            
            if best_deals:
                for i, deal in enumerate(best_deals, 1):
                    with st.expander(f"{i}. {deal['product_name']} - Save ₹{deal['savings_amount']:.2f}"):
                        st.write(f"**Lowest Price:** ₹{deal['lowest_price']:.2f} ({deal['lowest_platform']})")
                        st.write(f"**Highest Price:** ₹{deal['highest_price']:.2f}")
                        st.write(f"**Savings:** {deal['savings_percentage']:.1f}%")
            else:
                st.info("No deals data available")
        
        with col2:
            st.markdown("### Platform Status")
            
            # Core services status
            services = [
                ("Price Forecasting", "✅ Online", "success"),
                ("Competitive Pricing", "✅ Online", "success"),
                ("Market Copilot", "✅ Online", "success"),
                ("Document Parser", "✅ Online", "success"),
                ("Amazon Bedrock", "🔧 Framework Ready", "warning"),
                ("Amazon Q", "⚠️ Optional", "warning")
            ]
            
            for service, status, status_type in services:
                if status_type == "success":
                    st.success(f"{service}: {status}")
                elif status_type == "warning":
                    st.warning(f"{service}: {status}")
                else:
                    st.info(f"{service}: {status}")

    def render_forecasting(self):
        """Render price forecasting page."""
        st.header("📈 Price Forecasting")
        
        # Asset selection
        col1, col2, col3 = st.columns(3)
        
        with col1:
            asset = st.selectbox(
                "Select Asset:",
                ["GOLD", "SILVER", "ETF"]
            )
        
        with col2:
            horizon = st.slider(
                "Forecast Horizon (days):",
                min_value=1,
                max_value=90,
                value=30
            )
        
        with col3:
            model_type = st.selectbox(
                "Model Type:",
                ["moving_average", "random_forest"]
            )
        
        if st.button("Generate Forecast", type="primary"):
            with st.spinner("Generating forecast..."):
                try:
                    # Get historical data
                    if asset == "GOLD":
                        data = self.gold_data
                    elif asset == "SILVER":
                        data = self.silver_data
                    else:
                        data = self.etf_data
                    
                    if not data.empty:
                        # Train model and generate forecast
                        self.forecasting_engine.train_model(data, symbol=asset)
                        forecast_result = self.forecasting_engine.predict_prices(asset, horizon=horizon)
                        
                        # Display results
                        col1, col2 = st.columns(2)
                        
                        with col1:
                            st.subheader("Forecast Results")
                            
                            # Create forecast chart
                            fig = go.Figure()
                            
                            # Historical data
                            if 'date' in data.columns and 'close' in data.columns:
                                fig.add_trace(go.Scatter(
                                    x=data['date'].tail(60),  # Last 60 days
                                    y=data['close'].tail(60),
                                    mode='lines',
                                    name='Historical',
                                    line=dict(color='blue', width=2)
                                ))
                            
                            # Forecast data
                            if forecast_result and 'predicted_prices' in forecast_result:
                                last_date = data['date'].iloc[-1] if 'date' in data.columns else datetime.now()
                                forecast_dates = [last_date + timedelta(days=i+1) for i in range(horizon)]
                                
                                fig.add_trace(go.Scatter(
                                    x=forecast_dates,
                                    y=forecast_result['predicted_prices'],
                                    mode='lines',
                                    name='Forecast',
                                    line=dict(color='red', width=2, dash='dash')
                                ))
                                
                                # Confidence intervals if available
                                if 'confidence_intervals' in forecast_result:
                                    ci = forecast_result['confidence_intervals']
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
                                title=f"{asset} Price Forecast ({horizon} days)",
                                xaxis_title="Date",
                                yaxis_title="Price (₹)",
                                height=500
                            )
                            
                            st.plotly_chart(fig, use_container_width=True)
                        
                        with col2:
                            st.subheader("Forecast Metrics")
                            
                            if forecast_result:
                                # Display metrics
                                if 'model_metrics' in forecast_result:
                                    metrics = forecast_result['model_metrics']
                                    for metric, value in metrics.items():
                                        st.metric(metric.upper(), f"{value:.4f}")
                                
                                # Forecast summary
                                st.subheader("Summary")
                                if 'predicted_prices' in forecast_result:
                                    prices = forecast_result['predicted_prices']
                                    current_price = data['close'].iloc[-1] if 'close' in data.columns else 0
                                    
                                    avg_forecast = sum(prices) / len(prices)
                                    trend = "Upward" if avg_forecast > current_price else "Downward"
                                    change_pct = ((avg_forecast - current_price) / current_price) * 100
                                    
                                    st.write(f"**Current Price:** ₹{current_price:.2f}")
                                    st.write(f"**Average Forecast:** ₹{avg_forecast:.2f}")
                                    st.write(f"**Trend:** {trend}")
                                    st.write(f"**Expected Change:** {change_pct:+.2f}%")
                            
                            # Model information
                            st.subheader("Model Information")
                            st.write(f"**Model Type:** {model_type}")
                            st.write(f"**Training Data:** {len(data)} records")
                            st.write(f"**Forecast Horizon:** {horizon} days")
                    
                    else:
                        st.error(f"No data available for {asset}")
                        
                except Exception as e:
                    st.error(f"Error generating forecast: {str(e)}")

    def render_competitive_pricing(self):
        """Render competitive pricing page."""
        st.header("💰 Competitive Pricing Intelligence")
        
        # Product search
        col1, col2 = st.columns([2, 1])
        
        with col1:
            search_query = st.text_input("Search Products:", placeholder="Enter product name...")
        
        with col2:
            if st.button("Search", type="primary"):
                if search_query:
                    # Search products
                    search_results = self.pricing_engine.search_products(search_query)
                    st.session_state['search_results'] = search_results
        
        # Display search results or product list
        if 'search_results' in st.session_state and st.session_state['search_results']:
            products_to_show = st.session_state['search_results']
            st.success(f"Found {len(products_to_show)} products matching '{search_query}'")
        else:
            products_to_show = self.products[:10]  # Show first 10 products
        
        if products_to_show:
            # Product selection
            selected_product = st.selectbox(
                "Select Product for Comparison:",
                options=products_to_show,
                format_func=lambda x: x['product_name'] if isinstance(x, dict) else str(x)
            )
            
            if selected_product and st.button("Compare Prices", type="primary"):
                with st.spinner("Comparing prices across platforms..."):
                    try:
                        product_id = selected_product['product_id'] if isinstance(selected_product, dict) else selected_product
                        comparison = self.pricing_engine.compare_prices(product_id)
                        
                        if comparison:
                            # Display comparison results
                            st.subheader(f"Price Comparison: {comparison.product_name}")
                            
                            # Metrics row
                            col1, col2, col3, col4 = st.columns(4)
                            
                            with col1:
                                st.metric(
                                    "Lowest Price",
                                    f"₹{comparison.lowest_price:.2f}",
                                    delta=f"{comparison.lowest_platform}"
                                )
                            
                            with col2:
                                st.metric(
                                    "Highest Price",
                                    f"₹{comparison.highest_price:.2f}",
                                    delta=f"{comparison.highest_platform}"
                                )
                            
                            with col3:
                                st.metric(
                                    "Potential Savings",
                                    f"₹{comparison.savings_amount:.2f}",
                                    delta=f"{comparison.price_difference_percentage:.1f}%"
                                )
                            
                            with col4:
                                st.metric(
                                    "Platforms Compared",
                                    len(comparison.current_prices),
                                    delta="Active listings"
                                )
                            
                            # Recommendation
                            st.success(f"💡 **Recommendation:** {comparison.recommendation}")
                            
                            # Price comparison chart
                            col1, col2 = st.columns(2)
                            
                            with col1:
                                st.subheader("Current Prices by Platform")
                                
                                platforms = list(comparison.current_prices.keys())
                                prices = list(comparison.current_prices.values())
                                
                                # Color code bars (green for lowest, red for highest)
                                colors = []
                                for platform in platforms:
                                    if platform == comparison.lowest_platform:
                                        colors.append('green')
                                    elif platform == comparison.highest_platform:
                                        colors.append('red')
                                    else:
                                        colors.append('lightblue')
                                
                                fig = go.Figure(data=[
                                    go.Bar(x=platforms, y=prices, marker_color=colors)
                                ])
                                
                                fig.update_layout(
                                    title="Price Comparison Across Platforms",
                                    xaxis_title="Platform",
                                    yaxis_title="Price (₹)",
                                    height=400
                                )
                                
                                st.plotly_chart(fig, use_container_width=True)
                            
                            with col2:
                                st.subheader("Price Trends")
                                
                                # Show 7-day trends if available
                                if comparison.trend_7_days:
                                    st.write("**7-Day Price Trends:**")
                                    for platform, trend in comparison.trend_7_days.items():
                                        trend_icon = "📈" if trend > 0 else "📉" if trend < 0 else "➡️"
                                        color = "green" if trend > 0 else "red" if trend < 0 else "gray"
                                        st.markdown(f"- **{platform}:** {trend:+.1f}% {trend_icon}")
                                
                                # Detailed price table
                                st.write("**Detailed Comparison:**")
                                price_df = pd.DataFrame([
                                    {
                                        'Platform': platform,
                                        'Price (₹)': f"{price:.2f}",
                                        'Difference': f"{price - comparison.lowest_price:+.2f}",
                                        'Status': '🏆 Best' if platform == comparison.lowest_platform else 
                                                 '💸 Highest' if platform == comparison.highest_platform else '⚖️ Average'
                                    }
                                    for platform, price in comparison.current_prices.items()
                                ])
                                
                                st.dataframe(price_df, use_container_width=True)
                        
                        else:
                            st.error("No comparison data available for this product")
                    
                    except Exception as e:
                        st.error(f"Error comparing prices: {str(e)}")
        
        # Best deals section
        st.markdown("---")
        st.subheader("🔥 Best Deals Available")
        
        col1, col2 = st.columns([1, 3])
        
        with col1:
            deals_limit = st.slider("Number of deals:", 1, 20, 10)
        
        with col2:
            if st.button("Refresh Best Deals"):
                st.session_state['refresh_deals'] = True
        
        # Display best deals
        best_deals = self.pricing_engine.get_best_deals(deals_limit)
        
        if best_deals:
            for i, deal in enumerate(best_deals, 1):
                with st.expander(f"{i}. {deal['product_name']} - Save ₹{deal['savings_amount']:.2f} ({deal['savings_percentage']:.1f}%)"):
                    col1, col2, col3 = st.columns(3)
                    
                    with col1:
                        st.write(f"**Best Price:** ₹{deal['lowest_price']:.2f}")
                        st.write(f"**Platform:** {deal['lowest_platform']}")
                    
                    with col2:
                        st.write(f"**Highest Price:** ₹{deal['highest_price']:.2f}")
                        st.write(f"**Savings:** ₹{deal['savings_amount']:.2f}")
                    
                    with col3:
                        st.write(f"**Savings %:** {deal['savings_percentage']:.1f}%")
                        if st.button(f"Compare {deal['product_name']}", key=f"compare_{i}"):
                            # Trigger comparison for this product
                            comparison = self.pricing_engine.compare_prices(deal['product_id'])
                            if comparison:
                                st.success(f"✅ {comparison.recommendation}")
        else:
            st.info("No deals data available")

    def render_market_copilot(self):
        """Render market copilot chat interface."""
        st.header("🤖 Market Copilot")
        st.markdown("Ask me anything about market trends, pricing, or product comparisons!")
        
        # Initialize chat history
        if 'chat_history' not in st.session_state:
            st.session_state.chat_history = [
                {
                    'role': 'assistant',
                    'content': 'Hello! I\'m your AI Market Copilot. I can help you with:\n\n'
                              '• Price forecasting and trends\n'
                              '• Competitive pricing analysis\n'
                              '• Product comparisons\n'
                              '• Market insights\n\n'
                              'What would you like to know?'
                }
            ]
        
        # Chat interface
        chat_container = st.container()
        
        # Display chat history
        with chat_container:
            for message in st.session_state.chat_history:
                if message['role'] == 'user':
                    st.markdown(f'<div class="chat-message user-message"><strong>You:</strong> {message["content"]}</div>', 
                               unsafe_allow_html=True)
                else:
                    st.markdown(f'<div class="chat-message bot-message"><strong>Market Copilot:</strong> {message["content"]}</div>', 
                               unsafe_allow_html=True)
        
        # Chat input
        col1, col2 = st.columns([4, 1])
        
        with col1:
            user_input = st.text_input("Ask me anything:", key="chat_input", placeholder="e.g., Compare prices for Godrej fridge")
        
        with col2:
            send_button = st.button("Send", type="primary")
        
        # Quick action buttons
        st.markdown("**Quick Actions:**")
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            if st.button("📈 Gold Trends"):
                user_input = "What are the current gold price trends?"
                send_button = True
        
        with col2:
            if st.button("💰 Best Deals"):
                user_input = "Show me the best deals available"
                send_button = True
        
        with col3:
            if st.button("🔍 Compare Fridge"):
                user_input = "Compare prices for Godrej Single Door Fridge"
                send_button = True
        
        with col4:
            if st.button("📊 Market Summary"):
                user_input = "Give me a market summary"
                send_button = True
        
        # Process user input
        if send_button and user_input:
            # Add user message to history
            st.session_state.chat_history.append({
                'role': 'user',
                'content': user_input
            })
            
            # Generate response
            with st.spinner("Thinking..."):
                try:
                    # Update copilot context with current data
                    context = {
                        'products': self.products,
                        'timestamp': datetime.now().isoformat()
                    }
                    
                    if not self.gold_data.empty:
                        context['gold_price'] = self.gold_data['close'].iloc[-1] if 'close' in self.gold_data.columns else None
                    
                    if not self.silver_data.empty:
                        context['silver_price'] = self.silver_data['close'].iloc[-1] if 'close' in self.silver_data.columns else None
                    
                    self.market_copilot.update_context(context)
                    
                    # Process query
                    response = self.market_copilot.process_query(user_input, context)
                    
                    # Add response to history
                    st.session_state.chat_history.append({
                        'role': 'assistant',
                        'content': response
                    })
                    
                    # Rerun to update chat display
                    st.rerun()
                    
                except Exception as e:
                    error_response = f"I apologize, but I encountered an error: {str(e)}. Please try rephrasing your question."
                    st.session_state.chat_history.append({
                        'role': 'assistant',
                        'content': error_response
                    })
                    st.rerun()
        
        # Clear chat button
        if st.button("🗑️ Clear Chat"):
            st.session_state.chat_history = [st.session_state.chat_history[0]]  # Keep welcome message
            st.rerun()

    def render_document_analysis(self):
        """Render document analysis page."""
        st.header("📄 Document Analysis")
        st.markdown("Upload and analyze financial documents, market reports, and research papers.")
        
        # Document upload
        uploaded_file = st.file_uploader(
            "Upload Document",
            type=['txt', 'pdf', 'docx'],
            help="Supported formats: TXT, PDF, DOCX"
        )
        
        # Text input alternative
        st.markdown("**Or paste text directly:**")
        text_input = st.text_area(
            "Document Content:",
            height=200,
            placeholder="Paste your document content here..."
        )
        
        # Analysis options
        col1, col2 = st.columns(2)
        
        with col1:
            analysis_type = st.selectbox(
                "Analysis Type:",
                ["market_intelligence", "financial_report", "research_paper", "general"]
            )
        
        with col2:
            extract_entities = st.checkbox("Extract Financial Entities", value=True)
        
        # Analyze button
        if st.button("Analyze Document", type="primary"):
            content_to_analyze = None
            
            # Get content from file or text input
            if uploaded_file is not None:
                try:
                    if uploaded_file.type == "text/plain":
                        content_to_analyze = str(uploaded_file.read(), "utf-8")
                    else:
                        st.warning("PDF and DOCX parsing not implemented in this demo. Please use text input.")
                except Exception as e:
                    st.error(f"Error reading file: {str(e)}")
            
            elif text_input.strip():
                content_to_analyze = text_input.strip()
            
            if content_to_analyze:
                with st.spinner("Analyzing document..."):
                    try:
                        # Analyze document
                        analysis_result = self.document_parser.parse_document(
                            text_content=content_to_analyze,
                            document_id=f"doc_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
                        )
                        
                        # Display results
                        if analysis_result:
                            col1, col2 = st.columns(2)
                            
                            with col1:
                                st.subheader("📊 Analysis Summary")
                                
                                # Document info
                                st.write(f"**Document Type:** {analysis_result.document_type}")
                                st.write(f"**Content Length:** {len(content_to_analyze)} characters")
                                st.write(f"**Analysis Time:** {analysis_result.processing_timestamp.strftime('%Y-%m-%d %H:%M:%S')}")
                                
                                # Confidence scores
                                if analysis_result.confidence_scores:
                                    st.subheader("🎯 Confidence Scores")
                                    for aspect, score in analysis_result.confidence_scores.items():
                                        st.progress(score, text=f"{aspect}: {score:.2f}")
                            
                            with col2:
                                st.subheader("🔍 Extracted Entities")
                                
                                if analysis_result.extracted_entities:
                                    entities_df = pd.DataFrame(analysis_result.extracted_entities)
                                    st.dataframe(entities_df, use_container_width=True)
                                else:
                                    st.info("No entities extracted")
                            
                            # Market insights
                            if analysis_result.market_insights:
                                st.subheader("💡 Market Insights")
                                
                                for category, insights in analysis_result.market_insights.items():
                                    with st.expander(f"{category.replace('_', ' ').title()}"):
                                        if isinstance(insights, list):
                                            for insight in insights:
                                                st.write(f"• {insight}")
                                        else:
                                            st.write(insights)
                            
                            # Key insights
                            key_insights = analysis_result.get_key_insights()
                            if key_insights:
                                st.subheader("⭐ Key Insights")
                                for insight in key_insights:
                                    st.success(f"✅ {insight}")
                        
                        else:
                            st.error("Failed to analyze document")
                    
                    except Exception as e:
                        st.error(f"Error analyzing document: {str(e)}")
            
            else:
                st.warning("Please upload a file or paste text content to analyze")
        
        # Sample documents
        st.markdown("---")
        st.subheader("📚 Try Sample Documents")
        
        sample_docs = {
            "Market Report": "Gold prices have risen 15% this quarter due to inflation concerns and geopolitical tensions. Silver has shown similar trends with a 12% increase. ETF investments in precious metals have surged by 25% as investors seek safe-haven assets.",
            "Financial Analysis": "Q4 revenue reached ₹125.6 Cr, representing 11.8% growth YoY. Gross margin improved to 24.5% while net margin stood at 8.2%. Market share increased to 3.2% with 2.1M active users across 6 major platforms.",
            "Competitive Intelligence": "Amazon leads with 35% market share, followed by Flipkart at 28%. Price variations of up to 15% observed across platforms. Customer price sensitivity highest in electronics category with 78% using comparison tools."
        }
        
        col1, col2, col3 = st.columns(3)
        
        for i, (title, content) in enumerate(sample_docs.items()):
            with [col1, col2, col3][i]:
                if st.button(f"Load {title}"):
                    st.session_state['sample_doc'] = content
                    st.rerun()
        
        # Display loaded sample
        if 'sample_doc' in st.session_state:
            st.text_area("Loaded Sample Document:", value=st.session_state['sample_doc'], height=150, key="sample_display")

    def render_platform_status(self):
        """Render platform status and configuration page."""
        st.header("⚙️ Platform Status & Configuration")
        
        # System status
        st.subheader("🖥️ System Status")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.markdown("### Core Services")
            services = [
                ("Data Loader", "✅", "Online"),
                ("Forecasting Engine", "✅", "Online"),
                ("Pricing Engine", "✅", "Online"),
                ("Market Copilot", "✅", "Online"),
                ("Document Parser", "✅", "Online"),
                ("API Gateway", "✅", "Online")
            ]
            
            for service, status, description in services:
                st.success(f"{status} {service}: {description}")
        
        with col2:
            st.markdown("### Data Status")
            
            # Check data availability
            data_status = [
                ("Gold Prices", len(self.gold_data) > 0, len(self.gold_data)),
                ("Silver Prices", len(self.silver_data) > 0, len(self.silver_data)),
                ("ETF Prices", len(self.etf_data) > 0, len(self.etf_data)),
                ("Product Catalog", len(self.products) > 0, len(self.products))
            ]
            
            for data_type, available, count in data_status:
                if available:
                    st.success(f"✅ {data_type}: {count} records")
                else:
                    st.error(f"❌ {data_type}: No data")
        
        with col3:
            st.markdown("### Integration Status")
            
            # Check integration status
            integrations = [
                ("Amazon Bedrock", "🔧", "Framework Ready"),
                ("Amazon Q", "⚠️", "Optional Extension"),
                ("FastAPI", "✅", "Running"),
                ("Streamlit Dashboard", "✅", "Active")
            ]
            
            for integration, status, description in integrations:
                if status == "✅":
                    st.success(f"{status} {integration}: {description}")
                elif status == "🔧":
                    st.info(f"{status} {integration}: {description}")
                else:
                    st.warning(f"{status} {integration}: {description}")
        
        # Configuration
        st.markdown("---")
        st.subheader("🔧 Configuration")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("### API Configuration")
            
            api_host = st.text_input("API Host:", value="localhost")
            api_port = st.number_input("API Port:", value=8000, min_value=1000, max_value=9999)
            
            if st.button("Test API Connection"):
                try:
                    response = requests.get(f"http://{api_host}:{api_port}/health", timeout=5)
                    if response.status_code == 200:
                        st.success("✅ API connection successful")
                    else:
                        st.error(f"❌ API returned status code: {response.status_code}")
                except Exception as e:
                    st.error(f"❌ API connection failed: {str(e)}")
        
        with col2:
            st.markdown("### Model Configuration")
            
            default_horizon = st.number_input("Default Forecast Horizon:", value=30, min_value=1, max_value=365)
            confidence_level = st.slider("Confidence Level:", 0.80, 0.99, 0.95, 0.01)
            
            st.write(f"**Current Settings:**")
            st.write(f"- Forecast Horizon: {default_horizon} days")
            st.write(f"- Confidence Level: {confidence_level:.2f}")
        
        # Performance metrics
        st.markdown("---")
        st.subheader("📈 Performance Metrics")
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Data Load Time", "0.5s", delta="-0.1s")
        
        with col2:
            st.metric("Avg Response Time", "1.2s", delta="+0.2s")
        
        with col3:
            st.metric("Cache Hit Rate", "85%", delta="+5%")
        
        with col4:
            st.metric("Error Rate", "0.1%", delta="-0.05%")
        
        # Logs
        st.markdown("---")
        st.subheader("📋 Recent Logs")
        
        # Simulate log entries
        log_entries = [
            {"timestamp": "2024-01-15 10:30:15", "level": "INFO", "message": "Price comparison completed for P006"},
            {"timestamp": "2024-01-15 10:29:45", "level": "INFO", "message": "Forecast generated for GOLD (30 days)"},
            {"timestamp": "2024-01-15 10:29:12", "level": "INFO", "message": "Market copilot query processed"},
            {"timestamp": "2024-01-15 10:28:33", "level": "INFO", "message": "Data loader initialized successfully"},
            {"timestamp": "2024-01-15 10:28:01", "level": "INFO", "message": "Dashboard started"}
        ]
        
        log_df = pd.DataFrame(log_entries)
        st.dataframe(log_df, use_container_width=True)

    def render_amazon_q_integration(self):
        """Render Amazon Q integration status and demo."""
        st.header("🔧 Amazon Q Optional Integration")
        
        # Integration overview
        st.markdown("""
        Amazon Q integration provides advanced business reasoning, seller insights, and large PDF analysis capabilities.
        This is an **OPTIONAL** extension that enhances the platform with enterprise-grade AI capabilities.
        
        **⚠️ Important**: Amazon Q integration is **NOT executed in local builds** and requires AWS credentials and Amazon Q access.
        """)
        
        # Status check
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("📊 Integration Status")
            
            capabilities = self.amazon_q_manager.get_capabilities()
            
            # Display status
            status = capabilities.get('integration_status', {})
            
            st.write(f"**Enabled:** {'✅ Yes' if status.get('enabled') else '❌ No'}")
            st.write(f"**AWS Credentials Required:** {'✅ Yes' if status.get('aws_credentials_required') else '❌ No'}")
            st.write(f"**Amazon Q Access Required:** {'✅ Yes' if status.get('amazon_q_access_required') else '❌ No'}")
            st.write(f"**Local Build Compatible:** {'✅ Yes' if status.get('local_build_compatible') else '❌ No'}")
            
            if not status.get('enabled'):
                st.info("Amazon Q integration is currently disabled for local builds")
        
        with col2:
            st.subheader("🎯 Available Capabilities")
            
            for capability_name, capability_info in capabilities.items():
                if capability_name != 'integration_status':
                    with st.expander(f"{capability_name.replace('_', ' ').title()}"):
                        st.write(f"**Description:** {capability_info.get('description', 'N/A')}")
                        st.write("**Capabilities:**")
                        for cap in capability_info.get('capabilities', []):
                            st.write(f"• {cap}")
                        st.write(f"**Status:** {capability_info.get('status', 'Unknown')}")
        
        # Demo section
        st.markdown("---")
        st.subheader("🚀 Demo Mode (Mock Responses)")
        st.markdown("Try the Amazon Q capabilities with mock responses to see how they would work when enabled.")
        
        # Business reasoning demo
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("### 🧠 Business Reasoning")
            
            if st.button("Analyze Market Strategy"):
                with st.spinner("Analyzing market strategy..."):
                    market_data = {
                        'platform_prices': {'Amazon': 17999, 'Flipkart': 18490, 'Zepto': 16999},
                        'product_category': 'electronics',
                        'market_segment': 'home_appliances'
                    }
                    
                    analysis = self.amazon_q_manager.business_reasoning.analyze_market_strategy(market_data)
                    
                    st.success("Analysis Complete!")
                    
                    # Display results
                    st.write(f"**Strategy Type:** {analysis['strategy_type']}")
                    st.write(f"**Market Position:** {analysis['market_position']}")
                    st.write(f"**Confidence Score:** {analysis['confidence_score']:.2f}")
                    
                    with st.expander("Key Insights"):
                        for insight in analysis['key_insights']:
                            st.write(f"• {insight}")
                    
                    with st.expander("Strategic Recommendations"):
                        for rec in analysis['strategic_recommendations']:
                            st.write(f"• {rec}")
                    
                    st.warning("⚠️ This is a mock response for demonstration purposes")
        
        with col2:
            st.markdown("### 📄 PDF Analysis")
            
            if st.button("Analyze Sample Report"):
                with st.spinner("Analyzing PDF document..."):
                    analysis = self.amazon_q_manager.pdf_analyzer.analyze_large_pdf("sample_report.pdf")
                    
                    st.success("Analysis Complete!")
                    
                    # Display results
                    st.write(f"**Executive Summary:**")
                    st.write(analysis['executive_summary'])
                    
                    with st.expander("Key Insights"):
                        for insight in analysis['key_insights']:
                            st.write(f"• {insight}")
                    
                    with st.expander("Market Trends"):
                        for trend in analysis['market_trends']:
                            st.write(f"• {trend}")
                    
                    with st.expander("Financial Highlights"):
                        for key, value in analysis['financial_highlights'].items():
                            st.write(f"• **{key.replace('_', ' ').title()}:** {value}")
                    
                    st.warning("⚠️ This is a mock response for demonstration purposes")
        
        # Business query demo
        st.markdown("### 💼 Business Intelligence Query")
        
        query_input = st.text_input(
            "Ask a business question:",
            placeholder="What pricing strategy should we adopt for electronics?"
        )
        
        if st.button("Process Query") and query_input:
            with st.spinner("Processing business query..."):
                response = self.amazon_q_manager.process_business_query(query_input)
                
                st.write("**Response:**")
                st.info(response['response'])
                
                if 'capabilities_available' in response:
                    with st.expander("Available Capabilities"):
                        st.json(response['capabilities_available'])
        
        # Configuration section
        st.markdown("---")
        st.subheader("⚙️ Configuration (Future)")
        
        st.markdown("""
        When Amazon Q integration is enabled, the following configuration will be required:
        
        ```bash
        # Environment variables
        export AWS_ACCESS_KEY_ID="your_access_key"
        export AWS_SECRET_ACCESS_KEY="your_secret_key"
        export AMAZON_Q_APPLICATION_ID="your_q_app_id"
        export AMAZON_Q_REGION="us-east-1"
        ```
        
        **API Endpoints (Future):**
        - `POST /api/v1/amazon-q/business-analysis`
        - `POST /api/v1/amazon-q/market-strategy`
        - `POST /api/v1/amazon-q/seller-analysis`
        - `POST /api/v1/amazon-q/pdf-analysis`
        """)

    def run(self):
        """Run the dashboard application."""
        # Render sidebar and get selected page
        page = self.render_sidebar()
        
        # Render selected page
        if page == "Dashboard Overview":
            self.render_overview()
        elif page == "Price Forecasting":
            self.render_forecasting()
        elif page == "Competitive Pricing":
            self.render_competitive_pricing()
        elif page == "Market Copilot":
            self.render_market_copilot()
        elif page == "Document Analysis":
            self.render_document_analysis()
        elif page == "Platform Status":
            self.render_platform_status()
        elif page == "Amazon Q Integration":
            self.render_amazon_q_integration()

# Main execution
if __name__ == "__main__":
    # Initialize and run dashboard
    dashboard = DashboardApp()
    dashboard.run()