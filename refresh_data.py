#!/usr/bin/env python3
"""
Refresh Data Script
==================

This script forces the platform to reload data and clear any caches.
Use this when you've updated the CSV files but the dashboard isn't showing changes.

Usage:
    python refresh_data.py
"""

import requests
import time
import sys

def check_api_status():
    """Check if API server is running."""
    try:
        response = requests.get("http://localhost:8000/health", timeout=5)
        return response.status_code == 200
    except:
        return False

def reload_data_via_api():
    """Try to reload data via API endpoint."""
    try:
        response = requests.post("http://localhost:8000/api/v1/data/reload", timeout=10)
        if response.status_code == 200:
            print("✅ Data reloaded via API")
            return True
        else:
            print(f"⚠️ API reload returned status: {response.status_code}")
            return False
    except Exception as e:
        print(f"⚠️ API reload failed: {str(e)}")
        return False

def get_current_prices():
    """Get current prices from API."""
    try:
        response = requests.get("http://localhost:8000/api/v1/data/status", timeout=5)
        if response.status_code == 200:
            data = response.json()
            print("📊 Current API Data Status:")
            print(f"  {data}")
            return data
        else:
            print(f"⚠️ Could not get data status: {response.status_code}")
            return None
    except Exception as e:
        print(f"⚠️ Error getting data status: {str(e)}")
        return None

def main():
    """Main refresh function."""
    print("🔄 Refreshing Platform Data")
    print("=" * 30)
    
    # Check if API is running
    if not check_api_status():
        print("❌ API server is not running!")
        print("Please start it with: python main.py --mode server")
        return 1
    
    print("✅ API server is running")
    
    # Try to reload data
    print("\n🔄 Attempting to reload data...")
    if reload_data_via_api():
        print("✅ Data reload successful")
    else:
        print("⚠️ API reload not available, data will refresh on next restart")
    
    # Get current status
    print("\n📊 Checking current data...")
    get_current_prices()
    
    print("\n💡 Next steps:")
    print("1. Refresh your dashboard browser tab (F5 or Ctrl+R)")
    print("2. If still no change, restart API server:")
    print("   - Stop: Ctrl+C in API terminal")
    print("   - Start: python main.py --mode server")
    print("3. Then refresh dashboard again")
    
    return 0

if __name__ == "__main__":
    sys.exit(main())