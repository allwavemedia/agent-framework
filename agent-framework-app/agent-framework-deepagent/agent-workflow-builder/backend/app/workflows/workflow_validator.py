"""
Workflow validator for validating workflow structure and integrity.
"""
from typing import Dict, List, Any, Set, Tuple
from app.models import WorkflowResponse, WorkflowNodeResponse, WorkflowEdgeResponse
from app.core.logging import get_logger

logger = get_logger(__name__)


class WorkflowValidator:
    """Validator for workflow structures."""
    
    def __init__(self):
        self.logger = get_logger(__name__)
    
    async def validate(self, workflow: WorkflowResponse) -> Dict[str, Any]:
        """
        Validate a workflow structure.
        
        Returns:
            Dict with 'valid' (bool), 'errors' (List[str]), and 'warnings' (List[str])
        """
        errors = []
        warnings = []
        
        # Check if workflow has nodes
        if not workflow.nodes:
            errors.append("Workflow must have at least one node")
            return {"valid": False, "errors": errors, "warnings": warnings}
        
        # Validate start node
        start_node_errors = self._validate_start_node(workflow.nodes)
        errors.extend(start_node_errors)
        
        # Validate output nodes
        output_node_warnings = self._validate_output_nodes(workflow.nodes)
        warnings.extend(output_node_warnings)
        
        # Check for orphaned nodes
        orphaned_warnings = self._check_orphaned_nodes(workflow.nodes, workflow.edges)
        warnings.extend(orphaned_warnings)
        
        # Check for cycles
        cycle_errors = self._check_cycles(workflow.nodes, workflow.edges)
        errors.extend(cycle_errors)
        
        # Validate node configurations
        config_errors = self._validate_node_configs(workflow.nodes)
        errors.extend(config_errors)
        
        # Validate edges
        edge_errors = self._validate_edges(workflow.nodes, workflow.edges)
        errors.extend(edge_errors)
        
        # Check for unreachable nodes
        unreachable_warnings = self._check_unreachable_nodes(workflow.nodes, workflow.edges)
        warnings.extend(unreachable_warnings)
        
        is_valid = len(errors) == 0
        
        result = {
            "valid": is_valid,
            "errors": errors,
            "warnings": warnings,
            "node_count": len(workflow.nodes),
            "edge_count": len(workflow.edges),
        }
        
        if is_valid:
            logger.info(f"Workflow {workflow.name} validated successfully with {len(warnings)} warnings")
        else:
            logger.warning(f"Workflow {workflow.name} validation failed with {len(errors)} errors")
        
        return result
    
    def _validate_start_node(self, nodes: List[WorkflowNodeResponse]) -> List[str]:
        """Validate that there is exactly one start node."""
        errors = []
        
        start_nodes = [node for node in nodes if node.is_start_node]
        
        if len(start_nodes) == 0:
            errors.append("Workflow must have exactly one start node")
        elif len(start_nodes) > 1:
            errors.append(f"Workflow has {len(start_nodes)} start nodes, but must have exactly one")
        
        return errors
    
    def _validate_output_nodes(self, nodes: List[WorkflowNodeResponse]) -> List[str]:
        """Validate output nodes."""
        warnings = []
        
        output_nodes = [node for node in nodes if node.is_output_node]
        
        if len(output_nodes) == 0:
            warnings.append("Workflow has no output nodes - workflow output may not be captured")
        
        return warnings
    
    def _check_orphaned_nodes(self, nodes: List[WorkflowNodeResponse], edges: List[WorkflowEdgeResponse]) -> List[str]:
        """Check for nodes that have no incoming or outgoing edges."""
        warnings = []
        
        if not edges:
            return warnings
        
        # Build connectivity map
        node_connections = {node.id: {"incoming": 0, "outgoing": 0} for node in nodes}
        
        for edge in edges:
            if edge.source_node_id in node_connections:
                node_connections[edge.source_node_id]["outgoing"] += 1
            if edge.target_node_id in node_connections:
                node_connections[edge.target_node_id]["incoming"] += 1
        
        # Check for orphaned nodes (excluding start nodes which may have no incoming edges)
        for node in nodes:
            conn = node_connections[node.id]
            
            # A node is orphaned if it has no connections at all
            if conn["incoming"] == 0 and conn["outgoing"] == 0:
                warnings.append(f"Node '{node.name}' (ID: {node.id}) is orphaned - has no connections")
            
            # Warn about nodes with no outgoing edges (excluding potential end nodes)
            elif conn["outgoing"] == 0 and not node.is_output_node:
                warnings.append(f"Node '{node.name}' (ID: {node.id}) has no outgoing edges - may be a dead end")
        
        return warnings
    
    def _check_cycles(self, nodes: List[WorkflowNodeResponse], edges: List[WorkflowEdgeResponse]) -> List[str]:
        """Check for cycles in the workflow graph."""
        errors = []
        
        if not edges:
            return errors
        
        # Build adjacency list
        graph = {node.id: [] for node in nodes}
        for edge in edges:
            if edge.source_node_id in graph:
                graph[edge.source_node_id].append(edge.target_node_id)
        
        # Detect cycles using DFS
        visited = set()
        rec_stack = set()
        
        def has_cycle_util(node_id: int, path: List[int]) -> bool:
            visited.add(node_id)
            rec_stack.add(node_id)
            path.append(node_id)
            
            for neighbor in graph.get(node_id, []):
                if neighbor not in visited:
                    if has_cycle_util(neighbor, path):
                        return True
                elif neighbor in rec_stack:
                    # Found a cycle
                    cycle_start_idx = path.index(neighbor)
                    cycle_nodes = path[cycle_start_idx:] + [neighbor]
                    cycle_names = [next((n.name for n in nodes if n.id == nid), str(nid)) for nid in cycle_nodes]
                    errors.append(f"Cycle detected: {' -> '.join(cycle_names)}")
                    return True
            
            path.pop()
            rec_stack.remove(node_id)
            return False
        
        for node in nodes:
            if node.id not in visited:
                has_cycle_util(node.id, [])
        
        return errors
    
    def _validate_node_configs(self, nodes: List[WorkflowNodeResponse]) -> List[str]:
        """Validate node configurations."""
        errors = []
        
        for node in nodes:
            # Check for required configuration fields based on executor type
            if node.executor_type.value == "agent" and not node.agent_id:
                # Agent nodes should either have an agent_id or instructions in config
                if not node.config.get("instructions"):
                    errors.append(f"Agent node '{node.name}' (ID: {node.id}) requires either agent_id or instructions in config")
            
            elif node.executor_type.value == "function":
                # Function nodes should have function_code or function_name in config
                if not node.config.get("function_code") and not node.config.get("function_name"):
                    errors.append(f"Function node '{node.name}' (ID: {node.id}) requires function_code or function_name in config")
            
            elif node.executor_type.value == "condition":
                # Condition nodes should have a condition in config
                if not node.config.get("condition"):
                    errors.append(f"Condition node '{node.name}' (ID: {node.id}) requires condition in config")
            
            elif node.executor_type.value == "human_input":
                # Human input nodes should have a prompt in config
                if not node.config.get("prompt"):
                    errors.append(f"Human input node '{node.name}' (ID: {node.id}) requires prompt in config")
        
        return errors
    
    def _validate_edges(self, nodes: List[WorkflowNodeResponse], edges: List[WorkflowEdgeResponse]) -> List[str]:
        """Validate edges between nodes."""
        errors = []
        
        node_ids = {node.id for node in nodes}
        
        for edge in edges:
            # Check if source and target nodes exist
            if edge.source_node_id not in node_ids:
                errors.append(f"Edge {edge.id} references non-existent source node ID: {edge.source_node_id}")
            
            if edge.target_node_id not in node_ids:
                errors.append(f"Edge {edge.id} references non-existent target node ID: {edge.target_node_id}")
            
            # Check for self-loops
            if edge.source_node_id == edge.target_node_id:
                node_name = next((n.name for n in nodes if n.id == edge.source_node_id), str(edge.source_node_id))
                errors.append(f"Edge {edge.id} creates a self-loop on node '{node_name}' (ID: {edge.source_node_id})")
            
            # Validate condition syntax if present
            if edge.condition:
                condition_errors = self._validate_condition_syntax(edge.condition, edge.id)
                errors.extend(condition_errors)
        
        return errors
    
    def _validate_condition_syntax(self, condition: str, edge_id: int) -> List[str]:
        """Validate condition syntax (basic check)."""
        errors = []
        
        # Basic syntax validation
        if not condition.strip():
            errors.append(f"Edge {edge_id} has an empty condition")
            return errors
        
        # Check for common Python syntax issues
        try:
            # Try to compile the condition as a lambda
            compile(f"lambda data: {condition}", "<string>", "eval")
        except SyntaxError as e:
            errors.append(f"Edge {edge_id} has invalid condition syntax: {str(e)}")
        except Exception as e:
            errors.append(f"Edge {edge_id} condition validation error: {str(e)}")
        
        return errors
    
    def _check_unreachable_nodes(self, nodes: List[WorkflowNodeResponse], edges: List[WorkflowEdgeResponse]) -> List[str]:
        """Check for nodes that are unreachable from the start node."""
        warnings = []
        
        if not edges:
            # If no edges, only the start node is reachable
            unreachable = [node for node in nodes if not node.is_start_node]
            if unreachable:
                warnings.append(f"{len(unreachable)} nodes are unreachable (no edges defined)")
            return warnings
        
        # Find start node
        start_nodes = [node for node in nodes if node.is_start_node]
        if not start_nodes:
            return warnings  # This error is already caught by _validate_start_node
        
        start_node_id = start_nodes[0].id
        
        # Build adjacency list
        graph = {node.id: [] for node in nodes}
        for edge in edges:
            if edge.source_node_id in graph:
                graph[edge.source_node_id].append(edge.target_node_id)
        
        # BFS to find all reachable nodes
        reachable = set()
        queue = [start_node_id]
        reachable.add(start_node_id)
        
        while queue:
            current = queue.pop(0)
            for neighbor in graph.get(current, []):
                if neighbor not in reachable:
                    reachable.add(neighbor)
                    queue.append(neighbor)
        
        # Find unreachable nodes
        all_node_ids = {node.id for node in nodes}
        unreachable_ids = all_node_ids - reachable
        
        if unreachable_ids:
            unreachable_names = [next((n.name for n in nodes if n.id == nid), str(nid)) for nid in unreachable_ids]
            warnings.append(f"Unreachable nodes: {', '.join(unreachable_names)}")
        
        return warnings
    
    def get_workflow_stats(self, workflow: WorkflowResponse) -> Dict[str, Any]:
        """Get statistics about the workflow structure."""
        node_types = {}
        for node in workflow.nodes:
            node_type = node.executor_type.value
            node_types[node_type] = node_types.get(node_type, 0) + 1
        
        # Calculate graph properties
        max_depth = self._calculate_max_depth(workflow.nodes, workflow.edges)
        branching_factor = self._calculate_avg_branching_factor(workflow.nodes, workflow.edges)
        
        return {
            "total_nodes": len(workflow.nodes),
            "total_edges": len(workflow.edges),
            "node_types": node_types,
            "start_nodes": len([n for n in workflow.nodes if n.is_start_node]),
            "output_nodes": len([n for n in workflow.nodes if n.is_output_node]),
            "max_depth": max_depth,
            "avg_branching_factor": branching_factor,
        }
    
    def _calculate_max_depth(self, nodes: List[WorkflowNodeResponse], edges: List[WorkflowEdgeResponse]) -> int:
        """Calculate the maximum depth of the workflow graph."""
        if not nodes or not edges:
            return 1 if nodes else 0
        
        # Find start node
        start_nodes = [node for node in nodes if node.is_start_node]
        if not start_nodes:
            return 0
        
        start_node_id = start_nodes[0].id
        
        # Build adjacency list
        graph = {node.id: [] for node in nodes}
        for edge in edges:
            if edge.source_node_id in graph:
                graph[edge.source_node_id].append(edge.target_node_id)
        
        # BFS to find max depth
        max_depth = 0
        queue = [(start_node_id, 1)]  # (node_id, depth)
        visited = set()
        
        while queue:
            current, depth = queue.pop(0)
            if current in visited:
                continue
            visited.add(current)
            max_depth = max(max_depth, depth)
            
            for neighbor in graph.get(current, []):
                queue.append((neighbor, depth + 1))
        
        return max_depth
    
    def _calculate_avg_branching_factor(self, nodes: List[WorkflowNodeResponse], edges: List[WorkflowEdgeResponse]) -> float:
        """Calculate the average branching factor of the workflow graph."""
        if not nodes or not edges:
            return 0.0
        
        # Count outgoing edges for each node
        outgoing_counts = {node.id: 0 for node in nodes}
        for edge in edges:
            if edge.source_node_id in outgoing_counts:
                outgoing_counts[edge.source_node_id] += 1
        
        # Calculate average (excluding nodes with no outgoing edges)
        nodes_with_outgoing = [count for count in outgoing_counts.values() if count > 0]
        
        if not nodes_with_outgoing:
            return 0.0
        
        return sum(nodes_with_outgoing) / len(nodes_with_outgoing)
