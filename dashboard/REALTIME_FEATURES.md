# Real-time Dashboard Updates

This document describes the real-time update features added to the AI Retail Intelligence dashboard.

## Overview

The dashboard now supports real-time data updates through WebSocket connections, providing live price updates, competitive pricing changes, and connection status monitoring without requiring page refreshes.

## Architecture

### Components

1. **WebSocket Server** (`websocket_server.py`)
   - Flask-SocketIO based server
   - Handles multiple client connections
   - Broadcasts price updates every 5 seconds
   - Manages subscription rooms for different data streams

2. **Real-time Client** (`realtime_client.py`)
   - Python SocketIO client for Streamlit
   - Automatic reconnection handling
   - Callback-based event system
   - Connection status monitoring

3. **Enhanced Dashboard** (`app.py`)
   - Integrated WebSocket client
   - Live price indicators
   - Connection status display
   - Subscription management UI

### Data Flow

```
Data Sources → WebSocket Server → Broadcast → Dashboard Clients
     ↓              ↓                  ↓              ↓
  CSV Files    Connection Mgmt    Price Updates   Live Display
  Pricing DB   Room Management    Deal Updates    Status Indicators
```

## Features

### 1. Real-time Price Updates

- **Live Gold Prices**: Updates every 5 seconds with current market data
- **Live Silver Prices**: Real-time silver price tracking
- **Live ETF Prices**: ETF price updates with OHLC data
- **Visual Indicators**: 🔴 LIVE badge on metrics receiving real-time data

### 2. Connection Management

- **Auto-connect**: Attempts to connect on dashboard load
- **Auto-reconnect**: Automatic reconnection on connection loss
- **Status Indicators**: Visual feedback for connection state
  - ✅ Connected (green)
  - 🔄 Connecting (yellow)
  - ❌ Disconnected (red)

### 3. Subscription System

- **Price Updates Room**: Subscribe to live price feeds
- **Competitive Pricing Room**: Subscribe to deal updates
- **Selective Subscriptions**: Choose which data streams to receive
- **Bandwidth Optimization**: Only receive subscribed data

### 4. Connection Status Monitoring

- **Health Checks**: Periodic ping/pong for connection health
- **Server Status**: View connected clients and room statistics
- **Reconnection Controls**: Manual retry connection option

## Setup and Usage

### Prerequisites

```bash
# Install dependencies
pip install -r dashboard/requirements.txt
```

Required packages:
- `flask-socketio>=5.3.0`
- `python-socketio>=5.9.0`
- `eventlet>=0.33.0`

### Starting the WebSocket Server

**Option 1: Using the launcher script**
```bash
python dashboard/run_websocket_server.py
```

**Option 2: With custom settings**
```bash
python dashboard/run_websocket_server.py --host 0.0.0.0 --port 5000 --debug
```

**Option 3: Programmatically**
```python
from dashboard.websocket_server import start_server

start_server(host='0.0.0.0', port=5000, debug=False)
```

### Starting the Dashboard

```bash
# In a separate terminal
streamlit run dashboard/app.py
```

The dashboard will automatically attempt to connect to the WebSocket server at `http://localhost:5000`.

## Configuration

### WebSocket Server Configuration

Edit `dashboard/websocket_server.py`:

```python
# Update broadcast interval (default: 5 seconds)
socketio.sleep(5)  # Change to desired interval

# Configure CORS
CORS(app)  # Modify for production security

# Configure rooms
connection_manager.rooms = {
    'price_updates': [],
    'forecast_updates': [],
    'competitive_pricing': []
}
```

### Dashboard Configuration

Edit `dashboard/app.py`:

```python
# WebSocket server URL
self.websocket_url = "http://localhost:5000"

# Enable/disable real-time features
st.session_state.realtime_enabled = True
```

## API Reference

### WebSocket Events

#### Client → Server

**connect**
- Establishes connection to server
- Returns: `connection_status` event with client info

**subscribe**
```python
emit('subscribe', {'room': 'price_updates'})
```
- Subscribe to a data stream
- Rooms: `price_updates`, `competitive_pricing`, `forecast_updates`

**unsubscribe**
```python
emit('unsubscribe', {'room': 'price_updates'})
```
- Unsubscribe from a data stream

**ping**
```python
emit('ping')
```
- Health check request
- Returns: `pong` event

**get_status**
```python
emit('get_status')
```
- Request server status
- Returns: `status_response` event

#### Server → Client

**connection_status**
```json
{
  "status": "connected",
  "client_id": "abc123",
  "timestamp": "2024-01-15T10:30:00",
  "server_info": {
    "version": "1.0.0",
    "capabilities": ["price_updates", "forecast_updates", "competitive_pricing"]
  }
}
```

**price_update**
```json
{
  "data": {
    "gold": {
      "price": 155000.50,
      "open": 154800.00,
      "high": 155200.00,
      "low": 154500.00,
      "timestamp": "2024-01-15T10:30:00"
    },
    "silver": { ... },
    "etf": { ... }
  },
  "timestamp": "2024-01-15T10:30:00"
}
```

**competitive_pricing_update**
```json
{
  "best_deals": [...],
  "platform_summary": {...},
  "timestamp": "2024-01-15T10:30:00"
}
```

**subscription_status**
```json
{
  "status": "subscribed",
  "room": "price_updates",
  "timestamp": "2024-01-15T10:30:00"
}
```

**pong**
```json
{
  "timestamp": "2024-01-15T10:30:00",
  "server_status": "healthy"
}
```

**status_response**
```json
{
  "connected_clients": 5,
  "rooms": {
    "price_updates": 3,
    "competitive_pricing": 2
  },
  "timestamp": "2024-01-15T10:30:00",
  "server_status": "running"
}
```

### HTTP Endpoints

**GET /health**
```json
{
  "status": "healthy",
  "connected_clients": 5,
  "timestamp": "2024-01-15T10:30:00"
}
```

**GET /status**
```json
{
  "status": "running",
  "connected_clients": 5,
  "rooms": {
    "price_updates": 3,
    "competitive_pricing": 2
  },
  "timestamp": "2024-01-15T10:30:00"
}
```

## Usage Examples

### Python Client

```python
from dashboard.realtime_client import get_realtime_client

# Get client instance
client = get_realtime_client('http://localhost:5000')

# Register callback
def on_price_update(data):
    print(f"New prices: {data}")

client.register_callback('price_update', on_price_update)

# Subscribe to updates
client.subscribe('price_updates')

# Get latest data
prices = client.get_latest_prices()
print(prices)

# Check connection
if client.is_connected():
    print("Connected!")
```

### JavaScript Client (Future)

```javascript
// Connect to server
const socket = io('http://localhost:5000');

// Handle connection
socket.on('connect', () => {
  console.log('Connected!');
  
  // Subscribe to price updates
  socket.emit('subscribe', { room: 'price_updates' });
});

// Handle price updates
socket.on('price_update', (data) => {
  console.log('New prices:', data);
  updateUI(data);
});

// Handle disconnection
socket.on('disconnect', () => {
  console.log('Disconnected');
});
```

## Performance Considerations

### Bandwidth Optimization

- **Selective Subscriptions**: Only subscribe to needed data streams
- **Update Intervals**: Adjust broadcast frequency based on needs
- **Data Compression**: Consider enabling compression for large payloads

### Scalability

- **Connection Pooling**: Server supports multiple concurrent connections
- **Room-based Broadcasting**: Efficient targeted updates
- **Eventlet Async**: Non-blocking I/O for high concurrency

### Resource Usage

- **Server**: ~50-100MB RAM, minimal CPU
- **Client**: ~10-20MB RAM per connection
- **Network**: ~1-5KB per update (depends on data size)

## Troubleshooting

### Connection Issues

**Problem**: Dashboard shows "Disconnected"

**Solutions**:
1. Ensure WebSocket server is running: `python dashboard/run_websocket_server.py`
2. Check server logs for errors
3. Verify port 5000 is not blocked by firewall
4. Try manual reconnection from dashboard sidebar

**Problem**: "Connection refused" error

**Solutions**:
1. Verify server URL in dashboard configuration
2. Check if server is listening on correct host/port
3. Ensure no other service is using port 5000

### Data Not Updating

**Problem**: Connected but no data updates

**Solutions**:
1. Check if subscribed to correct room
2. Verify data sources are available (CSV files loaded)
3. Check server logs for broadcast errors
4. Ensure update interval is not too long

### Performance Issues

**Problem**: High CPU or memory usage

**Solutions**:
1. Increase update interval (reduce broadcast frequency)
2. Limit number of concurrent connections
3. Optimize data payload size
4. Consider using Redis for caching

## Security Considerations

### Production Deployment

1. **CORS Configuration**: Restrict allowed origins
   ```python
   CORS(app, origins=['https://yourdomain.com'])
   ```

2. **Authentication**: Add token-based auth
   ```python
   @socketio.on('connect')
   def handle_connect(auth):
       if not verify_token(auth['token']):
           return False
   ```

3. **Rate Limiting**: Implement per-client rate limits
   ```python
   from flask_limiter import Limiter
   limiter = Limiter(app)
   ```

4. **SSL/TLS**: Use secure WebSocket (wss://)
   ```python
   socketio.run(app, ssl_context='adhoc')
   ```

## Future Enhancements

### Planned Features

1. **Historical Data Replay**: Replay past price movements
2. **Custom Alerts**: User-defined price alerts
3. **Data Persistence**: Store real-time data to database
4. **Advanced Analytics**: Real-time trend analysis
5. **Mobile Support**: Native mobile app integration
6. **Multi-user Collaboration**: Shared dashboard views

### Integration Opportunities

1. **External Data Sources**: Live market feeds (Alpha Vantage, Yahoo Finance)
2. **Message Queues**: Redis Pub/Sub, RabbitMQ integration
3. **Cloud Deployment**: AWS, Azure, GCP WebSocket services
4. **Monitoring**: Prometheus, Grafana integration

## Testing

### Manual Testing

1. Start WebSocket server
2. Start dashboard
3. Verify connection status shows "Connected"
4. Subscribe to price updates
5. Observe live price changes (🔴 LIVE indicator)
6. Stop server and verify reconnection attempts

### Automated Testing

```python
# Test WebSocket server
import socketio

client = socketio.Client()
client.connect('http://localhost:5000')

# Test subscription
client.emit('subscribe', {'room': 'price_updates'})

# Test data reception
@client.on('price_update')
def on_update(data):
    assert 'data' in data
    assert 'timestamp' in data
    print("Test passed!")

client.wait()
```

## Support

For issues or questions:
1. Check server logs: `dashboard/logs/`
2. Review this documentation
3. Check GitHub issues
4. Contact development team

## License

This feature is part of the AI Retail Intelligence platform and follows the same license terms.
