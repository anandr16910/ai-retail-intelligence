#!/usr/bin/env python3
"""
Dashboard Launcher Script
========================

Convenient script to launch the AI Retail Intelligence dashboard.
This script handles the setup and launches both the main platform API
and the Streamlit dashboard.

Usage:
    python run_dashboard.py [--api-only] [--dashboard-only] [--port PORT]
"""

import subprocess
import sys
import time
import os
import argparse
import signal
import threading
from pathlib import Path

class DashboardLauncher:
    """Handles launching and managing the dashboard and API processes."""
    
    def __init__(self):
        self.api_process = None
        self.dashboard_process = None
        self.project_root = Path(__file__).parent.parent
        
    def check_dependencies(self):
        """Check if required dependencies are installed."""
        try:
            import streamlit
            import plotly
            import requests
            print("✅ Dashboard dependencies verified")
            return True
        except ImportError as e:
            print(f"❌ Missing dependency: {e}")
            print("Please install dashboard requirements:")
            print("pip install -r dashboard/requirements.txt")
            return False
    
    def check_platform_dependencies(self):
        """Check if platform dependencies are available."""
        try:
            sys.path.append(str(self.project_root))
            from src.competitive_pricing import CompetitivePricingEngine
            from src.forecasting_model import PriceForecastingEngine
            print("✅ Platform dependencies verified")
            return True
        except ImportError as e:
            print(f"❌ Platform dependency missing: {e}")
            print("Please ensure the main platform is properly installed:")
            print("pip install -r requirements.txt")
            return False
    
    def start_api(self, port=8000):
        """Start the main platform API."""
        print(f"🚀 Starting AI Retail Intelligence API on port {port}...")
        
        try:
            # Change to project root directory
            os.chdir(self.project_root)
            
            # Start the API server
            cmd = [sys.executable, "main.py", "--mode", "server", "--port", str(port)]
            self.api_process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            
            # Wait a moment for the server to start
            time.sleep(3)
            
            # Check if process is still running
            if self.api_process.poll() is None:
                print(f"✅ API server started successfully on http://localhost:{port}")
                return True
            else:
                stdout, stderr = self.api_process.communicate()
                print(f"❌ API server failed to start")
                print(f"Error: {stderr}")
                return False
                
        except Exception as e:
            print(f"❌ Error starting API server: {e}")
            return False
    
    def start_dashboard(self, dashboard_port=8501):
        """Start the Streamlit dashboard."""
        print(f"🎨 Starting Streamlit dashboard on port {dashboard_port}...")
        
        try:
            # Change to dashboard directory
            dashboard_dir = self.project_root / "dashboard"
            os.chdir(dashboard_dir)
            
            # Start Streamlit
            cmd = [
                sys.executable, "-m", "streamlit", "run", "app.py",
                "--server.port", str(dashboard_port),
                "--server.headless", "true",
                "--browser.gatherUsageStats", "false"
            ]
            
            self.dashboard_process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            
            # Wait for dashboard to start
            time.sleep(5)
            
            if self.dashboard_process.poll() is None:
                print(f"✅ Dashboard started successfully on http://localhost:{dashboard_port}")
                return True
            else:
                stdout, stderr = self.dashboard_process.communicate()
                print(f"❌ Dashboard failed to start")
                print(f"Error: {stderr}")
                return False
                
        except Exception as e:
            print(f"❌ Error starting dashboard: {e}")
            return False
    
    def wait_for_api(self, port=8000, timeout=30):
        """Wait for API to be ready."""
        import requests
        
        print("⏳ Waiting for API to be ready...")
        start_time = time.time()
        
        while time.time() - start_time < timeout:
            try:
                response = requests.get(f"http://localhost:{port}/health", timeout=2)
                if response.status_code == 200:
                    print("✅ API is ready")
                    return True
            except requests.exceptions.RequestException:
                pass
            
            time.sleep(1)
        
        print("❌ API failed to become ready within timeout")
        return False
    
    def cleanup(self):
        """Clean up processes on exit."""
        print("\n🧹 Cleaning up processes...")
        
        if self.dashboard_process:
            try:
                self.dashboard_process.terminate()
                self.dashboard_process.wait(timeout=5)
                print("✅ Dashboard process terminated")
            except subprocess.TimeoutExpired:
                self.dashboard_process.kill()
                print("⚠️ Dashboard process killed (forced)")
            except Exception as e:
                print(f"⚠️ Error terminating dashboard: {e}")
        
        if self.api_process:
            try:
                self.api_process.terminate()
                self.api_process.wait(timeout=5)
                print("✅ API process terminated")
            except subprocess.TimeoutExpired:
                self.api_process.kill()
                print("⚠️ API process killed (forced)")
            except Exception as e:
                print(f"⚠️ Error terminating API: {e}")
    
    def signal_handler(self, signum, frame):
        """Handle interrupt signals."""
        print(f"\n🛑 Received signal {signum}, shutting down...")
        self.cleanup()
        sys.exit(0)
    
    def run(self, api_only=False, dashboard_only=False, api_port=8000, dashboard_port=8501):
        """Run the dashboard launcher."""
        # Set up signal handlers
        signal.signal(signal.SIGINT, self.signal_handler)
        signal.signal(signal.SIGTERM, self.signal_handler)
        
        print("🛒 AI Retail Intelligence Dashboard Launcher")
        print("=" * 50)
        
        # Check dependencies
        if not dashboard_only and not self.check_platform_dependencies():
            return False
        
        if not api_only and not self.check_dependencies():
            return False
        
        try:
            # Start API if needed
            if not dashboard_only:
                if not self.start_api(api_port):
                    return False
                
                if not self.wait_for_api(api_port):
                    return False
            
            # Start dashboard if needed
            if not api_only:
                if not self.start_dashboard(dashboard_port):
                    return False
            
            # Print success message
            print("\n🎉 Launch successful!")
            print("=" * 50)
            
            if not dashboard_only:
                print(f"📡 API Server: http://localhost:{api_port}")
                print(f"📚 API Docs: http://localhost:{api_port}/docs")
            
            if not api_only:
                print(f"🎨 Dashboard: http://localhost:{dashboard_port}")
            
            print("\nPress Ctrl+C to stop all services")
            print("=" * 50)
            
            # Keep running until interrupted
            try:
                while True:
                    # Check if processes are still running
                    if not dashboard_only and (self.api_process and self.api_process.poll() is not None):
                        print("❌ API process has stopped unexpectedly")
                        break
                    
                    if not api_only and (self.dashboard_process and self.dashboard_process.poll() is not None):
                        print("❌ Dashboard process has stopped unexpectedly")
                        break
                    
                    time.sleep(1)
                    
            except KeyboardInterrupt:
                print("\n🛑 Shutdown requested by user")
            
            return True
            
        except Exception as e:
            print(f"❌ Unexpected error: {e}")
            return False
        
        finally:
            self.cleanup()

def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Launch AI Retail Intelligence Dashboard",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python run_dashboard.py                    # Start both API and dashboard
  python run_dashboard.py --api-only        # Start only the API server
  python run_dashboard.py --dashboard-only  # Start only the dashboard
  python run_dashboard.py --port 8080       # Use custom API port
        """
    )
    
    parser.add_argument(
        "--api-only",
        action="store_true",
        help="Start only the API server"
    )
    
    parser.add_argument(
        "--dashboard-only",
        action="store_true",
        help="Start only the dashboard (requires API to be running separately)"
    )
    
    parser.add_argument(
        "--api-port",
        type=int,
        default=8000,
        help="Port for the API server (default: 8000)"
    )
    
    parser.add_argument(
        "--dashboard-port",
        type=int,
        default=8501,
        help="Port for the dashboard (default: 8501)"
    )
    
    args = parser.parse_args()
    
    # Validate arguments
    if args.api_only and args.dashboard_only:
        print("❌ Cannot specify both --api-only and --dashboard-only")
        return 1
    
    # Create and run launcher
    launcher = DashboardLauncher()
    success = launcher.run(
        api_only=args.api_only,
        dashboard_only=args.dashboard_only,
        api_port=args.api_port,
        dashboard_port=args.dashboard_port
    )
    
    return 0 if success else 1

if __name__ == "__main__":
    sys.exit(main())