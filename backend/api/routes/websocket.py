"""
WebSocket routes for real-time features
"""

from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends
from sqlalchemy.orm import Session
import json

from core.database import get_db
from core.websocket_manager import manager
from middleware.auth import decode_token

router = APIRouter()


@router.websocket("/ws/{token}")
async def websocket_endpoint(
    websocket: WebSocket,
    token: str,
    db: Session = Depends(get_db)
):
    """Main WebSocket endpoint"""
    try:
        payload = decode_token(token)
        user_id = payload.get("sub")
        
        if not user_id:
            await websocket.close(code=1008)
            return
        
        await manager.connect(websocket, user_id)
        
        try:
            while True:
                data = await websocket.receive_text()
                message = json.loads(data)
                
                message_type = message.get("type")
                
                if message_type == "subscribe_scan":
                    scan_id = message.get("scan_id")
                    await manager.subscribe_to_scan(scan_id, user_id)
                
                elif message_type == "unsubscribe_scan":
                    scan_id = message.get("scan_id")
                    await manager.unsubscribe_from_scan(scan_id, user_id)
                
                elif message_type == "join_guild":
                    guild_id = message.get("guild_id")
                    await manager.join_guild_channel(guild_id, user_id)
                
                elif message_type == "leave_guild":
                    guild_id = message.get("guild_id")
                    await manager.leave_guild_channel(guild_id, user_id)
                
                elif message_type == "guild_message":
                    guild_id = message.get("guild_id")
                    content = message.get("content")
                    await manager.broadcast_to_guild(guild_id, {
                        "user_id": user_id,
                        "content": content
                    })
                
                elif message_type == "ping":
                    await websocket.send_json({"type": "pong"})
        
        except WebSocketDisconnect:
            manager.disconnect(websocket, user_id)
    
    except Exception as e:
        await websocket.close(code=1011)


@router.websocket("/ws/scans/{scan_id}")
async def scan_websocket(
    websocket: WebSocket,
    scan_id: int
):
    """WebSocket for specific scan updates"""
    await websocket.accept()
    
    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        pass


@router.websocket("/ws/guilds/{guild_id}")
async def guild_websocket(
    websocket: WebSocket,
    guild_id: int
):
    """WebSocket for guild chat"""
    await websocket.accept()
    
    try:
        while True:
            data = await websocket.receive_text()
            message = json.loads(data)
            
            await manager.broadcast_to_guild(guild_id, message)
    except WebSocketDisconnect:
        pass
