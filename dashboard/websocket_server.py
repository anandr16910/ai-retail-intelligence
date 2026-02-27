"""
WebSocket Server for Real-time Dashboard Updates
================================================

This module provides WebSocket support for real-time data streaming to the dashboard.
It handles live price updates, connection management, and efficient data broadcasting.

Features:
- Real-time price updates for gold, silver, and ETFs
- Connection status monitoring
- Efficient data broadcasting to multiple clients
- Automatic reconnection handling
- Rate limiting for data updates
"""

from flask import Flask
from flask_socketio import SocketIO, emit, join_room, leave_room
from flask_cors import CORS
import threading
import time
from datetime import datetime
from typing import Dict, List, Any, Optional
import sys
import os
import logging

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from src.data_loader import DataLoader
    from src.forecasting_model import PriceForecastingEngine
    from src.competitive_pricing import CompetitivePricingEngine
except ImportError as e:
    print(f"Warning: Could not import platform modules: {e}")
    DataLoader = None
    PriceForecastingEngine = None
    CompetitivePricingEngine = None

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize Flask app
app = Flask(__name__)
app.config['SECRET_KEY'] = 'ai-retail-intelligence-secret-key'
CORS(app)

# Initialize SocketIO with eventlet
socketio = SocketIO(
    app,
    cors_allowed_origins="*",
    async_mode='eventlet',
    logger=True,
    engineio_logger=False
)

# Global state
connected_clients = {}
data_loader = None
pricing_engine = None
forecasting_engine = None
update_thread = None
is_running = False


class ConnectionManager:
    """Manages WebSocket connections and client state."""
    
    def __init__(self):
        self.clients: Dict[str, Dict[str, Any]] = {}
        self.rooms: Dict[str, List[str]] = {
            'price_updates': [],
            'forecast_updates': [],
            'competitive_pricing': []
        }
    
    def add_client(self, client_id: str, client_info: Dict[str, Any]):
        """Add a new client connection."""
        self.clients[client_id] = {
            'connected_at': datetime.now(),
            'subscriptions': [],
            **client_info
        }
        logger.info(f"Client connected: {client_id}")
    
    def remove_client(self, client_id: str):
        """Remove a client connection."""
        if client_id in self.clients:
            # Remove from all rooms
            for room_clients in self.rooms.values():
                if client_id in room_clients:
                    room_clients.remove(client_id)
            
            del self.clients[client_id]
            logger.info(f"Client disconnected: {client_id}")
    
    def subscribe_to_room(self, client_id: str, room: str):
        """Subscribe a client to a data room."""
        if room in self.rooms and client_id not in self.rooms[room]:
            self.rooms[room].append(client_id)
            if client_id in self.clients:
                self.clients[client_id]['subscriptions'].append(room)
            logger.info(f"Client {client_id} subscribed to {room}")
    
    def unsubscribe_from_room(self, client_id: str, room: str):
        """Unsubscribe a client from a data room."""
        if room in self.rooms and client_id in self.rooms[room]:
            self.rooms[room].remove(client_id)
            if client_id in self.clients and room in self.clients[client_id]['subscriptions']:
                self.clients[client_id]['subscriptions'].remove(room)
            logger.info(f"Client {client_id} unsubscribed from {room}")
    
    def get_client_count(self) -> int:
        """Get total number of connected clients."""
        return len(self.clients)
    
    def get_room_client_count(self, room: str) -> int:
        """Get number of clients in a specific room."""
        return len(self.rooms.get(room, []))


# Initialize connection manager
connection_manager = ConnectionManager()


def initialize_components():
    """Initialize platform components."""
    global data_loader, pricing_engine, forecasting_engine
    
    try:
        if DataLoader:
            data_loader = DataLoader()
            logger.info("Data loader initialized")
        
        if CompetitivePricingEngine:
            pricing_engine = CompetitivePricingEngine()
            logger.info("Pricing engine initialized")
        
        if PriceForecastingEngine:
            forecasting_engine = PriceForecastingEngine()
            logger.info("Forecasting engine initialized")
        
        return True
    except Exception as e:
        logger.error(f"Error initializing components: {e}")
        return False


def get_latest_prices() -> Dict[str, Any]:
    """Get latest price data for all assets."""
    try:
        if not data_loader:
            return {}
        
        all_data = data_loader.load_all_data()
        
        prices = {}
        
        # Gold prices
        if 'gold' in all_data and not all_data['gold'].empty:
            gold_df = all_data['gold']
            if 'close' in gold_df.columns:
                latest_gold = gold_df.iloc[-1]
                prices['gold'] = {
                    'price': float(latest_gold['close']),
                    'open': float(latest_gold.get('open', latest_gold['close'])),
                    'high': float(latest_gold.get('high', latest_gold['close'])),
                    'low': float(latest_gold.get('low', latest_gold['close'])),
                    'timestamp': latest_gold.get('date', datetime.now()).isoformat() if 'date' in latest_gold else datetime.now().isoformat()
                }
        
        # Silver prices
        if 'silver' in all_data and not all_data['silver'].empty:
            silver_df = all_data['silver']
            if 'close' in silver_df.columns:
                latest_silver = silver_df.iloc[-1]
                prices['silver'] = {
                    'price': float(latest_silver['close']),
                    'open': float(latest_silver.get('open', latest_silver['close'])),
                    'high': float(latest_silver.get('high', latest_silver['close'])),
                    'low': float(latest_silver.get('low', latest_silver['close'])),
                    'timestamp': latest_silver.get('date', datetime.now()).isoformat() if 'date' in latest_silver else datetime.now().isoformat()
                }
        
        # ETF prices
        if 'etf' in all_data and not all_data['etf'].empty:
            etf_df = all_data['etf']
            if 'close' in etf_df.columns:
                latest_etf = etf_df.iloc[-1]
                prices['etf'] = {
                    'price': float(latest_etf['close']),
                    'open': float(latest_etf.get('open', latest_etf['close'])),
                    'high': float(latest_etf.get('high', latest_etf['close'])),
                    'low': float(latest_etf.get('low', latest_etf['close'])),
                    'timestamp': latest_etf.get('date', datetime.now()).isoformat() if 'date' in latest_etf else datetime.now().isoformat()
                }
        
        return prices
    
    except Exception as e:
        logger.error(f"Error getting latest prices: {e}")
        return {}


def get_competitive_pricing_updates() -> Dict[str, Any]:
    """Get latest competitive pricing data."""
    try:
        if not pricing_engine:
            return {}
        
        # Get best deals
        best_deals = pricing_engine.get_best_deals(5)
        
        # Get platform summary
        platform_summary = pricing_engine.get_platform_summary()
        
        return {
            'best_deals': best_deals,
            'platform_summary': platform_summary,
            'timestamp': datetime.now().isoformat()
        }
    
    except Exception as e:
        logger.error(f"Error getting competitive pricing updates: {e}")
        return {}


def broadcast_price_updates():
    """Background thread to broadcast price updates."""
    global is_running
    
    logger.info("Starting price update broadcast thread")
    
    while is_running:
        try:
            # Check if any clients are subscribed to price updates
            if connection_manager.get_room_client_count('price_updates') > 0:
                # Get latest prices
                prices = get_latest_prices()
                
                if prices:
                    # Broadcast to all clients in price_updates room
                    socketio.emit(
                        'price_update',
                        {
                            'data': prices,
                            'timestamp': datetime.now().isoformat()
                        },
                        room='price_updates'
                    )
                    logger.debug(f"Broadcasted price update to {connection_manager.get_room_client_count('price_updates')} clients")
            
            # Check if any clients are subscribed to competitive pricing
            if connection_manager.get_room_client_count('competitive_pricing') > 0:
                # Get competitive pricing updates
                pricing_data = get_competitive_pricing_updates()
                
                if pricing_data:
                    # Broadcast to all clients in competitive_pricing room
                    socketio.emit(
                        'competitive_pricing_update',
                        pricing_data,
                        room='competitive_pricing'
                    )
                    logger.debug(f"Broadcasted pricing update to {connection_manager.get_room_client_count('competitive_pricing')} clients")
            
            # Wait before next update (5 seconds for demo, adjust as needed)
            socketio.sleep(5)
        
        except Exception as e:
            logger.error(f"Error in broadcast thread: {e}")
            socketio.sleep(5)
    
    logger.info("Price update broadcast thread stopped")


# WebSocket event handlers

@socketio.on('connect')
def handle_connect():
    """Handle client connection."""
    client_id = request.sid if hasattr(request, 'sid') else 'unknown'
    
    connection_manager.add_client(client_id, {
        'user_agent': request.headers.get('User-Agent', 'Unknown') if hasattr(request, 'headers') else 'Unknown'
    })
    
    # Send connection confirmation
    emit('connection_status', {
        'status': 'connected',
        'client_id': client_id,
        'timestamp': datetime.now().isoformat(),
        'server_info': {
            'version': '1.0.0',
            'capabilities': ['price_updates', 'forecast_updates', 'competitive_pricing']
        }
    })
    
    logger.info(f"Client connected: {client_id}, Total clients: {connection_manager.get_client_count()}")


@socketio.on('disconnect')
def handle_disconnect():
    """Handle client disconnection."""
    client_id = request.sid if hasattr(request, 'sid') else 'unknown'
    connection_manager.remove_client(client_id)
    logger.info(f"Client disconnected: {client_id}, Total clients: {connection_manager.get_client_count()}")


@socketio.on('subscribe')
def handle_subscribe(data):
    """Handle subscription to data streams."""
    client_id = request.sid if hasattr(request, 'sid') else 'unknown'
    room = data.get('room', '')
    
    if room in connection_manager.rooms:
        join_room(room)
        connection_manager.subscribe_to_room(client_id, room)
        
        emit('subscription_status', {
            'status': 'subscribed',
            'room': room,
            'timestamp': datetime.now().isoformat()
        })
        
        # Send initial data
        if room == 'price_updates':
            prices = get_latest_prices()
            if prices:
                emit('price_update', {
                    'data': prices,
                    'timestamp': datetime.now().isoformat()
                })
        
        elif room == 'competitive_pricing':
            pricing_data = get_competitive_pricing_updates()
            if pricing_data:
                emit('competitive_pricing_update', pricing_data)
    
    else:
        emit('subscription_status', {
            'status': 'error',
            'message': f'Invalid room: {room}',
            'timestamp': datetime.now().isoformat()
        })


@socketio.on('unsubscribe')
def handle_unsubscribe(data):
    """Handle unsubscription from data streams."""
    client_id = request.sid if hasattr(request, 'sid') else 'unknown'
    room = data.get('room', '')
    
    if room in connection_manager.rooms:
        leave_room(room)
        connection_manager.unsubscribe_from_room(client_id, room)
        
        emit('subscription_status', {
            'status': 'unsubscribed',
            'room': room,
            'timestamp': datetime.now().isoformat()
        })


@socketio.on('ping')
def handle_ping():
    """Handle ping for connection health check."""
    emit('pong', {
        'timestamp': datetime.now().isoformat(),
        'server_status': 'healthy'
    })


@socketio.on('get_status')
def handle_get_status():
    """Handle status request."""
    emit('status_response', {
        'connected_clients': connection_manager.get_client_count(),
        'rooms': {
            room: connection_manager.get_room_client_count(room)
            for room in connection_manager.rooms.keys()
        },
        'timestamp': datetime.now().isoformat(),
        'server_status': 'running'
    })


# HTTP endpoints for health checks

@app.route('/health')
def health_check():
    """Health check endpoint."""
    return {
        'status': 'healthy',
        'connected_clients': connection_manager.get_client_count(),
        'timestamp': datetime.now().isoformat()
    }


@app.route('/status')
def status():
    """Status endpoint."""
    return {
        'status': 'running',
        'connected_clients': connection_manager.get_client_count(),
        'rooms': {
            room: connection_manager.get_room_client_count(room)
            for room in connection_manager.rooms.keys()
        },
        'timestamp': datetime.now().isoformat()
    }


def start_server(host='0.0.0.0', port=5000, debug=False):
    """Start the WebSocket server."""
    global is_running, update_thread
    
    # Initialize components
    if not initialize_components():
        logger.warning("Some components failed to initialize, continuing with limited functionality")
    
    # Start background update thread
    is_running = True
    update_thread = threading.Thread(target=broadcast_price_updates, daemon=True)
    update_thread.start()
    
    logger.info(f"Starting WebSocket server on {host}:{port}")
    
    # Run the server
    socketio.run(app, host=host, port=port, debug=debug)


def stop_server():
    """Stop the WebSocket server."""
    global is_running
    is_running = False
    logger.info("WebSocket server stopped")


if __name__ == '__main__':
    # Start server
    start_server(host='0.0.0.0', port=5000, debug=True)
