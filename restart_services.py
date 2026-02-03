#!/usr/bin/env python3
"""
Restart Services Script
======================

This script helps restart the AI Retail Intelligence services to pick up
the updated Indian price data.
"""

import subprocess
import sys
import time
import os
import signal
from datetime import datetime

def print_header():
    """Print script header."""
    print("🔄 AI Retail Intelligence - Service Restart")
    print("=" * 50)
    print(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 50)

def check_data_files():
    """Check if data files exist and show current prices."""
    print("\n📊 Checking Data Files...")
    
    data_files = [
        ("data/gold_prices.csv", "Gold"),
        ("data/silver_prices.csv", "Silver"), 
        ("data/etf_prices.csv", "ETF")
    ]
    
    for file_path, asset_type in data_files:
        if os.path.exists(file_path):
            try:
                import pandas as pd
                df = pd.read_csv(file_path)
                if not df.empty:
                    latest_price = df['close'].iloc[-1]
                    latest_date = df['date'].iloc[-1]
                    print(f"  ✅ {asset_type}: ₹{latest_price:,.2f} ({latest_date})")
                else:
                    print(f"  ⚠️ {asset_type}: File exists but empty")
            except Exception as e:
                print(f"  ❌ {asset_type}: Error reading file - {str(e)}")
        else:
            print(f"  ❌ {asset_type}: File not found - {file_path}")

def kill_existing_processes():
    """Kill any existing Python processes running the services."""
    print("\n🛑 Stopping Existing Services...")
    
    try:
        # Kill any existing main.py processes
        subprocess.run(["pkill", "-f", "main.py"], capture_output=True)
        print("  ✅ Stopped API server processes")
    except:
        print("  ℹ️ No API server processes found")
    
    try:
        # Kill any existing dashboard processes
        subprocess.run(["pkill", "-f", "dashboard/app.py"], capture_output=True)
        subprocess.run(["pkill", "-f", "streamlit"], capture_output=True)
        print("  ✅ Stopped dashboard processes")
    except:
        print("  ℹ️ No dashboard processes found")
    
    # Wait a moment for processes to terminate
    time.sleep(2)

def start_api_server():
    """Start the API server."""
    print("\n🚀 Starting API Server...")
    
    try:
        # Start API server in background
        process = subprocess.Popen(
            [sys.executable, "main.py", "--mode", "server"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        
        # Wait a moment for server to start
        time.sleep(3)
        
        # Check if process is still running
        if process.poll() is None:
            print("  ✅ API Server started successfully")
            print("  📡 Running on: http://localhost:8000")
            print("  📋 API Docs: http://localhost:8000/docs")
            return process
        else:
            stdout, stderr = process.communicate()
            print("  ❌ API Server failed to start")
            if stderr:
                print(f"  Error: {stderr.decode()}")
            return None
            
    except Exception as e:
        print(f"  ❌ Failed to start API server: {str(e)}")
        return None

def start_dashboard():
    """Start the dashboard."""
    print("\n🎨 Starting Dashboard...")
    
    try:
        # Start dashboard in background
        process = subprocess.Popen(
            [sys.executable, "-m", "streamlit", "run", "dashboard/app.py", "--server.port", "8501"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        
        # Wait a moment for dashboard to start
        time.sleep(5)
        
        # Check if process is still running
        if process.poll() is None:
            print("  ✅ Dashboard started successfully")
            print("  🌐 Running on: http://localhost:8501")
            return process
        else:
            stdout, stderr = process.communicate()
            print("  ❌ Dashboard failed to start")
            if stderr:
                print(f"  Error: {stderr.decode()}")
            return None
            
    except Exception as e:
        print(f"  ❌ Failed to start dashboard: {str(e)}")
        return None

def verify_services():
    """Verify that services are running."""
    print("\n🔍 Verifying Services...")
    
    try:
        import requests
        
        # Test API server
        try:
            response = requests.get("http://localhost:8000/health", timeout=5)
            if response.status_code == 200:
                print("  ✅ API Server: Healthy")
            else:
                print(f"  ⚠️ API Server: Status {response.status_code}")
        except:
            print("  ❌ API Server: Not responding")
        
        # Test dashboard (just check if port is open)
        try:
            response = requests.get("http://localhost:8501", timeout=5)
            if response.status_code == 200:
                print("  ✅ Dashboard: Accessible")
            else:
                print("  ⚠️ Dashboard: May still be loading")
        except:
            print("  ⚠️ Dashboard: Still starting up (this is normal)")
            
    except ImportError:
        print("  ℹ️ Requests not available, skipping service verification")

def main():
    """Main function."""
    print_header()
    
    # Check data files
    check_data_files()
    
    # Kill existing processes
    kill_existing_processes()
    
    # Start services
    api_process = start_api_server()
    dashboard_process = start_dashboard()
    
    # Verify services
    verify_services()
    
    # Final instructions
    print("\n" + "=" * 50)
    print("🎉 Service Restart Complete!")
    print("=" * 50)
    
    if api_process and dashboard_process:
        print("✅ Both services are running")
        print("\n📋 Next Steps:")
        print("1. Open dashboard: http://localhost:8501")
        print("2. Check Dashboard Overview for updated Indian prices")
        print("3. Gold should show ~₹70,495 per 10g")
        print("4. Silver should show ~₹82,477 per kg")
        print("5. Try Market Copilot: 'What is the current gold price in India?'")
        
        print("\n🛑 To stop services later:")
        print("  • Press Ctrl+C in the terminals")
        print("  • Or run: python restart_services.py --stop")
        
    else:
        print("⚠️ Some services failed to start")
        print("\n🔧 Manual Steps:")
        print("1. Terminal 1: python main.py --mode server")
        print("2. Terminal 2: streamlit run dashboard/app.py")
        print("3. Open: http://localhost:8501")
    
    print("\n💡 If prices still show old data:")
    print("  • Click the '🔄 Refresh Data' button in dashboard sidebar")
    print("  • Or refresh your browser (F5)")

def stop_services():
    """Stop all services."""
    print("🛑 Stopping All Services...")
    kill_existing_processes()
    print("✅ All services stopped")

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--stop":
        stop_services()
    else:
        main()