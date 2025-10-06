"""
WebSocket service for real-time communication.
"""
import json
import asyncio
from typing import Dict, List, Any, Set
from fastapi import WebSocket
from datetime import datetime

from app.models import WebSocketMessage, WorkflowExecutionEvent
from app.core.logging import get_logger

logger = get_logger(__name__)


class WebSocketManager:
    """Manager for WebSocket connections."""
    
    def __init__(self):
        # All active connections
        self.active_connections: List[WebSocket] = []
        
        # Connections monitoring specific executions
        self.execution_connections: Dict[int, Set[WebSocket]] = {}
        
        # Connection metadata
        self.connection_metadata: Dict[WebSocket, Dict[str, Any]] = {}
    
    async def connect(self, websocket: WebSocket) -> None:
        """Accept a new WebSocket connection."""
        await websocket.accept()
        self.active_connections.append(websocket)
        self.connection_metadata[websocket] = {
            "connected_at": datetime.utcnow(),
            "type": "general"
        }
        
        logger.info(f"WebSocket connected. Total connections: {len(self.active_connections)}")
        
        # Send welcome message
        await self.send_personal_message({
            "type": "connection_established",
            "data": {
                "message": "Connected to Agent Workflow Builder",
                "timestamp": datetime.utcnow().isoformat()
            }
        }, websocket)
    
    def disconnect(self, websocket: WebSocket) -> None:
        """Remove a WebSocket connection."""
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)
        
        # Remove from execution connections
        for execution_id, connections in self.execution_connections.items():
            if websocket in connections:
                connections.remove(websocket)
        
        # Clean up empty execution connection sets
        self.execution_connections = {
            k: v for k, v in self.execution_connections.items() if v
        }
        
        # Remove metadata
        if websocket in self.connection_metadata:
            del self.connection_metadata[websocket]
        
        logger.info(f"WebSocket disconnected. Total connections: {len(self.active_connections)}")
    
    async def connect_to_execution(self, websocket: WebSocket, execution_id: int) -> None:
        """Connect a WebSocket to monitor a specific execution."""
        await websocket.accept()
        
        if websocket not in self.active_connections:
            self.active_connections.append(websocket)
        
        if execution_id not in self.execution_connections:
            self.execution_connections[execution_id] = set()
        
        self.execution_connections[execution_id].add(websocket)
        
        self.connection_metadata[websocket] = {
            "connected_at": datetime.utcnow(),
            "type": "execution",
            "execution_id": execution_id
        }
        
        logger.info(f"WebSocket connected to execution {execution_id}")
        
        # Send welcome message
        await self.send_personal_message({
            "type": "execution_connection_established",
            "data": {
                "execution_id": execution_id,
                "message": f"Connected to execution {execution_id}",
                "timestamp": datetime.utcnow().isoformat()
            }
        }, websocket)
    
    def disconnect_from_execution(self, websocket: WebSocket, execution_id: int) -> None:
        """Disconnect a WebSocket from monitoring a specific execution."""
        if execution_id in self.execution_connections:
            self.execution_connections[execution_id].discard(websocket)
            
            if not self.execution_connections[execution_id]:
                del self.execution_connections[execution_id]
        
        self.disconnect(websocket)
    
    async def send_personal_message(self, message: Dict[str, Any], websocket: WebSocket) -> None:
        """Send a message to a specific WebSocket connection."""
        try:
            await websocket.send_text(json.dumps(message))
        except Exception as e:
            logger.error(f"Error sending personal message: {e}")
            self.disconnect(websocket)
    
    async def broadcast(self, message: Dict[str, Any]) -> None:
        """Broadcast a message to all connected clients."""
        if not self.active_connections:
            return
        
        message_text = json.dumps(message)
        disconnected = []
        
        for connection in self.active_connections:
            try:
                await connection.send_text(message_text)
            except Exception as e:
                logger.error(f"Error broadcasting message: {e}")
                disconnected.append(connection)
        
        # Clean up disconnected connections
        for connection in disconnected:
            self.disconnect(connection)
    
    async def broadcast_to_execution(self, execution_id: int, message: Dict[str, Any]) -> None:
        """Broadcast a message to clients monitoring a specific execution."""
        if execution_id not in self.execution_connections:
            return
        
        connections = self.execution_connections[execution_id].copy()
        if not connections:
            return
        
        message_text = json.dumps(message)
        disconnected = []
        
        for connection in connections:
            try:
                await connection.send_text(message_text)
            except Exception as e:
                logger.error(f"Error broadcasting to execution {execution_id}: {e}")
                disconnected.append(connection)
        
        # Clean up disconnected connections
        for connection in disconnected:
            self.disconnect_from_execution(connection, execution_id)
    
    async def handle_message(self, websocket: WebSocket, message_data: Dict[str, Any]) -> None:
        """Handle incoming message from a WebSocket client."""
        message_type = message_data.get("type")
        
        if message_type == "ping":
            await self.send_personal_message({
                "type": "pong",
                "data": {"timestamp": datetime.utcnow().isoformat()}
            }, websocket)
        
        elif message_type == "subscribe_execution":
            execution_id = message_data.get("execution_id")
            if execution_id:
                if execution_id not in self.execution_connections:
                    self.execution_connections[execution_id] = set()
                self.execution_connections[execution_id].add(websocket)
                
                await self.send_personal_message({
                    "type": "subscribed_to_execution",
                    "data": {"execution_id": execution_id}
                }, websocket)
        
        elif message_type == "unsubscribe_execution":
            execution_id = message_data.get("execution_id")
            if execution_id and execution_id in self.execution_connections:
                self.execution_connections[execution_id].discard(websocket)
                
                await self.send_personal_message({
                    "type": "unsubscribed_from_execution",
                    "data": {"execution_id": execution_id}
                }, websocket)
        
        else:
            logger.warning(f"Unknown message type: {message_type}")
    
    async def handle_execution_message(self, websocket: WebSocket, execution_id: int, message_data: Dict[str, Any]) -> None:
        """Handle execution-specific messages."""
        message_type = message_data.get("type")
        
        if message_type == "get_status":
            # This would typically fetch the current execution status
            # For now, just acknowledge the request
            await self.send_personal_message({
                "type": "execution_status",
                "data": {
                    "execution_id": execution_id,
                    "status": "running",  # This should come from the execution service
                    "timestamp": datetime.utcnow().isoformat()
                }
            }, websocket)
        
        else:
            logger.warning(f"Unknown execution message type: {message_type}")
    
    def get_connection_count(self) -> int:
        """Get the total number of active connections."""
        return len(self.active_connections)
    
    def get_execution_connections(self) -> Dict[int, int]:
        """Get the number of connections per execution."""
        return {
            execution_id: len(connections)
            for execution_id, connections in self.execution_connections.items()
        }
    
    async def notify_execution_event(self, execution_id: int, event: WorkflowExecutionEvent) -> None:
        """Notify clients about an execution event."""
        await self.broadcast_to_execution(execution_id, {
            "type": "execution_event",
            "data": event.dict()
        })