"""
Workflow executor for running workflows using Microsoft Agent Framework.
Handles execution, event streaming, and state management.
"""
import asyncio
from typing import Dict, Any, Optional, AsyncGenerator
from datetime import datetime

from app.core.logging import get_logger

logger = get_logger(__name__)

# Try to import Microsoft Agent Framework components
try:
    from agent_framework import Workflow, WorkflowOutputEvent, AgentRunUpdateEvent
    WORKFLOW_EXECUTION_AVAILABLE = True
    logger.info("Microsoft Agent Framework workflow execution available")
except ImportError as e:
    logger.warning(f"Agent Framework workflow execution not available: {e}")
    WORKFLOW_EXECUTION_AVAILABLE = False
    
    # Mock classes for development
    class Workflow:
        async def run(self, input_data):
            return {"result": "Mock workflow execution"}
        
        async def run_streaming(self, input_data):
            yield {"type": "start", "data": input_data}
            yield {"type": "complete", "result": "Mock workflow"}
    
    class WorkflowOutputEvent:
        def __init__(self, data):
            self.data = data
            self.event_type = "output"
    
    class AgentRunUpdateEvent:
        def __init__(self, executor_id, data):
            self.executor_id = executor_id
            self.data = data
            self.event_type = "agent_update"


class WorkflowExecutor:
    """Executor for running workflows with event streaming."""
    
    def __init__(self):
        self.logger = get_logger(__name__)
        self.running_workflows: Dict[int, Any] = {}
    
    async def execute(
        self, 
        workflow: Workflow, 
        input_data: Any,
        execution_id: Optional[int] = None,
        stream: bool = False
    ) -> Dict[str, Any]:
        """
        Execute a workflow with the given input data.
        
        Args:
            workflow: The Agent Framework workflow to execute
            input_data: Input data for the workflow
            execution_id: Optional execution ID for tracking
            stream: Whether to use streaming execution
        
        Returns:
            Dict containing execution results
        """
        try:
            if execution_id:
                self.running_workflows[execution_id] = workflow
            
            start_time = datetime.utcnow()
            
            if stream:
                # Use streaming execution
                result = await self._execute_streaming(workflow, input_data, execution_id)
            else:
                # Use non-streaming execution
                result = await workflow.run(input_data)
            
            end_time = datetime.utcnow()
            duration = (end_time - start_time).total_seconds()
            
            return {
                "success": True,
                "result": result,
                "execution_time": duration,
                "started_at": start_time.isoformat(),
                "completed_at": end_time.isoformat(),
            }
            
        except Exception as e:
            logger.error(f"Error executing workflow: {e}")
            return {
                "success": False,
                "error": str(e),
                "error_type": type(e).__name__,
            }
        finally:
            if execution_id and execution_id in self.running_workflows:
                del self.running_workflows[execution_id]
    
    async def execute_with_events(
        self,
        workflow: Workflow,
        input_data: Any,
        execution_id: Optional[int] = None
    ) -> AsyncGenerator[Dict[str, Any], None]:
        """
        Execute a workflow and yield events as they occur.
        
        This is used for real-time WebSocket streaming to the frontend.
        
        Args:
            workflow: The Agent Framework workflow to execute
            input_data: Input data for the workflow
            execution_id: Optional execution ID for tracking
        
        Yields:
            Dict containing event data
        """
        try:
            if execution_id:
                self.running_workflows[execution_id] = workflow
            
            # Yield start event
            yield {
                "event_type": "execution_started",
                "execution_id": execution_id,
                "timestamp": datetime.utcnow().isoformat(),
                "input_data": input_data
            }
            
            # Execute workflow with streaming
            try:
                if WORKFLOW_EXECUTION_AVAILABLE:
                    async for event in workflow.run_streaming(input_data):
                        yield await self._process_workflow_event(event, execution_id)
                else:
                    # Mock streaming for development
                    for i in range(3):
                        await asyncio.sleep(0.5)
                        yield {
                            "event_type": "progress",
                            "execution_id": execution_id,
                            "timestamp": datetime.utcnow().isoformat(),
                            "data": f"Mock progress step {i+1}"
                        }
            except Exception as e:
                yield {
                    "event_type": "execution_error",
                    "execution_id": execution_id,
                    "timestamp": datetime.utcnow().isoformat(),
                    "error": str(e),
                    "error_type": type(e).__name__
                }
                raise
            
            # Yield completion event
            yield {
                "event_type": "execution_completed",
                "execution_id": execution_id,
                "timestamp": datetime.utcnow().isoformat(),
            }
            
        finally:
            if execution_id and execution_id in self.running_workflows:
                del self.running_workflows[execution_id]
    
    async def _execute_streaming(
        self,
        workflow: Workflow,
        input_data: Any,
        execution_id: Optional[int] = None
    ) -> Any:
        """Execute workflow with streaming and collect final result."""
        final_result = None
        
        try:
            async for event in workflow.run_streaming(input_data):
                # Process and log events
                processed_event = await self._process_workflow_event(event, execution_id)
                logger.debug(f"Workflow event: {processed_event.get('event_type')}")
                
                # Capture final result
                if isinstance(event, WorkflowOutputEvent):
                    final_result = event.data
        
        except Exception as e:
            logger.error(f"Error in streaming execution: {e}")
            raise
        
        return final_result
    
    async def _process_workflow_event(self, event: Any, execution_id: Optional[int] = None) -> Dict[str, Any]:
        """
        Process a workflow event and convert it to a standardized format.
        
        Args:
            event: Agent Framework workflow event
            execution_id: Optional execution ID for tracking
        
        Returns:
            Dict containing standardized event data
        """
        try:
            # Handle WorkflowOutputEvent
            if isinstance(event, WorkflowOutputEvent):
                return {
                    "event_type": "workflow_output",
                    "execution_id": execution_id,
                    "timestamp": datetime.utcnow().isoformat(),
                    "data": event.data if hasattr(event, 'data') else str(event),
                }
            
            # Handle AgentRunUpdateEvent
            elif isinstance(event, AgentRunUpdateEvent):
                return {
                    "event_type": "agent_update",
                    "execution_id": execution_id,
                    "timestamp": datetime.utcnow().isoformat(),
                    "executor_id": getattr(event, 'executor_id', None),
                    "data": event.data if hasattr(event, 'data') else str(event),
                }
            
            # Handle generic events
            else:
                event_type = type(event).__name__
                return {
                    "event_type": event_type.lower().replace('event', ''),
                    "execution_id": execution_id,
                    "timestamp": datetime.utcnow().isoformat(),
                    "data": self._extract_event_data(event),
                }
        
        except Exception as e:
            logger.error(f"Error processing workflow event: {e}")
            return {
                "event_type": "processing_error",
                "execution_id": execution_id,
                "timestamp": datetime.utcnow().isoformat(),
                "error": str(e)
            }
    
    def _extract_event_data(self, event: Any) -> Any:
        """Extract data from an event object."""
        if hasattr(event, 'data'):
            return event.data
        elif hasattr(event, 'content'):
            return event.content
        elif hasattr(event, 'message'):
            return event.message
        elif hasattr(event, '__dict__'):
            return {k: v for k, v in event.__dict__.items() if not k.startswith('_')}
        else:
            return str(event)
    
    async def pause_execution(self, execution_id: int) -> bool:
        """
        Pause a running workflow execution.
        
        Note: This requires workflow checkpointing support.
        
        Args:
            execution_id: ID of the execution to pause
        
        Returns:
            True if paused successfully, False otherwise
        """
        if execution_id not in self.running_workflows:
            logger.warning(f"Cannot pause execution {execution_id}: not running")
            return False
        
        try:
            # TODO: Implement actual pause mechanism using workflow checkpointing
            # This would require integrating with Agent Framework's CheckpointManager
            logger.info(f"Pausing execution {execution_id}")
            
            # For now, we just remove it from tracking
            # In a real implementation, this would trigger a checkpoint save
            workflow = self.running_workflows.get(execution_id)
            if workflow:
                # Save checkpoint here
                pass
            
            return True
            
        except Exception as e:
            logger.error(f"Error pausing execution {execution_id}: {e}")
            return False
    
    async def resume_execution(
        self,
        workflow: Workflow,
        execution_id: int,
        checkpoint_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Resume a paused workflow execution from a checkpoint.
        
        Args:
            workflow: The workflow to resume
            execution_id: ID of the execution
            checkpoint_id: Optional checkpoint ID to resume from
        
        Returns:
            Dict containing execution results
        """
        try:
            logger.info(f"Resuming execution {execution_id} from checkpoint {checkpoint_id}")
            
            # TODO: Implement actual resume mechanism using workflow checkpointing
            # This would require:
            # 1. Loading the checkpoint state
            # 2. Restoring the workflow context
            # 3. Continuing execution from the saved state
            
            # For now, return a placeholder
            return {
                "success": True,
                "message": f"Resume not yet implemented for execution {execution_id}",
                "checkpoint_id": checkpoint_id
            }
            
        except Exception as e:
            logger.error(f"Error resuming execution {execution_id}: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def get_running_executions(self) -> Dict[int, Dict[str, Any]]:
        """
        Get information about currently running executions.
        
        Returns:
            Dict mapping execution IDs to execution info
        """
        running = {}
        
        for execution_id, workflow in self.running_workflows.items():
            running[execution_id] = {
                "execution_id": execution_id,
                "workflow_name": getattr(workflow, 'name', 'unknown'),
                "status": "running"
            }
        
        return running
    
    def is_execution_running(self, execution_id: int) -> bool:
        """Check if an execution is currently running."""
        return execution_id in self.running_workflows
    
    async def stop_execution(self, execution_id: int) -> bool:
        """
        Stop a running workflow execution.
        
        Args:
            execution_id: ID of the execution to stop
        
        Returns:
            True if stopped successfully, False otherwise
        """
        if execution_id not in self.running_workflows:
            logger.warning(f"Cannot stop execution {execution_id}: not running")
            return False
        
        try:
            logger.info(f"Stopping execution {execution_id}")
            
            # Remove from tracking
            if execution_id in self.running_workflows:
                del self.running_workflows[execution_id]
            
            # TODO: Implement actual cancellation mechanism
            # This would require canceling the asyncio task running the workflow
            
            return True
            
        except Exception as e:
            logger.error(f"Error stopping execution {execution_id}: {e}")
            return False
    
    def get_execution_stats(self) -> Dict[str, Any]:
        """Get statistics about workflow execution."""
        return {
            "running_count": len(self.running_workflows),
            "running_execution_ids": list(self.running_workflows.keys()),
            "framework_available": WORKFLOW_EXECUTION_AVAILABLE
        }
