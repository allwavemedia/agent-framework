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
from app.services.execution_service import ExecutionService
from app.workflows.workflow_executor import WorkflowExecutor
from app.core.logging import get_logger

logger = get_logger(__name__)

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
        logger.error(f"WebSocket error: {e}")
        websocket_manager.disconnect(websocket)


@router.websocket("/execution/{execution_id}")
async def execution_websocket(
    websocket: WebSocket, 
    execution_id: int,
    db: Session = Depends(get_db)
):
    """WebSocket endpoint for specific execution monitoring with real-time streaming.
    
    This endpoint provides real-time updates for workflow execution including:
    - Execution start/stop events
    - Workflow progress updates
    - Agent execution events
    - Error notifications
    - Completion status
    """
    await websocket_manager.connect_to_execution(websocket, execution_id)
    
    # Create execution service to fetch workflow details
    execution_service = ExecutionService(db)
    workflow_executor = WorkflowExecutor()
    
    try:
        # Start streaming task in background
        async def stream_execution():
            """Stream execution events to the connected WebSocket."""
            try:
                # Get execution details
                execution = await execution_service.get_execution(execution_id)
                if not execution:
                    await websocket_manager.send_personal_message({
                        "type": "error",
                        "data": {
                            "message": f"Execution {execution_id} not found",
                            "execution_id": execution_id
                        }
                    }, websocket)
                    return
                
                # Get workflow
                workflow = await execution_service.get_workflow_for_execution(execution_id)
                if not workflow:
                    await websocket_manager.send_personal_message({
                        "type": "error", 
                        "data": {
                            "message": "Workflow not found for execution",
                            "execution_id": execution_id
                        }
                    }, websocket)
                    return
                
                # Stream workflow execution events
                async for event in workflow_executor.execute_with_events(
                    workflow=workflow.workflow_obj,  # Actual Agent Framework workflow
                    input_data=execution.input_data,
                    execution_id=execution_id
                ):
                    # Broadcast event to all connected clients monitoring this execution
                    await websocket_manager.broadcast_to_execution(execution_id, {
                        "type": "execution_event",
                        "data": event
                    })
                    
            except Exception as e:
                logger.error(f"Error streaming execution {execution_id}: {e}")
                await websocket_manager.send_personal_message({
                    "type": "error",
                    "data": {
                        "message": f"Error streaming execution: {str(e)}",
                        "execution_id": execution_id
                    }
                }, websocket)
        
        # Start streaming in background
        stream_task = asyncio.create_task(stream_execution())
        
        # Handle client messages while streaming
        while True:
            # Keep connection alive and handle any client messages
            data = await websocket.receive_text()
            message_data = json.loads(data)
            
            # Handle execution-specific messages
            message_type = message_data.get("type")
            
            if message_type == "cancel_execution":
                # Cancel the execution
                stream_task.cancel()
                await websocket_manager.send_personal_message({
                    "type": "execution_cancelled",
                    "data": {"execution_id": execution_id}
                }, websocket)
                break
            else:
                await websocket_manager.handle_execution_message(
                    websocket, execution_id, message_data
                )
            
    except WebSocketDisconnect:
        logger.info(f"WebSocket disconnected from execution {execution_id}")
        websocket_manager.disconnect_from_execution(websocket, execution_id)
    except Exception as e:
        logger.error(f"Execution WebSocket error: {e}")
        websocket_manager.disconnect_from_execution(websocket, execution_id)
    finally:
        # Clean up streaming task if still running
        if 'stream_task' in locals() and not stream_task.done():
            stream_task.cancel()
            try:
                await stream_task
            except asyncio.CancelledError:
                pass


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