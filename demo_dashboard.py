#!/usr/bin/env python3
"""
Dashboard Demo Script
====================

Demonstration script for the AI Retail Intelligence web dashboard.
This script showcases the dashboard capabilities and provides a quick demo.

Usage:
    python demo_dashboard.py [--screenshots] [--auto-demo]
"""

import subprocess
import sys
import time
import webbrowser
import argparse
from pathlib import Path

def print_banner():
    """Print demo banner."""
    print("🛒 AI Retail Intelligence Dashboard Demo")
    print("=" * 50)
    print("This demo showcases the comprehensive web dashboard")
    print("for the AI Retail Intelligence platform.")
    print("=" * 50)

def check_requirements():
    """Check if dashboard requirements are met."""
    print("🔍 Checking requirements...")
    
    # Check if main platform is available
    try:
        from src.competitive_pricing import CompetitivePricingEngine
        print("✅ Main platform available")
    except ImportError:
        print("❌ Main platform not found. Please ensure you're in the project root.")
        return False
    
    # Check dashboard dependencies
    try:
        import streamlit
        import plotly
        print("✅ Dashboard dependencies available")
    except ImportError:
        print("❌ Dashboard dependencies missing. Installing...")
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "dashboard/requirements.txt"])
            print("✅ Dashboard dependencies installed")
        except subprocess.CalledProcessError:
            print("❌ Failed to install dashboard dependencies")
            return False
    
    return True

def start_demo_services():
    """Start the demo services."""
    print("\n🚀 Starting demo services...")
    
    # Start API server
    print("Starting API server...")
    api_process = subprocess.Popen([
        sys.executable, "main.py", "--mode", "server", "--port", "8000"
    ], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    
    # Wait for API to start
    time.sleep(5)
    
    # Start dashboard
    print("Starting dashboard...")
    dashboard_process = subprocess.Popen([
        sys.executable, "-m", "streamlit", "run", "dashboard/app.py",
        "--server.port", "8501",
        "--server.headless", "true",
        "--browser.gatherUsageStats", "false"
    ], stdout=subprocess.PIPE, stderr=subprocess.PIPE, cwd=".")
    
    # Wait for dashboard to start
    time.sleep(8)
    
    return api_process, dashboard_process

def open_dashboard():
    """Open dashboard in browser."""
    print("\n🌐 Opening dashboard in browser...")
    dashboard_url = "http://localhost:8501"
    
    try:
        webbrowser.open(dashboard_url)
        print(f"✅ Dashboard opened: {dashboard_url}")
    except Exception as e:
        print(f"⚠️ Could not open browser automatically: {e}")
        print(f"Please manually open: {dashboard_url}")

def demo_walkthrough():
    """Provide demo walkthrough instructions."""
    print("\n📋 Dashboard Demo Walkthrough")
    print("=" * 40)
    
    features = [
        ("🏠 Dashboard Overview", [
            "View real-time metrics and key performance indicators",
            "Explore interactive price trend charts",
            "Check platform comparison analytics",
            "Review recent activity and best deals"
        ]),
        
        ("📈 Price Forecasting", [
            "Select Gold, Silver, or ETF for forecasting",
            "Adjust forecast horizon (1-90 days)",
            "Choose model type (moving average or random forest)",
            "Generate interactive forecast with confidence intervals"
        ]),
        
        ("💰 Competitive Pricing", [
            "Search for products in the catalog",
            "Compare prices across 6 major platforms",
            "View potential savings and recommendations",
            "Explore best deals with highest savings"
        ]),
        
        ("🤖 Market Copilot", [
            "Chat with AI assistant about market trends",
            "Try quick action buttons for common queries",
            "Ask about price comparisons and forecasts",
            "Get contextual market insights and recommendations"
        ]),
        
        ("📄 Document Analysis", [
            "Upload financial documents or paste text",
            "Extract entities and market insights",
            "View confidence scores and analysis results",
            "Try sample documents for testing"
        ]),
        
        ("⚙️ Platform Status", [
            "Monitor system health and service status",
            "Check data availability and record counts",
            "View performance metrics and logs",
            "Configure API settings and parameters"
        ]),
        
        ("🔧 Amazon Q Integration", [
            "Explore optional Amazon Q capabilities",
            "Try demo mode with mock responses",
            "Learn about business reasoning features",
            "Understand future integration possibilities"
        ])
    ]
    
    for feature, steps in features:
        print(f"\n{feature}:")
        for step in steps:
            print(f"  • {step}")
    
    print("\n💡 Demo Tips:")
    print("  • Try the Godrej fridge comparison for a real scenario")
    print("  • Use the Market Copilot for natural language queries")
    print("  • Explore the interactive charts with zoom and pan")
    print("  • Check the platform status for system monitoring")

def sample_queries():
    """Provide sample queries for testing."""
    print("\n🔍 Sample Queries to Try")
    print("=" * 30)
    
    queries = [
        "Compare prices for Godrej Single Door Fridge",
        "What are the current gold price trends?",
        "Show me the best deals available",
        "Give me a market summary",
        "What's the forecast for silver prices?",
        "Which platform has the lowest prices?",
        "How much can I save on electronics?",
        "What are the top 5 deals today?"
    ]
    
    for i, query in enumerate(queries, 1):
        print(f"  {i}. {query}")

def cleanup_demo(api_process, dashboard_process):
    """Clean up demo processes."""
    print("\n🧹 Cleaning up demo...")
    
    try:
        if dashboard_process:
            dashboard_process.terminate()
            dashboard_process.wait(timeout=5)
            print("✅ Dashboard stopped")
    except:
        print("⚠️ Dashboard cleanup issue")
    
    try:
        if api_process:
            api_process.terminate()
            api_process.wait(timeout=5)
            print("✅ API server stopped")
    except:
        print("⚠️ API server cleanup issue")

def main():
    """Main demo function."""
    parser = argparse.ArgumentParser(description="AI Retail Intelligence Dashboard Demo")
    parser.add_argument("--auto-demo", action="store_true", help="Run automated demo")
    parser.add_argument("--screenshots", action="store_true", help="Generate screenshots (future)")
    args = parser.parse_args()
    
    print_banner()
    
    # Check requirements
    if not check_requirements():
        print("\n❌ Requirements not met. Please fix issues and try again.")
        return 1
    
    # Start services
    try:
        api_process, dashboard_process = start_demo_services()
        
        # Open dashboard
        open_dashboard()
        
        # Provide walkthrough
        demo_walkthrough()
        sample_queries()
        
        print("\n🎉 Demo is ready!")
        print("=" * 20)
        print("Dashboard: http://localhost:8501")
        print("API Docs:  http://localhost:8000/docs")
        print("\nPress Ctrl+C to stop the demo")
        
        # Keep running
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            print("\n🛑 Demo stopped by user")
        
    except Exception as e:
        print(f"❌ Demo failed: {e}")
        return 1
    
    finally:
        cleanup_demo(api_process, dashboard_process)
    
    print("\n✅ Demo completed successfully!")
    return 0

if __name__ == "__main__":
    sys.exit(main())