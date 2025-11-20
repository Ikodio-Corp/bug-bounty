"""
WebSocket Manager for Real-time Updates
"""

from typing import Dict, Set, List
from fastapi import WebSocket
import json
import asyncio


class ConnectionManager:
    """Manages WebSocket connections"""
    
    def __init__(self):
        self.active_connections: Dict[int, Set[WebSocket]] = {}
        self.scan_connections: Dict[int, Set[WebSocket]] = {}
    
    async def connect(self, websocket: WebSocket, user_id: int):
        """Connect a user's WebSocket"""
        await websocket.accept()
        
        if user_id not in self.active_connections:
            self.active_connections[user_id] = set()
        
        self.active_connections[user_id].add(websocket)
    
    def disconnect(self, websocket: WebSocket, user_id: int):
        """Disconnect a user's WebSocket"""
        if user_id in self.active_connections:
            self.active_connections[user_id].discard(websocket)
            
            if not self.active_connections[user_id]:
                del self.active_connections[user_id]
    
    async def subscribe_to_scan(self, websocket: WebSocket, scan_id: int):
        """Subscribe to scan updates"""
        if scan_id not in self.scan_connections:
            self.scan_connections[scan_id] = set()
        
        self.scan_connections[scan_id].add(websocket)
    
    def unsubscribe_from_scan(self, websocket: WebSocket, scan_id: int):
        """Unsubscribe from scan updates"""
        if scan_id in self.scan_connections:
            self.scan_connections[scan_id].discard(websocket)
            
            if not self.scan_connections[scan_id]:
                del self.scan_connections[scan_id]
    
    async def send_personal_message(self, message: str, user_id: int):
        """Send message to specific user"""
        if user_id in self.active_connections:
            disconnected = set()
            
            for connection in self.active_connections[user_id]:
                try:
                    await connection.send_text(message)
                except Exception:
                    disconnected.add(connection)
            
            for connection in disconnected:
                self.active_connections[user_id].discard(connection)
    
    async def send_scan_update(self, scan_id: int, message: Dict):
        """Send update to all subscribers of a scan"""
        if scan_id in self.scan_connections:
            disconnected = set()
            message_text = json.dumps(message)
            
            for connection in self.scan_connections[scan_id]:
                try:
                    await connection.send_text(message_text)
                except Exception:
                    disconnected.add(connection)
            
            for connection in disconnected:
                self.scan_connections[scan_id].discard(connection)
    
    async def broadcast(self, message: str, user_ids: List[int] = None):
        """Broadcast message to multiple users"""
        if user_ids is None:
            user_ids = list(self.active_connections.keys())
        
        for user_id in user_ids:
            await self.send_personal_message(message, user_id)
    
    async def notify_bug_update(
        self,
        user_id: int,
        bug_id: int,
        status: str,
        title: str
    ):
        """Notify user about bug status update"""
        message = json.dumps({
            "type": "bug_update",
            "bug_id": bug_id,
            "status": status,
            "title": title,
            "timestamp": asyncio.get_event_loop().time()
        })
        
        await self.send_personal_message(message, user_id)
    
    async def notify_scan_progress(
        self,
        scan_id: int,
        progress: int,
        status: str,
        vulnerabilities_found: int = 0
    ):
        """Notify scan progress update"""
        message = {
            "type": "scan_progress",
            "scan_id": scan_id,
            "progress": progress,
            "status": status,
            "vulnerabilities_found": vulnerabilities_found,
            "timestamp": asyncio.get_event_loop().time()
        }
        
        await self.send_scan_update(scan_id, message)
    
    async def notify_marketplace_purchase(
        self,
        seller_id: int,
        buyer_id: int,
        listing_title: str,
        price: float
    ):
        """Notify marketplace purchase"""
        seller_message = json.dumps({
            "type": "marketplace_sale",
            "listing_title": listing_title,
            "price": price,
            "timestamp": asyncio.get_event_loop().time()
        })
        
        buyer_message = json.dumps({
            "type": "marketplace_purchase",
            "listing_title": listing_title,
            "price": price,
            "timestamp": asyncio.get_event_loop().time()
        })
        
        await self.send_personal_message(seller_message, seller_id)
        await self.send_personal_message(buyer_message, buyer_id)
    
    async def notify_guild_activity(
        self,
        guild_id: int,
        member_ids: List[int],
        activity_type: str,
        details: Dict
    ):
        """Notify guild members of activity"""
        message = json.dumps({
            "type": "guild_activity",
            "guild_id": guild_id,
            "activity_type": activity_type,
            "details": details,
            "timestamp": asyncio.get_event_loop().time()
        })
        
        for member_id in member_ids:
            await self.send_personal_message(message, member_id)
    
    def get_active_users_count(self) -> int:
        """Get count of active users"""
        return len(self.active_connections)
    
    def get_user_connection_count(self, user_id: int) -> int:
        """Get number of connections for a user"""
        if user_id in self.active_connections:
            return len(self.active_connections[user_id])
        return 0


manager = ConnectionManager()
