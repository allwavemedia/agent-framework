"""
MCP (Model Context Protocol) service for integrating with Microsoft Learn MCP Server 
and Context7 MCP tools as requested by the user.
"""
from typing import Dict, List, Any
from app.core.logging import get_logger

logger = get_logger(__name__)

# MCP Client integration
try:
    from modelcontextprotocol import Client, types as mcp_types
    MCP_AVAILABLE = True
    logger.info("Model Context Protocol client available")
except ImportError as e:
    logger.warning(f"MCP client not available: {e}. Using mock implementation.")
    MCP_AVAILABLE = False
    
    # Mock MCP types for development
    class MockMCPTypes:
        Tool = dict
        Resource = dict
        Prompt = dict
    
    mcp_types = MockMCPTypes()
    
    class Client:
        def __init__(self, *args, **kwargs):
            pass
        
        async def connect(self):
            pass
        
        async def list_tools(self):
            return []
        
        async def call_tool(self, name, arguments):
            return {"result": f"Mock MCP tool call: {name} with {arguments}"}
        
        async def list_resources(self):
            return []
        
        async def read_resource(self, uri):
            return {"content": f"Mock resource content for {uri}"}


class MCPService:
    """Service for integrating with MCP servers and tools."""
    
    def __init__(self):
        self.clients = {}
        self.available_tools = {}
        self.available_resources = {}
        self._initialize_mcp_clients()
    
    def _initialize_mcp_clients(self):
        """Initialize MCP clients for different servers."""
        try:
            if not MCP_AVAILABLE:
                logger.warning("MCP not available, using mock clients")
                self.clients['mock'] = Client()
                return
            
            # Initialize Microsoft Learn MCP Server client
            self.clients['microsoft_learn'] = Client()
            logger.info("Microsoft Learn MCP client initialized")
            
            # Initialize Context7 MCP client 
            self.clients['context7'] = Client()
            logger.info("Context7 MCP client initialized")
            
        except Exception as e:
            logger.error(f"Error initializing MCP clients: {e}")
            # Fallback to mock client
            self.clients['mock'] = Client()
    
    async def connect_mcp_servers(self):
        """Connect to all MCP servers."""
        try:
            for server_name, client in self.clients.items():
                await client.connect()
                logger.info(f"Connected to MCP server: {server_name}")
                
                # List available tools and resources
                await self._discover_tools(server_name, client)
                await self._discover_resources(server_name, client)
                
        except Exception as e:
            logger.error(f"Error connecting to MCP servers: {e}")
    
    async def _discover_tools(self, server_name: str, client: Client):
        """Discover available tools from an MCP server."""
        try:
            tools = await client.list_tools()
            self.available_tools[server_name] = tools
            logger.info(f"Discovered {len(tools)} tools from {server_name}")
            
            for tool in tools:
                tool_name = tool.get('name', 'unknown')
                logger.debug(f"Tool discovered: {tool_name} from {server_name}")
                
        except Exception as e:
            logger.error(f"Error discovering tools from {server_name}: {e}")
    
    async def _discover_resources(self, server_name: str, client: Client):
        """Discover available resources from an MCP server."""
        try:
            resources = await client.list_resources()
            self.available_resources[server_name] = resources
            logger.info(f"Discovered {len(resources)} resources from {server_name}")
            
            for resource in resources:
                resource_uri = resource.get('uri', 'unknown')
                logger.debug(f"Resource discovered: {resource_uri} from {server_name}")
                
        except Exception as e:
            logger.error(f"Error discovering resources from {server_name}: {e}")
    
    async def call_mcp_tool(self, server_name: str, tool_name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Call an MCP tool from a specific server."""
        try:
            if server_name not in self.clients:
                raise ValueError(f"MCP server '{server_name}' not available")
            
            client = self.clients[server_name]
            result = await client.call_tool(tool_name, arguments)
            
            logger.info(f"MCP tool call successful: {server_name}.{tool_name}")
            return result
            
        except Exception as e:
            logger.error(f"Error calling MCP tool {server_name}.{tool_name}: {e}")
            return {"error": str(e)}
    
    async def read_mcp_resource(self, server_name: str, resource_uri: str) -> Dict[str, Any]:
        """Read a resource from an MCP server."""
        try:
            if server_name not in self.clients:
                raise ValueError(f"MCP server '{server_name}' not available")
            
            client = self.clients[server_name]
            result = await client.read_resource(resource_uri)
            
            logger.info(f"MCP resource read successful: {server_name} - {resource_uri}")
            return result
            
        except Exception as e:
            logger.error(f"Error reading MCP resource {server_name} - {resource_uri}: {e}")
            return {"error": str(e)}
    
    async def call_microsoft_learn_tool(self, tool_name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Call a tool from Microsoft Learn MCP Server."""
        return await self.call_mcp_tool('microsoft_learn', tool_name, arguments)
    
    async def call_context7_tool(self, tool_name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Call a tool from Context7 MCP Server."""
        return await self.call_mcp_tool('context7', tool_name, arguments)
    
    async def search_microsoft_docs(self, query: str, limit: int = 10) -> Dict[str, Any]:
        """Search Microsoft documentation using Microsoft Learn MCP tools."""
        try:
            # Call Microsoft Learn MCP tool for documentation search
            arguments = {
                "query": query,
                "limit": limit,
                "include_code_samples": True
            }
            
            result = await self.call_microsoft_learn_tool('search_docs', arguments)
            logger.info(f"Microsoft docs search completed for query: {query}")
            return result
            
        except Exception as e:
            logger.error(f"Error searching Microsoft docs: {e}")
            return {"error": str(e), "results": []}
    
    async def get_code_samples(self, technology: str, language: str = "python") -> Dict[str, Any]:
        """Get code samples using Microsoft Learn MCP tools."""
        try:
            # Call Microsoft Learn MCP tool for code samples
            arguments = {
                "technology": technology,
                "language": language,
                "include_explanations": True
            }
            
            result = await self.call_microsoft_learn_tool('get_code_samples', arguments)
            logger.info(f"Code samples retrieved for: {technology} ({language})")
            return result
            
        except Exception as e:
            logger.error(f"Error getting code samples: {e}")
            return {"error": str(e), "samples": []}
    
    async def search_library_docs(self, library_name: str) -> Dict[str, Any]:
        """Search library documentation using Context7 MCP tools."""
        try:
            # Call Context7 MCP tool for library documentation
            arguments = {
                "library": library_name,
                "include_examples": True,
                "include_api_reference": True
            }
            
            result = await self.call_context7_tool('search_library', arguments)
            logger.info(f"Library docs search completed for: {library_name}")
            return result
            
        except Exception as e:
            logger.error(f"Error searching library docs: {e}")
            return {"error": str(e), "documentation": []}
    
    def get_available_tools(self) -> Dict[str, List[Dict[str, Any]]]:
        """Get all available MCP tools across servers."""
        return self.available_tools.copy()
    
    def get_available_resources(self) -> Dict[str, List[Dict[str, Any]]]:
        """Get all available MCP resources across servers."""
        return self.available_resources.copy()
    
    def get_microsoft_learn_tools(self) -> List[Dict[str, Any]]:
        """Get available tools from Microsoft Learn MCP Server."""
        return self.available_tools.get('microsoft_learn', [])
    
    def get_context7_tools(self) -> List[Dict[str, Any]]:
        """Get available tools from Context7 MCP Server."""
        return self.available_tools.get('context7', [])
    
    async def create_agent_with_mcp_tools(self, agent_name: str, instructions: str, mcp_tools: List[str]) -> Dict[str, Any]:
        """Create an agent configuration that includes MCP tools."""
        try:
            # Create agent configuration with MCP tools
            agent_config = {
                "name": agent_name,
                "instructions": instructions,
                "mcp_tools": [],
                "capabilities": []
            }
            
            # Add requested MCP tools
            for tool_spec in mcp_tools:
                if '.' in tool_spec:
                    server_name, tool_name = tool_spec.split('.', 1)
                    
                    # Verify tool exists
                    server_tools = self.available_tools.get(server_name, [])
                    tool_exists = any(tool.get('name') == tool_name for tool in server_tools)
                    
                    if tool_exists:
                        agent_config["mcp_tools"].append({
                            "server": server_name,
                            "tool": tool_name,
                            "spec": tool_spec
                        })
                        agent_config["capabilities"].append(f"Can use {tool_spec}")
                    else:
                        logger.warning(f"MCP tool not found: {tool_spec}")
            
            logger.info(f"Created agent config with {len(agent_config['mcp_tools'])} MCP tools")
            return agent_config
            
        except Exception as e:
            logger.error(f"Error creating agent with MCP tools: {e}")
            return {"error": str(e)}
    
    async def execute_mcp_workflow_step(self, step_config: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a workflow step that uses MCP tools."""
        try:
            step_type = step_config.get('type', 'unknown')
            
            if step_type == 'microsoft_docs_search':
                query = step_config.get('query', '')
                return await self.search_microsoft_docs(query)
            
            elif step_type == 'code_samples':
                technology = step_config.get('technology', '')
                language = step_config.get('language', 'python')
                return await self.get_code_samples(technology, language)
            
            elif step_type == 'library_docs':
                library = step_config.get('library', '')
                return await self.search_library_docs(library)
            
            elif step_type == 'custom_mcp_call':
                server = step_config.get('server', '')
                tool = step_config.get('tool', '')
                arguments = step_config.get('arguments', {})
                return await self.call_mcp_tool(server, tool, arguments)
            
            else:
                return {"error": f"Unknown MCP workflow step type: {step_type}"}
                
        except Exception as e:
            logger.error(f"Error executing MCP workflow step: {e}")
            return {"error": str(e)}
    
    def get_mcp_integration_status(self) -> Dict[str, Any]:
        """Get the status of MCP integration."""
        return {
            "mcp_available": MCP_AVAILABLE,
            "connected_servers": list(self.clients.keys()),
            "total_tools": sum(len(tools) for tools in self.available_tools.values()),
            "total_resources": sum(len(resources) for resources in self.available_resources.values()),
            "microsoft_learn_connected": 'microsoft_learn' in self.clients,
            "context7_connected": 'context7' in self.clients
        }