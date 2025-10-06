"""
Workflow visualizer for generating visual representations of workflows.
Uses Microsoft Agent Framework's WorkflowViz when available.
"""
from typing import Dict, Any, Optional
from app.models import WorkflowResponse
from app.core.logging import get_logger

logger = get_logger(__name__)

# Try to import Microsoft Agent Framework WorkflowViz
try:
    from agent_framework import WorkflowViz
    WORKFLOW_VIZ_AVAILABLE = True
    logger.info("Microsoft Agent Framework WorkflowViz available")
except ImportError:
    logger.warning("WorkflowViz not available, using basic visualization")
    WORKFLOW_VIZ_AVAILABLE = False


class WorkflowVisualizer:
    """Visualizer for generating workflow diagrams."""
    
    def __init__(self):
        self.logger = get_logger(__name__)
    
    async def generate(self, workflow: WorkflowResponse, format: str = "mermaid") -> Dict[str, Any]:
        """
        Generate a visual representation of the workflow.
        
        Args:
            workflow: The workflow to visualize
            format: Output format ('mermaid', 'svg', 'png', 'dot')
        
        Returns:
            Dict with visualization data
        """
        try:
            if format == "mermaid":
                return await self.generate_mermaid(workflow)
            elif format == "svg":
                return await self.generate_svg(workflow)
            elif format == "png":
                return await self.generate_png(workflow)
            elif format == "dot":
                return await self.generate_dot(workflow)
            elif format == "json":
                return await self.generate_json(workflow)
            else:
                raise ValueError(f"Unsupported visualization format: {format}")
                
        except Exception as e:
            logger.error(f"Error generating visualization for workflow {workflow.name}: {e}")
            return {
                "format": format,
                "error": str(e),
                "workflow_id": workflow.id,
                "workflow_name": workflow.name
            }
    
    async def generate_mermaid(self, workflow: WorkflowResponse) -> Dict[str, Any]:
        """Generate Mermaid diagram definition."""
        try:
            mermaid_def = self._build_mermaid_diagram(workflow)
            
            return {
                "format": "mermaid",
                "content": mermaid_def,
                "workflow_id": workflow.id,
                "workflow_name": workflow.name,
                "node_count": len(workflow.nodes),
                "edge_count": len(workflow.edges)
            }
            
        except Exception as e:
            logger.error(f"Error generating Mermaid diagram: {e}")
            raise
    
    async def generate_svg(self, workflow: WorkflowResponse) -> Dict[str, Any]:
        """Generate SVG visualization."""
        if not WORKFLOW_VIZ_AVAILABLE:
            return {
                "format": "svg",
                "error": "WorkflowViz not available - cannot generate SVG",
                "fallback": "Use Mermaid format instead"
            }
        
        try:
            # Note: This requires building an actual Agent Framework workflow
            # and using WorkflowViz.export(format="svg")
            # For now, return placeholder
            return {
                "format": "svg",
                "content": await self._generate_svg_placeholder(workflow),
                "workflow_id": workflow.id,
                "workflow_name": workflow.name,
                "note": "SVG generation requires building executable workflow"
            }
            
        except Exception as e:
            logger.error(f"Error generating SVG: {e}")
            raise
    
    async def generate_png(self, workflow: WorkflowResponse) -> Dict[str, Any]:
        """Generate PNG visualization."""
        if not WORKFLOW_VIZ_AVAILABLE:
            return {
                "format": "png",
                "error": "WorkflowViz not available - cannot generate PNG",
                "fallback": "Use Mermaid format instead"
            }
        
        try:
            # Note: This requires building an actual Agent Framework workflow
            # and using WorkflowViz.export(format="png")
            return {
                "format": "png",
                "content": None,
                "workflow_id": workflow.id,
                "workflow_name": workflow.name,
                "note": "PNG generation requires building executable workflow and GraphViz"
            }
            
        except Exception as e:
            logger.error(f"Error generating PNG: {e}")
            raise
    
    async def generate_dot(self, workflow: WorkflowResponse) -> Dict[str, Any]:
        """Generate Graphviz DOT format."""
        try:
            dot_def = self._build_dot_diagram(workflow)
            
            return {
                "format": "dot",
                "content": dot_def,
                "workflow_id": workflow.id,
                "workflow_name": workflow.name,
                "node_count": len(workflow.nodes),
                "edge_count": len(workflow.edges)
            }
            
        except Exception as e:
            logger.error(f"Error generating DOT diagram: {e}")
            raise
    
    async def generate_json(self, workflow: WorkflowResponse) -> Dict[str, Any]:
        """Generate JSON representation for visualization libraries."""
        try:
            # Generate a JSON structure compatible with visualization libraries like D3.js or Cytoscape.js
            nodes = []
            for node in workflow.nodes:
                nodes.append({
                    "id": str(node.id),
                    "label": node.name,
                    "type": node.executor_type.value,
                    "position": {
                        "x": node.position_x,
                        "y": node.position_y
                    },
                    "is_start": node.is_start_node,
                    "is_output": node.is_output_node,
                    "agent_id": node.agent_id,
                    "config": node.config
                })
            
            edges = []
            for edge in workflow.edges:
                edges.append({
                    "id": str(edge.id),
                    "source": str(edge.source_node_id),
                    "target": str(edge.target_node_id),
                    "label": edge.label,
                    "condition": edge.condition,
                    "config": edge.config
                })
            
            return {
                "format": "json",
                "content": {
                    "nodes": nodes,
                    "edges": edges
                },
                "workflow_id": workflow.id,
                "workflow_name": workflow.name,
                "node_count": len(nodes),
                "edge_count": len(edges)
            }
            
        except Exception as e:
            logger.error(f"Error generating JSON visualization: {e}")
            raise
    
    def _build_mermaid_diagram(self, workflow: WorkflowResponse) -> str:
        """Build a Mermaid diagram definition from workflow."""
        lines = ["graph TB"]  # Top to Bottom direction
        
        # Add nodes
        for node in workflow.nodes:
            node_id = f"N{node.id}"
            node_label = node.name
            
            # Different shapes based on node type and properties
            if node.is_start_node:
                lines.append(f'    {node_id}(["{node_label}"])')  # Stadium shape for start
            elif node.is_output_node:
                lines.append(f'    {node_id}["{node_label}"]')    # Rectangle for output
            elif node.executor_type.value == "condition":
                lines.append(f'    {node_id}{{"{node_label}"}}')  # Diamond for condition
            elif node.executor_type.value == "human_input":
                lines.append(f'    {node_id}[/"{node_label}"\\]') # Parallelogram for input
            else:
                lines.append(f'    {node_id}["{node_label}"]')    # Rectangle for regular nodes
            
            # Add styling classes
            if node.is_start_node:
                lines.append(f'    class {node_id} startNode')
            elif node.is_output_node:
                lines.append(f'    class {node_id} outputNode')
            elif node.executor_type.value == "agent":
                lines.append(f'    class {node_id} agentNode')
        
        # Add edges
        for edge in workflow.edges:
            source_id = f"N{edge.source_node_id}"
            target_id = f"N{edge.target_node_id}"
            
            # Edge label
            if edge.label:
                label = edge.label
            elif edge.condition:
                label = edge.condition[:20] + "..." if len(edge.condition) > 20 else edge.condition
            else:
                label = ""
            
            # Different arrow styles
            if edge.condition:
                # Conditional edges use dotted lines
                if label:
                    lines.append(f'    {source_id} -."{label}".-> {target_id}')
                else:
                    lines.append(f'    {source_id} -.-> {target_id}')
            else:
                # Regular edges use solid lines
                if label:
                    lines.append(f'    {source_id} --"{label}"--> {target_id}')
                else:
                    lines.append(f'    {source_id} --> {target_id}')
        
        # Add styling classes
        lines.extend([
            "",
            "    classDef startNode fill:#90EE90,stroke:#006400,stroke-width:3px",
            "    classDef outputNode fill:#87CEEB,stroke:#00008B,stroke-width:3px",
            "    classDef agentNode fill:#FFD700,stroke:#FF8C00,stroke-width:2px"
        ])
        
        return "\n".join(lines)
    
    def _build_dot_diagram(self, workflow: WorkflowResponse) -> str:
        """Build a Graphviz DOT diagram definition from workflow."""
        lines = [
            "digraph workflow {",
            "    rankdir=TB;",
            "    node [shape=box, style=rounded];",
            ""
        ]
        
        # Add nodes
        for node in workflow.nodes:
            node_id = f"N{node.id}"
            node_label = node.name
            
            # Different attributes based on node type
            if node.is_start_node:
                lines.append(f'    {node_id} [label="{node_label}", shape=ellipse, fillcolor=lightgreen, style=filled];')
            elif node.is_output_node:
                lines.append(f'    {node_id} [label="{node_label}", fillcolor=lightblue, style=filled];')
            elif node.executor_type.value == "condition":
                lines.append(f'    {node_id} [label="{node_label}", shape=diamond];')
            elif node.executor_type.value == "agent":
                lines.append(f'    {node_id} [label="{node_label}", fillcolor=lightyellow, style=filled];')
            else:
                lines.append(f'    {node_id} [label="{node_label}"];')
        
        lines.append("")
        
        # Add edges
        for edge in workflow.edges:
            source_id = f"N{edge.source_node_id}"
            target_id = f"N{edge.target_node_id}"
            
            # Edge attributes
            attrs = []
            if edge.label:
                attrs.append(f'label="{edge.label}"')
            if edge.condition:
                attrs.append('style=dashed')
                if not edge.label:
                    condition_label = edge.condition[:20] + "..." if len(edge.condition) > 20 else edge.condition
                    attrs.append(f'label="{condition_label}"')
            
            attr_str = f" [{', '.join(attrs)}]" if attrs else ""
            lines.append(f'    {source_id} -> {target_id}{attr_str};')
        
        lines.append("}")
        
        return "\n".join(lines)
    
    async def _generate_svg_placeholder(self, workflow: WorkflowResponse) -> str:
        """Generate a simple SVG placeholder."""
        width = 800
        height = 600
        
        svg_lines = [
            f'<svg width="{width}" height="{height}" xmlns="http://www.w3.org/2000/svg">',
            f'  <rect width="{width}" height="{height}" fill="#f9f9f9" />',
            f'  <text x="{width//2}" y="{height//2}" text-anchor="middle" font-size="20" fill="#333">',
            f'    Workflow: {workflow.name}',
            '  </text>',
            f'  <text x="{width//2}" y="{height//2 + 30}" text-anchor="middle" font-size="14" fill="#666">',
            f'    {len(workflow.nodes)} nodes, {len(workflow.edges)} edges',
            '  </text>',
            f'  <text x="{width//2}" y="{height//2 + 50}" text-anchor="middle" font-size="12" fill="#999">',
            '    (Use Mermaid format for full visualization)',
            '  </text>',
            '</svg>'
        ]
        
        return "\n".join(svg_lines)
    
    async def generate_react_flow_data(self, workflow: WorkflowResponse) -> Dict[str, Any]:
        """
        Generate data structure optimized for React Flow visualization.
        This can be used directly by the frontend React Flow component.
        """
        try:
            # Convert nodes to React Flow format
            react_flow_nodes = []
            for node in workflow.nodes:
                node_type = "default"
                if node.is_start_node:
                    node_type = "input"
                elif node.is_output_node:
                    node_type = "output"
                
                react_flow_nodes.append({
                    "id": str(node.id),
                    "type": node_type,
                    "data": {
                        "label": node.name,
                        "executor_type": node.executor_type.value,
                        "agent_id": node.agent_id,
                        "config": node.config
                    },
                    "position": {
                        "x": node.position_x,
                        "y": node.position_y
                    }
                })
            
            # Convert edges to React Flow format
            react_flow_edges = []
            for edge in workflow.edges:
                edge_data = {
                    "id": str(edge.id),
                    "source": str(edge.source_node_id),
                    "target": str(edge.target_node_id),
                    "label": edge.label or "",
                }
                
                # Add conditional styling
                if edge.condition:
                    edge_data["animated"] = True
                    edge_data["style"] = {"strokeDasharray": "5,5"}
                    edge_data["data"] = {"condition": edge.condition}
                
                react_flow_edges.append(edge_data)
            
            return {
                "format": "react-flow",
                "nodes": react_flow_nodes,
                "edges": react_flow_edges,
                "workflow_id": workflow.id,
                "workflow_name": workflow.name
            }
            
        except Exception as e:
            logger.error(f"Error generating React Flow data: {e}")
            raise
