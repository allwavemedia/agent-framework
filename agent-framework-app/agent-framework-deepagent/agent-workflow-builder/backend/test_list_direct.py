"""
Test API endpoint directly
"""
import asyncio
import traceback
from app.core.database import get_db
from app.services.agent_service import AgentService

async def test_list_agents():
    """Test listing agents directly"""
    try:
        print("Creating database session...")
        db = next(get_db())
        
        print("Creating AgentService...")
        service = AgentService(db)
        
        print("Calling list_agents()...")
        agents = await service.list_agents(skip=0, limit=100)
        
        print(f"✅ Success! Got {len(agents)} agents")
        print(f"   Type: {type(agents)}")
        if agents:
            print(f"   First agent: {agents[0]}")
            print(f"   First agent type: {type(agents[0])}")
        
        return agents
        
    except Exception as e:
        print(f"❌ Error: {e}")
        print("\nFull traceback:")
        traceback.print_exc()
        return None

if __name__ == "__main__":
    asyncio.run(test_list_agents())
