#!/usr/bin/env python3
"""
Real-time Features Test Script
==============================

This script tests the WebSocket server and client functionality.

Usage:
    python dashboard/test_realtime.py
"""

import sys
import os
import time
import threading

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dashboard.realtime_client import RealtimeClient


def test_connection():
    """Test basic connection."""
    print("=" * 60)
    print("Test 1: Basic Connection")
    print("=" * 60)
    
    client = RealtimeClient('http://localhost:5000')
    
    print("Attempting to connect...")
    if client.connect():
        print("✅ Connection successful")
        time.sleep(2)
        
        if client.is_connected():
            print("✅ Connection verified")
        else:
            print("❌ Connection verification failed")
        
        client.disconnect()
        print("✅ Disconnection successful")
        return True
    else:
        print("❌ Connection failed")
        return False


def test_subscription():
    """Test subscription to data streams."""
    print("\n" + "=" * 60)
    print("Test 2: Subscription Management")
    print("=" * 60)
    
    client = RealtimeClient('http://localhost:5000')
    
    if not client.connect():
        print("❌ Connection failed")
        return False
    
    print("✅ Connected")
    time.sleep(1)
    
    # Test subscription
    print("Subscribing to price_updates...")
    if client.subscribe('price_updates'):
        print("✅ Subscription successful")
    else:
        print("❌ Subscription failed")
        return False
    
    time.sleep(2)
    
    # Test unsubscription
    print("Unsubscribing from price_updates...")
    if client.unsubscribe('price_updates'):
        print("✅ Unsubscription successful")
    else:
        print("❌ Unsubscription failed")
    
    client.disconnect()
    return True


def test_data_reception():
    """Test receiving data updates."""
    print("\n" + "=" * 60)
    print("Test 3: Data Reception")
    print("=" * 60)
    
    client = RealtimeClient('http://localhost:5000')
    
    if not client.connect():
        print("❌ Connection failed")
        return False
    
    print("✅ Connected")
    
    # Register callback
    received_data = {'count': 0}
    
    def on_price_update(data):
        received_data['count'] += 1
        print(f"📊 Received price update #{received_data['count']}")
        if 'data' in data:
            for asset, price_data in data['data'].items():
                if 'price' in price_data:
                    print(f"   {asset.upper()}: ₹{price_data['price']:.2f}")
    
    client.register_callback('price_update', on_price_update)
    
    # Subscribe to price updates
    print("Subscribing to price_updates...")
    client.subscribe('price_updates')
    
    # Wait for updates
    print("Waiting for data updates (15 seconds)...")
    time.sleep(15)
    
    if received_data['count'] > 0:
        print(f"✅ Received {received_data['count']} updates")
        success = True
    else:
        print("❌ No updates received")
        success = False
    
    client.disconnect()
    return success


def test_reconnection():
    """Test automatic reconnection."""
    print("\n" + "=" * 60)
    print("Test 4: Reconnection (Manual)")
    print("=" * 60)
    
    client = RealtimeClient('http://localhost:5000')
    
    if not client.connect():
        print("❌ Initial connection failed")
        return False
    
    print("✅ Initial connection successful")
    time.sleep(1)
    
    # Disconnect
    print("Disconnecting...")
    client.disconnect()
    time.sleep(1)
    
    if not client.is_connected():
        print("✅ Disconnection verified")
    
    # Reconnect
    print("Reconnecting...")
    if client.connect():
        print("✅ Reconnection successful")
        client.disconnect()
        return True
    else:
        print("❌ Reconnection failed")
        return False


def test_ping():
    """Test ping/pong health check."""
    print("\n" + "=" * 60)
    print("Test 5: Health Check (Ping/Pong)")
    print("=" * 60)
    
    client = RealtimeClient('http://localhost:5000')
    
    if not client.connect():
        print("❌ Connection failed")
        return False
    
    print("✅ Connected")
    time.sleep(1)
    
    # Send ping
    print("Sending ping...")
    client.ping()
    time.sleep(1)
    
    print("✅ Ping sent (check server logs for pong)")
    
    client.disconnect()
    return True


def test_status():
    """Test status request."""
    print("\n" + "=" * 60)
    print("Test 6: Status Request")
    print("=" * 60)
    
    client = RealtimeClient('http://localhost:5000')
    
    if not client.connect():
        print("❌ Connection failed")
        return False
    
    print("✅ Connected")
    time.sleep(1)
    
    # Request status
    print("Requesting server status...")
    client.get_status()
    time.sleep(1)
    
    print("✅ Status request sent (check server logs for response)")
    
    client.disconnect()
    return True


def run_all_tests():
    """Run all tests."""
    print("\n" + "=" * 60)
    print("Real-time Features Test Suite")
    print("=" * 60)
    print("\nMake sure the WebSocket server is running:")
    print("  python dashboard/run_websocket_server.py")
    print("\nPress Enter to continue or Ctrl+C to cancel...")
    
    try:
        input()
    except KeyboardInterrupt:
        print("\n\nTests cancelled")
        return
    
    results = []
    
    # Run tests
    results.append(("Connection", test_connection()))
    results.append(("Subscription", test_subscription()))
    results.append(("Data Reception", test_data_reception()))
    results.append(("Reconnection", test_reconnection()))
    results.append(("Health Check", test_ping()))
    results.append(("Status Request", test_status()))
    
    # Print summary
    print("\n" + "=" * 60)
    print("Test Summary")
    print("=" * 60)
    
    passed = 0
    failed = 0
    
    for test_name, result in results:
        status = "✅ PASSED" if result else "❌ FAILED"
        print(f"{test_name:20s} {status}")
        if result:
            passed += 1
        else:
            failed += 1
    
    print("=" * 60)
    print(f"Total: {len(results)} tests")
    print(f"Passed: {passed}")
    print(f"Failed: {failed}")
    print("=" * 60)
    
    if failed == 0:
        print("\n🎉 All tests passed!")
    else:
        print(f"\n⚠️  {failed} test(s) failed")


if __name__ == '__main__':
    try:
        run_all_tests()
    except KeyboardInterrupt:
        print("\n\nTests interrupted")
    except Exception as e:
        print(f"\n\n❌ Test error: {e}")
        import traceback
        traceback.print_exc()
