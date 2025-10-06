"""
WebSocket API routes for real-time communication.
"""
import json
import asyncio
from typing import Dict, Any
from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends
from sqlmodel import Session

from app.core.database import get_db
from app.models import WebSocketMessage, WorkflowExecutionEvent
from app.services.websocket_service import WebSocketManager

router = APIRouter()

# Global WebSocket manager
websocket_manager = WebSocketManager()


@router.websocket("/connect")
async def websocket_endpoint(websocket: WebSocket):
    """Main WebSocket endpoint for real-time communication."""
    await websocket_manager.connect(websocket)
    
    try:
        while True:
            # Receive message from client
            data = await websocket.receive_text()
            message_data = json.loads(data)
            
            # Process the message
            await websocket_manager.handle_message(websocket, message_data)
            
    except WebSocketDisconnect:
        websocket_manager.disconnect(websocket)
    except Exception as e:
        print(f"WebSocket error: {e}")
        websocket_manager.disconnect(websocket)


@router.websocket("/execution/{execution_id}")
async def execution_websocket(websocket: WebSocket, execution_id: int):
    """WebSocket endpoint for specific execution monitoring."""
    await websocket_manager.connect_to_execution(websocket, execution_id)
    
    try:
        while True:
            # Keep connection alive and handle any client messages
            data = await websocket.receive_text()
            message_data = json.loads(data)
            
            # Handle execution-specific messages
            await websocket_manager.handle_execution_message(
                websocket, execution_id, message_data
            )
            
    except WebSocketDisconnect:
        websocket_manager.disconnect_from_execution(websocket, execution_id)
    except Exception as e:
        print(f"Execution WebSocket error: {e}")
        websocket_manager.disconnect_from_execution(websocket, execution_id)


# HTTP endpoints for WebSocket management
@router.get("/connections")
async def get_active_connections():
    """Get information about active WebSocket connections."""
    return {
        "total_connections": websocket_manager.get_connection_count(),
        "execution_connections": websocket_manager.get_execution_connections(),
    }


@router.post("/broadcast")
async def broadcast_message(message: WebSocketMessage):
    """Broadcast a message to all connected clients."""
    await websocket_manager.broadcast(message.dict())
    return {"message": "Message broadcasted successfully"}


@router.post("/execution/{execution_id}/broadcast")
async def broadcast_to_execution(execution_id: int, message: WorkflowExecutionEvent):
    """Broadcast a message to clients monitoring a specific execution."""
    await websocket_manager.broadcast_to_execution(execution_id, message.dict())
    return {"message": f"Message broadcasted to execution {execution_id}"}