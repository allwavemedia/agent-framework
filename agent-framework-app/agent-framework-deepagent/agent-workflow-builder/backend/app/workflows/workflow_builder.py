"""
Workflow builder for creating executable workflows using Microsoft Agent Framework.
"""
from typing import Dict, Any, List, Optional, Callable
from app.models import WorkflowResponse, WorkflowNodeResponse, WorkflowEdgeResponse, ExecutorType
from app.core.logging import get_logger
from app.agents.agent_factory import AgentFactory

logger = get_logger(__name__)

# Import Microsoft Agent Framework workflow components
try:
    from agent_framework import WorkflowBuilder as AFWorkflowBuilder
    from agent_framework import ChatAgent, WorkflowExecutionContext
    WORKFLOW_FRAMEWORK_AVAILABLE = True
    logger.info("Microsoft Agent Framework workflows available")
except ImportError as e:
    logger.warning(f"Microsoft Agent Framework workflows not available: {e}. Using mock implementations.")
    WORKFLOW_FRAMEWORK_AVAILABLE = False
    
    # Mock classes for development
    class AFWorkflowBuilder:
        def __init__(self, start_executor=None):
            self.start_executor = start_executor
            self.edges = []
        
        def add_edge(self, source, target, condition=None):
            self.edges.append({'source': source, 'target': target, 'condition': condition})
            return self
        
        def add_fan_out_edge(self, source, targets, partitioner=None):
            for target in targets:
                self.add_edge(source, target)
            return self
        
        def add_fan_in_edge(self, target, sources):
            for source in sources:
                self.add_edge(source, target)
            return self
        
        def add_switch(self, source, switch_builder):
            # Mock switch builder
            return self
        
        def with_output_from(self, *executors):
            return self
        
        def build(self):
            return MockWorkflow(self.start_executor, self.edges)
    
    class MockWorkflow:
        def __init__(self, start_executor=None, edges=None):
            self.start_executor = start_executor
            self.edges = edges or []
        
        async def run(self, input_data):
            return {"result": f"Mock workflow execution completed with input: {input_data}"}
        
        async def run_stream(self, input_data):
            yield {"type": "start", "data": f"Starting workflow with: {input_data}"}
            yield {"type": "progress", "data": "Processing..."}
            yield {"type": "complete", "data": f"Mock workflow completed with: {input_data}"}
    
    class WorkflowExecutionContext:
        async def send_message(self, message, target_id=None):
            logger.info(f"Mock context sending message: {message} to {target_id}")
    
    class ChatAgent:
        def __init__(self, name, instructions):
            self.name = name
            self.instructions = instructions


class WorkflowBuilder:
    """Builder for creating executable workflows using Microsoft Agent Framework."""
    
    def __init__(self):
        self.logger = get_logger(__name__)
        self.agent_factory = AgentFactory()
    
    async def build_workflow(self, workflow_config: WorkflowResponse) -> Any:
        """Build an executable workflow from configuration."""
        try:
            if not WORKFLOW_FRAMEWORK_AVAILABLE:
                return await self._build_mock_workflow(workflow_config)
            
            # Determine workflow pattern based on configuration
            pattern = workflow_config.tags[0] if workflow_config.tags else "custom"
            
            if pattern == "sequential":
                return await self._build_sequential_workflow(workflow_config)
            elif pattern == "concurrent":
                return await self._build_concurrent_workflow(workflow_config)
            elif pattern == "conditional":
                return await self._build_conditional_workflow(workflow_config)
            else:
                return await self._build_custom_workflow(workflow_config)
                
        except Exception as e:
            logger.error(f"Error building workflow {workflow_config.name}: {e}")
            raise
    
    async def _build_sequential_workflow(self, workflow_config: WorkflowResponse) -> Any:
        """Build a sequential workflow using WorkflowBuilder."""
        logger.info(f"Building sequential workflow: {workflow_config.name}")
        
        # Create agents/executors for each node
        executors = {}
        for node in workflow_config.nodes:
            executor_instance = await self._create_executor(node)
            executors[node.id] = executor_instance
        
        # Find start node
        start_node = self._find_start_node(workflow_config.nodes)
        if not start_node:
            raise ValueError("No start node found in workflow")
        
        start_executor = executors[start_node.id]
        builder = AFWorkflowBuilder(start_executor)
        
        # Add sequential edges based on workflow configuration
        for edge in workflow_config.edges:
            source_executor = executors.get(edge.source_node_id)
            target_executor = executors.get(edge.target_node_id)
            
            if source_executor and target_executor:
                builder.add_edge(source_executor, target_executor)
        
        # Set output executors
        output_executors = [executors[node.id] for node in workflow_config.nodes if node.is_output_node]
        if output_executors:
            builder.with_output_from(*output_executors)
        
        workflow = builder.build()
        logger.info(f"Built sequential workflow with {len(executors)} executors")
        return workflow
    
    async def _build_concurrent_workflow(self, workflow_config: WorkflowResponse) -> Any:
        """Build a concurrent workflow using fan-out/fan-in patterns."""
        logger.info(f"Building concurrent workflow: {workflow_config.name}")
        
        # Create agents/executors for each node
        executors = {}
        for node in workflow_config.nodes:
            executor_instance = await self._create_executor(node)
            executors[node.id] = executor_instance
        
        # Find start node
        start_node = self._find_start_node(workflow_config.nodes)
        if not start_node:
            raise ValueError("No start node found in workflow")
        
        start_executor = executors[start_node.id]
        builder = AFWorkflowBuilder(start_executor)
        
        # Group nodes by their concurrent groups
        concurrent_groups = self._group_concurrent_nodes(workflow_config.nodes, workflow_config.edges)
        
        for group in concurrent_groups:
            if len(group) > 1:
                # Fan-out to concurrent executors
                group_executors = [executors[node_id] for node_id in group if node_id in executors]
                if group_executors:
                    builder.add_fan_out_edge(start_executor, group_executors)
        
        # Set output executors
        output_executors = [executors[node.id] for node in workflow_config.nodes if node.is_output_node]
        if output_executors:
            builder.with_output_from(*output_executors)
        
        workflow = builder.build()
        logger.info(f"Built concurrent workflow with {len(executors)} executors")
        return workflow
    
    async def _build_conditional_workflow(self, workflow_config: WorkflowResponse) -> Any:
        """Build a conditional workflow using switch-case patterns."""
        logger.info(f"Building conditional workflow: {workflow_config.name}")
        
        # Create agents/executors for each node
        executors = {}
        for node in workflow_config.nodes:
            executor_instance = await self._create_executor(node)
            executors[node.id] = executor_instance
        
        # Find start node
        start_node = self._find_start_node(workflow_config.nodes)
        if not start_node:
            raise ValueError("No start node found in workflow")
        
        start_executor = executors[start_node.id]
        builder = AFWorkflowBuilder(start_executor)
        
        # Add conditional edges
        for edge in workflow_config.edges:
            source_executor = executors.get(edge.source_node_id)
            target_executor = executors.get(edge.target_node_id)
            
            if source_executor and target_executor:
                if edge.condition:
                    # Add conditional edge
                    condition_func = self._compile_condition(edge.condition)
                    builder.add_edge(source_executor, target_executor, condition=condition_func)
                else:
                    # Add regular edge
                    builder.add_edge(source_executor, target_executor)
        
        # Set output executors
        output_executors = [executors[node.id] for node in workflow_config.nodes if node.is_output_node]
        if output_executors:
            builder.with_output_from(*output_executors)
        
        workflow = builder.build()
        logger.info(f"Built conditional workflow with {len(executors)} executors")
        return workflow
    
    async def _build_custom_workflow(self, workflow_config: WorkflowResponse) -> Any:
        """Build a custom workflow using WorkflowBuilder."""
        logger.info(f"Building custom workflow: {workflow_config.name}")
        
        # Create workflow builder
        executors = {}
        for node in workflow_config.nodes:
            executor_instance = await self._create_executor(node)
            executors[node.id] = executor_instance
        
        # Find start node
        start_node = self._find_start_node(workflow_config.nodes)
        if not start_node:
            raise ValueError("No start node found in workflow")
        
        start_executor = executors[start_node.id]
        builder = AFWorkflowBuilder(start_executor)
        
        # Add edges to connect executors
        for edge in workflow_config.edges:
            source_executor = executors.get(edge.source_node_id)
            target_executor = executors.get(edge.target_node_id)
            
            if source_executor and target_executor:
                if edge.condition:
                    # Add conditional edge
                    condition_func = self._compile_condition(edge.condition)
                    builder.add_edge(source_executor, target_executor, condition=condition_func)
                else:
                    # Add regular edge
                    builder.add_edge(source_executor, target_executor)
        
        # Set output executors
        output_executors = [executors[node.id] for node in workflow_config.nodes if node.is_output_node]
        if output_executors:
            builder.with_output_from(*output_executors)
        
        # Build the workflow
        workflow = builder.build()
        logger.info(f"Built custom workflow: {workflow_config.name}")
        return workflow
    
    async def _build_mock_workflow(self, workflow_config: WorkflowResponse) -> Any:
        """Build a mock workflow for development."""
        logger.info(f"Building mock workflow: {workflow_config.name}")
        return MockWorkflow()
    
    async def _create_executor(self, node: WorkflowNodeResponse) -> Any:
        """Create an executor from a workflow node."""
        if not WORKFLOW_FRAMEWORK_AVAILABLE:
            return self._create_mock_executor(node)
        
        # Create executor based on node type
        if node.executor_type == ExecutorType.AGENT:
            return await self._create_agent_executor(node)
        elif node.executor_type == ExecutorType.FUNCTION:
            return await self._create_function_executor(node)
        elif node.executor_type == ExecutorType.CONDITION:
            return await self._create_condition_executor(node)
        elif node.executor_type == ExecutorType.HUMAN_INPUT:
            return await self._create_human_input_executor(node)
        else:
            return await self._create_custom_executor(node)
    
    def _create_mock_executor(self, node: WorkflowNodeResponse) -> Any:
        """Create a mock executor for development."""
        class MockExecutor:
            def __init__(self, node_id, name):
                self.id = node_id
                self.name = name
            
            async def handle(self, input_data, context=None):
                logger.info(f"Mock executor {self.name} processing: {input_data}")
                return f"Mock output from {self.name}"
        
        return MockExecutor(str(node.id), node.name)
    
    async def _create_agent_executor(self, node: WorkflowNodeResponse) -> Any:
        """Create an agent executor using an actual AI agent."""
        if node.agent_id:
            # Load agent from database and create agent instance
            # For now, create a workflow agent with the node's configuration
            agent = self.agent_factory.create_workflow_agent(
                name=node.name,
                instructions=node.config.get('instructions', f'You are an agent named {node.name}')
            )
            
            logger.info(f"Created agent executor for node: {node.name}")
            return agent
        else:
            # Create a simple mock agent
            class SimpleAgentExecutor:
                def __init__(self, node_id, name):
                    self.id = node_id
                    self.name = name
                
                async def handle(self, input_data, context=None):
                    logger.info(f"Simple agent executor {self.name} processing: {input_data}")
                    return f"Agent {self.name} response to: {input_data}"
            
            return SimpleAgentExecutor(str(node.id), node.name)
    
    async def _create_function_executor(self, node: WorkflowNodeResponse) -> Any:
        """Create a function executor."""
        class FunctionExecutor:
            def __init__(self, node_id, name, config):
                self.id = node_id
                self.name = name
                self.config = config
            
            async def handle(self, input_data, context=None):
                # Execute the function defined in node config
                function_code = self.config.get('function_code', 'return input_data.upper()')
                
                try:
                    # This is a simplified example - in production, you'd want proper sandboxing
                    result = eval(f"lambda input_data: {function_code}")(input_data)
                    return str(result)
                except Exception as e:
                    logger.error(f"Error in function executor {self.name}: {e}")
                    return f"Error: {str(e)}"
        
        return FunctionExecutor(str(node.id), node.name, node.config)
    
    async def _create_condition_executor(self, node: WorkflowNodeResponse) -> Any:
        """Create a condition executor."""
        class ConditionExecutor:
            def __init__(self, node_id, name, config):
                self.id = node_id
                self.name = name
                self.config = config
            
            async def handle(self, input_data, context=None):
                # Evaluate condition and return result
                condition = self.config.get('condition', 'True')
                
                try:
                    result = eval(f"lambda input_data: {condition}")(input_data)
                    return {"condition_result": result, "data": input_data}
                except Exception as e:
                    logger.error(f"Error in condition executor {self.name}: {e}")
                    return {"condition_result": False, "data": input_data}
        
        return ConditionExecutor(str(node.id), node.name, node.config)
    
    async def _create_human_input_executor(self, node: WorkflowNodeResponse) -> Any:
        """Create a human input executor."""
        class HumanInputExecutor:
            def __init__(self, node_id, name, config):
                self.id = node_id
                self.name = name
                self.config = config
            
            async def handle(self, input_data, context=None):
                # Request human input
                prompt = self.config.get('prompt', 'Please provide input:')
                
                # This would integrate with the WebSocket system for real human input
                # For now, just return a request for input
                logger.info(f"Human input requested: {prompt}")
                return {
                    "type": "human_input_required",
                    "prompt": prompt,
                    "current_data": input_data
                }
        
        return HumanInputExecutor(str(node.id), node.name, node.config)
    
    async def _create_custom_executor(self, node: WorkflowNodeResponse) -> Any:
        """Create a custom executor."""
        class CustomExecutor:
            def __init__(self, node_id, name, config):
                self.id = node_id
                self.name = name
                self.config = config
            
            async def handle(self, input_data, context=None):
                # Execute custom logic defined in node config
                logger.info(f"Custom executor {self.name} processing: {input_data}")
                
                # This would execute custom code or call external services
                return f"Custom processing result from {self.name}"
        
        return CustomExecutor(str(node.id), node.name, node.config)
    
    def _compile_condition(self, condition_str: str) -> Callable:
        """Compile a condition string into a callable."""
        try:
            # This is a simplified example - in production, you'd want proper parsing and validation
            return eval(f"lambda data: {condition_str}")
        except Exception as e:
            logger.error(f"Error compiling condition '{condition_str}': {e}")
            return lambda data: True
    
    def _find_start_node(self, nodes: List[WorkflowNodeResponse]) -> Optional[WorkflowNodeResponse]:
        """Find the start node in the workflow."""
        for node in nodes:
            if node.is_start_node:
                return node
        
        # If no explicit start node, return the first node
        return nodes[0] if nodes else None
    
    def _group_concurrent_nodes(self, nodes: List[WorkflowNodeResponse], edges: List[WorkflowEdgeResponse]) -> List[List[str]]:
        """Group nodes that should execute concurrently."""
        # This is a simplified implementation
        # In a real implementation, you'd analyze the graph to find concurrent execution groups
        concurrent_groups = []
        
        # For now, just return individual nodes as groups
        for node in nodes:
            if not node.is_start_node:
                concurrent_groups.append([str(node.id)])
        
        return concurrent_groups
    
    def get_supported_patterns(self) -> List[str]:
        """Get list of supported workflow patterns."""
        if not WORKFLOW_FRAMEWORK_AVAILABLE:
            return ['custom', 'mock']
        
        return [
            'sequential',   # Sequential execution
            'concurrent',   # Concurrent execution with fan-out/fan-in
            'conditional',  # Conditional routing with switch-case
            'custom'        # Custom workflow builder
        ]