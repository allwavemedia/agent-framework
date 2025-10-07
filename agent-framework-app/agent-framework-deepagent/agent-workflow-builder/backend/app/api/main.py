"""
Main API router.
"""
from fastapi import APIRouter

from app.api.routes import agents, workflows, executions, websocket, mcp, checkpoints

api_router = APIRouter()

# Include all route modules
api_router.include_router(agents.router, prefix="/agents", tags=["agents"])
api_router.include_router(workflows.router, prefix="/workflows", tags=["workflows"])
api_router.include_router(executions.router, prefix="/executions", tags=["executions"])
api_router.include_router(websocket.router, prefix="/ws", tags=["websocket"])
api_router.include_router(mcp.router, prefix="/mcp", tags=["mcp"])
api_router.include_router(checkpoints.router, prefix="/checkpoints", tags=["checkpoints"])