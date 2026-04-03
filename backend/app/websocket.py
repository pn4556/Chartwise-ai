"""
WebSocket Manager for real-time updates
"""

import json
import asyncio
from typing import List, Dict, Set
from fastapi import WebSocket, WebSocketDisconnect
from datetime import datetime

class ConnectionManager:
    """Manages WebSocket connections"""
    
    def __init__(self):
        self.active_connections: List[WebSocket] = []
        self.subscriptions: Dict[str, Set[WebSocket]] = {}  # symbol -> set of connections
    
    async def connect(self, websocket: WebSocket):
        """Accept new connection"""
        await websocket.accept()
        self.active_connections.append(websocket)
        print(f"🔌 New WebSocket connection. Total: {len(self.active_connections)}")
    
    def disconnect(self, websocket: WebSocket):
        """Remove connection"""
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)
        
        # Remove from all subscriptions
        for symbol, connections in self.subscriptions.items():
            connections.discard(websocket)
        
        print(f"🔌 WebSocket disconnected. Total: {len(self.active_connections)}")
    
    def subscribe(self, websocket: WebSocket, symbol: str):
        """Subscribe to symbol updates"""
        if symbol not in self.subscriptions:
            self.subscriptions[symbol] = set()
        self.subscriptions[symbol].add(websocket)
        print(f"📊 {websocket.client} subscribed to {symbol}")
    
    def unsubscribe(self, websocket: WebSocket, symbol: str):
        """Unsubscribe from symbol updates"""
        if symbol in self.subscriptions:
            self.subscriptions[symbol].discard(websocket)
    
    async def broadcast_to_symbol(self, symbol: str, message: dict):
        """Send update to all subscribers of a symbol"""
        if symbol not in self.subscriptions:
            return
        
        disconnected = []
        for connection in self.subscriptions[symbol]:
            try:
                await connection.send_json(message)
            except:
                disconnected.append(connection)
        
        # Clean up disconnected clients
        for conn in disconnected:
            self.disconnect(conn)
    
    async def broadcast_to_all(self, message: dict):
        """Broadcast to all connected clients"""
        disconnected = []
        for connection in self.active_connections:
            try:
                await connection.send_json(message)
            except:
                disconnected.append(connection)
        
        # Clean up disconnected clients
        for conn in disconnected:
            self.disconnect(conn)

# Global manager instance
manager = ConnectionManager()

async def handle_websocket(websocket: WebSocket):
    """Handle WebSocket connection"""
    await manager.connect(websocket)
    
    # Send connection confirmation
    await websocket.send_json({
        'type': 'connected',
        'message': 'WebSocket connection established',
        'timestamp': datetime.now().isoformat()
    })
    
    try:
        while True:
            # Receive message from client
            data = await websocket.receive_text()
            message = json.loads(data)
            
            action = message.get('action')
            symbol = message.get('symbol')
            symbols = message.get('symbols', [])
            
            if action == 'subscribe' and symbol:
                manager.subscribe(websocket, symbol.upper())
                await websocket.send_json({
                    'type': 'subscribed',
                    'symbol': symbol.upper(),
                    'timestamp': datetime.now().isoformat()
                })
            
            elif action == 'subscribe_multiple' and symbols:
                # Subscribe to multiple symbols at once
                subscribed = []
                for sym in symbols:
                    manager.subscribe(websocket, sym.upper())
                    subscribed.append(sym.upper())
                await websocket.send_json({
                    'type': 'subscribed_multiple',
                    'symbols': subscribed,
                    'timestamp': datetime.now().isoformat()
                })
            
            elif action == 'unsubscribe' and symbol:
                manager.unsubscribe(websocket, symbol.upper())
                await websocket.send_json({
                    'type': 'unsubscribe',
                    'symbol': symbol.upper(),
                    'timestamp': datetime.now().isoformat()
                })
            
            elif action == 'unsubscribe_all':
                # Unsubscribe from all symbols
                for sym in list(manager.subscriptions.keys()):
                    manager.subscriptions[sym].discard(websocket)
                await websocket.send_json({
                    'type': 'unsubscribed_all',
                    'timestamp': datetime.now().isoformat()
                })
            
            elif action == 'ping':
                await websocket.send_json({
                    'type': 'pong',
                    'timestamp': datetime.now().isoformat()
                })
            
            elif action == 'get_subscriptions':
                # Return list of symbols this connection is subscribed to
                user_subs = [
                    sym for sym, conns in manager.subscriptions.items()
                    if websocket in conns
                ]
                await websocket.send_json({
                    'type': 'subscriptions',
                    'symbols': user_subs,
                    'timestamp': datetime.now().isoformat()
                })
    
    except WebSocketDisconnect:
        manager.disconnect(websocket)
    except Exception as e:
        print(f"WebSocket error: {e}")
        manager.disconnect(websocket)


async def broadcast_price_update(symbol: str, price_data: dict):
    """Broadcast real-time price update for a symbol"""
    message = {
        'type': 'price_update',
        'symbol': symbol,
        'data': price_data,
        'timestamp': datetime.now().isoformat()
    }
    await manager.broadcast_to_symbol(symbol, message)


async def broadcast_portfolio_update(user_id: str, portfolio_data: dict):
    """Broadcast portfolio update to specific user"""
    message = {
        'type': 'portfolio_update',
        'user_id': user_id,
        'data': portfolio_data,
        'timestamp': datetime.now().isoformat()
    }
    await manager.broadcast_to_all(message)
