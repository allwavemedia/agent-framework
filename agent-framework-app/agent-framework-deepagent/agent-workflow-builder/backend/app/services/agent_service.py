"""
Agent service for managing AI agents.
"""
from typing import List, Optional, Dict, Any
from datetime import datetime
from sqlmodel import Session, select

from app.models import Agent, AgentCreate, AgentUpdate, AgentResponse
from app.agents.agent_factory import AgentFactory
from app.core.logging import get_logger

logger = get_logger(__name__)


class AgentService:
    """Service for managing agents."""
    
    def __init__(self, db: Session):
        self.db = db
        self.agent_factory = AgentFactory()
    
    async def list_agents(self, skip: int = 0, limit: int = 100) -> List[AgentResponse]:
        """List all agents."""
        statement = select(Agent).offset(skip).limit(limit)
        result = self.db.exec(statement)
        agents = result.all()
        
        return [AgentResponse.from_orm(agent) for agent in agents]
    
    async def create_agent(self, agent_data: AgentCreate) -> AgentResponse:
        """Create a new agent."""
        # Create database record
        agent = Agent(**agent_data.dict())
        agent.created_at = datetime.utcnow()
        
        self.db.add(agent)
        self.db.commit()
        self.db.refresh(agent)
        
        logger.info(f"Created agent: {agent.name} (ID: {agent.id})")
        
        return AgentResponse.from_orm(agent)
    
    async def get_agent(self, agent_id: int) -> Optional[AgentResponse]:
        """Get an agent by ID."""
        agent = self.db.get(Agent, agent_id)
        if not agent:
            return None
        
        return AgentResponse.from_orm(agent)
    
    async def update_agent(self, agent_id: int, agent_data: AgentUpdate) -> Optional[AgentResponse]:
        """Update an agent."""
        agent = self.db.get(Agent, agent_id)
        if not agent:
            return None
        
        # Update fields
        update_data = agent_data.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(agent, field, value)
        
        agent.updated_at = datetime.utcnow()
        
        self.db.add(agent)
        self.db.commit()
        self.db.refresh(agent)
        
        logger.info(f"Updated agent: {agent.name} (ID: {agent.id})")
        
        return AgentResponse.from_orm(agent)
    
    async def delete_agent(self, agent_id: int) -> bool:
        """Delete an agent."""
        agent = self.db.get(Agent, agent_id)
        if not agent:
            return False
        
        self.db.delete(agent)
        self.db.commit()
        
        logger.info(f"Deleted agent: {agent.name} (ID: {agent_id})")
        
        return True
    
    async def test_agent(self, agent_id: int, test_input: Dict[str, Any]) -> Dict[str, Any]:
        """Test an agent with sample input."""
        agent = self.db.get(Agent, agent_id)
        if not agent:
            raise ValueError("Agent not found")
        
        try:
            # Create agent instance
            agent_instance = await self.agent_factory.create_agent(agent)
            
            # Run test
            result = await agent_instance.run(test_input.get("message", "Hello"))
            
            return {
                "success": True,
                "result": result.text if hasattr(result, 'text') else str(result),
                "agent_id": agent_id,
                "test_input": test_input,
                "timestamp": datetime.utcnow().isoformat(),
            }
            
        except Exception as e:
            logger.error(f"Error testing agent {agent_id}: {e}")
            return {
                "success": False,
                "error": str(e),
                "agent_id": agent_id,
                "test_input": test_input,
                "timestamp": datetime.utcnow().isoformat(),
            }