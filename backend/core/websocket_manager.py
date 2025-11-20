"""
WebSocket connection manager for real-time features
"""

from fastapi import WebSocket, WebSocketDisconnect
from typing import Dict, List, Set
import json
import asyncio
from datetime import datetime


class ConnectionManager:
    """Manage WebSocket connections"""
    
    def __init__(self):
        self.active_connections: Dict[int, List[WebSocket]] = {}
        self.scan_subscribers: Dict[int, Set[int]] = {}
        self.guild_channels: Dict[int, Set[int]] = {}
    
    async def connect(self, websocket: WebSocket, user_id: int):
        """Connect a new WebSocket client"""
        await websocket.accept()
        
        if user_id not in self.active_connections:
            self.active_connections[user_id] = []
        
        self.active_connections[user_id].append(websocket)
    
    def disconnect(self, websocket: WebSocket, user_id: int):
        """Disconnect a WebSocket client"""
        if user_id in self.active_connections:
            self.active_connections[user_id].remove(websocket)
            
            if not self.active_connections[user_id]:
                del self.active_connections[user_id]
    
    async def send_personal_message(self, message: dict, user_id: int):
        """Send message to specific user"""
        if user_id in self.active_connections:
            disconnected = []
            for connection in self.active_connections[user_id]:
                try:
                    await connection.send_json(message)
                except:
                    disconnected.append(connection)
            
            for connection in disconnected:
                self.disconnect(connection, user_id)
    
    async def broadcast(self, message: dict):
        """Broadcast message to all connected clients"""
        disconnected = []
        for user_id, connections in self.active_connections.items():
            for connection in connections:
                try:
                    await connection.send_json(message)
                except:
                    disconnected.append((connection, user_id))
        
        for connection, user_id in disconnected:
            self.disconnect(connection, user_id)
    
    async def subscribe_to_scan(self, scan_id: int, user_id: int):
        """Subscribe user to scan updates"""
        if scan_id not in self.scan_subscribers:
            self.scan_subscribers[scan_id] = set()
        
        self.scan_subscribers[scan_id].add(user_id)
    
    async def unsubscribe_from_scan(self, scan_id: int, user_id: int):
        """Unsubscribe user from scan updates"""
        if scan_id in self.scan_subscribers:
            self.scan_subscribers[scan_id].discard(user_id)
            
            if not self.scan_subscribers[scan_id]:
                del self.scan_subscribers[scan_id]
    
    async def notify_scan_update(self, scan_id: int, scan_data: dict):
        """Notify all subscribers of scan update"""
        if scan_id in self.scan_subscribers:
            message = {
                "type": "scan_update",
                "scan_id": scan_id,
                "data": scan_data,
                "timestamp": datetime.utcnow().isoformat()
            }
            
            for user_id in self.scan_subscribers[scan_id]:
                await self.send_personal_message(message, user_id)
    
    async def join_guild_channel(self, guild_id: int, user_id: int):
        """Join guild chat channel"""
        if guild_id not in self.guild_channels:
            self.guild_channels[guild_id] = set()
        
        self.guild_channels[guild_id].add(user_id)
    
    async def leave_guild_channel(self, guild_id: int, user_id: int):
        """Leave guild chat channel"""
        if guild_id in self.guild_channels:
            self.guild_channels[guild_id].discard(user_id)
            
            if not self.guild_channels[guild_id]:
                del self.guild_channels[guild_id]
    
    async def broadcast_to_guild(self, guild_id: int, message: dict):
        """Broadcast message to all guild members"""
        if guild_id in self.guild_channels:
            message_data = {
                "type": "guild_message",
                "guild_id": guild_id,
                "data": message,
                "timestamp": datetime.utcnow().isoformat()
            }
            
            for user_id in self.guild_channels[guild_id]:
                await self.send_personal_message(message_data, user_id)
    
    async def notify_bug_validation(self, user_id: int, bug_data: dict):
        """Notify user of bug validation"""
        message = {
            "type": "bug_validated",
            "data": bug_data,
            "timestamp": datetime.utcnow().isoformat()
        }
        
        await self.send_personal_message(message, user_id)
    
    async def notify_payment_received(self, user_id: int, payment_data: dict):
        """Notify user of payment"""
        message = {
            "type": "payment_received",
            "data": payment_data,
            "timestamp": datetime.utcnow().isoformat()
        }
        
        await self.send_personal_message(message, user_id)


manager = ConnectionManager()
