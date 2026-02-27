"""
Real-time WebSocket Client for Dashboard
========================================

This module provides WebSocket client functionality for real-time data updates
in the Streamlit dashboard. It handles connection management, data streaming,
and state synchronization.

Features:
- Automatic connection and reconnection
- Subscription management for different data streams
- Connection status monitoring
- Efficient state updates
- Error handling and recovery
"""

import socketio
import threading
import time
from datetime import datetime
from typing import Dict, Any, Callable, Optional, List
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class RealtimeClient:
    """WebSocket client for real-time dashboard updates."""
    
    def __init__(self, server_url: str = 'http://localhost:5000'):
        """
        Initialize the real-time client.
        
        Args:
            server_url: WebSocket server URL
        """
        self.server_url = server_url
        self.sio = socketio.Client(
            reconnection=True,
            reconnection_attempts=0,  # Infinite attempts
            reconnection_delay=1,
            reconnection_delay_max=5,
            logger=False,
            engineio_logger=False
        )
        
        # Connection state
        self.connected = False
        self.connection_status = 'disconnected'
        self.last_update = None
        
        # Data storage
        self.latest_prices = {}
        self.latest_competitive_pricing = {}
        self.subscriptions = set()
        
        # Callbacks
        self.callbacks: Dict[str, List[Callable]] = {
            'price_update': [],
            'competitive_pricing_update': [],
            'connection_status': [],
            'error': []
        }
        
        # Setup event handlers
        self._setup_handlers()
    
    def _setup_handlers(self):
        """Setup WebSocket event handlers."""
        
        @self.sio.on('connect')
        def on_connect():
            """Handle connection event."""
            self.connected = True
            self.connection_status = 'connected'
            logger.info(f"Connected to WebSocket server: {self.server_url}")
            self._trigger_callbacks('connection_status', {
                'status': 'connected',
                'timestamp': datetime.now().isoformat()
            })
        
        @self.sio.on('disconnect')
        def on_disconnect():
            """Handle disconnection event."""
            self.connected = False
            self.connection_status = 'disconnected'
            logger.info("Disconnected from WebSocket server")
            self._trigger_callbacks('connection_status', {
                'status': 'disconnected',
                'timestamp': datetime.now().isoformat()
            })
        
        @self.sio.on('connection_status')
        def on_connection_status(data):
            """Handle connection status update."""
            logger.info(f"Connection status: {data}")
            self._trigger_callbacks('connection_status', data)
        
        @self.sio.on('price_update')
        def on_price_update(data):
            """Handle price update event."""
            self.latest_prices = data.get('data', {})
            self.last_update = data.get('timestamp')
            logger.debug(f"Received price update: {len(self.latest_prices)} assets")
            self._trigger_callbacks('price_update', data)
        
        @self.sio.on('competitive_pricing_update')
        def on_competitive_pricing_update(data):
            """Handle competitive pricing update event."""
            self.latest_competitive_pricing = data
            self.last_update = data.get('timestamp')
            logger.debug("Received competitive pricing update")
            self._trigger_callbacks('competitive_pricing_update', data)
        
        @self.sio.on('subscription_status')
        def on_subscription_status(data):
            """Handle subscription status update."""
            logger.info(f"Subscription status: {data}")
        
        @self.sio.on('pong')
        def on_pong(data):
            """Handle pong response."""
            logger.debug(f"Pong received: {data}")
        
        @self.sio.on('status_response')
        def on_status_response(data):
            """Handle status response."""
            logger.info(f"Server status: {data}")
        
        @self.sio.on('error')
        def on_error(data):
            """Handle error event."""
            logger.error(f"WebSocket error: {data}")
            self._trigger_callbacks('error', data)
    
    def connect(self) -> bool:
        """
        Connect to the WebSocket server.
        
        Returns:
            True if connection successful, False otherwise
        """
        try:
            if not self.connected:
                logger.info(f"Connecting to {self.server_url}...")
                self.sio.connect(self.server_url)
                return True
            return True
        except Exception as e:
            logger.error(f"Connection error: {e}")
            self.connection_status = 'error'
            return False
    
    def disconnect(self):
        """Disconnect from the WebSocket server."""
        try:
            if self.connected:
                self.sio.disconnect()
                logger.info("Disconnected from server")
        except Exception as e:
            logger.error(f"Disconnection error: {e}")
    
    def subscribe(self, room: str) -> bool:
        """
        Subscribe to a data stream.
        
        Args:
            room: Room name to subscribe to (price_updates, competitive_pricing, etc.)
        
        Returns:
            True if subscription successful, False otherwise
        """
        try:
            if not self.connected:
                logger.warning("Not connected, attempting to connect...")
                if not self.connect():
                    return False
            
            self.sio.emit('subscribe', {'room': room})
            self.subscriptions.add(room)
            logger.info(f"Subscribed to {room}")
            return True
        except Exception as e:
            logger.error(f"Subscription error: {e}")
            return False
    
    def unsubscribe(self, room: str) -> bool:
        """
        Unsubscribe from a data stream.
        
        Args:
            room: Room name to unsubscribe from
        
        Returns:
            True if unsubscription successful, False otherwise
        """
        try:
            if self.connected:
                self.sio.emit('unsubscribe', {'room': room})
                self.subscriptions.discard(room)
                logger.info(f"Unsubscribed from {room}")
                return True
            return False
        except Exception as e:
            logger.error(f"Unsubscription error: {e}")
            return False
    
    def ping(self):
        """Send ping to check connection health."""
        try:
            if self.connected:
                self.sio.emit('ping')
        except Exception as e:
            logger.error(f"Ping error: {e}")
    
    def get_status(self):
        """Request server status."""
        try:
            if self.connected:
                self.sio.emit('get_status')
        except Exception as e:
            logger.error(f"Get status error: {e}")
    
    def register_callback(self, event: str, callback: Callable):
        """
        Register a callback for an event.
        
        Args:
            event: Event name (price_update, competitive_pricing_update, etc.)
            callback: Callback function to call when event occurs
        """
        if event in self.callbacks:
            self.callbacks[event].append(callback)
            logger.debug(f"Registered callback for {event}")
        else:
            logger.warning(f"Unknown event type: {event}")
    
    def unregister_callback(self, event: str, callback: Callable):
        """
        Unregister a callback for an event.
        
        Args:
            event: Event name
            callback: Callback function to remove
        """
        if event in self.callbacks and callback in self.callbacks[event]:
            self.callbacks[event].remove(callback)
            logger.debug(f"Unregistered callback for {event}")
    
    def _trigger_callbacks(self, event: str, data: Any):
        """
        Trigger all callbacks for an event.
        
        Args:
            event: Event name
            data: Event data
        """
        if event in self.callbacks:
            for callback in self.callbacks[event]:
                try:
                    callback(data)
                except Exception as e:
                    logger.error(f"Callback error for {event}: {e}")
    
    def get_latest_prices(self) -> Dict[str, Any]:
        """
        Get the latest price data.
        
        Returns:
            Dictionary of latest prices
        """
        return self.latest_prices.copy()
    
    def get_latest_competitive_pricing(self) -> Dict[str, Any]:
        """
        Get the latest competitive pricing data.
        
        Returns:
            Dictionary of latest competitive pricing data
        """
        return self.latest_competitive_pricing.copy()
    
    def is_connected(self) -> bool:
        """
        Check if client is connected.
        
        Returns:
            True if connected, False otherwise
        """
        return self.connected
    
    def get_connection_status(self) -> str:
        """
        Get current connection status.
        
        Returns:
            Connection status string
        """
        return self.connection_status
    
    def get_subscriptions(self) -> set:
        """
        Get current subscriptions.
        
        Returns:
            Set of subscribed rooms
        """
        return self.subscriptions.copy()


class RealtimeClientManager:
    """Manager for real-time client with automatic reconnection."""
    
    def __init__(self, server_url: str = 'http://localhost:5000'):
        """
        Initialize the client manager.
        
        Args:
            server_url: WebSocket server URL
        """
        self.client = RealtimeClient(server_url)
        self.auto_reconnect = True
        self.reconnect_thread = None
        self.running = False
    
    def start(self):
        """Start the client manager with auto-reconnection."""
        self.running = True
        
        # Connect initially
        self.client.connect()
        
        # Start reconnection thread
        self.reconnect_thread = threading.Thread(target=self._reconnect_loop, daemon=True)
        self.reconnect_thread.start()
        
        logger.info("Client manager started")
    
    def stop(self):
        """Stop the client manager."""
        self.running = False
        self.client.disconnect()
        logger.info("Client manager stopped")
    
    def _reconnect_loop(self):
        """Background thread for automatic reconnection."""
        while self.running:
            try:
                if not self.client.is_connected() and self.auto_reconnect:
                    logger.info("Attempting to reconnect...")
                    self.client.connect()
                
                # Wait before next check
                time.sleep(5)
            except Exception as e:
                logger.error(f"Reconnection loop error: {e}")
                time.sleep(5)
    
    def get_client(self) -> RealtimeClient:
        """
        Get the real-time client instance.
        
        Returns:
            RealtimeClient instance
        """
        return self.client


# Global client manager instance
_client_manager: Optional[RealtimeClientManager] = None


def get_realtime_client(server_url: str = 'http://localhost:5000') -> RealtimeClient:
    """
    Get or create the global real-time client instance.
    
    Args:
        server_url: WebSocket server URL
    
    Returns:
        RealtimeClient instance
    """
    global _client_manager
    
    if _client_manager is None:
        _client_manager = RealtimeClientManager(server_url)
        _client_manager.start()
    
    return _client_manager.get_client()


def stop_realtime_client():
    """Stop the global real-time client."""
    global _client_manager
    
    if _client_manager is not None:
        _client_manager.stop()
        _client_manager = None
