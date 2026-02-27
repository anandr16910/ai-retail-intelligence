#!/usr/bin/env python3
"""
WebSocket Server Launcher
=========================

This script starts the WebSocket server for real-time dashboard updates.
Run this before starting the Streamlit dashboard to enable real-time features.

Usage:
    python run_websocket_server.py [--host HOST] [--port PORT] [--debug]

Examples:
    python run_websocket_server.py
    python run_websocket_server.py --host 0.0.0.0 --port 5000
    python run_websocket_server.py --debug
"""

import argparse
import sys
import os
import logging

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dashboard.websocket_server import start_server, stop_server

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description='WebSocket Server for Real-time Dashboard Updates'
    )
    
    parser.add_argument(
        '--host',
        type=str,
        default='0.0.0.0',
        help='Host to bind to (default: 0.0.0.0)'
    )
    
    parser.add_argument(
        '--port',
        type=int,
        default=5000,
        help='Port to bind to (default: 5000)'
    )
    
    parser.add_argument(
        '--debug',
        action='store_true',
        help='Enable debug mode'
    )
    
    args = parser.parse_args()
    
    # Print startup banner
    print("=" * 60)
    print("AI Retail Intelligence - WebSocket Server")
    print("=" * 60)
    print(f"Host: {args.host}")
    print(f"Port: {args.port}")
    print(f"Debug: {args.debug}")
    print("=" * 60)
    print("\nStarting server...")
    print("Press Ctrl+C to stop\n")
    
    try:
        # Start the server
        start_server(host=args.host, port=args.port, debug=args.debug)
    except KeyboardInterrupt:
        print("\n\nShutting down server...")
        stop_server()
        print("Server stopped")
    except Exception as e:
        logger.error(f"Server error: {e}")
        sys.exit(1)


if __name__ == '__main__':
    main()
