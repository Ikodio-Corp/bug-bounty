"""
WebSocket Routes for Real-time Updates
"""

from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from core.websocket import manager
from core.database import get_async_session
from services.auth_service import get_current_user_ws
from models.user import User


router = APIRouter()


@router.websocket("/ws/{user_id}")
async def websocket_endpoint(
    websocket: WebSocket,
    user_id: int,
    current_user: User = Depends(get_current_user_ws)
):
    """
    WebSocket endpoint for real-time user notifications
    """
    if current_user.id != user_id:
        await websocket.close(code=1008)
        return
    
    await manager.connect(websocket, user_id)
    
    try:
        while True:
            data = await websocket.receive_text()
    
    except WebSocketDisconnect:
        manager.disconnect(websocket, user_id)


@router.websocket("/ws/scan/{scan_id}")
async def scan_websocket_endpoint(
    websocket: WebSocket,
    scan_id: int,
    current_user: User = Depends(get_current_user_ws)
):
    """
    WebSocket endpoint for real-time scan updates
    """
    await manager.connect(websocket, current_user.id)
    await manager.subscribe_to_scan(websocket, scan_id)
    
    try:
        while True:
            data = await websocket.receive_text()
    
    except WebSocketDisconnect:
        manager.unsubscribe_from_scan(websocket, scan_id)
        manager.disconnect(websocket, current_user.id)


@router.get("/ws/stats")
async def get_websocket_stats():
    """Get WebSocket connection statistics"""
    return {
        "active_users": manager.get_active_users_count(),
        "total_connections": sum(
            manager.get_user_connection_count(user_id)
            for user_id in manager.active_connections.keys()
        )
    }
