"""
Test SQLModel to Response Model conversion
"""
import traceback
from datetime import datetime
from app.models import Agent, AgentResponse, AgentType

try:
    print("Creating test Agent instance...")
    
    # Create an Agent instance (simulating what comes from database)
    agent = Agent(
        id=1,
        name="Test Agent",
        description="Test description",
        agent_type=AgentType.CHAT_AGENT,
        instructions="Test instructions",
        model_settings={"temperature": 0.7},
        tools=["tool1", "tool2"],
        is_active=True,
        created_at=datetime.utcnow(),
        updated_at=None
    )
    
    print(f"✅ Created Agent: {agent}")
    print(f"   Agent type: {type(agent)}")
    print(f"   Agent.name: {agent.name}")
    
    print("\nTesting manual conversion to AgentResponse...")
    
    # Test 1: Try model_validate
    try:
        response = AgentResponse.model_validate(agent)
        print(f"✅ model_validate works!")
        print(f"   Response: {response}")
    except Exception as e:
        print(f"❌ model_validate failed: {e}")
        traceback.print_exc()
    
    # Test 2: Try from dict
    try:
        agent_dict = agent.model_dump()
        response2 = AgentResponse(**agent_dict)
        print(f"✅ Dict conversion works!")
        print(f"   Response: {response2}")
    except Exception as e:
        print(f"❌ Dict conversion failed: {e}")
        traceback.print_exc()
    
    # Test 3: Return as-is (what FastAPI will do)
    print(f"\n✅ Can return Agent directly: {agent}")
    print(f"   FastAPI will convert using response_model")
    
except Exception as e:
    print(f"❌ Error: {e}")
    print("\nFull traceback:")
    traceback.print_exc()
