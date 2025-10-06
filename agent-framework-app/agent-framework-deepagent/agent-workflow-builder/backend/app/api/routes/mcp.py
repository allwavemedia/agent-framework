"""
API routes for MCP (Model Context Protocol) integration.
"""
from fastapi import APIRouter, HTTPException, Depends
from typing import Dict, List, Any
from app.services.mcp_service import MCPService
from app.core.logging import get_logger

logger = get_logger(__name__)
router = APIRouter(prefix="/mcp", tags=["mcp"])

# Dependency to get MCP service instance
async def get_mcp_service() -> MCPService:
    """Get MCP service instance."""
    return MCPService()


@router.get("/status")
async def get_mcp_status(mcp_service: MCPService = Depends(get_mcp_service)) -> Dict[str, Any]:
    """Get the status of MCP integration."""
    try:
        return mcp_service.get_mcp_integration_status()
    except Exception as e:
        logger.error(f"Error getting MCP status: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/connect")
async def connect_mcp_servers(mcp_service: MCPService = Depends(get_mcp_service)) -> Dict[str, str]:
    """Connect to all configured MCP servers."""
    try:
        await mcp_service.connect_mcp_servers()
        return {"message": "Successfully connected to MCP servers"}
    except Exception as e:
        logger.error(f"Error connecting to MCP servers: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/tools")
async def get_available_tools(mcp_service: MCPService = Depends(get_mcp_service)) -> Dict[str, List[Dict[str, Any]]]:
    """Get all available MCP tools across servers."""
    try:
        return mcp_service.get_available_tools()
    except Exception as e:
        logger.error(f"Error getting available tools: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/tools/microsoft-learn")
async def get_microsoft_learn_tools(mcp_service: MCPService = Depends(get_mcp_service)) -> List[Dict[str, Any]]:
    """Get available tools from Microsoft Learn MCP Server."""
    try:
        return mcp_service.get_microsoft_learn_tools()
    except Exception as e:
        logger.error(f"Error getting Microsoft Learn tools: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/tools/context7")
async def get_context7_tools(mcp_service: MCPService = Depends(get_mcp_service)) -> List[Dict[str, Any]]:
    """Get available tools from Context7 MCP Server."""
    try:
        return mcp_service.get_context7_tools()
    except Exception as e:
        logger.error(f"Error getting Context7 tools: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/resources")
async def get_available_resources(mcp_service: MCPService = Depends(get_mcp_service)) -> Dict[str, List[Dict[str, Any]]]:
    """Get all available MCP resources across servers."""
    try:
        return mcp_service.get_available_resources()
    except Exception as e:
        logger.error(f"Error getting available resources: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/search/microsoft-docs")
async def search_microsoft_docs(
    query: str,
    limit: int = 10,
    mcp_service: MCPService = Depends(get_mcp_service)
) -> Dict[str, Any]:
    """Search Microsoft documentation using Microsoft Learn MCP tools."""
    try:
        return await mcp_service.search_microsoft_docs(query, limit)
    except Exception as e:
        logger.error(f"Error searching Microsoft docs: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/code-samples")
async def get_code_samples(
    technology: str,
    language: str = "python",
    mcp_service: MCPService = Depends(get_mcp_service)
) -> Dict[str, Any]:
    """Get code samples using Microsoft Learn MCP tools."""
    try:
        return await mcp_service.get_code_samples(technology, language)
    except Exception as e:
        logger.error(f"Error getting code samples: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/search/library-docs")
async def search_library_docs(
    library_name: str,
    mcp_service: MCPService = Depends(get_mcp_service)
) -> Dict[str, Any]:
    """Search library documentation using Context7 MCP tools."""
    try:
        return await mcp_service.search_library_docs(library_name)
    except Exception as e:
        logger.error(f"Error searching library docs: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/tool/call")
async def call_mcp_tool(
    server_name: str,
    tool_name: str,
    arguments: Dict[str, Any],
    mcp_service: MCPService = Depends(get_mcp_service)
) -> Dict[str, Any]:
    """Call an MCP tool from a specific server."""
    try:
        return await mcp_service.call_mcp_tool(server_name, tool_name, arguments)
    except Exception as e:
        logger.error(f"Error calling MCP tool: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/resource/read")
async def read_mcp_resource(
    server_name: str,
    resource_uri: str,
    mcp_service: MCPService = Depends(get_mcp_service)
) -> Dict[str, Any]:
    """Read a resource from an MCP server."""
    try:
        return await mcp_service.read_mcp_resource(server_name, resource_uri)
    except Exception as e:
        logger.error(f"Error reading MCP resource: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/agent/create-with-tools")
async def create_agent_with_mcp_tools(
    agent_name: str,
    instructions: str,
    mcp_tools: List[str],
    mcp_service: MCPService = Depends(get_mcp_service)
) -> Dict[str, Any]:
    """Create an agent configuration that includes MCP tools."""
    try:
        return await mcp_service.create_agent_with_mcp_tools(agent_name, instructions, mcp_tools)
    except Exception as e:
        logger.error(f"Error creating agent with MCP tools: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/workflow/execute-step")
async def execute_mcp_workflow_step(
    step_config: Dict[str, Any],
    mcp_service: MCPService = Depends(get_mcp_service)
) -> Dict[str, Any]:
    """Execute a workflow step that uses MCP tools."""
    try:
        return await mcp_service.execute_mcp_workflow_step(step_config)
    except Exception as e:
        logger.error(f"Error executing MCP workflow step: {e}")
        raise HTTPException(status_code=500, detail=str(e))